"""Contracts for q25 role-specific seeds and held-out spatial readouts."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AMSN_CORE = ROOT / "amsn-core"
AMSN_RESEARCH = AMSN_CORE / "research"
for item in (ROOT / "research", AMSN_CORE, AMSN_RESEARCH):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from amsn.morphology import SWCMorphology

from run_prima_q25_role_specific_spatial_heldout import (
    HELDOUT_SPATIAL_SITES,
    IDENTITY_SCHEDULES,
    RESULT_STEM,
    ROLE_SPECIFIC_SCHEDULES,
    build_four_layouts_from_swc,
    build_heldout_spatial_outputs,
    seed_indices_for_role,
    validate_heldout_spatial_node_ids,
)


def test_role_specific_schedules_keep_the_original_seven_input_selector():
    assert ROLE_SPECIFIC_SCHEDULES == {
        "D0_none": ("none", ()),
        "BASAL_10K": ("basal", (10000.0,)),
        "APICAL_10K": ("apical", (10000.0,)),
        "BOTH_10K": ("both", (10000.0,)),
    }
    assert IDENTITY_SCHEDULES == ("D0_none", "BASAL_10K", "APICAL_10K", "BOTH_10K")


def test_preregistered_heldout_sites_are_not_used_as_q25_dual_seeds():
    assert HELDOUT_SPATIAL_SITES == (
        ("basal_q10", 3, 0.10),
        ("basal_q95", 3, 0.95),
        ("apical_q10", 4, 0.10),
        ("apical_q95", 4, 0.95),
    )
    q25 = {"basal_q25": 250, "apical_q25": 14}
    assert seed_indices_for_role(q25, "basal") == (250,)
    assert seed_indices_for_role(q25, "apical") == (14,)
    assert seed_indices_for_role(q25, "both") == (250, 14)


def test_heldout_sites_must_be_distinct_from_each_other_and_all_fitted_locations():
    shared = [1, 2, 3, 4, 5, 6, 7]
    q25 = {"basal_q25": 20, "apical_q25": 21}
    valid = {
        "basal_q10": 30,
        "basal_q95": 31,
        "apical_q10": 32,
        "apical_q95": 33,
    }
    validate_heldout_spatial_node_ids(shared, q25, valid)
    with pytest.raises(ValueError, match="collide"):
        validate_heldout_spatial_node_ids(shared, q25, {**valid, "basal_q10": 20})
    with pytest.raises(ValueError, match="unique"):
        validate_heldout_spatial_node_ids(shared, q25, {**valid, "basal_q10": 31})
    with pytest.raises(ValueError, match="labels"):
        validate_heldout_spatial_node_ids(shared, q25, {"basal_q10": 30})


def test_exact_worker_and_global_coverage_for_thirteen_output_rows():
    morphologies, scenarios = 4, 9
    schedules = len(ROLE_SPECIFIC_SCHEDULES)
    outputs = 7 + 2 + len(HELDOUT_SPATIAL_SITES)
    workers = morphologies * scenarios
    cases_per_worker = schedules * 2 * 6 * outputs
    summaries_per_worker = schedules * 2 * outputs
    assert outputs == 13
    assert cases_per_worker == 624
    assert summaries_per_worker == 104
    assert workers == 36
    assert workers * cases_per_worker == 22464
    assert workers * summaries_per_worker == 3744
    assert morphologies * 2 * schedules * outputs == 416
    assert scenarios * 2 * schedules * outputs == 936
    assert 2 * schedules * outputs == 104
    assert RESULT_STEM.endswith("2026-11-26")



def test_swc_only_layout_matches_preregistered_seven_port_and_spatial_holdouts():
    rows = ["1 1 0 0 0 5 -1"]
    previous = 1
    for index in range(1, 12):
        node_id = index + 1
        rows.append(f"{node_id} 3 {index * 10} 0 0 1 {previous}")
        previous = node_id
    previous = 1
    for index in range(1, 12):
        node_id = index + 12
        rows.append(f"{node_id} 4 0 {index * 10} 0 1 {previous}")
        previous = node_id

    morphology = SWCMorphology.from_text("\n".join(rows))
    tree = morphology.to_cable_tree()
    layouts, shared_node_ids, q25_node_ids = build_four_layouts_from_swc(
        morphology, tree
    )
    assert set(layouts) == {"seven"}
    seven = layouts["seven"]
    assert len(shared_node_ids) == len(set(shared_node_ids)) == 7
    assert len(seven["ports"]) == len(set(seven["ports"])) == 7
    assert set(seven["source_indices"]) == {"soma", "basal_q75", "apical_q75"}
    assert set(q25_node_ids) == {"basal_q25", "apical_q25"}

    heldout = build_heldout_spatial_outputs(
        morphology, tree, shared_node_ids, q25_node_ids
    )
    assert [item["output_label"] for item in heldout] == [
        "basal_q10", "basal_q95", "apical_q10", "apical_q95"
    ]
    heldout_ids = {item["swc_node_id"] for item in heldout}
    assert len(heldout_ids) == 4
    assert not heldout_ids.intersection(shared_node_ids)
    assert not heldout_ids.intersection(q25_node_ids.values())
