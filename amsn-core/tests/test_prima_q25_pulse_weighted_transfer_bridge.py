"""Tests for the pulse-weighted q25 transfer / transient bridge."""
from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import numpy as np
import pytest

import analyze_prima_q25_pulse_weighted_transfer_bridge as bridge


def test_expected_pulse_weighted_bridge_coverage():
    assert bridge.expected_counts() == {
        "frequency_points": 1001,
        "model_weighted_rows": 3024,
        "band_energy_rows": 12096,
        "transient_bridge_rows": 1512,
        "by_output_summary_rows": 336,
        "comparison_summary_rows": 84,
        "by_source_summary_rows": 48,
        "band_summary_rows": 192,
    }


def test_rectangular_pulse_spectrum_has_expected_nulls():
    frequencies = np.array([0.0, 100.0, 200.0, 500.0, 1000.0])
    power_10ms = bridge.rectangular_pulse_power_spectrum(frequencies, 10.0)
    assert power_10ms[0] > 0.0
    assert np.all(power_10ms[1:] < 1e-50)


def test_weighted_transfer_error_is_zero_for_identical_transfer():
    frequencies = bridge.FREQUENCIES_HZ
    reference = 3.0 + 2.0j / (1.0 + 1j * frequencies)
    metrics = bridge.integrate_weighted_error(
        frequencies, reference, reference.copy(), 2.0
    )
    assert metrics["pulse_weighted_relative_l2_pct"] == 0.0
    assert metrics["pulse_weighted_error_energy"] == 0.0


def test_weighted_error_responds_to_constant_relative_perturbation():
    frequencies = bridge.FREQUENCIES_HZ
    reference = 2.0 + 1.0j / (1.0 + 1j * frequencies)
    approximation = reference * 1.02
    metrics = bridge.integrate_weighted_error(
        frequencies, reference, approximation, 10.0
    )
    assert np.isclose(
        metrics["pulse_weighted_relative_l2_pct"], 2.0,
        rtol=1e-12, atol=0.0,
    )


def test_band_error_shares_sum_to_one_hundred_percent():
    frequencies = bridge.FREQUENCIES_HZ
    reference = 1.0 / (1.0 + 1j * frequencies / 250.0)
    approximation = reference + 1e-4 / (1.0 + 1j * frequencies / 100.0)
    bands = bridge.integrate_band_energy(frequencies, reference, approximation, 2.0)
    assert len(bands) == 4
    assert np.isclose(sum(x["band_error_share_pct"] for x in bands), 100.0,
                      rtol=1e-9, atol=1e-8)


def test_vectorized_hines_matches_reference_single_frequency_solver():
    from amsn.cable import CableCompartment, CableTree, PassiveParameters

    tree = CableTree(
        [
            CableCompartment("soma", 10e-6, 10e-6),
            CableCompartment("branch_a", 8e-6, 4e-6, "soma"),
            CableCompartment("branch_b", 6e-6, 3e-6, "branch_a"),
        ],
        PassiveParameters(),
    )
    frequencies = np.arange(0.0, 101.0, 5.0)
    sources = [0, 2]
    outputs = [0, 1, 2]
    observed = bridge.batched_hines_frequency_response(
        tree, frequencies, sources, outputs, chunk_size=7
    )
    expected = np.empty_like(observed)
    for j, frequency in enumerate(frequencies):
        for k, source in enumerate(sources):
            current = np.zeros(tree.n_compartments, dtype=np.complex128)
            current[source] = 1.0
            full = tree.solve_passive_frequency_response(frequency, current)
            expected[j, :, k] = full[np.asarray(outputs)]
    np.testing.assert_allclose(observed, expected, rtol=2e-13, atol=1e-18)


def test_transient_input_files_are_expected_locations():
    assert set(bridge.TRANSIENT_FILES) == {"NMO_163775", "NMO_107159"}
    assert bridge.PULSE_WIDTHS_MS == (2.0, 10.0)
    assert bridge.PULSE_ONSET_MS == 2.0
