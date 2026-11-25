"""Tests for the research-only passive output-aware dual-seed PRIMA prototype."""
from __future__ import annotations

import numpy as np
import pytest

from amsn.cable import CableCompartment, CableTree, PassiveParameters
from amsn.prima import _solve_shifted_passive_real, prima_reduce_passive_cable_multishift

from experimental_prima_output_aware_basis import build_output_aware_passive_basis


def _branched_tree() -> CableTree:
    return CableTree(
        [
            CableCompartment("soma", 20e-6, 20e-6),
            CableCompartment("basal_a", 100e-6, 2.0e-6, "soma"),
            CableCompartment("basal_b", 85e-6, 1.5e-6, "basal_a"),
            CableCompartment("apical_a", 140e-6, 1.8e-6, "soma"),
            CableCompartment("apical_b", 120e-6, 1.2e-6, "apical_a"),
            CableCompartment("tuft", 90e-6, 0.9e-6, "apical_b"),
        ],
        PassiveParameters(),
    )


def test_empty_output_seed_schedule_reproduces_existing_multishift_prima_exactly():
    tree = _branched_tree()
    retained = (0, 2)
    shifts = (0.0, 100.0, 1000.0)
    expected = prima_reduce_passive_cable_multishift(
        tree, retained, max_order=5, expansion_frequencies_hz=shifts
    )
    observed = build_output_aware_passive_basis(
        tree,
        retained,
        (5,),
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
    assert observed.diagnostics.initial_output_seed_columns == 0
    assert observed.diagnostics.initial_input_seed_columns == expected.order


def test_dual_output_seed_enriches_state_basis_without_expanding_input_selector():
    tree = _branched_tree()
    retained = (0, 2)
    outputs = (5,)
    result = build_output_aware_passive_basis(
        tree,
        retained,
        outputs,
        max_order=tree.n_compartments,
        input_expansion_frequencies_hz=(0.0, 100.0, 1000.0),
        output_seed_frequencies_hz=(1000.0,),
    )
    model = result.model
    diagnostics = result.diagnostics

    assert diagnostics.initial_output_seed_columns >= 1
    assert diagnostics.actual_order <= diagnostics.order_cap
    assert diagnostics.input_seed_columns_per_shift == (2, 2, 2)
    assert len(diagnostics.output_seed_columns_per_shift) == 1

    # The reduced input selector is still exactly the original retained ports.
    assert model.port_indices == retained
    assert model.input_matrix.shape == (model.order, len(retained))
    np.testing.assert_array_equal(
        model.input_matrix, model.basis[np.asarray(retained), :].T
    )

    # Outputs are independent measurement rows of the full-compartment basis.
    assert result.output_matrix.shape == (len(outputs), model.order)
    np.testing.assert_array_equal(
        result.output_matrix, model.basis[np.asarray(outputs), :]
    )

    # The selected dual resolvent vector is contained in the enriched subspace.
    selector = np.zeros(tree.n_compartments)
    selector[outputs[0]] = 1.0
    dual_seed = _solve_shifted_passive_real(tree, 2.0 * np.pi * 1000.0, selector)
    residual = dual_seed - model.basis @ (model.basis.T @ dual_seed)
    assert np.linalg.norm(residual) <= 2e-12 * np.linalg.norm(dual_seed)

    # Congruence projection preserves the passive positive-definite G/C pair.
    np.linalg.cholesky(model.conductance_matrix_s)
    np.linalg.cholesky(model.capacitance_matrix_f)
    assert diagnostics.basis_orthogonality_max_abs < 2e-12


def test_output_aware_builder_rejects_duplicate_or_invalid_indices():
    tree = _branched_tree()
    common = {
        "max_order": 4,
        "input_expansion_frequencies_hz": (0.0, 100.0),
    }
    with pytest.raises(ValueError, match="unique"):
        build_output_aware_passive_basis(
            tree, (0, 0), (5,), **common
        )
    with pytest.raises(IndexError, match="outside"):
        build_output_aware_passive_basis(
            tree, (0,), (tree.n_compartments,), **common
        )
    with pytest.raises(TypeError, match="integer"):
        build_output_aware_passive_basis(
            tree, (0,), (True,), **common
        )


def test_output_aware_builder_rejects_bad_frequency_and_order_contracts():
    tree = _branched_tree()
    with pytest.raises(ValueError, match="non-negative"):
        build_output_aware_passive_basis(
            tree, (0,), (5,), max_order=4,
            input_expansion_frequencies_hz=(0.0, -1.0),
        )
    with pytest.raises(ValueError, match="unique"):
        build_output_aware_passive_basis(
            tree, (0,), (5,), max_order=4,
            input_expansion_frequencies_hz=(0.0, 100.0),
            output_seed_frequencies_hz=(100.0, 100.0),
        )
    with pytest.raises(ValueError, match="positive"):
        build_output_aware_passive_basis(
            tree, (0,), (5,), max_order=0,
            input_expansion_frequencies_hz=(0.0, 100.0),
        )


def test_output_seed_budget_is_reported_without_changing_requested_input_seed_count():
    tree = _branched_tree()
    result = build_output_aware_passive_basis(
        tree,
        (0,),
        (4, 5),
        max_order=3,
        input_expansion_frequencies_hz=(0.0, 100.0),
        output_seed_frequencies_hz=(1000.0,),
    )
    assert len(result.diagnostics.input_seed_columns_per_shift) == 2
    assert len(result.diagnostics.output_seed_columns_per_shift) == 1
    assert result.diagnostics.initial_input_seed_columns <= 3
    assert result.diagnostics.initial_output_seed_columns <= 3
    assert result.model.port_indices == (0,)
    assert result.model.input_matrix.shape == (result.model.order, 1)
