"""Measure reuse of a multi-shift PRIMA basis after passive parameter changes."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from amsn.cable import CableCompartment, CableTree, PassiveParameters
from amsn.prima import (
    prima_reduce_passive_cable_multishift,
    reproject_passive_cable_basis,
)


def make_tree(parameters: PassiveParameters, count: int = 96) -> CableTree:
    compartments = [CableCompartment("soma", 24e-6, 20e-6)]
    for index in range(1, count):
        parent_index = (index - 1) // 2
        compartments.append(CableCompartment(
            f"node_{index}",
            35e-6,
            1.2e-6 if index % 3 else 0.9e-6,
            f"node_{parent_index}" if parent_index else "soma",
        ))
    return CableTree(compartments, parameters)


def full_impedance(tree: CableTree, ports: list[int], frequency_hz: float) -> np.ndarray:
    result = np.empty((len(ports), len(ports)), dtype=np.complex128)
    for column, source in enumerate(ports):
        current = np.zeros(tree.n_compartments, dtype=np.complex128)
        current[source] = 1.0
        result[:, column] = tree.solve_passive_frequency_response(
            frequency_hz, current
        )[ports]
    return result


def compare_transient(tree, model, ports):
    dt_s = 0.1e-3
    total_steps = 200
    full = np.full(tree.n_compartments, tree.parameters.e_leak_v)
    state = np.zeros(model.order)
    full_current = np.zeros(tree.n_compartments)
    port_current = np.zeros(len(ports))
    full_trace = []
    reduced_trace = []
    source_port = 1
    for step in range(total_steps):
        full_current.fill(0.0)
        port_current.fill(0.0)
        t = step * dt_s
        if 2e-3 <= t < 12e-3:
            full_current[ports[source_port]] = 10e-12
            port_current[source_port] = 10e-12
        full = tree.step_passive(full, dt_s, full_current)
        state = model.step_backward_euler(state, dt_s, port_current)
        full_trace.append(full[ports] - tree.parameters.e_leak_v)
        reduced_trace.append(model.port_voltages(state))
    ref = np.asarray(full_trace)
    approx = np.asarray(reduced_trace)
    return 100.0 * np.linalg.norm(approx - ref) / max(np.linalg.norm(ref), 1e-30)


def main() -> None:
    nominal_parameters = PassiveParameters()
    nominal_tree = make_tree(nominal_parameters)
    ports = [
        nominal_tree.index["soma"],
        nominal_tree.index["node_31"],
        nominal_tree.index["node_72"],
    ]
    nominal_model = prima_reduce_passive_cable_multishift(
        nominal_tree, ports, max_order=24,
        expansion_frequencies_hz=(0.0, 100.0, 1000.0, 3000.0),
    )

    scenarios = {
        "nominal": (1.0, 1.0, 1.0),
        "Rm_minus20": (0.8, 1.0, 1.0),
        "Rm_plus20": (1.2, 1.0, 1.0),
        "Cm_minus20": (1.0, 0.8, 1.0),
        "Cm_plus20": (1.0, 1.2, 1.0),
        "Ra_minus20": (1.0, 1.0, 0.8),
        "Ra_plus20": (1.0, 1.0, 1.2),
        "all_minus20": (0.8, 0.8, 0.8),
        "all_plus20": (1.2, 1.2, 1.2),
    }
    frequencies = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
    print("scenario,relative_Rm,relative_Cm,relative_Ra,order,frozen_basis_max_Z_pct,frozen_basis_max_Y_pct,fresh_basis_max_Z_pct,fresh_basis_max_Y_pct,frozen_transient_all_ports_nrmse_pct,fresh_transient_all_ports_nrmse_pct")
    for name, (rm_scale, cm_scale, ra_scale) in scenarios.items():
        parameters = PassiveParameters(
            specific_membrane_resistance_ohm_m2=nominal_parameters.specific_membrane_resistance_ohm_m2 * rm_scale,
            specific_capacitance_f_m2=nominal_parameters.specific_capacitance_f_m2 * cm_scale,
            axial_resistivity_ohm_m=nominal_parameters.axial_resistivity_ohm_m * ra_scale,
            e_leak_v=nominal_parameters.e_leak_v,
        )
        target_tree = make_tree(parameters)
        frozen = reproject_passive_cable_basis(nominal_tree, target_tree, nominal_model)
        fresh = prima_reduce_passive_cable_multishift(
            target_tree, ports, max_order=24,
            expansion_frequencies_hz=(0.0, 100.0, 1000.0, 3000.0),
        )
        np.linalg.cholesky(frozen.conductance_matrix_s)
        np.linalg.cholesky(frozen.capacitance_matrix_f)
        frozen_z_errors = []
        frozen_y_errors = []
        fresh_z_errors = []
        fresh_y_errors = []
        for frequency_hz in frequencies:
            full_z = full_impedance(target_tree, ports, frequency_hz)
            full_y = np.linalg.solve(full_z, np.eye(len(ports)))
            frozen_z = frozen.impedance_matrix(frequency_hz)
            fresh_z = fresh.impedance_matrix(frequency_hz)
            frozen_y = np.linalg.solve(frozen_z, np.eye(len(ports)))
            fresh_y = np.linalg.solve(fresh_z, np.eye(len(ports)))
            denom_z = max(np.linalg.norm(full_z), 1e-30)
            denom_y = max(np.linalg.norm(full_y), 1e-30)
            frozen_z_errors.append(100.0 * np.linalg.norm(frozen_z - full_z) / denom_z)
            frozen_y_errors.append(100.0 * np.linalg.norm(frozen_y - full_y) / denom_y)
            fresh_z_errors.append(100.0 * np.linalg.norm(fresh_z - full_z) / denom_z)
            fresh_y_errors.append(100.0 * np.linalg.norm(fresh_y - full_y) / denom_y)
        frozen_transient = compare_transient(target_tree, frozen, ports)
        fresh_transient = compare_transient(target_tree, fresh, ports)
        values = (
            name, rm_scale, cm_scale, ra_scale, frozen.order,
            max(frozen_z_errors), max(frozen_y_errors),
            max(fresh_z_errors), max(fresh_y_errors),
            frozen_transient, fresh_transient,
        )
        print(",".join(str(x) if isinstance(x, str) else f"{x:.10g}" for x in values))
        if not np.all(np.isfinite(np.asarray(values[1:], dtype=float))):
            raise RuntimeError(f"non-finite parameter robustness result for {name}")
    print("frozen_basis_passivity=passed")


if __name__ == "__main__":
    main()
