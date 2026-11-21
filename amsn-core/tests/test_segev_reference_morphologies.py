from pathlib import Path
from math import dist, pi, sqrt

import pytest

from amsn.morphology import SWCMorphology


DATA_DIR = Path(__file__).parents[1] / "data" / "human" / "segev"

def _edge_frustum_area(morphology, child_id):
    child = morphology.nodes[child_id]
    parent = morphology.nodes[child.parent_id]
    length = dist(
        (child.x_um, child.y_um, child.z_um),
        (parent.x_um, parent.y_um, parent.z_um),
    )
    return pi * (parent.radius_um + child.radius_um) * sqrt(
        length * length + (child.radius_um - parent.radius_um) ** 2
    )

FIXTURES = [
    ("2013_03_06_cell11_1125_H41_06.CNG.swc", 12410, {1: 3, 2: 116, 3: 5595, 4: 6696}),
    ("2013_03_13_cell03_1204_H42_02.CNG.swc", 13758, {1: 3, 2: 379, 3: 5847, 4: 7529}),
]


@pytest.mark.parametrize(("filename", "expected_nodes", "expected_types"), FIXTURES)
def test_segev_morphology_is_structurally_valid(filename, expected_nodes, expected_types):
    morphology = SWCMorphology.from_file(DATA_DIR / filename)
    counts = {}
    for node in morphology.nodes.values():
        counts[node.neurite_type] = counts.get(node.neurite_type, 0) + 1
    assert len(morphology.nodes) == expected_nodes
    assert counts == expected_types
    assert morphology.root_id == 1
    assert all(node.radius_um > 0 for node in morphology.nodes.values())


@pytest.mark.parametrize(("filename", "expected_nodes", "expected_types"), FIXTURES)
def test_segev_soma_normalization_and_cable_conversion(filename, expected_nodes, expected_types):
    morphology = SWCMorphology.from_file(DATA_DIR / filename)
    soma = morphology.detect_neuromorpho_three_point_soma()
    assert soma is not None
    assert soma.root_id == 1
    assert soma.soma_node_ids == (1, 2, 3)
    assert len(soma.wire_attachment_node_ids) >= 1
    cable = morphology.to_cable_tree()
    expected = expected_nodes - 2 - len(soma.wire_attachment_node_ids)
    assert cable.n_compartments == expected
    assert cable.area_m2.size == expected
    assert all(cable.area_m2 > 0)


def test_segev_three_point_soma_collapses_all_first_order_neurite_attachments():
    morphology = SWCMorphology.from_file(
        DATA_DIR / "2013_03_13_cell03_1204_H42_02.CNG.swc"
    )
    soma = morphology.detect_neuromorpho_three_point_soma()
    assert soma is not None
    # The axon branches immediately at node 5851, but Import3D still attaches
    # the axon at the soma without retaining this soma-centre SWC edge.
    assert morphology.nodes[5851].parent_id == morphology.root_id
    assert morphology.nodes[5851].neurite_type == 2
    assert len(morphology.children[5851]) == 2
    assert soma.wire_attachment_node_ids == (
        4, 904, 1899, 2236, 3302, 4636, 5282, 5851, 6230
    )
    assert morphology.electrical_node_mapping()[5851] == morphology.root_id

    cable = morphology.to_cable_tree()
    assert f"swc_{5851}" not in cable.index
    assert cable.n_compartments == len(morphology.nodes) - 2 - 9


def test_segev_cell1204_normalized_area_matches_import3d_geometry_ledger():
    morphology = SWCMorphology.from_file(
        DATA_DIR / "2013_03_13_cell03_1204_H42_02.CNG.swc"
    )
    info = morphology.detect_neuromorpho_three_point_soma()
    assert info is not None
    raw_area = morphology.summary().estimated_membrane_area_um2
    omitted_wire_area = sum(
        _edge_frustum_area(morphology, node_id)
        for node_id in info.wire_attachment_node_ids
    )
    soma_frustum_area = sum(
        _edge_frustum_area(morphology, node_id)
        for node_id in info.soma_node_ids[1:]
    )
    expected_area = (
        raw_area - omitted_wire_area - soma_frustum_area
        + info.root_soma_area_um2
    )
    cable = morphology.to_cable_tree()
    assert cable.area_m2.sum() * 1e12 == pytest.approx(
        expected_area, rel=2e-12
    )
    assert cable.area_m2.sum() * 1e12 == pytest.approx(
        83861.873829, abs=1e-3
    )
