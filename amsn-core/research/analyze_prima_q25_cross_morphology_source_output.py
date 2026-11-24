#!/usr/bin/env python3
"""Summarize matched PRIMA transient errors by source and shared output port.

Inputs are the already validated Peng and Tamas four-layout ablation CSVs.
This is a deterministic post-processing step: it does not rerun or alter PRIMA.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1]
RESULTS = ROOT / "results"
RESULT_STEM = "prima_q25_source_output_cross_morphology_2026-11-24"
LAYOUTS = ("eight_basal_q25", "eight_apical_q25", "nine_both_q25")
ORDERS = (112, 168)
SCENARIOS = (
    "nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
    "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20",
)
SOURCES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS = (2.0, 10.0)
EXPECTED_ROWS_PER_MORPHOLOGY = (
    len(LAYOUTS) * len(ORDERS) * len(SCENARIOS)
    * len(SOURCES) * len(PULSE_WIDTHS) * 7
)
MORPHOLOGIES = (
    {
        "name": "NMO_163775_Peng_mouse_Control",
        "path": RESULTS / (
            "NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24_"
            "matched_shared_vs_seven.csv"
        ),
        "neuromorpho_id": "NMO_163775",
        "species_label": "mouse",
        "expected_outputs": {
            1: "soma", 144: "basal_q75", 3926: "apical_q75",
            4180: "basal_q50", 40: "basal_q90", 4104: "apical_q50",
            3948: "apical_q90",
        },
    },
    {
        "name": "NMO_107159_Tamas_human_pyramidal_Control",
        "path": RESULTS / (
            "NMO_107159_TamasHumanPyramidalControl_prima_q25_four_layout_replication_2026-11-24_"
            "matched_shared_vs_seven.csv"
        ),
        "neuromorpho_id": "NMO_107159",
        "species_label": "human pyramidal comparison cell",
        "expected_outputs": {
            1: "soma", 6363: "basal_q75", 4735: "apical_q75",
            5564: "basal_q50", 7023: "basal_q90", 4301: "apical_q50",
            4623: "apical_q90",
        },
    },
)
REQUIRED_COLUMNS = {
    "layout_id", "port_count", "basis_order", "parameter_scenario",
    "source_name", "pulse_width_ms", "port_swc_id", "port_roles",
    "seven_port_nrmse_pct", "candidate_nrmse_pct",
    "candidate_over_seven_error_ratio", "candidate_minus_seven_pct_points",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "matched_rows_per_morphology": EXPECTED_ROWS_PER_MORPHOLOGY,
        "output_groups_per_morphology": len(LAYOUTS) * len(ORDERS) * len(SOURCES) * 7,
        "source_groups_per_morphology": len(LAYOUTS) * len(ORDERS) * len(SOURCES),
        "matched_rows_total": 2 * EXPECTED_ROWS_PER_MORPHOLOGY,
        "output_groups_total": 2 * len(LAYOUTS) * len(ORDERS) * len(SOURCES) * 7,
    }


def load_rows(
    path: Path,
    morphology_name: str,
    expected_outputs: dict[int, str],
) -> list[dict[str, Any]]:
    require(path.is_file(), f"missing matched-pair input: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, f"{path}: missing CSV header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        require(not missing, f"{path}: missing columns {sorted(missing)}")
        for line_number, raw in enumerate(reader, start=2):
            row: dict[str, Any] = dict(raw)
            row["basis_order"] = int(row["basis_order"])
            row["port_swc_id"] = int(row["port_swc_id"])
            row["pulse_width_ms"] = float(row["pulse_width_ms"])
            for name in (
                "seven_port_nrmse_pct", "candidate_nrmse_pct",
                "candidate_over_seven_error_ratio", "candidate_minus_seven_pct_points",
            ):
                row[name] = float(row[name])
                require(math.isfinite(row[name]),
                        f"{path}:{line_number}: non-finite {name}")
            require(row["layout_id"] in LAYOUTS,
                    f"{path}:{line_number}: unexpected layout {row['layout_id']}")
            require(row["basis_order"] in ORDERS,
                    f"{path}:{line_number}: unexpected basis order")
            require(row["parameter_scenario"] in SCENARIOS,
                    f"{path}:{line_number}: unexpected scenario")
            require(row["source_name"] in SOURCES,
                    f"{path}:{line_number}: unexpected input source")
            require(row["pulse_width_ms"] in PULSE_WIDTHS,
                    f"{path}:{line_number}: unexpected pulse width")
            require(row["seven_port_nrmse_pct"] >= 0 and row["candidate_nrmse_pct"] >= 0,
                    f"{path}:{line_number}: negative NRMSE")
            require(row["candidate_over_seven_error_ratio"] > 0,
                    f"{path}:{line_number}: non-positive error ratio")
            row["morphology"] = morphology_name
            rows.append(row)
    require(len(rows) == EXPECTED_ROWS_PER_MORPHOLOGY,
            f"{morphology_name}: {len(rows)} matched rows != {EXPECTED_ROWS_PER_MORPHOLOGY}")
    observed_outputs = {
        (int(row["port_swc_id"]), row["port_roles"]) for row in rows
    }
    expected_output_pairs = set(expected_outputs.items())
    require(observed_outputs == expected_output_pairs,
            f"{morphology_name}: shared output node/role set differs from pinned seven-port map")
    expected_port_counts = {
        "eight_basal_q25": 8,
        "eight_apical_q25": 8,
        "nine_both_q25": 9,
    }
    require(
        all(int(row["port_count"]) == expected_port_counts[row["layout_id"]] for row in rows),
        f"{morphology_name}: candidate port count does not match layout",
    )
    return rows


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize_output_groups(rows: list[dict[str, Any]], *, enforce_complete: bool = True) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["source_name"], row["port_swc_id"], row["port_roles"],
        )
        groups[key].append(row)

    output: list[dict[str, Any]] = []
    for key, subset in sorted(groups.items()):
        ratios = [r["candidate_over_seven_error_ratio"] for r in subset]
        deltas = [r["candidate_minus_seven_pct_points"] for r in subset]
        baseline_errors = [r["seven_port_nrmse_pct"] for r in subset]
        candidate_errors = [r["candidate_nrmse_pct"] for r in subset]
        worse = sum(delta > 0.0 for delta in deltas)
        better = sum(delta < 0.0 for delta in deltas)
        ties = len(deltas) - worse - better
        output.append({
            "morphology": key[0],
            "layout_id": key[1],
            "basis_order": key[2],
            "source_name": key[3],
            "port_swc_id": key[4],
            "port_roles": key[5],
            "matched_pairs": len(subset),
            "median_candidate_over_seven_ratio": statistics.median(ratios),
            "p90_candidate_over_seven_ratio": _percentile(ratios, 0.90),
            "max_candidate_over_seven_ratio": max(ratios),
            "worse_pairs": worse,
            "better_pairs": better,
            "tie_pairs": ties,
            "median_seven_port_nrmse_pct": statistics.median(baseline_errors),
            "median_candidate_nrmse_pct": statistics.median(candidate_errors),
            "max_candidate_nrmse_pct": max(candidate_errors),
            "max_absolute_delta_pct_points": max(abs(x) for x in deltas),
        })
    if enforce_complete:
        expected_groups = 2 * len(LAYOUTS) * len(ORDERS) * len(SOURCES) * 7
        require(len(output) == expected_groups,
                f"output-group coverage {len(output)} != {expected_groups}")
        require(all(row["matched_pairs"] == 18 for row in output),
                "each source/output/layout/order group must contain 9 scenarios × 2 pulses")
    return output


def summarize_source_groups(output_rows: list[dict[str, Any]], *, enforce_complete: bool = True) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in output_rows:
        key = (row["morphology"], row["layout_id"], row["basis_order"], row["source_name"])
        groups[key].append(row)

    summary: list[dict[str, Any]] = []
    for key, subset in sorted(groups.items()):
        ratios = [
            r["median_candidate_over_seven_ratio"]
            for r in subset
        ]
        worse = sum(int(r["worse_pairs"]) for r in subset)
        better = sum(int(r["better_pairs"]) for r in subset)
        ties = sum(int(r["tie_pairs"]) for r in subset)
        summary.append({
            "morphology": key[0],
            "layout_id": key[1],
            "basis_order": key[2],
            "source_name": key[3],
            "output_ports": len(subset),
            "matched_pairs": sum(int(r["matched_pairs"]) for r in subset),
            "median_output_group_ratio": statistics.median(ratios),
            "p90_output_group_ratio": _percentile(ratios, 0.90),
            "max_output_group_ratio": max(ratios),
            "worse_pairs": worse,
            "better_pairs": better,
            "tie_pairs": ties,
        })
    if enforce_complete:
        expected_groups = 2 * len(LAYOUTS) * len(ORDERS) * len(SOURCES)
        require(len(summary) == expected_groups,
                f"source-group coverage mismatch: {len(summary)} != {expected_groups}")
        require(all(row["matched_pairs"] == 126 for row in summary),
                "each source summary must aggregate 7 outputs × 9 scenarios × 2 pulses")
    return summary


def validate_unique_pair_identities(rows: list[dict[str, Any]]) -> None:
    seen: set[tuple] = set()
    for row in rows:
        key = (
            row["layout_id"], row["basis_order"], row["parameter_scenario"],
            row["source_name"], row["pulse_width_ms"], row["port_swc_id"],
        )
        require(key not in seen, f"duplicate source/output pair identity: {key}")
        seen.add(key)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_rows: list[dict[str, Any]] = []
    source_manifest = []
    for spec in MORPHOLOGIES:
        rows = load_rows(spec["path"], spec["name"], spec["expected_outputs"])
        validate_unique_pair_identities(rows)
        all_rows.extend(rows)
        source_manifest.append({
            "morphology": spec["name"],
            "neuromorpho_id": spec["neuromorpho_id"],
            "species_or_class": spec["species_label"],
            "input_path": str(spec["path"]),
            "matched_rows": len(rows),
        })

    output_summary = summarize_output_groups(all_rows)
    source_summary = summarize_source_groups(output_summary)
    worst_pairs = sorted(
        output_summary,
        key=lambda row: (
            -float(row["median_candidate_over_seven_ratio"]),
            row["morphology"], row["layout_id"], row["basis_order"],
        ),
    )[:50]

    write_csv(RESULTS / f"{RESULT_STEM}_by_output.csv", output_summary)
    write_csv(RESULTS / f"{RESULT_STEM}_by_source.csv", source_summary)
    write_csv(RESULTS / f"{RESULT_STEM}_worst_output_groups.csv", worst_pairs)

    dual_order168 = [
        row for row in source_summary
        if row["layout_id"] == "nine_both_q25" and row["basis_order"] == 168
    ]
    report = {
        "schema_version": 1,
        "status": "prima_q25_cross_morphology_source_output_map_passed",
        "sources": source_manifest,
        "exact_coverage": {
            "matched_rows_per_morphology": EXPECTED_ROWS_PER_MORPHOLOGY,
            "matched_rows_total": len(all_rows),
            "output_groups": len(output_summary),
            "source_groups": len(source_summary),
            "worst_output_groups": len(worst_pairs),
        },
        "dual_q25_order168_by_source": dual_order168,
        "scientific_limits": [
            "This is a post-processing summary of validated matched passive transient NRMSE pairs; it does not rerun the solver.",
            "Error ratios use the seven-port NRMSE as denominator; when that baseline is extremely small, ratios may look large while absolute NRMSE remains tiny.",
            "Only two individual morphology reconstructions are compared; they are not species or cell-class populations.",
            "The summaries localize input-source/output-port patterns but do not establish a causal biological or numerical mechanism.",
            "Full Hines remains the reference and no production defaults are changed.",
        ],
    }
    (RESULTS / f"{RESULT_STEM}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
