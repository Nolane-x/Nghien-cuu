"""Tests for q25 transfer frequency localization."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest

import analyze_prima_q25_transfer_frequency_localization as analysis


def test_expected_frequency_map_coverage_is_exact():
    assert analysis.expected_counts() == {
        "input_frequency_rows": 95256,
        "output_frequency_rows": 10584,
        "source_frequency_rows": 1512,
        "vs_seven_output_frequency_rows": 7938,
        "vs_seven_source_frequency_rows": 1134,
        "pulse_spectrum_weight_rows": 18,
    }


def test_rectangular_pulse_spectrum_dc_and_known_zeros():
    rows = analysis.pulse_spectrum_rows()
    two_ms = {(r["frequency_hz"]):r for r in rows if r["pulse_width_ms"] == 2.0}
    ten_ms = {(r["frequency_hz"]):r for r in rows if r["pulse_width_ms"] == 10.0}
    assert np.isclose(two_ms[1000.0]["normalized_rectangular_pulse_spectral_power"], 0.0, atol=1e-28)
    assert np.isclose(ten_ms[100.0]["normalized_rectangular_pulse_spectral_power"], 0.0, atol=1e-28)
    assert two_ms[0.1]["normalized_rectangular_pulse_spectral_power"] > 0.99
    assert ten_ms[0.1]["normalized_rectangular_pulse_spectral_power"] > 0.99


def test_percentile_interpolates_between_samples():
    assert analysis.percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5


def test_output_frequency_group_requires_nine_scenarios():
    rows=[]
    for scenario in analysis.SCENARIOS[:-1]:
        rows.append({
            "morphology":analysis.MORPHOLOGIES[0],
            "layout_id":"seven",
            "basis_order":168,
            "stage":"seed",
            "round_index":0,
            "basis_dimension":42,
            "source_name":"soma",
            "output_swc_id":1,
            "output_role":"soma",
            "frequency_hz":0.1,
            "parameter_scenario":scenario,
            "absolute_error_ohm":1e-9,
            "relative_absolute_error_pct":1e-8,
        })
    with pytest.raises(ValueError,match="scenario coverage mismatch"):
        analysis.group_output_frequency(rows)


def test_zero_seven_port_frequency_denominator_is_rejected():
    base={
        "morphology":analysis.MORPHOLOGIES[0],"layout_id":"seven",
        "basis_order":168,"stage":"seed","round_index":0,"basis_dimension":42,
        "source_name":"soma","output_swc_id":1,"output_role":"soma",
        "frequency_hz":0.1,"parameter_scenario":"nominal",
        "median_relative_transfer_error_pct":0.0,
        "max_absolute_transfer_error_ohm":0.0,
    }
    candidate=dict(base,layout_id="nine_both_q25",median_relative_transfer_error_pct=1e-8)
    rows=[base,candidate]
    with pytest.raises(ValueError,match="zero seven-port denominator"):
        analysis.compare_with_seven(rows)
