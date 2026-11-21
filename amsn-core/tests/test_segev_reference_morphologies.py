from pathlib import Path

import pytest

from amsn.morphology import SWCMorphology


DATA_DIR = Path(__file__).parents[1] / "data" / "human" / "segev"
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
