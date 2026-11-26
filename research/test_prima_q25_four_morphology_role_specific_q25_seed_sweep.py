"""Contracts for the four-morphology role-specific q25 seed sweep."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMSN_CORE = ROOT / "amsn-core"
AMSN_RESEARCH = AMSN_CORE / "research"
for item in (ROOT / "research", AMSN_CORE, AMSN_RESEARCH):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from run_prima_q25_four_morphology_role_specific_q25_seed_sweep import (
    IDENTITY_SCHEDULES,
    RESULT_STEM,
    ROLE_SPECIFIC_SCHEDULES,
    seed_indices_for_role,
)


def test_four_predeclared_schedules_change_only_the_q25_seed_role():
    assert ROLE_SPECIFIC_SCHEDULES == {
        "D0_none": ("none", ()),
        "BASAL_10K": ("basal", (10000.0,)),
        "APICAL_10K": ("apical", (10000.0,)),
        "BOTH_10K": ("both", (10000.0,)),
    }
    assert IDENTITY_SCHEDULES == (
        "D0_none", "BASAL_10K", "APICAL_10K", "BOTH_10K"
    )


def test_role_mapping_selects_only_the_declared_q25_observation_rows():
    outputs = {"basal_q25": 250, "apical_q25": 14}
    assert seed_indices_for_role(outputs, "basal") == (250,)
    assert seed_indices_for_role(outputs, "apical") == (14,)
    assert seed_indices_for_role(outputs, "both") == (250, 14)
    # D0 keeps both rows observable but contributes no dual frequencies.
    assert seed_indices_for_role(outputs, "none") == (250, 14)


def test_schedule_budget_and_expected_global_coverage_are_fixed():
    morphology_count = 4
    scenario_count = 9
    schedules = len(ROLE_SPECIFIC_SCHEDULES)
    case_rows_per_worker = schedules * 2 * 6 * 9
    summary_rows_per_worker = schedules * 2 * 9
    workers = morphology_count * scenario_count

    assert case_rows_per_worker == 432
    assert summary_rows_per_worker == 72
    assert workers == 36
    assert workers * case_rows_per_worker == 15552
    assert workers * summary_rows_per_worker == 2592
    assert morphology_count * 2 * schedules * 9 == 288
    assert scenario_count * 2 * schedules * 9 == 648
    assert 2 * schedules * 9 == 72
    assert workers * schedules == 144
    assert RESULT_STEM.endswith("2026-11-26")
