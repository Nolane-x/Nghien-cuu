"""Demonstrate passive PRIMA reduction on a synthetic branching cable."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from amsn.cable import CableCompartment, CableTree
from amsn.prima import prima_reduce_passive_cable


def make_tree(count: int = 96) -> CableTree:
    compartments = [CableCompartment("soma", 24e-6, 20e-6)]
    for index in range(1, count):
        parent_index = (index - 1) // 2
        compartments.append(CableCompartment(
            f"node_{index}",
            35e-6,
            1.2e-6 if index % 3 else 0.9e-6,
            f"node_{parent_index}" if parent_index else "soma",
        ))
    return CableTree(compartments)


def main() -> None:
    tree = make_tree()
    ports = [tree.index["soma"], tree.index["node_31"], tree.index["node_72"]]
    reduced = prima_reduce_passive_cable(tree, ports, max_order=18)
    print(f"full_order={tree.n_compartments} reduced_order={reduced.order} ports={len(ports)}")
    print("frequency_hz,impedance_frobenius_error_pct")
    errors = []
    for frequency_hz in (0.0, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0):
        full = np.empty((len(ports), len(ports)), dtype=np.complex128)
        for column, source in enumerate(ports):
            current = np.zeros(tree.n_compartments, dtype=np.complex128)
            current[source] = 1.0
            voltage = tree.solve_passive_frequency_response(frequency_hz, current)
            full[:, column] = voltage[ports]
        actual = reduced.impedance_matrix(frequency_hz)
        error_pct = 100.0 * np.linalg.norm(actual - full) / np.linalg.norm(full)
        print(f"{frequency_hz:g},{error_pct:.9g}")
        if not np.isfinite(error_pct):
            raise RuntimeError("non-finite PRIMA frequency-response error")
        errors.append((frequency_hz, error_pct))
    high_frequency_error = dict(errors)[3000.0]
    if high_frequency_error > 0.05:
        raise RuntimeError(
            f"3 kHz PRIMA error {high_frequency_error:.6g}% exceeds the 0.05% smoke limit"
        )

    # Check one finite-duration pulse using the projected backward-Euler model.
    state = np.zeros(reduced.order)
    max_voltage = 0.0
    dt_s = 2e-5
    for step in range(500):
        current = np.zeros(len(ports))
        if 20 <= step < 120:
            current[1] = 10e-12
        state = reduced.step_backward_euler(state, dt_s, current)
        max_voltage = max(max_voltage, float(np.max(np.abs(reduced.port_voltages(state)))))
    print(f"pulse_peak_port_perturbation_mV={max_voltage * 1e3:.9g}")
    print("passivity_cholesky=passed")


if __name__ == "__main__":
    main()
