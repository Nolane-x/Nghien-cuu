import math

import numpy as np
import pytest

from amsn.cable import CableCompartment, CableTree
from amsn.synapses import DoubleExponentialSynapse


def _tree():
    return CableTree([
        CableCompartment("soma", 20e-6, 20e-6, None),
        CableCompartment("dend_a", 100e-6, 2e-6, "soma"),
        CableCompartment("dend_b", 100e-6, 1.5e-6, "soma"),
        CableCompartment("branch", 80e-6, 1.0e-6, "dend_a"),
    ])


def test_double_exponential_synapse_is_zero_before_onset_and_peak_normalized():
    synapse = DoubleExponentialSynapse(
        onset_s=0.001,
        peak_conductance_s=0.8e-9,
        tau_rise_s=0.0002,
        tau_decay_s=0.002,
        reversal_potential_v=0.0,
    )
    assert synapse.conductance_at(0.0) == 0.0
    assert synapse.conductance_at(0.001) == 0.0
    assert synapse.conductance_at(synapse.peak_time_s) == pytest.approx(
        0.8e-9, rel=1e-12
    )
    assert synapse.conductance_at(synapse.peak_time_s - 1e-4) < 0.8e-9
    assert synapse.conductance_at(synapse.peak_time_s + 1e-4) < 0.8e-9
    assert synapse.conductance_at(0.01) > 0.0


@pytest.mark.parametrize("kwargs", [
    {"onset_s": -0.001},
    {"peak_conductance_s": -1e-9},
    {"tau_rise_s": 0.0},
    {"tau_decay_s": 0.0},
    {"tau_rise_s": 0.002, "tau_decay_s": 0.001},
    {"reversal_potential_v": float("nan")},
])
def test_double_exponential_synapse_rejects_invalid_parameters(kwargs):
    args = {
        "onset_s": 0.0,
        "peak_conductance_s": 1e-9,
        "tau_rise_s": 0.0002,
        "tau_decay_s": 0.002,
        "reversal_potential_v": 0.0,
    }
    args.update(kwargs)
    with pytest.raises(ValueError):
        DoubleExponentialSynapse(**args)


def test_double_exponential_synapse_rejects_nonfinite_query_time():
    synapse = DoubleExponentialSynapse(0.0, 1e-9, 0.0002, 0.002)
    with pytest.raises(ValueError, match="time_s"):
        synapse.conductance_at(float("nan"))


def test_synaptic_hines_step_matches_independent_dense_linear_system():
    tree = _tree()
    voltage = np.array([-60e-3, -58e-3, -62e-3, -55e-3])
    dt_s = 0.0001
    conductance = np.array([0.1e-9, 0.7e-9, 0.3e-9, 0.5e-9])
    reversal = np.array([0.0, 0.0, -0.075, 0.0])
    current = np.array([0.1e-12, -0.2e-12, 0.05e-12, 0.0])

    got = tree.step_synaptic_conductance(
        voltage, dt_s, conductance, reversal, current
    )
    c_over_dt = tree.capacitance_f / dt_s
    total_g = tree.membrane_leak_s + conductance
    membrane_source = (
        tree.membrane_leak_s * tree.parameters.e_leak_v
        + conductance * reversal
    )
    matrix = np.diag(c_over_dt + total_g)
    rhs = c_over_dt * voltage + membrane_source + current
    for i in range(1, tree.n_compartments):
        parent = tree.parent_index[i]
        axial = tree.axial_g_s[i]
        matrix[i, i] += axial
        matrix[parent, parent] += axial
        matrix[i, parent] -= axial
        matrix[parent, i] -= axial
    expected = np.linalg.solve(matrix, rhs)
    np.testing.assert_allclose(got, expected, rtol=2e-12, atol=2e-13)


def test_zero_synaptic_conductance_is_identical_to_passive_step():
    tree = _tree()
    voltage = np.linspace(-0.065, -0.050, tree.n_compartments)
    current = np.linspace(0.0, 0.2e-12, tree.n_compartments)
    got = tree.step_synaptic_conductance(
        voltage,
        0.0001,
        np.zeros(tree.n_compartments),
        0.0,
        current,
    )
    expected = tree.step_passive(voltage, 0.0001, current)
    np.testing.assert_allclose(got, expected, rtol=2e-14, atol=1e-15)


@pytest.mark.parametrize("conductance", [
    np.array([-1e-9, 0.0, 0.0, 0.0]),
    np.array([0.0, 0.0, float("nan"), 0.0]),
    np.zeros(3),
])
def test_synaptic_step_rejects_invalid_conductance(conductance):
    with pytest.raises(ValueError):
        _tree().step_synaptic_conductance(
            np.full(4, -0.065), 0.0001, conductance, 0.0
        )


def test_synaptic_simulation_without_conductance_matches_passive_simulation():
    tree = _tree()
    duration = 0.005
    dt = 0.0001

    passive = tree.simulate_passive(duration, dt)
    synaptic = tree.simulate_synaptic(
        duration,
        dt,
        synaptic_conductance_fn=lambda _time: np.zeros(tree.n_compartments),
        reversal_potential_v=0.0,
    )
    np.testing.assert_allclose(
        synaptic.voltage_v, passive.voltage_v, rtol=0.0, atol=1e-14
    )


def test_ampa_like_double_exponential_conductance_depolarizes_target_dendrite():
    tree = _tree()
    target = tree.index["dend_a"]
    synapse = DoubleExponentialSynapse(
        onset_s=0.001,
        peak_conductance_s=0.8e-9,
        tau_rise_s=0.0002,
        tau_decay_s=0.002,
        reversal_potential_v=0.0,
    )

    def conductance_fn(time_s):
        result = np.zeros(tree.n_compartments)
        result[target] = synapse.conductance_at(time_s)
        return result

    trace = tree.simulate_synaptic(
        duration_s=0.025,
        dt_s=0.000025,
        synaptic_conductance_fn=conductance_fn,
        reversal_potential_v=synapse.reversal_potential_v,
    )
    baseline = tree.parameters.e_leak_v
    target_trace = trace.voltage_v[:, target]
    soma_trace = trace.voltage_v[:, tree.index["soma"]]
    assert np.all(np.isfinite(trace.voltage_v))
    assert np.max(target_trace) > baseline
    assert np.max(soma_trace) > baseline
    assert target_trace[-1] < np.max(target_trace)


def test_synaptic_simulation_rejects_nonfinite_reversal_potential():
    tree = _tree()
    with pytest.raises(ValueError, match="reversal_potential_v"):
        tree.simulate_synaptic(
            duration_s=0.001,
            dt_s=0.0001,
            synaptic_conductance_fn=lambda _time: np.zeros(tree.n_compartments),
            reversal_potential_v=float("inf"),
        )


def test_synaptic_simulation_samples_kinetics_at_step_left_edge():
    tree = _tree()
    sampled_times = []

    def conductance_fn(time_s):
        sampled_times.append(time_s)
        return np.zeros(tree.n_compartments)

    tree.simulate_synaptic(
        duration_s=0.0002,
        dt_s=0.0001,
        synaptic_conductance_fn=conductance_fn,
        reversal_potential_v=0.0,
    )

    assert sampled_times == pytest.approx([0.0, 0.0001])

def test_double_exponential_synapse_uses_alpha_limit_for_equal_time_constants():
    peak = 0.8e-9
    tau = 0.001
    synapse = DoubleExponentialSynapse(
        onset_s=0.002,
        peak_conductance_s=peak,
        tau_rise_s=tau,
        tau_decay_s=tau,
    )

    assert synapse.peak_time_s == pytest.approx(0.003)
    assert synapse.conductance_at(synapse.peak_time_s) == pytest.approx(
        peak, rel=1e-12
    )
    assert synapse.conductance_at(0.0035) == pytest.approx(
        peak * 1.5 * math.exp(-0.5), rel=1e-12
    )
    assert synapse.conductance_at(0.004) == pytest.approx(
        peak * 2.0 * math.exp(-1.0), rel=1e-12
    )


def test_double_exponential_synapse_uses_stable_alpha_limit_for_near_equal_taus():
    peak = 1.2e-9
    tau_rise = 0.001
    tau_decay = 0.001000000000001
    synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=peak,
        tau_rise_s=tau_rise,
        tau_decay_s=tau_decay,
    )

    assert synapse.peak_time_s == pytest.approx(tau_rise, rel=1e-10)
    assert synapse.conductance_at(synapse.peak_time_s) == pytest.approx(
        peak, rel=1e-12
    )
