"""Four-layout q25 replication checks for NMO_107159 Tamas human pyramidal Control."""
from __future__ import annotations

import sys
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import replay_nmo107159_four_layout_replication as ablation


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
    common = [1, 6363, 4735, 5564, 7023, 4301, 4623]
    basal = 6609
    apical = 4404
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
    common = [1, 6363, 4735, 5564, 7023, 4301, 4623]
    layouts = {
        "seven": common,
        "eight_basal_q25": common + [6609],
        "eight_apical_q25": common + [4404],
        "nine_both_q25": common + [6609, 4404],
    }
    layouts["eight_basal_q25"] = common + [4404]
    try:
        ablation.validate_layout_node_sets(
            common,
            layouts,
            {"basal_q25": 6609, "apical_q25": 4404},
        )
    except ValueError as exc:
        assert "eight_basal_q25" in str(exc)
    else:
        raise AssertionError("cross-contaminated q25 layout must fail closed")


def test_pairwise_coverage_formula_matches_factorial_design():
    assert 3 * 9 * 2 * 3 * 2 * 7 == ablation.EXPECTED_MATCHED_ROWS


def test_q25_observation_formula_counts_single_and_dual_layouts():
    assert 9 * 2 * 3 * 2 * (1 + 1 + 2) == ablation.EXPECTED_Q25_ROWS


def test_tamas_source_identity_is_reused():
    assert ablation.EXPECTED_SWC_RECORDS == 7228
    assert ablation.EXPECTED_SWC_SHA256 == (
        "6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023"
    )
