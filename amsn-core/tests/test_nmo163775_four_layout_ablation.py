"""Tests for the isolated q25 single-port and dual-port ablation."""
from __future__ import annotations

import sys
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import replay_nmo163775_four_layout_ablation as ablation


def test_expected_four_layout_matrix_is_exact():
    assert ablation.expected_counts() == {
        "models": 72,
        "frequency": 648,
        "transient": 3456,
        "matched_shared_vs_seven": 2268,
        "q25_only": 432,
        "hines_shared": 1134,
    }


def test_layout_node_sets_separate_single_and_double_q25_additions():
    common = [1, 40, 144, 3926, 3948, 4104, 4180]
    basal = 224
    apical = 4096
    layouts = {
        "seven": common,
        "eight_basal_q25": common + [basal],
        "eight_apical_q25": common + [apical],
        "nine_both_q25": common + [basal, apical],
    }
    ablation.validate_layout_node_sets(
        common,
        layouts,
        {"basal_q25": basal, "apical_q25": apical},
    )


def test_layout_validation_rejects_q25_probe_leakage():
    common = [1, 40, 144, 3926, 3948, 4104, 4180]
    layouts = {
        "seven": common,
        "eight_basal_q25": common + [224],
        "eight_apical_q25": common + [4096],
        "nine_both_q25": common + [224, 4096],
    }
    layouts["eight_basal_q25"] = common + [4096]
    try:
        ablation.validate_layout_node_sets(
            common,
            layouts,
            {"basal_q25": 224, "apical_q25": 4096},
        )
    except ValueError as exc:
        assert "eight_basal_q25" in str(exc)
    else:
        raise AssertionError("cross-contaminated q25 layout must fail closed")


def test_pairwise_coverage_formula_matches_factorial_design():
    expected = (
        3 * 9 * 2 * 3 * 2 * 7
    )
    assert expected == ablation.EXPECTED_MATCHED_ROWS


def test_q25_observation_formula_counts_single_and_dual_layouts():
    expected = 9 * 2 * 3 * 2 * (1 + 1 + 2)
    assert expected == ablation.EXPECTED_Q25_ROWS


def test_pinned_source_identity_is_reused():
    assert ablation.EXPECTED_SWC_RECORDS == 4209
    assert ablation.EXPECTED_SWC_SHA256 == "94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f"
