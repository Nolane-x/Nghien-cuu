"""Matched-port Schur admittance comparison: AMSN versus native NEURON.

AMSN constructs an exact frequency-dependent Schur complement by eliminating
every cable compartment except the seven shared SWC source/probe vertices.
A second independent AMSN path constructs the full 7x7 port impedance matrix
with the ordinary Hines solver and inverts it. NEURON constructs the matching
7x7 transfer-impedance matrix from its native Import3D fine segment tree,
using exact SWC section coordinates for each port, then inverts it to obtain
the effective port admittance.

This compares two reduced boundary operators on the same SWC ports. It is
not a matched-support membrane projection: all non-port compartments inside
each simulator are eliminated implicitly by the port reduction. The resulting
matrices are frequency-dependent and dense. This is passive numerical
validation, not biological validation.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.reduction import schur_reduce_passive_admittance


RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
CURRENT_A = 1e-9
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988_Mohan2015")
MORPHOLOGY_PATH = os.environ.get("AMSN_MORPHOLOGY_PATH")
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
OUTPUT_PREFIX = os.environ.get("AMSN_SCHUR_OUTPUT_PREFIX", "")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def neuron_transfer_ohm(impedance, x: float, section) -> complex:
    magnitude_mohm = float(impedance.transfer(float(x), sec=section))
    phase_rad = float(impedance.transfer_phase(float(x), sec=section))
    if (
        not np.isfinite(magnitude_mohm)
        or magnitude_mohm < 0.0
        or not np.isfinite(phase_rad)
    ):
        raise RuntimeError(
            f"invalid NEURON transfer impedance magnitude/phase: "
            f"{magnitude_mohm}, {phase_rad}"
        )
    return magnitude_mohm * 1e6 * np.exp(1j * phase_rad)


def relative_frobenius_pct(actual: np.ndarray, reference_matrix: np.ndarray) -> float:
    denominator = float(np.linalg.norm(reference_matrix))
    if not np.isfinite(denominator) or denominator == 0.0:
        raise RuntimeError("zero or non-finite reference matrix norm")
    return 100.0 * float(np.linalg.norm(actual - reference_matrix)) / denominator


def matrix_error_parts(
    amsn_matrix: np.ndarray,
    neuron_matrix: np.ndarray,
) -> tuple[float, float, float, float]:
    total = relative_frobenius_pct(amsn_matrix, neuron_matrix)
    diagonal_mask = np.eye(amsn_matrix.shape[0], dtype=bool)
    off_diagonal_mask = ~diagonal_mask
    diagonal_error = relative_frobenius_pct(
        amsn_matrix[diagonal_mask], neuron_matrix[diagonal_mask]
    )
    off_diagonal_error = relative_frobenius_pct(
        amsn_matrix[off_diagonal_mask], neuron_matrix[off_diagonal_mask]
    )
    absolute_max = float(np.max(np.abs(amsn_matrix - neuron_matrix)))
    return total, diagonal_error, off_diagonal_error, absolute_max


def build_amsn_port_impedance(
    tree,
    boundary_indices: list[int],
    frequency_hz: float,
) -> np.ndarray:
    count = len(boundary_indices)
    impedance = np.empty((count, count), dtype=np.complex128)
    for source_column, source_index in enumerate(boundary_indices):
        current = np.zeros(tree.n_compartments, dtype=np.complex128)
        current[source_index] = CURRENT_A
        voltage = tree.solve_passive_frequency_response(frequency_hz, current)
        impedance[:, source_column] = voltage[boundary_indices] / CURRENT_A
    return impedance


def build_neuron_port_impedance(
    boundary_ids: list[int],
    sites: dict,
    frequency_hz: float,
) -> np.ndarray:
    count = len(boundary_ids)
    impedance_matrix = np.empty((count, count), dtype=np.complex128)
    h.CVode().active(0)
    for source_column, source_id in enumerate(boundary_ids):
        source_site = sites[source_id]
        h.finitialize(ELEAK_MV)
        impedance = h.Impedance()
        impedance.loc(float(source_site["normalized_x"]), sec=source_site["section"])
        impedance.compute(float(frequency_hz))
        for probe_row, probe_id in enumerate(boundary_ids):
            probe_site = sites[probe_id]
            impedance_matrix[probe_row, source_column] = neuron_transfer_ohm(
                impedance,
                float(probe_site["normalized_x"]),
                probe_site["section"],
            )
    if not (
        np.all(np.isfinite(impedance_matrix.real))
        and np.all(np.isfinite(impedance_matrix.imag))
    ):
        raise RuntimeError("NEURON port impedance matrix contains non-finite values")
    return impedance_matrix


def main() -> None:
    if not np.isfinite(NEURON_MAX_SEGMENT_UM) or NEURON_MAX_SEGMENT_UM <= 0.0:
        raise ValueError("AMSN_NEURON_MAX_SEGMENT_UM must be finite and positive")

    reference.DATA = Path(MORPHOLOGY_PATH) if MORPHOLOGY_PATH else reference.DATA
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV

    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(morphology, reader, sections)
    boundary_ids = list(dict.fromkeys(
        [node_id for _, node_id in injections + probes]
    ))
    if len(injections) != 3 or len(probes) != 5 or len(boundary_ids) != 7:
        raise RuntimeError(
            f"expected 3 source labels, 5 probe labels and 7 unique ports; "
            f"got {len(injections)}, {len(probes)}, {len(boundary_ids)}"
        )
    if set(boundary_ids) != set(sites):
        raise RuntimeError("not every retained SWC port has an Import3D mapping")

    electrical_map = morphology.electrical_node_mapping()
    node_to_name = {
        node_id: f"swc_{electrical_map[node_id]}"
        for node_id in morphology.nodes
    }
    cable = morphology.to_cable_tree()
    boundary_indices = [cable.index[node_to_name[node_id]] for node_id in boundary_ids]

    roles: dict[int, list[str]] = defaultdict(list)
    for name, node_id in injections:
        roles[node_id].append(f"source:{name}")
    for name, node_id in probes:
        roles[node_id].append(f"probe:{name}")

    boundary_meta = []
    for node_id, index in zip(boundary_ids, boundary_indices):
        site = sites[node_id]
        boundary_meta.append({
            "node_id": node_id,
            "cable_index": index,
            "roles": ";".join(roles[node_id]),
            "section": site["section"].name(),
            "section_x": float(site["normalized_x"]),
        })

    prefix = OUTPUT_PREFIX or (
        f"{MORPHOLOGY_LABEL}_mesh{NEURON_MAX_SEGMENT_UM:g}um_"
    )
    results_dir = Path(__file__).parents[1] / "results"
    raw_path = results_dir / f"{prefix}human_passive_schur_port_matrix_2026-11-21.csv"
    summary_path = results_dir / f"{prefix}human_passive_schur_port_summary_2026-11-21.csv"
    localization_path = results_dir / f"{prefix}human_passive_schur_port_localization_2026-11-21.csv"
    raw_rows: list[dict] = []
    summary_rows: list[dict] = []
    localization_rows: list[dict] = []
    maximum_schur_identity_error_pct = 0.0
    maximum_amsn_reciprocity_error_pct = 0.0
    maximum_neuron_reciprocity_error_pct = 0.0
    maximum_neuron_impedance_condition = 0.0

    for frequency_hz in FREQUENCIES_HZ:
        y_amsn_schur = schur_reduce_passive_admittance(
            cable, boundary_indices, frequency_hz
        )
        z_amsn = build_amsn_port_impedance(cable, boundary_indices, frequency_hz)
        z_neuron = build_neuron_port_impedance(boundary_ids, sites, frequency_hz)

        amsn_condition = float(np.linalg.cond(z_amsn))
        neuron_condition = float(np.linalg.cond(z_neuron))
        maximum_neuron_impedance_condition = max(
            maximum_neuron_impedance_condition, neuron_condition
        )
        if (
            not np.isfinite(amsn_condition)
            or not np.isfinite(neuron_condition)
            or max(amsn_condition, neuron_condition) > 1e15
        ):
            raise RuntimeError(
                f"ill-conditioned port impedance matrix at {frequency_hz:g} Hz: "
                f"AMSN={amsn_condition:.12g}, NEURON={neuron_condition:.12g}"
            )

        y_amsn_from_z = np.linalg.inv(z_amsn)
        y_neuron = np.linalg.inv(z_neuron)
        schur_identity_error = relative_frobenius_pct(y_amsn_schur, y_amsn_from_z)
        maximum_schur_identity_error_pct = max(
            maximum_schur_identity_error_pct, schur_identity_error
        )
        if schur_identity_error > 1e-7:
            raise RuntimeError(
                f"AMSN Schur reduction disagrees with independent full-tree "
                f"port solve at {frequency_hz:g} Hz: {schur_identity_error:.12g}%"
            )

        amsn_reciprocity = relative_frobenius_pct(z_amsn, z_amsn.T)
        neuron_reciprocity = relative_frobenius_pct(z_neuron, z_neuron.T)
        maximum_amsn_reciprocity_error_pct = max(
            maximum_amsn_reciprocity_error_pct, amsn_reciprocity
        )
        maximum_neuron_reciprocity_error_pct = max(
            maximum_neuron_reciprocity_error_pct, neuron_reciprocity
        )

        total_error, diagonal_error, offdiag_error, max_abs_error = matrix_error_parts(
            y_amsn_schur, y_neuron
        )
        z_error, z_diagonal_error, z_offdiag_error, z_max_abs_error = matrix_error_parts(
            z_amsn, z_neuron
        )
        summary_rows.append({
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "frequency_hz": frequency_hz,
            "boundary_port_count": len(boundary_ids),
            "amsn_compartment_count": cable.n_compartments,
            "neuron_section_count": len(sections),
            "neuron_segment_count": sum(section.nseg for section in sections),
            "amsn_schur_vs_full_port_inverse_error_pct": schur_identity_error,
            "amsn_reciprocity_error_pct": amsn_reciprocity,
            "neuron_reciprocity_error_pct": neuron_reciprocity,
            "neuron_port_impedance_condition": neuron_condition,
            "port_admittance_frobenius_error_pct": total_error,
            "port_admittance_diagonal_error_pct": diagonal_error,
            "port_admittance_offdiagonal_error_pct": offdiag_error,
            "port_admittance_max_absolute_error_s": max_abs_error,
            "port_impedance_frobenius_error_pct": z_error,
            "port_impedance_diagonal_error_pct": z_diagonal_error,
            "port_impedance_offdiagonal_error_pct": z_offdiag_error,
            "port_impedance_max_absolute_error_ohm": z_max_abs_error,
        })

        # Localize each frequency-domain residual by retained port row.
        # Relative row norms avoid judging tiny individual off-diagonal
        # elements by unstable elementwise percentages.
        for port_index, port_meta in enumerate(boundary_meta):
            row_delta = y_amsn_schur[port_index, :] - y_neuron[port_index, :]
            row_reference = y_neuron[port_index, :]
            off_diagonal_mask = np.arange(len(boundary_ids)) != port_index
            offdiag_delta = row_delta[off_diagonal_mask]
            offdiag_reference = row_reference[off_diagonal_mask]
            diagonal_delta = row_delta[port_index]
            diagonal_reference = row_reference[port_index]
            localization_rows.append({
                "morphology_label": MORPHOLOGY_LABEL,
                "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                "frequency_hz": frequency_hz,
                "port_index": port_index,
                "port_swc_id": port_meta["node_id"],
                "port_cable_index": port_meta["cable_index"],
                "port_roles": port_meta["roles"],
                "port_section": port_meta["section"],
                "port_section_x": port_meta["section_x"],
                "row_frobenius_relative_error_pct": (
                    100.0 * float(np.linalg.norm(row_delta))
                    / max(float(np.linalg.norm(row_reference)), 1e-30)
                ),
                "offdiagonal_row_relative_error_pct": (
                    100.0 * float(np.linalg.norm(offdiag_delta))
                    / max(float(np.linalg.norm(offdiag_reference)), 1e-30)
                ),
                "diagonal_entry_relative_error_pct": (
                    100.0 * abs(diagonal_delta) / max(abs(diagonal_reference), 1e-30)
                ),
                "row_max_absolute_error_s": float(np.max(np.abs(row_delta))),
                "diagonal_absolute_error_s": float(abs(diagonal_delta)),
            })

        for row_index, row_meta in enumerate(boundary_meta):
            for column_index, column_meta in enumerate(boundary_meta):
                y_a = y_amsn_schur[row_index, column_index]
                y_n = y_neuron[row_index, column_index]
                z_a = z_amsn[row_index, column_index]
                z_n = z_neuron[row_index, column_index]
                raw_rows.append({
                    "morphology_label": MORPHOLOGY_LABEL,
                    "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                    "frequency_hz": frequency_hz,
                    "row_port_index": row_index,
                    "row_swc_id": row_meta["node_id"],
                    "row_cable_index": row_meta["cable_index"],
                    "row_roles": row_meta["roles"],
                    "row_section": row_meta["section"],
                    "row_section_x": row_meta["section_x"],
                    "column_port_index": column_index,
                    "column_swc_id": column_meta["node_id"],
                    "column_cable_index": column_meta["cable_index"],
                    "column_roles": column_meta["roles"],
                    "column_section": column_meta["section"],
                    "column_section_x": column_meta["section_x"],
                    "amsn_schur_admittance_real_s": y_a.real,
                    "amsn_schur_admittance_imag_s": y_a.imag,
                    "neuron_port_admittance_real_s": y_n.real,
                    "neuron_port_admittance_imag_s": y_n.imag,
                    "admittance_absolute_error_s": abs(y_a - y_n),
                    "admittance_relative_error_pct": (
                        100.0 * abs(y_a - y_n) / max(abs(y_n), 1e-30)
                    ),
                    "amsn_port_impedance_real_ohm": z_a.real,
                    "amsn_port_impedance_imag_ohm": z_a.imag,
                    "neuron_port_impedance_real_ohm": z_n.real,
                    "neuron_port_impedance_imag_ohm": z_n.imag,
                    "impedance_absolute_error_ohm": abs(z_a - z_n),
                    "impedance_relative_error_pct": (
                        100.0 * abs(z_a - z_n) / max(abs(z_n), 1e-30)
                    ),
                    "amsn_schur_identity_error_pct": schur_identity_error,
                })

    expected_raw_rows = len(FREQUENCIES_HZ) * len(boundary_ids) ** 2
    if len(raw_rows) != expected_raw_rows:
        raise RuntimeError(
            f"expected {expected_raw_rows} raw port rows, got {len(raw_rows)}"
        )
    if len(summary_rows) != len(FREQUENCIES_HZ):
        raise RuntimeError("reduced port summary row count mismatch")
    expected_localization_rows = len(FREQUENCIES_HZ) * len(boundary_ids)
    if len(localization_rows) != expected_localization_rows:
        raise RuntimeError(
            f"expected {expected_localization_rows} port localization rows, "
            f"got {len(localization_rows)}"
        )
    write_csv(raw_path, raw_rows)
    write_csv(summary_path, summary_rows)
    write_csv(localization_path, localization_rows)

    max_admittance_error = max(
        float(row["port_admittance_frobenius_error_pct"]) for row in summary_rows
    )
    max_impedance_error = max(
        float(row["port_impedance_frobenius_error_pct"]) for row in summary_rows
    )
    print(f"NEURON={neuron.__version__}")
    print(
        f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}; "
        f"SWC_records={len(morphology.nodes)}"
    )
    print(
        f"AMSN_compartments={cable.n_compartments}; NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}; "
        f"mesh_cap_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(
        f"boundary_ports={len(boundary_ids)}; frequencies={len(FREQUENCIES_HZ)}; "
        f"raw_rows={len(raw_rows)}; summary_rows={len(summary_rows)}"
    )
    print(
        f"schur_vs_full_AMSN_inverse_error_pct_max={maximum_schur_identity_error_pct:.12g}; "
        f"AMSN_reciprocity_error_pct_max={maximum_amsn_reciprocity_error_pct:.12g}; "
        f"NEURON_reciprocity_error_pct_max={maximum_neuron_reciprocity_error_pct:.12g}"
    )
    print(
        f"port_admittance_frobenius_error_pct_max={max_admittance_error:.12g}; "
        f"port_impedance_frobenius_error_pct_max={max_impedance_error:.12g}; "
        f"neuron_impedance_condition_max={maximum_neuron_impedance_condition:.12g}"
    )
    print(f"raw_csv={raw_path}; bytes={raw_path.stat().st_size}")
    print(f"summary_csv={summary_path}; rows={len(summary_rows)}")
    print(f"port_localization_csv={localization_path}; rows={len(localization_rows)}")


if __name__ == "__main__":
    main()
