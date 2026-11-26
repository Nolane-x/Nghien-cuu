"""Tests for the accepted q25-versus-edge multilocation result report."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for item in (ROOT / "research", ROOT / "amsn-core", ROOT / "amsn-core" / "research"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from research.analyze_prima_q25_multilocation_seed_results import (
    CANDIDATES,
    EDGE_LABELS,
    EXPECTED_COUNTS,
    Q25_LABELS,
    SCHEDULE_SEEDS,
    percentile,
    summarize,
    validate_metadata,
)


def _metadata():
    schedules = {
        "D0_none": ("none", (), ()),
        "Q25_BOTH_10K": ("q25_both", ("basal_q25", "apical_q25"), (20, 21)),
        "BASAL_EDGES_10K": ("basal_edges", ("basal_q10", "basal_q95"), (30, 31)),
        "APICAL_EDGES_10K": ("apical_edges", ("apical_q10", "apical_q95"), (32, 33)),
        "BOTH_EDGES_10K": ("both_edges", EDGE_LABELS, (30, 31, 32, 33)),
    }
    rows = []
    for morph_id in ("NMO_A", "NMO_B", "NMO_C", "NMO_D"):
        for scenario in range(9):
            for schedule, (strategy, labels, seed_ids) in schedules.items():
                rows.append({
                    "neuromorpho_id": morph_id,
                    "scenario": f"scenario_{scenario}",
                    "schedule": schedule,
                    "seed_role": strategy,
                    "initial_output_seed_columns": len(seed_ids),
                    "seed_site_labels": list(labels),
                    "seed_swc_node_ids": list(seed_ids),
                    "seed_node_indices": [] if schedule == "D0_none" else list(seed_ids),
                    "dual_seed_frequencies_hz": [] if schedule == "D0_none" else [10000.0],
                    "actual_order": 224,
                    "seven_input_ports_unchanged": True,
                    "shared_swc_node_ids": [1, 2, 3, 4, 5, 6, 7],
                    "q25_swc_node_ids": {"basal_q25": 20, "apical_q25": 21},
                    "heldout_spatial_sites": [
                        {
                            "output_label": label,
                            "swc_node_id": node_id,
                            "tree_index": node_id + 100,
                            "branch_class": "basal" if label.startswith("basal") else "apical",
                            "path_distance_quantile": quantile,
                        }
                        for label, node_id, quantile in (
                            ("basal_q10", 30, 0.10),
                            ("basal_q95", 31, 0.95),
                            ("apical_q10", 32, 0.10),
                            ("apical_q95", 33, 0.95),
                        )
                    ],
                    "swc_sha256": "f" * 64,
                })
    assert len(rows) == 180
    return rows


def test_paired_summary_uses_absolute_delta_alongside_ratios():
    result = summarize([
        (0.5, -0.2, 0.4, 0.2),
        (1.2, 0.1, 0.4, 0.5),
        (0.8, -0.05, 0.4, 0.35),
        (1.0, 0.0, 0.4, 0.4),
    ])
    assert result["matched"] == 4
    assert result["median_ratio"] == pytest.approx(0.9)
    assert result["median_delta_pp"] == pytest.approx(-0.025)
    assert result["median_d0_nrmse_pct"] == pytest.approx(0.4)
    assert result["median_candidate_nrmse_pct"] == pytest.approx(0.375)
    assert result["better"] == 2 and result["worse"] == 1 and result["unchanged"] == 1


def test_multilocation_metadata_covers_all_morphologies_scenarios_and_schedules():
    maps = validate_metadata(_metadata())
    assert set(maps) == {"NMO_A", "NMO_B", "NMO_C", "NMO_D"}
    assert set(SCHEDULE_SEEDS) == {"D0_none", *CANDIDATES}
    assert set(Q25_LABELS).isdisjoint(EDGE_LABELS)
    assert EXPECTED_COUNTS["case_metrics_read_back"] == 28080
    assert EXPECTED_COUNTS["finite_dft_identity_read_back"] == 180


def test_metadata_fails_closed_if_an_edge_seed_collides_with_q25_or_shared_nodes():
    rows = _metadata()
    rows[0]["heldout_spatial_sites"][0]["swc_node_id"] = 20
    with pytest.raises(ValueError, match="distinct"):
        validate_metadata(rows)

    rows = _metadata()
    rows[0]["heldout_spatial_sites"][0]["swc_node_id"] = 1
    with pytest.raises(ValueError, match="distinct"):
        validate_metadata(rows)


def test_metadata_fails_closed_if_strategy_seed_list_is_not_exact():
    rows = _metadata()
    rows[0]["seed_site_labels"] = ["basal_q10"]
    with pytest.raises(ValueError, match="seed labels"):
        validate_metadata(rows)


def test_requested_multilocation_seed_budgets_distinguish_matched_and_four_seed_conditions():

    rows = _metadata()
    for row in rows:
        row["initial_output_seed_columns"] = len(row["seed_site_labels"])
    seed_ranks = {}
    for row in rows:
        seed_ranks.setdefault(row["schedule"], set()).add(row["initial_output_seed_columns"])
    assert seed_ranks["D0_none"] == {0}
    assert seed_ranks["Q25_BOTH_10K"] == {2}
    assert seed_ranks["BASAL_EDGES_10K"] == {2}
    assert seed_ranks["APICAL_EDGES_10K"] == {2}
    assert seed_ranks["BOTH_EDGES_10K"] == {4}



def test_percentile_is_interpolated_and_handles_single_values():
    assert percentile([0.0, 10.0], 0.90) == pytest.approx(9.0)
    assert percentile([2.0], 0.90) == pytest.approx(2.0)


def test_end_to_end_report_from_complete_synthetic_multilocation_archive(tmp_path):
    import csv
    import hashlib
    import json

    from research.analyze_prima_q25_multilocation_seed_results import (
        RESULT_STEM,
        make_report,
    )

    results = tmp_path / "amsn-core" / "results"
    output = tmp_path / "research" / "multilocation.md"
    results.mkdir(parents=True)

    morphologies = [
        ("NMO_A", "Morphology A"),
        ("NMO_B", "Morphology B"),
        ("NMO_C", "Morphology C"),
        ("NMO_D", "Morphology D"),
    ]
    scenarios = [f"scenario_{i}" for i in range(9)]
    outputs = [
        ("shared_output", f"shared_{i}", i, None)
        for i in range(1, 8)
    ] + [
        ("q25_output", "basal_q25", 8, None),
        ("q25_output", "apical_q25", 9, None),
        ("heldout_spatial_output", "basal_q10", 10, ("basal", 0.10)),
        ("heldout_spatial_output", "basal_q95", 11, ("basal", 0.95)),
        ("heldout_spatial_output", "apical_q10", 12, ("apical", 0.10)),
        ("heldout_spatial_output", "apical_q95", 13, ("apical", 0.95)),
    ]
    strategy_labels = {
        "D0_none": (),
        "Q25_BOTH_10K": ("basal_q25", "apical_q25"),
        "BASAL_EDGES_10K": ("basal_q10", "basal_q95"),
        "APICAL_EDGES_10K": ("apical_q10", "apical_q95"),
        "BOTH_EDGES_10K": ("basal_q10", "basal_q95", "apical_q10", "apical_q95"),
    }
    schedules = tuple(strategy_labels)

    case_path = results / f"{RESULT_STEM}_case_metrics.csv"
    case_fields = [
        "morphology", "neuromorpho_id", "scenario", "schedule",
        "window_ms", "source", "pulse_width_ms", "output_role",
        "output_label", "transient_nrmse_pct",
    ]
    rows = []
    for morph_id, morph_name in morphologies:
        for scenario in scenarios:
            for schedule in schedules:
                for window in (20.0, 40.0):
                    for source in ("soma", "basal_q75", "apical_q75"):
                        for pulse_width in (2.0, 10.0):
                            for role, label, _node, _meta in outputs:
                                baseline = 0.8
                                value = baseline
                                if schedule != "D0_none":
                                    if label in ("shared_1", "shared_2", "shared_3",
                                                 "shared_4", "shared_5", "shared_6", "shared_7"):
                                        value = 0.81
                                    elif schedule == "Q25_BOTH_10K":
                                        value = 0.2 if role == "q25_output" else 1.0
                                    elif schedule == "BASAL_EDGES_10K":
                                        value = 0.4 if label.startswith("basal_q") else 0.75
                                    elif schedule == "APICAL_EDGES_10K":
                                        value = 0.4 if label.startswith("apical_q") else 0.75
                                    elif schedule == "BOTH_EDGES_10K":
                                        value = 0.3 if role == "heldout_spatial_output" else 0.5
                                rows.append({
                                    "morphology": morph_name,
                                    "neuromorpho_id": morph_id,
                                    "scenario": scenario,
                                    "schedule": schedule,
                                    "window_ms": window,
                                    "source": source,
                                    "pulse_width_ms": pulse_width,
                                    "output_role": role,
                                    "output_label": label,
                                    "transient_nrmse_pct": value,
                                })
    assert len(rows) == 28080
    with case_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=case_fields)
        writer.writeheader()
        writer.writerows(rows)

    metadata = []
    seed_maps = {
        "basal_q25": 8, "apical_q25": 9,
        "basal_q10": 10, "basal_q95": 11,
        "apical_q10": 12, "apical_q95": 13,
    }
    for morph_id, _morph_name in morphologies:
        for scenario in scenarios:
            for schedule in schedules:
                labels = strategy_labels[schedule]
                metadata.append({
                    "neuromorpho_id": morph_id,
                    "scenario": scenario,
                    "schedule": schedule,
                    "seed_role": {
                        "D0_none": "none",
                        "Q25_BOTH_10K": "q25_both",
                        "BASAL_EDGES_10K": "basal_edges",
                        "APICAL_EDGES_10K": "apical_edges",
                        "BOTH_EDGES_10K": "both_edges",
                    }[schedule],
                    "initial_output_seed_columns": len(labels),
                    "seed_site_labels": list(labels),
                    "seed_swc_node_ids": [seed_maps[x] for x in labels],
                    "seed_node_indices": [] if schedule == "D0_none" else [seed_maps[x] for x in labels],
                    "dual_seed_frequencies_hz": [] if schedule == "D0_none" else [10000.0],
                    "actual_order": 224,
                    "seven_input_ports_unchanged": True,
                    "shared_swc_node_ids": [1, 2, 3, 4, 5, 6, 7],
                    "q25_swc_node_ids": {"basal_q25": 8, "apical_q25": 9},
                    "heldout_spatial_sites": [
                        {
                            "output_label": label,
                            "swc_node_id": node,
                            "tree_index": node + 100,
                            "branch_class": "basal" if label.startswith("basal") else "apical",
                            "path_distance_quantile": quantile,
                        }
                        for label, node, quantile in (
                            ("basal_q10", 10, 0.10),
                            ("basal_q95", 11, 0.95),
                            ("apical_q10", 12, 0.10),
                            ("apical_q95", 13, 0.95),
                        )
                    ],
                    "swc_sha256": "f" * 64,
                })
    assert len(metadata) == 180
    metadata_path = results / f"{RESULT_STEM}_basis_metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    counts = {
        "worker_groups_expected": 36,
        "worker_groups_passed": 36,
        "case_metrics_expected": 28080,
        "case_metrics_read_back": 28080,
        "group_summary_expected": 4680,
        "group_summary_read_back": 4680,
        "morphology_summary_expected": 520,
        "morphology_summary_read_back": 520,
        "scenario_summary_expected": 1170,
        "scenario_summary_read_back": 1170,
        "pooled_summary_expected": 130,
        "pooled_summary_read_back": 130,
        "finite_dft_identity_expected": 180,
        "finite_dft_identity_read_back": 180,
        "basis_metadata_rows": 180,
        "unique_case_keys": 28080,
    }
    report = {
        "schema_version": 1,
        "status": "passed",
        "fixed_protocol": {
            "basis_order": 224,
            "morphologies": [
                {"neuromorpho_id": morph_id, "name": name, "expected_swc_sha256": "f" * 64}
                for morph_id, name in morphologies
            ],
            "passive_scenarios": scenarios,
        },
        "coverage": counts,
        "numerical_gates": {
            "d0_exact_production_parity_all_scenarios": True,
            "all_reduced_g_c_cholesky_positive": True,
            "all_models_reached_order_224": True,
            "seven_input_ports_unchanged_all_models": True,
            "max_basis_orthogonality_abs": 1e-15,
        },
        "dft_identity": {
            "all_rows_passed": True,
            "max_full_hines_relative_error": 1e-12,
            "max_reduced_relative_error": 1e-12,
            "tolerance": 2e-8,
        },
        "runtime": {
            "wall_seconds": 40.0,
            "worker_processes": 36,
            "github_actions_run_id": "987654321",
        },
    }
    report_path = results / f"{RESULT_STEM}_report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    file_rows = []
    for suffix, expected_count in (
        ("group_summary", 4680),
        ("morphology_summary", 520),
        ("scenario_summary", 1170),
        ("pooled_summary", 130),
        ("finite_dft_identity", 180),
    ):
        path = results / f"{RESULT_STEM}_{suffix}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["row"])
            writer.writerows([[i] for i in range(expected_count)])
        file_rows.append(path)
    timing_path = results / f"{RESULT_STEM}.time.txt"
    timing_path.write_text("exit_status=0\n", encoding="utf-8")
    file_rows.extend([case_path, metadata_path, report_path, timing_path])
    assert len(file_rows) == 9
    manifest = {
        "status": "passed",
        "files": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in file_rows
        ],
    }
    (results / f"{RESULT_STEM}_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    make_report(results, output)
    rendered = output.read_text(encoding="utf-8")
    assert "## Seed strategy comparison" in rendered
    assert "## Readout-specific transfer" in rendered
    assert "## Results by morphology" in rendered
    assert "## Results by passive parameter scenario" in rendered
    assert "## Exact coverage and numerical gates" in rendered
    assert "Source run 987654321" in rendered or "run 987654321" in rendered
    assert "| Q25_BOTH_10K | basal_q25, apical_q25 | 2 | 2 (2–2) | 864 |" in rendered
    assert "| BASAL_EDGES_10K | basal_q10, basal_q95 | 2 | 2 (2–2) | 864 |" in rendered
    assert "| APICAL_EDGES_10K | apical_q10, apical_q95 | 2 | 2 (2–2) | 864 |" in rendered
    assert "| BOTH_EDGES_10K | basal_q10, basal_q95, apical_q10, apical_q95 | 4 | 4 (4–4) | 864 |" in rendered
