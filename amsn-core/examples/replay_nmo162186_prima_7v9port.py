#!/usr/bin/env python3
"""Matched 7-port/9-port PRIMA validation on the independent NMO_162186 holdout.

The same SWC, passive parameter scenarios, source sites, square-pulse protocol,
six expansion shifts and achieved basis orders are used for both port sets.
The 9-port set adds only basal-q25 and apical-q25 output probes. Comparisons
pair shared outputs by exact SWC node ID and retain q25-only errors separately.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

import human_fine_mesh_passive_dc_audit as fine_audit
import human_prima_port_enrichment as port_enrichment
import neuron_cross_validation as reference
from amsn.cable import CableTree, PassiveParameters
from amsn.morphology import SWCMorphology
from amsn.prima import prima_reduce_passive_cable_multishift

LABEL = "NMO_162186_AllenL23"
SWC = Path("data/human/allen_cell_types/770307286_transformed.CNG.swc")
EXPECTED_SWC_RECORDS = 7287
EXPECTED_SWC_SHA256 = "a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc"
ORDERS = (112, 168)
SHIFTS = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
STRATEGY = "extended_10khz"
PORT_COUNTS = (7, 9)
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS_MS = (2.0, 10.0)
DT_S = 0.1e-3
DURATION_S = 20e-3
PULSE_ONSET_S = 2e-3
CURRENT_A = 10e-12
EXPECTED_SCENARIOS = 9
EXPECTED_MODEL_ROWS = len(PORT_COUNTS) * len(ORDERS) * EXPECTED_SCENARIOS
EXPECTED_FREQUENCY_ROWS = EXPECTED_MODEL_ROWS * len(FREQUENCIES_HZ)
EXPECTED_TRANSIENT_ROWS = (
    EXPECTED_SCENARIOS * len(ORDERS) * len(SOURCE_NAMES) *
    len(PULSE_WIDTHS_MS) * (7 + 9)
)
EXPECTED_SHARED_ROWS = (
    EXPECTED_SCENARIOS * len(ORDERS) * len(SOURCE_NAMES) *
    len(PULSE_WIDTHS_MS) * 7
)
EXPECTED_Q25_ROWS = (
    EXPECTED_SCENARIOS * len(ORDERS) * len(SOURCE_NAMES) *
    len(PULSE_WIDTHS_MS) * 2
)
EXPECTED_HINES_SHARED_ROWS = (
    EXPECTED_SCENARIOS * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7
)


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


def run_reduced_transient(model, port_count: int, source_port: int, pulse_width_ms: float):
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


def validate_port_node_sets(
    seven_node_ids: list[int],
    nine_node_ids: list[int],
    nine_roles_by_node: dict[int, list[str]],
) -> tuple[list[int], list[int]]:
    """Require 7 canonical shared nodes plus exactly two q25-only probes."""
    seven = set(seven_node_ids)
    nine = set(nine_node_ids)
    if len(seven_node_ids) != 7 or len(seven) != 7:
        raise ValueError("seven-port layout must contain seven unique SWC node IDs")
    if len(nine_node_ids) != 9 or len(nine) != 9:
        raise ValueError("nine-port layout must contain nine unique SWC node IDs")
    if not seven.issubset(nine):
        raise ValueError("the nine-port layout does not preserve all seven canonical SWC nodes")
    extra = nine - seven
    if len(extra) != 2:
        raise ValueError(f"expected exactly two q25-only probes, found {len(extra)}")
    extra_role_names = {
        role.lower()
        for node_id in extra
        for role in nine_roles_by_node.get(node_id, [])
    }
    if not any("basal_q25" in role for role in extra_role_names):
        raise ValueError("nine-port layout is missing the basal-q25-only probe")
    if not any("apical_q25" in role for role in extra_role_names):
        raise ValueError("nine-port layout is missing the apical-q25-only probe")
    return sorted(seven), sorted(extra)


def build_port_layouts(morphology, reader, sections, base: CableTree):
    injections7, probes7, mapped7 = fine_audit.build_sites(morphology, reader, sections)
    injections9, probes9, mapped9 = port_enrichment.build_sites(
        morphology, reader, sections, extra_probe_quantiles=(0.25,)
    )

    def make_layout(port_count, injections, probes, mapped):
        node_ids = list(dict.fromkeys(node_id for _, node_id in injections + probes))
        if len(node_ids) != port_count:
            raise RuntimeError(f"expected {port_count} retained SWC ports, got {len(node_ids)}")
        electrical_map = morphology.electrical_node_mapping()
        port_names = {
            node_id: f"swc_{electrical_map[node_id]}"
            for node_id in node_ids
        }
        ports = [base.index[port_names[node_id]] for node_id in node_ids]
        roles = {node_id: [] for node_id in node_ids}
        for role, node_id in injections + probes:
            if role not in roles[node_id]:
                roles[node_id].append(role)
        source_ids = {role: node_id for role, node_id in injections}
        if set(source_ids) != set(SOURCE_NAMES):
            raise RuntimeError(f"source coverage mismatch in {port_count}-port layout: {source_ids}")
        source_indices = {role: node_ids.index(node_id) for role, node_id in source_ids.items()}
        return {
            "port_count": port_count,
            "node_ids": node_ids,
            "ports": ports,
            "roles": roles,
            "source_ids": source_ids,
            "source_indices": source_indices,
            "mapping": mapped,
        }

    seven = make_layout(7, injections7, probes7, mapped7)
    nine = make_layout(9, injections9, probes9, mapped9)
    if seven["source_ids"] != nine["source_ids"]:
        raise RuntimeError("seven-port and nine-port source SWC node IDs differ")
    common, q25_extra = validate_port_node_sets(
        seven["node_ids"], nine["node_ids"], nine["roles"]
    )
    if set(common) != set(seven["node_ids"]):
        raise RuntimeError("canonical shared-port SWC identity check failed")
    if len(q25_extra) != 2:
        raise RuntimeError("q25 probe coverage check failed")
    return {7: seven, 9: nine}, common, q25_extra


def build_matched_shared_rows(transient_rows: list[dict], common_node_ids: list[int]) -> list[dict]:
    index = {}
    for row in transient_rows:
        if row["port_count"] not in (7, 9):
            continue
        if int(row["port_swc_id"]) not in common_node_ids:
            continue
        key = (
            int(row["basis_order"]),
            row["parameter_scenario"],
            row["source_name"],
            float(row["pulse_width_ms"]),
            int(row["port_swc_id"]),
        )
        index[(row["port_count"], *key)] = row
    keys7 = {key[1:] for key in index if key[0] == 7}
    keys9 = {key[1:] for key in index if key[0] == 9}
    if keys7 != keys9 or len(keys7) != EXPECTED_SHARED_ROWS:
        raise ValueError(
            f"matched shared output coverage mismatch: 7-port={len(keys7)}, "
            f"9-port={len(keys9)}, expected={EXPECTED_SHARED_ROWS}"
        )
    result = []
    for key in sorted(keys7):
        seven = index[(7, *key)]
        nine = index[(9, *key)]
        e7 = float(seven["port_nrmse_pct"])
        e9 = float(nine["port_nrmse_pct"])
        ratio = e9 / e7 if e7 > 0 else (1.0 if e9 == 0 else None)
        result.append({
            "basis_order": key[0],
            "parameter_scenario": key[1],
            "source_name": key[2],
            "pulse_width_ms": key[3],
            "port_swc_id": key[4],
            "port_roles": seven["port_roles"],
            "seven_port_nrmse_pct": e7,
            "nine_port_nrmse_pct": e9,
            "error_ratio_nine_over_seven": ratio,
            "nine_port_minus_seven_port_pct_points": e9 - e7,
        })
    return result


def summarize_matched_rows(rows: list[dict]) -> list[dict]:
    result = []
    for order in ORDERS:
        subset = [row for row in rows if int(row["basis_order"]) == order]
        finite_ratios = [
            float(row["error_ratio_nine_over_seven"])
            for row in subset if row["error_ratio_nine_over_seven"] is not None
        ]
        result.append({
            "basis_order": order,
            "matched_shared_output_pairs": len(subset),
            "nine_port_worse_pairs": sum(
                float(row["nine_port_nrmse_pct"]) > float(row["seven_port_nrmse_pct"]) + 1e-15
                for row in subset
            ),
            "nine_port_better_pairs": sum(
                float(row["nine_port_nrmse_pct"]) < float(row["seven_port_nrmse_pct"]) - 1e-15
                for row in subset
            ),
            "ties_within_1e_15_pct_points": sum(
                abs(float(row["nine_port_minus_seven_port_pct_points"])) <= 1e-15
                for row in subset
            ),
            "median_error_ratio_nine_over_seven": (
                float(np.median(finite_ratios)) if finite_ratios else None
            ),
            "max_error_ratio_nine_over_seven": max(finite_ratios) if finite_ratios else None,
            "max_seven_port_nrmse_pct": max(float(row["seven_port_nrmse_pct"]) for row in subset),
            "max_nine_port_nrmse_pct": max(float(row["nine_port_nrmse_pct"]) for row in subset),
        })
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty results CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def expected_counts() -> dict[str, int]:
    return {
        "models": EXPECTED_MODEL_ROWS,
        "frequency": EXPECTED_FREQUENCY_ROWS,
        "transient": EXPECTED_TRANSIENT_ROWS,
        "matched_shared": EXPECTED_SHARED_ROWS,
        "q25_only": EXPECTED_Q25_ROWS,
        "hines_shared": EXPECTED_HINES_SHARED_ROWS,
    }


def main():
    reference.DATA = SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.125
    morphology = SWCMorphology.from_file(SWC)
    if len(morphology.nodes) != EXPECTED_SWC_RECORDS:
        raise RuntimeError(
            f"SWC record count {len(morphology.nodes)} != {EXPECTED_SWC_RECORDS}"
        )
    digest = hashlib.sha256(SWC.read_bytes()).hexdigest()
    if digest != EXPECTED_SWC_SHA256:
        raise RuntimeError(f"SWC SHA-256 mismatch: {digest}")

    preflight_path = Path("results/NMO_162186_holdout_preflight/preflight.json")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("source_sha256") != EXPECTED_SWC_SHA256:
        raise RuntimeError("preflight SWC digest differs from the replay source")
    if int(preflight.get("amsn_unique_port_count", 0)) != 7:
        raise RuntimeError("the seven-port preflight does not contain exactly seven canonical ports")

    reader, sections = reference.import_swc_with_neuron()
    base = morphology.to_cable_tree()
    layouts, common_node_ids, q25_extra_node_ids = build_port_layouts(
        morphology, reader, sections, base
    )
    base_parameters = base.parameters

    model_rows = []
    frequency_rows = []
    transient_rows = []
    hines_shared_rows = []
    parameter_data = parameter_cases()

    for scenario, (rm_scale, cm_scale, ra_scale) in parameter_data.items():
        target_parameters = PassiveParameters(
            specific_capacitance_f_m2=base_parameters.specific_capacitance_f_m2 * cm_scale,
            specific_membrane_resistance_ohm_m2=base_parameters.specific_membrane_resistance_ohm_m2 * rm_scale,
            axial_resistivity_ohm_m=base_parameters.axial_resistivity_ohm_m * ra_scale,
            e_leak_v=base_parameters.e_leak_v,
        )
        target = CableTree(
            [base.by_name[name] for name in base.order],
            target_parameters,
        )

        # Compute full-Hines traces for both output sets once per scenario.
        hines_cache = {}
        for port_count in PORT_COUNTS:
            layout = layouts[port_count]
            for source_name in SOURCE_NAMES:
                source_port = layout["source_indices"][source_name]
                for pulse_width_ms in PULSE_WIDTHS_MS:
                    trace, seconds = run_full_hines_transient(
                        target, layout["ports"], source_port, pulse_width_ms
                    )
                    hines_cache[(port_count, source_name, pulse_width_ms)] = {
                        "trace": trace,
                        "seconds": seconds,
                    }

        # Verify that the seven shared Hines traces are identical regardless
        # of whether seven or nine output probes were requested.
        index7 = {node_id: i for i, node_id in enumerate(layouts[7]["node_ids"])}
        index9 = {node_id: i for i, node_id in enumerate(layouts[9]["node_ids"])}
        for source_name in SOURCE_NAMES:
            for pulse_width_ms in PULSE_WIDTHS_MS:
                trace7 = hines_cache[(7, source_name, pulse_width_ms)]["trace"]
                trace9 = hines_cache[(9, source_name, pulse_width_ms)]["trace"]
                for node_id in common_node_ids:
                    a = trace7[:, index7[node_id]]
                    b = trace9[:, index9[node_id]]
                    difference = np.abs(a - b)
                    hines_shared_rows.append({
                        "parameter_scenario": scenario,
                        "source_name": source_name,
                        "pulse_width_ms": pulse_width_ms,
                        "port_swc_id": node_id,
                        "max_absolute_hines_trace_difference_v": float(np.max(difference)),
                        "relative_l2_difference_pct": relative_l2_percent(a, b),
                    })

        for port_count in PORT_COUNTS:
            layout = layouts[port_count]
            ports = layout["ports"]
            node_ids = layout["node_ids"]
            roles = layout["roles"]
            source_indices = layout["source_indices"]
            models = {}

            for order in ORDERS:
                model_id = f"order{order}_extended_10khz"
                started = time.perf_counter()
                model = prima_reduce_passive_cable_multishift(
                    target, ports, order, SHIFTS
                )
                build_seconds = time.perf_counter() - started
                if model.order != order:
                    raise RuntimeError(
                        f"{port_count}-port {model_id}: achieved order {model.order}, expected {order}"
                    )
                np.linalg.cholesky(model.conductance_matrix_s)
                np.linalg.cholesky(model.capacitance_matrix_f)
                if not np.all(np.isfinite(model.basis)):
                    raise RuntimeError(f"{port_count}-port {model_id} has non-finite basis values")
                basis_bytes = int(model.basis.nbytes)
                reduced_bytes = int(
                    model.conductance_matrix_s.nbytes + model.capacitance_matrix_f.nbytes
                )
                numeric_bytes = basis_bytes + reduced_bytes
                models[order] = model
                model_rows.append({
                    "morphology_label": LABEL,
                    "port_count": port_count,
                    "basis_order": order,
                    "model_id": model_id,
                    "parameter_scenario": scenario,
                    "expansion_shifts_hz": ";".join(str(value) for value in SHIFTS),
                    "full_compartment_order": target.n_compartments,
                    "state_reduction_pct": 100.0 * (1.0 - order / target.n_compartments),
                    "basis_build_wall_seconds": build_seconds,
                    "basis_bytes": basis_bytes,
                    "reduced_matrix_bytes": reduced_bytes,
                    "numeric_storage_bytes": numeric_bytes,
                    "passivity_check": "cholesky_passed",
                    "retained_port_swc_ids": ";".join(str(x) for x in node_ids),
                })

            identity = np.eye(port_count, dtype=float)
            for frequency_hz in FREQUENCIES_HZ:
                full_z = port_impedance(target, ports, frequency_hz)
                full_y = np.linalg.solve(full_z, identity)
                for order, model in models.items():
                    reduced_z = model.impedance_matrix(frequency_hz)
                    reduced_y = np.linalg.solve(reduced_z, identity)
                    frequency_rows.append({
                        "morphology_label": LABEL,
                        "port_count": port_count,
                        "basis_order": order,
                        "model_id": f"order{order}_extended_10khz",
                        "parameter_scenario": scenario,
                        "frequency_hz": frequency_hz,
                        "z_error_vs_hines_pct": relative_l2_percent(full_z, reduced_z),
                        "y_error_vs_hines_pct": relative_l2_percent(full_y, reduced_y),
                    })

            for order, model in models.items():
                model_id = f"order{order}_extended_10khz"
                for source_name in SOURCE_NAMES:
                    source_port = source_indices[source_name]
                    for pulse_width_ms in PULSE_WIDTHS_MS:
                        hines = hines_cache[(port_count, source_name, pulse_width_ms)]
                        reduced_trace, reduced_seconds = run_reduced_transient(
                            model, port_count, source_port, pulse_width_ms
                        )
                        full_trace = hines["trace"]
                        errors = [
                            relative_l2_percent(full_trace[:, i], reduced_trace[:, i])
                            for i in range(port_count)
                        ]
                        overall_error = relative_l2_percent(full_trace, reduced_trace)
                        max_error = max(errors)
                        for index, node_id in enumerate(node_ids):
                            transient_rows.append({
                                "morphology_label": LABEL,
                                "port_count": port_count,
                                "basis_order": order,
                                "model_id": model_id,
                                "parameter_scenario": scenario,
                                "source_name": source_name,
                                "source_swc_id": layout["source_ids"][source_name],
                                "pulse_width_ms": pulse_width_ms,
                                "pulse_onset_ms": PULSE_ONSET_S * 1000.0,
                                "pulse_amplitude_pA": CURRENT_A * 1e12,
                                "duration_ms": DURATION_S * 1000.0,
                                "dt_ms": DT_S * 1000.0,
                                "port_swc_id": node_id,
                                "port_roles": ";".join(roles[node_id]),
                                "port_nrmse_pct": errors[index],
                                "overall_nrmse_pct": overall_error,
                                "max_port_nrmse_pct": max_error,
                                "full_hines_seconds": hines["seconds"],
                                "reduced_transient_seconds": reduced_seconds,
                            })

    matched_rows = build_matched_shared_rows(transient_rows, common_node_ids)
    matched_summary = summarize_matched_rows(matched_rows)
    q25_rows = [
        row for row in transient_rows
        if row["port_count"] == 9
        and any("q25" in role.lower() for role in row["port_roles"].split(";"))
    ]
    q25_summary = []
    for order in ORDERS:
        values = [
            float(row["port_nrmse_pct"])
            for row in q25_rows if int(row["basis_order"]) == order
        ]
        q25_summary.append({
            "basis_order": order,
            "q25_observations": len(values),
            "median_q25_nrmse_pct": float(np.median(values)),
            "max_q25_nrmse_pct": max(values),
        })

    expected = expected_counts()
    actual = {
        "models": len(model_rows),
        "frequency": len(frequency_rows),
        "transient": len(transient_rows),
        "matched_shared": len(matched_rows),
        "q25_only": len(q25_rows),
        "hines_shared": len(hines_shared_rows),
    }
    if actual != expected:
        raise RuntimeError(f"exact matrix coverage mismatch: actual={actual}; expected={expected}")
    if any(
        not math.isfinite(float(row["max_absolute_hines_trace_difference_v"]))
        for row in hines_shared_rows
    ):
        raise RuntimeError("non-finite shared Hines reference comparison")
    if any(
        float(row["max_absolute_hines_trace_difference_v"]) > 1e-15
        for row in hines_shared_rows
    ):
        raise RuntimeError("7-port and 9-port Hines references differ at a shared SWC output")

    # Four summary rows: one per port count and basis order.
    summary_rows = []
    for port_count in PORT_COUNTS:
        for order in ORDERS:
            models_subset = [
                row for row in model_rows
                if int(row["port_count"]) == port_count and int(row["basis_order"]) == order
            ]
            freq_subset = [
                row for row in frequency_rows
                if int(row["port_count"]) == port_count and int(row["basis_order"]) == order
            ]
            trans_subset = [
                row for row in transient_rows
                if int(row["port_count"]) == port_count and int(row["basis_order"]) == order
            ]
            freq10 = [row for row in freq_subset if float(row["frequency_hz"]) == 10000.0]
            zvals = [float(row["z_error_vs_hines_pct"]) for row in freq10]
            yvals = [float(row["y_error_vs_hines_pct"]) for row in freq10]
            tvals = [float(row["port_nrmse_pct"]) for row in trans_subset]
            storage = [int(row["numeric_storage_bytes"]) for row in models_subset]
            builds = [float(row["basis_build_wall_seconds"]) for row in models_subset]
            summary_rows.append({
                "port_count": port_count,
                "basis_order": order,
                "model_scenario_rows": len(models_subset),
                "frequency_rows": len(freq_subset),
                "transient_port_rows": len(trans_subset),
                "median_z_error_10khz_pct": float(np.median(zvals)),
                "max_z_error_10khz_pct": max(zvals),
                "median_y_error_10khz_pct": float(np.median(yvals)),
                "max_y_error_10khz_pct": max(yvals),
                "median_transient_port_nrmse_pct": float(np.median(tvals)),
                "max_transient_port_nrmse_pct": max(tvals),
                "median_numeric_storage_mb": float(np.median(storage)) / (1024.0 * 1024.0),
                "median_basis_build_seconds": float(np.median(builds)),
            })

    results_dir = Path(__file__).parents[1] / "results"
    stem = "NMO_162186_prima_7v9port_matched_order_2026-11-23"
    outputs = {
        "models": model_rows,
        "frequency": frequency_rows,
        "transient": transient_rows,
        "matched_shared": matched_rows,
        "matched_summary": matched_summary,
        "q25": q25_rows,
        "q25_summary": q25_summary,
        "hines_shared": hines_shared_rows,
        "summary": summary_rows,
    }
    for suffix, rows in outputs.items():
        write_csv(results_dir / f"{stem}_{suffix}.csv", rows)

    report = {
        "schema_version": 1,
        "status": "matched_7port_9port_prima_holdout_replay_passed",
        "runtime_promotion": False,
        "morphology": {
            "label": LABEL,
            "swc_path": str(SWC),
            "swc_record_count": EXPECTED_SWC_RECORDS,
            "swc_sha256": digest,
            "preflight_sha256": preflight["source_sha256"],
            "electrical_compartments": base.n_compartments,
            "experimental_condition": "epilepsy surgical specimen",
            "axon_complete": False,
        },
        "protocol": {
            "orders": list(ORDERS),
            "shift_strategy": STRATEGY,
            "expansion_shifts_hz": list(SHIFTS),
            "parameter_scenarios": list(parameter_data),
            "frequencies_hz": list(FREQUENCIES_HZ),
            "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_onset_ms": PULSE_ONSET_S * 1000.0,
            "pulse_amplitude_pA": CURRENT_A * 1e12,
            "duration_ms": DURATION_S * 1000.0,
            "dt_ms": DT_S * 1000.0,
            "mesh_max_segment_um": 0.125,
        },
        "port_layouts": {
            str(port_count): {
                "node_ids": layout["node_ids"],
                "roles_by_node": {str(node): layout["roles"][node] for node in layout["node_ids"]},
                "source_ids": layout["source_ids"],
            }
            for port_count, layout in layouts.items()
        },
        "shared_swc_node_ids": common_node_ids,
        "q25_only_swc_node_ids": q25_extra_node_ids,
        "exact_coverage": actual,
        "matched_shared_summary": matched_summary,
        "q25_summary": q25_summary,
        "model_summary": summary_rows,
        "scientific_limits": [
            "This is a passive linear-RC numerical comparison against full Hines on one independent morphology.",
            "The two port layouts share exactly seven SWC node IDs; the nine-port layout adds basal-q25 and apical-q25 only.",
            "Orders 112 and 168 use identical six-shift extended-10kHz expansion frequencies for both port counts.",
            "The morphology is one epilepsy surgical specimen with incomplete axon; it is not a healthy control or representative human population.",
            "The comparison does not establish active-channel, nonlinear-synapse, plasticity or biological validity.",
            "No production order default, canonical Hines reference or runtime behavior is modified.",
        ],
        "runtime": {
            "python": __import__("platform").python_version(),
            "numpy": np.__version__,
            "neuron": __import__("neuron").__version__,
        },
    }
    (results_dir / f"{stem}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "exact_coverage": actual,
        "matched_summary": matched_summary,
        "q25_summary": q25_summary,
        "model_summary": summary_rows,
        "results_dir": str(results_dir),
        "stem": stem,
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
