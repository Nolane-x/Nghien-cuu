#!/usr/bin/env python3
"""Replay released Wilbers K MODs on independent original voltage-clamp protocols.

The simulation uses the unchanged Dataverse MOD sources and imports the
original channel_tools.py fitting/current helpers. Protocol loops mirror
K_IV_ss and K_recovery_ss so full voltage-indexed outputs can be compared
against the independent Figure 4 per-recording workbook audit.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import audit_wilbers_k_mod_variants as audit

K_NAMES = (
    "k_human", "k_mouse", "k_human_h1", "k_human_hm12inf",
    "k_hybrid1", "k_hybrid2", "k_hybrid3", "k_hybrid4", "k_hybrid5",
)
K_PINS = {
    "k_human": {"id": 318647, "bytes": 4220, "sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5"},
    "k_mouse": {"id": 318649, "bytes": 4189, "sha1": "1d83124eefc45aa7321a5a21337f080c2519ceed"},
    "k_human_h1": {"id": 318627, "bytes": 3587, "sha1": "e9ded848fa149b86aec30f6d3f5b173f0c7cb523"},
    "k_human_hm12inf": {"id": 318604, "bytes": 4614, "sha1": "72ab45e927d542271fc8d54a9ed7e7cb14d771d2"},
    "k_hybrid1": {"id": 318628, "bytes": 4056, "sha1": "3bb28fc3fcdace2b07392c69140518c91977ce1e"},
    "k_hybrid2": {"id": 318622, "bytes": 4046, "sha1": "05040e3bfe6d2914a14358e62bb631f0c9ef492b"},
    "k_hybrid3": {"id": 318609, "bytes": 4046, "sha1": "89e09570588d45e45ce413b9da42e5007ec98aa4"},
    "k_hybrid4": {"id": 318619, "bytes": 4070, "sha1": "b786dd01e95b7cbf89e652c4fe2d88e4295c9cae"},
    "k_hybrid5": {"id": 318605, "bytes": 4080, "sha1": "0df02624547f1df97de4fa06d1992524f62e220f"},
}
SOURCE_NAMES = ("channel_tools", "channel_kinetics")
SOURCE_ROLES = {
    "k_human": "canonical human potassium reference",
    "k_mouse": "canonical mouse potassium comparator",
    "k_human_h1": "released reduced-state human variant with m,h gates",
    "k_human_hm12inf": "released human variant with m,m1,m2,h1,h2 gates",
    **audit.HYBRID_ROLES,
}

FIGURE4_JSON = Path("research/../amsn-core/results/wilbers_figure4_voltage_clamp_audit_2026-11-23.json")
FIGURE4_PER_RECORDING = Path("amsn-core/results/wilbers_figure4_voltage_clamp_per_recording_2026-11-23.csv")
EXPECTED_FIGURE4_SHA256 = "79a39dce26b9e47cc6a1aa81bbc4dc3e29e3d2c733809dad14e98d4f5f9b4836"
EXPECTED_FIGURE4_MEASUREMENTS = 3732

K_IV_DURS_MS = (20.0, 500.0, 50.0, 100.0)
K_IV_START_AMPS_MV = (-140.0, 0.0, 60.0, -140.0)
K_IV_VOLTAGES_MV = tuple(float(x) for x in np.arange(-110, 60, 10))
K_IV_DT_MS = 0.1
RECOVERY_DT_MS = 0.5
RECOVERY_VOLTAGE_MV = -80.0
RECOVERY_DELAYS_MS = tuple(float(x) for x in np.linspace(2, 92, 10) ** 2)
RECOVERY_DURS_PREFIX_MS = (2.0, 5000.0)
RECOVERY_FINAL_TEST_MS = 5.0
TEMPERATURE_C = 34.0
EK_MV = -101.0


def finite(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def validate_variant_catalog() -> None:
    if set(K_NAMES) != set(K_PINS):
        raise ValueError("The nine released K mechanisms and immutable source pins differ")
    for name in K_NAMES:
        spec = audit.SOURCES[name]
        pin = K_PINS[name]
        if int(spec["id"]) != pin["id"] or Path(spec["path"]).name != f"{name}.mod":
            raise ValueError(f"Unexpected Dataverse mapping for {name}: {spec}")
        if len(pin["sha1"]) != 40 or pin["bytes"] <= 0:
            raise ValueError(f"Missing source integrity pin for {name}")


def validate_original_protocol_sources(channel_tools: str) -> dict[str, Any]:
    """Require the voltage-clamp constants and helper calls in the released code."""
    functions = {
        name: audit.function_source(channel_tools, name)
        for name in (
            "K_IV_ss", "K_recovery_ss", "k_mech_IV", "runIk",
            "fit_boltz_act", "fit_boltz_inact", "get_tau_act",
            "get_tau_inact_double", "get_double_tau_rec",
        )
    }
    missing = [name for name, source in functions.items() if not source]
    if missing:
        raise ValueError(f"Original channel_tools.py functions are missing: {missing}")
    compact = {
        name: re.sub(r"\s+", "", source)
        for name, source in functions.items()
    }
    required = {
        "K_IV_ss": (
            "h.celsius=34",
            "steps_per_ms=10",
            "durs=[20,500,50,100]",
            "amps=[-140,0,60,-140]",
            "volts=np.arange(-110,60,10)",
            "mask=(t>20.4)&(t<520)",
            "mask=(t>520)&(t<570)",
            "get_tau_inact_double(x[pk:-1],y[pk:-1])",
        ),
        "K_recovery_ss": (
            "h.celsius=34",
            "steps_per_ms=2",
            "durs=[2,5000]",
            "amps=[-120,60]",
            "rectimes=np.linspace(2,92,10)**2",
            "volts=np.array([-80])",
            "durs=[2,5000,rectime,5]",
            "amps=[-120,40,v,40]",
            "get_double_tau_rec(rectimes,pulse2)",
        ),
        "k_mech_IV": (
            "cell.diam=10",
            "cell.insert(mechname)",
            "cell.Ra=200",
            "cell.cm=1",
            "cell.ek=-101",
        ),
    }
    absent = {
        function: [token for token in tokens if token not in compact[function]]
        for function, tokens in required.items()
    }
    absent = {key: value for key, value in absent.items() if value}
    if absent:
        raise ValueError(f"Released K protocol/setup source no longer matches expected constants: {absent}")
    return {
        "functions_verified": sorted(functions),
        "protocol_constants_verified": required,
        "source_function_sha256": {
            name: __import__("hashlib").sha256(source.encode("utf-8")).hexdigest()
            for name, source in functions.items()
        },
        "note": (
            "The original helper's K_IV_ss and K_recovery_ss bodies are inspected, "
            "while their loop outputs are captured with the same source runIk and "
            "curve-fit functions so full curves can be archived."
        ),
    }


def load_original_channel_tools(path: Path):
    import matplotlib
    matplotlib.use("Agg", force=True)
    spec = importlib.util.spec_from_file_location("wilbers_original_channel_tools", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the checksum-verified original channel_tools.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def compile_all_variants(payloads: dict[str, bytes], output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    for name in K_NAMES:
        (output / f"{name}.mod").write_bytes(payloads[name])
    compiler = shutil.which("nrnivmodl")
    if not compiler:
        raise RuntimeError("nrnivmodl is unavailable")
    result = subprocess.run(
        [compiler], cwd=output, text=True, capture_output=True, timeout=300
    )
    if result.returncode:
        raise RuntimeError(
            "Joint compilation of the nine unchanged K MOD files failed.\n"
            f"STDOUT:\n{result.stdout[-10000:]}\nSTDERR:\n{result.stderr[-10000:]}"
        )
    libraries = list(output.rglob("libnrnmech.so")) + list(output.rglob("libnrnmech.dylib"))
    if len(libraries) != 1:
        raise RuntimeError(f"Expected one joint NEURON mechanism library, found {libraries}")
    return libraries[0]


def create_original_k_cell(h, mechanism: str):
    cell = h.Section(name=f"cell_{mechanism}")
    # These are copied from channel_tools.k_mech_IV without changing the
    # original channel model or its parameter defaults.
    cell.diam = 10.0
    cell.insert(mechanism)
    cell.Ra = 200.0
    cell.cm = 1.0
    cell.ek = EK_MV
    getattr(cell(0.5), mechanism)
    return cell


def _safe_curve_fit(function, *args):
    try:
        result = function(*args)
        if isinstance(result, tuple):
            return tuple(finite(x) for x in result)
        return finite(result)
    except Exception:
        return tuple(None for _ in range(2)) if function.__name__ in (
            "get_tau_inact_double", "fit_boltz_act", "fit_boltz_inact",
            "get_double_tau_rec",
        ) else None


def run_original_k_iv_protocol(helper, h, cell) -> dict[str, Any]:
    """Replay original K_IV_ss protocol and expose its per-voltage arrays."""
    h.celsius = TEMPERATURE_C
    h.dt = K_IV_DT_MS
    durs = list(K_IV_DURS_MS)
    amps = list(K_IV_START_AMPS_MV)
    volts = np.asarray(K_IV_VOLTAGES_MV, dtype=float)
    tvec = h.Vector()
    tvec.record(h._ref_t)

    activation_conductance: list[float] = []
    inactivation_conductance: list[float] = []
    tau_activation: list[float | None] = []
    tau_inactivation_fast: list[float | None] = []
    tau_inactivation_slow: list[float | None] = []
    sample_counts: list[int] = []
    errors: list[dict[str, Any]] = []

    for voltage in volts:
        amps[1] = float(voltage)
        current = np.asarray(helper.runIk(cell, durs, amps), dtype=float).reshape(-1)
        time_axis = np.asarray(tvec, dtype=float).reshape(-1)
        if current.size != time_axis.size:
            raise RuntimeError(
                f"K_IV_ss at {voltage:g} mV: runIk returned {current.size} current samples "
                f"but original recorder produced {time_axis.size} time samples"
            )
        if not np.isfinite(current).all() or not np.isfinite(time_axis).all():
            raise RuntimeError(f"K_IV_ss at {voltage:g} mV produced non-finite current/time samples")
        sample_counts.append(int(current.size))

        # Original channel_tools.K_IV_ss: activation window and g = I/(V - ek).
        activation_mask = (time_axis > durs[0] + 0.4) & (time_axis < 520.0)
        if int(activation_mask.sum()) == 0:
            raise RuntimeError(f"K_IV_ss activation window is empty at {voltage:g} mV")
        conductance = current[activation_mask] / (float(voltage) - float(cell.ek))
        activation_conductance.append(float(np.max(conductance)))

        tau_act: float | None = None
        tau_fast: float | None = None
        tau_slow: float | None = None
        if float(np.max(current[activation_mask])) > 1e-8:
            x = time_axis[activation_mask]
            y = current[activation_mask]
            peak = int(np.argmax(y))
            tau_act = _safe_curve_fit(helper.get_tau_act, x[:peak], y[:peak])
            fit = _safe_curve_fit(helper.get_tau_inact_double, x[peak:-1], y[peak:-1])
            if isinstance(fit, tuple):
                tau_fast, tau_slow = fit
            else:
                tau_fast, tau_slow = None, None
        tau_activation.append(tau_act)
        tau_inactivation_fast.append(tau_fast)
        tau_inactivation_slow.append(tau_slow)

        # Original channel_tools.K_IV_ss: availability after the +60 mV step.
        inactivation_mask = (time_axis > 520.0) & (time_axis < 570.0)
        if int(inactivation_mask.sum()) == 0:
            raise RuntimeError(f"K_IV_ss inactivation window is empty at {voltage:g} mV")
        inactivation_current = current[inactivation_mask]
        inactivation_g = inactivation_current / (amps[2] - float(cell.ek))
        inactivation_conductance.append(float(np.max(inactivation_g)))

    act = np.asarray(activation_conductance, dtype=float)
    inact = np.asarray(inactivation_conductance, dtype=float)
    if not np.isfinite(act).all() or not np.isfinite(inact).all():
        raise RuntimeError("K_IV_ss produced a non-finite conductance curve")
    if float(np.max(act)) <= 0 or float(np.max(inact)) <= 0:
        raise RuntimeError("K_IV_ss conductance curves do not have a positive normalization maximum")
    act = act / float(np.max(act))
    inact = inact / float(np.max(inact))

    activation_fit = _safe_curve_fit(helper.fit_boltz_act, volts.copy(), act.copy())
    inactivation_mask = volts <= 0.0
    inactivation_fit = _safe_curve_fit(
        helper.fit_boltz_inact, volts[inactivation_mask].copy(), inact[inactivation_mask].copy()
    )
    if not isinstance(activation_fit, tuple):
        activation_fit = (None, None)
    if not isinstance(inactivation_fit, tuple):
        inactivation_fit = (None, None)

    return {
        "protocol": {
            "name": "original K_IV_ss",
            "temperature_c": TEMPERATURE_C,
            "dt_ms": K_IV_DT_MS,
            "durations_ms": list(K_IV_DURS_MS),
            "command_voltages_mV": list(K_IV_START_AMPS_MV),
            "test_voltage_grid_mV": volts.tolist(),
            "activation_window_ms": [20.4, 520.0],
            "inactivation_window_ms": [520.0, 570.0],
            "reversal_potential_mV": EK_MV,
            "samples_per_test_voltage": sample_counts,
        },
        "curves": {
            "G_Gmax_activation": act.tolist(),
            "G_Gmax_inactivation": inact.tolist(),
            "tau_activation_ms": tau_activation,
            "tau_inactivation_fast_ms": tau_inactivation_fast,
            "tau_inactivation_slow_ms": tau_inactivation_slow,
        },
        "fits": {
            "activation_vhalf_mV": finite(activation_fit[0]),
            "activation_slope_mV": finite(activation_fit[1]),
            "inactivation_vhalf_mV": finite(inactivation_fit[0]),
            "inactivation_slope_mV": finite(inactivation_fit[1]),
        },
        "fit_failures": errors,
    }


def run_original_k_recovery_protocol(helper, h, cell) -> dict[str, Any]:
    """Replay the original K_recovery_ss -80 mV recovery experiment."""
    h.celsius = TEMPERATURE_C
    h.dt = RECOVERY_DT_MS
    delays = np.asarray(RECOVERY_DELAYS_MS, dtype=float)
    tvec = h.Vector()
    tvec.record(h._ref_t)
    pulse2: list[float] = []
    sample_counts: list[int] = []

    for delay in delays:
        durs = [*RECOVERY_DURS_PREFIX_MS, float(delay), RECOVERY_FINAL_TEST_MS]
        amps = [-120.0, 40.0, RECOVERY_VOLTAGE_MV, 40.0]
        current = np.asarray(helper.runIk(cell, durs, amps), dtype=float).reshape(-1)
        time_axis = np.asarray(tvec, dtype=float).reshape(-1)
        if current.size != time_axis.size:
            raise RuntimeError(
                f"K_recovery_ss at {delay:g} ms: current/time lengths differ "
                f"({current.size}/{time_axis.size})"
            )
        if not np.isfinite(current).all() or not np.isfinite(time_axis).all():
            raise RuntimeError(f"K_recovery_ss at {delay:g} ms produced non-finite samples")
        sample_counts.append(int(current.size))
        mask = (
            (time_axis > 5002.0 + float(delay))
            & (time_axis < 5002.0 + float(delay) + RECOVERY_FINAL_TEST_MS)
        )
        if int(mask.sum()) == 0:
            raise RuntimeError(f"K_recovery_ss final test window is empty at delay {delay:g} ms")
        # Preserve the exact original source readout: maximum current in the
        # final 5-ms pulse, followed by get_double_tau_rec(rectimes, pulse2).
        pulse2.append(float(np.max(current[mask])))

    fit: tuple[float | None, float | None]
    try:
        result = helper.get_double_tau_rec(delays.copy(), np.asarray(pulse2, dtype=float))
        fit = tuple(finite(x) for x in result)
    except Exception as exc:
        fit = (None, None)
        fit_error = f"{type(exc).__name__}: {exc}"
    else:
        fit_error = None

    return {
        "protocol": {
            "name": "original K_recovery_ss",
            "temperature_c": TEMPERATURE_C,
            "dt_ms": RECOVERY_DT_MS,
            "hold_duration_ms": 2.0,
            "conditioning_voltage_mV": 40.0,
            "conditioning_duration_ms": 5000.0,
            "recovery_voltage_mV": RECOVERY_VOLTAGE_MV,
            "recovery_delays_ms": delays.tolist(),
            "final_test_voltage_mV": 40.0,
            "final_test_duration_ms": RECOVERY_FINAL_TEST_MS,
            "samples_per_delay": sample_counts,
        },
        "curves": {"test_pulse_peak_current": pulse2},
        "fits": {"recovery_fast_tau_ms": fit[0], "recovery_slow_tau_ms": fit[1]},
        "fit_error": fit_error,
    }


def target_curve_summary(targets: pd.DataFrame, species: str, variable: str) -> dict[float, dict[str, Any]]:
    subset = targets.loc[
        (targets["Species"] == species)
        & (targets["variable"] == variable)
        & (targets["included_in_author_statistics"] == True)  # noqa: E712
    ]
    output: dict[float, dict[str, Any]] = {}
    for voltage, group in subset.groupby("voltage_mV", dropna=True):
        values = pd.to_numeric(group["value"], errors="coerce").dropna().to_numpy(dtype=float)
        n = int(values.size)
        if not n:
            continue
        sd = float(np.std(values, ddof=1)) if n > 1 else None
        sem = float(sd / math.sqrt(n)) if sd is not None else None
        output[float(voltage)] = {
            "n_cells": n,
            "mean": float(np.mean(values)),
            "sd": sd,
            "sem": sem,
            "median": float(np.median(values)),
        }
    return output


def compare_curve_to_targets(
    model_values: list[float | None],
    model_voltages: list[float],
    targets: pd.DataFrame,
    species: str,
    variable: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    target = target_curve_summary(targets, species, variable)
    model_map = {float(v): finite(x) for v, x in zip(model_voltages, model_values)}
    rows: list[dict[str, Any]] = []
    errors: list[float] = []
    sem_z: list[float] = []
    within = 0
    for voltage in sorted(set(target).intersection(model_map)):
        model = model_map[voltage]
        expected = target[voltage]
        if model is None:
            continue
        error = model - expected["mean"]
        errors.append(error)
        if expected["sem"] is not None and expected["sem"] > 0:
            sem_z.append(abs(error) / expected["sem"])
            inside = abs(error) <= 1.96 * expected["sem"]
            within += int(inside)
        else:
            inside = None
        rows.append({
            "Species": species,
            "variable": variable,
            "voltage_mV": voltage,
            "n_target_cells": expected["n_cells"],
            "target_mean": expected["mean"],
            "target_sd": expected["sd"],
            "target_sem": expected["sem"],
            "model_value": model,
            "model_minus_target": error,
            "absolute_standardized_error_by_sem": (
                abs(error) / expected["sem"] if expected["sem"] is not None and expected["sem"] > 0 else None
            ),
            "within_pointwise_1_96_sem": inside,
        })
    if errors:
        metric = {
            "n_voltage_points": len(errors),
            "mae": float(np.mean(np.abs(errors))),
            "rmse": float(np.sqrt(np.mean(np.square(errors)))),
            "mean_bias": float(np.mean(errors)),
            "mean_absolute_error_in_sem_units": float(np.mean(sem_z)) if sem_z else None,
            "points_within_pointwise_1_96_sem": within,
            "within_sem_denominator": len(sem_z),
            "interpretation": "descriptive comparison; pointwise SEM overlap is not an inferential test",
        }
    else:
        metric = {
            "n_voltage_points": 0, "mae": None, "rmse": None, "mean_bias": None,
            "mean_absolute_error_in_sem_units": None,
            "points_within_pointwise_1_96_sem": 0, "within_sem_denominator": 0,
            "interpretation": "no common finite voltage points",
        }
    return metric, rows


def compare_scalar_target(
    model_value: float | None,
    targets: pd.DataFrame,
    species: str,
    variable: str,
) -> dict[str, Any]:
    subset = targets.loc[
        (targets["Species"] == species)
        & (targets["variable"] == variable)
        & (targets["included_in_author_statistics"] == True)  # noqa: E712
    ]
    values = pd.to_numeric(subset["value"], errors="coerce").dropna().to_numpy(dtype=float)
    model = finite(model_value)
    if values.size == 0 or model is None:
        return {"n_target_cells": int(values.size), "model_value": model, "target_mean": None, "delta": None, "z_by_sd": None}
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1)) if values.size > 1 else None
    return {
        "n_target_cells": int(values.size),
        "model_value": model,
        "target_mean": mean,
        "target_sd": sd,
        "target_sem": float(sd / math.sqrt(values.size)) if sd is not None else None,
        "delta_model_minus_target": model - mean,
        "z_by_sample_sd": (model - mean) / sd if sd is not None and sd > 0 else None,
    }


def compare_recovery_target(model_value: float | None, scalar_audit: dict[str, Any], species: str, key: str) -> dict[str, Any]:
    target = scalar_audit[species]["recovery"][key]
    model = finite(model_value)
    mean = finite(target.get("mean"))
    sd = finite(target.get("sd"))
    return {
        "n_target_cells": int(target.get("n", 0)),
        "model_value": model,
        "target_mean": mean,
        "target_sd": sd,
        "target_sem": finite(target.get("sem")),
        "delta_model_minus_target": model - mean if model is not None and mean is not None else None,
        "z_by_sample_sd": (model - mean) / sd if model is not None and mean is not None and sd is not None and sd > 0 else None,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty result CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.12g")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figure4-json", type=Path, default=FIGURE4_JSON)
    parser.add_argument("--per-recording-csv", type=Path, default=FIGURE4_PER_RECORDING)
    parser.add_argument("--output-json", type=Path, default=Path("results/wilbers_k_voltage_clamp_replay_2026-11-23.json"))
    parser.add_argument("--curves-csv", type=Path, default=Path("results/wilbers_k_voltage_clamp_model_curves_2026-11-23.csv"))
    parser.add_argument("--comparison-csv", type=Path, default=Path("results/wilbers_k_voltage_clamp_per_voltage_comparison_2026-11-23.csv"))
    parser.add_argument("--summary-csv", type=Path, default=Path("results/wilbers_k_voltage_clamp_summary_2026-11-23.csv"))
    args = parser.parse_args()

    validate_variant_catalog()
    figure4_audit = json.loads(args.figure4_json.read_text(encoding="utf-8"))
    if figure4_audit.get("status") != "official_figure4_voltage_clamp_workbook_verified_and_per_recording_audited":
        raise ValueError("Figure 4 target audit is missing or has an unexpected status")
    if figure4_audit.get("workbook", {}).get("source_sha256") != EXPECTED_FIGURE4_SHA256:
        raise ValueError("Figure 4 workbook SHA-256 differs from the independently audited version")
    if int(figure4_audit.get("measurement_row_count", -1)) != EXPECTED_FIGURE4_MEASUREMENTS:
        raise ValueError("Figure 4 per-recording target row count changed; review before comparing models")
    targets = pd.read_csv(args.per_recording_csv)
    if len(targets) != EXPECTED_FIGURE4_MEASUREMENTS:
        raise ValueError(f"Expected {EXPECTED_FIGURE4_MEASUREMENTS} audited Figure 4 target rows, got {len(targets)}")
    required_target_columns = {
        "Filename", "Species", "variable", "voltage_mV", "value",
        "included_in_author_statistics",
    }
    if not required_target_columns.issubset(targets.columns):
        raise ValueError(f"Audited Figure 4 CSV missing columns: {sorted(required_target_columns - set(targets.columns))}")
    if set(targets["Species"].dropna().unique()) != {"Human", "Mouse"}:
        raise ValueError("Figure 4 target cohorts are incomplete or unexpectedly pooled")

    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-independent-k-vc-") as temp:
        root = Path(temp)
        downloads = root / "downloads"
        downloads.mkdir()
        payloads: dict[str, bytes] = {}
        integrity: dict[str, Any] = {}
        fetch_names = [*K_NAMES, *SOURCE_NAMES]
        for name in fetch_names:
            spec = audit.SOURCES[name]
            payloads[name], integrity[name] = audit.fetch_verified(name, spec, downloads)

        for name in K_NAMES:
            pin = K_PINS[name]
            checked = integrity[name]
            if (
                int(checked["id"]) != pin["id"]
                or int(checked["bytes"]) != pin["bytes"]
                or str(checked["observed_sha1"]).lower() != pin["sha1"]
                or str(checked["official_sha1"]).lower() != pin["sha1"]
            ):
                raise RuntimeError(f"Released MOD source integrity failed for {name}")

        channel_tools_source = payloads["channel_tools"].decode("utf-8-sig")
        protocol_audit = validate_original_protocol_sources(channel_tools_source)
        helper_path = downloads / "channel_tools.py"
        helper_path.write_bytes(payloads["channel_tools"])
        helper = load_original_channel_tools(helper_path)

        mod_dir = root / "Mod"
        library = compile_all_variants(payloads, mod_dir)
        from neuron import h
        if h.nrn_load_dll(str(library)) == 0:
            raise RuntimeError("NEURON failed to load the joint original K MOD library")

        model_results: dict[str, Any] = {}
        model_failures: dict[str, str] = {}
        curve_rows: list[dict[str, Any]] = []
        comparison_rows: list[dict[str, Any]] = []
        summary_rows: list[dict[str, Any]] = []

        iv_vars = (
            "G_Gmax_activation",
            "G_Gmax_inactivation",
            "tau_activation_ms",
            "tau_inactivation_fast_ms",
            "tau_inactivation_slow_ms",
        )
        for name in K_NAMES:
            cell = None
            try:
                cell = create_original_k_cell(h, name)
                iv = run_original_k_iv_protocol(helper, h, cell)
                recovery = run_original_k_recovery_protocol(helper, h, cell)
                model_results[name] = {
                    "status": "completed",
                    "source_role": SOURCE_ROLES[name],
                    "source_mod_sha1": integrity[name]["observed_sha1"],
                    "source_mod_sha256": integrity[name]["sha256"],
                    "k_iv_ss": iv,
                    "k_recovery_ss": recovery,
                    "runtime_promotion": False,
                }
                for variable in iv_vars:
                    values = iv["curves"][variable]
                    for voltage, value in zip(iv["protocol"]["test_voltage_grid_mV"], values):
                        curve_rows.append({
                            "mechanism": name,
                            "source_role": SOURCE_ROLES[name],
                            "protocol": "K_IV_ss",
                            "variable": variable,
                            "voltage_mV": voltage,
                            "model_value": finite(value),
                        })
                for voltage, value in zip(
                    recovery["protocol"]["recovery_delays_ms"],
                    recovery["curves"]["test_pulse_peak_current"],
                ):
                    curve_rows.append({
                        "mechanism": name,
                        "source_role": SOURCE_ROLES[name],
                        "protocol": "K_recovery_ss",
                        "variable": "recovery_test_pulse_peak_current",
                        "voltage_mV": voltage,
                        "model_value": finite(value),
                    })
            except Exception as exc:
                model_failures[name] = f"{type(exc).__name__}: {exc}"
                model_results[name] = {
                    "status": "failed",
                    "source_role": SOURCE_ROLES[name],
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "runtime_promotion": False,
                }
            finally:
                if cell is not None:
                    try:
                        h.delete_section(sec=cell)
                    except Exception:
                        pass

        if model_failures:
            raise RuntimeError(f"One or more released mechanisms failed original voltage-clamp replay: {model_failures}")

        scalar_audit = figure4_audit["scalar_audit"]
        for name in K_NAMES:
            iv = model_results[name]["k_iv_ss"]
            recovery = model_results[name]["k_recovery_ss"]
            for species in ("Human", "Mouse"):
                for variable in iv_vars:
                    metric, detail_rows = compare_curve_to_targets(
                        iv["curves"][variable],
                        iv["protocol"]["test_voltage_grid_mV"],
                        targets,
                        species,
                        variable,
                    )
                    comparison_rows.extend([
                        {"mechanism": name, "source_role": SOURCE_ROLES[name], **row}
                        for row in detail_rows
                    ])
                    summary_rows.append({
                        "mechanism": name,
                        "source_role": SOURCE_ROLES[name],
                        "Species": species,
                        "endpoint": variable,
                        **metric,
                    })

                for variable, model_key in (
                    ("Vhalf_activation_mV", "activation_vhalf_mV"),
                    ("Vhalf_inactivation_mV", "inactivation_vhalf_mV"),
                ):
                    scalar = compare_scalar_target(iv["fits"][model_key], targets, species, variable)
                    summary_rows.append({
                        "mechanism": name,
                        "source_role": SOURCE_ROLES[name],
                        "Species": species,
                        "endpoint": variable,
                        "n_voltage_points": None,
                        "mae": abs(scalar["delta_model_minus_target"]) if scalar["delta_model_minus_target"] is not None else None,
                        "rmse": None,
                        "mean_bias": scalar["delta_model_minus_target"],
                        "mean_absolute_error_in_sem_units": (
                            abs(scalar["delta_model_minus_target"]) / scalar["target_sem"]
                            if scalar.get("target_sem") not in (None, 0) and scalar.get("delta_model_minus_target") is not None else None
                        ),
                        "points_within_pointwise_1_96_sem": None,
                        "within_sem_denominator": None,
                        "target_summary": scalar,
                    })

                for endpoint, key, fit_key in (
                    ("recovery_fast_tau_ms", "fast_tau_ms", "recovery_fast_tau_ms"),
                    ("recovery_slow_tau_ms", "slow_tau_ms", "recovery_slow_tau_ms"),
                ):
                    scalar = compare_recovery_target(
                        recovery["fits"][fit_key], scalar_audit, species, key
                    )
                    summary_rows.append({
                        "mechanism": name,
                        "source_role": SOURCE_ROLES[name],
                        "Species": species,
                        "endpoint": endpoint,
                        "n_voltage_points": None,
                        "mae": abs(scalar["delta_model_minus_target"]) if scalar["delta_model_minus_target"] is not None else None,
                        "rmse": None,
                        "mean_bias": scalar["delta_model_minus_target"],
                        "mean_absolute_error_in_sem_units": (
                            abs(scalar["delta_model_minus_target"]) / scalar["target_sem"]
                            if scalar.get("target_sem") not in (None, 0) and scalar.get("delta_model_minus_target") is not None else None
                        ),
                        "points_within_pointwise_1_96_sem": None,
                        "within_sem_denominator": None,
                        "target_summary": scalar,
                    })

        report = {
            "schema_version": 1,
            "status": "all_nine_released_k_mods_replayed_on_original_independent_voltage_clamp_protocols",
            "runtime_eligible": False,
            "dataset": figure4_audit["dataset"],
            "figure4_target_audit": {
                "workbook_sha256": EXPECTED_FIGURE4_SHA256,
                "measurement_rows": EXPECTED_FIGURE4_MEASUREMENTS,
                "cells_by_species": figure4_audit["workbook"]["table_audit"]["cells_by_species"],
                "subjects_by_species": figure4_audit["workbook"]["table_audit"]["subjects_by_species"],
            },
            "runtime": {
                "python": __import__("platform").python_version(),
                "neuron": __import__("neuron").__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
            },
            "source_integrity": integrity,
            "original_protocol_source_audit": protocol_audit,
            "joint_compilation": {
                "status": "success",
                "compiled_mechanisms": list(K_NAMES),
                "unchanged_mod_sources": True,
                "library": "single joint NEURON mechanism library",
            },
            "cell_setup": {
                "diameter_um": 10.0,
                "Ra_ohm_cm": 200.0,
                "Cm_uF_cm2": 1.0,
                "ek_mV": EK_MV,
                "length_um": "original NEURON default; not overridden by channel_tools.k_mech_IV",
            },
            "protocol_replay": {
                "K_IV_ss": {
                    "temperature_c": TEMPERATURE_C,
                    "dt_ms": K_IV_DT_MS,
                    "durations_ms": list(K_IV_DURS_MS),
                    "command_voltages_mV": list(K_IV_START_AMPS_MV),
                    "test_voltage_grid_mV": list(K_IV_VOLTAGES_MV),
                    "activation_window_ms": [20.4, 520.0],
                    "inactivation_window_ms": [520.0, 570.0],
                    "source_current": "original channel_tools.runIk",
                    "source_fits": [
                        "original channel_tools.get_tau_act",
                        "original channel_tools.get_tau_inact_double",
                        "original channel_tools.fit_boltz_act",
                        "original channel_tools.fit_boltz_inact",
                    ],
                },
                "K_recovery_ss": {
                    "temperature_c": TEMPERATURE_C,
                    "dt_ms": RECOVERY_DT_MS,
                    "conditioning_voltage_mV": 40.0,
                    "conditioning_duration_ms": 5000.0,
                    "recovery_voltage_mV": RECOVERY_VOLTAGE_MV,
                    "recovery_delays_ms": list(RECOVERY_DELAYS_MS),
                    "final_test_voltage_mV": 40.0,
                    "final_test_duration_ms": RECOVERY_FINAL_TEST_MS,
                    "source_current": "original channel_tools.runIk",
                    "source_fit": "original channel_tools.get_double_tau_rec",
                },
            },
            "models": model_results,
            "comparisons": comparison_rows,
            "summary_rows": summary_rows,
            "model_failures": model_failures,
            "scientific_limits": [
                "The original Dataverse K MOD source bytes were compiled unchanged; no model default or parameter was optimized.",
                "K_IV_ss and K_recovery_ss voltage commands, temperature, timestep, cell geometry and source current/fitting helpers are taken from the released channel_tools.py.",
                "The Figure 4 workbook contains per-recording derived measurements, not raw time-series current traces.",
                "Human and Mouse observations are summarized separately; individual cells are nested within 2 Human and 7 Mouse subject identifiers.",
                "Pointwise mean/SEM comparisons are descriptive. The small number of subjects prevents treating cell-level rows as fully independent biological replicates.",
                "The original helper's fit acceptance and numerical behavior are retained. A missing/failed tau fit is reported as unavailable, not silently imputed.",
                "The AP-clamp ranking is not used as a voltage-clamp fitting target; this is a separate protocol family.",
                "No MOD, fitted parameter default, AMSN runtime or production model is promoted by this experiment.",
            ],
        }

        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        write_csv(args.curves_csv, curve_rows)
        write_csv(args.comparison_csv, comparison_rows)
        write_csv(args.summary_csv, summary_rows)
        print(json.dumps({
            "status": report["status"],
            "compiled_mechanisms": len(K_NAMES),
            "replayed_mechanisms": sum(v.get("status") == "completed" for v in model_results.values()),
            "model_failures": model_failures,
            "figure4_cells": report["figure4_target_audit"]["cells_by_species"],
            "curve_rows": len(curve_rows),
            "per_voltage_comparison_rows": len(comparison_rows),
            "summary_rows": len(summary_rows),
            "output_json": str(args.output_json),
            "curves_csv": str(args.curves_csv),
            "comparison_csv": str(args.comparison_csv),
            "summary_csv": str(args.summary_csv),
        }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
