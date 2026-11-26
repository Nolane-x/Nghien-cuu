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


def test_percentile_is_interpolated_and_handles_single_values():
    assert percentile([0.0, 10.0], 0.90) == pytest.approx(9.0)
    assert percentile([2.0], 0.90) == pytest.approx(2.0)
