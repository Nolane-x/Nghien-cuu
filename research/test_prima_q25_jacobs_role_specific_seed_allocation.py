"""Focused contracts for role-isolated q25 output-dual basis seeding."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AMSN_CORE = REPO_ROOT / "amsn-core"
AMSN_RESEARCH = AMSN_CORE / "research"
for item in (AMSN_CORE, AMSN_RESEARCH):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import numpy as np

from amsn.cable import CableCompartment, CableTree, PassiveParameters
from amsn.prima import prima_reduce_passive_cable_multishift
from experimental_prima_output_aware_basis import build_output_aware_passive_basis


def _branched_tree() -> CableTree:
    return CableTree(
        [
            CableCompartment("soma", 20e-6, 20e-6),
            CableCompartment("basal_a", 100e-6, 2.0e-6, "soma"),
            CableCompartment("basal_b", 85e-6, 1.5e-6, "basal_a"),
            CableCompartment("basal_distal", 70e-6, 1.1e-6, "basal_b"),
            CableCompartment("apical_a", 140e-6, 1.8e-6, "soma"),
            CableCompartment("apical_b", 120e-6, 1.2e-6, "apical_a"),
            CableCompartment("tuft", 90e-6, 0.9e-6, "apical_b"),
            CableCompartment("tuft_distal", 75e-6, 0.7e-6, "tuft"),
        ],
        PassiveParameters(),
    )


def _dual_vector(tree: CableTree, index: int, frequency_hz: float) -> np.ndarray:
    from amsn.prima import _solve_shifted_passive_real
    selector = np.zeros(tree.n_compartments, dtype=np.float64)
    selector[index] = 1.0
    return _solve_shifted_passive_real(tree, 2.0 * np.pi * frequency_hz, selector)


def _assert_seed_in_span(model, tree: CableTree, index: int, frequency_hz: float) -> None:
    seed = _dual_vector(tree, index, frequency_hz)
    residual = seed - model.basis @ (model.basis.T @ seed)
    assert np.linalg.norm(residual) <= 2e-12 * np.linalg.norm(seed)


def test_apical_only_dual_seed_keeps_input_selector_and_spans_apical_seed():
    tree = _branched_tree()
    retained = (0,)
    result = build_output_aware_passive_basis(
        tree,
        retained,
        (7,),
        max_order=7,
        input_expansion_frequencies_hz=(0.0, 100.0),
        output_seed_frequencies_hz=(1000.0,),
    )
    model = result.model
    assert model.port_indices == retained
    assert model.input_matrix.shape == (model.order, 1)
    np.testing.assert_array_equal(
        model.input_matrix, model.basis[np.asarray(retained), :].T
    )
    assert result.diagnostics.output_indices == (7,)
    assert result.diagnostics.initial_output_seed_columns >= 1
    _assert_seed_in_span(model, tree, 7, 1000.0)
    np.linalg.cholesky(model.conductance_matrix_s)
    np.linalg.cholesky(model.capacitance_matrix_f)
    assert result.diagnostics.basis_orthogonality_max_abs < 2e-12


def test_basal_and_apical_only_schedules_keep_one_input_and_include_their_own_seed():
    tree = _branched_tree()
    retained = (0,)
    common = {
        "max_order": 7,
        "input_expansion_frequencies_hz": (0.0, 100.0),
        "output_seed_frequencies_hz": (10000.0,),
    }
    basal = build_output_aware_passive_basis(tree, retained, (3,), **common)
    apical = build_output_aware_passive_basis(tree, retained, (7,), **common)
    assert basal.diagnostics.output_indices == (3,)
    assert apical.diagnostics.output_indices == (7,)
    assert basal.diagnostics.initial_output_seed_columns >= 1
    assert apical.diagnostics.initial_output_seed_columns >= 1
    assert basal.model.port_indices == apical.model.port_indices == retained
    assert basal.model.input_matrix.shape[1] == apical.model.input_matrix.shape[1] == 1
    _assert_seed_in_span(basal.model, tree, 3, 10000.0)
    _assert_seed_in_span(apical.model, tree, 7, 10000.0)


def test_empty_dual_schedule_remains_exactly_the_production_multishift_basis():
    tree = _branched_tree()
    retained = (0, 2)
    shifts = (0.0, 100.0, 1000.0)
    expected = prima_reduce_passive_cable_multishift(
        tree, retained, max_order=5, expansion_frequencies_hz=shifts
    )
    observed = build_output_aware_passive_basis(
        tree,
        retained,
        (6, 7),
        max_order=5,
        input_expansion_frequencies_hz=shifts,
        output_seed_frequencies_hz=(),
    )
    np.testing.assert_array_equal(observed.model.basis, expected.basis)
    np.testing.assert_array_equal(
        observed.model.conductance_matrix_s, expected.conductance_matrix_s
    )
    np.testing.assert_array_equal(
        observed.model.capacitance_matrix_f, expected.capacitance_matrix_f
    )
    np.testing.assert_array_equal(observed.model.input_matrix, expected.input_matrix)
