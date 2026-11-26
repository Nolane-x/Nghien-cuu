"""Regression tests for q25-versus-edge multilocation PRIMA seed schedules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMSN_CORE = ROOT / "amsn-core"
for item in (ROOT / "research", AMSN_CORE, AMSN_CORE / "research"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from amsn.morphology import SWCMorphology
from run_prima_q25_multilocation_seed_sweep import (
    IDENTITY_SCHEDULES,
    MULTILOCATION_SCHEDULES,
    build_four_layouts_from_swc,
    build_heldout_spatial_outputs,
    seed_indices_for_multilocation_strategy,
    validate_heldout_spatial_node_ids,
)


def _edge_sites():
    return [
        {"output_label": "basal_q10", "tree_index": 30, "swc_node_id": 30},
        {"output_label": "basal_q95", "tree_index": 31, "swc_node_id": 31},
        {"output_label": "apical_q10", "tree_index": 32, "swc_node_id": 32},
        {"output_label": "apical_q95", "tree_index": 33, "swc_node_id": 33},
    ]


def test_multilocation_schedule_matrix_is_locked_and_uses_one_dual_shift():
    assert MULTILOCATION_SCHEDULES == {
        "D0_none": ("none", ()),
        "Q25_BOTH_10K": ("q25_both", (10000.0,)),
        "BASAL_EDGES_10K": ("basal_edges", (10000.0,)),
        "APICAL_EDGES_10K": ("apical_edges", (10000.0,)),
        "BOTH_EDGES_10K": ("both_edges", (10000.0,)),
    }
    assert IDENTITY_SCHEDULES == tuple(MULTILOCATION_SCHEDULES)


def test_seed_strategy_resolves_the_exact_q25_and_edge_coordinates():
    q25 = {"basal_q25": 20, "apical_q25": 21}
    edges = _edge_sites()
    retained = (1, 2, 3, 4, 5, 6, 7)

    indices, labels = seed_indices_for_multilocation_strategy(
        q25, edges, "none", retained
    )
    assert indices == (20, 21)
    assert labels == ()

    indices, labels = seed_indices_for_multilocation_strategy(
        q25, edges, "q25_both", retained
    )
    assert indices == (20, 21)
    assert labels == ("basal_q25", "apical_q25")

    indices, labels = seed_indices_for_multilocation_strategy(
        q25, edges, "basal_edges", retained
    )
    assert indices == (30, 31)
    assert labels == ("basal_q10", "basal_q95")

    indices, labels = seed_indices_for_multilocation_strategy(
        q25, edges, "apical_edges", retained
    )
    assert indices == (32, 33)
    assert labels == ("apical_q10", "apical_q95")

    indices, labels = seed_indices_for_multilocation_strategy(
        q25, edges, "both_edges", retained
    )
    assert indices == (30, 31, 32, 33)
    assert labels == ("basal_q10", "basal_q95", "apical_q10", "apical_q95")


def test_seed_strategy_fails_closed_for_collisions_missing_labels_and_unknown_roles():
    q25 = {"basal_q25": 20, "apical_q25": 21}
    retained = (1, 2, 3, 4, 5, 6, 7)
    edges = _edge_sites()

    colliding = [dict(item) for item in edges]
    colliding[0]["tree_index"] = 1
    try:
        seed_indices_for_multilocation_strategy(q25, colliding, "basal_edges", retained)
    except ValueError as exc:
        assert "collide" in str(exc)
    else:
        raise AssertionError("retained-port collision was accepted")

    duplicate = [dict(item) for item in edges]
    duplicate[1]["tree_index"] = duplicate[0]["tree_index"]
    try:
        seed_indices_for_multilocation_strategy(q25, duplicate, "both_edges", retained)
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate seed coordinate was accepted")

    missing = edges[:-1]
    try:
        seed_indices_for_multilocation_strategy(q25, missing, "both_edges", retained)
    except ValueError as exc:
        assert "edge site labels" in str(exc)
    else:
        raise AssertionError("missing edge label was accepted")

    try:
        seed_indices_for_multilocation_strategy(q25, edges, "posthoc_best", retained)
    except ValueError as exc:
        assert "unknown multilocation" in str(exc)
    else:
        raise AssertionError("unregistered seed schedule was accepted")


def test_node_map_requires_seven_shared_two_q25_and_four_unique_edge_nodes():
    shared = [1, 2, 3, 4, 5, 6, 7]
    q25 = {"basal_q25": 20, "apical_q25": 21}
    edges = {item["output_label"]: item["swc_node_id"] for item in _edge_sites()}
    validate_heldout_spatial_node_ids(shared, q25, edges)


def test_synthetic_swc_mapper_keeps_the_seven_inputs_and_separate_q25_edge_rows():
    rows = ["1 1 0 0 0 5 -1"]
    parent = 1
    for index in range(1, 12):
        node_id = index + 1
        rows.append(f"{node_id} 3 {index * 10} 0 0 1 {parent}")
        parent = node_id
    parent = 1
    for index in range(1, 12):
        node_id = index + 12
        rows.append(f"{node_id} 4 0 {index * 10} 0 1 {parent}")
        parent = node_id

    morphology = SWCMorphology.from_text("\n".join(rows))
    tree = morphology.to_cable_tree()
    _layouts, shared, q25 = build_four_layouts_from_swc(morphology, tree)
    edges = build_heldout_spatial_outputs(morphology, tree, shared, q25)
    edge_ids = {item["swc_node_id"] for item in edges}
    assert len(shared) == 7
    assert len(q25) == 2
    assert len(edges) == 4
    assert len(edge_ids) == 4
    assert not set(shared).intersection(q25.values())
    assert not set(shared).intersection(edge_ids)
    assert not set(q25.values()).intersection(edge_ids)


def test_multilocation_case_and_metadata_coverage_is_exact():
    morphologies = 4
    scenarios = 9
    schedules = len(MULTILOCATION_SCHEDULES)
    outputs = 7 + 2 + 4
    workers = morphologies * scenarios
    cases_per_worker = schedules * 2 * 6 * outputs
    summaries_per_worker = schedules * 2 * outputs

    assert schedules == 5
    assert outputs == 13
    assert workers == 36
    assert cases_per_worker == 780
    assert summaries_per_worker == 130
    assert workers * cases_per_worker == 28080
    assert workers * summaries_per_worker == 4680
    assert morphologies * 2 * schedules * outputs == 520
    assert scenarios * 2 * schedules * outputs == 1170
    assert 2 * schedules * outputs == 130
    assert workers * schedules == 180
