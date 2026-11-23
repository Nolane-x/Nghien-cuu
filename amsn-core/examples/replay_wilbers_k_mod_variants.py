#!/usr/bin/env python3
"""Replay all released Wilbers potassium mechanisms on the original 200-AP command.

The original Dataverse bytes are checksum-verified before compilation. All
mechanisms receive the same H_wide command, temperature, timestep and
single-compartment setup. The only runtime optimization is the already-tested
list-backed current recorder; a separate source 5-AP run is compared with the
first five amplitudes of each 200-AP replay. This is a research reproduction,
not an AMSN runtime promotion.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

EXAMPLES_DIR = Path(__file__).resolve().parent
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

import audit_wilbers_k_mod_variants as audit
import replay_wilbers_apclamp as replay


K_VARIANT_NAMES = (
    "k_human",
    "k_mouse",
    "k_human_h1",
    "k_human_hm12inf",
    "k_hybrid1",
    "k_hybrid2",
    "k_hybrid3",
    "k_hybrid4",
    "k_hybrid5",
)
K_VARIANTS = {name: audit.SOURCES[name] for name in K_VARIANT_NAMES}
# Immutable pins copied from the completed Dataverse provenance audit artifact.
# The runtime fetch also checks live official Dataverse metadata before bytes
# are accepted; both the published pins and live metadata must agree.
K_VARIANT_PINS = {
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
SOURCE_ROLES = {
    "k_human": "canonical human potassium reference",
    "k_mouse": "canonical mouse potassium comparator",
    "k_human_h1": "released reduced-state human variant with m,h gates",
    "k_human_hm12inf": "released human variant with m,m1,m2,h1,h2 gates",
    **audit.HYBRID_ROLES,
}
EXPECTED_WORKBOOK_COLUMNS = 200
DATASET_DOI = "10.34894/L5J0SD"


def validate_variant_catalog() -> None:
    """Fail fast if the released-source catalog is incomplete or ambiguous."""
    if set(K_VARIANTS) != set(K_VARIANT_NAMES):
        raise ValueError("The K MOD catalog does not contain the exact nine released mechanisms")
    ids = [int(spec["id"]) for spec in K_VARIANTS.values()]
    if len(ids) != len(set(ids)):
        raise ValueError("K MOD catalog contains duplicate Dataverse file IDs")
    for name, spec in K_VARIANTS.items():
        pin = K_VARIANT_PINS[name]
        if spec.get("kind") != "mod" or Path(spec["path"]).name != f"{name}.mod":
            raise ValueError(f"Unexpected Dataverse source mapping for {name}: {spec!r}")
        if int(spec["id"]) != pin["id"] or int(spec["id"]) <= 0:
            raise ValueError(f"Dataverse immutable file ID changed for {name}")
        if len(pin["sha1"]) != 40 or pin["bytes"] <= 0:
            raise ValueError(f"Missing immutable provenance pin for {name}")


def parse_mod_identity(payload: bytes, expected_name: str) -> dict[str, Any]:
    """Read source-declared SUFFIX, STATE and RANGE without changing the MOD."""
    source = payload.decode("utf-8-sig")
    parsed = audit.parse_mod_parameters(source)
    suffix = parsed["suffix"]
    if suffix != expected_name:
        raise ValueError(
            f"Dataverse source {expected_name} declares SUFFIX {suffix!r}; refusing to load it under another name"
        )
    state_block = re.search(r"\bSTATE\s*\{(.*?)\}", source, re.S)
    state_names = (
        re.findall(r"\b[A-Za-z_]\w*\b", state_block.group(1))
        if state_block else []
    )
    return {
        "suffix": suffix,
        "state_names": state_names,
        "range": parsed["range"],
        "parameter_names": sorted(parsed["parameters"]),
        "parameter_values": parsed["parameters"],
        "source_role": SOURCE_ROLES[expected_name],
    }


def validate_amplitudes(values: Any, expected_count: int, mechanism_name: str) -> list[float]:
    """Require exact AP coverage and finite amplitudes; never silently drop NaNs."""
    import numpy as np

    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size != expected_count:
        raise ValueError(
            f"{mechanism_name}: expected {expected_count} AP amplitudes, observed {array.size}"
        )
    if not np.isfinite(array).all():
        bad = np.flatnonzero(~np.isfinite(array)).tolist()
        raise ValueError(f"{mechanism_name}: non-finite AP amplitudes at indices {bad[:20]}")
    return [float(value) for value in array]


def validate_first_five_consistency(
    short_values: Any,
    long_values: Any,
    mechanism_name: str,
    *,
    rtol: float = 1e-12,
    atol: float = 1e-12,
) -> dict[str, Any]:
    """Cross-check the original 5-AP helper against the prefix of the 200-AP run."""
    import numpy as np

    short = np.asarray(short_values, dtype=float).reshape(-1)
    long = np.asarray(long_values, dtype=float).reshape(-1)
    if short.size != 5 or long.size != 200:
        raise ValueError(
            f"{mechanism_name}: expected 5/200 AP arrays, observed {short.size}/{long.size}"
        )
    if not np.isfinite(short).all() or not np.isfinite(long[:5]).all():
        raise ValueError(f"{mechanism_name}: first-five comparison contains non-finite values")
    difference = np.abs(short - long[:5])
    if not np.allclose(short, long[:5], rtol=rtol, atol=atol):
        raise ValueError(
            f"{mechanism_name}: 5-AP source helper differs from 200-AP prefix; "
            f"max_abs_difference={float(difference.max())}"
        )
    return {
        "status": "identical_within_tolerance",
        "ap_count": 5,
        "rtol": rtol,
        "atol": atol,
        "max_absolute_amplitude_difference": float(difference.max()),
    }


def compare_variant_to_recordings(
    model_amplitudes: Any,
    experimental_per_ap: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare AP1-normalized output with a workbook cohort and report epochs."""
    import numpy as np

    model_curve = replay.normalize_by_first(model_amplitudes)
    if not model_curve or any(value is None or not math.isfinite(float(value)) for value in model_curve):
        raise ValueError("Model AP1 normalization is undefined or non-finite")
    if len(experimental_per_ap) != len(model_curve):
        raise ValueError("Model and workbook AP series have different lengths")
    experiment = [row["mean"] for row in experimental_per_ap]
    if any(value is None or not math.isfinite(float(value)) for value in experiment):
        raise ValueError("Experimental workbook mean series contains a missing or non-finite AP")
    overall = replay.compare_curve(model_curve, experiment)

    def epoch(start: int, end: int) -> dict[str, Any]:
        if end <= start:
            return {"ap_range": [start + 1, end], "n": 0, "mae": None, "rmse": None}
        metrics = replay.compare_curve(model_curve[start:end], experiment[start:end])
        return {"ap_range": [start + 1, end], **metrics}

    in_band = [
        abs(float(model_curve[index]) - float(row["mean"])) <= 1.96 * float(row["sem"])
        for index, row in enumerate(experimental_per_ap)
        if row["sem"] is not None and math.isfinite(float(row["sem"]))
    ]
    last = len(model_curve) - 1
    return {
        "normalization": "model amplitude divided by its own AP1 amplitude",
        "model_curve": [float(value) for value in model_curve],
        "experimental_per_ap": experimental_per_ap,
        "metrics_vs_recording_mean": overall,
        "epoch_metrics": {
            "ap1_5": epoch(0, min(5, len(model_curve))),
            "ap1_100": epoch(0, min(100, len(model_curve))),
            "ap101_200": epoch(100, len(model_curve)),
        },
        "model_points_within_mean_plus_minus_1_96_sem": int(sum(in_band)),
        "pointwise_sem_overlap_is_descriptive_only": True,
        "ap5_model": float(model_curve[4]) if len(model_curve) >= 5 else None,
        "ap5_experiment": float(experiment[4]) if len(experiment) >= 5 else None,
        "ap200_model": float(model_curve[last]),
        "ap200_experiment": float(experiment[last]),
        "ap200_sem": (
            float(experimental_per_ap[last]["sem"])
            if experimental_per_ap[last]["sem"] is not None else None
        ),
        "ap200_delta_model_minus_experiment": float(model_curve[last] - experiment[last]),
    }


def run_k_mechanism(
    helper: Any,
    h: Any,
    mechanism_name: str,
    command: Any,
    time_axis: Any,
    ap_count: int,
) -> list[float]:
    """Execute one original K SUFFIX through the original Wilbers helper."""
    import numpy as np

    section = None
    try:
        section = helper.init_k(mechanism_name)
        # Resolve the exact requested SUFFIX on the newly-created section. This
        # catches a helper silently inserting a different/default mechanism.
        getattr(section(0.5), mechanism_name)
        runner = helper.Ik_AP1_5 if ap_count == 5 else helper.Ik_AP1_5_200
        values = runner(section, time_axis, command)
        return validate_amplitudes(values, ap_count, mechanism_name)
    finally:
        if section is not None:
            h.delete_section(sec=section)
        try:
            import matplotlib.pyplot as plt
            plt.close("all")
        except Exception:
            pass


def build_workbook_targets(payload: bytes) -> tuple[Any, dict[str, list[dict[str, Any]]]]:
    """Read only the AP1-normalized human-input columns from the raw K workbook."""
    from io import BytesIO

    frame = replay.pd.read_excel(BytesIO(payload), sheet_name="data")
    required = {"species", "Filename"}
    if not required.issubset(frame.columns):
        raise ValueError(f"K workbook is missing required columns: {sorted(required - set(frame.columns))}")
    columns: dict[int, str] = {}
    for column in frame.columns:
        parsed = replay.parse_k_workbook_header(column)
        if parsed and parsed[1] <= EXPECTED_WORKBOOK_COLUMNS:
            columns[parsed[1]] = str(column)
    missing = sorted(set(range(1, EXPECTED_WORKBOOK_COLUMNS + 1)) - set(columns))
    if missing:
        raise ValueError(f"K workbook human-input AP columns missing: {missing[:10]}")

    targets: dict[str, list[dict[str, Any]]] = {}
    for code, label in (("H", "Human"), ("M", "Mouse")):
        selected = frame.loc[frame["species"].astype(str).str.strip() == code]
        recording_count = int(selected["Filename"].astype(str).nunique())
        if recording_count <= 0:
            raise ValueError(f"K workbook contains no {label} recordings for human-input waveform")
        rows = replay.workbook_group_curve(frame, columns, selected, EXPECTED_WORKBOOK_COLUMNS)
        if any(row["n_recordings"] != recording_count for row in rows):
            raise ValueError(f"K workbook {label} cohort has inconsistent per-AP recording coverage")
        targets[label] = rows
    return frame, targets


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve an explicit empty-result artifact when every variant fails.
    fieldnames = list(rows[0]) if rows else ["status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/wilbers_k_mod_variant_apclamp_200_2026-11-23.json"),
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("results/wilbers_k_mod_variant_apclamp_summary_2026-11-23.csv"),
    )
    parser.add_argument(
        "--per-ap-csv",
        type=Path,
        default=Path("results/wilbers_k_mod_variant_apclamp_per_ap_2026-11-23.csv"),
    )
    args = parser.parse_args()
    validate_variant_catalog()

    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-k-variants-") as tmp:
        root = Path(tmp)
        cache = root / "downloads"
        cache.mkdir()
        payloads: dict[str, bytes] = {}
        integrity: dict[str, Any] = {}

        # Reuse the same exact, hash-pinned experimental command and workbook
        # from the already validated original 200-AP replay.
        for name in ("trace", "k_workbook", "apclamp_tools"):
            payloads[name], integrity[name] = replay.fetch_verified(
                name, replay.FILES[name], cache
            )

        variant_payloads: dict[str, bytes] = {}
        source_audit: dict[str, Any] = {}
        for name, spec in K_VARIANTS.items():
            payload, verified = audit.fetch_verified(name, spec, cache)
            pin = K_VARIANT_PINS[name]
            if (
                int(verified["id"]) != pin["id"]
                or int(verified["bytes"]) != pin["bytes"]
                or str(verified["official_sha1"]).lower() != pin["sha1"]
                or str(verified["observed_sha1"]).lower() != pin["sha1"]
            ):
                raise RuntimeError(
                    f"{name}: live Dataverse metadata/download does not match "
                    f"the previously published immutable ID/size/SHA-1 pin"
                )
            verified["previous_audit_pin"] = pin
            verified["pin_match"] = True
            variant_payloads[name] = payload
            integrity[name] = verified
            source_audit[name] = parse_mod_identity(payload, name)

        trace = replay.np.loadtxt(
            __import__("io").BytesIO(payloads["trace"]),
            delimiter=",",
            skiprows=1,
        )
        trace = replay.np.asarray(trace)
        if trace.ndim == 2 and trace.shape[1] == 1:
            trace = trace[:, 0]
        if trace.ndim != 1:
            raise RuntimeError(f"Expected a 1-D H_wide trace, observed shape {trace.shape}")

        start_index = round(replay.TIME_START_MS * replay.SAMPLE_FREQ_PER_MS)
        end5_ms = replay.protocol_end_ms(5)
        end200_ms = replay.protocol_end_ms(200)
        end5_index = round(end5_ms * replay.SAMPLE_FREQ_PER_MS) + 1
        end200_index = round(end200_ms * replay.SAMPLE_FREQ_PER_MS) + 1
        command5 = replay.np.asarray(trace[start_index:end5_index], dtype=float)
        command200 = replay.np.asarray(trace[start_index:end200_index], dtype=float)
        if command5.size != replay.expected_protocol_samples(5):
            raise RuntimeError(f"Five-AP trace window has {command5.size} samples, expected 13501")
        if command200.size != replay.expected_protocol_samples(200):
            raise RuntimeError(f"200-AP trace window has {command200.size} samples, expected 622876")
        peaks5 = replay.find_peaks(command5, prominence=50)[0]
        peaks200 = replay.find_peaks(command200, prominence=50)[0]
        if len(peaks5) != 5 or len(peaks200) != 200:
            raise RuntimeError(
                f"Wrong command peak coverage: five-AP={len(peaks5)}, 200-AP={len(peaks200)}"
            )

        time5 = replay.np.linspace(replay.TIME_START_MS, end5_ms, len(command5))
        time200 = replay.np.linspace(replay.TIME_START_MS, end200_ms, len(command200))
        _, workbook_targets = build_workbook_targets(payloads["k_workbook"])

        # Compile all nine independently hash-verified source files together.
        # Their source-declared SUFFIX values were checked above and must be
        # unique; no source mechanism text is patched or rewritten.
        suffixes = [source_audit[name]["suffix"] for name in K_VARIANT_NAMES]
        if len(suffixes) != len(set(suffixes)):
            raise RuntimeError(f"Duplicate source-declared NMODL SUFFIX values: {suffixes}")
        mod_dir = root / "Mod"
        mod_dir.mkdir()
        for name, payload in variant_payloads.items():
            (mod_dir / f"{name}.mod").write_bytes(payload)
        compiler = shutil.which("nrnivmodl")
        if compiler is None:
            raise RuntimeError("nrnivmodl is unavailable; pinned NEURON installation is required")
        build = subprocess.run(
            [compiler],
            cwd=mod_dir,
            text=True,
            capture_output=True,
            timeout=300,
        )
        if build.returncode:
            raise RuntimeError(
                "Joint compilation of the nine source K mechanisms failed.\n"
                f"STDOUT:\n{build.stdout[-10000:]}\nSTDERR:\n{build.stderr[-10000:]}"
            )
        libraries = list(mod_dir.rglob("libnrnmech.so")) + list(mod_dir.rglob("libnrnmech.dylib"))
        if len(libraries) != 1:
            raise RuntimeError(f"Expected one compiled mechanism library, observed {libraries}")

        from neuron import h

        if h.nrn_load_dll(str(libraries[0])) == 0:
            raise RuntimeError("NEURON failed to load the jointly compiled K mechanism library")

        helper_path = cache / "apclamp_tools.py"
        helper_path.write_bytes(payloads["apclamp_tools"])
        helper = replay.load_original_helper(helper_path, ap_count=200)
        if not hasattr(helper, "Ik_AP1_5"):
            raise RuntimeError("The original AP-clamp helper does not expose its five-AP K routine")

        # Run the original five-AP routine before replacing its original
        # np.append recorder. It provides an independent prefix check for each
        # mechanism, not just the canonical K source.
        short_results: dict[str, list[float]] = {}
        for name in K_VARIANT_NAMES:
            short_results[name] = run_k_mechanism(
                helper, h, name, command5, time5, ap_count=5
            )

        recorder_info = replay.install_linear_current_recorders(helper, h)
        h.celsius = 34.0
        h.dt = 1000.0 / replay.SAMPLE_RATE_HZ

        models: dict[str, Any] = {}
        comparisons: dict[str, Any] = {}
        summary_rows: list[dict[str, Any]] = []
        per_ap_rows: list[dict[str, Any]] = []
        model_failures: dict[str, str] = {}

        for name in K_VARIANT_NAMES:
            try:
                long_values = run_k_mechanism(
                    helper, h, name, command200, time200, ap_count=200
                )
                consistency = validate_first_five_consistency(
                    short_results[name], long_values, name
                )
                normalized = replay.normalize_by_first(long_values)
                if any(value is None or not math.isfinite(float(value)) for value in normalized):
                    raise ValueError(f"{name}: AP1-normalized 200-AP curve is invalid")
                models[name] = {
                    "status": "completed",
                    "mechanism": name,
                    "source_role": SOURCE_ROLES[name],
                    "amplitude": replay.finite_summary(long_values),
                    "normalized_ap1_curve": [float(value) for value in normalized],
                    "original_five_ap_amplitudes": short_results[name],
                    "first_five_prefix_equivalence": consistency,
                    "normalization": "divide model current peak amplitudes by that model's AP1 amplitude",
                    "source_mod_unchanged": True,
                }
            except Exception as exc:
                model_failures[name] = f"{type(exc).__name__}: {exc}"
                models[name] = {
                    "status": "failed",
                    "mechanism": name,
                    "source_role": SOURCE_ROLES[name],
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "source_mod_unchanged": True,
                }

            if models[name]["status"] != "completed":
                continue

            long_values = models[name]["amplitude"]["values"]
            for cohort, experimental_rows in workbook_targets.items():
                comparison = compare_variant_to_recordings(long_values, experimental_rows)
                comparison["cell_species"] = cohort
                comparison["recording_count"] = int(experimental_rows[0]["n_recordings"])
                comparisons[f"{name}:{cohort}"] = comparison

                metrics = comparison["metrics_vs_recording_mean"]
                epochs = comparison["epoch_metrics"]
                canonical_metrics = None
                if name != "k_human":
                    canonical_metrics = comparisons.get(f"k_human:{cohort}", {}).get(
                        "metrics_vs_recording_mean"
                    )
                summary_rows.append({
                    "mechanism": name,
                    "source_role": SOURCE_ROLES[name],
                    "cell_species": cohort,
                    "recording_count": comparison["recording_count"],
                    "mae_ap1_200": metrics["mae"],
                    "rmse_ap1_200": metrics["rmse"],
                    "mae_ap1_5": epochs["ap1_5"]["mae"],
                    "rmse_ap1_5": epochs["ap1_5"]["rmse"],
                    "mae_ap1_100": epochs["ap1_100"]["mae"],
                    "rmse_ap1_100": epochs["ap1_100"]["rmse"],
                    "mae_ap101_200": epochs["ap101_200"]["mae"],
                    "rmse_ap101_200": epochs["ap101_200"]["rmse"],
                    "ap5_model": comparison["ap5_model"],
                    "ap5_experiment": comparison["ap5_experiment"],
                    "ap200_model": comparison["ap200_model"],
                    "ap200_experiment": comparison["ap200_experiment"],
                    "ap200_sem": comparison["ap200_sem"],
                    "ap200_delta": comparison["ap200_delta_model_minus_experiment"],
                    "points_within_pointwise_1_96_sem": comparison[
                        "model_points_within_mean_plus_minus_1_96_sem"
                    ],
                    "mae_delta_vs_canonical_k_human": (
                        metrics["mae"] - canonical_metrics["mae"]
                        if canonical_metrics and canonical_metrics.get("mae") is not None else None
                    ),
                    "rmse_delta_vs_canonical_k_human": (
                        metrics["rmse"] - canonical_metrics["rmse"]
                        if canonical_metrics and canonical_metrics.get("rmse") is not None else None
                    ),
                })

                model_curve = comparison["model_curve"]
                for index, experimental in enumerate(experimental_rows):
                    model_value = float(model_curve[index])
                    mean = float(experimental["mean"])
                    sem = float(experimental["sem"]) if experimental["sem"] is not None else None
                    per_ap_rows.append({
                        "mechanism": name,
                        "source_role": SOURCE_ROLES[name],
                        "cell_species": cohort,
                        "recording_count": comparison["recording_count"],
                        "ap": index + 1,
                        "model_amplitude": float(long_values[index]),
                        "model_normalized_ap1": model_value,
                        "experimental_mean": mean,
                        "experimental_sd": experimental["sd"],
                        "experimental_sem": sem,
                        "model_minus_experimental": model_value - mean,
                        "inside_pointwise_mean_plus_minus_1_96_sem": (
                            abs(model_value - mean) <= 1.96 * sem if sem is not None else None
                        ),
                    })

        # Recalculate all deltas after canonical cohort comparisons are present,
        # independent of the source mechanism iteration order.
        for row in summary_rows:
            canonical = next(
                (
                    item for item in summary_rows
                    if item["mechanism"] == "k_human" and item["cell_species"] == row["cell_species"]
                ),
                None,
            )
            if canonical is None:
                row["mae_delta_vs_canonical_k_human"] = None
                row["rmse_delta_vs_canonical_k_human"] = None
            else:
                row["mae_delta_vs_canonical_k_human"] = (
                    row["mae_ap1_200"] - canonical["mae_ap1_200"]
                )
                row["rmse_delta_vs_canonical_k_human"] = (
                    row["rmse_ap1_200"] - canonical["rmse_ap1_200"]
                )

        successful_count = sum(item.get("status") == "completed" for item in models.values())
        status = (
            "validated_all_nine_k_mod_variants_replayed_on_original_200_ap_h_wide_command"
            if successful_count == len(K_VARIANT_NAMES)
            else "completed_with_k_mod_variant_failures"
        )
        report = {
            "schema_version": 1,
            "status": status,
            "runtime_eligible": False,
            "dataset": {
                "doi": DATASET_DOI,
                "released_version": 3,
                "license": "CC0-1.0",
                "source_variant_audit_workflow": 45144507180,
                "source_variant_audit_artifact_id": 14803831434,
            },
            "runtime": {
                "python": __import__("platform").python_version(),
                "neuron": __import__("neuron").__version__,
                "numpy": replay.np.__version__,
                "pandas": replay.pd.__version__,
            },
            "protocol": {
                "trace_file_id": replay.FILES["trace"]["id"],
                "trace_bytes": len(payloads["trace"]),
                "trace_sha1": integrity["trace"]["observed_sha1"],
                "trace_sha256": integrity["trace"]["observed_sha256"],
                "source_window_ms": [replay.TIME_START_MS, end200_ms],
                "five_ap_window_ms": [replay.TIME_START_MS, end5_ms],
                "five_ap_samples": int(command5.size),
                "five_ap_command_peaks": int(len(peaks5)),
                "two_hundred_ap_samples": int(command200.size),
                "two_hundred_ap_command_peaks": int(len(peaks200)),
                "sample_rate_hz": replay.SAMPLE_RATE_HZ,
                "dt_ms": 1000.0 / replay.SAMPLE_RATE_HZ,
                "temperature_c": 34.0,
                "k_voltage_offset_mV": 0.0,
                "model_section": "single 10 um diameter section, Ra=200 ohm cm, Cm=1 uF/cm2",
                "input_waveform": "original H_wide AP-clamp command",
            },
            "source_integrity": integrity,
            "source_mechanisms": source_audit,
            "joint_compilation": {
                "status": "success",
                "mechanism_count": len(K_VARIANT_NAMES),
                "library": "one NEURON mechanism library compiled from the nine unchanged MOD source files",
                "source_files_modified": False,
            },
            "current_recorder_optimization": recorder_info,
            "models": models,
            "comparisons": comparisons,
            "summary_rows": summary_rows,
            "ranking_by_human_recording_mae": [
                {
                    "mechanism": row["mechanism"],
                    "mae_ap1_200": row["mae_ap1_200"],
                    "rmse_ap1_200": row["rmse_ap1_200"],
                    "ap200_delta": row["ap200_delta"],
                    "points_within_pointwise_1_96_sem": row["points_within_pointwise_1_96_sem"],
                }
                for row in sorted(
                    (item for item in summary_rows if item["cell_species"] == "Human"),
                    key=lambda item: item["mae_ap1_200"],
                )
            ],
            "model_failures": model_failures,
            "scientific_limits": [
                "All nine released K mechanisms are run against the same original H_wide human AP-clamp voltage command.",
                "The original mechanism files are compiled unchanged; no model equation, parameter default or production runtime is modified.",
                "The workbook comparison uses amp_h_n_ columns (human input waveform) and keeps Human and Mouse recording cohorts separate.",
                "The model is a deterministic single-compartment replay; cohort MAE/RMSE and pointwise mean +/- 1.96 SEM overlap are descriptive, not inferential statistics.",
                "The five-AP/full-train prefix comparison checks execution consistency; it does not establish biological validity.",
                "The released hybrid mechanism roles are sourced from the original channel_kinetics.py comments and not inferred from AP-clamp fit.",
                "A better match to this one AP-clamp protocol does not establish parameter identifiability or agreement with independent voltage-clamp protocols.",
                "No variant is promoted to AMSN runtime or recommended as a default by this experiment alone.",
            ],
        }

        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        write_csv(args.summary_csv, summary_rows)
        write_csv(args.per_ap_csv, per_ap_rows)
        print(json.dumps({
            "status": report["status"],
            "protocol": report["protocol"],
            "compiled_mechanisms": len(K_VARIANT_NAMES),
            "successful_mechanisms": successful_count,
            "failed_mechanisms": model_failures,
            "human_recording_rank": report["ranking_by_human_recording_mae"],
            "summary_csv": str(args.summary_csv),
            "per_ap_csv": str(args.per_ap_csv),
            "output_json": str(args.output_json),
        }, indent=2, allow_nan=False))

        if successful_count != len(K_VARIANT_NAMES):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
