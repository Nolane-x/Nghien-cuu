"""Compare DC-only and positive-real multi-shift passive PRIMA models."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from amsn.cable import CableCompartment, CableTree
from amsn.prima import (
    prima_reduce_passive_cable,
    prima_reduce_passive_cable_multishift,
)


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


def full_port_impedance(tree, ports, frequency_hz):
    result = np.empty((len(ports), len(ports)), dtype=np.complex128)
    for column, source in enumerate(ports):
        current = np.zeros(tree.n_compartments, dtype=np.complex128)
        current[source] = 1.0
        result[:, column] = tree.solve_passive_frequency_response(
            frequency_hz, current
        )[ports]
    return result


def main() -> None:
    tree = make_tree()
    ports = [tree.index["soma"], tree.index["node_31"], tree.index["node_72"]]
    dc = prima_reduce_passive_cable(tree, ports, max_order=18)
    multishift = prima_reduce_passive_cable_multishift(
        tree,
        ports,
        max_order=18,
        expansion_frequencies_hz=(0.0, 100.0, 1000.0, 3000.0),
    )
    print(
        f"full_order={tree.n_compartments} dc_order={dc.order} "
        f"multishift_order={multishift.order} ports={len(ports)}"
    )
    print("frequency_hz,dc_error_pct,multishift_error_pct")
    errors = []
    for frequency_hz in (0.0, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0):
        full = full_port_impedance(tree, ports, frequency_hz)
        dc_error = 100.0 * np.linalg.norm(dc.impedance_matrix(frequency_hz) - full) / np.linalg.norm(full)
        multi_error = 100.0 * np.linalg.norm(multishift.impedance_matrix(frequency_hz) - full) / np.linalg.norm(full)
        print(f"{frequency_hz:g},{dc_error:.9g},{multi_error:.9g}")
        if not np.isfinite(dc_error + multi_error):
            raise RuntimeError("non-finite PRIMA frequency response error")
        errors.append((frequency_hz, dc_error, multi_error))

    # Both projected C and G are positive definite: the multi-shift basis
    # retains the passivity guarantee while moving error across the band.
    np.linalg.cholesky(multishift.conductance_matrix_s)
    np.linalg.cholesky(multishift.capacitance_matrix_f)
    print("multishift_passivity_cholesky=passed")
    dc_high = next(row[1] for row in errors if row[0] == 3000.0)
    multi_high = next(row[2] for row in errors if row[0] == 3000.0)
    print(f"high_frequency_error_change_pct={(multi_high-dc_high):.9g}")


if __name__ == "__main__":
    main()
