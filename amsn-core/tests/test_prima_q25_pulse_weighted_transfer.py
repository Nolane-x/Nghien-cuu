"""Tests for pulse-spectrum-weighted q25 transfer validation."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest

import audit_prima_q25_basis_conditioning as conditioning
import analyze_prima_q25_pulse_weighted_transfer as pulse


def test_frequency_grid_covers_dc_through_nyquist_and_known_zeros():
    f=pulse.build_frequency_grid()
    assert f[0] == 0.0
    assert f[-1] == 5000.0
    assert np.all(np.diff(f) > 0.0)
    assert 100.0 in f and 500.0 in f and 1000.0 in f


def test_expected_pulse_weighted_transfer_coverage():
    assert pulse.expected_counts() == {
        "frequency_hz": len(pulse.FREQUENCIES_HZ),
        "frequency_rows": 380268,
        "weighted_output_rows": 1512,
        "weighted_summary_rows": 168,
        "weighted_source_summary_rows": 24,
        "vs_seven_paired_rows": 756,
        "vs_seven_source_summary_rows": 12,
        "transient_input_rows": 1512,
        "pulse_spectrum_sample_rows": 196,
    }


def test_weighted_transfer_error_is_zero_for_identical_transfer():
    f=np.asarray(pulse.FREQUENCIES_HZ,dtype=float)
    response=np.exp(-1j*2*np.pi*f*0.0002)/(1.0+1j*f/1000.0)
    for width in pulse.PULSE_WIDTHS_MS:
        weighted,unweighted=pulse.weighted_complex_transfer_error(response,response,f,width)
        assert weighted == 0.0
        assert unweighted == 0.0


def test_weighted_transfer_error_tracks_exact_scalar_gain():
    f=np.asarray(pulse.FREQUENCIES_HZ,dtype=float)
    response=1.0/(1.0+1j*f/1000.0)
    actual=1.02*response
    weighted,unweighted=pulse.weighted_complex_transfer_error(response,actual,f,2.0)
    assert np.isclose(weighted,2.0,rtol=1e-12,atol=0.0)
    assert np.isclose(unweighted,2.0,rtol=1e-12,atol=0.0)


def test_weighted_transfer_rejects_nonfinite_or_zero_reference():
    f=np.asarray(pulse.FREQUENCIES_HZ,dtype=float)
    with pytest.raises(ValueError,match="non-finite"):
        pulse.weighted_complex_transfer_error(
            np.array([complex(float("nan"),0.0)]*len(f)),
            np.ones(len(f),dtype=complex),f,2.0
        )
    with pytest.raises(ValueError,match="zero energy"):
        pulse.weighted_complex_transfer_error(
            np.zeros(len(f),dtype=complex),np.zeros(len(f),dtype=complex),f,2.0
        )


def test_average_rank_handles_ties_and_safe_correlations():
    ranks=pulse._average_ranks([1.0,2.0,2.0,4.0])
    np.testing.assert_allclose(ranks,[1.0,2.5,2.5,4.0])
    assert pulse.safe_corr([1,2,3],[1,2,3]) > 0.999
    assert pulse.safe_corr([1,1,1],[1,2,3]) is None


import math
