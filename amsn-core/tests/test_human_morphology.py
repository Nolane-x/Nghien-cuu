from pathlib import Path
import math

import pytest

from amsn.morphology import SWCMorphology
from amsn.morphometrics import distal_cylinder_morphometrics


DATA = (
    Path(__file__).parents[1]
    / "data"
    / "human"
    / "1094_Mohan_etal_2015.CNG.swc"
)


def _edge_frustum_area(morphology, child_id):
    child = morphology.nodes[child_id]
    parent = morphology.nodes[child.parent_id]
    length = math.dist(
        (child.x_um, child.y_um, child.z_um),
        (parent.x_um, parent.y_um, parent.z_um),
    )
    return math.pi * (parent.radius_um+child.radius_um) * math.sqrt(
        length**2 + (child.radius_um-parent.radius_um)**2
    )


def test_neuromorpho_human_l23_candidate_is_structurally_intact():
    morphology = SWCMorphology.from_file(DATA)
    type_counts = {}
    for node in morphology.nodes.values():
        type_counts[node.neurite_type] = type_counts.get(node.neurite_type, 0) + 1
    assert len(morphology.nodes) == 8903
    assert type_counts == {1: 3, 3: 4051, 4: 4849}
    assert morphology.root_id == 1
    assert all(node.radius_um > 0 for node in morphology.nodes.values())


def test_multi_point_soma_does_not_receive_a_second_spherical_area():
    morphology = SWCMorphology.from_text("""
    1 1 0 0 0 5 -1
    2 1 0 -5 0 5 1
    3 1 0 5 0 5 1
    4 3 0 0 10 1 1
    """)
    expected = 0.0
    for node in morphology.nodes.values():
        if node.parent_id == -1:
            continue
        parent = morphology.nodes[node.parent_id]
        length = math.dist(
            (node.x_um, node.y_um, node.z_um),
            (parent.x_um, parent.y_um, parent.z_um),
        )
        expected += math.pi * (parent.radius_um + node.radius_um) * math.sqrt(
            length**2 + (node.radius_um-parent.radius_um)**2
        )
    assert morphology.summary().estimated_membrane_area_um2 == pytest.approx(expected)
    with pytest.raises(ValueError, match="multi-point soma"):
        morphology.to_cable_tree(root_soma_area_um2=314.0)
    cable = morphology.to_cable_tree()
    assert cable.area_m2.sum() == pytest.approx(expected * 1e-12, rel=1e-12)


def test_neuromorpho_three_point_soma_and_wire_stems_are_detected_exactly():
    morphology = SWCMorphology.from_file(DATA)
    info = morphology.detect_neuromorpho_three_point_soma()
    assert info is not None
    assert info.root_id == 1
    assert info.soma_node_ids == (1, 2, 3)
    assert info.wire_attachment_node_ids == (
        4, 1035, 1731, 1782, 2645, 3404, 4001, 4055
    )
    assert sum(info.wire_attachment_lengths_um.values()) == pytest.approx(
        72.224194, abs=1e-5
    )
    assert info.root_soma_area_um2 == pytest.approx(921.859209332, abs=1e-8)

    mapping = morphology.electrical_node_mapping()
    assert {mapping[node_id] for node_id in info.soma_node_ids} == {1}
    assert {mapping[node_id] for node_id in info.wire_attachment_node_ids} == {1}
    assert mapping[3784] == 3784


def test_neuromorpho_cable_matches_import3d_soma_surface_and_wire_policy():
    morphology = SWCMorphology.from_file(DATA)
    info = morphology.detect_neuromorpho_three_point_soma()
    assert info is not None
    raw_area = morphology.summary().estimated_membrane_area_um2
    omitted_wire_area = sum(
        _edge_frustum_area(morphology, node_id)
        for node_id in info.wire_attachment_node_ids
    )
    soma_frustum_area = distal_cylinder_morphometrics(morphology).soma_surface_area_um2
    expected_area = (
        raw_area - omitted_wire_area - soma_frustum_area
        + info.root_soma_area_um2
    )

    cable = morphology.to_cable_tree()
    assert cable.n_compartments == len(morphology.nodes) - 10
    assert cable.area_m2.sum() * 1e12 == pytest.approx(expected_area, rel=2e-12)
    for node_id in (2, 3, *info.wire_attachment_node_ids):
        assert f"swc_{node_id}" not in cable.index
    for node_id in (1, 3784, 5920):
        assert f"swc_{node_id}" in cable.index


def test_nonmatching_three_point_soma_is_not_normalized():
    morphology = SWCMorphology.from_text("""
    1 1 0 0 0 5 -1
    2 1 0 -4 0 4 1
    3 1 0 4 0 4 1
    4 3 0 0 10 1 1
    """)
    assert morphology.detect_neuromorpho_three_point_soma() is None
    assert morphology.electrical_node_mapping() == {
        1: 1, 2: 2, 3: 3, 4: 4
    }


def test_neuromorpho_morphometry_reproduces_recorded_values():
    metrics = distal_cylinder_morphometrics(SWCMorphology.from_file(DATA))
    assert metrics.neurite_length_um == pytest.approx(12611.0, abs=0.03)
    assert metrics.neurite_surface_area_um2 == pytest.approx(22768.8, abs=0.1)
    assert metrics.neurite_volume_um3 == pytest.approx(4826.47, abs=0.01)
    assert metrics.soma_surface_area_um2 == pytest.approx(921.346, abs=0.001)
    assert metrics.bifurcation_count == 58
    assert metrics.stem_count == 8


def test_real_morphology_raw_summary_remains_unchanged():
    summary = SWCMorphology.from_file(DATA).summary()
    assert summary.branch_point_count == 58
    assert summary.total_path_length_um == pytest.approx(12628.101463, abs=1e-5)
    assert summary.estimated_membrane_area_um2 == pytest.approx(26209.054175, abs=1e-4)
