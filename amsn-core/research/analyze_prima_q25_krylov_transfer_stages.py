#!/usr/bin/env python3
"""Measure source-to-output transfer errors after each PRIMA Krylov growth stage.

Uses two pinned morphology holdouts and four q25 layouts. Intermediate bases
are instrumented with the same twice-reorthogonalized block process as the
production builder; final bases are required to match production exactly.
The audit does not change production code or solver defaults.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

RESEARCH = Path(__file__).resolve().parent
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import audit_prima_q25_basis_conditioning as conditioning
import audit_prima_q25_krylov_growth as growth
from amsn.prima import _apply_passive_conductance, _solve_shifted_passive_real

LAYOUT_IDS = conditioning.LAYOUT_IDS
ORDERS = conditioning.ORDERS
SHIFTS_HZ = conditioning.SHIFTS_HZ
RELATIVE_TOLERANCE = conditioning.RELATIVE_TOLERANCE
SOURCES = ("soma", "basal_q75", "apical_q75")
FREQUENCIES_HZ = tuple(conditioning.peng_replay.baseline.FREQUENCIES_HZ)
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())
STAGES_BY_ORDER = {112: 3, 168: 4}
EXPECTED_SNAPSHOTS = 2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * sum(STAGES_BY_ORDER.values())
EXPECTED_MODEL_OUTPUT_ROWS = EXPECTED_SNAPSHOTS * len(SOURCES) * 7
EXPECTED_FREQUENCY_ROWS = EXPECTED_MODEL_OUTPUT_ROWS * len(FREQUENCIES_HZ)
EXPECTED_SUMMARY_ROWS = 2 * len(LAYOUT_IDS) * sum(STAGES_BY_ORDER.values()) * len(SOURCES) * 7
EXPECTED_SOURCE_SUMMARY_ROWS = 2 * len(LAYOUT_IDS) * sum(STAGES_BY_ORDER.values()) * len(SOURCES)
RESULT_STEM = "prima_q25_krylov_transfer_stages_cross_morphology_2026-11-24"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "snapshots": EXPECTED_SNAPSHOTS,
        "model_output_rows": EXPECTED_MODEL_OUTPUT_ROWS,
        "frequency_rows": EXPECTED_FREQUENCY_ROWS,
        "summary_rows": EXPECTED_SUMMARY_ROWS,
        "source_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
    }


def projected_passive_matrices(tree, basis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Match the production congruence projection of passive G and C."""
    values = np.asarray(basis, dtype=float)
    require(values.ndim == 2 and values.shape[0] == tree.n_compartments,
            "basis shape does not match the cable tree")
    capacitance_action = tree.capacitance_f[:, None] * values
    conductance_action = _apply_passive_conductance(tree, values)
    c_reduced = values.T @ capacitance_action
    g_reduced = values.T @ conductance_action
    c_reduced = 0.5 * (c_reduced + c_reduced.T)
    g_reduced = 0.5 * (g_reduced + g_reduced.T)
    return g_reduced, c_reduced


def complex_relative_l2_percent(reference: np.ndarray, approximation: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.complex128)
    approx = np.asarray(approximation, dtype=np.complex128)
    require(ref.shape == approx.shape, "transfer vectors must have identical shape")
    require(np.all(np.isfinite(ref)) and np.all(np.isfinite(approx)),
            "transfer vectors must be finite")
    return float(100.0 * np.linalg.norm(approx - ref) / max(float(np.linalg.norm(ref)), 1e-30))


def instrumented_basis_snapshots(
    tree,
    ports: list[int],
    max_order: int,
    shifts_hz: tuple[float, ...],
) -> list[dict[str, Any]]:
    """Return prefix bases after seed, then after every complete round-robin pass."""
    n = tree.n_compartments
    order_cap = min(int(max_order), n)
    selector = np.zeros((n, len(ports)), dtype=float)
    selector[np.asarray(ports, dtype=int), np.arange(len(ports))] = 1.0
    basis_columns: list[np.ndarray] = []
    shifted_blocks: list[tuple[float, np.ndarray]] = []
    snapshots: list[dict[str, Any]] = []

    for frequency_hz in shifts_hz:
        shift = 2.0 * math.pi * frequency_hz
        seed = _solve_shifted_passive_real(tree, shift, selector)
        block, _ = growth._instrumented_orthogonalize_block(
            seed, basis_columns, RELATIVE_TOLERANCE, order_cap,
            context={"stage": "seed", "shift_hz": frequency_hz},
        )
        shifted_blocks.append((shift, block))

    snapshots.append({
        "stage": "seed",
        "round_index": 0,
        "basis": np.column_stack(basis_columns).copy(),
    })

    round_index = 1
    while len(basis_columns) < order_cap:
        added_any = False
        next_blocks: list[tuple[float, np.ndarray]] = []
        for shift_index, (shift, block) in enumerate(shifted_blocks):
            if len(basis_columns) >= order_cap or block.shape[1] == 0:
                next_blocks.append((shift, np.empty((n, 0), dtype=float)))
                continue
            candidates = _solve_shifted_passive_real(
                tree, shift, -tree.capacitance_f[:, None] * block
            )
            following, _ = growth._instrumented_orthogonalize_block(
                candidates,
                basis_columns,
                RELATIVE_TOLERANCE,
                order_cap,
                context={
                    "stage": "krylov",
                    "round_index": round_index,
                    "shift_hz": shifts_hz[shift_index],
                },
            )
            if following.shape[1] > 0:
                added_any = True
            next_blocks.append((shift, following))
        shifted_blocks = next_blocks
        if not added_any:
            break
        snapshots.append({
            "stage": f"krylov_round_{round_index}",
            "round_index": round_index,
            "basis": np.column_stack(basis_columns).copy(),
        })
        round_index += 1

    require(bool(snapshots), "no PRIMA basis snapshots were generated")
    return snapshots


def build_target_tree(module, base_tree, scales: tuple[float, float, float]):
    return conditioning.build_target_tree(module, base_tree, scales)


def summarize_model_output_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["stage"], row["round_index"], row["basis_dimension"],
            row["parameter_scenario"], row["source_name"],
            row["output_swc_id"], row["output_role"],
        )
        groups[key].append(row)
    output = []
    for key, subset in sorted(groups.items()):
        require(len(subset) == len(FREQUENCIES_HZ),
                f"transfer frequency coverage mismatch for {key}: {len(subset)}")
        refs = np.asarray([
            complex(float(r["full_hines_real_v_per_a"]), float(r["full_hines_imag_v_per_a"]))
            for r in subset
        ])
        reduced = np.asarray([
            complex(float(r["reduced_real_v_per_a"]), float(r["reduced_imag_v_per_a"]))
            for r in subset
        ])
        abs_errors = np.asarray([float(r["absolute_error_ohm"]) for r in subset])
        rel_abs = np.asarray([float(r["relative_absolute_error_pct"]) for r in subset])
        output.append({
            "morphology": key[0],
            "layout_id": key[1],
            "basis_order": key[2],
            "stage": key[3],
            "round_index": key[4],
            "basis_dimension": key[5],
            "parameter_scenario": key[6],
            "source_name": key[7],
            "output_swc_id": key[8],
            "output_role": key[9],
            "frequency_count": len(subset),
            "relative_transfer_l2_error_pct": complex_relative_l2_percent(refs, reduced),
            "median_frequency_relative_absolute_error_pct": float(np.median(rel_abs)),
            "max_frequency_relative_absolute_error_pct": float(np.max(rel_abs)),
            "median_absolute_transfer_error_ohm": float(np.median(abs_errors)),
            "max_absolute_transfer_error_ohm": float(np.max(abs_errors)),
        })
    require(len(output) == EXPECTED_MODEL_OUTPUT_ROWS,
            f"per-model source/output coverage {len(output)} != {EXPECTED_MODEL_OUTPUT_ROWS}")
    return output


def summarize_across_scenarios(model_output_rows: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    output_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in model_output_rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["stage"], row["round_index"], row["basis_dimension"],
            row["source_name"], row["output_swc_id"], row["output_role"],
        )
        output_groups[key].append(row)
    by_output = []
    for key, subset in sorted(output_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES),
                f"scenario coverage mismatch for output summary {key}")
        values = [float(r["relative_transfer_l2_error_pct"]) for r in subset]
        max_abs = [float(r["max_absolute_transfer_error_ohm"]) for r in subset]
        by_output.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "stage": key[3], "round_index": key[4], "basis_dimension": key[5],
            "source_name": key[6], "output_swc_id": key[7], "output_role": key[8],
            "parameter_scenarios": len(subset),
            "median_relative_transfer_l2_error_pct": float(np.median(values)),
            "p90_relative_transfer_l2_error_pct": float(np.percentile(values, 90)),
            "max_relative_transfer_l2_error_pct": float(np.max(values)),
            "median_max_absolute_transfer_error_ohm": float(np.median(max_abs)),
        })
    require(len(by_output) == EXPECTED_SUMMARY_ROWS,
            f"source/output summary rows {len(by_output)} != {EXPECTED_SUMMARY_ROWS}")

    source_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in by_output:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["stage"], row["round_index"], row["basis_dimension"], row["source_name"],
        )
        source_groups[key].append(row)
    by_source = []
    for key, subset in sorted(source_groups.items()):
        require(len(subset) == 7, f"source group must aggregate seven shared outputs: {key}")
        values = [float(r["median_relative_transfer_l2_error_pct"]) for r in subset]
        by_source.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "stage": key[3], "round_index": key[4], "basis_dimension": key[5],
            "source_name": key[6], "shared_output_ports": len(subset),
            "median_output_relative_transfer_l2_error_pct": float(np.median(values)),
            "p90_output_relative_transfer_l2_error_pct": float(np.percentile(values, 90)),
            "max_output_relative_transfer_l2_error_pct": float(np.max(values)),
        })
    require(len(by_source) == EXPECTED_SOURCE_SUMMARY_ROWS,
            f"source summary rows {len(by_source)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    return by_output, by_source


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    snapshot_rows: list[dict[str, Any]] = []
    frequency_rows: list[dict[str, Any]] = []
    model_output_rows: list[dict[str, Any]] = []
    morphology_manifest = []

    for morph_spec in conditioning.MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph_spec["expected_records"],
                f"{morph_spec['name']}: SWC record count mismatch")
        preflight = json.loads(morph_spec["preflight"].read_text(encoding="utf-8"))
        require(preflight.get("status") == "PASS", f"{morph_spec['name']}: preflight failed")
        digest = morph_spec["expected_sha256"]
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph_spec['name']}: preflight source digest mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, common_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        require(
            set(q25_ids.values()) == set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])),
            f"{morph_spec['name']}: q25 node IDs do not match the preflight",
        )
        morphology_manifest.append({
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_sha256": digest,
            "swc_records": morph_spec["expected_records"],
            "common_shared_output_ids": common_ids,
            "q25_node_ids": q25_ids,
        })

        for scenario_name, scales in baseline.parameter_cases().items():
            target = build_target_tree(module, base_tree, scales)
            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                node_to_slot = {node_id: i for i, node_id in enumerate(layout["node_ids"])}
                require(set(common_ids).issubset(node_to_slot),
                        f"{morph_spec['name']}/{layout_id}: shared output nodes missing")
                source_slots = [layout["source_indices"][source] for source in SOURCES]

                # Full-Hines reference is computed once per scenario/layout/source/frequency,
                # then reused at every intermediate Krylov snapshot and both basis orders.
                hines_cache: dict[tuple[str, float], dict[int, complex]] = {}
                for source_name, source_slot in zip(SOURCES, source_slots):
                    current = np.zeros(target.n_compartments, dtype=np.complex128)
                    current[layout["ports"][source_slot]] = 1.0 + 0.0j
                    for frequency_hz in FREQUENCIES_HZ:
                        full = target.solve_passive_frequency_response(frequency_hz, current)
                        hines_cache[(source_name, frequency_hz)] = {
                            node_id: complex(full[layout["ports"][node_to_slot[node_id]]])
                            for node_id in common_ids
                        }

                for order in ORDERS:
                    snapshots = instrumented_basis_snapshots(
                        target, layout["ports"], order, SHIFTS_HZ
                    )
                    production_model = baseline.prima_reduce_passive_cable_multishift(
                        target, layout["ports"], order, SHIFTS_HZ,
                        relative_tolerance=RELATIVE_TOLERANCE,
                    )
                    final_basis = snapshots[-1]["basis"]
                    require(final_basis.shape == production_model.basis.shape,
                            "final instrumented basis shape differs from production")
                    basis_delta = float(np.max(np.abs(final_basis - production_model.basis)))
                    require(basis_delta <= 1e-14,
                            f"instrumented final basis differs from production by {basis_delta}")
                    for snapshot in snapshots:
                        stage = snapshot["stage"]
                        round_index = int(snapshot["round_index"])
                        basis = snapshot["basis"]
                        achieved_order = int(basis.shape[1])
                        gram_error = float(np.max(np.abs(basis.T @ basis - np.eye(achieved_order))))
                        require(np.isfinite(gram_error) and gram_error <= 1e-12,
                                "intermediate Krylov basis is not orthonormal")
                        g_reduced, c_reduced = projected_passive_matrices(target, basis)
                        np.linalg.cholesky(g_reduced)
                        np.linalg.cholesky(c_reduced)
                        if achieved_order == order:
                            g_delta = float(np.max(np.abs(g_reduced - production_model.conductance_matrix_s)))
                            c_delta = float(np.max(np.abs(c_reduced - production_model.capacitance_matrix_f)))
                            require(g_delta <= 1e-12 and c_delta <= 1e-12,
                                    "final projected G/C matrices differ from production")
                        snapshot_rows.append({
                            "morphology": morph_spec["name"],
                            "neuromorpho_id": morph_spec["neuromorpho_id"],
                            "layout_id": layout_id,
                            "port_count": layout["port_count"],
                            "basis_order": order,
                            "parameter_scenario": scenario_name,
                            "stage": stage,
                            "round_index": round_index,
                            "basis_dimension": achieved_order,
                            "basis_orthogonality_max_abs": gram_error,
                            "final_basis_max_abs_difference_vs_production": basis_delta,
                            "final_projected_g_max_abs_difference_vs_production": (
                                g_delta if achieved_order == order else ""
                            ),
                            "final_projected_c_max_abs_difference_vs_production": (
                                c_delta if achieved_order == order else ""
                            ),
                        })

                        port_basis = basis[np.asarray(layout["ports"], dtype=int), :]
                        rhs = port_basis[np.asarray(source_slots, dtype=int), :].T
                        per_pair: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
                        for frequency_hz in FREQUENCIES_HZ:
                            omega = 2.0 * math.pi * frequency_hz
                            lhs = g_reduced.astype(np.complex128) + 1j * omega * c_reduced
                            states = np.linalg.solve(lhs, rhs)
                            reduced_ports = port_basis @ states
                            for source_index, source_name in enumerate(SOURCES):
                                for output_node in common_ids:
                                    output_slot = node_to_slot[output_node]
                                    reference_value = hines_cache[(source_name, frequency_hz)][output_node]
                                    reduced_value = complex(reduced_ports[output_slot, source_index])
                                    difference = reduced_value - reference_value
                                    absolute_error = float(abs(difference))
                                    relative_absolute = 100.0 * absolute_error / max(abs(reference_value), 1e-30)
                                    row = {
                                        "morphology": morph_spec["name"],
                                        "layout_id": layout_id,
                                        "basis_order": order,
                                        "stage": stage,
                                        "round_index": round_index,
                                        "basis_dimension": achieved_order,
                                        "parameter_scenario": scenario_name,
                                        "source_name": source_name,
                                        "output_swc_id": int(output_node),
                                        "output_role": ";".join(layout["roles"][output_node]),
                                        "frequency_hz": frequency_hz,
                                        "full_hines_real_v_per_a": reference_value.real,
                                        "full_hines_imag_v_per_a": reference_value.imag,
                                        "reduced_real_v_per_a": reduced_value.real,
                                        "reduced_imag_v_per_a": reduced_value.imag,
                                        "absolute_error_ohm": absolute_error,
                                        "relative_absolute_error_pct": relative_absolute,
                                    }
                                    frequency_rows.append(row)
                                    per_pair[(source_name, output_node)].append(row)
                        for (source_name, output_node), values in per_pair.items():
                            refs = np.asarray([
                                complex(r["full_hines_real_v_per_a"], r["full_hines_imag_v_per_a"])
                                for r in values
                            ])
                            approx = np.asarray([
                                complex(r["reduced_real_v_per_a"], r["reduced_imag_v_per_a"])
                                for r in values
                            ])
                            abs_errors = [float(r["absolute_error_ohm"]) for r in values]
                            rel_abs = [float(r["relative_absolute_error_pct"]) for r in values]
                            model_output_rows.append({
                                "morphology": morph_spec["name"],
                                "layout_id": layout_id,
                                "basis_order": order,
                                "stage": stage,
                                "round_index": round_index,
                                "basis_dimension": achieved_order,
                                "parameter_scenario": scenario_name,
                                "source_name": source_name,
                                "output_swc_id": int(output_node),
                                "output_role": ";".join(layout["roles"][output_node]),
                                "frequency_count": len(values),
                                "relative_transfer_l2_error_pct": complex_relative_l2_percent(refs, approx),
                                "median_frequency_relative_absolute_error_pct": float(np.median(rel_abs)),
                                "max_frequency_relative_absolute_error_pct": float(np.max(rel_abs)),
                                "median_absolute_transfer_error_ohm": float(np.median(abs_errors)),
                                "max_absolute_transfer_error_ohm": float(np.max(abs_errors)),
                            })

    expected = expected_counts()
    require(len(snapshot_rows) == expected["snapshots"],
            f"snapshot coverage {len(snapshot_rows)} != {expected['snapshots']}")
    require(len(model_output_rows) == expected["model_output_rows"],
            f"model output rows {len(model_output_rows)} != {expected['model_output_rows']}")
    require(len(frequency_rows) == expected["frequency_rows"],
            f"frequency rows {len(frequency_rows)} != {expected['frequency_rows']}")
    output_summary, source_summary = summarize_across_scenarios(model_output_rows)

    results_dir = Path(__file__).parents[1] / "results"
    write_csv(results_dir / f"{RESULT_STEM}_snapshots.csv", snapshot_rows)
    write_csv(results_dir / f"{RESULT_STEM}_by_output_model.csv", model_output_rows)
    write_csv(results_dir / f"{RESULT_STEM}_frequency.csv", frequency_rows)
    write_csv(results_dir / f"{RESULT_STEM}_by_output_summary.csv", output_summary)
    write_csv(results_dir / f"{RESULT_STEM}_by_source_summary.csv", source_summary)

    report = {
        "schema_version": 1,
        "status": "prima_q25_krylov_transfer_stage_audit_passed",
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(LAYOUT_IDS),
            "basis_orders": list(ORDERS),
            "parameter_scenarios": list(SCENARIO_NAMES),
            "expansion_shifts_hz": list(SHIFTS_HZ),
            "frequency_grid_hz": list(FREQUENCIES_HZ),
            "sources": list(SOURCES),
        },
        "exact_coverage": {
            "snapshots": len(snapshot_rows),
            "model_output_rows": len(model_output_rows),
            "frequency_rows": len(frequency_rows),
            "by_output_summary_rows": len(output_summary),
            "by_source_summary_rows": len(source_summary),
            "expected": expected,
            "max_final_basis_difference_vs_production": max(
                float(r["final_basis_max_abs_difference_vs_production"]) for r in snapshot_rows
            ),
        },
        "interpretation_note": "Transfer errors are evaluated on the same seven shared SWC outputs and three q75/soma source locations at each Krylov prefix snapshot, against full Hines for that morphology/layout/scenario.",
        "scientific_limits": [
            "This is passive linear-RC numerical transfer validation, not active-neuron or biological validation.",
            "The instrumented final basis is checked against the unmodified production PRIMA builder for each model; intermediate prefixes come from the same verified growth process.",
            "Transfer residual reduction does not establish biological relevance or by itself prove why a transient output error changes.",
            "Only two individual morphology reconstructions are compared; they are not populations.",
            "Full Hines remains canonical and no production code or defaults are changed.",
        ],
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "neuron": __import__("neuron").__version__,
            "wall_seconds": time.perf_counter() - started,
        },
    }
    (results_dir / f"{RESULT_STEM}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "exact_coverage": report["exact_coverage"],
        "runtime": report["runtime"],
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
