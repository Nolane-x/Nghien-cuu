"""Research-only output-aware rational-Krylov basis enrichment.

The passive PRIMA implementation normally uses the retained current ports as
both its input selector and its observable output map. This prototype keeps the
input selector fixed while optionally adding selected output-coordinate
resolvent vectors as dual seeds in the *state basis*. The final reduced G/C
operators are still formed by the existing congruence projection, so the
prototype does not alter production code or the passive input map.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import pi
from typing import Any

import numpy as np

from amsn.cable import CableTree
from amsn.prima import (
    PassiveReducedModel,
    _orthogonalize_block,
    _project_passive_basis,
    _solve_shifted_passive_real,
)


@dataclass(frozen=True, slots=True)
class OutputAwareBasisDiagnostics:
    """Auditable seed and orthogonality diagnostics for one prototype build."""

    input_seed_columns_per_shift: tuple[int, ...]
    output_seed_columns_per_shift: tuple[int, ...]
    input_expansion_frequencies_hz: tuple[float, ...]
    output_seed_frequencies_hz: tuple[float, ...]
    retained_indices: tuple[int, ...]
    output_indices: tuple[int, ...]
    order_cap: int
    actual_order: int
    basis_orthogonality_max_abs: float

    @property
    def initial_input_seed_columns(self) -> int:
        return sum(self.input_seed_columns_per_shift)

    @property
    def initial_output_seed_columns(self) -> int:
        return sum(self.output_seed_columns_per_shift)


@dataclass(frozen=True, slots=True)
class OutputAwareReducedBasis:
    """Reduced passive input model plus separate full-compartment output rows."""

    model: PassiveReducedModel
    diagnostics: OutputAwareBasisDiagnostics

    @property
    def output_matrix(self) -> np.ndarray:
        """Return L V for the declared observation coordinates, in declared order."""
        indices = np.asarray(self.diagnostics.output_indices, dtype=np.int64)
        return self.model.basis[indices, :].copy()


def _validated_indices(
    values: Sequence[int],
    compartment_count: int,
    *,
    label: str,
) -> tuple[int, ...]:
    try:
        raw = tuple(values)
    except TypeError as exc:
        raise TypeError(f"{label} must be a sequence of integer indices") from exc
    if not raw:
        raise ValueError(f"{label} must contain at least one index")
    result: list[int] = []
    for value in raw:
        if isinstance(value, (bool, np.bool_)) or not isinstance(
            value, (int, np.integer)
        ):
            raise TypeError(f"{label} must contain only integer indices")
        index = int(value)
        if index < 0 or index >= compartment_count:
            raise IndexError(
                f"{label} index {index} is outside [0, {compartment_count})"
            )
        result.append(index)
    if len(result) != len(set(result)):
        raise ValueError(f"{label} indices must be unique")
    return tuple(result)


def _validated_frequencies(
    values: Sequence[float],
    *,
    label: str,
    allow_empty: bool,
) -> tuple[float, ...]:
    try:
        raw = tuple(values)
    except TypeError as exc:
        raise TypeError(f"{label} must be a sequence of frequencies") from exc
    if not raw and not allow_empty:
        raise ValueError(f"{label} must contain at least one frequency")
    result: list[float] = []
    for value in raw:
        if isinstance(value, (bool, np.bool_)):
            raise TypeError(f"{label} must contain real frequencies")
        frequency = float(value)
        if not np.isfinite(frequency) or frequency < 0.0:
            raise ValueError(f"{label} frequencies must be finite and non-negative")
        result.append(frequency)
    if len(result) != len(set(result)):
        raise ValueError(f"{label} frequencies must be unique")
    return tuple(result)


def _selector(compartment_count: int, indices: tuple[int, ...]) -> np.ndarray:
    value = np.zeros((compartment_count, len(indices)), dtype=np.float64)
    value[np.asarray(indices, dtype=np.int64), np.arange(len(indices))] = 1.0
    return value


def build_output_aware_passive_basis(
    tree: CableTree,
    retained_indices: Sequence[int],
    output_indices: Sequence[int],
    *,
    max_order: int,
    input_expansion_frequencies_hz: Sequence[float],
    output_seed_frequencies_hz: Sequence[float] = (),
    relative_tolerance: float = 1e-12,
) -> OutputAwareReducedBasis:
    """Build a passive basis with fixed inputs and optional dual output seeds.

    Input seeds are constructed exactly as in
    :func:`amsn.prima.prima_reduce_passive_cable_multishift`: every shifted
    input block is seeded first, then the shifted Krylov chains are grown in
    round-robin order.

    Output seeds are columns of (G + 2*pi*f*C)^-1 L.T, where L selects the
    requested observation coordinates. They are appended only after all
    initial input blocks have been seeded. Their shifted Krylov chains then
    participate in the same round-robin growth. Crucially, the final model is
    projected with the original retained input coordinates only:
    B_r = V.T B_input, while the output map is returned separately as L V.

    This is a research prototype, not a production solver. It is useful for
    testing whether a small number of output-dual seeds can improve selected
    q25 readouts without paying the initial seed cost of adding q25 to B.
    """
    if not isinstance(tree, CableTree):
        raise TypeError("tree must be a CableTree")

    retained = _validated_indices(
        retained_indices, tree.n_compartments, label="retained_indices"
    )
    outputs = _validated_indices(
        output_indices, tree.n_compartments, label="output_indices"
    )
    input_frequencies = _validated_frequencies(
        input_expansion_frequencies_hz,
        label="input_expansion_frequencies_hz",
        allow_empty=False,
    )
    output_frequencies = _validated_frequencies(
        output_seed_frequencies_hz,
        label="output_seed_frequencies_hz",
        allow_empty=True,
    )

    if isinstance(max_order, (bool, np.bool_)) or not isinstance(
        max_order, (int, np.integer)
    ):
        raise TypeError("max_order must be an integer")
    if int(max_order) <= 0:
        raise ValueError("max_order must be positive")
    order_cap = min(int(max_order), tree.n_compartments)

    tolerance = float(relative_tolerance)
    if not np.isfinite(tolerance) or not (0.0 < tolerance < 1.0):
        raise ValueError("relative_tolerance must be finite and between 0 and 1")

    input_selector = _selector(tree.n_compartments, retained)
    output_selector = _selector(tree.n_compartments, outputs)
    basis_columns: list[np.ndarray] = []
    shifted_blocks: list[tuple[float, np.ndarray]] = []
    input_seed_counts: list[int] = []
    output_seed_counts: list[int] = []

    # Preserve the existing multishift input initialization order exactly.
    for frequency in input_frequencies:
        shift = 2.0 * pi * frequency
        starting_block = _solve_shifted_passive_real(
            tree, shift, input_selector
        )
        block = _orthogonalize_block(
            starting_block, basis_columns, tolerance, order_cap
        )
        input_seed_counts.append(int(block.shape[1]))
        shifted_blocks.append((shift, block))

    if not any(input_seed_counts):
        raise FloatingPointError("failed to construct the initial input Krylov block")

    # Output-dual seed blocks are added only after every input shift has seeded.
    for frequency in output_frequencies:
        shift = 2.0 * pi * frequency
        starting_block = _solve_shifted_passive_real(
            tree, shift, output_selector
        )
        block = _orthogonalize_block(
            starting_block, basis_columns, tolerance, order_cap
        )
        output_seed_counts.append(int(block.shape[1]))
        shifted_blocks.append((shift, block))

    # One round-robin schedule is shared by primal input and dual output blocks.
    while len(basis_columns) < order_cap:
        added_any = False
        updated_blocks: list[tuple[float, np.ndarray]] = []
        for shift, block in shifted_blocks:
            if len(basis_columns) >= order_cap or block.shape[1] == 0:
                updated_blocks.append(
                    (shift, np.empty((tree.n_compartments, 0), dtype=np.float64))
                )
                continue
            candidates = _solve_shifted_passive_real(
                tree,
                shift,
                -tree.capacitance_f[:, None] * block,
            )
            following = _orthogonalize_block(
                candidates, basis_columns, tolerance, order_cap
            )
            if following.shape[1] > 0:
                added_any = True
            updated_blocks.append((shift, following))
        shifted_blocks = updated_blocks
        if not added_any:
            break

    model = _project_passive_basis(tree, retained, basis_columns)
    gram_error = model.basis.T @ model.basis - np.eye(model.order)
    orthogonality = float(np.max(np.abs(gram_error)))
    if not np.isfinite(orthogonality):
        raise FloatingPointError("non-finite output-aware basis orthogonality")

    diagnostics = OutputAwareBasisDiagnostics(
        input_seed_columns_per_shift=tuple(input_seed_counts),
        output_seed_columns_per_shift=tuple(output_seed_counts),
        input_expansion_frequencies_hz=input_frequencies,
        output_seed_frequencies_hz=output_frequencies,
        retained_indices=retained,
        output_indices=outputs,
        order_cap=order_cap,
        actual_order=model.order,
        basis_orthogonality_max_abs=orthogonality,
    )
    return OutputAwareReducedBasis(model=model, diagnostics=diagnostics)
