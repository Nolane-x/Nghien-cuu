"""Tests for instrumented q25 multi-shift Krylov growth audit."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest

import audit_prima_q25_krylov_growth as audit
from amsn.prima import _orthogonalize_block


def test_expected_cross_morphology_model_and_seed_block_counts():
    assert audit.expected_counts() == {"models": 144, "seed_blocks": 864}


def test_instrumented_orthogonalizer_matches_production_private_primitive():
    rng = np.random.default_rng(20261124)
    initial = [np.eye(12)[:, i].copy() for i in range(2)]
    existing_a = [x.copy() for x in initial]
    existing_b = [x.copy() for x in initial]
    candidates = rng.normal(size=(12, 7))
    candidates[:, 6] = candidates[:, 0] + 1e-15 * candidates[:, 1]

    expected = _orthogonalize_block(candidates, existing_a, 1e-12, 10)
    observed, events = audit._instrumented_orthogonalize_block(
        candidates,
        existing_b,
        1e-12,
        10,
        context={"stage": "fixture", "shift_hz": 100.0},
    )
    np.testing.assert_array_equal(observed, expected)
    assert len(existing_a) == len(existing_b)
    for left, right in zip(existing_a, existing_b):
        np.testing.assert_array_equal(left, right)
    assert sum(bool(x["accepted"]) for x in events) == observed.shape[1]


def test_instrumented_orthogonalizer_tracks_rank_rejection():
    candidates = np.column_stack([np.array([1.0, 0.0]), np.array([2.0, 0.0])])
    basis = []
    observed, events = audit._instrumented_orthogonalize_block(
        candidates,
        basis,
        1e-12,
        4,
        context={"stage": "fixture"},
    )
    assert observed.shape == (2, 1)
    assert events[0]["accepted"] is True
    assert events[1]["accepted"] is False
    assert events[1]["rejection_reason"] == "relative_tolerance"
    assert events[1]["residual_ratio"] <= 1e-12


def test_instrumented_orthogonalizer_rejects_nonfinite_candidate():
    with pytest.raises(FloatingPointError, match="non-finite Krylov vector"):
        audit._instrumented_orthogonalize_block(
            np.array([[float("nan")], [0.0]]),
            [],
            1e-12,
            4,
            context={"stage": "fixture"},
        )


def test_instrumented_orthogonalizer_respects_order_cap():
    candidates = np.eye(4)
    basis = [np.array([1.0, 0.0, 0.0, 0.0])]
    observed, events = audit._instrumented_orthogonalize_block(
        candidates,
        basis,
        1e-12,
        2,
        context={"stage": "fixture"},
    )
    assert observed.shape == (4, 1)
    assert len(basis) == 2
    assert len(events) == 1
