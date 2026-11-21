"""Matched-support full passive admittance operator comparison for Segev cells.

This audit consumes three independently validated ingredients written in the
same workflow:
- AMSN and NEURON reduced axial edge conductances on a shared electrical SWC graph;
- AMSN CableTree and NEURON segment-area support on the same electrical nodes;
- fixed specific membrane resistance/capacitance applied to those matched node
  control volumes.

It compares the complex passive admittance operator
    Y(omega) = L_axial + diag(A/Rm + j*omega*Cm*A)
on the shared node support. It reports axial, leak, capacitance and combined
operator actions separately for deterministic complex voltage probes.

Important scope: this is a matched-support finite-volume operator assembled
from the validated reduced axial graph and projected NEURON segment-area
support. It is not an exact Schur complement of the original fine NEURON
segment-level matrix, nor a biological validation.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np


MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
RANDOM_SEED = 20261121
RANDOM_VOLTAGE_CASES = 32
RANDOM_VOLTAGE_STD_V = 0.010
FREQUENCIES_HZ = (0.0, 0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0)


def read_dict_csv(path: Path, key_columns: tuple[str, ...] = ()) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"required matched-support CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise RuntimeError(f"required matched-support CSV is empty: {path}")
    if key_columns:
        seen = set()
        for row in rows:
            key = tuple(row[column] for column in key_columns)
            if key in seen:
                raise RuntimeError(f"duplicate key {key} in {path}")
            seen.add(key)
    return rows


def relative_l2(values: np.ndarray, reference: np.ndarray) -> float:
    return float(np.linalg.norm(values - reference) / max(np.linalg.norm(reference), 1e-300))


def percentile_summary(values: list[float]) -> tuple[float, float, float, float]:
    array = np.asarray(values, dtype=float)
    return (
        float(np.median(array)),
        float(np.percentile(array, 95)),
        float(np.percentile(array, 99)),
        float(np.max(array)),
    )


def apply_tree_operator(
    voltage: np.ndarray,
    parent_index: np.ndarray,
    child_index: np.ndarray,
    conductance_s: np.ndarray,
    diagonal_admittance_s: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return total and axial current vectors for one sparse tree Laplacian."""
    axial = np.zeros_like(voltage, dtype=np.complex128)
    for parent, child, conductance in zip(parent_index, child_index, conductance_s):
        current = conductance * (voltage[parent] - voltage[child])
        axial[parent] += current
        axial[child] -= current
    total = axial + diagonal_admittance_s * voltage
    return total, axial


def main() -> None:
    results_dir = Path(__file__).parents[1] / "results"
    prefix = "" if MORPHOLOGY_LABEL == "NMO_290988" else f"{MORPHOLOGY_LABEL}_"
    area_path = results_dir / f"{prefix}human_membrane_area_control_volumes_2026-11-21.csv"
    edge_path = results_dir / f"{prefix}human_full_tree_axial_matrix_edges_2026-11-21.csv"

    area_rows = read_dict_csv(area_path, ("electrical_node_id",))
    edge_rows = read_dict_csv(
        edge_path, ("amsn_parent_electrical_node", "amsn_child_electrical_node")
    )

    node_ids = [int(row["electrical_node_id"]) for row in area_rows]
    if len(node_ids) != len(set(node_ids)):
        raise RuntimeError("duplicate electrical node IDs in area support CSV")
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    node_count = len(node_ids)
    if len(edge_rows) != node_count - 1:
        raise RuntimeError(
            f"expected a tree with {node_count - 1} edges, found {len(edge_rows)}"
        )

    amsn_area_m2 = np.asarray([
        float(row["amsn_control_volume_area_um2"]) * 1e-12
        for row in area_rows
    ], dtype=float)
    neuron_area_m2 = np.asarray([
        float(row["neuron_segment_area_support_um2"]) * 1e-12
        for row in area_rows
    ], dtype=float)
    if (
        not np.all(np.isfinite(amsn_area_m2))
        or not np.all(np.isfinite(neuron_area_m2))
        or np.any(amsn_area_m2 <= 0)
        or np.any(neuron_area_m2 <= 0)
    ):
        raise RuntimeError("invalid membrane-area control-volume support")

    parent_index = []
    child_index = []
    amsn_g = []
    neuron_g = []
    edge_key_set = set()
    union_parent = list(range(node_count))

    def find(x):
        while union_parent[x] != x:
            union_parent[x] = union_parent[union_parent[x]]
            x = union_parent[x]
        return x

    for row in edge_rows:
        parent_id = int(row["amsn_parent_electrical_node"])
        child_id = int(row["amsn_child_electrical_node"])
        if parent_id not in node_index or child_id not in node_index:
            raise RuntimeError(f"edge references a node absent from area support: {parent_id}->{child_id}")
        key = (parent_id, child_id)
        if key in edge_key_set:
            raise RuntimeError(f"duplicate axial edge in matrix CSV: {key}")
        edge_key_set.add(key)
        p = node_index[parent_id]
        c = node_index[child_id]
        root_p = find(p)
        root_c = find(c)
        if root_p == root_c:
            raise RuntimeError(f"cycle detected in reduced axial graph at edge {key}")
        union_parent[root_p] = root_c
        parent_index.append(p)
        child_index.append(c)
        amsn_g.append(float(row["amsn_axial_conductance_s"]))
        neuron_g.append(float(row["neuron_ri_network_axial_conductance_s"]))

    if len({find(i) for i in range(node_count)}) != 1:
        raise RuntimeError("reduced axial graph is disconnected")
    parent_index = np.asarray(parent_index, dtype=np.int64)
    child_index = np.asarray(child_index, dtype=np.int64)
    amsn_g = np.asarray(amsn_g, dtype=float)
    neuron_g = np.asarray(neuron_g, dtype=float)
    if (
        not np.all(np.isfinite(amsn_g))
        or not np.all(np.isfinite(neuron_g))
        or np.any(amsn_g <= 0)
        or np.any(neuron_g <= 0)
    ):
        raise RuntimeError("invalid axial conductances")

    # Matched-support diagonal membrane terms. Specific values are identical;
    # only the independently audited area support differs between engines.
    amsn_leak_s = amsn_area_m2 / RM_OHM_M2
    neuron_leak_s = neuron_area_m2 / RM_OHM_M2
    amsn_cap_f = CM_F_M2 * amsn_area_m2
    neuron_cap_f = CM_F_M2 * neuron_area_m2

    rng = np.random.default_rng(RANDOM_SEED)
    voltage_vectors = (
        rng.normal(size=(RANDOM_VOLTAGE_CASES, node_count))
        + 1j * rng.normal(size=(RANDOM_VOLTAGE_CASES, node_count))
    ) * (RANDOM_VOLTAGE_STD_V / np.sqrt(2.0))

    edge_error_pct = 100.0 * np.abs(neuron_g - amsn_g) / np.maximum(np.abs(amsn_g), 1e-300)
    leak_error_pct = 100.0 * np.abs(neuron_leak_s - amsn_leak_s) / np.maximum(np.abs(amsn_leak_s), 1e-300)
    cap_error_pct = 100.0 * np.abs(neuron_cap_f - amsn_cap_f) / np.maximum(np.abs(amsn_cap_f), 1e-300)
    area_error_pct = 100.0 * np.abs(neuron_area_m2 - amsn_area_m2) / np.maximum(np.abs(amsn_area_m2), 1e-300)

    rows = []
    constant_voltage_residuals = []
    axial_conservation_residuals = []
    for frequency_hz in FREQUENCIES_HZ:
        omega = 2.0 * np.pi * frequency_hz
        amsn_diag = amsn_leak_s + 1j * omega * amsn_cap_f
        neuron_diag = neuron_leak_s + 1j * omega * neuron_cap_f

        total_errors = []
        axial_errors = []
        leak_errors = []
        cap_errors = []
        max_abs_current_difference = 0.0
        max_total_current_conservation = 0.0
        max_axial_current_conservation = 0.0

        for voltage in voltage_vectors:
            amsn_total, amsn_axial = apply_tree_operator(
                voltage, parent_index, child_index, amsn_g, amsn_diag
            )
            neuron_total, neuron_axial = apply_tree_operator(
                voltage, parent_index, child_index, neuron_g, neuron_diag
            )
            amsn_leak = amsn_leak_s * voltage
            neuron_leak = neuron_leak_s * voltage
            amsn_cap = 1j * omega * amsn_cap_f * voltage
            neuron_cap = 1j * omega * neuron_cap_f * voltage

            total_errors.append(relative_l2(neuron_total, amsn_total))
            axial_errors.append(relative_l2(neuron_axial, amsn_axial))
            leak_errors.append(relative_l2(neuron_leak, amsn_leak))
            if frequency_hz > 0:
                cap_errors.append(relative_l2(neuron_cap, amsn_cap))
            max_abs_current_difference = max(
                max_abs_current_difference,
                float(np.max(np.abs(neuron_total - amsn_total))),
            )
            max_total_current_conservation = max(
                max_total_current_conservation,
                abs(float(np.real(np.sum(amsn_axial)))),
                abs(float(np.imag(np.sum(amsn_axial)))),
                abs(float(np.real(np.sum(neuron_axial)))),
                abs(float(np.imag(np.sum(neuron_axial)))),
            )
            max_axial_current_conservation = max(
                max_axial_current_conservation,
                abs(float(np.sum(amsn_axial))),
                abs(float(np.sum(neuron_axial))),
            )

        # Constant voltage must produce no axial current in either graph.
        constant_voltage = np.full(node_count, 0.010 + 0j, dtype=np.complex128)
        _, amsn_constant_axial = apply_tree_operator(
            constant_voltage, parent_index, child_index, amsn_g, amsn_diag
        )
        _, neuron_constant_axial = apply_tree_operator(
            constant_voltage, parent_index, child_index, neuron_g, neuron_diag
        )
        constant_residual = max(
            float(np.max(np.abs(amsn_constant_axial))),
            float(np.max(np.abs(neuron_constant_axial))),
        )
        constant_voltage_residuals.append(constant_residual)
        axial_conservation_residuals.append(max_axial_current_conservation)

        total_stats = percentile_summary(total_errors)
        axial_stats = percentile_summary(axial_errors)
        leak_stats = percentile_summary(leak_errors)
        cap_stats = percentile_summary(cap_errors) if cap_errors else (0.0, 0.0, 0.0, 0.0)
        rows.append({
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "frequency_hz": frequency_hz,
            "random_voltage_cases": RANDOM_VOLTAGE_CASES,
            "seed": RANDOM_SEED,
            "voltage_std_mV": RANDOM_VOLTAGE_STD_V * 1000.0,
            "specific_Rm_ohm_m2": RM_OHM_M2,
            "specific_Cm_F_m2": CM_F_M2,
            "Eleak_mV": ELEAK_MV,
            "passive_operator_relative_L2_median": total_stats[0],
            "passive_operator_relative_L2_p95": total_stats[1],
            "passive_operator_relative_L2_p99": total_stats[2],
            "passive_operator_relative_L2_max": total_stats[3],
            "axial_operator_relative_L2_median": axial_stats[0],
            "axial_operator_relative_L2_p95": axial_stats[1],
            "axial_operator_relative_L2_max": axial_stats[3],
            "leak_diagonal_relative_L2_median": leak_stats[0],
            "leak_diagonal_relative_L2_p95": leak_stats[1],
            "leak_diagonal_relative_L2_max": leak_stats[3],
            "capacitance_diagonal_relative_L2_median": cap_stats[0],
            "capacitance_diagonal_relative_L2_p95": cap_stats[1],
            "capacitance_diagonal_relative_L2_max": cap_stats[3],
            "edge_conductance_abs_median_pct": float(np.median(edge_error_pct)),
            "edge_conductance_abs_p95_pct": float(np.percentile(edge_error_pct, 95)),
            "edge_conductance_abs_max_pct": float(np.max(edge_error_pct)),
            "node_area_abs_median_pct": float(np.median(area_error_pct)),
            "node_area_abs_p95_pct": float(np.percentile(area_error_pct, 95)),
            "node_area_abs_max_pct": float(np.max(area_error_pct)),
            "node_leak_abs_max_pct": float(np.max(leak_error_pct)),
            "node_capacitance_abs_max_pct": float(np.max(cap_error_pct)),
            "max_absolute_node_current_difference_a": max_abs_current_difference,
            "max_axial_total_current_conservation_residual_a": max_total_current_conservation,
            "constant_voltage_axial_nullspace_residual_a": constant_residual,
        })

    out_path = results_dir / f"{prefix}human_full_tree_passive_admittance_operator_2026-11-21.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"morphology={MORPHOLOGY_LABEL}; nodes={node_count}; edges={len(edge_rows)}")
    print(
        f"NEURON_max_segment_um={NEURON_MAX_SEGMENT_UM}; "
        f"Rm_ohm_m2={RM_OHM_M2}; Cm_F_m2={CM_F_M2}; Eleak_mV={ELEAK_MV}"
    )
    print(
        f"edge_conductance_abs_median_p95_max_pct="
        f"{np.median(edge_error_pct):.12g},{np.percentile(edge_error_pct,95):.12g},{np.max(edge_error_pct):.12g}"
    )
    print(
        f"node_area_abs_median_p95_max_pct="
        f"{np.median(area_error_pct):.12g},{np.percentile(area_error_pct,95):.12g},{np.max(area_error_pct):.12g}"
    )
    print(
        f"leak_diagonal_abs_max_pct={np.max(leak_error_pct):.12g}; "
        f"capacitance_diagonal_abs_max_pct={np.max(cap_error_pct):.12g}"
    )
    for row in rows:
        print(
            f"frequency_hz={row['frequency_hz']:g}; "
            f"passive_operator_relative_L2_median_p95_max="
            f"{row['passive_operator_relative_L2_median']:.12g},"
            f"{row['passive_operator_relative_L2_p95']:.12g},"
            f"{row['passive_operator_relative_L2_max']:.12g}; "
            f"axial_max={row['axial_operator_relative_L2_max']:.12g}; "
            f"leak_max={row['leak_diagonal_relative_L2_max']:.12g}; "
            f"cap_max={row['capacitance_diagonal_relative_L2_max']:.12g}"
        )
    print(
        f"max_axial_current_conservation_residual_a={max(axial_conservation_residuals):.12g}; "
        f"max_constant_voltage_nullspace_residual_a={max(constant_voltage_residuals):.12g}"
    )
    print(f"output_csv={out_path}; rows={len(rows)}")


if __name__ == "__main__":
    main()
