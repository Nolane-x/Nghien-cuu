import numpy as np

from amsn.cable import CableCompartment, CableTree
from amsn.hh import HodgkinHuxley1952, simulate_hh


def test_hh_gate_steady_state_is_finite_and_bounded():
    hh = HodgkinHuxley1952(3)
    for gate in (hh.state.m, hh.state.h, hh.state.n):
        assert np.all(np.isfinite(gate))
        assert np.all((gate >= 0.0) & (gate <= 1.0))


def test_classic_hh_single_compartment_generates_action_potential():
    # A canonical squid-axon HH smoke test; this is deliberately not a
    # human-cortical parameter set.
    length = 100e-6
    diameter = 1e-8 / (np.pi * length)
    tree = CableTree([CableCompartment("axon", length, diameter)])

    def stimulus(t):
        return np.array([1.0e-9 if 0.001 <= t < 0.002 else 0.0])

    trace = simulate_hh(tree, duration_s=0.030, dt_s=1e-5, current_fn=stimulus)
    v = trace.voltage_v[:, 0]
    assert np.max(v) > 0.080
    assert np.min(v) < -0.005
    assert np.all(np.isfinite(v))


def test_classic_hh_peak_converges_under_timestep_refinement():
    length = 100e-6
    diameter = 1e-8 / (np.pi * length)
    tree = CableTree([CableCompartment("axon", length, diameter)])
    stimulus = lambda t: np.array([1.0e-9 if 0.001 <= t < 0.002 else 0.0])
    coarse = simulate_hh(tree, 0.015, 1e-5, current_fn=stimulus)
    fine = simulate_hh(tree, 0.015, 2.5e-6, current_fn=stimulus)
    coarse_peak = int(np.argmax(coarse.voltage_v[:, 0]))
    fine_peak = int(np.argmax(fine.voltage_v[:, 0]))
    peak_error = abs(coarse.voltage_v[coarse_peak, 0] - fine.voltage_v[fine_peak, 0])
    time_error = abs(coarse.time_s[coarse_peak] - fine.time_s[fine_peak])
    assert peak_error < 0.3e-3
    assert time_error < 0.03e-3
