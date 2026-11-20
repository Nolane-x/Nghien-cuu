import math
import pytest

from amsn.discretization import (
    ac_length_constant_um,
    electrotonic_length_um,
    edge_subdivision_fractions,
    refine_swc_morphology,
    to_electrotonic_cable_tree,
)
from amsn.morphology import SWCMorphology


def test_constant_diameter_electrotonic_length_equals_length_over_lambda():
    length = 1000.0
    diameter = 2.0
    lam = ac_length_constant_um(diameter, 100.0, 0.7, 0.01)
    got = electrotonic_length_um(length, diameter, diameter, 100.0, 0.7, 0.01)
    assert got == pytest.approx(length / lam, rel=1e-14)


def test_tapered_electrotonic_integral_matches_closed_form():
    length, d0, d1 = 250.0, 0.5, 4.0
    f, ri, cm = 80.0, 0.8, 0.012
    expected = length * math.sqrt(4 * math.pi * f * ri * cm) / 1000.0
    expected *= 2.0 / (math.sqrt(d0) + math.sqrt(d1))
    assert electrotonic_length_um(length, d0, d1, f, ri, cm) == pytest.approx(expected)


def test_tapered_integral_agrees_with_independent_midpoint_quadrature():
    length, d0, d1 = 400.0, 0.3, 5.0
    frequency, ri, cm = 100.0, 0.7, 0.01
    steps = 100_000
    dx = length / steps
    numerical = 0.0
    for i in range(steps):
        x_mid = (i + 0.5) / steps
        diameter = d0 + (d1 - d0) * x_mid
        numerical += dx / ac_length_constant_um(diameter, frequency, ri, cm)
    exact = electrotonic_length_um(length, d0, d1, frequency, ri, cm)
    assert exact == pytest.approx(numerical, rel=2e-9)


def test_union_of_physical_and_electrotonic_cuts_obeys_both_limits():
    length, d0, d1 = 900.0, 3.0, 0.4
    max_length, max_electro = 37.0, 0.08
    cuts = edge_subdivision_fractions(
        length, d0, d1,
        max_segment_length_um=max_length,
        max_electrotonic_length=max_electro,
        reference_frequency_hz=100.0,
        axial_resistivity_ohm_m=0.7,
        specific_capacitance_f_m2=0.01,
    )
    assert cuts[0] == 0.0 and cuts[-1] == 1.0
    assert tuple(sorted(set(cuts))) == cuts
    for a, b in zip(cuts, cuts[1:]):
        seg_len = length * (b - a)
        da = d0 + (d1 - d0) * a
        db = d0 + (d1 - d0) * b
        seg_electro = electrotonic_length_um(seg_len, da, db)
        assert seg_len <= max_length + 1e-10
        assert seg_electro <= max_electro + 1e-12


def test_refinement_preserves_original_nodes_branching_length_and_area():
    morph = SWCMorphology.from_text("""
    1 1 0 0 0 5 -1
    2 3 0 0 400 2 1
    3 3 200 0 700 1 2
    4 3 -200 0 700 1.5 2
    5 3 300 0 950 0.8 3
    """)
    before = morph.summary()
    refined = refine_swc_morphology(
        morph,
        max_segment_length_um=40.0,
        max_electrotonic_length=0.1,
        reference_frequency_hz=100.0,
    )
    after = refined.summary()
    assert len(refined.nodes) > len(morph.nodes)
    assert set(morph.nodes).issubset(refined.nodes)
    assert after.edge_count == after.node_count - 1
    assert after.branch_point_count == before.branch_point_count
    assert after.total_path_length_um == pytest.approx(before.total_path_length_um, rel=1e-12)
    assert after.estimated_membrane_area_um2 == pytest.approx(
        before.estimated_membrane_area_um2, rel=1e-12
    )
    assert morph.summary().node_count == before.node_count  # no in-place mutation

    for node in refined.nodes.values():
        if node.parent_id == -1:
            continue
        parent = refined.nodes[node.parent_id]
        length = math.dist(
            (node.x_um, node.y_um, node.z_um),
            (parent.x_um, parent.y_um, parent.z_um),
        )
        assert length <= 40.0 + 1e-10
        elen = electrotonic_length_um(length, 2 * parent.radius_um, 2 * node.radius_um)
        assert elen <= 0.1 + 1e-12


def test_refinement_rejects_invalid_parameters():
    morph = SWCMorphology.from_text("1 1 0 0 0 1 -1\n2 3 0 0 10 1 1")
    with pytest.raises(ValueError):
        refine_swc_morphology(morph, max_electrotonic_length=0.0)
    with pytest.raises(ValueError):
        edge_subdivision_fractions(10, 1, 1, max_segment_length_um=-1)


def test_refined_morphology_can_be_converted_to_passive_cable_tree():
    morph = SWCMorphology.from_text("1 1 0 0 0 2 -1\n2 3 0 0 200 1 1")
    tree = to_electrotonic_cable_tree(
        morph, max_segment_length_um=25.0, max_electrotonic_length=0.1
    )
    assert tree.n_compartments > 2

def test_tighter_electrotonic_limit_never_reduces_node_count():
    morph = SWCMorphology.from_text("""
    1 1 0 0 0 6 -1
    2 3 0 0 300 1.5 1
    3 3 100 0 600 0.5 2
    """)
    n_coarse = len(refine_swc_morphology(morph, max_electrotonic_length=0.2).nodes)
    n_medium = len(refine_swc_morphology(morph, max_electrotonic_length=0.1).nodes)
    n_fine = len(refine_swc_morphology(morph, max_electrotonic_length=0.05).nodes)
    assert n_coarse <= n_medium <= n_fine
