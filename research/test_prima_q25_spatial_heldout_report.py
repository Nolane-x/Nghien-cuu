"""Unit tests for paired-case spatial held-out result reporting."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.analyze_prima_q25_spatial_heldout_results import (
    HELDOUT_LABELS,
    Q25_LABELS,
    RESULT_STEM,
    make_report,
    percentile,
    summarize,
    validate_node_metadata,
)


def _metadata_rows():
    rows = []
    for morph_id in ("NMO_A", "NMO_B", "NMO_C", "NMO_D"):
        for scenario in range(9):
            for schedule in ("D0_none", "BASAL_10K", "APICAL_10K", "BOTH_10K"):
                rows.append({
                    "neuromorpho_id": morph_id,
                    "actual_order": 224,
                    "seven_input_ports_unchanged": True,
                    "shared_swc_node_ids": [1, 2, 3, 4, 5, 6, 7],
                    "q25_swc_node_ids": {
                        "basal_q25": 8,
                        "apical_q25": 9,
                    },
                    "heldout_spatial_sites": [
                        {
                            "output_role": "heldout_spatial_output",
                            "output_label": label,
                            "swc_node_id": node_id,
                            "tree_index": node_id + 100,
                            "branch_class": "basal" if label.startswith("basal") else "apical",
                            "path_distance_quantile": quantile,
                        }
                        for label, node_id, quantile in (
                            ("basal_q10", 10, 0.10),
                            ("basal_q95", 11, 0.95),
                            ("apical_q10", 12, 0.10),
                            ("apical_q95", 13, 0.95),
                        )
                    ],
                })
    assert len(rows) == 144
    return rows


def test_percentile_uses_linear_interpolation_and_handles_singleton():
    assert percentile([0.0, 10.0], 0.90) == pytest.approx(9.0)
    assert percentile([1.0], 0.90) == pytest.approx(1.0)


def test_paired_summary_keeps_absolute_deltas_and_direction_counts():
    result = summarize([
        (0.5, -0.2, 0.4, 0.2),
        (1.2, 0.1, 0.4, 0.5),
        (0.8, -0.05, 0.4, 0.35),
        (1.0, 0.0, 0.4, 0.4),
    ])
    assert result["matched"] == 4
    assert result["median_ratio"] == pytest.approx(0.9)
    assert result["median_delta_pp"] == pytest.approx(-0.025)
    assert result["median_reference_nrmse_pct"] == pytest.approx(0.4)
    assert result["median_candidate_nrmse_pct"] == pytest.approx(0.375)
    assert result["better"] == 2
    assert result["worse"] == 1
    assert result["unchanged"] == 1


def test_node_metadata_requires_four_unique_spatial_holdouts_and_13_distinct_nodes():
    mapping = validate_node_metadata(_metadata_rows())
    assert set(mapping) == {"NMO_A", "NMO_B", "NMO_C", "NMO_D"}
    assert set(mapping["NMO_A"]["heldout_spatial_sites"]) == set(HELDOUT_LABELS)
    assert set(mapping["NMO_A"]["q25_swc_node_ids"]) == set(Q25_LABELS)


def test_node_metadata_fails_closed_on_holdout_or_target_collisions():
    rows = _metadata_rows()
    rows[0]["heldout_spatial_sites"][0]["swc_node_id"] = 8
    with pytest.raises(ValueError, match="collide"):
        validate_node_metadata(rows)

    rows = _metadata_rows()
    rows[0]["heldout_spatial_sites"][0]["swc_node_id"] = 11
    with pytest.raises(ValueError, match="distinct"):
        validate_node_metadata(rows)


def test_end_to_end_report_generation_from_complete_synthetic_archive(tmp_path):
    results_dir = tmp_path / "amsn-core" / "results"
    report_path = tmp_path / "research" / "results.md"
    results_dir.mkdir(parents=True)

    morphologies = [
        ("NMO_A", "Morphology A"),
        ("NMO_B", "Morphology B"),
        ("NMO_C", "Morphology C"),
        ("NMO_D", "Morphology D"),
    ]
    scenarios = [
        "nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
        "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20",
    ]
    schedules = ("D0_none", "BASAL_10K", "APICAL_10K", "BOTH_10K")
    outputs = [
        ("shared_output", f"shared_{index}", index, None)
        for index in range(1, 8)
    ] + [
        ("q25_output", "basal_q25", 8, None),
        ("q25_output", "apical_q25", 9, None),
    ] + [
        ("heldout_spatial_output", "basal_q10", 10, ("basal", 0.10)),
        ("heldout_spatial_output", "basal_q95", 11, ("basal", 0.95)),
        ("heldout_spatial_output", "apical_q10", 12, ("apical", 0.10)),
        ("heldout_spatial_output", "apical_q95", 13, ("apical", 0.95)),
    ]

    case_path = results_dir / f"{RESULT_STEM}_case_metrics.csv"
    fieldnames = [
        "morphology", "neuromorpho_id", "scenario", "schedule", "window_ms",
        "source", "pulse_width_ms", "output_role", "output_label",
        "swc_node_id", "transient_nrmse_pct",
    ]
    rows = []
    for morph_id, morph_name in morphologies:
        for scenario in scenarios:
            for schedule in schedules:
                for window_ms in (20.0, 40.0):
                    for source in ("soma", "basal_q75", "apical_q75"):
                        for pulse_width_ms in (2.0, 10.0):
                            for role, label, node_id, _spatial_meta in outputs:
                                baseline = 0.80 + (node_id * 0.01)
                                candidate = baseline if schedule == "D0_none" else baseline * 0.8
                                rows.append({
                                    "morphology": morph_name,
                                    "neuromorpho_id": morph_id,
                                    "scenario": scenario,
                                    "schedule": schedule,
                                    "window_ms": window_ms,
                                    "source": source,
                                    "pulse_width_ms": pulse_width_ms,
                                    "output_role": role,
                                    "output_label": label,
                                    "swc_node_id": node_id,
                                    "transient_nrmse_pct": candidate,
                                })
    assert len(rows) == 22464
    with case_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    metadata = []
    for morph_id, _morph_name in morphologies:
        for scenario in scenarios:
            for schedule in schedules:
                metadata.append({
                    "neuromorpho_id": morph_id,
                    "actual_order": 224,
                    "seven_input_ports_unchanged": True,
                    "shared_swc_node_ids": [1, 2, 3, 4, 5, 6, 7],
                    "q25_swc_node_ids": {
                        "basal_q25": 8,
                        "apical_q25": 9,
                    },
                    "heldout_spatial_sites": [
                        {
                            "output_role": role,
                            "output_label": label,
                            "swc_node_id": node_id,
                            "tree_index": node_id + 100,
                            "branch_class": meta[0],
                            "path_distance_quantile": meta[1],
                        }
                        for role, label, node_id, meta in outputs
                        if meta is not None
                    ],
                })
    assert len(metadata) == 144
    metadata_path = results_dir / f"{RESULT_STEM}_basis_metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    report = {
        "status": "passed",
        "coverage": {
            "worker_groups_passed": 36,
            "case_metrics_read_back": 22464,
            "group_summary_read_back": 3744,
            "morphology_summary_read_back": 416,
            "scenario_summary_read_back": 936,
            "pooled_summary_read_back": 104,
            "finite_dft_identity_read_back": 144,
            "basis_metadata_rows": 144,
            "unique_case_keys": 22464,
        },
        "fixed_protocol": {
            "morphologies": [
                {
                    "neuromorpho_id": morph_id,
                    "name": morph_name,
                    "expected_swc_sha256": "a" * 64,
                }
                for morph_id, morph_name in morphologies
            ],
            "passive_scenario_count": 9,
            "passive_scenarios": scenarios,
            "basis_order": 224,
            "output_rows": 13,
            "input_expansion_shifts_hz": [0, 100, 1000, 3000, 6000, 10000],
            "sources": ["soma", "basal_q75", "apical_q75"],
            "pulse_widths_ms": [2, 10],
            "dt_ms": 0.00625,
            "windows_ms": [20, 40],
        },
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
        "runtime": {"wall_seconds": 10.0, "worker_processes": 36},
    }
    report_path_json = results_dir / f"{RESULT_STEM}_report.json"
    report_path_json.write_text(json.dumps(report), encoding="utf-8")

    archive_paths = [case_path]
    placeholder_suffixes = [
        "group_summary.csv",
        "morphology_summary.csv",
        "scenario_summary.csv",
        "pooled_summary.csv",
        "finite_dft_identity.csv",
    ]
    for suffix in placeholder_suffixes:
        path = results_dir / f"{RESULT_STEM}_{suffix}"
        path.write_text("synthetic fixture\n", encoding="utf-8")
        archive_paths.append(path)
    archive_paths.extend([metadata_path, report_path_json])
    timing_path = results_dir / f"{RESULT_STEM}.time.txt"
    timing_path.write_text("exit_status=0\n", encoding="utf-8")
    archive_paths.append(timing_path)
    assert len(archive_paths) == 9

    manifest = {
        "status": "passed",
        "files": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in archive_paths
        ],
    }
    manifest_path = results_dir / f"{RESULT_STEM}_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    make_report(results_dir, report_path)
    rendered = report_path.read_text(encoding="utf-8")
    assert "## Pooled q25 and spatial held-out readouts" in rendered
    assert "## Held-out results by morphology" in rendered
    assert "## Held-out results by passive parameter scenario" in rendered
    assert "Median D0 NRMSE (%)" in rendered
    assert "NMO_A" in rendered and "NMO_D" in rendered
