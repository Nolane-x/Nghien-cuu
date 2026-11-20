import numpy as np
import pytest

from amsn.cable import CableCompartment, CableTree


def _tree():
    return CableTree([
        CableCompartment("soma", 20e-6, 20e-6, None),
        CableCompartment("dend_a", 100e-6, 2e-6, "soma"),
        CableCompartment("dend_b", 100e-6, 1.5e-6, "soma"),
        CableCompartment("branch", 80e-6, 1.0e-6, "dend_a"),
    ])


def test_passive_dc_hines_solution_matches_independent_dense_system():
    tree = _tree()
    current = np.array([0.2e-12, 10e-12, -1.5e-12, 0.7e-12])
    got = tree.solve_passive_steady_state(current)

    matrix = np.diag(tree.membrane_leak_s.copy())
    rhs = tree.membrane_leak_s * tree.parameters.e_leak_v + current
    for i in range(1, tree.n_compartments):
        parent = tree.parent_index[i]
        conductance = tree.axial_g_s[i]
        matrix[i, i] += conductance
        matrix[parent, parent] += conductance
        matrix[i, parent] -= conductance
        matrix[parent, i] -= conductance
    expected = np.linalg.solve(matrix, rhs)
    np.testing.assert_allclose(got, expected, rtol=2e-12, atol=2e-13)


def test_passive_dc_without_injection_is_uniform_at_leak_reversal():
    tree = _tree()
    got = tree.solve_passive_steady_state()
    np.testing.assert_allclose(
        got, np.full(tree.n_compartments, tree.parameters.e_leak_v),
        rtol=0.0, atol=1e-14,
    )


@pytest.mark.parametrize("current", [
    np.zeros(3),
    np.array([0.0, 0.0, float("nan"), 0.0]),
    np.array([0.0, 0.0, float("inf"), 0.0]),
])
def test_passive_dc_rejects_invalid_injected_current(current):
    with pytest.raises(ValueError):
        _tree().solve_passive_steady_state(current)
