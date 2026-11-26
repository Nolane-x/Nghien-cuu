"""Unit tests for paired-case spatial held-out result reporting."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.analyze_prima_q25_spatial_heldout_results import (
    HELDOUT_LABELS,
    Q25_LABELS,
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
        (0.5, -0.2),
        (1.2, 0.1),
        (0.8, -0.05),
        (1.0, 0.0),
    ])
    assert result["matched"] == 4
    assert result["median_ratio"] == pytest.approx(0.9)
    assert result["median_delta_pp"] == pytest.approx(-0.025)
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
