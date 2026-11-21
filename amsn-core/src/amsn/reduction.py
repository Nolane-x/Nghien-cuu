"""Exact passive frequency-domain Kron reduction for cable trees."""
from __future__ import annotations

from collections.abc import Sequence
from math import pi

import numpy as np

from .cable import CableTree


def schur_reduce_passive_admittance(
    tree: CableTree,
    retained_indices: Sequence[int],
    frequency_hz: float,
) -> np.ndarray:
    """Return the exact complex admittance Schur complement on retained ports.

    The full passive nodal operator is
        Y = G_axial + diag(g_membrane + j * 2*pi*f * C_membrane).

    The returned dense matrix preserves the supplied port ordering. Solving
    it with currents applied only at retained ports reproduces the full
    CableTree voltages at those ports, up to floating-point roundoff.

    Internal vertices are eliminated in reverse topological order. Because
    the original axial graph is a tree, fill-in remains limited by the
    retained boundary set. The result is frequency-dependent when membrane
    capacitance is nonzero; it is not a static resistor-tree replacement.
    """
    if not isinstance(tree, CableTree):
        raise TypeError("tree must be a CableTree")
    try:
        raw_indices = tuple(retained_indices)
    except TypeError as exc:
        raise TypeError("retained_indices must be a sequence of integer indices") from exc
    if not raw_indices:
        raise ValueError("at least one retained compartment is required")

    boundary: list[int] = []
    for value in raw_indices:
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
            raise TypeError("retained compartment indices must be integers")
        index = int(value)
        if index < 0 or index >= tree.n_compartments:
            raise IndexError(
                f"retained compartment index {index} is outside "
                f"[0, {tree.n_compartments})"
            )
        boundary.append(index)
    if len(boundary) != len(set(boundary)):
        raise ValueError("retained compartment indices must be unique")

    frequency = float(frequency_hz)
    if not np.isfinite(frequency) or frequency < 0.0:
        raise ValueError("frequency_hz must be finite and non-negative")

    n = tree.n_compartments
    omega = 2.0 * pi * frequency
    diagonal = (
        tree.membrane_leak_s.astype(np.complex128)
        + 1j * omega * tree.capacitance_f
    )
    adjacency: list[dict[int, complex]] = [dict() for _ in range(n)]

    for child in range(1, n):
        parent = int(tree.parent_index[child])
        if parent < 0 or parent >= child:
            raise ValueError("CableTree parent indices are not in topological order")
        conductance = float(tree.axial_g_s[child])
        if not np.isfinite(conductance) or conductance <= 0.0:
            raise ValueError("CableTree axial conductances must be finite and positive")
        diagonal[child] += conductance
        diagonal[parent] += conductance
        off_diagonal = complex(-conductance)
        adjacency[child][parent] = off_diagonal
        adjacency[parent][child] = off_diagonal

    retained = set(boundary)
    for node in range(n - 1, -1, -1):
        if node in retained:
            continue
        pivot = diagonal[node]
        if (
            not np.isfinite(pivot.real)
            or not np.isfinite(pivot.imag)
            or abs(pivot) == 0.0
        ):
            raise FloatingPointError(
                f"singular or non-finite Schur pivot at compartment {node}"
            )
        neighbors = sorted(adjacency[node].items())
        if not neighbors:
            raise FloatingPointError(
                f"internal compartment {node} became disconnected during reduction"
            )

        for neighbor, coupling in neighbors:
            diagonal[neighbor] -= coupling * coupling / pivot

        for left_position, (left, left_coupling) in enumerate(neighbors):
            for right, right_coupling in neighbors[left_position + 1:]:
                updated = (
                    adjacency[left].get(right, 0.0j)
                    - left_coupling * right_coupling / pivot
                )
                if updated == 0.0j:
                    adjacency[left].pop(right, None)
                    adjacency[right].pop(left, None)
                else:
                    adjacency[left][right] = updated
                    adjacency[right][left] = updated

        for neighbor, _ in neighbors:
            adjacency[neighbor].pop(node, None)
        adjacency[node].clear()

    reduced = np.zeros((len(boundary), len(boundary)), dtype=np.complex128)
    for row, node in enumerate(boundary):
        if not (np.isfinite(diagonal[node].real) and np.isfinite(diagonal[node].imag)):
            raise FloatingPointError("non-finite diagonal in reduced port matrix")
        reduced[row, row] = diagonal[node]
        for column, other in enumerate(boundary):
            if row != column:
                reduced[row, column] = adjacency[node].get(other, 0.0j)
        remaining = set(adjacency[node]).difference(retained)
        if remaining:
            raise RuntimeError(
                f"internal nodes remain connected to retained port {node}: "
                f"{sorted(remaining)[:8]}"
            )

    if not (np.all(np.isfinite(reduced.real)) and np.all(np.isfinite(reduced.imag))):
        raise FloatingPointError("non-finite values in reduced passive admittance")
    if not np.allclose(reduced, reduced.T, rtol=2e-11, atol=1e-18):
        raise FloatingPointError("Schur reduction lost complex symmetry")
    return reduced
