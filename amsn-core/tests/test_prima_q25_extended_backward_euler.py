"""Tests for exact-backward-Euler extended-window q25 audit."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest
from scipy import __version__ as SCIPY_VERSION

import audit_prima_q25_extended_backward_euler as audit


def test_expected_extended_window_coverage():
    assert audit.expected_counts() == {
        "windows_ms": 4,
        "extended_transient_rows": 6048,
        "comparison_rows": 3024,
        "20ms_parity_rows": 756,
        "by_output_summary_rows": 672,
        "comparison_summary_rows": 336,
        "by_source_summary_rows": 48,
        "window_summary_rows": 16,
        "layout_window_summary_rows": 32,
    }


def test_sparse_full_cable_factor_matches_tree_backward_euler_step():
    from amsn.cable import CableCompartment, CableTree, PassiveParameters

    tree = CableTree(
        [
            CableCompartment("soma", 10e-6, 10e-6),
            CableCompartment("branch_a", 8e-6, 4e-6, "soma"),
            CableCompartment("branch_b", 6e-6, 3e-6, "branch_a"),
        ],
        PassiveParameters(),
    )
    factor, c_over_dt = audit.build_sparse_hines_factor(tree, audit.DT_S)
    voltage_perturbation = np.zeros((tree.n_compartments, 2), dtype=float)
    leak = tree.parameters.e_leak_v
    for step in range(17):
        current = np.zeros((tree.n_compartments, 2), dtype=float)
        if 2 <= step < 7:
            current[0, 0] = audit.CURRENT_A
        if 4 <= step < 12:
            current[2, 1] = audit.CURRENT_A
        observed = factor.solve(
            c_over_dt[:, None] * voltage_perturbation + current
        )
        expected = np.column_stack([
            tree.step_passive(
                leak + voltage_perturbation[:, column],
                audit.DT_S,
                current[:, column],
            ) - leak
            for column in range(2)
        ])
        np.testing.assert_allclose(observed, expected, rtol=2e-11, atol=2e-16)
        voltage_perturbation = observed


def test_reduced_transition_operators_match_step_backward_euler():
    from amsn.prima import PassiveReducedModel

    model = PassiveReducedModel(
        port_indices=(0, 1),
        basis=np.eye(2),
        conductance_matrix_s=np.array([[3.0, -1.0], [-1.0, 2.0]]),
        capacitance_matrix_f=np.array([[2.0, 0.0], [0.0, 1.0]]),
        input_matrix=np.eye(2),
    )
    transition, input_map = audit.reduced_backward_euler_operators(model, 0.25)
    state = np.array([0.2, -0.1])
    current = np.array([1.0, 0.5])
    expected = model.step_backward_euler(state, 0.25, current)
    observed = transition @ state + input_map @ current
    np.testing.assert_allclose(observed, expected, rtol=1e-14, atol=1e-14)


def test_protocol_has_correct_inclusive_and_exclusive_edges():
    protocol = audit.column_protocol()
    assert protocol == [
        ("soma", 2.0), ("soma", 10.0),
        ("basal_q75", 2.0), ("basal_q75", 10.0),
        ("apical_q75", 2.0), ("apical_q75", 10.0),
    ]
    current = audit._make_current_matrix(4, [0, 1, 2], protocol, 20)
    expected_start = np.zeros((4, 6), dtype=float)
    expected_start[0, 0:2] = audit.CURRENT_A
    expected_start[1, 2:4] = audit.CURRENT_A
    expected_start[2, 4:6] = audit.CURRENT_A
    np.testing.assert_array_equal(current, expected_start)

    current_end_2ms = audit._make_current_matrix(4, [0, 1, 2], protocol, 40)
    expected_after_2ms = np.zeros((4, 6), dtype=float)
    expected_after_2ms[0, 1] = audit.CURRENT_A
    expected_after_2ms[1, 3] = audit.CURRENT_A
    expected_after_2ms[2, 5] = audit.CURRENT_A
    np.testing.assert_array_equal(current_end_2ms, expected_after_2ms)


def test_sparse_factor_uses_scipy_and_finite_protocol():
    assert SCIPY_VERSION
    assert audit.DT_MS == 0.1
    assert audit.WINDOWS_MS == (20.0, 40.0, 100.0, 200.0)
