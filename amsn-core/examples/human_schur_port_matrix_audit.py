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
import human_prima_port_enrichment as port_enrichment
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.reduction import schur_reduce_passive_admittance
from amsn.prima import (
    prima_reduce_passive_cable,
    prima_reduce_passive_cable_multishift,
)


RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
CURRENT_A = 1e-9
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988_Mohan2015")
MORPHOLOGY_PATH = os.environ.get("AMSN_MORPHOLOGY_PATH")
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
OUTPUT_PREFIX = os.environ.get("AMSN_SCHUR_OUTPUT_PREFIX", "")
PRIMA_MAX_ORDER = int(os.environ.get("AMSN_PRIMA_MAX_ORDER", "56"))
PRIMA_MULTI_SHIFT_HZ = (0.0, 100.0, 1000.0, 3000.0)
PRIMA_MULTI_SHIFT_EXTENDED_HZ = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
EXTENDED_ORDER_SWEEP = tuple(
    int(value.strip())
    for value in os.environ.get("AMSN_PRIMA_EXTENDED_ORDERS", "28,56,84").split(",")
    if value.strip()
)
if (
    not EXTENDED_ORDER_SWEEP
    or any(order <= 0 for order in EXTENDED_ORDER_SWEEP)
    or len(set(EXTENDED_ORDER_SWEEP)) != len(EXTENDED_ORDER_SWEEP)
    or 56 not in EXTENDED_ORDER_SWEEP
):
    raise ValueError(
        "AMSN_PRIMA_EXTENDED_ORDERS must contain unique positive orders and include 56"
    )
EXTRA_PROBE_QUANTILES = (
    (0.25, 0.75)
    if os.environ.get("AMSN_PORT_ENRICHMENT", "").strip() == "apical_basal_q25_q75"
    else ()
)
TRANSIENT_SCENARIOS = (
    ("soma", 2.0),
    ("basal_q75", 2.0),
    ("apical_q75", 2.0),
    ("soma", 10.0),
    ("basal_q75", 10.0),
    ("apical_q75", 10.0),
)


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



def build_prima_transient_port_comparison(
    tree,
    reduced_model,
    boundary_indices: list[int],
    source_port_index: int,
    boundary_meta: list[dict],
    reduction_method: str,
    *,
    source_name: str = "basal_q75",
    pulse_width_ms: float = 10.0,
    pulse_start_ms: float = 2.0,
    pulse_current_pa: float = 10.0,
    dt_ms: float = 0.1,
    duration_ms: float = 20.0,
) -> list[dict]:
    """Compare reduced and full Hines port traces for one named current pulse."""
    if isinstance(source_port_index, bool) or not isinstance(source_port_index, int):
        raise TypeError("source_port_index must be an integer")
    if not 0 <= source_port_index < len(boundary_indices):
        raise IndexError("source_port_index is outside the retained port set")
    values = np.asarray(
        [pulse_width_ms, pulse_start_ms, pulse_current_pa, dt_ms, duration_ms],
        dtype=float,
    )
    if not np.all(np.isfinite(values)):
        raise ValueError("transient settings must be finite")
    if pulse_width_ms <= 0.0 or pulse_start_ms < 0.0 or pulse_current_pa <= 0.0:
        raise ValueError("pulse width/current must be positive and pulse start nonnegative")
    if dt_ms <= 0.0 or duration_ms <= 0.0:
        raise ValueError("transient dt and duration must be positive")
    dt_s = dt_ms * 1e-3
    duration_s = duration_ms * 1e-3
    steps_float = duration_s / dt_s
    steps = round(steps_float)
    if not np.isclose(steps_float, steps, rtol=0.0, atol=1e-10):
        raise ValueError("duration_ms must be an integer multiple of dt_ms")
    pulse_start_s = pulse_start_ms * 1e-3
    pulse_end_s = pulse_start_s + pulse_width_ms * 1e-3
    if pulse_end_s > duration_s:
        raise ValueError("pulse must end no later than the transient duration")
    pulse_current_a = pulse_current_pa * 1e-12
    scenario_id = f"{source_name}_pulse{pulse_width_ms:g}ms"
    reversal_v = tree.parameters.e_leak_v
    full_voltage = np.full(tree.n_compartments, reversal_v, dtype=float)
    reduced_state = np.zeros(reduced_model.order, dtype=float)
    full_current = np.zeros(tree.n_compartments, dtype=float)
    port_current = np.zeros(len(boundary_indices), dtype=float)
    full_trace = np.empty((steps, len(boundary_indices)), dtype=float)
    reduced_trace = np.empty_like(full_trace)

    for step in range(steps):
        time_s = step * dt_s
        full_current.fill(0.0)
        port_current.fill(0.0)
        if pulse_start_s <= time_s < pulse_end_s:
            full_current[boundary_indices[source_port_index]] = pulse_current_a
            port_current[source_port_index] = pulse_current_a
        full_voltage = tree.step_passive(full_voltage, dt_s, full_current)
        reduced_state = reduced_model.step_backward_euler(
            reduced_state, dt_s, port_current
        )
        full_trace[step, :] = full_voltage[boundary_indices] - reversal_v
        reduced_trace[step, :] = reduced_model.port_voltages(reduced_state)

    rows: list[dict] = []
    for port_index, meta in enumerate(boundary_meta):
        reference_trace = full_trace[:, port_index]
        reduced_port_trace = reduced_trace[:, port_index]
        denominator = max(float(np.linalg.norm(reference_trace)), 1e-30)
        reference_peak = float(np.max(np.abs(reference_trace)))
        absolute_error = reduced_port_trace - reference_trace
        rows.append({
            "metric": "transient_port",
            "reduction_method": reduction_method,
            "model_id": reduction_method,
            "reduced_order": reduced_model.order,
            "scenario_id": scenario_id,
            "source_name": source_name,
            "pulse_width_ms": pulse_width_ms,
            "frequency_hz": "",
            "port_index": port_index,
            "port_swc_id": meta["node_id"],
            "port_roles": meta["roles"],
            "transient_dt_ms": dt_ms,
            "transient_duration_ms": duration_ms,
            "transient_pulse_start_ms": pulse_start_ms,
            "transient_pulse_end_ms": pulse_start_ms + pulse_width_ms,
            "transient_current_pA": pulse_current_pa,
            "transient_port_nrmse_pct": (
                100.0 * float(np.linalg.norm(absolute_error)) / denominator
            ),
            "transient_max_abs_error_mV": float(np.max(np.abs(absolute_error))) * 1e3,
            "transient_full_peak_mV": reference_peak * 1e3,
            "transient_peak_relative_error_pct": (
                100.0 * float(np.max(np.abs(absolute_error)))
                / max(reference_peak, 1e-30)
            ),
        })

    all_reference = full_trace.ravel()
    all_error = (reduced_trace - full_trace).ravel()
    rows.append({
        "metric": "transient_all_ports",
        "reduction_method": reduction_method,
        "model_id": reduction_method,
        "reduced_order": reduced_model.order,
        "scenario_id": scenario_id,
        "source_name": source_name,
        "pulse_width_ms": pulse_width_ms,
        "frequency_hz": "",
        "port_index": "",
        "port_swc_id": "",
        "port_roles": "all_retained_ports",
        "transient_dt_ms": dt_ms,
        "transient_duration_ms": duration_ms,
        "transient_pulse_start_ms": pulse_start_ms,
        "transient_pulse_end_ms": pulse_start_ms + pulse_width_ms,
        "transient_current_pA": pulse_current_pa,
        "transient_port_nrmse_pct": (
            100.0 * float(np.linalg.norm(all_error))
            / max(float(np.linalg.norm(all_reference)), 1e-30)
        ),
        "transient_max_abs_error_mV": float(np.max(np.abs(all_error))) * 1e3,
        "transient_full_peak_mV": float(np.max(np.abs(all_reference))) * 1e3,
        "transient_peak_relative_error_pct": (
            100.0 * float(np.max(np.abs(all_error)))
            / max(float(np.max(np.abs(all_reference))), 1e-30)
        ),
    })
    return rows



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
    if EXTRA_PROBE_QUANTILES:
        injections, probes, sites = port_enrichment.build_sites(
            morphology,
            reader,
            sections,
            extra_probe_quantiles=EXTRA_PROBE_QUANTILES,
        )
    else:
        injections, probes, sites = fine_audit.build_sites(
            morphology, reader, sections
        )
    boundary_ids = list(dict.fromkeys(
        [node_id for _, node_id in injections + probes]
    ))
    expected_probe_count = 5 + 2 * len(EXTRA_PROBE_QUANTILES)
    expected_unique_ports = 7 if not EXTRA_PROBE_QUANTILES else 9
    if (
        len(injections) != 3
        or len(probes) != expected_probe_count
        or len(boundary_ids) != expected_unique_ports
    ):
        raise RuntimeError(
            f"expected 3 source labels, {expected_probe_count} probe labels and "
            f"{expected_unique_ports} unique ports; got "
            f"{len(injections)}, {len(probes)}, {len(boundary_ids)}"
        )
    if EXTRA_PROBE_QUANTILES:
        expected_extra_labels = {
            f"{branch}_{f'q{round(quantile * 100):02d}'}"
            for quantile in EXTRA_PROBE_QUANTILES
            for branch in ("basal", "apical")
        }
        actual_labels = {name for name, _ in probes}
        if not expected_extra_labels.issubset(actual_labels):
            raise RuntimeError(
                f"missing enriched probe labels: "
                f"{sorted(expected_extra_labels - actual_labels)}"
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
    if len(set(boundary_indices)) != len(boundary_indices):
        duplicate_indices = sorted(
            index for index in set(boundary_indices)
            if boundary_indices.count(index) > 1
        )
        raise RuntimeError(
            "retained SWC ports collapse to duplicate electrical compartments "
            f"after morphology normalization: {duplicate_indices}"
        )
    if PRIMA_MAX_ORDER <= 0:
        raise ValueError("AMSN_PRIMA_MAX_ORDER must be positive")
    prima_model = prima_reduce_passive_cable(cable, boundary_indices, max_order=PRIMA_MAX_ORDER)
    prima_multishift_model = prima_reduce_passive_cable_multishift(
        cable, boundary_indices, max_order=PRIMA_MAX_ORDER,
        expansion_frequencies_hz=PRIMA_MULTI_SHIFT_HZ,
    )
    prima_multishift_extended_model = prima_reduce_passive_cable_multishift(
        cable, boundary_indices, max_order=PRIMA_MAX_ORDER,
        expansion_frequencies_hz=PRIMA_MULTI_SHIFT_EXTENDED_HZ,
    )
    for projected_model in (prima_multishift_model, prima_multishift_extended_model):
        np.linalg.cholesky(projected_model.conductance_matrix_s)
        np.linalg.cholesky(projected_model.capacitance_matrix_f)
    prima_order_sweep_models = {
        28: prima_reduce_passive_cable_multishift(
            cable, boundary_indices, max_order=28,
            expansion_frequencies_hz=PRIMA_MULTI_SHIFT_HZ,
        ),
        56: prima_multishift_model,
        84: prima_reduce_passive_cable_multishift(
            cable, boundary_indices, max_order=84,
            expansion_frequencies_hz=PRIMA_MULTI_SHIFT_HZ,
        ),
    }
    prima_extended_order_sweep_models = {
        "four_shift_order56_control": prima_multishift_model,
    }
    for order in EXTENDED_ORDER_SWEEP:
        if order == 56:
            sweep_model = prima_multishift_extended_model
        else:
            sweep_model = prima_reduce_passive_cable_multishift(
                cable,
                boundary_indices,
                max_order=order,
                expansion_frequencies_hz=PRIMA_MULTI_SHIFT_EXTENDED_HZ,
            )
        prima_extended_order_sweep_models[f"six_shift_order{order}"] = sweep_model
    for model_id, projected_model in prima_extended_order_sweep_models.items():
        np.linalg.cholesky(projected_model.conductance_matrix_s)
        np.linalg.cholesky(projected_model.capacitance_matrix_f)
        if projected_model.order >= cable.n_compartments:
            raise RuntimeError(
                f"{model_id} did not reduce the full compartment state count"
            )
    if prima_model.order >= cable.n_compartments:
        raise RuntimeError("PRIMA audit did not reduce the full compartment state count")

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
    if EXTRA_PROBE_QUANTILES and not prefix.endswith("9port_"):
        prefix = f"{prefix}9port_"
    results_dir = Path(__file__).parents[1] / "results"
    raw_path = results_dir / f"{prefix}human_passive_schur_port_matrix_2026-11-22.csv"
    summary_path = results_dir / f"{prefix}human_passive_schur_port_summary_2026-11-22.csv"
    localization_path = results_dir / f"{prefix}human_passive_schur_port_localization_2026-11-22.csv"
    prima_path = results_dir / f"{prefix}human_passive_prima_reduction_2026-11-22.csv"
    prima_multishift_path = results_dir / f"{prefix}human_passive_prima_multishift_reduction_2026-11-22.csv"
    prima_multishift_extended_path = results_dir / f"{prefix}human_passive_prima_multishift_extended_reduction_2026-11-22.csv"
    prima_sweep_path = results_dir / f"{prefix}human_passive_prima_multishift_order_sweep_2026-11-22.csv"
    prima_extended_sweep_path = results_dir / f"{prefix}human_passive_prima_extended_order_transient_sweep_2026-11-22.csv"
    raw_rows: list[dict] = []
    summary_rows: list[dict] = []
    localization_rows: list[dict] = []
    prima_rows: list[dict] = []
    prima_multishift_rows: list[dict] = []
    prima_multishift_extended_rows: list[dict] = []
    prima_sweep_rows: list[dict] = []
    prima_extended_sweep_rows: list[dict] = []
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
        z_prima = prima_model.impedance_matrix(frequency_hz)
        y_prima = np.linalg.solve(z_prima, np.eye(len(boundary_ids)))
        z_prima_multi = prima_multishift_model.impedance_matrix(frequency_hz)
        y_prima_multi = np.linalg.solve(z_prima_multi, np.eye(len(boundary_ids)))
        z_prima_multi_extended = prima_multishift_extended_model.impedance_matrix(frequency_hz)
        y_prima_multi_extended = np.linalg.solve(
            z_prima_multi_extended, np.eye(len(boundary_ids))
        )
        prima_multishift_extended_rows.append({
            "metric": "frequency_response",
            "reduction_method": "multi_shift_extended_10khz",
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "frequency_hz": frequency_hz,
            "full_compartment_order": cable.n_compartments,
            "prima_order": prima_multishift_extended_model.order,
            "expansion_frequencies_hz": ";".join(str(x) for x in PRIMA_MULTI_SHIFT_EXTENDED_HZ),
            "state_count_reduction_pct": 100.0 * (1.0 - prima_multishift_extended_model.order / cable.n_compartments),
            "impedance_frobenius_error_pct": relative_frobenius_pct(z_prima_multi_extended, z_amsn),
            "admittance_frobenius_error_pct": relative_frobenius_pct(y_prima_multi_extended, y_amsn_schur),
            "neuron_impedance_frobenius_error_pct": relative_frobenius_pct(z_prima_multi_extended, z_neuron),
            "neuron_admittance_frobenius_error_pct": relative_frobenius_pct(y_prima_multi_extended, y_neuron),
        })
        for model_id, sweep_model in prima_extended_order_sweep_models.items():
            z_extended_sweep = (
                z_prima_multi if model_id == "four_shift_order56_control"
                else z_prima_multi_extended if model_id == "six_shift_order56"
                else sweep_model.impedance_matrix(frequency_hz)
            )
            y_extended_sweep = (
                y_prima_multi if model_id == "four_shift_order56_control"
                else y_prima_multi_extended if model_id == "six_shift_order56"
                else np.linalg.solve(
                    z_extended_sweep, np.eye(len(boundary_ids))
                )
            )
            shift_set = (
                PRIMA_MULTI_SHIFT_HZ
                if model_id == "four_shift_order56_control"
                else PRIMA_MULTI_SHIFT_EXTENDED_HZ
            )
            requested_order = (
                56 if model_id == "four_shift_order56_control"
                else int(model_id.rsplit("order", 1)[1])
            )
            prima_extended_sweep_rows.append({
                "metric": "frequency_response",
                "model_id": model_id,
                "morphology_label": MORPHOLOGY_LABEL,
                "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                "frequency_hz": frequency_hz,
                "full_compartment_order": cable.n_compartments,
                "requested_order": requested_order,
                "prima_order": sweep_model.order,
                "state_count_reduction_pct": (
                    100.0 * (1.0 - sweep_model.order / cable.n_compartments)
                ),
                "expansion_frequencies_hz": ";".join(str(x) for x in shift_set),
                "impedance_vs_hines_pct": relative_frobenius_pct(
                    z_extended_sweep, z_amsn
                ),
                "admittance_vs_hines_pct": relative_frobenius_pct(
                    y_extended_sweep, y_amsn_schur
                ),
                "impedance_vs_neuron_pct": relative_frobenius_pct(
                    z_extended_sweep, z_neuron
                ),
                "admittance_vs_neuron_pct": relative_frobenius_pct(
                    y_extended_sweep, y_neuron
                ),
                "neuron_impedance_condition": neuron_condition,
            })
        prima_multishift_rows.append({
            "metric": "frequency_response",
            "reduction_method": "multi_shift_positive_real",
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "frequency_hz": frequency_hz,
            "full_compartment_order": cable.n_compartments,
            "prima_order": prima_multishift_model.order,
            "expansion_frequencies_hz": ";".join(str(x) for x in PRIMA_MULTI_SHIFT_HZ),
            "state_count_reduction_pct": 100.0 * (1.0 - prima_multishift_model.order / cable.n_compartments),
            "impedance_frobenius_error_pct": relative_frobenius_pct(z_prima_multi, z_amsn),
            "admittance_frobenius_error_pct": relative_frobenius_pct(y_prima_multi, y_amsn_schur),
            "neuron_impedance_frobenius_error_pct": relative_frobenius_pct(z_prima_multi, z_neuron),
            "neuron_admittance_frobenius_error_pct": relative_frobenius_pct(y_prima_multi, y_neuron),
        })
        for order, sweep_model in prima_order_sweep_models.items():
            if order == prima_multishift_model.order:
                z_sweep = z_prima_multi
                y_sweep = y_prima_multi
            else:
                z_sweep = sweep_model.impedance_matrix(frequency_hz)
                y_sweep = np.linalg.solve(z_sweep, np.eye(len(boundary_ids)))
            prima_sweep_rows.append({
                "metric": "frequency_response",
                "reduction_method": "multi_shift_positive_real",
                "morphology_label": MORPHOLOGY_LABEL,
                "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                "frequency_hz": frequency_hz,
                "full_compartment_order": cable.n_compartments,
                "prima_order": sweep_model.order,
                "expansion_frequencies_hz": ";".join(str(x) for x in PRIMA_MULTI_SHIFT_HZ),
                "state_count_reduction_pct": 100.0 * (1.0 - sweep_model.order / cable.n_compartments),
                "impedance_frobenius_error_pct": relative_frobenius_pct(z_sweep, z_amsn),
                "admittance_frobenius_error_pct": relative_frobenius_pct(y_sweep, y_amsn_schur),
                "neuron_impedance_frobenius_error_pct": relative_frobenius_pct(z_sweep, z_neuron),
                "neuron_admittance_frobenius_error_pct": relative_frobenius_pct(y_sweep, y_neuron),
            })
        prima_rows.append({
            "metric": "frequency_response",
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "frequency_hz": frequency_hz,
            "full_compartment_order": cable.n_compartments,
            "prima_order": prima_model.order,
            "prima_max_order": PRIMA_MAX_ORDER,
            "state_count_reduction_pct": 100.0 * (1.0 - prima_model.order / cable.n_compartments),
            "impedance_frobenius_error_pct": relative_frobenius_pct(z_prima, z_amsn),
            "admittance_frobenius_error_pct": relative_frobenius_pct(y_prima, y_amsn_schur),
        })
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
            "prima_reduced_order": prima_model.order,
            "prima_state_count_reduction_pct": 100.0 * (1.0 - prima_model.order / cable.n_compartments),
            "prima_impedance_frobenius_error_pct": relative_frobenius_pct(z_prima, z_amsn),
            "prima_admittance_frobenius_error_pct": relative_frobenius_pct(y_prima, y_amsn_schur),
            "prima_multishift_impedance_vs_neuron_pct": relative_frobenius_pct(z_prima_multi, z_neuron),
            "prima_multishift_admittance_vs_neuron_pct": relative_frobenius_pct(y_prima_multi, y_neuron),
            "prima_multishift_extended_impedance_vs_neuron_pct": relative_frobenius_pct(z_prima_multi_extended, z_neuron),
            "prima_multishift_extended_admittance_vs_neuron_pct": relative_frobenius_pct(y_prima_multi_extended, y_neuron),
            "neuron_impedance_frobenius_error_pct": relative_frobenius_pct(z_prima, z_neuron),
            "neuron_admittance_frobenius_error_pct": relative_frobenius_pct(y_prima, y_neuron),
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
    basal_source_id = next(node_id for name, node_id in injections if name == "basal_q75")
    basal_source_port = boundary_ids.index(basal_source_id)
    prima_rows.extend(build_prima_transient_port_comparison(cable, prima_model, boundary_indices, basal_source_port, boundary_meta, "dc_krylov"))
    prima_multishift_rows.extend(build_prima_transient_port_comparison(
        cable, prima_multishift_model, boundary_indices, basal_source_port,
        boundary_meta, "multi_shift_positive_real"
    ))
    for order, sweep_model in prima_order_sweep_models.items():
        prima_sweep_rows.extend(build_prima_transient_port_comparison(
            cable, sweep_model, boundary_indices, basal_source_port,
            boundary_meta, f"multi_shift_order_{order}"
        ))
    write_csv(prima_path, prima_rows)
    write_csv(prima_multishift_path, prima_multishift_rows)
    prima_multishift_extended_rows.extend(build_prima_transient_port_comparison(
        cable, prima_multishift_extended_model, boundary_indices, basal_source_port,
        boundary_meta, "multi_shift_extended_10khz"
    ))
    write_csv(prima_multishift_extended_path, prima_multishift_extended_rows)
    write_csv(prima_sweep_path, prima_sweep_rows)

    injection_ids = dict(injections)
    required_sources = {source_name for source_name, _ in TRANSIENT_SCENARIOS}
    missing_sources = required_sources.difference(injection_ids)
    if missing_sources:
        raise RuntimeError(
            f"transient scenarios reference unmapped injection sources: {sorted(missing_sources)}"
        )
    for model_id, sweep_model in prima_extended_order_sweep_models.items():
        if tuple(sweep_model.port_indices) != tuple(boundary_indices):
            raise RuntimeError(f"{model_id} retained-port order does not match the audit")
        for source_name, pulse_width_ms in TRANSIENT_SCENARIOS:
            source_id = injection_ids[source_name]
            source_port_index = boundary_ids.index(source_id)
            prima_extended_sweep_rows.extend(build_prima_transient_port_comparison(
                cable,
                sweep_model,
                boundary_indices,
                source_port_index,
                boundary_meta,
                model_id,
                source_name=source_name,
                pulse_width_ms=pulse_width_ms,
            ))
    expected_extended_rows = len(prima_extended_order_sweep_models) * (
        len(FREQUENCIES_HZ)
        + len(TRANSIENT_SCENARIOS) * (len(boundary_indices) + 1)
    )
    if len(prima_extended_sweep_rows) != expected_extended_rows:
        raise RuntimeError(
            f"expected {expected_extended_rows} extended order/transient rows, "
            f"got {len(prima_extended_sweep_rows)}"
        )
    write_csv(prima_extended_sweep_path, prima_extended_sweep_rows)

    max_admittance_error = max(
        float(row["port_admittance_frobenius_error_pct"]) for row in summary_rows
    )
    max_impedance_error = max(
        float(row["port_impedance_frobenius_error_pct"]) for row in summary_rows
    )
    print(f"NEURON={neuron.__version__}")
    print(f"PRIMA_order={prima_model.order}/{cable.n_compartments}; state_reduction_pct={100.0 * (1.0-prima_model.order/cable.n_compartments):.9g}; requested_cap={PRIMA_MAX_ORDER}")
    print(f"PRIMA_multishift_order={prima_multishift_model.order}/{cable.n_compartments}; expansion_frequencies_hz={PRIMA_MULTI_SHIFT_HZ}")
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
    print(f"prima_reduction_csv={prima_path}; rows={len(prima_rows)}")
    print(f"prima_multishift_reduction_csv={prima_multishift_path}; rows={len(prima_multishift_rows)}")
    print(f"prima_multishift_extended_reduction_csv={prima_multishift_extended_path}; rows={len(prima_multishift_extended_rows)}")
    print(f"prima_multishift_order_sweep_csv={prima_sweep_path}; rows={len(prima_sweep_rows)}; orders={tuple(prima_order_sweep_models)}")
    print(f"prima_extended_order_transient_sweep_csv={prima_extended_sweep_path}; rows={len(prima_extended_sweep_rows)}; models={tuple(prima_extended_order_sweep_models)}; scenarios={len(TRANSIENT_SCENARIOS)}")
    max_multi_z = max(float(row["impedance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    max_multi_y = max(float(row["admittance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    multi_transient = next(row for row in prima_multishift_rows if row["metric"] == "transient_all_ports")
    max_multi_z_neuron = max(float(row["neuron_impedance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    max_multi_y_neuron = max(float(row["neuron_admittance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    print("PRIMA_multishift_port_impedance_error_pct_max=%.12g; PRIMA_multishift_port_admittance_error_pct_max=%.12g; PRIMA_multishift_Z_vs_NEURON_pct_max=%.12g; PRIMA_multishift_Y_vs_NEURON_pct_max=%.12g; PRIMA_multishift_transient_all_ports_NRMSE_pct=%.12g" % (max_multi_z, max_multi_y, max_multi_z_neuron, max_multi_y_neuron, multi_transient["transient_port_nrmse_pct"]))
    extended_frequency_rows = [row for row in prima_multishift_extended_rows if row["metric"] == "frequency_response"]
    extended_transient = next(row for row in prima_multishift_extended_rows if row["metric"] == "transient_all_ports")
    print("PRIMA_multishift_extended_Z_vs_AMSN_pct_max=%.12g; PRIMA_multishift_extended_Y_vs_AMSN_pct_max=%.12g; PRIMA_multishift_extended_Z_vs_NEURON_pct_max=%.12g; PRIMA_multishift_extended_Y_vs_NEURON_pct_max=%.12g; transient_all_ports_NRMSE_pct=%.12g" % (
        max(float(row["impedance_frobenius_error_pct"]) for row in extended_frequency_rows),
        max(float(row["admittance_frobenius_error_pct"]) for row in extended_frequency_rows),
        max(float(row["neuron_impedance_frobenius_error_pct"]) for row in extended_frequency_rows),
        max(float(row["neuron_admittance_frobenius_error_pct"]) for row in extended_frequency_rows),
        extended_transient["transient_port_nrmse_pct"],
    ))
    for order in prima_order_sweep_models:
        subset = [row for row in prima_sweep_rows if row["metric"] == "frequency_response" and int(row["prima_order"]) == order]
        max_z_sweep = max(float(row["impedance_frobenius_error_pct"]) for row in subset)
        max_y_sweep = max(float(row["admittance_frobenius_error_pct"]) for row in subset)
        max_z_neuron = max(float(row["neuron_impedance_frobenius_error_pct"]) for row in subset)
        max_y_neuron = max(float(row["neuron_admittance_frobenius_error_pct"]) for row in subset)
        trace_sweep = next(row for row in prima_sweep_rows if row["metric"] == "transient_all_ports" and row["reduction_method"] == f"multi_shift_order_{order}")
        print("PRIMA_order_sweep=%d; max_Z_pct=%.12g; max_Y_pct=%.12g; max_Z_vs_NEURON_pct=%.12g; max_Y_vs_NEURON_pct=%.12g; transient_all_ports_NRMSE_pct=%.12g" % (order, max_z_sweep, max_y_sweep, max_z_neuron, max_y_neuron, trace_sweep["transient_port_nrmse_pct"]))
    for model_id in prima_extended_order_sweep_models:
        frequency_subset = [
            row for row in prima_extended_sweep_rows
            if row["metric"] == "frequency_response" and row["model_id"] == model_id
        ]
        transient_subset = [
            row for row in prima_extended_sweep_rows
            if row["metric"] == "transient_all_ports" and row["reduction_method"] == model_id
        ]
        max_z_neuron = max(float(row["impedance_vs_neuron_pct"]) for row in frequency_subset)
        max_y_neuron = max(float(row["admittance_vs_neuron_pct"]) for row in frequency_subset)
        max_transient = max(float(row["transient_port_nrmse_pct"]) for row in transient_subset)
        print(
            f"EXTENDED_SWEEP={model_id}; "
            f"max_Z_vs_NEURON_pct={max_z_neuron:.12g}; "
            f"max_Y_vs_NEURON_pct={max_y_neuron:.12g}; "
            f"max_all_port_transient_NRMSE_pct={max_transient:.12g}"
        )
    max_prima_z = max(float(row["impedance_frobenius_error_pct"]) for row in prima_rows if row["metric"] == "frequency_response")
    max_multi_z_neuron = max(float(row["neuron_impedance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    max_multi_y_neuron = max(float(row["neuron_admittance_frobenius_error_pct"]) for row in prima_multishift_rows if row["metric"] == "frequency_response")
    max_prima_y = max(float(row["admittance_frobenius_error_pct"]) for row in prima_rows if row["metric"] == "frequency_response")
    global_transient = next(row for row in prima_rows if row["metric"] == "transient_all_ports")
    print("PRIMA_port_impedance_error_pct_max=%.12g; PRIMA_port_admittance_error_pct_max=%.12g; PRIMA_transient_all_ports_NRMSE_pct=%.12g" % (max_prima_z, max_prima_y, global_transient["transient_port_nrmse_pct"]))


if __name__ == "__main__":
    main()
