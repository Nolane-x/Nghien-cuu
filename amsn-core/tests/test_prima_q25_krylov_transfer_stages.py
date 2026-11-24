"""Tests for cross-morphology Krylov-prefix transfer residual audit."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest

import analyze_prima_q25_krylov_transfer_stages as transfer


def test_expected_transfer_stage_matrix_is_exact():
    assert transfer.expected_counts() == {
        "snapshots": 504,
        "model_output_rows": 10584,
        "frequency_rows": 95256,
        "summary_rows": 1176,
        "source_summary_rows": 168,
    }


def test_projected_passive_matrices_match_dense_three_compartment_fixture():
    from amsn.cable import CableCompartment, CableTree, PassiveParameters

    tree = CableTree(
        [
            CableCompartment("soma", 10e-6, 10e-6),
            CableCompartment("branch_a", 8e-6, 4e-6, "soma"),
            CableCompartment("branch_b", 6e-6, 3e-6, "branch_a"),
        ],
        PassiveParameters(),
    )
    basis = np.linalg.qr(
        np.array([[1.0, 2.0], [2.0, -1.0], [1.0, 1.0]], dtype=float)
    )[0]
    g, c = transfer.projected_passive_matrices(tree, basis)

    from amsn.prima import _apply_passive_conductance

    expected_g = basis.T @ _apply_passive_conductance(tree, basis)
    expected_c = basis.T @ (tree.capacitance_f[:, None] * basis)
    np.testing.assert_allclose(g, 0.5 * (expected_g + expected_g.T), rtol=1e-14, atol=1e-20)
    np.testing.assert_allclose(c, 0.5 * (expected_c + expected_c.T), rtol=1e-14, atol=1e-25)
    assert np.linalg.eigvalsh(g).min() > 0.0
    assert np.linalg.eigvalsh(c).min() > 0.0


def test_complex_transfer_relative_l2_error():
    reference = np.array([1.0 + 1.0j, 2.0 - 1.0j])
    assert transfer.complex_relative_l2_percent(reference, reference) == 0.0
    actual = reference * 1.01
    assert np.isclose(
        transfer.complex_relative_l2_percent(reference, actual),
        1.0,
        rtol=1e-12,
        atol=0.0,
    )


def test_complex_transfer_metric_rejects_nonfinite_values():
    with pytest.raises(ValueError, match="finite"):
        transfer.complex_relative_l2_percent(
            np.array([1.0 + 0.0j]), np.array([complex(float("nan"), 0.0)])
        )


def test_snapshot_stage_schedule_matches_basis_orders():
    assert transfer.STAGES_BY_ORDER == {112: 3, 168: 4}
    assert transfer.EXPECTED_SNAPSHOTS == 504
