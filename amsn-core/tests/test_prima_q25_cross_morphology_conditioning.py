"""Tests for cross-morphology q25 PRIMA basis conditioning audit."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import audit_prima_q25_basis_conditioning as audit


def test_expected_cross_morphology_model_matrix_is_exact():
    assert audit.expected_counts() == {"models": 144, "shift_seeds": 864, "port_leverage": 1152}


def test_generalized_rate_spectrum_is_positive_for_spd_pair():
    import numpy as np

    g = np.diag([4.0, 9.0, 16.0])
    c = np.diag([2.0, 3.0, 4.0])
    minimum, maximum, ratio = audit.generalized_rate_spectrum(g, c)
    assert np.isclose(minimum, 2.0, rtol=1e-14, atol=0.0)
    assert np.isclose(maximum, 4.0, rtol=1e-14, atol=0.0)
    assert np.isclose(ratio, 2.0, rtol=1e-14, atol=0.0)


def test_generalized_rate_spectrum_rejects_non_positive_capacitance():
    import numpy as np
    import pytest

    with pytest.raises(np.linalg.LinAlgError):
        audit.generalized_rate_spectrum(np.eye(2), np.diag([1.0, 0.0]))


def test_condition_number_requires_positive_eigenvalues():
    import numpy as np
    import pytest

    with pytest.raises(ValueError):
        audit.finite_condition(np.array([1.0, 0.0]), "fixture")
    assert audit.finite_condition(np.array([2.0, 4.0]), "fixture") == 2.0
