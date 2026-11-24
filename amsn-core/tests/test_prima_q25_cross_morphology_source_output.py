"""Tests for cross-morphology q25 source/output residual maps."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import pytest

import analyze_prima_q25_cross_morphology_source_output as analysis


def row(source="soma", output_id=1, ratio=2.0, delta=1.0, pulse=2.0, scenario="nominal"):
    return {
        "morphology": "fixture",
        "layout_id": "nine_both_q25",
        "basis_order": 168,
        "source_name": source,
        "port_swc_id": output_id,
        "port_roles": "soma" if output_id == 1 else "basal_q75",
        "parameter_scenario": scenario,
        "pulse_width_ms": pulse,
        "candidate_over_seven_error_ratio": ratio,
        "candidate_minus_seven_pct_points": delta,
        "seven_port_nrmse_pct": 1e-6,
        "candidate_nrmse_pct": ratio * 1e-6,
    }


def test_expected_cross_morphology_coverage():
    assert analysis.expected_counts() == {
        "matched_rows_per_morphology": 2268,
        "output_groups_per_morphology": 126,
        "source_groups_per_morphology": 18,
        "matched_rows_total": 4536,
        "output_groups_total": 252,
    }


def test_output_group_summary_counts_sign_and_percentiles():
    rows = [
        row(ratio=1.0, delta=0.0, pulse=2.0),
        row(ratio=2.0, delta=1.0, pulse=10.0),
    ]
    summary = analysis.summarize_output_groups(rows, enforce_complete=False)
    assert len(summary) == 1
    assert summary[0]["matched_pairs"] == 2
    assert summary[0]["worse_pairs"] == 1
    assert summary[0]["better_pairs"] == 0
    assert summary[0]["tie_pairs"] == 1
    assert summary[0]["median_candidate_over_seven_ratio"] == 1.5


def test_source_summary_aggregates_seven_outputs():
    rows = []
    for output_id in range(1, 8):
        rows.extend([
            row(output_id=output_id, ratio=1.0, delta=0.0, pulse=2.0),
            row(output_id=output_id, ratio=2.0, delta=1.0, pulse=10.0),
        ])
    output = analysis.summarize_output_groups(rows, enforce_complete=False)
    summary = analysis.summarize_source_groups(output, enforce_complete=False)
    assert len(summary) == 1
    assert summary[0]["output_ports"] == 7
    assert summary[0]["matched_pairs"] == 14
    assert summary[0]["worse_pairs"] == 7


def test_duplicate_pair_identity_is_rejected():
    item = row()
    with pytest.raises(ValueError, match="duplicate"):
        analysis.validate_unique_pair_identities([item, dict(item)])


def test_incomplete_source_summary_is_rejected_by_production_guard():
    rows = [row(ratio=1.0, delta=0.0, pulse=2.0)]
    output = analysis.summarize_output_groups(rows, enforce_complete=False)
    with pytest.raises(ValueError, match="source-group coverage mismatch"):
        analysis.summarize_source_groups(output)
