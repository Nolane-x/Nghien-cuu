import numpy as np
import pytest

from amsn.cable import CableCompartment, CableTree, PassiveParameters


def _tree():
    return CableTree([
        CableCompartment("soma", 20e-6, 20e-6, None),
        CableCompartment("dend_a", 100e-6, 2e-6, "soma"),
        CableCompartment("dend_b", 100e-6, 1.5e-6, "soma"),
        CableCompartment("branch", 80e-6, 1.0e-6, "dend_a"),
    ])


def test_single_compartment_passive_decay_matches_backward_euler_solution():
    p = PassiveParameters(e_leak_v=-0.065)
    tree = CableTree([CableCompartment("one", 100e-6, 10e-6)], p)
    v0 = -0.020
    dt = 1e-5
    duration = 1e-3
    result = tree.simulate_passive(duration, dt, initial_voltage_v=v0)
    tau = tree.capacitance_f[0] / tree.membrane_leak_s[0]
    steps = int(duration / dt)
    expected = p.e_leak_v + (v0 - p.e_leak_v) / (1.0 + dt / tau) ** steps
    assert result.voltage_v[-1, 0] == pytest.approx(expected, rel=1e-10)


def test_hines_step_matches_dense_linear_system():
    tree = _tree()
    n = tree.n_compartments
    v = np.linspace(-0.07, -0.05, n)
    gm = tree.membrane_leak_s * np.array([1.0, 1.2, 0.8, 1.4])
    reversal = np.array([-0.065, -0.060, -0.070, -0.055])
    source = gm * reversal
    current = np.array([0.0, 1e-12, 0.0, -0.2e-12])
    dt = 2e-5
    got = tree.step_linear(v, dt, gm, source, current)

    matrix = np.diag(tree.capacitance_f / dt + gm)
    for i in range(1, n):
        p = tree.parent_index[i]
        g = tree.axial_g_s[i]
        matrix[i, i] += g
        matrix[p, p] += g
        matrix[i, p] -= g
        matrix[p, i] -= g
    rhs = tree.capacitance_f / dt * v + source + current
    expected = np.linalg.solve(matrix, rhs)
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-14)


def test_passive_tree_relaxes_toward_leak_reversal():
    tree = _tree()
    result = tree.simulate_passive(0.02, 1e-4, initial_voltage_v=-0.020)
    assert np.all(np.isfinite(result.voltage_v))
    assert np.all(result.voltage_v[-1] < result.voltage_v[0])
    assert np.max(np.abs(result.voltage_v[-1] + 0.065)) < 0.01


def test_compartment_tree_rejects_disconnected_or_cyclic_graph():
    with pytest.raises(ValueError):
        CableTree([
            CableCompartment("root", 1e-5, 1e-6),
            CableCompartment("loop", 1e-5, 1e-6, "loop"),
        ])


def test_time_step_refinement_converges_for_passive_response():
    tree = _tree()
    def stimulus(t):
        values = np.zeros(tree.n_compartments)
        if 0.002 <= t < 0.006:
            values[tree.index["branch"]] = 20e-12
        return values
    coarse = tree.simulate_passive(0.012, 2e-5, current_fn=stimulus)
    fine = tree.simulate_passive(0.012, 1e-5, current_fn=stimulus)
    # Compare common sample times; backward Euler's global error should shrink.
    discrepancy = np.max(np.abs(coarse.voltage_v - fine.voltage_v[::2]))
    assert discrepancy < 2e-3


def test_swc_conversion_preserves_area_and_tapered_axial_resistance():
    from math import pi
    from amsn.morphology import SWCMorphology

    morph = SWCMorphology.from_text("""
    1 1 0 0 0 2 -1
    2 3 0 0 10 1 1
    3 3 10 0 10 0.5 2
    4 3 -10 0 10 0.75 2
    """)
    cable = morph.to_cable_tree()
    summary = morph.summary()
    assert cable.n_compartments == 4
    assert float(cable.area_m2.sum() * 1e12) == pytest.approx(
        summary.estimated_membrane_area_um2, rel=1e-12
    )

    child_index = cable.index["swc_2"]
    # The root-to-node-2 SWC edge is a 10 um linear taper from 2 to 1 um radius.
    expected_r = cable.parameters.axial_resistivity_ohm_m * (
        10e-6 / (pi * 2e-6 * 1e-6)
    )
    assert 1.0 / cable.axial_g_s[child_index] == pytest.approx(expected_r, rel=1e-12)


def test_swc_conversion_subdivides_long_edges_and_keeps_branch_topology():
    from amsn.morphology import SWCMorphology

    morph = SWCMorphology.from_text("""
    1 1 0 0 0 2 -1
    2 3 0 0 10 1 1
    3 3 10 0 10 1 2
    4 3 -10 0 10 1 2
    """)
    cable = morph.to_cable_tree(max_segment_length_um=2.5)
    # 10 um + 10 um + 10 um are each represented by four electrical links.
    assert cable.n_compartments == 13
    assert cable.n_compartments - 1 == 12
    assert np.all(cable.area_m2 > 0)
    assert np.all(cable.axial_g_s[1:] > 0)


def test_passive_parameters_reject_non_physical_values():
    with pytest.raises(ValueError):
        PassiveParameters(axial_resistivity_ohm_m=0.0)
    with pytest.raises(ValueError):
        PassiveParameters(specific_capacitance_f_m2=float("nan"))
    with pytest.raises(ValueError):
        PassiveParameters(e_leak_v=float("inf"))


def test_uniform_cable_input_resistance_matches_analytic_sealed_cable():
    from math import pi, sqrt, tanh

    def calculate_input_resistance(segment_length_m: float) -> float:
        radius = 1e-6
        total_length = 1e-3
        n_nodes = round(total_length / segment_length_m) + 1
        dx = total_length / (n_nodes - 1)
        compartments = []
        for i in range(n_nodes):
            # Vertex-centred finite-volume control volumes: terminal nodes own
            # half a segment of membrane area; interior nodes own one segment.
            area = pi * (2.0 * radius) * dx * (0.5 if i in (0, n_nodes - 1) else 1.0)
            compartments.append(CableCompartment(
                name=f"x{i}",
                length_m=dx,
                diameter_m=2.0 * radius,
                parent=None if i == 0 else f"x{i - 1}",
                membrane_area_m2=area,
                axial_geometry_factor_m_inv=(
                    None if i == 0 else dx / (pi * radius**2)
                ),
            ))
        parameters = PassiveParameters(
            specific_capacitance_f_m2=0.01,
            specific_membrane_resistance_ohm_m2=1.0,
            axial_resistivity_ohm_m=0.7,
            e_leak_v=-0.065,
        )
        tree = CableTree(compartments, parameters)
        injected = np.zeros(n_nodes)
        injected[0] = 1e-9
        voltage = tree.step_passive(np.full(n_nodes, -0.065), 1e9, injected)
        return float((voltage[0] + 0.065) / injected[0])

    radius = 1e-6
    total_length = 1e-3
    rm = 1.0
    ri = 0.7
    length_constant = sqrt(rm * radius / (2.0 * ri))
    infinite_cable_input_resistance = sqrt(rm * ri / (2.0 * pi**2 * radius**3))
    analytic = infinite_cable_input_resistance / tanh(total_length / length_constant)

    coarse_error = abs(calculate_input_resistance(20e-6) / analytic - 1.0)
    fine_error = abs(calculate_input_resistance(10e-6) / analytic - 1.0)
    assert coarse_error < 7e-5
    assert fine_error < 2e-5
    assert fine_error < coarse_error / 3.0


def _dense_frequency_response(tree, frequency_hz, injected_current_a):
    from math import pi

    omega = 2.0 * pi * frequency_hz
    matrix = np.diag(
        tree.membrane_leak_s + 1j * omega * tree.capacitance_f
    ).astype(np.complex128)
    for i in range(1, tree.n_compartments):
        parent = tree.parent_index[i]
        conductance = tree.axial_g_s[i]
        matrix[i, i] += conductance
        matrix[parent, parent] += conductance
        matrix[i, parent] -= conductance
        matrix[parent, i] -= conductance
    return np.linalg.solve(matrix, injected_current_a)


@pytest.mark.parametrize("frequency_hz", [0.0, 17.5, 100.0, 1000.0])
def test_complex_hines_frequency_response_matches_dense_linear_system(frequency_hz):
    tree = _tree()
    current = np.array(
        [1.0 + 0.2j, -0.3 + 0.1j, 0.2 - 0.4j, 0.5 + 0.0j],
        dtype=np.complex128,
    ) * 1e-12
    got = tree.solve_passive_frequency_response(frequency_hz, current)
    expected = _dense_frequency_response(tree, frequency_hz, current)
    np.testing.assert_allclose(got, expected, rtol=2e-12, atol=1e-20)


def test_zero_frequency_phasor_matches_passive_dc_perturbation():
    tree = _tree()
    current = np.zeros(tree.n_compartments)
    current[tree.index["branch"]] = 10e-12
    dc_absolute = tree.solve_passive_steady_state(current)
    phasor = tree.solve_passive_frequency_response(0.0, current)
    np.testing.assert_allclose(
        phasor, dc_absolute - tree.parameters.e_leak_v,
        rtol=2e-12, atol=1e-14,
    )


@pytest.mark.parametrize("frequency_hz", [-1.0, float("nan"), float("inf")])
def test_frequency_response_rejects_invalid_frequencies(frequency_hz):
    tree = _tree()
    with pytest.raises(ValueError):
        tree.solve_passive_frequency_response(frequency_hz)


def test_frequency_response_rejects_bad_current_shape_and_non_finite_values():
    tree = _tree()
    with pytest.raises(ValueError):
        tree.solve_passive_frequency_response(100.0, np.zeros(2))
    current = np.zeros(tree.n_compartments, dtype=np.complex128)
    current[1] = complex(float("nan"), 0.0)
    with pytest.raises(ValueError):
        tree.solve_passive_frequency_response(100.0, current)
