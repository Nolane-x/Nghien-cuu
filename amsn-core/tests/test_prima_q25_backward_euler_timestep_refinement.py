"""Focused tests for the q25 backward-Euler timestep refinement audit."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import analyze_prima_q25_backward_euler_timestep_refinement as audit


def test_timestep_grid_aligns_pulses_and_all_observation_windows():
    audit.validate_timestep_grid()
    for dt in audit.DT_GRID_MS:
        assert all(round(window / dt) == pytest.approx(window / dt) for window in audit.WINDOWS_MS)
        assert round(audit.tail.PULSE_ONSET_MS / dt) == pytest.approx(audit.tail.PULSE_ONSET_MS / dt)
        assert all(round(width / dt) == pytest.approx(width / dt) for width in audit.PULSE_WIDTHS_MS)


def test_invalid_timestep_that_misses_pulse_edge_is_rejected():
    with pytest.raises(ValueError, match="not an exact multiple"):
        audit.validate_timestep_grid((0.07, 0.05, 0.025))


def test_expected_coverage_contract():
    assert audit.expected_counts() == {
        "metric_rows": 18144,
        "seven_nine_comparison_rows": 9072,
        "source_window_summary_rows": 144,
        "morphology_window_summary_rows": 24,
        "hines_temporal_convergence_rows": 6048,
        "hines_temporal_convergence_summary_rows": 16,
    }


@pytest.mark.parametrize(
    ("coarse_dt", "fine_dt", "stride"),
    [(0.1, 0.025, 4), (0.05, 0.025, 2), (0.025, 0.025, 1)],
)
def test_fine_trace_alignment_uses_end_of_step_samples(coarse_dt, fine_dt, stride):
    fine = np.arange(40, dtype=float).reshape(20, 2)
    aligned = audit.fine_trace_at_coarse_sample_times(fine, coarse_dt, fine_dt)
    expected = fine[stride - 1::stride]
    np.testing.assert_array_equal(aligned, expected)


def test_fine_trace_alignment_rejects_non_nested_timestep_pair():
    with pytest.raises(ValueError, match="integer multiple"):
        audit.fine_trace_at_coarse_sample_times(np.zeros((10, 2)), 0.07, 0.025)


def test_relative_l2_is_scale_invariant():
    reference = np.array([1e-8, -2e-8, 0.5e-8])
    reduced = reference * 1.03
    first = audit.relative_l2_percent(reference, reduced)
    second = audit.relative_l2_percent(reference * 1000.0, reduced * 1000.0)
    assert first == pytest.approx(second, rel=1e-13)
    assert first == pytest.approx(3.0)


def test_source_window_summary_aggregates_all_scenarios_and_outputs():
    metrics = []
    comparisons = []
    for morphology in ("morph_a", "morph_b"):
        for dt in audit.DT_GRID_MS:
            for window in audit.WINDOWS_MS:
                for source in audit.SOURCE_NAMES:
                    for pulse in audit.PULSE_WIDTHS_MS:
                        key = (morphology, dt, source, pulse, window)
                        for scenario in audit.SCENARIO_NAMES:
                            for output in range(7):
                                metrics.append({
                                    "morphology": key[0],
                                    "dt_ms": key[1],
                                    "source_name": key[2],
                                    "pulse_width_ms": key[3],
                                    "window_ms": key[4],
                                    "layout_id": "nine_both_q25",
                                    "absolute_vs_perturbation_hines_delta_pct": 0.01,
                                })
                                comparisons.append({
                                    "morphology": key[0],
                                    "dt_ms": key[1],
                                    "source_name": key[2],
                                    "pulse_width_ms": key[3],
                                    "window_ms": key[4],
                                    "seven_perturbation_transient_nrmse_pct": 1.0,
                                    "nine_perturbation_transient_nrmse_pct": 2.0,
                                    "nine_over_seven_perturbation_transient_ratio": 2.0,
                                })
    rows = audit.summarize_source_windows(metrics, comparisons)
    assert len(rows) == audit.EXPECTED_SOURCE_SUMMARY_ROWS == 144
    assert all(row["scenario_output_pairs"] == 63 for row in rows)
    assert all(row["median_nine_over_seven_ratio"] == 2.0 for row in rows)


def test_morphology_window_summary_keeps_all_dt_and_windows():
    source_rows = []
    for morphology in ("morph_a", "morph_b"):
        for dt in audit.DT_GRID_MS:
            for window in audit.WINDOWS_MS:
                for source in audit.SOURCE_NAMES:
                    for pulse in audit.PULSE_WIDTHS_MS:
                        source_rows.append({
                            "morphology": morphology,
                            "dt_ms": dt,
                            "source_name": source,
                            "pulse_width_ms": pulse,
                            "window_ms": window,
                            "median_nine_over_seven_ratio": 2.5,
                            "p90_nine_over_seven_ratio": 3.0,
                            "median_seven_transient_nrmse_pct": 1e-7,
                            "median_nine_transient_nrmse_pct": 2.5e-7,
                            "worse_pairs": 63,
                            "median_absolute_vs_perturbation_delta_pct": 0.01,
                        })
    rows = audit.summarize_morphology_windows(source_rows)
    assert len(rows) == 2 * 3 * 4
    assert all(row["source_pulse_groups"] == 6 for row in rows)
    assert all(row["worse_pairs_of_378"] == 378 for row in rows)


def test_hines_convergence_summary_uses_full_scenario_protocol_output_coverage():
    rows = []
    for morphology in ("m1", "m2"):
        for coarse_dt in (0.1, 0.05):
            for window in audit.WINDOWS_MS:
                for scenario in audit.SCENARIO_NAMES:
                    for source, pulse in audit.PROTOCOL:
                        for output in range(7):
                            rows.append({
                                "morphology": morphology,
                                "coarse_dt_ms": coarse_dt,
                                "window_ms": window,
                                "full_hines_coarse_vs_fine_nrmse_pct": 0.2,
                            })
    summary = audit.summarize_hines_convergence(rows)
    assert len(summary) == 2 * 2 * 4
    assert all(row["paired_scenario_protocol_output_rows"] == 378 for row in summary)


def test_absolute_current_charge_is_preserved_by_sampled_pulse_convention():
    # With each chosen dt, the integer-sample pulse integrates to the same
    # current charge per protocol column.
    amplitude = float(audit.tail.CURRENT_A)
    for dt_ms in audit.DT_GRID_MS:
        dt_s = dt_ms / 1000.0
        for width in audit.PULSE_WIDTHS_MS:
            samples = int(round(width / dt_ms))
            charge = amplitude * samples * dt_s
            assert charge == pytest.approx(amplitude * width / 1000.0, rel=0.0, abs=1e-27)



def test_factorized_reduced_step_supports_multiple_protocol_rhs():
    from types import SimpleNamespace

    rng = np.random.default_rng(20261124)
    raw_g = rng.normal(size=(5, 5))
    raw_c = rng.normal(size=(5, 5))
    conductance = raw_g.T @ raw_g + np.eye(5) * 3.0
    capacitance = raw_c.T @ raw_c + np.eye(5) * 0.5
    input_matrix = rng.normal(size=(5, 3))
    model = SimpleNamespace(
        conductance_matrix_s=conductance,
        capacitance_matrix_f=capacitance,
        input_matrix=input_matrix,
    )
    dt_s = 2.5e-5
    factor = audit.tail.factor_reduced_backward_euler(model, dt_s)
    previous = rng.normal(size=(5, 6))
    current = rng.normal(size=(3, 6))

    multi = audit.tail.reduced_backward_euler_step_factorized(
        model, factor, previous, current, dt_s
    )
    individual = np.column_stack([
        audit.tail.reduced_backward_euler_step_factorized(
            model, factor, previous[:, column], current[:, column], dt_s
        )
        for column in range(previous.shape[1])
    ])
    np.testing.assert_allclose(multi, individual, rtol=2e-13, atol=2e-13)


def test_sampled_current_matrix_preserves_charge_and_source_routing():
    source_indices = [3, 7, 11]
    protocol = audit.PROTOCOL
    dt_ms = 0.025
    dt_s = dt_ms / 1000.0
    steps = int(round(20.0 / dt_ms))
    observed_charge = np.zeros(len(protocol), dtype=float)
    for step in range(steps):
        current = audit.make_current_matrix(
            16, source_indices, protocol, step, dt_s
        )
        observed_charge += np.sum(current, axis=0) * dt_s

    for column, (source, width_ms) in enumerate(protocol):
        expected_charge = audit.tail.CURRENT_A * width_ms / 1000.0
        assert observed_charge[column] == pytest.approx(
            expected_charge, rel=0.0, abs=1e-27
        )
        source_row = source_indices[audit.SOURCE_NAMES.index(source)]
        assert source_row < 16

def test_expected_dt_order_and_fine_reference():
    assert audit.DT_GRID_MS == (0.1, 0.05, 0.025)
    assert audit.FINE_REFERENCE_DT_MS == 0.025
