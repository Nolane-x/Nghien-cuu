"""Stress-test passive PRIMA basis transfer over source and pulse protocols."""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.cable import CableTree, PassiveParameters
from amsn.morphology import SWCMorphology
from amsn.prima import (
    prima_reduce_passive_cable_multishift,
    reproject_passive_cable_basis,
)
from amsn.robustness_metrics import (
    columnwise_relative_l2_percent,
    relative_l2_percent,
)

LABEL = os.environ["AMSN_MORPHOLOGY_LABEL"]
SWC = Path(os.environ["AMSN_MORPHOLOGY_PATH"])
EXPECTED = int(os.environ["AMSN_EXPECTED_SWC_RECORDS"])
ORDER = int(os.environ.get("AMSN_PRIMA_PARAMETER_ORDER", "56"))
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
BASE_SHIFTS_HZ = (0.0, 100.0, 1000.0, 3000.0)
EXTENDED_SHIFTS_HZ = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
MODEL_ORDER = (
    "frozen_nominal_3khz_basis",
    "fresh_3khz_basis",
    "fresh_extended_10khz_basis",
)
PULSE_WIDTHS_MS = (2.0, 10.0)
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
DT_S = 0.1e-3
DURATION_S = 20e-3
PULSE_ONSET_S = 2e-3
CURRENT_A = 10e-12


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


def run_transient_protocol(
    tree: CableTree,
    models: dict[str, object],
    ports: list[int],
    source_port: int,
    pulse_width_ms: float,
):
    """Run one Hines reference while advancing every reduced model in parallel."""
    steps = int(round(DURATION_S / DT_S))
    pulse_end_s = PULSE_ONSET_S + pulse_width_ms * 1e-3
    leak = tree.parameters.e_leak_v
    voltage = np.full(tree.n_compartments, leak, dtype=float)
    full_current = np.zeros(tree.n_compartments, dtype=float)
    port_current = np.zeros(len(ports), dtype=float)
    states = {name: np.zeros(model.order, dtype=float) for name, model in models.items()}
    full_trace = np.empty((steps, len(ports)), dtype=float)
    reduced_traces = {
        name: np.empty((steps, len(ports)), dtype=float) for name in models
    }

    for step in range(steps):
        time_s = step * DT_S
        injected = PULSE_ONSET_S <= time_s < pulse_end_s
        full_current.fill(0.0)
        port_current.fill(0.0)
        if injected:
            full_current[ports[source_port]] = CURRENT_A
            port_current[source_port] = CURRENT_A

        voltage = tree.step_passive(voltage, DT_S, full_current)
        full_trace[step] = voltage[ports] - leak
        for name, model in models.items():
            states[name] = model.step_backward_euler(states[name], DT_S, port_current)
            reduced_traces[name][step] = model.port_voltages(states[name])

    results = {}
    for name, trace in reduced_traces.items():
        port_errors = columnwise_relative_l2_percent(full_trace, trace, axis=0)
        results[name] = {
            "overall_nrmse_pct": relative_l2_percent(full_trace, trace),
            "max_port_nrmse_pct": float(np.max(port_errors)),
            "port_nrmse_pct": port_errors,
        }
    return results


def write_rows(path: Path, rows: list[dict]):
    if not rows:
        raise RuntimeError(f"refusing to write an empty results file: {path}")
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
        raise RuntimeError(f"expected seven unique electrical ports, got {len(port_node_ids)}")

    electrical_mapping = morphology.electrical_node_mapping()
    port_names = {
        node_id: f"swc_{electrical_mapping[node_id]}" for node_id in port_node_ids
    }
    base = morphology.to_cable_tree()
    ports = [base.index[port_names[node_id]] for node_id in port_node_ids]
    port_roles = {node_id: [] for node_id in port_node_ids}
    for name, node_id in injections + probes:
        if name not in port_roles[node_id]:
            port_roles[node_id].append(name)
    source_port_indices = {
        name: port_node_ids.index(node_id) for name, node_id in injections
    }
    if set(source_port_indices) != set(SOURCE_NAMES):
        raise RuntimeError(f"source set mismatch: {sorted(source_port_indices)}")

    nominal_model = prima_reduce_passive_cable_multishift(
        base, ports, ORDER, BASE_SHIFTS_HZ
    )
    p0 = base.parameters
    frequency_rows: list[dict] = []
    transient_rows: list[dict] = []
    model_rows: list[dict] = []

    for case_name, (rm_scale, cm_scale, ra_scale) in parameter_cases().items():
        parameters = PassiveParameters(
            specific_capacitance_f_m2=p0.specific_capacitance_f_m2 * cm_scale,
            specific_membrane_resistance_ohm_m2=(
                p0.specific_membrane_resistance_ohm_m2 * rm_scale
            ),
            axial_resistivity_ohm_m=p0.axial_resistivity_ohm_m * ra_scale,
            e_leak_v=p0.e_leak_v,
        )
        target = CableTree([base.by_name[name] for name in base.order], parameters)
        models = {
            "frozen_nominal_3khz_basis": reproject_passive_cable_basis(
                base, target, nominal_model
            ),
            "fresh_3khz_basis": prima_reduce_passive_cable_multishift(
                target, ports, ORDER, BASE_SHIFTS_HZ
            ),
            "fresh_extended_10khz_basis": prima_reduce_passive_cable_multishift(
                target, ports, ORDER, EXTENDED_SHIFTS_HZ
            ),
        }

        for model_name, model in models.items():
            try:
                np.linalg.cholesky(model.conductance_matrix_s)
                np.linalg.cholesky(model.capacitance_matrix_f)
                passivity = "cholesky_passed"
            except np.linalg.LinAlgError as exc:
                raise RuntimeError(
                    f"reduced model lost positive definiteness: {case_name}/{model_name}"
                ) from exc
            if model.order <= 0 or not np.all(np.isfinite(model.basis)):
                raise RuntimeError(f"invalid reduced basis: {case_name}/{model_name}")
            model_rows.append({
                "morphology_label": LABEL,
                "parameter_scenario": case_name,
                "Rm_scale": rm_scale,
                "Cm_scale": cm_scale,
                "Ra_scale": ra_scale,
                "full_compartment_order": target.n_compartments,
                "requested_order": ORDER,
                "actual_order": model.order,
                "state_reduction_pct": 100.0 * (1.0 - model.order / target.n_compartments),
                "model_id": model_name,
                "expansion_shifts_hz": ";".join(
                    str(x) for x in (
                        EXTENDED_SHIFTS_HZ
                        if model_name == "fresh_extended_10khz_basis"
                        else BASE_SHIFTS_HZ
                    )
                ),
                "passivity_check": passivity,
            })

        for frequency_hz in FREQUENCIES_HZ:
            full_z = port_impedance(target, ports, frequency_hz)
            full_y = np.linalg.solve(full_z, np.eye(len(ports)))
            for model_name, model in models.items():
                reduced_z = model.impedance_matrix(frequency_hz)
                reduced_y = model.admittance_matrix(frequency_hz)
                frequency_rows.append({
                    "morphology_label": LABEL,
                    "parameter_scenario": case_name,
                    "Rm_scale": rm_scale,
                    "Cm_scale": cm_scale,
                    "Ra_scale": ra_scale,
                    "model_id": model_name,
                    "requested_order": ORDER,
                    "actual_order": model.order,
                    "frequency_hz": frequency_hz,
                    "z_error_vs_hines_pct": relative_l2_percent(full_z, reduced_z),
                    "y_error_vs_hines_pct": relative_l2_percent(full_y, reduced_y),
                    "neuron_mesh_cap_um": 0.125,
                    "port_count": len(ports),
                })

        for source_name in SOURCE_NAMES:
            source_port = source_port_indices[source_name]
            for pulse_width_ms in PULSE_WIDTHS_MS:
                transient_metrics = run_transient_protocol(
                    target, models, ports, source_port, pulse_width_ms
                )
                for model_name, metrics in transient_metrics.items():
                    for port_index, node_id in enumerate(port_node_ids):
                        transient_rows.append({
                            "morphology_label": LABEL,
                            "parameter_scenario": case_name,
                            "Rm_scale": rm_scale,
                            "Cm_scale": cm_scale,
                            "Ra_scale": ra_scale,
                            "model_id": model_name,
                            "requested_order": ORDER,
                            "actual_order": models[model_name].order,
                            "source_name": source_name,
                            "source_swc_id": port_node_ids[source_port],
                            "pulse_shape": "square",
                            "pulse_width_ms": pulse_width_ms,
                            "pulse_onset_ms": PULSE_ONSET_S * 1000.0,
                            "pulse_amplitude_pA": CURRENT_A * 1e12,
                            "duration_ms": DURATION_S * 1000.0,
                            "dt_ms": DT_S * 1000.0,
                            "port_swc_id": node_id,
                            "port_roles": ";".join(port_roles[node_id]),
                            "overall_nrmse_pct": metrics["overall_nrmse_pct"],
                            "max_port_nrmse_pct": metrics["max_port_nrmse_pct"],
                            "port_nrmse_pct": float(metrics["port_nrmse_pct"][port_index]),
                        })

    output = Path(__file__).parents[1] / "results"
    stem = f"{LABEL}_human_prima_basis_transfer_protocol_robustness_2026-11-22"
    write_rows(output / f"{stem}_model_summary.csv", model_rows)
    write_rows(output / f"{stem}_frequency.csv", frequency_rows)
    write_rows(output / f"{stem}_transient.csv", transient_rows)

    expected_frequency = len(parameter_cases()) * len(MODEL_ORDER) * len(FREQUENCIES_HZ)
    expected_transient = (
        len(parameter_cases()) * len(MODEL_ORDER) * len(SOURCE_NAMES)
        * len(PULSE_WIDTHS_MS) * len(ports)
    )
    if len(model_rows) != len(parameter_cases()) * len(MODEL_ORDER):
        raise RuntimeError(f"model coverage mismatch: {len(model_rows)}")
    if len(frequency_rows) != expected_frequency:
        raise RuntimeError(
            f"frequency coverage mismatch: {len(frequency_rows)} != {expected_frequency}"
        )
    if len(transient_rows) != expected_transient:
        raise RuntimeError(
            f"transient coverage mismatch: {len(transient_rows)} != {expected_transient}"
        )

    print(
        f"morphology={LABEL}; compartments={base.n_compartments}; ports={len(ports)}; "
        f"models={len(model_rows)}; frequency_rows={len(frequency_rows)}; "
        f"transient_port_rows={len(transient_rows)}; passivity=passed"
    )
    for model_name in MODEL_ORDER:
        frows = [row for row in frequency_rows if row["model_id"] == model_name]
        trows = [row for row in transient_rows if row["model_id"] == model_name]
        print(
            f"model={model_name}; "
            f"max_Z_error={max(float(r['z_error_vs_hines_pct']) for r in frows):.9g}%; "
            f"max_Y_error={max(float(r['y_error_vs_hines_pct']) for r in frows):.9g}%; "
            f"median_port_transient={np.median([float(r['port_nrmse_pct']) for r in trows]):.9g}%; "
            f"max_port_transient={max(float(r['port_nrmse_pct']) for r in trows):.9g}%"
        )
    print(f"results_dir={output}; csv_files=3")


if __name__ == "__main__":
    main()
