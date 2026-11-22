"""Pareto sweep of passive PRIMA basis order and expansion-shift distribution.

Candidates are compared at identical parameter scenarios, source sites, pulse
widths, output SWC nodes and full Hines references. This is a passive linear
RC experiment; it does not model active channels or nonlinear synapses.
"""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import numpy as np

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.cable import CableTree, PassiveParameters
from amsn.morphology import SWCMorphology
from amsn.prima import prima_reduce_passive_cable_multishift

LABEL = os.environ["AMSN_MORPHOLOGY_LABEL"]
SWC = Path(os.environ["AMSN_MORPHOLOGY_PATH"])
EXPECTED = int(os.environ["AMSN_EXPECTED_SWC_RECORDS"])

ORDERS = (56, 84, 112)
SHIFT_SETS = {
    "narrow_3khz": (0.0, 100.0, 1000.0, 3000.0),
    "extended_10khz": (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0),
    "balanced_10khz": (0.0, 10.0, 100.0, 1000.0, 3000.0, 10000.0),
}
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS_MS = (2.0, 10.0)
DT_S = 0.1e-3
DURATION_S = 20e-3
PULSE_ONSET_S = 2e-3
CURRENT_A = 10e-12
EXPECTED_MODEL_ROWS = 9 * 9
EXPECTED_FREQUENCY_ROWS = 9 * 9 * len(FREQUENCIES_HZ)
EXPECTED_TRANSIENT_ROWS = 9 * 9 * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7


def relative_l2_percent(reference_values, approximation_values) -> float:
    reference_array = np.asarray(reference_values)
    approximation_array = np.asarray(approximation_values)
    if reference_array.shape != approximation_array.shape:
        raise ValueError("reference and approximation arrays have different shapes")
    if not np.all(np.isfinite(reference_array)) or not np.all(np.isfinite(approximation_array)):
        raise ValueError("relative L2 metric received non-finite values")
    denominator = max(float(np.linalg.norm(reference_array)), 1e-30)
    return float(100.0 * np.linalg.norm(approximation_array - reference_array) / denominator)


def port_impedance(tree: CableTree, ports: list[int], frequency_hz: float) -> np.ndarray:
    impedance = np.empty((len(ports), len(ports)), dtype=np.complex128)
    for column, source_index in enumerate(ports):
        current = np.zeros(tree.n_compartments, dtype=np.complex128)
        current[source_index] = 1.0
        response = tree.solve_passive_frequency_response(frequency_hz, current)
        impedance[:, column] = response[ports]
    return impedance


def parameter_cases():
    return {
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


def candidate_specs():
    return [
        {
            "model_id": f"order{order}_{strategy}",
            "order": order,
            "strategy": strategy,
            "shifts": shifts,
        }
        for order in ORDERS
        for strategy, shifts in SHIFT_SETS.items()
    ]


def run_full_hines_transient(
    tree: CableTree,
    ports: list[int],
    source_port: int,
    pulse_width_ms: float,
):
    steps = int(round(DURATION_S / DT_S))
    pulse_end_s = PULSE_ONSET_S + pulse_width_ms * 1e-3
    leak = tree.parameters.e_leak_v
    voltage = np.full(tree.n_compartments, leak, dtype=float)
    current = np.zeros(tree.n_compartments, dtype=float)
    trace = np.empty((steps, len(ports)), dtype=float)

    started = time.perf_counter()
    for step in range(steps):
        now_s = step * DT_S
        current.fill(0.0)
        if PULSE_ONSET_S <= now_s < pulse_end_s:
            current[ports[source_port]] = CURRENT_A
        voltage = tree.step_passive(voltage, DT_S, current)
        trace[step] = voltage[ports] - leak
    return trace, time.perf_counter() - started


def run_reduced_transient(
    model,
    port_count: int,
    source_port: int,
    pulse_width_ms: float,
):
    steps = int(round(DURATION_S / DT_S))
    pulse_end_s = PULSE_ONSET_S + pulse_width_ms * 1e-3
    state = np.zeros(model.order, dtype=float)
    current = np.zeros(port_count, dtype=float)
    trace = np.empty((steps, port_count), dtype=float)

    started = time.perf_counter()
    for step in range(steps):
        now_s = step * DT_S
        current.fill(0.0)
        if PULSE_ONSET_S <= now_s < pulse_end_s:
            current[source_port] = CURRENT_A
        state = model.step_backward_euler(state, DT_S, current)
        trace[step] = model.port_voltages(state)
    return trace, time.perf_counter() - started


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise RuntimeError(f"refusing to write empty results CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    reference.DATA = SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.125
    morphology = SWCMorphology.from_file(SWC)
    if len(morphology.nodes) != EXPECTED:
        raise RuntimeError(
            f"SWC record count {len(morphology.nodes)} != expected {EXPECTED}"
        )

    reader, sections = reference.import_swc_with_neuron()
    injections, probes, _ = fine_audit.build_sites(morphology, reader, sections)
    port_node_ids = list(dict.fromkeys(node_id for _, node_id in injections + probes))
    if len(port_node_ids) != 7:
        raise RuntimeError(f"expected seven unique retained ports, got {len(port_node_ids)}")

    electrical_mapping = morphology.electrical_node_mapping()
    port_names = {
        node_id: f"swc_{electrical_mapping[node_id]}" for node_id in port_node_ids
    }
    base = morphology.to_cable_tree()
    ports = [base.index[port_names[node_id]] for node_id in port_node_ids]
    roles = {node_id: [] for node_id in port_node_ids}
    for role, node_id in injections + probes:
        if role not in roles[node_id]:
            roles[node_id].append(role)
    source_indices = {
        role: port_node_ids.index(node_id) for role, node_id in injections
    }
    if set(source_indices) != set(SOURCE_NAMES):
        raise RuntimeError(f"source coverage mismatch: {sorted(source_indices)}")

    parameter_data = parameter_cases()
    specs = candidate_specs()
    if len(specs) != 9:
        raise RuntimeError(f"candidate matrix should contain 9 models, got {len(specs)}")

    model_rows = []
    frequency_rows = []
    transient_rows = []
    base_parameters = base.parameters

    for scenario, (rm_scale, cm_scale, ra_scale) in parameter_data.items():
        target_parameters = PassiveParameters(
            specific_capacitance_f_m2=(
                base_parameters.specific_capacitance_f_m2 * cm_scale
            ),
            specific_membrane_resistance_ohm_m2=(
                base_parameters.specific_membrane_resistance_ohm_m2 * rm_scale
            ),
            axial_resistivity_ohm_m=(
                base_parameters.axial_resistivity_ohm_m * ra_scale
            ),
            e_leak_v=base_parameters.e_leak_v,
        )
        target = CableTree(
            [base.by_name[name] for name in base.order],
            target_parameters,
        )
        models = {}
        metadata = {}

        for spec in specs:
            build_started = time.perf_counter()
            model = prima_reduce_passive_cable_multishift(
                target,
                ports,
                spec["order"],
                spec["shifts"],
            )
            build_seconds = time.perf_counter() - build_started
            if model.order != spec["order"]:
                raise RuntimeError(
                    f"candidate {spec['model_id']} achieved order {model.order}, "
                    f"expected {spec['order']}"
                )
            np.linalg.cholesky(model.conductance_matrix_s)
            np.linalg.cholesky(model.capacitance_matrix_f)
            if not np.all(np.isfinite(model.basis)):
                raise RuntimeError(f"candidate {spec['model_id']} has a non-finite basis")

            basis_bytes = int(model.basis.nbytes)
            conductance_bytes = int(model.conductance_matrix_s.nbytes)
            capacitance_bytes = int(model.capacitance_matrix_f.nbytes)
            matrix_bytes = conductance_bytes + capacitance_bytes
            metadata[spec["model_id"]] = {
                "order": model.order,
                "strategy": spec["strategy"],
                "shifts": ";".join(str(value) for value in spec["shifts"]),
                "build_seconds": build_seconds,
                "basis_bytes": basis_bytes,
                "reduced_matrix_bytes": matrix_bytes,
                "numeric_storage_bytes": basis_bytes + matrix_bytes,
            }
            models[spec["model_id"]] = model

        for spec in specs:
            model_id = spec["model_id"]
            details = metadata[model_id]
            model_rows.append({
                "morphology_label": LABEL,
                "parameter_scenario": scenario,
                "Rm_scale": rm_scale,
                "Cm_scale": cm_scale,
                "Ra_scale": ra_scale,
                "model_id": model_id,
                "basis_order_requested": spec["order"],
                "basis_order_actual": details["order"],
                "shift_strategy": spec["strategy"],
                "expansion_shifts_hz": details["shifts"],
                "full_compartment_order": target.n_compartments,
                "state_reduction_pct": 100.0 * (
                    1.0 - details["order"] / target.n_compartments
                ),
                "basis_build_wall_seconds": details["build_seconds"],
                "basis_bytes": details["basis_bytes"],
                "reduced_matrix_bytes": details["reduced_matrix_bytes"],
                "numeric_storage_bytes": details["numeric_storage_bytes"],
                "passivity_check": "cholesky_passed",
            })

        identity = np.eye(len(ports), dtype=float)
        for frequency_hz in FREQUENCIES_HZ:
            full_z = port_impedance(target, ports, frequency_hz)
            full_y = np.linalg.solve(full_z, identity)
            for spec in specs:
                model_id = spec["model_id"]
                model = models[model_id]
                reduced_z = model.impedance_matrix(frequency_hz)
                reduced_y = np.linalg.solve(reduced_z, identity)
                frequency_rows.append({
                    "morphology_label": LABEL,
                    "parameter_scenario": scenario,
                    "model_id": model_id,
                    "basis_order_requested": spec["order"],
                    "basis_order_actual": model.order,
                    "shift_strategy": spec["strategy"],
                    "frequency_hz": frequency_hz,
                    "z_error_vs_hines_pct": relative_l2_percent(full_z, reduced_z),
                    "y_error_vs_hines_pct": relative_l2_percent(full_y, reduced_y),
                })

        for source_name in SOURCE_NAMES:
            source_port = source_indices[source_name]
            for pulse_width_ms in PULSE_WIDTHS_MS:
                full_trace, full_seconds = run_full_hines_transient(
                    target, ports, source_port, pulse_width_ms
                )
                for spec in specs:
                    model_id = spec["model_id"]
                    model = models[model_id]
                    reduced_trace, reduced_seconds = run_reduced_transient(
                        model, len(ports), source_port, pulse_width_ms
                    )
                    port_errors = [
                        relative_l2_percent(full_trace[:, index], reduced_trace[:, index])
                        for index in range(len(ports))
                    ]
                    overall_error = relative_l2_percent(full_trace, reduced_trace)
                    max_error = max(port_errors)
                    for port_index, node_id in enumerate(port_node_ids):
                        transient_rows.append({
                            "morphology_label": LABEL,
                            "parameter_scenario": scenario,
                            "model_id": model_id,
                            "basis_order_requested": spec["order"],
                            "basis_order_actual": model.order,
                            "shift_strategy": spec["strategy"],
                            "source_name": source_name,
                            "source_swc_id": port_node_ids[source_port],
                            "pulse_shape": "square",
                            "pulse_width_ms": pulse_width_ms,
                            "pulse_onset_ms": PULSE_ONSET_S * 1000.0,
                            "pulse_amplitude_pA": CURRENT_A * 1e12,
                            "duration_ms": DURATION_S * 1000.0,
                            "dt_ms": DT_S * 1000.0,
                            "port_swc_id": node_id,
                            "port_roles": ";".join(roles[node_id]),
                            "port_nrmse_pct": port_errors[port_index],
                            "overall_nrmse_pct": overall_error,
                            "max_port_nrmse_pct": max_error,
                            "full_hines_seconds": full_seconds,
                            "reduced_transient_seconds": reduced_seconds,
                        })

    if len(model_rows) != EXPECTED_MODEL_ROWS:
        raise RuntimeError(f"model row coverage mismatch: {len(model_rows)}")
    if len(frequency_rows) != EXPECTED_FREQUENCY_ROWS:
        raise RuntimeError(f"frequency row coverage mismatch: {len(frequency_rows)}")
    if len(transient_rows) != EXPECTED_TRANSIENT_ROWS:
        raise RuntimeError(f"transient row coverage mismatch: {len(transient_rows)}")

    output = Path(__file__).parents[1] / "results"
    stem = f"{LABEL}_human_prima_shift_order_pareto_2026-11-22"
    write_csv(output / f"{stem}_models.csv", model_rows)
    write_csv(output / f"{stem}_frequency.csv", frequency_rows)
    write_csv(output / f"{stem}_transient.csv", transient_rows)

    print(
        f"morphology={LABEL}; compartments={base.n_compartments}; ports={len(ports)}; "
        f"model_rows={len(model_rows)}; frequency_rows={len(frequency_rows)}; "
        f"transient_rows={len(transient_rows)}; all_passivity_checks=passed"
    )
    for spec in specs:
        candidate_rows = [row for row in model_rows if row["model_id"] == spec["model_id"]]
        frows = [row for row in frequency_rows if row["model_id"] == spec["model_id"]]
        trows = [row for row in transient_rows if row["model_id"] == spec["model_id"]]
        print(
            f"candidate={spec['model_id']}; "
            f"median_build_s={np.median([float(row['basis_build_wall_seconds']) for row in candidate_rows]):.9g}; "
            f"median_Z_10khz_pct={np.median([float(row['z_error_vs_hines_pct']) for row in frows if float(row['frequency_hz']) == 10000.0]):.9g}; "
            f"median_Y_10khz_pct={np.median([float(row['y_error_vs_hines_pct']) for row in frows if float(row['frequency_hz']) == 10000.0]):.9g}; "
            f"median_transient_pct={np.median([float(row['port_nrmse_pct']) for row in trows]):.9g}; "
            f"max_transient_pct={max(float(row['port_nrmse_pct']) for row in trows):.9g}"
        )
    print(f"results_dir={output}; csv_files=3")


if __name__ == "__main__":
    main()
