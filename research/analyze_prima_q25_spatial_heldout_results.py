#!/usr/bin/env python3
"""Build an auditable Markdown report from the accepted q25 spatial-holdout archive.

This post-hoc analysis uses only the archived case-level CSV, report JSON and
basis metadata. Candidate/D0 ratios are recomputed from exact paired cases.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

RESULT_STEM = (
    "prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout"
    "_order224_2026-11-26"
)
EXPECTED_COUNTS = {
    "case_metrics_read_back": 22464,
    "group_summary_read_back": 3744,
    "morphology_summary_read_back": 416,
    "scenario_summary_read_back": 936,
    "pooled_summary_read_back": 104,
    "finite_dft_identity_read_back": 144,
    "basis_metadata_rows": 144,
    "unique_case_keys": 22464,
}
HELDOUT_LABELS = ("basal_q10", "basal_q95", "apical_q10", "apical_q95")
Q25_LABELS = ("basal_q25", "apical_q25")
OUTPUT_ORDER = (
    "basal_q10", "basal_q95", "apical_q10", "apical_q95",
    "basal_q25", "apical_q25",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), f"CSV is empty: {path}")
    return rows


def percentile(values: list[float], q: float) -> float:
    require(bool(values), "cannot summarize an empty value list")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def summarize(values: list[tuple[float, float, float, float]]) -> dict[str, Any]:
    ratios = [ratio for ratio, _delta, _reference, _candidate in values]
    deltas = [delta for _ratio, delta, _reference, _candidate in values]
    references = [reference for _ratio, _delta, reference, _candidate in values]
    candidates = [candidate for _ratio, _delta, _reference, candidate in values]
    return {
        "matched": len(values),
        "median_ratio": float(statistics.median(ratios)),
        "p90_ratio": percentile(ratios, 0.90),
        "worst_ratio": max(ratios),
        "median_reference_nrmse_pct": float(statistics.median(references)),
        "median_candidate_nrmse_pct": float(statistics.median(candidates)),
        "median_delta_pp": float(statistics.median(deltas)),
        "better": sum(delta < 0.0 for delta in deltas),
        "worse": sum(delta > 0.0 for delta in deltas),
        "unchanged": sum(delta == 0.0 for delta in deltas),
    }


def validate_node_metadata(metadata: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    require(len(metadata) == 144, f"expected 144 metadata rows, got {len(metadata)}")
    mapping_by_morphology: dict[str, dict[str, Any]] = {}
    for row in metadata:
        morph_id = str(row["neuromorpho_id"])
        shared = [int(x) for x in row["shared_swc_node_ids"]]
        q25_map = {str(k): int(v) for k, v in row["q25_swc_node_ids"].items()}
        heldout_rows = row["heldout_spatial_sites"]
        heldout_map = {
            str(site["output_label"]): {
                "swc_node_id": int(site["swc_node_id"]),
                "tree_index": int(site["tree_index"]),
                "branch_class": str(site["branch_class"]),
                "path_distance_quantile": float(site["path_distance_quantile"]),
            }
            for site in heldout_rows
        }
        require(len(shared) == 7 and len(set(shared)) == 7,
                f"{morph_id}: shared input/output selector is not seven unique nodes")
        require(set(q25_map) == set(Q25_LABELS) and len(set(q25_map.values())) == 2,
                f"{morph_id}: q25 node mapping is malformed")
        require(set(heldout_map) == set(HELDOUT_LABELS) and len(heldout_map) == 4,
                f"{morph_id}: held-out spatial mapping is malformed")
        shared_set = set(shared)
        q25_set = set(q25_map.values())
        heldout_set = {item["swc_node_id"] for item in heldout_map.values()}
        require(not shared_set.intersection(q25_set | heldout_set),
                f"{morph_id}: shared SWC nodes collide with q25/held-out nodes")
        require(not q25_set.intersection(heldout_set),
                f"{morph_id}: q25 nodes collide with held-out spatial nodes")
        require(len(shared_set | q25_set | heldout_set) == 13,
                f"{morph_id}: expected 13 distinct observed SWC nodes")
        require(row["actual_order"] == 224 and row["seven_input_ports_unchanged"],
                f"{morph_id}: invalid basis order or input-port metadata")

        current = {
            "shared_swc_node_ids": shared,
            "q25_swc_node_ids": q25_map,
            "heldout_spatial_sites": heldout_map,
            "swc_sha256": row.get("swc_sha256", ""),
        }
        previous = mapping_by_morphology.get(morph_id)
        if previous is not None:
            require(previous == current,
                    f"{morph_id}: node map changed between scenarios or schedules")
        else:
            mapping_by_morphology[morph_id] = current

    require(len(mapping_by_morphology) == 4,
            f"expected four morphology node maps, got {len(mapping_by_morphology)}")
    return mapping_by_morphology


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def fmt_ratio(value: float) -> str:
    return f"{value:.4g}"


def fmt_delta(value: float) -> str:
    return f"{value:+.4e}"


def make_report(results_dir: Path, output_path: Path) -> None:
    json_path = results_dir / f"{RESULT_STEM}_report.json"
    case_path = results_dir / f"{RESULT_STEM}_case_metrics.csv"
    metadata_path = results_dir / f"{RESULT_STEM}_basis_metadata.json"
    manifest_path = results_dir / f"{RESULT_STEM}_manifest.json"

    report = read_json(json_path)
    manifest = read_json(manifest_path)
    cases = read_csv(case_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    require(report.get("status") == "passed", "numerical report status is not passed")
    require(manifest.get("status") == "passed", "archive manifest status is not passed")
    require(report["dft_identity"]["all_rows_passed"],
            "not all finite-record DFT identities passed")
    require(report["dft_identity"]["max_full_hines_relative_error"]
            < report["dft_identity"]["tolerance"],
            "full-Hines finite-record identity exceeded tolerance")
    require(report["dft_identity"]["max_reduced_relative_error"]
            < report["dft_identity"]["tolerance"],
            "reduced finite-record identity exceeded tolerance")
    for gate in (
        "d0_exact_production_parity_all_scenarios",
        "all_reduced_g_c_cholesky_positive",
        "all_models_reached_order_224",
        "seven_input_ports_unchanged_all_models",
    ):
        require(report["numerical_gates"][gate] is True, f"numerical gate failed: {gate}")
    require(len(manifest.get("files", [])) == 9,
            "archive manifest must cover all nine result files")
    for entry in manifest["files"]:
        path = results_dir / entry["path"]
        require(path.is_file(), f"manifest file is missing: {path}")
        require(path.stat().st_size == entry["bytes"],
                f"manifest byte count mismatch: {path.name}")
        require(sha256_file(path) == entry["sha256"],
                f"manifest SHA-256 mismatch: {path.name}")
    for key, expected in EXPECTED_COUNTS.items():
        observed = (
            len(cases) if key in {"case_metrics_read_back", "unique_case_keys"}
            else int(report["coverage"][key])
        )
        require(observed == expected,
                f"{key}: expected {expected}, got {observed}")
    require(len({(
        row["morphology"], row["neuromorpho_id"], row["scenario"],
        row["schedule"], row["window_ms"], row["source"],
        row["pulse_width_ms"], row["output_label"],
    ) for row in cases}) == len(cases), "case-level identities are not unique")

    node_maps = validate_node_metadata(metadata)
    morphology_hashes = {
        item["neuromorpho_id"]: item["expected_swc_sha256"]
        for item in report["fixed_protocol"]["morphologies"]
    }
    require(set(node_maps) == set(morphology_hashes),
            "basis metadata morphologies differ from the pinned source manifest")
    for morph_id, mapping in node_maps.items():
        mapping["swc_sha256"] = morphology_hashes[morph_id]
    baseline: dict[tuple[Any, ...], float] = {}
    for row in cases:
        if row["schedule"] != "D0_none":
            continue
        key = (
            row["morphology"], row["neuromorpho_id"], row["scenario"],
            float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), row["output_label"],
        )
        require(key not in baseline, f"duplicate D0 case key: {key}")
        baseline[key] = float(row["transient_nrmse_pct"])

    grouped_output: dict[tuple[str, float, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_label: dict[tuple[str, float, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_morphology: dict[tuple[str, str, float, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_scenario: dict[tuple[str, str, float, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    for row in cases:
        schedule = row["schedule"]
        if schedule == "D0_none":
            continue
        key = (
            row["morphology"], row["neuromorpho_id"], row["scenario"],
            float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), row["output_label"],
        )
        require(key in baseline, f"missing paired D0 row: {key}")
        candidate = float(row["transient_nrmse_pct"])
        reference = baseline[key]
        ratio = candidate / max(reference, 1e-30)
        delta = candidate - reference
        pair = (ratio, delta, reference, candidate)
        window = float(row["window_ms"])
        grouped_output[(schedule, window, row["output_role"])].append(pair)
        grouped_label[(schedule, window, row["output_label"])].append(pair)
        grouped_morphology[(row["morphology"], schedule, window, row["output_label"])].append(pair)
        grouped_scenario[(row["scenario"], schedule, window, row["output_label"])].append(pair)

    pooled_rows = []
    for label in OUTPUT_ORDER:
        for window in (20.0, 40.0):
            for schedule in ("D0_none", "BASAL_10K", "APICAL_10K", "BOTH_10K"):
                if schedule == "D0_none":
                    baseline_values = [
                        float(row["transient_nrmse_pct"])
                        for row in cases
                        if row["schedule"] == "D0_none"
                        and row["output_label"] == label
                        and float(row["window_ms"]) == window
                    ]
                    require(bool(baseline_values),
                            f"missing D0 baseline values for {label}/{window:g} ms")
                    median_baseline = float(statistics.median(baseline_values))
                    summary = {
                        "matched": len(baseline_values),
                        "median_ratio": 1.0,
                        "p90_ratio": 1.0,
                        "worst_ratio": 1.0,
                        "median_reference_nrmse_pct": median_baseline,
                        "median_candidate_nrmse_pct": median_baseline,
                        "median_delta_pp": 0.0,
                        "better": 0,
                        "worse": 0,
                    }
                else:
                    summary = summarize(grouped_label[(schedule, window, label)])
                pooled_rows.append([
                    label, f"{window:g}", schedule, str(summary["matched"]),
                    fmt_ratio(summary["median_ratio"]),
                    fmt_ratio(summary["p90_ratio"]),
                    fmt_ratio(summary["worst_ratio"]),
                    "-" if summary["median_reference_nrmse_pct"] is None else fmt_ratio(summary["median_reference_nrmse_pct"]),
                    "-" if summary["median_candidate_nrmse_pct"] is None else fmt_ratio(summary["median_candidate_nrmse_pct"]),
                    fmt_delta(summary["median_delta_pp"]),
                    f'{summary["better"]}/{summary["worse"]}',
                ])

    role_rows = []
    for window in (20.0, 40.0):
        for schedule in ("BASAL_10K", "APICAL_10K", "BOTH_10K"):
            for role in ("heldout_spatial_output", "q25_output", "shared_output"):
                summary = summarize(grouped_output[(schedule, window, role)])
                role_rows.append([
                    f"{window:g}", schedule, role, str(summary["matched"]),
                    fmt_ratio(summary["median_ratio"]),
                    fmt_ratio(summary["p90_ratio"]),
                    fmt_ratio(summary["median_reference_nrmse_pct"]),
                    fmt_ratio(summary["median_candidate_nrmse_pct"]),
                    fmt_delta(summary["median_delta_pp"]),
                    f'{summary["better"]}/{summary["worse"]}',
                ])

    morphology_rows = []
    morphology_names = report["fixed_protocol"]["morphologies"]
    morphology_name_by_id = {
        item["neuromorpho_id"]: item["name"] for item in morphology_names
    }
    for morph_id in sorted(node_maps):
        morph_name = morphology_name_by_id[morph_id]
        for label in HELDOUT_LABELS:
            for window in (20.0, 40.0):
                for schedule in ("BASAL_10K", "APICAL_10K", "BOTH_10K"):
                    summary = summarize(
                        grouped_morphology[(morph_name, schedule, window, label)]
                    )
                    morphology_rows.append([
                        morph_id, label, f"{window:g}", schedule,
                        fmt_ratio(summary["median_ratio"]),
                        fmt_ratio(summary["p90_ratio"]),
                        fmt_ratio(summary["median_reference_nrmse_pct"]),
                        fmt_ratio(summary["median_candidate_nrmse_pct"]),
                        fmt_delta(summary["median_delta_pp"]),
                        f'{summary["better"]}/{summary["worse"]}',
                    ])

    scenario_rows = []
    scenario_names = report["fixed_protocol"]["passive_scenarios"]
    for scenario in scenario_names:
        for label in HELDOUT_LABELS:
            for window in (20.0, 40.0):
                for schedule in ("BASAL_10K", "APICAL_10K", "BOTH_10K"):
                    summary = summarize(
                        grouped_scenario[(scenario, schedule, window, label)]
                    )
                    scenario_rows.append([
                        scenario, label, f"{window:g}", schedule,
                        str(summary["matched"]),
                        fmt_ratio(summary["median_ratio"]),
                        fmt_ratio(summary["median_reference_nrmse_pct"]),
                        fmt_ratio(summary["median_candidate_nrmse_pct"]),
                        fmt_delta(summary["median_delta_pp"]),
                        f'{summary["better"]}/{summary["worse"]}',
                    ])

    candidate_schedules = ("BASAL_10K", "APICAL_10K", "BOTH_10K")
    heldout_schedule_rows = []
    q25_schedule_rows = []
    heldout_label_schedule_rows = []
    heldout_morphology_rows = []
    heldout_median_ratio_below_one = 0

    for morph_id in sorted(node_maps):
        morph_name = morphology_name_by_id.get(morph_id)
        require(morph_name is not None, f"missing morphology name for {morph_id}")
        for schedule in candidate_schedules:
            pairs = [
                pair
                for label in HELDOUT_LABELS
                for window in (20.0, 40.0)
                for pair in grouped_morphology[(morph_name, schedule, window, label)]
            ]
            summary = summarize(pairs)
            heldout_morphology_rows.append([
                morph_id,
                schedule,
                f'{summary["matched"]:,}',
                fmt_ratio(summary["median_ratio"]),
                fmt_ratio(summary["median_reference_nrmse_pct"]),
                fmt_ratio(summary["median_candidate_nrmse_pct"]),
                fmt_delta(summary["median_delta_pp"]),
                f'{summary["better"]}/{summary["worse"]}',
            ])

    for schedule in candidate_schedules:
        heldout_pairs = [
            pair
            for label in HELDOUT_LABELS
            for window in (20.0, 40.0)
            for pair in grouped_label[(schedule, window, label)]
        ]
        heldout_summary = summarize(heldout_pairs)
        heldout_schedule_rows.append([
            schedule,
            f'{heldout_summary["matched"]:,}',
            fmt_ratio(heldout_summary["median_ratio"]),
            fmt_ratio(heldout_summary["median_reference_nrmse_pct"]),
            fmt_ratio(heldout_summary["median_candidate_nrmse_pct"]),
            fmt_delta(heldout_summary["median_delta_pp"]),
            f'{heldout_summary["better"]}/{heldout_summary["worse"]}',
        ])

        q25_pairs = [
            pair
            for label in Q25_LABELS
            for window in (20.0, 40.0)
            for pair in grouped_label[(schedule, window, label)]
        ]
        q25_summary = summarize(q25_pairs)
        q25_schedule_rows.append([
            schedule,
            f'{q25_summary["matched"]:,}',
            fmt_ratio(q25_summary["median_ratio"]),
            fmt_ratio(q25_summary["median_reference_nrmse_pct"]),
            fmt_ratio(q25_summary["median_candidate_nrmse_pct"]),
            fmt_delta(q25_summary["median_delta_pp"]),
            f'{q25_summary["better"]}/{q25_summary["worse"]}',
        ])

        for label in HELDOUT_LABELS:
            label_pairs = [
                pair
                for window in (20.0, 40.0)
                for pair in grouped_label[(schedule, window, label)]
            ]
            summary = summarize(label_pairs)
            heldout_median_ratio_below_one += int(summary["median_ratio"] < 1.0)
            heldout_label_schedule_rows.append([
                label,
                schedule,
                f'{summary["matched"]:,}',
                fmt_ratio(summary["median_ratio"]),
                fmt_ratio(summary["median_reference_nrmse_pct"]),
                fmt_ratio(summary["median_candidate_nrmse_pct"]),
                fmt_delta(summary["median_delta_pp"]),
                f'{summary["better"]}/{summary["worse"]}',
            ])

    protocol = report["fixed_protocol"]
    gates = report["numerical_gates"]
    dft = report["dft_identity"]
    runtime = report.get("runtime", {})
    workflow_run_id = runtime.get("github_actions_run_id")
    if isinstance(workflow_run_id, (str, int)) and str(workflow_run_id).isdigit():
        workflow_line = (
            f"**Workflow:** [run {workflow_run_id}]"
            f"(https://github.com/Nolane-x/Nghien-cuu/actions/runs/{workflow_run_id})  "
        )
    else:
        workflow_line = "**Workflow:** run ID not recorded in archive  "
    lines = [
        "# PRIMA q25 role-specific seeds — held-out spatial generalization results",
        "",
        "**Date:** 26 November 2026  ",
        "**Status:** accepted numerical result; generated from case-level archive  ",
        "**Basis order:** 224  ",
        workflow_line,
        "",
        "## Executive summary",
        "",
        "This study compares D0 with basal-only, apical-only and joint 10-kHz q25 output-dual seeds at four dendritic observation sites that were not used to construct the dual seeds. The canonical seven input ports remain unchanged. Results below are recomputed from paired case-level NRMSE values, not from ratios of aggregate medians.",
        "",
        "A pooled median error ratio below 1 is not sufficient evidence of spatial generalization by itself. Interpret the four held-out labels and four morphology strata separately, and read absolute percentage-point deltas alongside ratios when D0 is near the numerical floor.",
        "",
        f"Across all four unseeded spatial locations and both windows, each candidate schedule has {heldout_schedule_rows[0][1]} paired cases. Only {heldout_median_ratio_below_one}/12 held-out-label-by-schedule combinations have a pooled median candidate/D0 ratio below 1. This is a mixed pattern, not consistent evidence of broad spatial transfer; the morphology-stratified and scenario-stratified results below remain decisive.",
        "",
        "## Spatial generalization verdict (descriptive, not a significance test)",
        "",
        markdown_table(
            ["Schedule", "Held-out pairs", "Median ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            heldout_schedule_rows,
        ),
        "",
        "The q25 seed targets are summarized separately. Strong q25-only gains alongside mixed unseeded-location results indicate target-local basis specialization rather than demonstrated broad spatial generalization.",
        "",
        markdown_table(
            ["Schedule", "q25 pairs", "Median ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            q25_schedule_rows,
        ),
        "",
        "## Held-out spatial aggregate by morphology",
        "",
        markdown_table(
            ["Morphology", "Schedule", "Pairs", "Median ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            heldout_morphology_rows,
        ),
        "",
        "This morphology aggregate pools only the four declared held-out locations and both windows within each reconstruction; each row contains 432 paired cases. It is descriptive and is not a population estimate.",
        "",
        "## Held-out location summary across both windows",
        "",
        markdown_table(
            ["Held-out output", "Schedule", "Pairs", "Median ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            heldout_label_schedule_rows,
        ),
        "",
        "All comparisons are paired at the morphology, passive scenario, window, input source and pulse-width level. Counts are descriptive; no inferential p-value or population-level claim is made. Several D0 medians are extremely small, so ratios can be unstable and absolute NRMSE and percentage-point deltas must be read together.",
        "",
        "## Fixed protocol",
        "",
        f'- Morphologies: {len(protocol["morphologies"])} individual reconstructions; {", ".join(x["neuromorpho_id"] for x in protocol["morphologies"])}.',
        f'- Passive parameter scenarios: {protocol["passive_scenario_count"]}.',
        f'- Basis order: {protocol["basis_order"]}; seven fixed input ports; {protocol["output_rows"]} observed outputs.',
        f'- Primal input shifts (Hz): {", ".join(str(x) for x in protocol["input_expansion_shifts_hz"])}.',
        f'- Sources: {", ".join(protocol["sources"])}; pulse widths: {", ".join(str(x) for x in protocol["pulse_widths_ms"])} ms.',
        f'- Timestep: {protocol["dt_ms"]} ms; windows: {", ".join(str(x) for x in protocol["windows_ms"])} ms.',
        "- q25 dual-seed schedules: D0_none, BASAL_10K, APICAL_10K, BOTH_10K.",
        "",
        "## Exact coverage and numerical gates",
        "",
        markdown_table(
            ["Evidence", "Expected", "Verified"],
            [
                ["Morphology/scenario workers", "36", str(report["coverage"]["worker_groups_passed"])],
                ["Case metrics", "22,464", str(report["coverage"]["case_metrics_read_back"])],
                ["Worker summaries", "3,744", str(report["coverage"]["group_summary_read_back"])],
                ["Morphology/window summaries", "416", str(report["coverage"]["morphology_summary_read_back"])],
                ["Scenario/window summaries", "936", str(report["coverage"]["scenario_summary_read_back"])],
                ["Pooled/window summaries", "104", str(report["coverage"]["pooled_summary_read_back"])],
                ["Finite-record DFT identities", "144", str(report["coverage"]["finite_dft_identity_read_back"])],
                ["Basis metadata rows", "144", str(report["coverage"]["basis_metadata_rows"])],
                ["Unique case keys", "22,464", str(report["coverage"]["unique_case_keys"])],
            ],
        ),
        "",
        f'- D0 exact production parity: {gates["d0_exact_production_parity_all_scenarios"]}.',
        f'- All reduced G/C matrices Cholesky-positive: {gates["all_reduced_g_c_cholesky_positive"]}.',
        f'- All models reached order 224: {gates["all_models_reached_order_224"]}.',
        f'- Seven input ports unchanged: {gates["seven_input_ports_unchanged_all_models"]}.',
        f'- Maximum basis orthogonality error: {gates["max_basis_orthogonality_abs"]:.4e}.',
        f'- All DFT identities passed: {dft["all_rows_passed"]}; maximum full-Hines residual {dft["max_full_hines_relative_error"]:.4e}; maximum reduced residual {dft["max_reduced_relative_error"]:.4e}; tolerance {dft["tolerance"]:.1e}.',
        f'- Runtime: {runtime.get("wall_seconds", float("nan")):.1f} s wall; {runtime.get("worker_processes", 0)} isolated workers.',
        "",
        "## Pooled q25 and spatial held-out readouts",
        "",
        markdown_table(
            ["Output", "Window ms", "Schedule", "Cases", "Median ratio", "P90 ratio", "Worst ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            pooled_rows,
        ),
        "",
        "The ratio for each case is candidate NRMSE divided by the D0 NRMSE for the same morphology, scenario, source, pulse width, window and output. Δ is candidate minus D0 in NRMSE percentage points. Negative Δ is better. Both median absolute NRMSE values are shown so very small D0 denominators cannot be hidden by a large relative ratio.",
        "",
        "## Output-role aggregate",
        "",
        markdown_table(
            ["Window ms", "Schedule", "Output role", "Cases", "Median ratio", "P90 ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            role_rows,
        ),
        "",
        "## Held-out results by morphology",
        "",
        markdown_table(
            ["Morphology", "Held-out output", "Window ms", "Schedule", "Median ratio", "P90 ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            morphology_rows,
        ),
        "",
        "## Held-out results by passive parameter scenario",
        "",
        markdown_table(
            ["Scenario", "Held-out output", "Window ms", "Schedule", "Cases", "Median ratio", "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ NRMSE (pp)", "Better/Worse"],
            scenario_rows,
        ),
        "",
        "Each scenario cell contains 24 matched records (four morphology strata × three sources × two pulse widths). Scenario-specific improvement is checked alongside the four morphology-specific tables above.",
        "",
        "## Exact spatial node map",
        "",
    ]
    for morph_id in sorted(node_maps):
        mapping = node_maps[morph_id]
        lines.extend([
            f"### {morph_id}",
            "",
            f'- SWC SHA-256: `{mapping["swc_sha256"]}`.',
            f'- Seven shared node IDs: {", ".join(str(x) for x in mapping["shared_swc_node_ids"])}.',
            f'- q25 node IDs: basal {mapping["q25_swc_node_ids"]["basal_q25"]}; apical {mapping["q25_swc_node_ids"]["apical_q25"]}.',
            "",
            markdown_table(
                ["Output", "SWC node ID", "Tree index", "Branch", "Path quantile"],
                [
                    [label, str(site["swc_node_id"]), str(site["tree_index"]),
                     site["branch_class"], f'{site["path_distance_quantile"]:.2f}']
                    for label, site in mapping["heldout_spatial_sites"].items()
                ],
            ),
            "",
        ])
    lines.extend([
        "## Scientific limits",
        "",
        "- Four reconstructions are four individual morphology strata, not a biological population.",
        "- This is passive linear-RC numerical reduction only: no active channels, action potentials, synapses, plasticity, calcium signalling or metabolism are simulated.",
        "- Spatial holdouts are unseeded observation sites within existing SWC reconstructions, not independent biological specimens.",
        "- Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 has no-diameter metadata.",
        "- Full Hines remains the canonical reference. No production solver, default port layout or basis-order default is changed.",
        "",
        "## Archived sources",
        "",
        f'- Case metrics: `{case_path.name}`.',
        f'- Basis/node metadata: `{metadata_path.name}`.',
        f'- Numerical report: `{json_path.name}`.',
        f'- Integrity manifest: `{manifest_path.name}`.',
        "",
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("amsn-core/results"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/PRIMA_Q25_ROLE_SPECIFIC_SPATIAL_HELDOUT_RESULTS_2026-11-26.md"
        ),
    )
    args = parser.parse_args()
    make_report(args.results_dir, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
