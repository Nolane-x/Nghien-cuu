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


def test_neuromorpho_morphometry_reproduces_recorded_values():
    metrics = distal_cylinder_morphometrics(SWCMorphology.from_file(DATA))
    assert metrics.neurite_length_um == pytest.approx(12611.0, abs=0.03)
    assert metrics.neurite_surface_area_um2 == pytest.approx(22768.8, abs=0.1)
    assert metrics.neurite_volume_um3 == pytest.approx(4826.47, abs=0.01)
    assert metrics.soma_surface_area_um2 == pytest.approx(921.346, abs=0.001)
    assert metrics.bifurcation_count == 58
    assert metrics.stem_count == 8


def test_real_morphology_summary_avoids_soma_double_count():
    summary = SWCMorphology.from_file(DATA).summary()
    assert summary.branch_point_count == 58
    assert summary.total_path_length_um == pytest.approx(12628.101463, abs=1e-5)
    assert summary.estimated_membrane_area_um2 == pytest.approx(26209.054175, abs=1e-4)
