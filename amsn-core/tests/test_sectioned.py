from collections import Counter
from math import hypot, pi

import pytest

from amsn.morphology import SWCMorphology
from amsn.sectioned import _section_paths, to_sectioned_cable_tree


SYNTHETIC = """
1 1 0 0 0 5 -1
2 1 0 -5 0 5 1
3 1 0 5 0 5 1
4 3 10 0 0 1.0 1
5 3 20 0 0 0.8 4
6 3 20 10 0 0.7 5
7 3 30 10 0 0.5 6
8 3 20 -10 0 0.7 5
9 3 30 -10 0 0.5 8
10 4 0 0 20 0.9 1
11 4 0 0 40 0.6 10
12 4 0 10 50 0.4 11
"""


def _original_edge_axial_sum(morphology):
    value = 0.0
    for node in morphology.nodes.values():
        if node.parent_id == -1:
            continue
        parent = morphology.nodes[node.parent_id]
        length_um = hypot(
            hypot(node.x_um-parent.x_um, node.y_um-parent.y_um),
            node.z_um-parent.z_um,
        )
        value += length_um * 1e-6 / (
            pi * (parent.radius_um*1e-6) * (node.radius_um*1e-6)
        )
    return value


def test_section_decomposition_covers_each_original_edge_exactly_once():
    morphology = SWCMorphology.from_text(SYNTHETIC)
    sections = _section_paths(morphology, {6, 11})
    counts = Counter(
        (parent, child)
        for path in sections
        for parent, child in zip(path, path[1:])
    )
    expected = {
        (node.parent_id, node.node_id)
        for node in morphology.nodes.values()
        if node.parent_id != -1
    }
    assert set(counts) == expected
    assert set(counts.values()) == {1}


def test_sectioned_mesh_preserves_arc_length_area_and_axial_integral():
    morphology = SWCMorphology.from_text(SYNTHETIC)
    result = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=100.0,
        max_electrotonic_length=0.1,
        preserve_node_ids={4, 6, 10},
        normalize_neuromorpho_soma=False,
    )
    assert result.tree.n_compartments < len(morphology.nodes)
    assert set(result.swc_node_to_compartment) == set(morphology.nodes)
    assert result.swc_node_to_compartment[6] == "swc_6"
    assert result.swc_node_mapping_error_um[6] == pytest.approx(0.0)
    assert sum(result.edge_arc_length_m.values()) * 1e6 == pytest.approx(
        morphology.summary().total_path_length_um, rel=1e-12
    )
    assert result.tree.area_m2.sum() * 1e12 == pytest.approx(
        morphology.summary().estimated_membrane_area_um2, rel=1e-12
    )
    assert sum(result.edge_axial_geometry_factor_m_inv.values()) == pytest.approx(
        _original_edge_axial_sum(morphology), rel=1e-12
    )
    assert max(result.edge_arc_length_m.values()) * 1e6 <= 100.0 + 1e-8
    assert max(result.edge_electrotonic_length.values()) <= 0.1 + 1e-12


def test_preserved_nodes_and_structural_boundaries_are_exact_control_points():
    morphology = SWCMorphology.from_text(SYNTHETIC)
    result = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=100.0,
        max_electrotonic_length=10.0,
        preserve_node_ids={6, 11},
        normalize_neuromorpho_soma=False,
    )
    for node_id in (1, 2, 3, 5, 6, 7, 9, 10, 11, 12):
        # Branch points, terminals, transitions and protected nodes survive.
        assert result.swc_node_to_compartment[node_id] == f"swc_{node_id}"
        assert result.swc_node_mapping_error_um[node_id] == pytest.approx(0.0)
    assert result.swc_node_mapping_error_um[6] == 0.0


def test_sectioned_converter_rejects_unknown_preserved_node():
    morphology = SWCMorphology.from_text(SYNTHETIC)
    with pytest.raises(ValueError, match="unknown SWC IDs"):
        to_sectioned_cable_tree(morphology, preserve_node_ids={999})


def test_real_human_l23_morphology_reduces_electrical_compartments():
    from pathlib import Path

    data = (
        Path(__file__).parents[1]
        / "data"
        / "human"
        / "1094_Mohan_etal_2015.CNG.swc"
    )
    morphology = SWCMorphology.from_file(data)
    protected = {1, 3355, 3814, 3784, 6897, 5164, 5920}
    result = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=50.0,
        max_electrotonic_length=0.1,
        preserve_node_ids=protected,
    )
    assert result.tree.n_compartments < 2000
    assert result.tree.n_compartments < len(morphology.nodes)
    assert set(result.swc_node_to_compartment) == set(morphology.nodes)
    for node_id in protected:
        assert result.swc_node_to_compartment[node_id] == f"swc_{node_id}"
        assert result.swc_node_mapping_error_um[node_id] == 0.0
    info = morphology.detect_neuromorpho_three_point_soma()
    assert info is not None
    excluded_children = set(info.soma_node_ids[1:]) | set(info.wire_attachment_node_ids)
    retained_length_um = 0.0
    retained_area_um2 = info.root_soma_area_um2
    retained_axial_m_inv = 0.0
    for node in morphology.nodes.values():
        if node.parent_id == -1 or node.node_id in excluded_children:
            continue
        parent = morphology.nodes[node.parent_id]
        length_um = hypot(
            hypot(node.x_um-parent.x_um, node.y_um-parent.y_um),
            node.z_um-parent.z_um,
        )
        retained_length_um += length_um
        retained_area_um2 += pi*(parent.radius_um+node.radius_um)*(
            length_um**2+(node.radius_um-parent.radius_um)**2
        )**0.5
        retained_axial_m_inv += length_um*1e-6/(
            pi*(parent.radius_um*1e-6)*(node.radius_um*1e-6)
        )

    assert sum(result.edge_arc_length_m.values()) * 1e6 == pytest.approx(
        retained_length_um, rel=2e-12
    )
    assert result.tree.area_m2.sum() * 1e12 == pytest.approx(
        retained_area_um2, rel=2e-12
    )
    assert sum(result.edge_axial_geometry_factor_m_inv.values()) == pytest.approx(
        retained_axial_m_inv, rel=2e-12
    )
    for node_id in (*info.soma_node_ids, *info.wire_attachment_node_ids):
        assert result.swc_node_to_compartment[node_id] == "swc_1"
