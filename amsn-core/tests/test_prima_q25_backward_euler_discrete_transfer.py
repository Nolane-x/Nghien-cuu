"""Tests for the exact backward-Euler discrete-time transfer relation."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import analyze_prima_q25_backward_euler_discrete_transfer as audit


def test_backward_euler_frequency_mapping_endpoints():
    frequencies = np.array([0.0, 1000.0, 5000.0])
    values = audit.backward_euler_s_values(frequencies, 1e-4)
    assert values[0] == 0.0
    assert values[-1].real == pytest.approx(20000.0)
    assert values[-1].imag == pytest.approx(0.0, abs=1e-10)
    assert values[1].real > 0.0
    assert values[1].imag > 0.0


def test_frequency_bins_for_each_window_are_subsets_of_master_grid():
    for window in audit.WINDOWS_MS:
        frequencies, indices = audit.finite_window_frequency_indices(window)
        assert np.allclose(
            audit.MASTER_FREQUENCIES_HZ[indices], frequencies,
            rtol=0.0, atol=1e-10,
        )
        assert frequencies[0] == 0.0
        assert frequencies[-1] == 5000.0
        assert frequencies[1] == pytest.approx(1000.0 / window)


def test_zoh_factor_matches_analytic_rectangular_pulse_transform():
    dt = 1e-4
    sample_count = 2000
    onset_index = 20
    width_samples = 20
    amplitude = 10e-12
    frequencies = np.array([0.0, 25.0, 250.0, 1000.0, 3200.0, 5000.0])
    samples = np.zeros(sample_count)
    samples[onset_index:onset_index + width_samples] = amplitude
    dft = np.fft.rfft(samples)
    indices = np.rint(frequencies / 5.0).astype(int)
    sample_spectrum = dft[indices]
    observed = audit.zoh_frequency_factor(frequencies, dt) * sample_spectrum
    width_s = width_samples * dt
    centre_s = (onset_index + width_samples / 2.0) * dt
    expected = (
        amplitude * width_s * np.sinc(frequencies * width_s)
        * np.exp(-2j * np.pi * frequencies * centre_s)
    )
    np.testing.assert_allclose(observed, expected, rtol=2e-11, atol=1e-28)


def test_finite_record_dft_identity_includes_terminal_state():
    # Scalar passive BE: A*x[n] - D*x[n-1] = B*u[n].
    conductance = 2.0
    capacitance = 3.0
    dt = 0.1
    d_over_dt = capacitance / dt
    lhs = conductance + d_over_dt
    n = 200
    current = np.zeros(n)
    current[20:40] = 1.0
    state = np.zeros(n)
    previous = 0.0
    for index, value in enumerate(current):
        previous = (d_over_dt * previous + value) / lhs
        state[index] = previous

    frequencies = np.fft.rfftfreq(n, d=dt)
    s_be = audit.backward_euler_s_values(frequencies, dt)
    operator = conductance + s_be * capacitance
    input_dft = np.fft.rfft(current)
    terminal = state[-1]
    reconstructed = input_dft / operator - (d_over_dt * terminal) / operator
    observed = np.fft.rfft(state)
    np.testing.assert_allclose(reconstructed, observed, rtol=2e-11, atol=2e-12)


def test_discrete_response_matches_z_domain_recurrence():
    conductance = 2.0
    capacitance = 3e-4
    current_gain = 1.0
    output_gain = 1.0
    dt = 1e-4
    frequencies = np.array([0.0, 50.0, 500.0, 2500.0, 5000.0])
    omega_dt = 2.0 * np.pi * frequencies * dt
    z_inverse = np.exp(-1j * omega_dt)

    d_over_dt = capacitance / dt
    lhs = conductance + d_over_dt
    state_pole = d_over_dt / lhs
    input_gain = current_gain / lhs
    recurrence_response = (
        output_gain * input_gain / (1.0 - state_pole * z_inverse)
    )

    s_be = audit.backward_euler_s_values(frequencies, dt)
    resolvent_response = (
        output_gain * current_gain / (conductance + s_be * capacitance)
    )
    np.testing.assert_allclose(
        recurrence_response, resolvent_response, rtol=2e-14, atol=1e-14
    )

    continuous_response = (
        output_gain * current_gain
        / (conductance + 1j * 2.0 * np.pi * frequencies * capacitance)
    )
    assert recurrence_response[0] == pytest.approx(continuous_response[0])
    assert abs(recurrence_response[-1] - continuous_response[-1]) > 1e-3


def test_weighted_error_is_scale_invariant_for_common_input_gain():
    frequencies = np.fft.rfftfreq(200, d=1e-4)
    full = 2.0 + 1j * frequencies / 10000.0
    model = full * (1.0 + 0.02j)
    input_dft = np.ones(frequencies.size, dtype=np.complex128)
    first = audit.weighted_transfer_error(
        full, model, input_dft, frequencies, continuous_zoh_input=False
    )[0]
    second = audit.weighted_transfer_error(
        full, model, input_dft * 17.0, frequencies, continuous_zoh_input=False
    )[0]
    assert first == pytest.approx(second, rel=1e-13)


def test_finite_identity_residual_uses_output_scale_not_tiny_error_scale():
    actual = np.array([1e-9 + 0j, -1e-9 + 0j])
    reconstructed = actual + np.array([1e-12 + 0j, -1e-12 + 0j])
    relative, absolute = audit._finite_identity_error(
        actual, reconstructed, scale_norm=float(np.linalg.norm(actual) * 1e3)
    )
    assert absolute == pytest.approx(np.sqrt(2.0) * 1e-12)
    assert relative == pytest.approx(1e-6)


def test_full_hines_absolute_and_perturbation_replays_are_equivalent():
    from types import SimpleNamespace

    tree = SimpleNamespace(
        n_compartments=3,
        capacitance_f=np.array([1.0e-12, 1.2e-12, 0.8e-12]),
        membrane_leak_s=np.array([1.0e-9, 1.2e-9, 0.9e-9]),
        axial_g_s=np.array([0.0, 2.0e-9, 1.5e-9]),
        parent_index=np.array([0, 0, 0], dtype=np.int64),
        parameters=SimpleNamespace(e_leak_v=-0.070),
    )
    factor = audit.tail.build_tree_hines_be_factor(tree, audit.DT_S)
    source_indices = [0, 1, 2]
    output_indices = [0, 1, 2]

    canonical, _, canonical_protocol = audit.simulate_full_hines_with_terminal_states(
        tree, factor, source_indices, output_indices
    )
    perturbation, _, perturbation_protocol = audit.simulate_full_hines_perturbation_windows(
        tree, factor, source_indices, output_indices
    )
    assert canonical_protocol == perturbation_protocol
    relative_delta_pct = (
        100.0 * np.linalg.norm(canonical - perturbation)
        / max(float(np.linalg.norm(perturbation)), 1e-30)
    )
    # The absolute-voltage and zero-origin formulations are algebraically
    # identical; the tolerance is a numerical parity guard, not a solver-accuracy
    # claim. Production code continues to use the canonical absolute-voltage path.
    assert relative_delta_pct <= 1e-5


def test_morphology_window_summary_keeps_perturbation_metric_separate():
    source_rows = []
    for morphology in ("morph_a", "morph_b"):
        for source in audit.SOURCE_NAMES:
            for pulse_width in audit.PULSE_WIDTHS_MS:
                for window in audit.WINDOWS_MS:
                    source_rows.append({
                        "morphology": morphology,
                        "source_name": source,
                        "pulse_width_ms": pulse_width,
                        "window_ms": window,
                        "median_nine_over_seven_continuous_ac_ratio": 32.0,
                        "median_nine_over_seven_discrete_be_ratio": 30.0,
                        "median_nine_over_seven_transient_nrmse_ratio": 1.02,
                        "median_nine_over_seven_perturbation_coordinate_transient_nrmse_ratio": 25.0,
                        "median_nine_boundary_component_of_error_norm_pct": 4.0,
                        "continuous_ac_worse_pairs": 63,
                        "discrete_be_worse_pairs": 63,
                        "transient_nrmse_worse_pairs": 35,
                        "perturbation_coordinate_transient_nrmse_worse_pairs": 63,
                    })

    rows = audit._summarize_morphology_windows(source_rows)
    assert len(rows) == 2 * len(audit.WINDOWS_MS)
    assert all(row["source_pulse_groups"] == 6 for row in rows)
    assert all(
        row["median_nine_over_seven_absolute_transient_nrmse_ratio"] == 1.02
        for row in rows
    )
    assert all(
        row["median_nine_over_seven_perturbation_transient_nrmse_ratio"] == 25.0
        for row in rows
    )
    assert all(
        row["median_perturbation_transient_worse_pairs_of_63"] == 63.0
        for row in rows
    )


def test_expected_coverage_contract():
    assert audit.expected_counts() == {
        "master_frequency_points": 1001,
        "frequency_summary_rows": 84084,
        "case_metric_rows": 6048,
        "nine_seven_comparison_rows": 3024,
        "source_window_summary_rows": 48,
        "morphology_window_summary_rows": 8,
        "finite_dft_identity_rows": 864,
    }
