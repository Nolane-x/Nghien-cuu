#!/usr/bin/env python3
"""Validate and summarize the 2026-11-22 PRIMA shift/order Pareto artifacts."""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

DATE = "2026-11-22"
ORDERS = (56, 84, 112)
STRATEGIES = ("narrow_3khz", "extended_10khz", "balanced_10khz")
MODELS = {f"order{order}_{strategy}" for order in ORDERS for strategy in STRATEGIES}
SCENARIOS = {
    "nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
    "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20",
}
FREQUENCIES = {0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0}
SOURCES = {"soma", "basal_q75", "apical_q75"}
PULSES = {2.0, 10.0}
MORPHOLOGIES = {
    "NMO_68174_cell1125",
    "NMO_68175_cell1204",
    "NMO_290988_Mohan2015",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_number(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {field}: {value}")
    return value


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def discover_inputs(root: Path):
    suffixes = {
        "models": "_human_prima_shift_order_pareto_2026-11-22_models.csv",
        "frequency": "_human_prima_shift_order_pareto_2026-11-22_frequency.csv",
        "transient": "_human_prima_shift_order_pareto_2026-11-22_transient.csv",
    }
    grouped = defaultdict(dict)
    for path in root.rglob("*.csv"):
        for kind, suffix in suffixes.items():
            if path.name.endswith(suffix):
                morphology = path.name[:-len(suffix)]
                if kind in grouped[morphology]:
                    raise ValueError(f"duplicate {kind} CSV for {morphology}")
                grouped[morphology][kind] = path
                break
    if set(grouped) != MORPHOLOGIES:
        raise ValueError(f"morphology set mismatch: {sorted(grouped)}")
    for morphology, paths in grouped.items():
        if set(paths) != set(suffixes):
            raise ValueError(f"missing CSV type for {morphology}: {sorted(paths)}")
    return grouped


def validate_morphology(label: str, paths: dict[str, Path]):
    models = read_csv(paths["models"])
    frequency = read_csv(paths["frequency"])
    transient = read_csv(paths["transient"])
    if (len(models), len(frequency), len(transient)) != (81, 729, 3402):
        raise ValueError(
            f"{label} row coverage mismatch: models={len(models)}, "
            f"frequency={len(frequency)}, transient={len(transient)}"
        )
    if {row["model_id"] for row in models} != MODELS:
        raise ValueError(f"{label} model summary ID mismatch")
    if {row["parameter_scenario"] for row in models} != SCENARIOS:
        raise ValueError(f"{label} model summary scenario mismatch")
    for row in models:
        model_id = row["model_id"]
        expected_order = int(model_id.split("_", 1)[0].removeprefix("order"))
        if int(row["basis_order_requested"]) != expected_order:
            raise ValueError(f"{label} requested order mismatch for {model_id}")
        if int(row["basis_order_actual"]) != expected_order:
            raise ValueError(f"{label} achieved order mismatch for {model_id}")
        if row["shift_strategy"] not in STRATEGIES:
            raise ValueError(f"{label} unexpected strategy: {row['shift_strategy']}")
        if row["passivity_check"] != "cholesky_passed":
            raise ValueError(f"{label} Cholesky check failed for {model_id}")
        if finite_number(row, "basis_build_wall_seconds") < 0:
            raise ValueError(f"{label} negative basis build time")
        if int(row["numeric_storage_bytes"]) <= 0:
            raise ValueError(f"{label} invalid numeric storage")

    if {row["model_id"] for row in frequency} != MODELS:
        raise ValueError(f"{label} frequency model ID mismatch")
    if {row["parameter_scenario"] for row in frequency} != SCENARIOS:
        raise ValueError(f"{label} frequency scenario mismatch")
    if {float(row["frequency_hz"]) for row in frequency} != FREQUENCIES:
        raise ValueError(f"{label} frequency point mismatch")
    frequency_keys = set()
    for row in frequency:
        key = (row["model_id"], row["parameter_scenario"], float(row["frequency_hz"]))
        if key in frequency_keys:
            raise ValueError(f"{label} duplicate frequency key: {key}")
        frequency_keys.add(key)
        finite_number(row, "z_error_vs_hines_pct")
        finite_number(row, "y_error_vs_hines_pct")
    if len(frequency_keys) != 9 * 9 * 9:
        raise ValueError(f"{label} incomplete model/scenario/frequency matrix")

    if {row["model_id"] for row in transient} != MODELS:
        raise ValueError(f"{label} transient model ID mismatch")
    if {row["parameter_scenario"] for row in transient} != SCENARIOS:
        raise ValueError(f"{label} transient scenario mismatch")
    if {row["source_name"] for row in transient} != SOURCES:
        raise ValueError(f"{label} transient source mismatch")
    if {float(row["pulse_width_ms"]) for row in transient} != PULSES:
        raise ValueError(f"{label} transient pulse mismatch")

    groups = defaultdict(list)
    source_map = {}
    for row in transient:
        key = (
            row["model_id"], row["parameter_scenario"], row["source_name"],
            float(row["pulse_width_ms"])
        )
        groups[key].append(row)
        for field in (
            "port_nrmse_pct", "overall_nrmse_pct", "max_port_nrmse_pct",
            "full_hines_seconds", "reduced_transient_seconds",
        ):
            value = finite_number(row, field)
            if field.endswith("_nrmse_pct") and value < 0:
                raise ValueError(f"{label} negative error value: {field}")
        output_key = (
            row["parameter_scenario"], row["source_name"],
            float(row["pulse_width_ms"]), row["port_swc_id"]
        )
        previous = source_map.setdefault(output_key, row["source_swc_id"])
        if previous != row["source_swc_id"]:
            raise ValueError(f"{label} source SWC mapping drift for {output_key}")

    if len(groups) != 9 * 9 * 3 * 2 or any(len(rows) != 7 for rows in groups.values()):
        raise ValueError(f"{label} transient seven-port coverage mismatch")
    if len(source_map) != 9 * 3 * 2 * 7:
        raise ValueError(f"{label} transient output-key coverage mismatch")

    return models, frequency, transient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    inputs = discover_inputs(args.artifact_root)
    all_models, all_frequency, all_transient = [], [], []
    for label, paths in sorted(inputs.items()):
        models, frequency, transient = validate_morphology(label, paths)
        all_models.extend(models)
        all_frequency.extend(frequency)
        all_transient.extend(transient)

    if (len(all_models), len(all_frequency), len(all_transient)) != (243, 2187, 10206):
        raise ValueError("combined 3-morphology coverage mismatch")

    frequency_summary = []
    for model_id in sorted(MODELS):
        for frequency_hz in sorted(FREQUENCIES):
            rows = [
                row for row in all_frequency
                if row["model_id"] == model_id and float(row["frequency_hz"]) == frequency_hz
            ]
            z = [finite_number(row, "z_error_vs_hines_pct") for row in rows]
            y = [finite_number(row, "y_error_vs_hines_pct") for row in rows]
            frequency_summary.append({
                "model_id": model_id,
                "basis_order": int(model_id.split("_", 1)[0].removeprefix("order")),
                "shift_strategy": model_id.split("_", 1)[1],
                "frequency_hz": frequency_hz,
                "matched_morphology_scenario_rows": len(rows),
                "median_Z_pct": statistics.median(z),
                "max_Z_pct": max(z),
                "median_Y_pct": statistics.median(y),
                "max_Y_pct": max(y),
            })

    transient_summary = []
    transient_runtime_summary = []
    for model_id in sorted(MODELS):
        rows = [row for row in all_transient if row["model_id"] == model_id]
        errors = [finite_number(row, "port_nrmse_pct") for row in rows]
        transient_summary.append({
            "model_id": model_id,
            "rows": len(rows),
            "median_port_nrmse_pct": statistics.median(errors),
            "p90_port_nrmse_pct": percentile(errors, 0.90),
            "max_port_nrmse_pct": max(errors),
            "median_overall_nrmse_pct": statistics.median(
                finite_number(row, "overall_nrmse_pct") for row in rows
            ),
            "max_overall_nrmse_pct": max(
                finite_number(row, "overall_nrmse_pct") for row in rows
            ),
        })
        unique = {}
        for row in rows:
            key = (
                row["morphology_label"], row["parameter_scenario"],
                row["source_name"], float(row["pulse_width_ms"])
            )
            value = finite_number(row, "reduced_transient_seconds")
            old = unique.setdefault(key, value)
            if not math.isclose(old, value, rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError(f"runtime differs across ports for {model_id}/{key}")
        runtime_values = list(unique.values())
        transient_runtime_summary.append({
            "model_id": model_id,
            "protocol_runs": len(runtime_values),
            "median_reduced_transient_seconds": statistics.median(runtime_values),
            "max_reduced_transient_seconds": max(runtime_values),
        })

    candidate_summary = []
    objective_fields = (
        "median_Z_3000_pct", "median_Y_3000_pct",
        "median_Z_6000_pct", "median_Y_6000_pct",
        "median_Z_10000_pct", "median_Y_10000_pct",
        "median_port_nrmse_pct", "p90_port_nrmse_pct", "max_port_nrmse_pct",
        "median_basis_build_seconds", "median_numeric_storage_mb",
    )
    for model_id in sorted(MODELS):
        model_rows = [row for row in all_models if row["model_id"] == model_id]
        freq_map = {
            (float(row["frequency_hz"]), row["model_id"]): row
            for row in frequency_summary if row["model_id"] == model_id
        }
        transient = next(row for row in transient_summary if row["model_id"] == model_id)
        build = [finite_number(row, "basis_build_wall_seconds") for row in model_rows]
        storage = [int(row["numeric_storage_bytes"]) / (1024 * 1024) for row in model_rows]
        summary = {
            "model_id": model_id,
            "basis_order": int(model_id.split("_", 1)[0].removeprefix("order")),
            "shift_strategy": model_id.split("_", 1)[1],
            "morphology_parameter_rows": len(model_rows),
            "median_basis_build_seconds": statistics.median(build),
            "max_basis_build_seconds": max(build),
            "median_numeric_storage_mb": statistics.median(storage),
            "max_numeric_storage_mb": max(storage),
            "median_port_nrmse_pct": transient["median_port_nrmse_pct"],
            "p90_port_nrmse_pct": transient["p90_port_nrmse_pct"],
            "max_port_nrmse_pct": transient["max_port_nrmse_pct"],
        }
        for frequency_hz in (3000.0, 6000.0, 10000.0):
            row = freq_map[(frequency_hz, model_id)]
            suffix = int(frequency_hz)
            summary[f"median_Z_{suffix}_pct"] = finite_number(row, "median_Z_pct")
            summary[f"median_Y_{suffix}_pct"] = finite_number(row, "median_Y_pct")
        candidate_summary.append(summary)

    pareto_rows = []
    for candidate in candidate_summary:
        dominated_by = []
        for other in candidate_summary:
            if other["model_id"] == candidate["model_id"]:
                continue
            no_worse = all(other[field] <= candidate[field] for field in objective_fields)
            strictly_better = any(other[field] < candidate[field] for field in objective_fields)
            if no_worse and strictly_better:
                dominated_by.append(other["model_id"])
        pareto_rows.append({
            **candidate,
            "pareto_optimal": not dominated_by,
            "dominated_by": ";".join(dominated_by),
            "objective_count": len(objective_fields),
        })

    resource_rows = []
    for path in args.artifact_root.rglob("*-pareto-resource.time.txt"):
        values = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key] = value
        required = (
            "elapsed_wall_seconds", "user_cpu_seconds", "system_cpu_seconds",
            "max_rss_kb", "exit_status",
        )
        if any(key not in values for key in required):
            raise ValueError(f"incomplete process resource record: {path}")
        if values["exit_status"] != "0":
            raise ValueError(f"non-zero process exit status in {path}")
        resource_rows.append({
            "resource_file": path.name,
            "elapsed_wall_seconds": float(values["elapsed_wall_seconds"]),
            "user_cpu_seconds": float(values["user_cpu_seconds"]),
            "system_cpu_seconds": float(values["system_cpu_seconds"]),
            "max_rss_kb": int(values["max_rss_kb"]),
            "max_rss_mb": int(values["max_rss_kb"]) / 1024.0,
            "exit_status": values["exit_status"],
        })
    if resource_rows and len(resource_rows) != 3:
        raise ValueError(f"expected three process resource files, got {len(resource_rows)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        f"prima_shift_order_pareto_candidate_summary_{DATE}.csv": candidate_summary,
        f"prima_shift_order_pareto_frontier_{DATE}.csv": pareto_rows,
        f"prima_shift_order_pareto_frequency_summary_{DATE}.csv": frequency_summary,
        f"prima_shift_order_pareto_transient_summary_{DATE}.csv": transient_summary,
        f"prima_shift_order_pareto_transient_runtime_{DATE}.csv": transient_runtime_summary,
    }
    if resource_rows:
        tables[f"prima_shift_order_pareto_process_resources_{DATE}.csv"] = resource_rows
    for filename, rows in tables.items():
        write_csv(args.output_dir / filename, rows)

    front = [row["model_id"] for row in pareto_rows if row["pareto_optimal"]]
    print(
        f"PASS: models={len(all_models)}, frequency={len(all_frequency)}, "
        f"transient={len(all_transient)}, candidates={len(candidate_summary)}, "
        f"pareto_front={';'.join(front)}"
    )


if __name__ == "__main__":
    main()
