#!/usr/bin/env python3
"""Compare two complete order-168 q25 four-layout runs by exact paired keys."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

KEY_FIELDS = (
    "morphology", "parameter_scenario", "source_name", "output_swc_id",
    "pulse_width_ms", "window_ms", "layout_id",
)
METRIC_FIELDS = (
    "continuous_ac_zoh_weighted_error_pct",
    "continuous_ac_weighted_error_norm_v_s",
    "discrete_be_periodic_transfer_error_pct",
    "discrete_be_error_norm_v",
    "finite_transient_nrmse_pct",
    "perturbation_coordinate_transient_nrmse_pct",
    "finite_error_dft_norm_v_samples",
    "periodic_transfer_component_norm_v_samples",
    "terminal_boundary_component_norm_v_samples",
    "transfer_boundary_cross_term_pct",
)
LAYOUTS = ("seven", "eight_basal_q25", "eight_apical_q25", "nine_both_q25")
MORPHOLOGY_NAMES = {
    "NMO_03524_JacobsControl": "Jacobs",
    "NMO_107159_Tamas_human_pyramidal_Control": "Tamas",
    "NMO_162186_AllenL23": "Allen",
    "NMO_163775_Peng_mouse_Control": "Peng",
}
EXPECTED_CASE_ROWS = 12096


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in KEY_FIELDS)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot take median of empty values")
    return float(statistics.median(values))


def percentile(values: list[float], fraction: float) -> float:
    data = sorted(values)
    if not data:
        raise ValueError("cannot compute percentile of empty values")
    position = (len(data) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[lower]
    weight = position - lower
    return data[lower] * (1.0 - weight) + data[upper] * weight


def index_rows(rows: list[dict[str, str]], label: str) -> dict[tuple[str, ...], dict[str, str]]:
    if len(rows) != EXPECTED_CASE_ROWS:
        raise ValueError(f"{label}: row count {len(rows)} != {EXPECTED_CASE_ROWS}")
    indexed: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        k = key(row)
        if k in indexed:
            raise ValueError(f"{label}: duplicate paired key {k}")
        if row.get("layout_id") not in LAYOUTS:
            raise ValueError(f"{label}: unexpected layout {row.get('layout_id')}")
        indexed[k] = row
    groups: dict[tuple[str, ...], set[str]] = {}
    for k in indexed:
        base = k[:6]
        groups.setdefault(base, set()).add(k[6])
    if len(groups) != 3024 or any(v != set(LAYOUTS) for v in groups.values()):
        raise ValueError(f"{label}: incomplete four-layout paired case matrix")
    return indexed


def compare_basis_hashes(reference_report: dict[str, Any], rerun_report: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "basis_sha256", "conductance_sha256",
        "capacitance_sha256", "input_sha256",
    )
    def index(report: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, str]]:
        rows = report["reproducibility_diagnostics"]["basis_models"]
        return {
            (x["morphology"], x["parameter_scenario"], x["layout_id"]): x
            for x in rows
        }
    a, b = index(reference_report), index(rerun_report)
    if set(a) != set(b) or len(a) != 144:
        raise ValueError("basis-diagnostic key sets differ or coverage is not 144")
    summary = {}
    for field in fields:
        equal = sum(a[k][field] == b[k][field] for k in a)
        summary[field] = {"equal": equal, "different": len(a) - equal, "total": len(a)}
    return summary


def compare_trace_hashes(reference_report: dict[str, Any], rerun_report: dict[str, Any]) -> dict[str, Any]:
    def index(report: dict[str, Any]) -> dict[tuple[str, str, str], str]:
        rows = report["reproducibility_diagnostics"]["trace_outputs"]
        return {
            (x["morphology"], x["parameter_scenario"], x["trace_kind"]): x["trace_sha256"]
            for x in rows
        }
    a, b = index(reference_report), index(rerun_report)
    if set(a) != set(b) or len(a) != 216:
        raise ValueError("trace-diagnostic key sets differ or coverage is not 216")
    equal = sum(a[k] == b[k] for k in a)
    return {"equal": equal, "different": len(a) - equal, "total": len(a)}


def run(reference_dir: Path, rerun_dir: Path, output_dir: Path) -> dict[str, Any]:
    stem = "prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25"
    ref_case = reference_dir / f"{stem}_case_metrics.csv"
    rerun_case = rerun_dir / f"{stem}_case_metrics.csv"
    ref_report_path = reference_dir / f"{stem}_report.json"
    rerun_report_path = rerun_dir / f"{stem}_report.json"
    reference_report = json.loads(ref_report_path.read_text(encoding="utf-8"))
    rerun_report = json.loads(rerun_report_path.read_text(encoding="utf-8"))
    for label, report in (("reference", reference_report), ("rerun", rerun_report)):
        if report.get("status") != "prima_q25_four_morphology_four_layout_boundary_ablation_passed":
            raise ValueError(f"{label} report did not pass")
        if report.get("scope", {}).get("basis_order") != 168:
            raise ValueError(f"{label} report is not basis order 168")

    ref_index = index_rows(read_csv(ref_case), "reference")
    rerun_index = index_rows(read_csv(rerun_case), "rerun")
    if set(ref_index) != set(rerun_index):
        raise ValueError("reference and rerun paired case keys differ")

    metric_rows = []
    for field in METRIC_FIELDS:
        diffs, scaled = [], []
        for k in ref_index:
            a = float(ref_index[k][field])
            b = float(rerun_index[k][field])
            if not (math.isfinite(a) and math.isfinite(b)):
                raise ValueError(f"non-finite value in {field}/{k}")
            delta = abs(a - b)
            diffs.append(delta)
            scaled.append(delta / max(abs(a), abs(b), 1e-300))
        metric_rows.append({
            "metric": field,
            "changed_rows": sum(x != 0.0 for x in diffs),
            "total_rows": len(diffs),
            "median_absolute_difference": median(diffs),
            "p90_absolute_difference": percentile(diffs, 0.90),
            "p99_absolute_difference": percentile(diffs, 0.99),
            "maximum_absolute_difference": max(diffs),
            "median_scaled_relative_difference": median(scaled),
            "p99_scaled_relative_difference": percentile(scaled, 0.99),
        })

    morphology_rows = []
    base_keys = {
        k[:6] for k in ref_index
        if k[6] == "seven"
    }
    for morphology in sorted(MORPHOLOGY_NAMES):
        for window in ("20.0", "40.0"):
            selected = [
                k for k in base_keys
                if k[0] == morphology and k[5] == window
            ]
            if len(selected) != 378:
                raise ValueError(f"{morphology}/{window}: expected 378 matched baseline keys")
            for metric in (
                "discrete_be_periodic_transfer_error_pct",
                "perturbation_coordinate_transient_nrmse_pct",
                "finite_transient_nrmse_pct",
            ):
                for layout in LAYOUTS[1:]:
                    ratios, deltas = [], []
                    worse = 0
                    for base in selected:
                        base_key = base + ("seven",)
                        candidate_key = base + (layout,)
                        a = float(ref_index[base_key][metric])
                        b = float(rerun_index[base_key][metric])
                        c = float(ref_index[candidate_key][metric])
                        d = float(rerun_index[candidate_key][metric])
                        if a <= 0.0 or b <= 0.0:
                            raise ValueError("non-positive baseline error in ratio comparison")
                        ratios.append(c / a)
                        deltas.append(c - a)
                        worse += c > a
                    rerun_ratios, rerun_deltas, rerun_worse = [], [], 0
                    for base in selected:
                        base_key = base + ("seven",)
                        candidate_key = base + (layout,)
                        a = float(rerun_index[base_key][metric])
                        b = float(rerun_index[candidate_key][metric])
                        rerun_ratios.append(b / a if a > 0 else math.inf)
                        rerun_deltas.append(b - a)
                        rerun_worse += b > a
                    morphology_rows.append({
                        "morphology": morphology,
                        "morphology_label": MORPHOLOGY_NAMES[morphology],
                        "window_ms": float(window),
                        "metric": metric,
                        "candidate_layout": layout,
                        "paired_cases": len(selected),
                        "reference_median_candidate_over_seven_ratio": median(ratios),
                        "rerun_median_candidate_over_seven_ratio": median(rerun_ratios),
                        "reference_candidate_worse_pairs": worse,
                        "rerun_candidate_worse_pairs": rerun_worse,
                        "reference_median_absolute_error_delta": median(deltas),
                        "rerun_median_absolute_error_delta": median(rerun_deltas),
                    })

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / f"{stem}_rerun_455858_case_metrics.csv", read_csv(rerun_case))
    rerun_report_copy = output_dir / f"{stem}_rerun_455858_report.json"
    rerun_report_copy.write_bytes(rerun_report_path.read_bytes())
    for suffix in (
        "layout_vs_seven_comparisons.csv",
        "source_layout_window_summary.csv",
        "morphology_layout_window_summary.csv",
        "finite_dft_identity.csv",
    ):
        source = rerun_dir / f"{stem}_{suffix}"
        if source.exists():
            (output_dir / f"{stem}_rerun_455858_{suffix}").write_bytes(source.read_bytes())

    metric_path = output_dir / f"{stem}_rerun_455858_metric_differences.csv"
    _write_csv(metric_path, metric_rows)
    morphology_path = output_dir / f"{stem}_rerun_455858_morphology_sensitivity.csv"
    _write_csv(morphology_path, morphology_rows)

    dispatch = {}
    for label, report in (("reference", reference_report), ("rerun", rerun_report)):
        runtime = report.get("reproducibility_diagnostics", {}).get("numerical_runtime", {})
        dispatch[label] = {
            "thread_environment": runtime.get("thread_environment"),
            "threadpools": runtime.get("threadpools"),
            "runtime_versions": report.get("runtime"),
            "numpy_build_configuration": runtime.get("numpy_build_configuration"),
        }

    summary = {
        "schema_version": 1,
        "status": "passed",
        "reference_run_id": 45585262246,
        "rerun_run_id": 45585843464,
        "basis_order": 168,
        "case_metric_rows_each": EXPECTED_CASE_ROWS,
        "matched_pair_keys": len(ref_index),
        "case_metrics_sha256": {
            "reference": sha256(ref_case),
            "rerun": sha256(rerun_case),
        },
        "basis_hash_comparison": compare_basis_hashes(reference_report, rerun_report),
        "trace_hash_comparison": compare_trace_hashes(reference_report, rerun_report),
        "metric_differences": metric_rows,
        "morphology_sensitivity_rows": len(morphology_rows),
        "cpu_dispatch": dispatch,
        "outputs": {
            "rerun_case_metrics": f"{stem}_rerun_455858_case_metrics.csv",
            "rerun_comparisons": f"{stem}_rerun_455858_layout_vs_seven_comparisons.csv",
            "rerun_report": rerun_report_copy.name,
            "metric_differences": metric_path.name,
            "morphology_sensitivity": morphology_path.name,
        },
        "interpretation": [
            "The two independently completed runs passed the same coverage and finite-DFT identity checks but did not construct identical bases.",
            "Compare absolute differences together with scaled relative differences; relative differences can be exaggerated by residuals close to zero.",
            "The repeated-run data are a CPU-dispatch sensitivity audit, not a bitwise replication claim.",
            "Do not infer population-level or biological effects from these four individual passive linear-RC morphology cases.",
        ],
    }
    summary_path = output_dir / f"{stem}_rerun_455858_comparison_report.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--rerun-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.reference_dir, args.rerun_dir, args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
