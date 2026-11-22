#!/usr/bin/env python3
"""Validate and summarize the 2026-11-22 human PRIMA basis-transfer artifacts.

The input root contains extracted per-morphology GitHub Actions artifacts.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

DATE = "2026-11-22"
MODELS = (
    "frozen_nominal_3khz_basis",
    "fresh_3khz_basis",
    "fresh_extended_10khz_basis",
)
FREQUENCIES = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
SCENARIOS = {
    "nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
    "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20",
}
SOURCES = {"soma", "basal_q75", "apical_q75"}
PULSE_WIDTHS = {2.0, 10.0}
EXPECTED_MORPHOLOGIES = {
    "NMO_68174_cell1125", "NMO_68175_cell1204", "NMO_290988_Mohan2015"
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_float(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {field}: {value}")
    return value


def median(values: list[float]) -> float:
    return statistics.median(values)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty summary: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def collect_inputs(root: Path):
    files = list(root.rglob("*_human_prima_basis_transfer_protocol_robustness_2026-11-22_*.csv"))
    by_morphology: dict[str, dict[str, Path]] = defaultdict(dict)
    suffixes = {
        "model_summary": "_model_summary.csv",
        "frequency": "_frequency.csv",
        "transient": "_transient.csv",
    }
    for path in files:
        for kind, suffix in suffixes.items():
            if path.name.endswith(suffix):
                label = path.name.split("_human_prima_basis_transfer_protocol_robustness_", 1)[0]
                if kind in by_morphology[label]:
                    raise ValueError(f"duplicate {kind} CSV for {label}")
                by_morphology[label][kind] = path
                break
    if set(by_morphology) != EXPECTED_MORPHOLOGIES:
        raise ValueError(f"morphology coverage mismatch: {sorted(by_morphology)}")
    for label, paths in by_morphology.items():
        if set(paths) != set(suffixes):
            raise ValueError(f"missing result CSV for {label}: {sorted(paths)}")
    return by_morphology


def group_rows(rows: list[dict[str, str]], fields: tuple[str, ...]):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row[field] for field in fields)
        grouped[key].append(row)
    return grouped.items()


def analyze(root: Path, output: Path) -> None:
    inputs = collect_inputs(root)
    all_models, all_frequency, all_transient = [], [], []

    for label, paths in sorted(inputs.items()):
        models = read_csv(paths["model_summary"])
        frequency = read_csv(paths["frequency"])
        transient = read_csv(paths["transient"])
        if len(models) != 27 or len(frequency) != 243 or len(transient) != 1134:
            raise ValueError(
                f"row count mismatch for {label}: model={len(models)}, "
                f"frequency={len(frequency)}, transient={len(transient)}"
            )
        if {row["model_id"] for row in models} != set(MODELS):
            raise ValueError(f"model summary identity mismatch for {label}")
        if {row["parameter_scenario"] for row in models} != SCENARIOS:
            raise ValueError(f"parameter scenario mismatch for {label}")
        if any(int(row["requested_order"]) != 56 or int(row["actual_order"]) != 56 for row in models):
            raise ValueError(f"requested/actual order mismatch for {label}")
        if any(row["passivity_check"] != "cholesky_passed" for row in models):
            raise ValueError(f"Cholesky positive-definiteness check failed for {label}")

        if {row["model_id"] for row in frequency} != set(MODELS):
            raise ValueError(f"frequency model identity mismatch for {label}")
        if {row["parameter_scenario"] for row in frequency} != SCENARIOS:
            raise ValueError(f"frequency scenario mismatch for {label}")
        if {float(row["frequency_hz"]) for row in frequency} != set(FREQUENCIES):
            raise ValueError(f"frequency coverage mismatch for {label}")
        for row in frequency:
            if int(row["requested_order"]) != 56 or int(row["actual_order"]) != 56:
                raise ValueError(f"frequency actual order mismatch for {label}")
            finite_float(row, "z_error_vs_hines_pct")
            finite_float(row, "y_error_vs_hines_pct")

        if {row["model_id"] for row in transient} != set(MODELS):
            raise ValueError(f"transient model identity mismatch for {label}")
        if {row["parameter_scenario"] for row in transient} != SCENARIOS:
            raise ValueError(f"transient parameter scenario mismatch for {label}")
        if {row["source_name"] for row in transient} != SOURCES:
            raise ValueError(f"transient source mismatch for {label}")
        if {float(row["pulse_width_ms"]) for row in transient} != PULSE_WIDTHS:
            raise ValueError(f"pulse-width mismatch for {label}")
        if any(int(row["requested_order"]) != 56 or int(row["actual_order"]) != 56 for row in transient):
            raise ValueError(f"transient actual order mismatch for {label}")

        groups = defaultdict(list)
        for row in transient:
            key = (row["model_id"], row["parameter_scenario"], row["source_name"],
                   float(row["pulse_width_ms"]))
            groups[key].append(row)
            for field in ("port_nrmse_pct", "overall_nrmse_pct", "max_port_nrmse_pct"):
                value = finite_float(row, field)
                if value < 0:
                    raise ValueError(f"negative transient error in {label}: {field}")
        if len(groups) != 3 * 9 * 3 * 2 or any(len(rows) != 7 for rows in groups.values()):
            raise ValueError(f"per-source/pulse output-port coverage mismatch for {label}")
        if len({(r["source_name"], r["pulse_width_ms"], r["port_swc_id"]) for r in transient}) != 3 * 2 * 7:
            raise ValueError(f"source/pulse/SWC-node coverage mismatch for {label}")

        all_models.extend(models)
        all_frequency.extend(frequency)
        all_transient.extend(transient)

    if (len(all_models), len(all_frequency), len(all_transient)) != (81, 729, 3402):
        raise ValueError("combined result coverage mismatch")

    error_by_model = {}
    for row in all_transient:
        key = (row["morphology_label"], row["parameter_scenario"], row["source_name"],
               float(row["pulse_width_ms"]), row["port_swc_id"])
        model_key = (key, row["model_id"])
        if model_key in error_by_model:
            raise ValueError(f"duplicate transient pairing key: {model_key}")
        error_by_model[model_key] = finite_float(row, "port_nrmse_pct")
    pair_keys = {key for key, _ in error_by_model}
    if len(pair_keys) != 1134:
        raise ValueError(f"expected 1,134 unique transient output conditions, got {len(pair_keys)}")
    if any((key, model) not in error_by_model for key in pair_keys for model in MODELS):
        raise ValueError("incomplete paired transient model comparison")

    frequency_summary = []
    for (frequency_hz, model_id), rows in group_rows(all_frequency, ("frequency_hz", "model_id")):
        z = [finite_float(row, "z_error_vs_hines_pct") for row in rows]
        y = [finite_float(row, "y_error_vs_hines_pct") for row in rows]
        frequency_summary.append({
            "frequency_hz": frequency_hz, "model_id": model_id, "rows": len(rows),
            "median_Z_pct": statistics.median(z), "max_Z_pct": max(z),
            "median_Y_pct": statistics.median(y), "max_Y_pct": max(y),
        })

    high_band_summary = []
    for (morphology, frequency_hz, model_id), rows in group_rows(
        [r for r in all_frequency if float(r["frequency_hz"]) in (6000.0, 10000.0)],
        ("morphology_label", "frequency_hz", "model_id")
    ):
        z = [finite_float(row, "z_error_vs_hines_pct") for row in rows]
        y = [finite_float(row, "y_error_vs_hines_pct") for row in rows]
        high_band_summary.append({
            "morphology_label": morphology, "frequency_hz": frequency_hz,
            "model_id": model_id, "rows": len(rows),
            "median_Z_pct": statistics.median(z), "max_Z_pct": max(z),
            "median_Y_pct": statistics.median(y), "max_Y_pct": max(y),
        })

    transient_morphology_summary = []
    for (morphology, model_id), rows in group_rows(all_transient, ("morphology_label", "model_id")):
        errors = [finite_float(row, "port_nrmse_pct") for row in rows]
        overall = [finite_float(row, "overall_nrmse_pct") for row in rows]
        transient_morphology_summary.append({
            "morphology_label": morphology, "model_id": model_id, "rows": len(rows),
            "median_port_nrmse_pct": statistics.median(errors), "max_port_nrmse_pct": max(errors),
            "median_overall_nrmse_pct": statistics.median(overall), "max_overall_nrmse_pct": max(overall),
        })

    transient_source_summary = []
    for (source, pulse, model_id), rows in group_rows(all_transient, ("source_name", "pulse_width_ms", "model_id")):
        errors = [finite_float(row, "port_nrmse_pct") for row in rows]
        transient_source_summary.append({
            "source_name": source, "pulse_width_ms": pulse, "model_id": model_id,
            "rows": len(rows), "median_port_nrmse_pct": statistics.median(errors),
            "max_port_nrmse_pct": max(errors),
        })

    comparisons = (
        ("fresh_extended_10khz_basis", "fresh_3khz_basis", "extended_vs_fresh3k"),
        ("fresh_3khz_basis", "frozen_nominal_3khz_basis", "fresh3k_vs_frozen3k"),
        ("fresh_extended_10khz_basis", "frozen_nominal_3khz_basis", "extended_vs_frozen"),
    )
    pairwise_summary = []
    for numerator, denominator, label in comparisons:
        ratios = [error_by_model[(key, numerator)] / error_by_model[(key, denominator)]
                  for key in pair_keys]
        pairwise_summary.append({
            "comparison": label, "matched_rows": len(ratios),
            "median_ratio": statistics.median(ratios),
            "p90_ratio": percentile(ratios, 0.9),
            "max_ratio": max(ratios), "min_ratio": min(ratios),
            "wins_lower_error": sum(value < 1.0 - 1e-12 for value in ratios),
            "regressions_higher_error": sum(value > 1.0 + 1e-12 for value in ratios),
            "ties": sum(abs(value - 1.0) <= 1e-12 for value in ratios),
        })

    high_band_pairwise = []
    for frequency_hz in (6000.0, 10000.0):
        rows = [r for r in all_frequency if float(r["frequency_hz"]) == frequency_hz]
        for metric in ("z_error_vs_hines_pct", "y_error_vs_hines_pct"):
            values = defaultdict(dict)
            for row in rows:
                key = (row["morphology_label"], row["parameter_scenario"])
                values[key][row["model_id"]] = finite_float(row, metric)
            ratios = [v["fresh_extended_10khz_basis"] / v["fresh_3khz_basis"]
                      for v in values.values()]
            high_band_pairwise.append({
                "frequency_hz": frequency_hz, "metric": metric,
                "matched_morphology_scenario_pairs": len(ratios),
                "median_extended_over_fresh3k": statistics.median(ratios),
                "p90_extended_over_fresh3k": percentile(ratios, 0.9),
                "max_extended_over_fresh3k": max(ratios),
                "extended_lower_error_count": sum(value < 1.0 for value in ratios),
                "fresh3k_lower_error_count": sum(value > 1.0 for value in ratios),
            })

    model_audit = []
    for (morphology,), rows in group_rows(all_models, ("morphology_label",)):
        model_audit.append({
            "morphology_label": morphology, "model_rows": len(rows),
            "parameter_scenarios": len({r["parameter_scenario"] for r in rows}),
            "model_variants": len({r["model_id"] for r in rows}),
            "requested_orders": ";".join(sorted({r["requested_order"] for r in rows})),
            "actual_orders": ";".join(sorted({r["actual_order"] for r in rows})),
            "passivity_all_cholesky_passed": all(r["passivity_check"] == "cholesky_passed" for r in rows),
            "state_reduction_pct": rows[0]["state_reduction_pct"],
            "full_compartment_order": rows[0]["full_compartment_order"],
        })

    output.mkdir(parents=True, exist_ok=True)
    tables = {
        f"human_prima_basis_transfer_model_audit_{DATE}.csv": model_audit,
        f"human_prima_basis_transfer_frequency_by_frequency_{DATE}.csv": frequency_summary,
        f"human_prima_basis_transfer_high_band_by_morphology_{DATE}.csv": high_band_summary,
        f"human_prima_basis_transfer_transient_by_morphology_{DATE}.csv": transient_morphology_summary,
        f"human_prima_basis_transfer_transient_by_source_pulse_{DATE}.csv": transient_source_summary,
        f"human_prima_basis_transfer_transient_pairwise_{DATE}.csv": pairwise_summary,
        f"human_prima_basis_transfer_high_band_pairwise_{DATE}.csv": high_band_pairwise,
    }
    for filename, rows in tables.items():
        write_csv(output / filename, rows)
    print(f"PASS: {len(all_models)} model rows, {len(all_frequency)} frequency rows, "
          f"{len(all_transient)} transient rows; 3 morphologies; all 56-state models; "
          f"all Cholesky checks passed; 1,134 matched transient comparison keys.")
    for row in pairwise_summary:
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True,
                        help="Root directory containing extracted Actions artifacts")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.artifact_root, args.output_dir)


if __name__ == "__main__":
    main()
