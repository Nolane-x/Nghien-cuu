#!/usr/bin/env python3
"""Four-layout q25 ablation for the NMO_163775 Peng Control morphology.

Layouts:
  seven:            canonical seven ports
  eight_basal_q25:  canonical seven + basal-q25
  eight_apical_q25: canonical seven + apical-q25
  nine_both_q25:    canonical seven + both q25 probes

All layouts share the same SWC, passive scenarios, source nodes, orders,
frequency set, pulse protocol, NEURON mesh cap and full-Hines reference.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import replay_nmo163775_peng_7v9port as baseline

LABEL = baseline.LABEL
SWC = baseline.SWC
EXPECTED_SWC_RECORDS = baseline.EXPECTED_SWC_RECORDS
EXPECTED_SWC_SHA256 = baseline.EXPECTED_SWC_SHA256
ORDERS = baseline.ORDERS
SHIFTS = baseline.SHIFTS
FREQUENCIES_HZ = baseline.FREQUENCIES_HZ
SOURCE_NAMES = baseline.SOURCE_NAMES
PULSE_WIDTHS_MS = baseline.PULSE_WIDTHS_MS
LAYOUT_EXTRAS = {
    "seven": (),
    "eight_basal_q25": ("basal_q25",),
    "eight_apical_q25": ("apical_q25",),
    "nine_both_q25": ("basal_q25", "apical_q25"),
}
LAYOUT_IDS = tuple(LAYOUT_EXTRAS)
PORT_COUNTS_BY_LAYOUT = {
    "seven": 7,
    "eight_basal_q25": 8,
    "eight_apical_q25": 8,
    "nine_both_q25": 9,
}
COMMON_PORT_COUNT = 7
EXPECTED_SCENARIOS = 9
EXPECTED_MODEL_ROWS = len(LAYOUT_IDS) * len(ORDERS) * EXPECTED_SCENARIOS
EXPECTED_FREQUENCY_ROWS = EXPECTED_MODEL_ROWS * len(FREQUENCIES_HZ)
EXPECTED_TRANSIENT_ROWS = (
    EXPECTED_SCENARIOS * len(ORDERS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * (7 + 8 + 8 + 9)
)
EXPECTED_MATCHED_ROWS = (
    (len(LAYOUT_IDS) - 1) * EXPECTED_SCENARIOS * len(ORDERS)
    * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * COMMON_PORT_COUNT
)
EXPECTED_Q25_ROWS = (
    EXPECTED_SCENARIOS * len(ORDERS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 4
)
EXPECTED_HINES_SHARED_ROWS = (
    (len(LAYOUT_IDS) - 1) * EXPECTED_SCENARIOS * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * COMMON_PORT_COUNT
)
RESULT_STEM = "NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "models": EXPECTED_MODEL_ROWS,
        "frequency": EXPECTED_FREQUENCY_ROWS,
        "transient": EXPECTED_TRANSIENT_ROWS,
        "matched_shared_vs_seven": EXPECTED_MATCHED_ROWS,
        "q25_only": EXPECTED_Q25_ROWS,
        "hines_shared": EXPECTED_HINES_SHARED_ROWS,
    }


def validate_layout_node_sets(
    common_node_ids: list[int],
    layout_node_ids: dict[str, list[int]],
    q25_node_ids_by_role: dict[str, int],
) -> None:
    """Fail closed unless four layouts differ only by the named q25 probes."""
    common = set(common_node_ids)
    require(len(common_node_ids) == COMMON_PORT_COUNT and len(common) == COMMON_PORT_COUNT,
            "canonical shared-node set must contain seven unique IDs")
    require(set(layout_node_ids) == set(LAYOUT_IDS), "exactly four named layouts are required")
    require(set(q25_node_ids_by_role) == {"basal_q25", "apical_q25"},
            "both distinct q25 node IDs must be pinned")
    q25_ids = set(q25_node_ids_by_role.values())
    require(len(q25_ids) == 2, "basal and apical q25 IDs must be distinct")
    require(not q25_ids.intersection(common), "q25 nodes must not overlap the canonical seven")
    for layout_id, extras in LAYOUT_EXTRAS.items():
        nodes = layout_node_ids[layout_id]
        expected = common | {q25_node_ids_by_role[role] for role in extras}
        require(len(nodes) == len(set(nodes)), f"{layout_id}: duplicate node IDs")
        require(set(nodes) == expected, f"{layout_id}: retained node IDs do not match its q25 ablation")


def build_four_layouts(morphology, reader, sections, base_tree):
    injections7, probes7, mapped7 = baseline.fine_audit.build_sites(
        morphology, reader, sections
    )
    injections9, probes9, mapped9 = baseline.port_enrichment.build_sites(
        morphology, reader, sections, extra_probe_quantiles=(0.25,)
    )
    source7 = dict(injections7)
    source9 = dict(injections9)
    require(source7 == source9, "source SWC node IDs changed between canonical and enriched maps")
    require(set(source7) == set(SOURCE_NAMES), "source map is incomplete")

    q25_node_ids = {
        role: node_id
        for role, node_id in probes9
        if role in {"basal_q25", "apical_q25"}
    }
    require(set(q25_node_ids) == {"basal_q25", "apical_q25"},
            f"q25 roles are incomplete: {q25_node_ids}")

    electrical_map = morphology.electrical_node_mapping()

    def make_layout(layout_id: str) -> dict[str, Any]:
        extras = LAYOUT_EXTRAS[layout_id]
        extra_probes = [(role, q25_node_ids[role]) for role in extras]
        probes = list(probes7) + extra_probes
        node_ids = list(dict.fromkeys(node_id for _, node_id in injections7 + probes))
        roles: dict[int, list[str]] = {node_id: [] for node_id in node_ids}
        for role, node_id in injections7 + probes:
            if role not in roles[node_id]:
                roles[node_id].append(role)
        port_names = {
            node_id: f"swc_{electrical_map[node_id]}" for node_id in node_ids
        }
        ports = [base_tree.index[port_names[node_id]] for node_id in node_ids]
        source_indices = {
            source_name: node_ids.index(node_id)
            for source_name, node_id in source7.items()
        }
        require(len(node_ids) == COMMON_PORT_COUNT + len(extras),
                f"{layout_id}: expected {COMMON_PORT_COUNT + len(extras)} ports, got {len(node_ids)}")
        return {
            "layout_id": layout_id,
            "port_count": len(node_ids),
            "extras": extras,
            "node_ids": node_ids,
            "ports": ports,
            "roles": roles,
            "source_ids": source7,
            "source_indices": source_indices,
            "mapping": mapped9 if extras else mapped7,
        }

    layouts = {layout_id: make_layout(layout_id) for layout_id in LAYOUT_IDS}
    common_ids = list(layouts["seven"]["node_ids"])
    validate_layout_node_sets(
        common_ids,
        {layout_id: layout["node_ids"] for layout_id, layout in layouts.items()},
        q25_node_ids,
    )
    for layout_id, layout in layouts.items():
        require(layout["source_ids"] == source7, f"{layout_id}: injection sites are not matched")
    return layouts, common_ids, q25_node_ids


def build_pairwise_shared_rows(
    transient_rows: list[dict[str, Any]],
    common_node_ids: list[int],
) -> list[dict[str, Any]]:
    index = {}
    for row in transient_rows:
        if int(row["port_swc_id"]) not in common_node_ids:
            continue
        key = (
            row["layout_id"],
            int(row["basis_order"]),
            row["parameter_scenario"],
            row["source_name"],
            float(row["pulse_width_ms"]),
            int(row["port_swc_id"]),
        )
        if key in index:
            raise ValueError(f"duplicate transient identity: {key}")
        index[key] = row

    result = []
    for layout_id in LAYOUT_IDS:
        if layout_id == "seven":
            continue
        baseline_keys = {
            key[1:] for key in index if key[0] == "seven"
        }
        candidate_keys = {
            key[1:] for key in index if key[0] == layout_id
        }
        require(baseline_keys == candidate_keys,
                f"{layout_id}: shared-output pair coverage differs from seven-port reference")
        for key in sorted(baseline_keys):
            seven = index[("seven", *key)]
            candidate = index[(layout_id, *key)]
            e7 = float(seven["port_nrmse_pct"])
            ec = float(candidate["port_nrmse_pct"])
            require(e7 > 0.0, f"{layout_id}: zero seven-port error denominator for {key}")
            result.append({
                "layout_id": layout_id,
                "port_count": candidate["port_count"],
                "basis_order": key[0],
                "parameter_scenario": key[1],
                "source_name": key[2],
                "pulse_width_ms": key[3],
                "port_swc_id": key[4],
                "port_roles": seven["port_roles"],
                "seven_port_nrmse_pct": e7,
                "candidate_nrmse_pct": ec,
                "candidate_over_seven_error_ratio": ec / e7,
                "candidate_minus_seven_pct_points": ec - e7,
            })
    require(len(result) == EXPECTED_MATCHED_ROWS,
            f"matched shared rows {len(result)} != {EXPECTED_MATCHED_ROWS}")
    return result


def summarize_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for layout_id in LAYOUT_IDS:
        if layout_id == "seven":
            continue
        for order in ORDERS:
            subset = [
                row for row in rows
                if row["layout_id"] == layout_id and int(row["basis_order"]) == order
            ]
            ratios = [float(row["candidate_over_seven_error_ratio"]) for row in subset]
            e7 = [float(row["seven_port_nrmse_pct"]) for row in subset]
            ec = [float(row["candidate_nrmse_pct"]) for row in subset]
            delta = [float(row["candidate_minus_seven_pct_points"]) for row in subset]
            require(len(subset) == 378, f"{layout_id} order {order}: expected 378 paired outputs")
            result.append({
                "layout_id": layout_id,
                "port_count": PORT_COUNTS_BY_LAYOUT[layout_id],
                "basis_order": order,
                "matched_shared_output_pairs": len(subset),
                "candidate_worse_pairs": sum(value > 1e-15 for value in delta),
                "candidate_better_pairs": sum(value < -1e-15 for value in delta),
                "ties_within_1e_15_pct_points": sum(abs(value) <= 1e-15 for value in delta),
                "median_candidate_over_seven_ratio": float(np.median(ratios)),
                "p90_candidate_over_seven_ratio": float(np.quantile(ratios, 0.90, method="higher")),
                "max_candidate_over_seven_ratio": max(ratios),
                "median_seven_port_nrmse_pct": float(np.median(e7)),
                "median_candidate_nrmse_pct": float(np.median(ec)),
                "max_seven_port_nrmse_pct": max(e7),
                "max_candidate_nrmse_pct": max(ec),
                "max_absolute_delta_pct_points": max(abs(value) for value in delta),
            })
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started_total = time.perf_counter()
    reference = baseline.reference
    reference.DATA = SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.5
    morphology = baseline.SWCMorphology.from_file(SWC)
    require(len(morphology.nodes) == EXPECTED_SWC_RECORDS, "SWC record count changed")
    digest = hashlib.sha256(SWC.read_bytes()).hexdigest()
    require(digest == EXPECTED_SWC_SHA256, "SWC SHA-256 mismatch")

    preflight_path = Path("results/NMO_163775_PengControl_holdout/preflight.json")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    require(preflight.get("status") == "PASS", "Peng preflight did not pass")
    require(preflight.get("source", {}).get("source_sha256") == EXPECTED_SWC_SHA256,
            "preflight digest differs from source")
    reader, sections = reference.import_swc_with_neuron()
    base_tree = morphology.to_cable_tree()
    layouts, common_ids, q25_ids = build_four_layouts(
        morphology, reader, sections, base_tree
    )
    preflight_q25 = set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", []))
    require(set(q25_ids.values()) == preflight_q25,
            f"q25 IDs differ from preflight: {q25_ids} vs {preflight_q25}")

    base_parameters = base_tree.parameters
    parameter_data = baseline.parameter_cases()
    model_rows: list[dict[str, Any]] = []
    frequency_rows: list[dict[str, Any]] = []
    transient_rows: list[dict[str, Any]] = []
    hines_shared_rows: list[dict[str, Any]] = []
    hines_seconds: dict[tuple[str, str, float, str], float] = {}

    for scenario, (rm_scale, cm_scale, ra_scale) in parameter_data.items():
        parameters = baseline.PassiveParameters(
            specific_capacitance_f_m2=base_parameters.specific_capacitance_f_m2 * cm_scale,
            specific_membrane_resistance_ohm_m2=base_parameters.specific_membrane_resistance_ohm_m2 * rm_scale,
            axial_resistivity_ohm_m=base_parameters.axial_resistivity_ohm_m * ra_scale,
            e_leak_v=base_parameters.e_leak_v,
        )
        target = baseline.CableTree(
            [base_tree.by_name[name] for name in base_tree.order],
            parameters,
        )

        # Full-Hines references are solved independently for each layout.
        hines_cache: dict[tuple[str, str, float], dict[str, Any]] = {}
        for layout_id, layout in layouts.items():
            for source_name in SOURCE_NAMES:
                source_index = layout["source_indices"][source_name]
                for pulse_width in PULSE_WIDTHS_MS:
                    trace, seconds = baseline.run_full_hines_transient(
                        target, layout["ports"], source_index, pulse_width
                    )
                    hines_cache[(layout_id, source_name, pulse_width)] = {
                        "trace": trace,
                        "seconds": seconds,
                    }
                    hines_seconds[(scenario, source_name, pulse_width, layout_id)] = seconds

        base_layout = layouts["seven"]
        base_index = {node_id: i for i, node_id in enumerate(base_layout["node_ids"])}
        for layout_id in LAYOUT_IDS:
            if layout_id == "seven":
                continue
            layout = layouts[layout_id]
            candidate_index = {node_id: i for i, node_id in enumerate(layout["node_ids"])}
            for source_name in SOURCE_NAMES:
                for pulse_width in PULSE_WIDTHS_MS:
                    base_trace = hines_cache[("seven", source_name, pulse_width)]["trace"]
                    candidate_trace = hines_cache[(layout_id, source_name, pulse_width)]["trace"]
                    for node_id in common_ids:
                        left = base_trace[:, base_index[node_id]]
                        right = candidate_trace[:, candidate_index[node_id]]
                        hines_shared_rows.append({
                            "layout_id": layout_id,
                            "parameter_scenario": scenario,
                            "source_name": source_name,
                            "pulse_width_ms": pulse_width,
                            "port_swc_id": node_id,
                            "max_absolute_hines_trace_difference_v": float(np.max(np.abs(left - right))),
                            "relative_l2_difference_pct": baseline.relative_l2_percent(left, right),
                        })

        # Build all reduced candidates and compare frequency matrices to the
        # full Hines reference generated for the identical layout.
        for layout_id, layout in layouts.items():
            models = {}
            for order in ORDERS:
                build_start = time.perf_counter()
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], order, SHIFTS
                )
                build_seconds = time.perf_counter() - build_start
                require(model.order == order,
                        f"{layout_id}: achieved order {model.order}, expected {order}")
                np.linalg.cholesky(model.conductance_matrix_s)
                np.linalg.cholesky(model.capacitance_matrix_f)
                require(np.all(np.isfinite(model.basis)), f"{layout_id}: non-finite basis")
                basis_bytes = int(model.basis.nbytes)
                reduced_bytes = int(
                    model.conductance_matrix_s.nbytes + model.capacitance_matrix_f.nbytes
                )
                model_rows.append({
                    "layout_id": layout_id,
                    "port_count": layout["port_count"],
                    "q25_mode": "none" if not layout["extras"] else "+".join(layout["extras"]),
                    "basis_order": order,
                    "parameter_scenario": scenario,
                    "expansion_shifts_hz": ";".join(str(value) for value in SHIFTS),
                    "full_compartment_order": target.n_compartments,
                    "state_reduction_pct": 100.0 * (1.0 - order / target.n_compartments),
                    "basis_build_wall_seconds": build_seconds,
                    "basis_bytes": basis_bytes,
                    "reduced_matrix_bytes": reduced_bytes,
                    "numeric_storage_bytes": basis_bytes + reduced_bytes,
                    "passivity_check": "cholesky_passed",
                    "retained_port_swc_ids": ";".join(str(node) for node in layout["node_ids"]),
                })
                models[order] = model

            identity = np.eye(layout["port_count"], dtype=float)
            for frequency in FREQUENCIES_HZ:
                full_z = baseline.port_impedance(target, layout["ports"], frequency)
                full_y = np.linalg.solve(full_z, identity)
                for order, model in models.items():
                    reduced_z = model.impedance_matrix(frequency)
                    reduced_y = np.linalg.solve(reduced_z, identity)
                    frequency_rows.append({
                        "layout_id": layout_id,
                        "port_count": layout["port_count"],
                        "basis_order": order,
                        "parameter_scenario": scenario,
                        "frequency_hz": frequency,
                        "z_error_vs_hines_pct": baseline.relative_l2_percent(full_z, reduced_z),
                        "y_error_vs_hines_pct": baseline.relative_l2_percent(full_y, reduced_y),
                    })

            # Replay every basis order, source and pulse against its own
            # layout-specific full-Hines transient.
            for order, model in models.items():
                for source_name in SOURCE_NAMES:
                    source_index = layout["source_indices"][source_name]
                    source_id = layout["source_ids"][source_name]
                    for pulse_width in PULSE_WIDTHS_MS:
                        hines = hines_cache[(layout_id, source_name, pulse_width)]
                        reduced, reduced_seconds = baseline.run_reduced_transient(
                            model, layout["port_count"], source_index, pulse_width
                        )
                        full = hines["trace"]
                        errors = [
                            baseline.relative_l2_percent(full[:, i], reduced[:, i])
                            for i in range(layout["port_count"])
                        ]
                        overall = baseline.relative_l2_percent(full, reduced)
                        maximum = max(errors)
                        for index, node_id in enumerate(layout["node_ids"]):
                            transient_rows.append({
                                "layout_id": layout_id,
                                "port_count": layout["port_count"],
                                "basis_order": order,
                                "parameter_scenario": scenario,
                                "source_name": source_name,
                                "source_swc_id": source_id,
                                "pulse_width_ms": pulse_width,
                                "pulse_onset_ms": 2.0,
                                "pulse_amplitude_pA": 10.0,
                                "duration_ms": 20.0,
                                "dt_ms": 0.1,
                                "port_swc_id": node_id,
                                "port_roles": ";".join(layout["roles"][node_id]),
                                "port_nrmse_pct": errors[index],
                                "overall_nrmse_pct": overall,
                                "max_port_nrmse_pct": maximum,
                                "full_hines_seconds": hines["seconds"],
                                "reduced_transient_seconds": reduced_seconds,
                            })

    matched_rows = build_pairwise_shared_rows(transient_rows, common_ids)
    q25_rows = [
        row for row in transient_rows
        if any("q25" in role.lower() for role in row["port_roles"].split(";"))
    ]
    require(len(q25_rows) == EXPECTED_Q25_ROWS,
            f"q25-only coverage {len(q25_rows)} != {EXPECTED_Q25_ROWS}")

    for row in hines_shared_rows:
        require(
            float(row["max_absolute_hines_trace_difference_v"]) <= 1e-15,
            f"full-Hines shared traces differ for {row}",
        )
        require(
            float(row["relative_l2_difference_pct"]) <= 1e-12,
            f"full-Hines shared relative L2 differs for {row}",
        )

    actual = {
        "models": len(model_rows),
        "frequency": len(frequency_rows),
        "transient": len(transient_rows),
        "matched_shared_vs_seven": len(matched_rows),
        "q25_only": len(q25_rows),
        "hines_shared": len(hines_shared_rows),
    }
    require(actual == expected_counts(),
            f"exact four-layout matrix coverage mismatch: {actual} != {expected_counts()}")

    matched_summary = summarize_pairs(matched_rows)
    q25_summary = []
    for layout_id in LAYOUT_IDS:
        if layout_id == "seven":
            continue
        for order in ORDERS:
            values = [
                float(row["port_nrmse_pct"])
                for row in q25_rows
                if row["layout_id"] == layout_id and int(row["basis_order"]) == order
            ]
            q25_summary.append({
                "layout_id": layout_id,
                "basis_order": order,
                "q25_observations": len(values),
                "median_q25_nrmse_pct": float(np.median(values)),
                "max_q25_nrmse_pct": max(values),
            })

    summary_rows = []
    for layout_id, layout in layouts.items():
        for order in ORDERS:
            subset_m = [row for row in model_rows if row["layout_id"] == layout_id and row["basis_order"] == order]
            subset_f = [row for row in frequency_rows if row["layout_id"] == layout_id and row["basis_order"] == order and row["frequency_hz"] == 10000.0]
            subset_t = [row for row in transient_rows if row["layout_id"] == layout_id and row["basis_order"] == order]
            summary_rows.append({
                "layout_id": layout_id,
                "port_count": layout["port_count"],
                "basis_order": order,
                "model_scenario_rows": len(subset_m),
                "frequency_10khz_rows": len(subset_f),
                "transient_port_rows": len(subset_t),
                "median_z_error_10khz_pct": float(np.median([float(row["z_error_vs_hines_pct"]) for row in subset_f])),
                "median_y_error_10khz_pct": float(np.median([float(row["y_error_vs_hines_pct"]) for row in subset_f])),
                "median_transient_nrmse_pct": float(np.median([float(row["port_nrmse_pct"]) for row in subset_t])),
                "max_transient_nrmse_pct": max(float(row["port_nrmse_pct"]) for row in subset_t),
                "median_numeric_storage_mb": float(np.median([int(row["numeric_storage_bytes"]) for row in subset_m])) / (1024.0 * 1024.0),
            })

    output_dir = Path("results")
    outputs = {
        "models": model_rows,
        "frequency": frequency_rows,
        "transient": transient_rows,
        "matched_shared_vs_seven": matched_rows,
        "matched_summary": matched_summary,
        "q25": q25_rows,
        "q25_summary": q25_summary,
        "hines_shared": hines_shared_rows,
        "summary": summary_rows,
    }
    for suffix, data in outputs.items():
        write_csv(output_dir / f"{RESULT_STEM}_{suffix}.csv", data)

    report = {
        "schema_version": 1,
        "status": "peng_q25_four_layout_ablation_passed",
        "source": {
            "neuromorpho_id": "NMO_163775",
            "swc_sha256": digest,
            "swc_record_count": len(morphology.nodes),
            "metadata_note": "Control-condition mouse; dendrites and axon complete; NeuroMorpho marks No Diameter",
        },
        "protocol": {
            "orders": list(ORDERS),
            "shifts_hz": list(SHIFTS),
            "frequencies_hz": list(FREQUENCIES_HZ),
            "parameter_scenarios": list(parameter_data),
            "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_amplitude_pA": 10.0,
            "pulse_onset_ms": 2.0,
            "duration_ms": 20.0,
            "dt_ms": 0.1,
            "mesh_max_segment_um": 0.5,
        },
        "layout_node_ids": {key: value["node_ids"] for key, value in layouts.items()},
        "common_shared_node_ids": common_ids,
        "q25_node_ids": q25_ids,
        "exact_coverage": actual,
        "matched_summary": matched_summary,
        "q25_summary": q25_summary,
        "layout_summary": summary_rows,
        "scientific_limits": [
            "This is one mouse morphology, not a population.",
            "The experiment is passive linear-RC numerical comparison against full Hines only.",
            "NeuroMorpho lists No Diameter; standardized SWC radii are not measured biological diameters.",
            "No active-channel, nonlinear-synapse, plasticity or biological validity is established.",
            "The analysis isolates single-probe versus dual-probe enrichment under the selected protocol; it does not establish a universal layout rule.",
            "Full Hines remains canonical; no production default or solver behavior changes.",
        ],
        "runtime": {
            "python": __import__("sys").version.split()[0],
            "numpy": np.__version__,
            "neuron": __import__("neuron").__version__,
            "wall_seconds": time.perf_counter() - started_total,
        },
    }
    with (output_dir / f"{RESULT_STEM}_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")

    print(json.dumps({
        "status": report["status"],
        "exact_coverage": actual,
        "q25_node_ids": q25_ids,
        "matched_summary": matched_summary,
        "q25_summary": q25_summary,
        "layout_summary": summary_rows,
        "runtime": report["runtime"],
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
