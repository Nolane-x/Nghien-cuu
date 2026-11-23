#!/usr/bin/env python3
"""Reproduce the original Wilbers 5-AP and 200-AP H_wide AP-clamp protocols.

All original source artifacts are downloaded by immutable Dataverse ID and
SHA-1/size checked. NEURON 9.0.2 executes the unchanged Na/K mechanism files
and the original 5/200-AP helper routines. In 200-AP mode only, the helper's
quadratic np.append current recorder is replaced by equivalent list-backed
recorders. Voltage commands, integration steps, channel equations and peak
thresholds are unchanged. No AMSN runtime code is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

BASE = "https://dataverse.nl/api"
FILES = {
    "trace": {
        "id": 318541, "path": "Figures5_6/APclamp/H_wide.csv",
        "bytes": 15095411, "sha1": "e209550ce746483de580459f7d8e40de91ec3667",
    },
    "na_workbook": {
        "id": 318668, "path": "Figure2/Na_data_fig2.xlsx",
        "bytes": 548562, "sha1": "cd702d7f1ca65b0b88a2565f289740546902e36b",
    },
    "k_workbook": {
        "id": 318669, "path": "Figure2/K_data_fig2.xlsx",
        "bytes": 302011, "sha1": "287720f8db3b20b167edd9e639dd67b0a1194def",
    },
    "amps_na": {
        "id": 318540, "path": "Figures5_6/APclamp/amps_na.csv",
        "bytes": 11751, "sha1": "75eb8b1b17becf31cac4d42869e44679bc9aa42a",
    },
    "amps_k": {
        "id": 318543, "path": "Figures5_6/APclamp/amps_k.csv",
        "bytes": 10297, "sha1": "7b7c6906d39fae9382f20deb310621fa48c07cf0",
    },
    "apclamp_tools": {
        "id": 318538, "path": "Figures5_6/APclamp/apclamp_tools.py",
        "bytes": 5082, "sha1": "be15b4567ada212035e33281ed097031c1a3cece",
    },
    "apclamp_na": {
        "id": 318544, "path": "Figures5_6/APclamp/apclamp_na.py",
        "bytes": 5856, "sha1": "912469a0c3a0da144657ce2c055cf326e0d5fd7e",
    },
    "apclamp_k": {
        "id": 318542, "path": "Figures5_6/APclamp/apclamp_k.py",
        "bytes": 1501, "sha1": "629098ed765e1a7b86b36180e7f9a5f9cf4f3ffe",
    },
    "na_human": {
        "id": 318629, "path": "Figures5_6/MOD/na_human.mod",
        "bytes": 3602, "sha1": "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    },
    "na_mouse": {
        "id": 318631, "path": "Figures5_6/MOD/na_mouse.mod",
        "bytes": 3616, "sha1": "f06a781f23a996fa3ecd6f7c68aacb12646e2f61",
    },
    "k_human": {
        "id": 318647, "path": "Figures5_6/MOD/k_human.mod",
        "bytes": 4220, "sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
    },
    "k_mouse": {
        "id": 318649, "path": "Figures5_6/MOD/k_mouse.mod",
        "bytes": 4189, "sha1": "1d83124eefc45aa7321a5a21337f080c2519ceed",
    },
}

K_HUMAN_FINAL_FIT_SNAPSHOT = {
    "thi1": 20.386620488986296,
    "thi2": -84.16487679230283,
    "qi1": 25.748310780322146,
    "qi2": 6.809126450666186,
    "Rd": 0.0009968112992653684,
    "Rg": 0.0004388884380488172,
}
K_HUMAN_FINAL_FIT_SNAPSHOT_SOURCE = {
    "dataset_doi": "10.34894/L5J0SD",
    "fit_file_id": 326237,
    "fit_file_sha1": "c819e59813acd70fae7af7151752bb1d8bbc7357",
    "fit_file_sha256": "842cbfffc8031b8fa03044cd862494474f55ccc2ac2493a2cf5bc3a1fa99958c",
    "canonical_mod_file_id": 318647,
    "canonical_mod_sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
    "canonical_mod_sha256": "899aa0dfa697b7f735258e10b002c8876c108902afc0f9fc4bc1963f6caee5",
    "status": "unapplied trailing final-best-fit dictionary; sensitivity only",
}

SAMPLE_FREQ_PER_MS = 125
SAMPLE_RATE_HZ = 125000
TIME_START_MS = 199
AP_INTERVAL_MS = 25
AP_POST_WINDOW_MS = 7
NA_VOLTAGE_OFFSET_MV = -10.0


def protocol_end_ms(ap_count: int) -> int:
    if ap_count not in (5, 200):
        raise ValueError("ap_count must be 5 or 200")
    return 200 + AP_INTERVAL_MS * (ap_count - 1) + AP_POST_WINDOW_MS


def expected_protocol_samples(ap_count: int) -> int:
    return (
        round(protocol_end_ms(ap_count) * SAMPLE_FREQ_PER_MS) + 1
        - round(TIME_START_MS * SAMPLE_FREQ_PER_MS)
    )


def fetch_verified(name: str, spec: dict[str, Any], cache: Path) -> tuple[bytes, dict[str, Any]]:
    metadata_url = f"{BASE}/files/{spec['id']}"
    metadata_attempts = []
    metadata = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                metadata_url,
                headers={
                    "User-Agent": "AMSN-Wilbers-APclamp-reproduction/1.0",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type")
                status_code = getattr(response, "status", None)
            if not body:
                raise ValueError("Dataverse metadata endpoint returned an empty body")
            parsed = json.loads(body)
            metadata = parsed["data"]["dataFile"]
            metadata_attempts.append({
                "attempt": attempt + 1,
                "status": status_code,
                "content_type": content_type,
                "body_bytes": len(body),
                "result": "success",
            })
            break
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            metadata_attempts.append({
                "attempt": attempt + 1,
                "error": repr(exc),
            })
            if attempt < 4:
                time.sleep((1.5, 3.0, 6.0, 10.0)[attempt])
    if metadata is None:
        raise RuntimeError(
            f"Dataverse metadata unavailable for {name} after 5 attempts: "
            + json.dumps(metadata_attempts, sort_keys=True)
        )

    official_sha1 = metadata["checksum"]["value"]
    official_bytes = int(metadata["filesize"])
    if official_sha1 != spec["sha1"] or official_bytes != spec["bytes"]:
        raise RuntimeError(
            f"Dataverse metadata mismatch for {name}: "
            f"sha1={official_sha1}, bytes={official_bytes}"
        )

    attempts = []
    urls = (
        f"{BASE}/access/datafile/{spec['path']}/{spec['id']}",
        f"{BASE}/access/datafile/{spec['id']}",
    )
    for url in urls:
        accepted = False
        for attempt in range(3):
            request = urllib.request.Request(url, headers={
                "User-Agent": "AMSN-Wilbers-APclamp-reproduction/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept": "*/*",
            })
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    payload = response.read()
                    content_type = response.headers.get("Content-Type")
                    final_url = response.url.split("?", 1)[0]
                    status_code = getattr(response, "status", None)
                if not payload:
                    raise ValueError("Dataverse data endpoint returned an empty body")
                sha1 = hashlib.sha1(payload).hexdigest()
                sha256 = hashlib.sha256(payload).hexdigest()
                observation = {
                    "url": url,
                    "attempt": attempt + 1,
                    "final_url": final_url,
                    "status": status_code,
                    "bytes": len(payload),
                    "content_type": content_type,
                    "sha1": sha1,
                    "sha256": sha256,
                }
                attempts.append(observation)
                if len(payload) == spec["bytes"] and sha1 == official_sha1:
                    (cache / name).write_bytes(payload)
                    return payload, {
                        "official_sha1": official_sha1,
                        "official_bytes": official_bytes,
                        "observed_sha1": sha1,
                        "observed_sha256": sha256,
                        "metadata_attempts": metadata_attempts,
                        "download_attempts": attempts,
                    }
                if attempt < 2:
                    time.sleep((2.0, 5.0)[attempt])
                else:
                    accepted = False
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                ValueError,
            ) as exc:
                attempts.append({"url": url, "attempt": attempt + 1, "error": repr(exc)})
                if attempt < 2:
                    time.sleep((2.0, 5.0)[attempt])
        if accepted:
            break
    raise RuntimeError(
        f"Download did not match official Dataverse SHA-1 for {name}: "
        + json.dumps({"metadata_attempts": metadata_attempts, "download_attempts": attempts}, sort_keys=True)
    )


def load_original_helper(path: Path, ap_count: int = 5) -> Any:
    spec = importlib.util.spec_from_file_location("wilbers_apclamp_tools_original", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create Python import spec for original apclamp_tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    required = ["init_na", "init_k"]
    required.extend(("Ina_AP1_5", "Ik_AP1_5") if ap_count == 5 else ("Ina_AP1_5_200", "Ik_AP1_5_200"))
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise RuntimeError(f"Original helper module missing functions for {ap_count}-AP replay: {missing}")
    return module


def install_linear_current_recorders(helper: Any, h: Any) -> dict[str, Any]:
    """Replace only np.append's quadratic copying with equivalent list storage."""
    def record_na(cell: Any, command: Any, samplefreq: int = 125000) -> np.ndarray:
        h.celsius = 34
        h.dt = 1000 / samplefreq
        command_vector = h.Vector(command)
        clamp = h.VClamp(cell(0.5))
        clamp.dur[0] = len(command) * h.dt
        command_vector.play(clamp._ref_amp[0], h.dt)
        h.finitialize(command[0])
        current = []
        while h.t <= clamp.dur[0]:
            h.fadvance()
            current.append(float(cell.ina))
        return np.asarray(current, dtype=float)

    def record_k(cell: Any, command: Any, samplefreq: int = 125000) -> np.ndarray:
        h.celsius = 34
        h.dt = 1000 / samplefreq
        command_vector = h.Vector(command)
        clamp = h.VClamp(cell(0.5))
        clamp.dur[0] = len(command) * h.dt
        command_vector.play(clamp._ref_amp[0], h.dt)
        h.finitialize(command[0])
        current = []
        while h.t <= clamp.dur[0]:
            h.fadvance()
            current.append(float(cell.ik))
        return np.asarray(current, dtype=float)

    required = ("APclamp", "APclamp_k")
    missing = [name for name in required if not hasattr(helper, name)]
    if missing:
        raise RuntimeError(f"Original helper is missing APclamp recorders: {missing}")
    helper.APclamp = record_na
    helper.APclamp_k = record_k
    return {
        "enabled": True,
        "replaced_helpers": ["APclamp", "APclamp_k"],
        "channel_equations_modified": False,
        "voltage_clamp_command_modified": False,
        "integration_step_modified": False,
        "peak_detection_modified": False,
        "reason": "Avoid O(n^2) np.append array reallocations for the 200-AP waveform.",
    }


def finite_summary(values: Any) -> dict[str, Any]:
    array = np.asarray(values, dtype=float).reshape(-1)
    finite = array[np.isfinite(array)]
    return {
        "count": int(array.size),
        "finite_count": int(finite.size),
        "nonfinite_count": int(array.size - finite.size),
        "values": [float(x) if np.isfinite(x) else None for x in array],
        "minimum": float(finite.min()) if finite.size else None,
        "maximum": float(finite.max()) if finite.size else None,
    }


def normalized(values: Any, by: str) -> list[float | None]:
    array = np.asarray(values, dtype=float).reshape(-1)
    finite = array[np.isfinite(array)]
    if not finite.size:
        return [None] * int(array.size)
    denominator = float(array[0]) if by == "first" else float(np.nanmax(array))
    if not math.isfinite(denominator) or abs(denominator) < 1e-30:
        return [None] * int(array.size)
    return [float(x / denominator) if np.isfinite(x) else None for x in array]


def validate_linear_current_recorder_equivalence(
    helper: Any,
    h: Any,
    source_trace: np.ndarray,
) -> dict[str, Any]:
    """Prove list-backed current sampling preserves the original 5-AP helper output."""
    start = round(TIME_START_MS * SAMPLE_FREQ_PER_MS)
    end_ms = protocol_end_ms(5)
    end = round(end_ms * SAMPLE_FREQ_PER_MS) + 1
    command = np.asarray(source_trace[start:end], dtype=float)
    if command.size != expected_protocol_samples(5):
        raise RuntimeError("Could not extract the expected five-AP command for recorder equivalence")
    time_axis = np.linspace(TIME_START_MS, end_ms, len(command))
    outputs: dict[str, np.ndarray] = {}

    # First run uses both original np.append-based APclamp recorders unchanged.
    for ion, voltage in (("na", command + NA_VOLTAGE_OFFSET_MV), ("k", command.copy())):
        for species in ("human", "mouse"):
            section = None
            try:
                section = helper.init_na(f"na_{species}") if ion == "na" else helper.init_k(f"k_{species}")
                result = (
                    helper.Ina_AP1_5(section, time_axis, voltage)
                    if ion == "na" else helper.Ik_AP1_5(section, time_axis, voltage)
                )
                outputs[f"{ion}_{species}"] = np.asarray(result, dtype=float).reshape(-1)
            finally:
                if section is not None:
                    h.delete_section(sec=section)
                try:
                    import matplotlib.pyplot as plt
                    plt.close("all")
                except Exception:
                    pass

    # Replace only the two recorder functions with the optimized implementation.
    recorder_info = install_linear_current_recorders(helper, h)
    comparisons = {}
    for ion, voltage in (("na", command + NA_VOLTAGE_OFFSET_MV), ("k", command.copy())):
        for species in ("human", "mouse"):
            section = None
            try:
                section = helper.init_na(f"na_{species}") if ion == "na" else helper.init_k(f"k_{species}")
                result = (
                    helper.Ina_AP1_5(section, time_axis, voltage)
                    if ion == "na" else helper.Ik_AP1_5(section, time_axis, voltage)
                )
                optimized = np.asarray(result, dtype=float).reshape(-1)
                original = outputs[f"{ion}_{species}"]
                if optimized.shape != original.shape:
                    raise RuntimeError(
                        f"{ion}_{species} recorder length changed: {optimized.size} vs {original.size}"
                    )
                if not np.allclose(optimized, original, rtol=1e-12, atol=1e-12, equal_nan=True):
                    max_abs = float(np.nanmax(np.abs(optimized - original)))
                    raise RuntimeError(
                        f"{ion}_{species} list-backed recorder changed AP amplitudes; max abs diff={max_abs}"
                    )
                comparisons[f"{ion}_{species}"] = {
                    "status": "identical_within_1e-12",
                    "ap_count": int(optimized.size),
                    "max_absolute_amplitude_difference": float(np.nanmax(np.abs(optimized - original))),
                }
            finally:
                if section is not None:
                    h.delete_section(sec=section)
                try:
                    import matplotlib.pyplot as plt
                    plt.close("all")
                except Exception:
                    pass

    return {
        "status": "passed",
        "protocol": "original first-five-AP command, identical to the source 5-AP slice",
        "recorder_optimization": recorder_info,
        "comparison_tolerance": {"rtol": 1e-12, "atol": 1e-12},
        "model_comparisons": comparisons,
    }


def execute_model(
    helper: Any, h: Any, ion: str, species: str,
    trace: np.ndarray, t: np.ndarray, ap_count: int = 5,
    parameter_overrides: dict[str, float] | None = None,
) -> dict[str, Any]:
    cell = None
    applied_overrides: dict[str, float] = {}
    try:
        if ion == "na":
            cell = helper.init_na(f"na_{species}")
            mechanism = getattr(cell(0.5), f"na_{species}")
            amplitudes = helper.Ina_AP1_5(cell, t, trace) if ap_count == 5 else helper.Ina_AP1_5_200(cell, t, trace)
            normalization = "AP1 (same as original Na source plot)"
        else:
            cell = helper.init_k(f"k_{species}")
            mechanism = getattr(cell(0.5), f"k_{species}")
            if parameter_overrides:
                if species != "human":
                    raise ValueError("Archived fit snapshot applies only to human K")
                for name, value in parameter_overrides.items():
                    if not hasattr(mechanism, name):
                        raise RuntimeError(f"k_human mechanism does not expose {name}")
                    setattr(mechanism, name, float(value))
                    applied_overrides[name] = float(getattr(mechanism, name))
                    if not math.isclose(applied_overrides[name], float(value), rel_tol=0, abs_tol=1e-12):
                        raise RuntimeError(f"Failed to apply fit snapshot parameter {name}")
            amplitudes = helper.Ik_AP1_5(cell, t, trace) if ap_count == 5 else helper.Ik_AP1_5_200(cell, t, trace)
            normalization = "maximum amplitude (same as original K source plot)"
        if len(amplitudes) != ap_count:
            raise RuntimeError(f"Original helper returned {len(amplitudes)} amplitudes for {ap_count} APs")
        summary = finite_summary(amplitudes)
        return {
            "status": "completed",
            "mechanism": f"{ion}_{species}",
            "amplitude": summary,
            "normalized": normalized(amplitudes, "first" if ion == "na" else "max"),
            "normalization": normalization,
            "parameter_overrides_applied": applied_overrides,
        }
    except Exception as exc:
        return {
            "status": "error",
            "mechanism": f"{ion}_{species}",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    finally:
        if cell is not None:
            try:
                h.delete_section(sec=cell)
            except Exception:
                pass


def summarize_experimental_csv(payload: bytes, ion: str, ap_count: int = 5) -> dict[str, Any]:
    from io import BytesIO
    frame = pd.read_csv(BytesIO(payload))
    output: dict[str, Any] = {
        "columns": list(frame.columns),
        "rows": int(len(frame)),
    }
    if ion == "na":
        required = {"Species", "APnr", "relative_amp"}
        if required.issubset(frame.columns):
            selected = frame.loc[frame["APnr"] <= ap_count]
            output["by_species"] = {
                str(species): {
                    "n": int(len(group)),
                    "mean_by_ap": {
                        str(int(ap)): float(value)
                        for ap, value in group.groupby("APnr")["relative_amp"].mean().items()
                    },
                }
                for species, group in selected.groupby("Species")
            }
    else:
        required = {"species", "APnr", "amp"}
        if required.issubset(frame.columns):
            selected = frame.loc[frame["APnr"] <= ap_count]
            output["by_species"] = {
                str(species): {
                    "n": int(len(group)),
                    "mean_by_ap": {
                        str(int(ap)): float(value)
                        for ap, value in group.groupby("APnr")["amp"].mean().items()
                    },
                }
                for species, group in selected.groupby("species")
            }
    return output



def compare_curve(model: Any, experiment: Any) -> dict[str, Any]:
    model_values = np.asarray(model, dtype=float).reshape(-1)
    experiment_values = np.asarray(experiment, dtype=float).reshape(-1)
    if model_values.size != experiment_values.size:
        raise ValueError("Model and experimental AP series have different lengths")
    finite = np.isfinite(model_values) & np.isfinite(experiment_values)
    if not finite.any():
        return {"n": 0, "mae": None, "rmse": None, "max_abs_error": None, "difference": []}
    difference = model_values[finite] - experiment_values[finite]
    return {
        "n": int(finite.sum()),
        "mae": float(np.mean(np.abs(difference))),
        "rmse": float(np.sqrt(np.mean(difference**2))),
        "max_abs_error": float(np.max(np.abs(difference))),
        "difference": [float(x) for x in difference],
    }


def normalize_by_first(values: Any) -> list[float | None]:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size == 0 or not np.isfinite(array[0]) or abs(float(array[0])) < 1e-30:
        return [None] * int(array.size)
    return [float(value / array[0]) if np.isfinite(value) else None for value in array]


def summarize_model_vs_experiment(
    models: dict[str, Any],
    amps_na_payload: bytes,
    amps_k_payload: bytes,
    ap_count: int = 5,
) -> dict[str, Any]:
    from io import BytesIO

    na_frame = pd.read_csv(BytesIO(amps_na_payload))
    k_frame = pd.read_csv(BytesIO(amps_k_payload))
    comparisons: dict[str, Any] = {}
    for species, source_species in (("human", "Human"), ("mouse", "Mouse")):
        exp = (
            na_frame.loc[na_frame["Species"] == source_species]
            .loc[na_frame["APnr"] <= ap_count]
            .groupby("APnr")["relative_amp"]
            .mean()
            .reindex(range(1, ap_count + 1))
            .to_numpy(dtype=float)
        )
        model = models[f"na_{species}"]
        model_curve = model["normalized"]
        comparisons[f"na_{species}"] = {
            "source_plot_normalization": "divide modeled peak amplitude by AP1",
            "model_normalized_curve": model_curve,
            "experimental_recording_mean_curve": [float(x) for x in exp],
            "source_normalization_metrics": compare_curve(model_curve, exp),
        }

    for species, source_species in (("human", "H"), ("mouse", "M")):
        exp = (
            k_frame.loc[k_frame["species"] == source_species]
            .loc[k_frame["APnr"] <= ap_count]
            .groupby("APnr")["amp"]
            .mean()
            .reindex(range(1, ap_count + 1))
            .to_numpy(dtype=float)
        )
        model = models[f"k_{species}"]
        source_curve = model["normalized"]
        raw_values = model["amplitude"]["values"]
        ap1_curve = normalize_by_first(raw_values)
        comparisons[f"k_{species}"] = {
            "source_plot_normalization": "divide modeled amplitude by maximum modeled amplitude",
            "model_normalized_curve_source_exact": source_curve,
            "experimental_recording_mean_curve": [float(x) for x in exp],
            "source_normalization_metrics": compare_curve(source_curve, exp),
            "additional_shape_only_check": {
                "normalization": "divide modeled amplitude by model AP1; not the original potassium script",
                "model_normalized_curve": ap1_curve,
                "metrics": compare_curve(ap1_curve, exp),
            },
            "normalization_warning": (
                "The original potassium script normalizes model output by its maximum, "
                "while the experimental amp column has AP1 mean 1.0 in the released data. "
                "The model's largest response occurs at AP2; preserve the source's exact "
                "normalization and report AP1-normalized shape comparison separately."
            ),
        }
    return {
        "ap_range": [1, ap_count],
        "source_experimental_grouping": {
            "na": "amps_na.csv Species; means across the five AP-clamp recordings per species",
            "k": "amps_k.csv species; H_wide command waveform, means across recordings",
        },
        "comparisons": comparisons,
        "interpretation": (
            f"MAE/RMSE compare the exact {ap_count}-AP replay from a single shared voltage command "
            "with the released per-recording experimental means. The experimental means "
            "summarize recordings, while the model curve is one deterministic single-compartment "
            "simulation; these are descriptive discrepancies, not inferential statistics."
        ),
    }



def parse_na_workbook_header(value: Any) -> tuple[str, int] | None:
    match = re.fullmatch(r"relative_amp_(Hnarrow|Hwide)_\s*(\d+)", str(value).strip())
    return (match.group(1), int(match.group(2))) if match else None


def parse_k_workbook_header(value: Any) -> tuple[str, int] | None:
    normalized = str(value).replace(" ", "").strip()
    match = re.fullmatch(r"amp_h_n_(\d+)", normalized)
    return ("h", int(match.group(1))) if match else None


def workbook_group_curve(
    frame: pd.DataFrame,
    columns_by_ap: dict[int, str],
    selected: pd.DataFrame,
    ap_count: int,
) -> list[dict[str, Any]]:
    output = []
    for ap in range(1, ap_count + 1):
        col = columns_by_ap[ap]
        values = pd.to_numeric(selected[col], errors="coerce").dropna().to_numpy(dtype=float)
        n = int(values.size)
        sd = float(np.std(values, ddof=1)) if n > 1 else 0.0 if n == 1 else None
        sem = float(sd / math.sqrt(n)) if n and sd is not None else None
        output.append({
            "ap": ap,
            "n_recordings": n,
            "mean": float(np.mean(values)) if n else None,
            "median": float(np.median(values)) if n else None,
            "sd": sd,
            "sem": sem,
            "min": float(np.min(values)) if n else None,
            "max": float(np.max(values)) if n else None,
        })
    return output


def summarize_model_vs_original_workbooks(
    models: dict[str, Any],
    na_workbook_payload: bytes,
    k_workbook_payload: bytes,
    ap_count: int,
) -> dict[str, Any]:
    """Compare model curves with each recording in the original Figure 2 workbooks."""
    from io import BytesIO

    na_frame = pd.read_excel(BytesIO(na_workbook_payload), sheet_name="data")
    k_frame = pd.read_excel(BytesIO(k_workbook_payload), sheet_name="data")

    na_columns: dict[str, dict[int, str]] = {"Hnarrow": {}, "Hwide": {}}
    for column in na_frame.columns:
        parsed = parse_na_workbook_header(column)
        if parsed:
            group, ap = parsed
            na_columns[group][ap] = str(column)
    for group, mapping in na_columns.items():
        missing = sorted(set(range(1, ap_count + 1)) - set(mapping))
        if missing:
            raise RuntimeError(f"Na workbook group {group} missing AP columns: {missing[:10]}")

    na_species = na_frame["Filename"].astype(str).map(
        lambda filename: "Mouse" if filename.startswith("M") else "Human"
    )
    comparisons: dict[str, Any] = {}
    for waveform in ("Hnarrow", "Hwide"):
        for species in ("Human", "Mouse"):
            selected = na_frame.loc[na_species == species]
            rows = workbook_group_curve(selected, na_columns[waveform], selected, ap_count)
            model_curve = models[f"na_{species.lower()}"]["normalized"]
            experiment_mean = [row["mean"] for row in rows]
            metrics = compare_curve(model_curve, experiment_mean)
            valid = [
                abs(float(model_curve[i]) - float(rows[i]["mean"])) <= 1.96 * float(rows[i]["sem"])
                for i in range(ap_count)
                if rows[i]["sem"] is not None and rows[i]["mean"] is not None
            ]
            comparisons[f"na_{species.lower()}_{waveform.lower()}"] = {
                "cell_species": species,
                "waveform_group": waveform,
                "waveform_group_interpretation": (
                    "Main Figure 2 group" if waveform == "Hnarrow"
                    else "Raw Hwide candidate; retained separately because the source workbook descriptions for Hwide and Mwide conflict"
                ),
                "recording_count": int(selected["Filename"].nunique()),
                "model_normalization": "AP1",
                "model_curve": model_curve,
                "experimental_per_ap": rows,
                "metrics_vs_recording_mean": metrics,
                "model_points_within_mean_plus_minus_1_96_sem": int(sum(valid)),
                "fraction_points_within_mean_plus_minus_1_96_sem": float(sum(valid) / len(valid)) if valid else None,
                "ap200_model": model_curve[-1],
                "ap200_experimental_mean": rows[-1]["mean"],
                "ap200_experimental_sem": rows[-1]["sem"],
            }

    k_columns: dict[int, str] = {}
    for column in k_frame.columns:
        parsed = parse_k_workbook_header(column)
        if parsed and parsed[1] <= ap_count:
            k_columns[parsed[1]] = str(column)
    missing = sorted(set(range(1, ap_count + 1)) - set(k_columns))
    if missing:
        raise RuntimeError(f"K workbook normalized human-input columns missing APs: {missing[:10]}")

    for code, species in (("H", "Human"), ("M", "Mouse")):
        selected = k_frame.loc[k_frame["species"].astype(str) == code]
        rows = workbook_group_curve(selected, k_columns, selected, ap_count)
        model_raw = models[f"k_{species.lower()}"]["amplitude"]["values"]
        model_curve = normalize_by_first(model_raw)
        experiment_mean = [row["mean"] for row in rows]
        metrics = compare_curve(model_curve, experiment_mean)
        valid = [
            abs(float(model_curve[i]) - float(rows[i]["mean"])) <= 1.96 * float(rows[i]["sem"])
            for i in range(ap_count)
            if rows[i]["sem"] is not None and rows[i]["mean"] is not None
        ]
        comparisons[f"k_{species.lower()}_human_input"] = {
            "cell_species": species,
            "waveform_group": "human input waveform (amp_h_n_ columns)",
            "recording_count": int(selected["Filename"].nunique()),
            "model_normalization": "AP1, matching workbook normalized columns",
            "model_curve": model_curve,
            "experimental_per_ap": rows,
            "metrics_vs_recording_mean": metrics,
            "model_points_within_mean_plus_minus_1_96_sem": int(sum(valid)),
            "fraction_points_within_mean_plus_minus_1_96_sem": float(sum(valid) / len(valid)) if valid else None,
            "ap200_model": model_curve[-1],
            "ap200_experimental_mean": rows[-1]["mean"],
            "ap200_experimental_sem": rows[-1]["sem"],
        }

    return {
        "comparison_source": {
            "na": "Na_data_fig2.xlsx, per-recording relative_amp columns, Hnarrow and Hwide retained separately",
            "k": "K_data_fig2.xlsx, per-recording amp_h_n_ normalized human-input columns",
        },
        "ap_range": [1, ap_count],
        "comparisons": comparisons,
        "caveat": (
            "The Hwide AP-command and Na workbook group mapping is not silently assumed. Both Hnarrow (the main published Figure 2 group, which matches the legacy amps_na.csv curve) and Hwide (the candidate matching the raw trace filename) are reported. K uses the explicit normalized human-input condition. CI-band overlap is a descriptive pointwise check, not a simultaneous confidence band or hypothesis test."
        ),
    }



def compare_k_fit_snapshot_with_workbook(
    model: dict[str, Any], workbook_payload: bytes, ap_count: int
) -> dict[str, Any]:
    from io import BytesIO
    frame = pd.read_excel(BytesIO(workbook_payload), sheet_name="data")
    columns: dict[int, str] = {}
    for column in frame.columns:
        parsed = parse_k_workbook_header(column)
        if parsed and parsed[1] <= ap_count:
            columns[parsed[1]] = str(column)
    if sorted(columns) != list(range(1, ap_count + 1)):
        raise RuntimeError("K human-input workbook columns are incomplete for fit-snapshot comparison")
    selected = frame.loc[frame["species"].astype(str) == "H"]
    rows = workbook_group_curve(selected, columns, selected, ap_count)
    model_curve = normalize_by_first(model["amplitude"]["values"])
    experiment = [row["mean"] for row in rows]
    metrics = compare_curve(model_curve, experiment)
    inband = [
        abs(float(model_curve[i]) - float(rows[i]["mean"])) <= 1.96 * float(rows[i]["sem"])
        for i in range(ap_count)
        if rows[i]["sem"] is not None and rows[i]["mean"] is not None
    ]
    return {
        "recording_count": int(selected["Filename"].nunique()),
        "normalization": "model AP1-normalized against workbook amp_h_n_ series",
        "model_curve": model_curve,
        "experimental_per_ap": rows,
        "metrics_vs_recording_mean": metrics,
        "model_points_within_mean_plus_minus_1_96_sem": int(sum(inband)),
        "ap5_model": model_curve[4] if ap_count >= 5 else None,
        "ap5_experiment": rows[4]["mean"] if ap_count >= 5 else None,
        "ap200_model": model_curve[-1],
        "ap200_experiment": rows[-1]["mean"],
        "ap200_sem": rows[-1]["sem"],
        "ap200_delta_model_minus_experiment": float(model_curve[-1] - rows[-1]["mean"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-apclamp-replay.json"))
    parser.add_argument("--ap-count", type=int, choices=(5, 200), default=5)
    args = parser.parse_args()
    ap_count = args.ap_count
    time_end_ms = protocol_end_ms(ap_count)

    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-apclamp-") as tmp:
        root = Path(tmp)
        cache = root / "downloaded"
        cache.mkdir()
        payloads, integrity = {}, {}
        for name, spec in FILES.items():
            payloads[name], integrity[name] = fetch_verified(name, spec, cache)

        trace = np.loadtxt(BytesIO(payloads["trace"]), delimiter=",", skiprows=1)
        trace = np.asarray(trace)
        if trace.ndim == 2 and trace.shape[1] == 1:
            trace = trace[:, 0]
        if trace.ndim != 1:
            raise RuntimeError(f"Original trace loader expects a 1-D csv; observed shape {trace.shape}")
        peak_indices, peak_props = find_peaks(trace, prominence=50)
        start_index = round(TIME_START_MS * SAMPLE_FREQ_PER_MS)
        end_index = round(time_end_ms * SAMPLE_FREQ_PER_MS) + 1
        source_slice = trace[start_index:end_index]
        expected_samples = expected_protocol_samples(ap_count)
        if len(source_slice) != expected_samples:
            raise RuntimeError(
                f"Expected the {ap_count}-AP source window to contain {expected_samples} samples, got {len(source_slice)}"
            )
        command_peaks = find_peaks(source_slice, prominence=50)[0]
        if len(command_peaks) != ap_count:
            raise RuntimeError(
                f"Expected exactly {ap_count} voltage-command AP peaks, got {len(command_peaks)}"
            )
        t = np.linspace(TIME_START_MS, time_end_ms, len(source_slice))
        na_trace = source_slice + NA_VOLTAGE_OFFSET_MV
        k_trace = source_slice.copy()

        # Compile the four untouched source mechanisms exactly as the source
        # script compiles the shared MOD directory.
        mod_dir = root / "Mod"
        mod_dir.mkdir()
        for name in ("na_human", "na_mouse", "k_human", "k_mouse"):
            (mod_dir / f"{name}.mod").write_bytes(payloads[name])
        compiler = shutil.which("nrnivmodl")
        if compiler is None:
            raise RuntimeError("nrnivmodl missing; NEURON is not installed")
        build = subprocess.run([compiler], cwd=mod_dir, text=True, capture_output=True, timeout=240)
        if build.returncode:
            raise RuntimeError(
                f"Original human/mouse mechanisms failed to compile.\n"
                f"STDOUT:\n{build.stdout[-10000:]}\nSTDERR:\n{build.stderr[-10000:]}"
            )
        libs = list(mod_dir.rglob("libnrnmech.so")) or list(mod_dir.rglob("libnrnmech.dylib"))
        if len(libs) != 1:
            raise RuntimeError(f"Expected one compiled NEURON library, found {libs}")

        from neuron import h
        if h.nrn_load_dll(str(libs[0])) == 0:
            raise RuntimeError("NEURON failed to load the compiled source mechanisms")
        helper_path = cache / "apclamp_tools.py"
        helper_path.write_bytes(payloads["apclamp_tools"])
        helper = load_original_helper(helper_path, ap_count=ap_count)
        recorder_equivalence = None
        if ap_count == 200:
            recorder_equivalence = validate_linear_current_recorder_equivalence(helper, h, trace)
            recorder_optimization = recorder_equivalence["recorder_optimization"]
        else:
            recorder_optimization = {
                "enabled": False,
                "reason": "The 5-AP baseline retains the original helper current recorders unchanged.",
            }
        h.celsius = 34.0
        h.dt = 1000.0 / SAMPLE_RATE_HZ

        models = {}
        for ion, command in (("na", na_trace), ("k", k_trace)):
            for species in ("human", "mouse"):
                models[f"{ion}_{species}"] = execute_model(helper, h, ion, species, command, t, ap_count=ap_count)
                try:
                    import matplotlib.pyplot as plt
                    plt.close("all")
                except Exception:
                    pass

        parameter_sensitivity = None
        if ap_count == 200:
            fit_snapshot_model = execute_model(
                helper, h, "k", "human", k_trace, t, ap_count=ap_count,
                parameter_overrides=K_HUMAN_FINAL_FIT_SNAPSHOT,
            )
            parameter_sensitivity = {
                "name": "k_human_archived_fit_driver_final_best_fit_snapshot",
                "source": K_HUMAN_FINAL_FIT_SNAPSHOT_SOURCE,
                "parameter_overrides": K_HUMAN_FINAL_FIT_SNAPSHOT,
                "model_replay": fit_snapshot_model,
                "comparison_vs_recording_workbook": (
                    compare_k_fit_snapshot_with_workbook(
                        fit_snapshot_model, payloads["k_workbook"], ap_count
                    ) if fit_snapshot_model.get("status") == "completed" else None
                ),
                "canonical_mod_unchanged": True,
                "production_runtime_unchanged": True,
            }

        trace_info = {
            "file_id": FILES["trace"]["id"],
            "bytes": len(payloads["trace"]),
            "sha1": hashlib.sha1(payloads["trace"]).hexdigest(),
            "sha256": hashlib.sha256(payloads["trace"]).hexdigest(),
            "shape": [int(x) for x in np.asarray(np.loadtxt(BytesIO(payloads["trace"]), delimiter=",", skiprows=1)).shape],
            "sample_count": int(trace.size),
            "min_mV": float(np.min(trace)),
            "max_mV": float(np.max(trace)),
            "mean_mV": float(np.mean(trace)),
            "sd_mV": float(np.std(trace)),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "dt_ms": 1000.0 / SAMPLE_RATE_HZ,
            "whole_trace_prominence_50_peak_count": int(len(peak_indices)),
            "first_peaks_time_ms": [float(x / SAMPLE_FREQ_PER_MS) for x in peak_indices[:20]],
        }
        protocol = {
            "source_scripts": {
                "na": "apclamp_na.py",
                "k": "apclamp_k.py",
                "shared_helper": "apclamp_tools.py",
            },
            "source_time_start_ms": TIME_START_MS,
            "source_time_end_ms": time_end_ms,
            "requested_ap_count": ap_count,
            "slice_start_index": start_index,
            "slice_end_index_exclusive": end_index,
            "slice_samples": int(len(source_slice)),
            "ap_train_voltage_peaks_in_slice": [float(x) for x in (command_peaks / SAMPLE_FREQ_PER_MS + TIME_START_MS)],
            "na_voltage_offset_mV": NA_VOLTAGE_OFFSET_MV,
            "k_voltage_offset_mV": 0.0,
            "command_sample_rate_hz": SAMPLE_RATE_HZ,
            "temperature_c": 34.0,
            "model_section": "single 10 um diameter section, Ra=200 ohm cm, Cm=1 uF/cm2",
        }
        report = {
            "schema_version": 3,
            "status": f"raw_human_apclamp_trace_verified_original_{ap_count}_ap_neuron_helpers_replayed_and_compared_with_experimental_means",
            "requested_ap_count": ap_count,
            "runtime_eligible": False,
            "runtime_versions": {
                "python": __import__("platform").python_version(),
                "neuron": __import__("neuron").__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
            },
            "source_integrity": {
                name: {
                    "id": FILES[name]["id"],
                    "path": FILES[name]["path"],
                    "bytes": len(payloads[name]),
                    "sha1": hashlib.sha1(payloads[name]).hexdigest(),
                    "sha256": hashlib.sha256(payloads[name]).hexdigest(),
                    "verification": integrity[name],
                }
                for name in FILES
            },
            "raw_trace": trace_info,
            "protocol": protocol,
            "current_recorder_optimization": recorder_optimization,
            "current_recorder_equivalence": recorder_equivalence,
            "parameter_sensitivity": parameter_sensitivity,
            "experimental_ap_amplitudes": {
                "na": summarize_experimental_csv(payloads["amps_na"], "na", ap_count=ap_count),
                "k": summarize_experimental_csv(payloads["amps_k"], "k", ap_count=ap_count),
            },
            "original_model_replay": models,
            "model_vs_experiment": summarize_model_vs_experiment(
                models, payloads["amps_na"], payloads["amps_k"], ap_count=ap_count
            ),
            "model_vs_original_workbooks": summarize_model_vs_original_workbooks(
                models, payloads["na_workbook"], payloads["k_workbook"], ap_count=ap_count
            ),
            "interpretation_limits": [
                "The original source helper code and unmodified human/mouse MOD files were executed; no mechanism correction was applied.",
                "Na waveform offset is -10 mV per the original apclamp_na.py; K receives no offset per apclamp_k.py.",
                f"This command replay covers the first {ap_count} APs from the H_wide waveform.",
                "The K source trap0 anomalies may produce unstable or non-finite simulation output; do not conceal failed or non-finite results.",
                "No AMSN runtime active-channel mechanism or production defaults are changed.",
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "trace": trace_info,
            "protocol": protocol,
            "models": models,
            "model_vs_experiment": report["model_vs_experiment"],
            "output": str(args.output),
        }, indent=2, allow_nan=False))


if __name__ == "__main__":
    from io import BytesIO
    main()
