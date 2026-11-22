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


def test_frequency_phasor_matches_time_domain_sinusoidal_steady_state():
    tree = _tree()
    frequency_hz = 50.0
    angular_frequency = 2.0 * np.pi * frequency_hz
    dt_s = 5e-6
    duration_s = 0.25
    current_amplitude_a = 20e-12
    source_index = tree.index["branch"]
    current_phasor = np.zeros(tree.n_compartments, dtype=np.complex128)
    current_phasor[source_index] = current_amplitude_a
    expected = tree.solve_passive_frequency_response(
        frequency_hz, current_phasor
    )

    def sinusoidal_current(time_s):
        current = np.zeros(tree.n_compartments)
        current[source_index] = (
            current_amplitude_a * np.cos(angular_frequency * time_s)
        )
        return current

    trace = tree.simulate_passive(
        duration_s,
        dt_s,
        current_fn=sinusoidal_current,
        initial_voltage_v=tree.parameters.e_leak_v,
    )

    # simulate_passive applies the left-edge current to the following step.
    # Fit the last five cycles against that sampled input-time convention.
    mask = trace.time_s >= duration_s - 5.0 / frequency_hz
    fit_time = trace.time_s[mask] - dt_s
    samples = trace.voltage_v[mask, source_index] - tree.parameters.e_leak_v
    design = np.column_stack([
        np.cos(angular_frequency * fit_time),
        np.sin(angular_frequency * fit_time),
        np.ones_like(fit_time),
    ])
    coefficients, *_ = np.linalg.lstsq(design, samples, rcond=None)
    observed = complex(coefficients[0], -coefficients[1])
    relative_error = abs(observed - expected[source_index]) / abs(
        expected[source_index]
    )

    # Backward-Euler discretization at 5 us contributes a small, known
    # O(omega*dt) difference from the continuous-time phasor solution.
    assert relative_error < 2e-3


@pytest.mark.parametrize("frequency_hz", [0.0, 17.5, 100.0, 3000.0])
def test_schur_reduced_admittance_matches_dense_schur_complement(frequency_hz):
    from amsn.reduction import schur_reduce_passive_admittance

    tree = _tree()
    boundary = [tree.index["branch"], tree.index["soma"], tree.index["dend_b"]]
    internal = [i for i in range(tree.n_compartments) if i not in boundary]
    dense = np.diag(
        tree.membrane_leak_s + 1j * 2.0 * np.pi * frequency_hz * tree.capacitance_f
    ).astype(np.complex128)
    for child in range(1, tree.n_compartments):
        parent = tree.parent_index[child]
        conductance = tree.axial_g_s[child]
        dense[child, child] += conductance
        dense[parent, parent] += conductance
        dense[child, parent] -= conductance
        dense[parent, child] -= conductance

    if internal:
        a_bb = dense[np.ix_(boundary, boundary)]
        a_bi = dense[np.ix_(boundary, internal)]
        a_ib = dense[np.ix_(internal, boundary)]
        a_ii = dense[np.ix_(internal, internal)]
        expected = a_bb - a_bi @ np.linalg.solve(a_ii, a_ib)
    else:
        expected = dense[np.ix_(boundary, boundary)]

    reduced = schur_reduce_passive_admittance(tree, boundary, frequency_hz)
    np.testing.assert_allclose(reduced, expected, rtol=2e-12, atol=1e-18)
    np.testing.assert_allclose(reduced, reduced.T, rtol=2e-12, atol=1e-18)


@pytest.mark.parametrize("frequency_hz", [0.0, 50.0, 1000.0])
def test_schur_reduced_ports_reproduce_full_tree_boundary_voltage(frequency_hz):
    from amsn.reduction import schur_reduce_passive_admittance

    tree = _tree()
    boundary = [tree.index["branch"], tree.index["soma"], tree.index["dend_b"]]
    port_current = np.array(
        [0.8 + 0.2j, -0.3 + 0.1j, 0.4 - 0.5j], dtype=np.complex128
    ) * 1e-12
    full_current = np.zeros(tree.n_compartments, dtype=np.complex128)
    full_current[boundary] = port_current
    full_voltage = tree.solve_passive_frequency_response(frequency_hz, full_current)
    reduced = schur_reduce_passive_admittance(tree, boundary, frequency_hz)
    reduced_voltage = np.linalg.solve(reduced, port_current)
    np.testing.assert_allclose(
        reduced_voltage, full_voltage[boundary], rtol=2e-11, atol=1e-17
    )


def test_schur_reduction_all_ports_matches_full_admittance():
    from amsn.reduction import schur_reduce_passive_admittance

    tree = _tree()
    boundary = list(range(tree.n_compartments))
    frequency_hz = 123.0
    reduced = schur_reduce_passive_admittance(tree, boundary, frequency_hz)
    expected = np.diag(
        tree.membrane_leak_s + 1j * 2.0 * np.pi * frequency_hz * tree.capacitance_f
    ).astype(np.complex128)
    for child in range(1, tree.n_compartments):
        parent = tree.parent_index[child]
        conductance = tree.axial_g_s[child]
        expected[child, child] += conductance
        expected[parent, parent] += conductance
        expected[child, parent] -= conductance
        expected[parent, child] -= conductance
    np.testing.assert_allclose(reduced, expected, rtol=1e-13, atol=1e-18)


def test_schur_reduction_rejects_invalid_retained_ports():
    from amsn.reduction import schur_reduce_passive_admittance

    tree = _tree()
    with pytest.raises(ValueError):
        schur_reduce_passive_admittance(tree, [], 10.0)
    with pytest.raises(ValueError):
        schur_reduce_passive_admittance(tree, [0, 0], 10.0)
    with pytest.raises(TypeError):
        schur_reduce_passive_admittance(tree, [0, 1.5], 10.0)
    with pytest.raises(IndexError):
        schur_reduce_passive_admittance(tree, [tree.n_compartments], 10.0)
    with pytest.raises(ValueError):
        schur_reduce_passive_admittance(tree, [0], -1.0)


def _full_port_impedance(tree, ports, frequency_hz):
    impedance = np.empty((len(ports), len(ports)), dtype=np.complex128)
    for column, source in enumerate(ports):
        current = np.zeros(tree.n_compartments, dtype=np.complex128)
        current[source] = 1.0
        voltage = tree.solve_passive_frequency_response(frequency_hz, current)
        impedance[:, column] = voltage[ports]
    return impedance


def test_prima_reduction_matches_full_tree_dc_port_impedance():
    from amsn.prima import prima_reduce_passive_cable

    tree = _tree()
    ports = [tree.index["soma"], tree.index["branch"]]
    reduced = prima_reduce_passive_cable(tree, ports, max_order=2)
    assert reduced.order <= 2
    expected = _full_port_impedance(tree, ports, 0.0)
    np.testing.assert_allclose(
        reduced.impedance_matrix(0.0), expected, rtol=2e-10, atol=1e-10
    )


def test_prima_full_order_projection_matches_complex_port_response():
    from amsn.prima import prima_reduce_passive_cable

    tree = _tree()
    ports = list(range(tree.n_compartments))
    reduced = prima_reduce_passive_cable(tree, ports, max_order=tree.n_compartments)
    assert reduced.order == tree.n_compartments
    for frequency_hz in (0.0, 17.5, 1000.0):
        expected = _full_port_impedance(tree, ports, frequency_hz)
        np.testing.assert_allclose(
            reduced.impedance_matrix(frequency_hz),
            expected,
            rtol=2e-10,
            atol=2e-10,
        )


def test_prima_projected_matrices_are_passive_and_stable():
    from amsn.prima import prima_reduce_passive_cable

    tree = _tree()
    ports = [tree.index["soma"], tree.index["dend_a"], tree.index["branch"]]
    reduced = prima_reduce_passive_cable(tree, ports, max_order=3)
    np.testing.assert_allclose(
        reduced.conductance_matrix_s,
        reduced.conductance_matrix_s.T,
        rtol=1e-12,
        atol=1e-18,
    )
    np.testing.assert_allclose(
        reduced.capacitance_matrix_f,
        reduced.capacitance_matrix_f.T,
        rtol=1e-12,
        atol=1e-24,
    )
    np.linalg.cholesky(reduced.conductance_matrix_s)
    np.linalg.cholesky(reduced.capacitance_matrix_f)
    rates = np.linalg.eigvals(
        np.linalg.solve(
            reduced.capacitance_matrix_f, reduced.conductance_matrix_s
        )
    )
    assert np.all(rates.real > 0.0)
    assert np.max(np.abs(rates.imag)) < 1e-7 * np.max(rates.real)


def test_prima_backward_euler_step_matches_full_order_hines_step():
    from amsn.prima import prima_reduce_passive_cable

    tree = _tree()
    ports = list(range(tree.n_compartments))
    reduced = prima_reduce_passive_cable(tree, ports, max_order=tree.n_compartments)
    current = np.array([0.2, -0.1, 0.4, 0.7], dtype=float) * 1e-12
    dt_s = 2e-5
    state = np.zeros(reduced.order)
    next_state = reduced.step_backward_euler(state, dt_s, current)
    reduced_voltage = reduced.basis @ next_state

    full_current = np.zeros(tree.n_compartments)
    full_current[ports] = current
    reversal = tree.parameters.e_leak_v
    full_voltage = tree.step_linear(
        np.full(tree.n_compartments, reversal),
        dt_s,
        tree.membrane_leak_s,
        tree.membrane_leak_s * reversal,
        full_current,
    )
    np.testing.assert_allclose(
        reduced_voltage, full_voltage - reversal, rtol=2e-10, atol=1e-14
    )


def test_prima_reduction_rejects_invalid_configuration_and_inputs():
    from amsn.prima import prima_reduce_passive_cable

    tree = _tree()
    with pytest.raises(ValueError):
        prima_reduce_passive_cable(tree, [])
    with pytest.raises(ValueError):
        prima_reduce_passive_cable(tree, [0, 0])
    with pytest.raises(TypeError):
        prima_reduce_passive_cable(tree, [0, 1.5])
    with pytest.raises(IndexError):
        prima_reduce_passive_cable(tree, [tree.n_compartments])
    with pytest.raises(ValueError):
        prima_reduce_passive_cable(tree, [0], max_order=0)
    with pytest.raises(ValueError):
        prima_reduce_passive_cable(tree, [0], relative_tolerance=1.0)

    reduced = prima_reduce_passive_cable(tree, [0], max_order=2)
    with pytest.raises(ValueError):
        reduced.impedance_matrix(-1.0)
    with pytest.raises(ValueError):
        reduced.step_backward_euler(np.zeros(reduced.order), 0.0, np.zeros(1))
    with pytest.raises(ValueError):
        reduced.step_backward_euler(np.zeros(reduced.order), 1e-4, np.zeros(2))
    with pytest.raises(ValueError):
        reduced.port_voltages(np.zeros(reduced.order + 1))


def _dense_shifted_passive_matrix(tree, shift_per_s):
    matrix = np.diag(
        tree.membrane_leak_s + shift_per_s * tree.capacitance_f
    ).astype(float)
    for child in range(1, tree.n_compartments):
        parent = tree.parent_index[child]
        conductance = tree.axial_g_s[child]
        matrix[child, child] += conductance
        matrix[parent, parent] += conductance
        matrix[child, parent] -= conductance
        matrix[parent, child] -= conductance
    return matrix


def test_multishift_hines_solver_matches_dense_positive_real_shift():
    from amsn.prima import _solve_shifted_passive_real

    tree = _tree()
    shift = 2.0 * np.pi * 3000.0
    rhs = np.column_stack([
        np.array([1.0, -0.2, 0.3, 0.8]) * 1e-12,
        np.array([-0.4, 0.7, 0.2, -0.1]) * 1e-12,
    ])
    got = _solve_shifted_passive_real(tree, shift, rhs)
    expected = np.linalg.solve(_dense_shifted_passive_matrix(tree, shift), rhs)
    np.testing.assert_allclose(got, expected, rtol=2e-12, atol=1e-20)


def test_multishift_prima_full_order_matches_full_complex_port_response():
    from amsn.prima import prima_reduce_passive_cable_multishift

    tree = _tree()
    ports = list(range(tree.n_compartments))
    reduced = prima_reduce_passive_cable_multishift(
        tree,
        ports,
        max_order=tree.n_compartments,
        expansion_frequencies_hz=(0.0, 100.0, 3000.0),
    )
    assert reduced.order == tree.n_compartments
    for frequency_hz in (0.0, 17.5, 1000.0, 3000.0):
        expected = _full_port_impedance(tree, ports, frequency_hz)
        np.testing.assert_allclose(
            reduced.impedance_matrix(frequency_hz),
            expected,
            rtol=2e-10,
            atol=2e-10,
        )


def test_multishift_prima_projection_remains_passive_and_stable():
    from amsn.prima import prima_reduce_passive_cable_multishift

    tree = _tree()
    ports = [tree.index["soma"], tree.index["dend_a"], tree.index["branch"]]
    reduced = prima_reduce_passive_cable_multishift(
        tree, ports, max_order=3, expansion_frequencies_hz=(0.0, 1000.0, 3000.0)
    )
    assert reduced.order == 3
    np.linalg.cholesky(reduced.conductance_matrix_s)
    np.linalg.cholesky(reduced.capacitance_matrix_f)
    rates = np.linalg.eigvals(
        np.linalg.solve(reduced.capacitance_matrix_f, reduced.conductance_matrix_s)
    )
    assert np.all(rates.real > 0.0)


def test_multishift_prima_rejects_invalid_expansion_points():
    from amsn.prima import prima_reduce_passive_cable_multishift

    tree = _tree()
    with pytest.raises(ValueError):
        prima_reduce_passive_cable_multishift(tree, [0], expansion_frequencies_hz=[])
    with pytest.raises(ValueError):
        prima_reduce_passive_cable_multishift(tree, [0], expansion_frequencies_hz=(-1.0,))
    with pytest.raises(ValueError):
        prima_reduce_passive_cable_multishift(tree, [0], expansion_frequencies_hz=(0.0, 0.0))
    with pytest.raises(ValueError):
        prima_reduce_passive_cable_multishift(tree, [0], expansion_frequencies_hz=(float("nan"),))
    with pytest.raises(TypeError):
        prima_reduce_passive_cable_multishift(tree, [0], expansion_frequencies_hz=(True,))


@pytest.mark.parametrize("max_order", [2, 3, 4])
def test_multishift_prima_extended_order_sweep_preserves_passivity(max_order):
    from amsn.prima import prima_reduce_passive_cable_multishift

    tree = _tree()
    ports = [tree.index["soma"], tree.index["dend_a"], tree.index["branch"]]
    reduced = prima_reduce_passive_cable_multishift(
        tree,
        ports,
        max_order=max_order,
        expansion_frequencies_hz=(0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0),
    )

    assert 0 < reduced.order <= max_order
    np.linalg.cholesky(reduced.conductance_matrix_s)
    np.linalg.cholesky(reduced.capacitance_matrix_f)
    np.testing.assert_allclose(
        reduced.conductance_matrix_s,
        reduced.conductance_matrix_s.T,
        rtol=1e-12,
        atol=1e-18,
    )
    np.testing.assert_allclose(
        reduced.capacitance_matrix_f,
        reduced.capacitance_matrix_f.T,
        rtol=1e-12,
        atol=1e-24,
    )
    for frequency_hz in (0.0, 100.0, 3000.0, 6000.0, 10000.0):
        impedance = reduced.impedance_matrix(frequency_hz)
        assert np.all(np.isfinite(impedance.real))
        assert np.all(np.isfinite(impedance.imag))
        np.testing.assert_allclose(impedance, impedance.T, rtol=2e-10, atol=1e-10)

    for source_port in range(reduced.port_count):
        current = np.zeros(reduced.port_count, dtype=float)
        current[source_port] = 10e-12
        next_state = reduced.step_backward_euler(
            np.zeros(reduced.order), 0.1e-3, current
        )
        assert np.all(np.isfinite(next_state))
        assert np.all(np.isfinite(reduced.port_voltages(next_state)))


def _tree_with_parameters(tree, parameters):
    return CableTree(
        [tree.by_name[name] for name in tree.order],
        parameters,
    )


def test_passive_prima_basis_reprojection_matches_reference_when_parameters_unchanged():
    from amsn.prima import (
        prima_reduce_passive_cable_multishift,
        reproject_passive_cable_basis,
    )

    tree = _tree()
    ports = [tree.index["soma"], tree.index["dend_a"], tree.index["branch"]]
    original = prima_reduce_passive_cable_multishift(
        tree, ports, max_order=3, expansion_frequencies_hz=(0.0, 300.0)
    )
    reprojected = reproject_passive_cable_basis(tree, tree, original)
    np.testing.assert_allclose(reprojected.basis, original.basis, rtol=0.0, atol=0.0)
    for frequency_hz in (0.0, 100.0, 3000.0):
        np.testing.assert_allclose(
            reprojected.impedance_matrix(frequency_hz),
            original.impedance_matrix(frequency_hz),
            rtol=1e-13,
            atol=1e-12,
        )


@pytest.mark.parametrize(
    "parameters",
    [
        PassiveParameters(specific_membrane_resistance_ohm_m2=0.8),
        PassiveParameters(specific_membrane_resistance_ohm_m2=1.2),
        PassiveParameters(specific_capacitance_f_m2=0.008),
        PassiveParameters(specific_capacitance_f_m2=0.012),
        PassiveParameters(axial_resistivity_ohm_m=0.56),
        PassiveParameters(axial_resistivity_ohm_m=0.84),
        PassiveParameters(
            specific_capacitance_f_m2=0.012,
            specific_membrane_resistance_ohm_m2=0.8,
            axial_resistivity_ohm_m=0.84,
        ),
    ],
)
def test_passive_prima_basis_reprojection_stays_passive_under_parameter_variation(parameters):
    from amsn.prima import (
        prima_reduce_passive_cable_multishift,
        reproject_passive_cable_basis,
    )

    tree = _tree()
    perturbed = _tree_with_parameters(tree, parameters)
    ports = [tree.index["soma"], tree.index["dend_a"], tree.index["branch"]]
    original = prima_reduce_passive_cable_multishift(
        tree, ports, max_order=3, expansion_frequencies_hz=(0.0, 300.0)
    )
    reprojected = reproject_passive_cable_basis(tree, perturbed, original)
    assert reprojected.order == original.order
    np.linalg.cholesky(reprojected.conductance_matrix_s)
    np.linalg.cholesky(reprojected.capacitance_matrix_f)
    for frequency_hz in (0.0, 100.0, 3000.0):
        impedance = reprojected.impedance_matrix(frequency_hz)
        assert np.all(np.isfinite(impedance.real))
        assert np.all(np.isfinite(impedance.imag))


def test_passive_prima_basis_reprojection_rejects_geometry_or_topology_change():
    from amsn.prima import (
        prima_reduce_passive_cable_multishift,
        reproject_passive_cable_basis,
    )

    tree = _tree()
    ports = [tree.index["soma"], tree.index["dend_a"]]
    model = prima_reduce_passive_cable_multishift(
        tree, ports, max_order=2, expansion_frequencies_hz=(0.0, 100.0)
    )
    changed_geometry = CableTree([
        CableCompartment("soma", 20e-6, 20e-6),
        CableCompartment("dend_a", 100e-6, 2.2e-6, "soma"),
        CableCompartment("dend_b", 100e-6, 1.5e-6, "soma"),
        CableCompartment("branch", 80e-6, 1.0e-6, "dend_a"),
    ])
    changed_topology = CableTree([
        CableCompartment("soma", 20e-6, 20e-6),
        CableCompartment("dend_a", 100e-6, 2e-6, "soma"),
        CableCompartment("dend_b", 100e-6, 1.5e-6, "dend_a"),
        CableCompartment("branch", 80e-6, 1.0e-6, "soma"),
    ])
    with pytest.raises(ValueError):
        reproject_passive_cable_basis(tree, changed_geometry, model)
    with pytest.raises(ValueError):
        reproject_passive_cable_basis(tree, changed_topology, model)
