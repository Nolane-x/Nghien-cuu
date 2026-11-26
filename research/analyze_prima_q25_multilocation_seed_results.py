#!/usr/bin/env python3
"""Auditable paired-case report for q25-versus-edge multilocation PRIMA seeds."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

RESULT_STEM = (
    "prima_q25_four_morphology_multilocation_output_dual_seed"
    "_order224_2026-11-26"
)
EXPECTED_COUNTS = {
    "case_metrics_read_back": 28080,
    "group_summary_read_back": 4680,
    "morphology_summary_read_back": 520,
    "scenario_summary_read_back": 1170,
    "pooled_summary_read_back": 130,
    "finite_dft_identity_read_back": 180,
    "basis_metadata_rows": 180,
    "unique_case_keys": 28080,
}
SCHEDULES = (
    "D0_none",
    "Q25_BOTH_10K",
    "BASAL_EDGES_10K",
    "APICAL_EDGES_10K",
    "BOTH_EDGES_10K",
)
CANDIDATES = SCHEDULES[1:]
Q25_LABELS = ("basal_q25", "apical_q25")
EDGE_LABELS = ("basal_q10", "basal_q95", "apical_q10", "apical_q95")
SHARED_LABELS = tuple(f"shared_{i}" for i in range(1, 8))
OUTPUT_LABELS = SHARED_LABELS + Q25_LABELS + EDGE_LABELS
SCHEDULE_SEEDS = {
    "D0_none": (),
    "Q25_BOTH_10K": Q25_LABELS,
    "BASAL_EDGES_10K": ("basal_q10", "basal_q95"),
    "APICAL_EDGES_10K": ("apical_q10", "apical_q95"),
    "BOTH_EDGES_10K": EDGE_LABELS,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
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


def summarize(pairs: list[tuple[float, float, float, float]]) -> dict[str, Any]:
    ratios = [x[0] for x in pairs]
    deltas = [x[1] for x in pairs]
    baselines = [x[2] for x in pairs]
    candidates = [x[3] for x in pairs]
    return {
        "matched": len(pairs),
        "median_ratio": float(statistics.median(ratios)),
        "p90_ratio": percentile(ratios, 0.90),
        "worst_ratio": max(ratios),
        "median_d0_nrmse_pct": float(statistics.median(baselines)),
        "median_candidate_nrmse_pct": float(statistics.median(candidates)),
        "median_delta_pp": float(statistics.median(deltas)),
        "better": sum(x < 0.0 for x in deltas),
        "worse": sum(x > 0.0 for x in deltas),
        "unchanged": sum(x == 0.0 for x in deltas),
    }


def validate_metadata(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    require(len(rows) == 180, f"expected 180 basis metadata rows, got {len(rows)}")
    mapping_by_morphology: dict[str, dict[str, Any]] = {}
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        morph_id = str(row["neuromorpho_id"])
        schedule = str(row["schedule"])
        scenario = str(row["scenario"])
        require(schedule in SCHEDULES, f"{morph_id}: unknown schedule {schedule}")
        require(row["actual_order"] == 224, f"{morph_id}/{schedule}: basis order is not 224")
        require(row["seven_input_ports_unchanged"] is True,
                f"{morph_id}/{schedule}: seven-port selector changed")
        key = (morph_id, scenario, schedule)
        require(key not in seen, f"duplicate basis metadata identity: {key}")
        seen.add(key)

        shared = [int(x) for x in row["shared_swc_node_ids"]]
        q25 = {str(k): int(v) for k, v in row["q25_swc_node_ids"].items()}
        edge_rows = row["heldout_spatial_sites"]
        edges = {
            str(x["output_label"]): {
                "swc_node_id": int(x["swc_node_id"]),
                "tree_index": int(x["tree_index"]),
                "branch_class": str(x["branch_class"]),
                "path_distance_quantile": float(x["path_distance_quantile"]),
            }
            for x in edge_rows
        }
        require(len(shared) == 7 and len(set(shared)) == 7,
                f"{morph_id}: shared map must contain seven unique SWC nodes")
        require(set(q25) == set(Q25_LABELS) and len(set(q25.values())) == 2,
                f"{morph_id}: q25 map malformed")
        require(set(edges) == set(EDGE_LABELS) and len(edges) == 4,
                f"{morph_id}: edge map malformed")
        edge_ids = {x["swc_node_id"] for x in edges.values()}
        all_ids = set(shared) | set(q25.values()) | edge_ids
        require(len(edge_ids) == 4 and len(all_ids) == 13,
                f"{morph_id}: 13 observed SWC nodes are not distinct")

        seed_labels = tuple(str(x) for x in row.get("seed_site_labels", []))
        expected_seeds = SCHEDULE_SEEDS[schedule]
        require(seed_labels == expected_seeds,
                f"{morph_id}/{schedule}: seed labels {seed_labels} != {expected_seeds}")
        accepted_seed_columns = int(row["initial_output_seed_columns"])
        require(0 <= accepted_seed_columns <= len(expected_seeds),
                f"{morph_id}/{schedule}: accepted dual rank exceeds requested seed count")
        if schedule == "D0_none":
            require(accepted_seed_columns == 0,
                    f"{morph_id}: D0 unexpectedly retained output-dual columns")
        seed_swc = [int(x) for x in row.get("seed_swc_node_ids", [])]
        expected_swc = [
            q25[label] if label in q25 else edges[label]["swc_node_id"]
            for label in expected_seeds
        ]
        require(seed_swc == expected_swc,
                f"{morph_id}/{schedule}: seed SWC node IDs do not match the pinned readout map")
        dual_freq = [float(x) for x in row.get("dual_seed_frequencies_hz", [])]
        require(dual_freq == ([] if schedule == "D0_none" else [10000.0]),
                f"{morph_id}/{schedule}: dual shift differs from the protocol")
        if schedule == "D0_none":
            require(row.get("seed_node_indices") == [],
                    f"{morph_id}: D0 must not create output-dual seed columns")

        current = {
            "shared_swc_node_ids": shared,
            "q25_swc_node_ids": q25,
            "edge_spatial_sites": edges,
            "swc_sha256": str(row.get("swc_sha256", "")),
        }
        previous = mapping_by_morphology.get(morph_id)
        if previous is not None:
            require(previous == current,
                    f"{morph_id}: readout node mapping changed across schedules/scenarios")
        else:
            mapping_by_morphology[morph_id] = current

    require(len(mapping_by_morphology) == 4,
            f"expected four morphology maps, got {len(mapping_by_morphology)}")
    require(len(seen) == 180, "metadata does not cover every morphology/scenario/schedule cell")
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
    report_path = results_dir / f"{RESULT_STEM}_report.json"
    cases_path = results_dir / f"{RESULT_STEM}_case_metrics.csv"
    metadata_path = results_dir / f"{RESULT_STEM}_basis_metadata.json"
    manifest_path = results_dir / f"{RESULT_STEM}_manifest.json"

    report = read_json(report_path)
    manifest = read_json(manifest_path)
    cases = read_csv(cases_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    require(report.get("status") == "passed", "numerical report status is not passed")
    require(manifest.get("status") == "passed", "archive manifest status is not passed")
    require(len(manifest.get("files", [])) == 9, "manifest must cover nine archive files")
    for entry in manifest["files"]:
        path = results_dir / entry["path"]
        require(path.is_file(), f"manifest file is missing: {path.name}")
        require(path.stat().st_size == entry["bytes"], f"manifest byte count mismatch: {path.name}")
        require(sha256_file(path) == entry["sha256"], f"manifest SHA-256 mismatch: {path.name}")

    for key, expected in EXPECTED_COUNTS.items():
        observed = len(cases) if key in {"case_metrics_read_back", "unique_case_keys"} \
            else int(report["coverage"][key])
        require(observed == expected, f"{key}: expected {expected}, got {observed}")

    actual_csv_counts = {
        "group_summary": 4680,
        "morphology_summary": 520,
        "scenario_summary": 1170,
        "pooled_summary": 130,
        "finite_dft_identity": 180,
    }
    for suffix, expected in actual_csv_counts.items():
        path = results_dir / f"{RESULT_STEM}_{suffix}.csv"
        observed = len(read_csv(path))
        require(observed == expected,
                f"{suffix} CSV: expected {expected} rows, got {observed}")

    gates = report["numerical_gates"]
    for name in (
        "d0_exact_production_parity_all_scenarios",
        "all_reduced_g_c_cholesky_positive",
        "all_models_reached_order_224",
        "seven_input_ports_unchanged_all_models",
    ):
        require(gates[name] is True, f"numerical gate failed: {name}")
    dft = report["dft_identity"]
    require(dft["all_rows_passed"] is True, "not all finite-record DFT identities passed")
    require(dft["max_full_hines_relative_error"] < dft["tolerance"],
            "full-Hines DFT identity exceeded tolerance")
    require(dft["max_reduced_relative_error"] < dft["tolerance"],
            "reduced DFT identity exceeded tolerance")
    require(gates["max_basis_orthogonality_abs"] < 2e-12,
            "basis orthogonality gate failed")

    node_maps = validate_metadata(metadata)
    protocol = report["fixed_protocol"]
    morphology_hashes = {
        item["neuromorpho_id"]: item["expected_swc_sha256"]
        for item in protocol["morphologies"]
    }
    require(set(node_maps) == set(morphology_hashes),
            "metadata morphologies differ from the pinned source manifest")
    for morph_id, mapping in node_maps.items():
        mapping["swc_sha256"] = morphology_hashes[morph_id]

    expected_output_roles = {
        **{label: "shared_output" for label in SHARED_LABELS},
        **{label: "q25_output" for label in Q25_LABELS},
        **{label: "heldout_spatial_output" for label in EDGE_LABELS},
    }
    seen_case_keys: set[tuple[Any, ...]] = set()
    baseline: dict[tuple[Any, ...], float] = {}
    for row in cases:
        require(row["schedule"] in SCHEDULES, f"unknown case schedule: {row['schedule']}")
        label = row["output_label"]
        require(label in OUTPUT_LABELS, f"unknown output label: {label}")
        require(row["output_role"] == expected_output_roles[label],
                f"{label}: output role mismatch")
        key = (
            row["morphology"], row["neuromorpho_id"], row["scenario"],
            row["schedule"], float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), label,
        )
        require(key not in seen_case_keys, f"duplicate case key: {key}")
        seen_case_keys.add(key)
        if row["schedule"] == "D0_none":
            baseline_key = (
                row["morphology"], row["neuromorpho_id"], row["scenario"],
                float(row["window_ms"]), row["source"],
                float(row["pulse_width_ms"]), label,
            )
            require(baseline_key not in baseline, f"duplicate D0 key: {baseline_key}")
            baseline[baseline_key] = float(row["transient_nrmse_pct"])
    require(len(seen_case_keys) == 28080, "case identities are not complete")

    grouped_output: dict[tuple[str, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_label: dict[tuple[str, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_morph: dict[tuple[str, str, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    grouped_scenario: dict[tuple[str, str, str], list[tuple[float, float, float, float]]] = defaultdict(list)
    for row in cases:
        schedule = row["schedule"]
        if schedule == "D0_none":
            continue
        baseline_key = (
            row["morphology"], row["neuromorpho_id"], row["scenario"],
            float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), row["output_label"],
        )
        require(baseline_key in baseline, f"missing exact paired D0 row: {baseline_key}")
        candidate = float(row["transient_nrmse_pct"])
        reference = baseline[baseline_key]
        pair = (
            candidate / max(reference, 1e-30),
            candidate - reference,
            reference,
            candidate,
        )
        role = row["output_role"]
        label = row["output_label"]
        grouped_output[(schedule, role)].append(pair)
        grouped_label[(schedule, label)].append(pair)
        grouped_morph[(row["neuromorpho_id"], schedule, role)].append(pair)
        grouped_scenario[(row["scenario"], schedule, role)].append(pair)

    metadata_by_schedule: dict[str, list[int]] = defaultdict(list)
    for row in metadata:
        metadata_by_schedule[str(row["schedule"])].append(
            int(row["initial_output_seed_columns"])
        )
    for schedule in SCHEDULES:
        require(len(metadata_by_schedule[schedule]) == 36,
                f"{schedule}: expected 36 observed seed-rank entries")
        if schedule == "D0_none":
            require(all(x == 0 for x in metadata_by_schedule[schedule]),
                    "D0 unexpectedly retained output-dual columns")

    strategy_rows = []
    for schedule in CANDIDATES:
        q25_summary = summarize([
            pair for label in Q25_LABELS for pair in grouped_label[(schedule, label)]
        ])
        edge_summary = summarize([
            pair for label in EDGE_LABELS for pair in grouped_label[(schedule, label)]
        ])
        shared_summary = summarize([
            pair for label in SHARED_LABELS for pair in grouped_label[(schedule, label)]
        ])
        seed_labels = ", ".join(SCHEDULE_SEEDS[schedule])
        accepted_rank_values = metadata_by_schedule[schedule]
        rank_label = (
            f"{statistics.median(accepted_rank_values):g} "
            f"({min(accepted_rank_values)}–{max(accepted_rank_values)})"
        )
        strategy_rows.append([
            schedule,
            seed_labels,
            str(len(SCHEDULE_SEEDS[schedule])),
            rank_label,
            f"{q25_summary['matched']:,}",
            fmt_ratio(q25_summary["median_ratio"]),
            fmt_delta(q25_summary["median_delta_pp"]),
            f"{edge_summary['matched']:,}",
            fmt_ratio(edge_summary["median_ratio"]),
            fmt_delta(edge_summary["median_delta_pp"]),
            fmt_ratio(shared_summary["median_ratio"]),
            fmt_delta(shared_summary["median_delta_pp"]),
        ])

    label_rows = []
    for label in Q25_LABELS + EDGE_LABELS:
        for schedule in CANDIDATES:
            summary = summarize(grouped_label[(schedule, label)])
            label_rows.append([
                label, schedule, f"{summary['matched']:,}",
                fmt_ratio(summary["median_ratio"]),
                fmt_ratio(summary["median_d0_nrmse_pct"]),
                fmt_ratio(summary["median_candidate_nrmse_pct"]),
                fmt_delta(summary["median_delta_pp"]),
                f"{summary['better']}/{summary['worse']}",
            ])

    morphology_rows = []
    for morph_id in sorted(node_maps):
        for schedule in CANDIDATES:
            for role in ("q25_output", "heldout_spatial_output", "shared_output"):
                summary = summarize(grouped_morph[(morph_id, schedule, role)])
                morphology_rows.append([
                    morph_id, schedule, role, f"{summary['matched']:,}",
                    fmt_ratio(summary["median_ratio"]),
                    fmt_ratio(summary["median_d0_nrmse_pct"]),
                    fmt_ratio(summary["median_candidate_nrmse_pct"]),
                    fmt_delta(summary["median_delta_pp"]),
                    f"{summary['better']}/{summary['worse']}",
                ])

    scenario_rows = []
    for scenario in protocol["passive_scenarios"]:
        for schedule in CANDIDATES:
            for role in ("q25_output", "heldout_spatial_output"):
                summary = summarize(grouped_scenario[(scenario, schedule, role)])
                scenario_rows.append([
                    scenario, schedule, role, f"{summary['matched']:,}",
                    fmt_ratio(summary["median_ratio"]),
                    fmt_delta(summary["median_delta_pp"]),
                    f"{summary['better']}/{summary['worse']}",
                ])

    runtime = report.get("runtime", {})
    run_id = runtime.get("github_actions_run_id")
    workflow_line = (
        f"**Numerical workflow:** [run {run_id}]"
        f"(https://github.com/Nolane-x/Nghien-cuu/actions/runs/{run_id})  "
        if isinstance(run_id, (str, int)) and str(run_id).isdigit()
        else "**Numerical workflow:** source run ID unavailable  "
    )

    lines = [
        "# PRIMA q25-versus-edge multilocation output-dual seed results",
        "",
        "**Date:** 26 November 2026  ",
        "**Status:** accepted numerical archive; generated from paired case-level data  ",
        "**Basis order:** 224  ",
        workflow_line,
        "",
        "## Executive summary",
        "",
        "This experiment reverses the seed placement from the prior q25 study. It compares q25-target seeds with basal/apical edge seeds, while measuring the same 13 readouts in every schedule. The seven input ports, primal shifts, numerical integrator and full-Hines reference remain unchanged.",
        "",
        "The transfer directions differ by schedule: Q25_BOTH_10K seeds q25 and leaves four edge outputs unseeded; edge schedules seed two or four edge outputs and leave q25 outputs unseeded. A row used as a seed is not treated as a held-out validation for that schedule.",
        "",
        "## Seed strategy comparison",
        "",
        markdown_table(
            ["Schedule", "Seed labels", "Requested sites", "Accepted initial dual columns\nmedian (min–max)",
             "q25 pairs", "q25 median ratio", "q25 median Δ (pp)",
             "edge pairs", "edge median ratio", "edge median Δ (pp)",
             "shared median ratio", "shared median Δ (pp)"],
            strategy_rows,
        ),
        "",
        "Requested seed sites are the predeclared coordinate count; accepted initial dual columns are the observed independent directions retained after reorthogonalization (median and min–max over 36 morphology/scenario cells). The primary resource-matched comparisons are Q25_BOTH_10K, BASAL_EDGES_10K and APICAL_EDGES_10K (two requested sites each). BOTH_EDGES_10K requests four sites and is a higher-budget coverage condition, not a location-only comparison.",
        "",
        "Ratios compare candidate NRMSE with the exact paired D0 case. Negative percentage-point deltas indicate lower candidate error. Read both because D0 may be close to the numerical floor.",
        "",
        "## Readout-specific transfer",
        "",
        markdown_table(
            ["Output", "Schedule", "Pairs", "Median ratio", "Median D0 NRMSE (%)",
             "Median candidate NRMSE (%)", "Median Δ (pp)", "Better/Worse"],
            label_rows,
        ),
        "",
        "## Results by morphology",
        "",
        markdown_table(
            ["Morphology", "Schedule", "Output role", "Pairs", "Median ratio",
             "Median D0 NRMSE (%)", "Median candidate NRMSE (%)", "Median Δ (pp)", "Better/Worse"],
            morphology_rows,
        ),
        "",
        "## Results by passive parameter scenario",
        "",
        markdown_table(
            ["Scenario", "Schedule", "Output role", "Pairs", "Median ratio",
             "Median Δ (pp)", "Better/Worse"],
            scenario_rows,
        ),
        "",
        "## Exact coverage and numerical gates",
        "",
        markdown_table(
            ["Evidence", "Expected", "Verified"],
            [
                ["Morphology/scenario workers", "36", str(report["coverage"]["worker_groups_passed"])],
                ["Case metrics", "28,080", str(report["coverage"]["case_metrics_read_back"])],
                ["Worker summaries", "4,680", str(report["coverage"]["group_summary_read_back"])],
                ["Morphology/window summaries", "520", str(report["coverage"]["morphology_summary_read_back"])],
                ["Scenario/window summaries", "1,170", str(report["coverage"]["scenario_summary_read_back"])],
                ["Pooled/window summaries", "130", str(report["coverage"]["pooled_summary_read_back"])],
                ["Finite-record DFT identities", "180", str(report["coverage"]["finite_dft_identity_read_back"])],
                ["Basis metadata rows", "180", str(report["coverage"]["basis_metadata_rows"])],
                ["Unique case keys", "28,080", str(report["coverage"]["unique_case_keys"])],
            ],
        ),
        "",
        f"- D0 exact production parity: {gates['d0_exact_production_parity_all_scenarios']}.",
        f"- All reduced G/C matrices Cholesky-positive: {gates['all_reduced_g_c_cholesky_positive']}.",
        f"- Every model reached order 224: {gates['all_models_reached_order_224']}.",
        f"- Seven input ports unchanged: {gates['seven_input_ports_unchanged_all_models']}.",
        f"- Maximum basis orthogonality error: {gates['max_basis_orthogonality_abs']:.4e}.",
        f"- All DFT identities passed: {dft['all_rows_passed']}; max full-Hines residual {dft['max_full_hines_relative_error']:.4e}; max reduced residual {dft['max_reduced_relative_error']:.4e}; tolerance {dft['tolerance']:.1e}.",
        f"- Runtime: {runtime.get('wall_seconds', float('nan')):.1f} s wall; {runtime.get('worker_processes', 0)} isolated workers.",
        "",
        "## Exact SWC node map",
        "",
    ]
    morphology_names = {x["neuromorpho_id"]: x["name"] for x in protocol["morphologies"]}
    for morph_id in sorted(node_maps):
        mapping = node_maps[morph_id]
        edges = mapping["edge_spatial_sites"]
        lines.extend([
            f"### {morph_id} — {morphology_names[morph_id]}",
            "",
            f"- SWC SHA-256: `{mapping['swc_sha256']}`.",
            f"- Shared seven: {', '.join(str(x) for x in mapping['shared_swc_node_ids'])}.",
            f"- q25: basal {mapping['q25_swc_node_ids']['basal_q25']}; apical {mapping['q25_swc_node_ids']['apical_q25']}.",
            "",
            markdown_table(
                ["Edge output", "SWC node ID", "Tree index", "Branch", "Path quantile"],
                [
                    [label, str(site["swc_node_id"]), str(site["tree_index"]),
                     site["branch_class"], f"{site['path_distance_quantile']:.2f}"]
                    for label, site in edges.items()
                ],
            ),
            "",
        ])
    lines.extend([
        "## Scientific limits",
        "",
        "- Four individual reconstructions are morphology strata, not a biological population.",
        "- This is passive linear-RC model reduction only; active channels, spikes, synapses, plasticity, calcium signalling, metabolism and cognition are not modeled.",
        "- q25/edge seed rows are measured in all schedules; only the rows not seeded by a given schedule are transfer readouts for that schedule.",
        "- Relative ratios are secondary when D0 error is near the numerical floor; absolute percentage-point deltas must also be interpreted.",
        "- Full Hines remains canonical. No production solver or default has changed.",
        "",
        "## Archived sources",
        "",
        f"- Case metrics: `{cases_path.name}`.",
        f"- Basis metadata: `{metadata_path.name}`.",
        f"- Numerical report: `{report_path.name}`.",
        f"- Integrity manifest: `{manifest_path.name}`.",
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
        default=Path("research/PRIMA_Q25_MULTILOCATION_OUTPUT_DUAL_SEED_RESULTS_2026-11-26.md"),
    )
    args = parser.parse_args()
    make_report(args.results_dir, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
