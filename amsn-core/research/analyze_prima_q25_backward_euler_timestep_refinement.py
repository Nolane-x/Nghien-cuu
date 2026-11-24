#!/usr/bin/env python3
"""Timestep-refinement audit of seven-port and dual-q25 PRIMA transients.

The comparison is made in voltage-perturbation coordinates so the tiny
reduction residual is not hidden by subtraction of the absolute leak voltage.
The canonical absolute-voltage Hines replay is retained as a round-off
diagnostic. Full Hines at dt=0.025 ms is the finest temporal reference; no
production solver or default is changed.
"""
from __future__ import annotations

import csv
import hashlib
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
import audit_prima_q25_extended_backward_euler as tail

DT_GRID_MS = (0.1, 0.05, 0.025, 0.0125)
WINDOWS_MS = (20.0, 40.0, 100.0, 200.0)
SOURCE_NAMES = tuple(tail.SOURCE_NAMES)
PULSE_WIDTHS_MS = tuple(tail.PULSE_WIDTHS_MS)
LAYOUT_IDS = tuple(tail.LAYOUT_IDS)
BASIS_ORDER = int(tail.BASIS_ORDER)
SOURCE_COUNT = len(SOURCE_NAMES)
PROTOCOL = tail.column_protocol()
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())
RESULT_STEM = "prima_q25_backward_euler_timestep_refinement_2026-11-24"
FINE_REFERENCE_DT_MS = min(DT_GRID_MS)

EXPECTED_METRIC_ROWS = (
    2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(DT_GRID_MS)
    * len(PROTOCOL) * 7 * len(WINDOWS_MS)
)
EXPECTED_COMPARISON_ROWS = (
    2 * len(SCENARIO_NAMES) * len(DT_GRID_MS)
    * len(PROTOCOL) * 7 * len(WINDOWS_MS)
)
EXPECTED_SOURCE_SUMMARY_ROWS = (
    2 * len(DT_GRID_MS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS)
)
EXPECTED_MORPH_WINDOW_SUMMARY_ROWS = (
    2 * len(DT_GRID_MS) * len(WINDOWS_MS)
)
EXPECTED_HINES_CONVERGENCE_ROWS = (
    2 * len(SCENARIO_NAMES) * (len(DT_GRID_MS) - 1)
    * len(PROTOCOL) * 7 * len(WINDOWS_MS)
)
EXPECTED_HINES_CONVERGENCE_SUMMARY_ROWS = (
    2 * (len(DT_GRID_MS) - 1) * len(WINDOWS_MS)
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_timestep_grid(
    dt_grid_ms: tuple[float, ...] = DT_GRID_MS,
    windows_ms: tuple[float, ...] = WINDOWS_MS,
    pulse_widths_ms: tuple[float, ...] = PULSE_WIDTHS_MS,
    onset_ms: float = float(tail.PULSE_ONSET_MS),
) -> None:
    values = tuple(float(x) for x in dt_grid_ms)
    require(bool(values) and all(np.isfinite(x) and x > 0.0 for x in values),
            "all timesteps must be finite and positive")
    require(tuple(sorted(values, reverse=True)) == values,
            "timesteps must be ordered from coarse to fine")
    require(len(set(values)) == len(values), "duplicate timestep")
    for dt_ms in values:
        for duration in (*windows_ms, onset_ms, *(onset_ms + x for x in pulse_widths_ms)):
            steps = float(duration) / dt_ms
            require(
                abs(steps - round(steps)) <= 1e-9,
                f"{duration} ms is not an exact multiple of dt={dt_ms} ms",
            )
    require(min(values) == FINE_REFERENCE_DT_MS,
            "the finest timestep must remain the declared reference")


def expected_counts() -> dict[str, int]:
    return {
        "metric_rows": EXPECTED_METRIC_ROWS,
        "seven_nine_comparison_rows": EXPECTED_COMPARISON_ROWS,
        "source_window_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
        "morphology_window_summary_rows": EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        "hines_temporal_convergence_rows": EXPECTED_HINES_CONVERGENCE_ROWS,
        "hines_temporal_convergence_summary_rows": EXPECTED_HINES_CONVERGENCE_SUMMARY_ROWS,
    }


def relative_l2_percent(reference: np.ndarray, approximation: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.float64)
    approx = np.asarray(approximation, dtype=np.float64)
    require(ref.shape == approx.shape, "waveform arrays must have matching shape")
    require(np.all(np.isfinite(ref)) and np.all(np.isfinite(approx)),
            "waveform arrays must be finite")
    return float(
        100.0 * np.linalg.norm(approx - ref)
        / max(float(np.linalg.norm(ref)), 1e-30)
    )


def fine_trace_at_coarse_sample_times(
    fine_trace: np.ndarray, coarse_dt_ms: float, fine_dt_ms: float,
) -> np.ndarray:
    coarse = float(coarse_dt_ms)
    fine = float(fine_dt_ms)
    require(coarse >= fine > 0.0, "coarse/fine timestep order is invalid")
    stride_float = coarse / fine
    require(abs(stride_float - round(stride_float)) <= 1e-12,
            "coarse timestep must be an integer multiple of fine timestep")
    stride = int(round(stride_float))
    trace = np.asarray(fine_trace)
    require(trace.ndim >= 1 and trace.shape[0] >= stride,
            "fine trace does not contain a complete coarse sample")
    return trace[stride - 1::stride]


def make_current_matrix(
    row_count: int,
    source_indices: list[int],
    protocol: list[tuple[str, float]],
    step_index: int,
    dt_s: float,
) -> np.ndarray:
    current = np.zeros((row_count, len(protocol)), dtype=np.float64)
    now_s = int(step_index) * float(dt_s)
    onset_s = float(tail.PULSE_ONSET_MS) / 1000.0
    for column, (source_name, pulse_width_ms) in enumerate(protocol):
        stop_s = (float(tail.PULSE_ONSET_MS) + float(pulse_width_ms)) / 1000.0
        if onset_s <= now_s < stop_s:
            current[int(source_indices[SOURCE_NAMES.index(source_name)]), column] = float(tail.CURRENT_A)
    return current


def simulate_full_hines_pair(
    tree,
    dt_ms: float,
    source_tree_indices: list[int],
    output_tree_indices: list[int],
    protocol: list[tuple[str, float]],
) -> tuple[np.ndarray, np.ndarray]:
    """Return canonical absolute-voltage and stable perturbation Hines traces."""
    dt_s = float(dt_ms) / 1000.0
    steps = int(round(max(WINDOWS_MS) / float(dt_ms)))
    require(abs(steps * float(dt_ms) - max(WINDOWS_MS)) <= 1e-9,
            "maximum window is not exactly divisible by timestep")
    factor = tail.build_tree_hines_be_factor(tree, dt_s)
    perturbation_factor = dict(factor)
    perturbation_factor["leak_source_a"] = np.zeros_like(factor["leak_source_a"])
    leak = float(factor["leak_reversal_v"])
    columns = len(protocol)
    canonical_state = np.full((tree.n_compartments, columns), leak, dtype=np.float64)
    perturbation_state = np.zeros((tree.n_compartments, columns), dtype=np.float64)
    canonical_trace = np.empty((steps, len(output_tree_indices), columns), dtype=np.float64)
    perturbation_trace = np.empty_like(canonical_trace)
    output_rows = np.asarray(output_tree_indices, dtype=np.int64)

    for step in range(steps):
        current = make_current_matrix(
            tree.n_compartments, source_tree_indices, protocol, step, dt_s
        )
        canonical_state = tail.tree_hines_backward_euler_step(
            factor, canonical_state, current
        )
        perturbation_state = tail.tree_hines_backward_euler_step(
            perturbation_factor, perturbation_state, current
        )
        canonical_trace[step, :, :] = canonical_state[output_rows, :] - leak
        perturbation_trace[step, :, :] = perturbation_state[output_rows, :]

    require(np.all(np.isfinite(canonical_trace)),
            "canonical absolute-voltage Hines trace is non-finite")
    require(np.all(np.isfinite(perturbation_trace)),
            "perturbation-coordinate Hines trace is non-finite")
    return canonical_trace, perturbation_trace


def simulate_reduced_layout(
    model,
    layout: dict[str, Any],
    common_output_ids: list[int],
    protocol: list[tuple[str, float]],
    dt_ms: float,
) -> np.ndarray:
    """Run all six input protocols together through the reduced BE recurrence."""
    dt_s = float(dt_ms) / 1000.0
    steps = int(round(max(WINDOWS_MS) / float(dt_ms)))
    factor = tail.factor_reduced_backward_euler(model, dt_s)
    state = np.zeros((model.order, len(protocol)), dtype=np.float64)
    port_current = np.zeros((layout["port_count"], len(protocol)), dtype=np.float64)
    source_slots = {
        source: int(layout["source_indices"][source]) for source in SOURCE_NAMES
    }
    common_slot = {
        int(node): index for index, node in enumerate(layout["node_ids"])
    }
    output_slots = np.asarray(
        [common_slot[int(node)] for node in common_output_ids], dtype=np.int64
    )
    port_values = np.empty((layout["port_count"], len(protocol)), dtype=np.float64)
    trace = np.empty((steps, len(common_output_ids), len(protocol)), dtype=np.float64)

    for step in range(steps):
        port_current.fill(0.0)
        now_s = step * dt_s
        onset_s = float(tail.PULSE_ONSET_MS) / 1000.0
        for column, (source_name, pulse_width_ms) in enumerate(protocol):
            stop_s = (float(tail.PULSE_ONSET_MS) + float(pulse_width_ms)) / 1000.0
            if onset_s <= now_s < stop_s:
                port_current[source_slots[source_name], column] = float(tail.CURRENT_A)
        state = tail.reduced_backward_euler_step_factorized(
            model, factor, state, port_current, dt_s
        )
        for column in range(len(protocol)):
            port_values[:, column] = model.port_voltages(state[:, column])
        trace[step, :, :] = port_values[output_slots, :]

    require(np.all(np.isfinite(trace)), "reduced PRIMA trace is non-finite")
    return trace


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def summarize_source_windows(
    metric_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metric_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in metric_rows:
        if row["layout_id"] == "seven":
            continue
        key = (
            row["morphology"], row["dt_ms"], row["source_name"],
            row["pulse_width_ms"], row["window_ms"],
        )
        metric_groups[key].append(row)

    comparison_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (
            row["morphology"], row["dt_ms"], row["source_name"],
            row["pulse_width_ms"], row["window_ms"],
        )
        comparison_groups[key].append(row)

    output = []
    expected_pairs = len(SCENARIO_NAMES) * 7
    for key, subset in sorted(metric_groups.items()):
        require(len(subset) == expected_pairs,
                f"source/window metric coverage mismatch: {key}")
        paired = comparison_groups[key]
        require(len(paired) == expected_pairs,
                f"source/window paired coverage mismatch: {key}")
        output.append({
            "morphology": key[0],
            "dt_ms": key[1],
            "source_name": key[2],
            "pulse_width_ms": key[3],
            "window_ms": key[4],
            "scenario_output_pairs": len(subset),
            "median_seven_transient_nrmse_pct": float(np.median([
                float(row["seven_perturbation_transient_nrmse_pct"]) for row in paired
            ])),
            "median_nine_transient_nrmse_pct": float(np.median([
                float(row["nine_perturbation_transient_nrmse_pct"]) for row in paired
            ])),
            "median_nine_over_seven_ratio": float(np.median([
                float(row["nine_over_seven_perturbation_transient_ratio"])
                for row in paired
            ])),
            "p90_nine_over_seven_ratio": float(np.percentile([
                float(row["nine_over_seven_perturbation_transient_ratio"])
                for row in paired
            ], 90)),
            "worse_pairs": sum(
                float(row["nine_over_seven_perturbation_transient_ratio"]) > 1.0
                for row in paired
            ),
            "median_absolute_vs_perturbation_delta_pct": float(np.median([
                float(row["absolute_vs_perturbation_hines_delta_pct"])
                for row in subset
            ])),
        })
    require(
        len(output) == EXPECTED_SOURCE_SUMMARY_ROWS,
        f"source/window summary rows {len(output)} != {EXPECTED_SOURCE_SUMMARY_ROWS}",
    )
    return output


def summarize_morphology_windows(
    source_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        groups[(row["morphology"], float(row["dt_ms"]), float(row["window_ms"]))].append(row)
    output = []
    for key, subset in sorted(groups.items()):
        require(len(subset) == len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS),
                f"morphology/window summary lacks six source/pulse groups: {key}")
        output.append({
            "morphology": key[0],
            "dt_ms": key[1],
            "window_ms": key[2],
            "source_pulse_groups": len(subset),
            "median_nine_over_seven_transient_ratio": float(np.median([
                float(row["median_nine_over_seven_ratio"]) for row in subset
            ])),
            "p90_nine_over_seven_transient_ratio": float(np.median([
                float(row["p90_nine_over_seven_ratio"]) for row in subset
            ])),
            "median_seven_transient_nrmse_pct": float(np.median([
                float(row["median_seven_transient_nrmse_pct"]) for row in subset
            ])),
            "median_nine_transient_nrmse_pct": float(np.median([
                float(row["median_nine_transient_nrmse_pct"]) for row in subset
            ])),
            "worse_pairs_of_378": sum(int(row["worse_pairs"]) for row in subset),
            "median_absolute_vs_perturbation_delta_pct": float(np.median([
                float(row["median_absolute_vs_perturbation_delta_pct"]) for row in subset
            ])),
        })
    require(
        len(output) == EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        f"morphology/window summary rows {len(output)} != {EXPECTED_MORPH_WINDOW_SUMMARY_ROWS}",
    )
    return output


def summarize_hines_convergence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["morphology"], row["coarse_dt_ms"], row["window_ms"])].append(row)
    output = []
    expected = len(SCENARIO_NAMES) * len(PROTOCOL) * 7
    for key, subset in sorted(groups.items()):
        require(len(subset) == expected,
                f"Hines temporal convergence coverage mismatch: {key}")
        errors = [float(row["full_hines_coarse_vs_fine_nrmse_pct"]) for row in subset]
        output.append({
            "morphology": key[0],
            "coarse_dt_ms": key[1],
            "fine_reference_dt_ms": FINE_REFERENCE_DT_MS,
            "window_ms": key[2],
            "paired_scenario_protocol_output_rows": len(subset),
            "median_full_hines_coarse_vs_fine_nrmse_pct": float(np.median(errors)),
            "p90_full_hines_coarse_vs_fine_nrmse_pct": float(np.percentile(errors, 90)),
            "max_full_hines_coarse_vs_fine_nrmse_pct": float(np.max(errors)),
        })
    require(
        len(output) == EXPECTED_HINES_CONVERGENCE_SUMMARY_ROWS,
        f"Hines temporal summary rows {len(output)} != {EXPECTED_HINES_CONVERGENCE_SUMMARY_ROWS}",
    )
    return output


def main() -> None:
    started = time.perf_counter()
    validate_timestep_grid()
    results_dir = Path(__file__).parents[1] / "results"

    metric_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    hines_convergence_rows: list[dict[str, Any]] = []
    morphology_manifest = []
    max_full_hines_absolute_coordinate_delta_pct = 0.0

    for morph_spec in conditioning.MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph_spec["expected_records"],
                f"{morph_spec['name']}: morphology record count mismatch")
        digest = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
        require(digest == morph_spec["expected_sha256"],
                f"{morph_spec['name']}: source checksum mismatch")
        preflight = json.loads(morph_spec["preflight"].read_text(encoding="utf-8"))
        require(preflight.get("status") == "PASS",
                f"{morph_spec['name']}: morphology preflight failed")
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph_spec['name']}: preflight checksum mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, common_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        require(len(common_ids) == 7, "expected exactly seven shared outputs")
        expected_q25 = set(
            int(x) for x in preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])
        )
        require(set(int(x) for x in q25_ids.values()) == expected_q25,
                f"{morph_spec['name']}: q25 node identity mismatch")
        morphology_manifest.append({
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_records": morph_spec["expected_records"],
            "swc_sha256": digest,
            "shared_output_node_ids": [int(x) for x in common_ids],
            "q25_node_ids": {k: int(v) for k, v in q25_ids.items()},
        })

        seven_layout = layouts["seven"]
        shared_slot_seven = {
            int(node): index for index, node in enumerate(seven_layout["node_ids"])
        }
        source_tree_indices = [
            int(seven_layout["ports"][int(seven_layout["source_indices"][source])])
            for source in SOURCE_NAMES
        ]
        output_tree_indices = [
            int(seven_layout["ports"][shared_slot_seven[int(node)]])
            for node in common_ids
        ]
        source_tree_map = {
            source: int(source_tree_indices[i]) for i, source in enumerate(SOURCE_NAMES)
        }

        for scenario_name, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)
            models: dict[str, dict[str, Any]] = {}
            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                source_slots = [
                    int(layout["source_indices"][source]) for source in SOURCE_NAMES
                ]
                layout_source_tree = [
                    int(layout["ports"][source_slots[i]])
                    for i in range(len(SOURCE_NAMES))
                ]
                require(layout_source_tree == source_tree_indices,
                        f"{morph_spec['name']}/{layout_id}: source identity changed")
                output_slot_map = {
                    int(node): index for index, node in enumerate(layout["node_ids"])
                }
                require(set(int(x) for x in common_ids).issubset(output_slot_map),
                        f"{morph_spec['name']}/{layout_id}: common output absent")
                output_slots = [output_slot_map[int(node)] for node in common_ids]
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], BASIS_ORDER,
                    conditioning.SHIFTS_HZ,
                    relative_tolerance=conditioning.RELATIVE_TOLERANCE,
                )
                require(model.order == BASIS_ORDER,
                        f"{morph_spec['name']}/{layout_id}: PRIMA order mismatch")
                require(
                    np.allclose(
                        model.input_matrix[:, np.asarray(source_slots, dtype=np.int64)],
                        model.basis[np.asarray(layout["ports"])[np.asarray(source_slots)], :].T,
                        rtol=0.0, atol=2e-15,
                    ),
                    f"{morph_spec['name']}/{layout_id}: input basis mapping mismatch",
                )
                models[layout_id] = {
                    "model": model,
                    "layout": layout,
                    "source_slots": source_slots,
                    "output_slots": output_slots,
                }

            full_perturbation_by_dt: dict[float, np.ndarray] = {}
            full_canonical_by_dt: dict[float, np.ndarray] = {}

            for dt_ms in DT_GRID_MS:
                dt_s = float(dt_ms) / 1000.0
                steps = int(round(max(WINDOWS_MS) / float(dt_ms)))
                full_canonical, full_perturbation = simulate_full_hines_pair(
                    target, dt_ms, source_tree_indices, output_tree_indices, PROTOCOL
                )
                full_canonical_by_dt[float(dt_ms)] = full_canonical
                full_perturbation_by_dt[float(dt_ms)] = full_perturbation
                coordinate_delta = (
                    100.0 * np.linalg.norm(full_canonical - full_perturbation)
                    / max(float(np.linalg.norm(full_perturbation)), 1e-30)
                )
                max_full_hines_absolute_coordinate_delta_pct = max(
                    max_full_hines_absolute_coordinate_delta_pct, coordinate_delta
                )

                reduced_by_layout: dict[str, np.ndarray] = {}
                for layout_id in LAYOUT_IDS:
                    payload = models[layout_id]
                    reduced_by_layout[layout_id] = simulate_reduced_layout(
                        payload["model"], payload["layout"], common_ids,
                        PROTOCOL, dt_ms,
                    )

                for window_ms in WINDOWS_MS:
                    n = int(round(float(window_ms) / float(dt_ms)))
                    require(n <= steps, "window exceeds simulated trace")
                    for protocol_index, (source_name, pulse_width_ms) in enumerate(PROTOCOL):
                        source_index = SOURCE_NAMES.index(source_name)
                        pulse_index = PULSE_WIDTHS_MS.index(float(pulse_width_ms))
                        for output_index, output_node in enumerate(common_ids):
                            full_stable = full_perturbation[:n, output_index, protocol_index]
                            full_absolute = full_canonical[:n, output_index, protocol_index]
                            seven = reduced_by_layout["seven"][:n, output_index, protocol_index]
                            nine = reduced_by_layout["nine_both_q25"][:n, output_index, protocol_index]
                            seven_nrmse = relative_l2_percent(full_stable, seven)
                            nine_nrmse = relative_l2_percent(full_stable, nine)
                            absolute_nine_nrmse = relative_l2_percent(full_absolute, nine)
                            coordinate_delta = relative_l2_percent(full_stable, full_absolute)
                            common = {
                                "morphology": morph_spec["name"],
                                "neuromorpho_id": morph_spec["neuromorpho_id"],
                                "parameter_scenario": scenario_name,
                                "dt_ms": float(dt_ms),
                                "window_ms": float(window_ms),
                                "sample_count": n,
                                "source_name": source_name,
                                "pulse_width_ms": float(pulse_width_ms),
                                "output_swc_id": int(output_node),
                                "absolute_vs_perturbation_hines_delta_pct": coordinate_delta,
                            }
                            metric_rows.append({
                                **common,
                                "layout_id": "seven",
                                "perturbation_transient_nrmse_pct": seven_nrmse,
                                "canonical_absolute_transient_nrmse_pct": relative_l2_percent(
                                    full_absolute, seven
                                ),
                                "reference_waveform_l2_v_sqrt_samples": float(
                                    np.linalg.norm(full_stable)
                                ),
                                "absolute_error_l2_v_sqrt_samples": float(
                                    np.linalg.norm(seven - full_stable)
                                ),
                                "max_absolute_error_v": float(np.max(np.abs(seven - full_stable))),
                            })
                            metric_rows.append({
                                **common,
                                "layout_id": "nine_both_q25",
                                "perturbation_transient_nrmse_pct": nine_nrmse,
                                "canonical_absolute_transient_nrmse_pct": absolute_nine_nrmse,
                                "reference_waveform_l2_v_sqrt_samples": float(
                                    np.linalg.norm(full_stable)
                                ),
                                "absolute_error_l2_v_sqrt_samples": float(
                                    np.linalg.norm(nine - full_stable)
                                ),
                                "max_absolute_error_v": float(np.max(np.abs(nine - full_stable))),
                            })
                            require(np.isfinite(coordinate_delta),
                                    "non-finite absolute-vs-perturbation Hines delta")
                            comparison_rows.append({
                                **common,
                                "seven_perturbation_transient_nrmse_pct": seven_nrmse,
                                "nine_perturbation_transient_nrmse_pct": nine_nrmse,
                                "nine_over_seven_perturbation_transient_ratio": (
                                    nine_nrmse / max(seven_nrmse, 1e-300)
                                ),
                                "nine_absolute_vs_perturbation_delta_pct": coordinate_delta,
                                "nine_canonical_absolute_nrmse_pct": absolute_nine_nrmse,
                            })

            # Compare each coarse full-Hines perturbation trace with the fine
            # full-Hines trace sampled at the exact same end-of-step times.
            fine_trace = full_perturbation_by_dt[FINE_REFERENCE_DT_MS]
            for coarse_dt_ms in DT_GRID_MS:
                if coarse_dt_ms == FINE_REFERENCE_DT_MS:
                    continue
                coarse_trace = full_perturbation_by_dt[float(coarse_dt_ms)]
                fine_aligned = fine_trace_at_coarse_sample_times(
                    fine_trace, coarse_dt_ms, FINE_REFERENCE_DT_MS
                )
                require(fine_aligned.shape == coarse_trace.shape,
                        "fine/coarse Hines aligned trace shapes differ")
                for window_ms in WINDOWS_MS:
                    n = int(round(float(window_ms) / float(coarse_dt_ms)))
                    for protocol_index, (source_name, pulse_width_ms) in enumerate(PROTOCOL):
                        for output_index, output_node in enumerate(common_ids):
                            error_pct = relative_l2_percent(
                                fine_aligned[:n, output_index, protocol_index],
                                coarse_trace[:n, output_index, protocol_index],
                            )
                            hines_convergence_rows.append({
                                "morphology": morph_spec["name"],
                                "parameter_scenario": scenario_name,
                                "coarse_dt_ms": float(coarse_dt_ms),
                                "fine_reference_dt_ms": FINE_REFERENCE_DT_MS,
                                "window_ms": float(window_ms),
                                "source_name": source_name,
                                "pulse_width_ms": float(pulse_width_ms),
                                "output_swc_id": int(output_node),
                                "full_hines_coarse_vs_fine_nrmse_pct": error_pct,
                            })

    require(len(metric_rows) == EXPECTED_METRIC_ROWS,
            f"metric rows {len(metric_rows)} != {EXPECTED_METRIC_ROWS}")
    require(len(comparison_rows) == EXPECTED_COMPARISON_ROWS,
            f"paired rows {len(comparison_rows)} != {EXPECTED_COMPARISON_ROWS}")
    require(len(hines_convergence_rows) == EXPECTED_HINES_CONVERGENCE_ROWS,
            f"Hines convergence rows {len(hines_convergence_rows)} != {EXPECTED_HINES_CONVERGENCE_ROWS}")

    source_summary = summarize_source_windows(metric_rows, comparison_rows)
    morphology_window_summary = summarize_morphology_windows(source_summary)
    hines_convergence_summary = summarize_hines_convergence(hines_convergence_rows)

    output_paths = {
        "metrics": results_dir / f"{RESULT_STEM}_metrics.csv",
        "comparisons": results_dir / f"{RESULT_STEM}_seven_nine_comparisons.csv",
        "source_summary": results_dir / f"{RESULT_STEM}_source_window_summary.csv",
        "morphology_window_summary": results_dir / f"{RESULT_STEM}_morphology_window_summary.csv",
        "hines_temporal_convergence": results_dir / f"{RESULT_STEM}_hines_temporal_convergence.csv",
        "hines_temporal_convergence_summary": results_dir / f"{RESULT_STEM}_hines_temporal_convergence_summary.csv",
    }
    rows_by_name = {
        "metrics": metric_rows,
        "comparisons": comparison_rows,
        "source_summary": source_summary,
        "morphology_window_summary": morphology_window_summary,
        "hines_temporal_convergence": hines_convergence_rows,
        "hines_temporal_convergence_summary": hines_convergence_summary,
    }
    for name, path in output_paths.items():
        write_csv(path, rows_by_name[name])
    readback = {name: read_csv_rows(path) for name, path in output_paths.items()}
    expected = {
        "metrics": EXPECTED_METRIC_ROWS,
        "comparisons": EXPECTED_COMPARISON_ROWS,
        "source_summary": EXPECTED_SOURCE_SUMMARY_ROWS,
        "morphology_window_summary": EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        "hines_temporal_convergence": EXPECTED_HINES_CONVERGENCE_ROWS,
        "hines_temporal_convergence_summary": EXPECTED_HINES_CONVERGENCE_SUMMARY_ROWS,
    }
    for name, count in expected.items():
        require(readback[name] == count,
                f"{name} CSV read-back {readback[name]} != {count}")

    report = {
        "schema_version": 1,
        "status": "prima_q25_backward_euler_timestep_refinement_passed",
        "research_question": (
            "Does the seven-port versus dual-q25 nine-port transient error ratio "
            "converge as the backward-Euler timestep is refined from 0.1 to 0.025 ms?"
        ),
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(LAYOUT_IDS),
            "basis_order": BASIS_ORDER,
            "parameter_scenarios": list(SCENARIO_NAMES),
            "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_onset_ms": float(tail.PULSE_ONSET_MS),
            "pulse_amplitude_pA": float(tail.CURRENT_A) * 1e12,
            "dt_grid_ms": list(DT_GRID_MS),
            "fine_hines_reference_dt_ms": FINE_REFERENCE_DT_MS,
            "windows_ms": list(WINDOWS_MS),
            "shared_output_count": 7,
        },
        "method": {
            "reference": (
                "Full Hines implicit backward-Euler cable solve; the stable reduction "
                "comparison uses a second equivalent Hines replay in perturbation "
                "coordinates (zero initial perturbation, zero leak source)."
            ),
            "canonical_roundoff_diagnostic": (
                "The absolute-voltage Hines replay is retained and compared with the "
                "perturbation replay at every timestep; it is not used as the primary "
                "denominator for tiny PRIMA errors."
            ),
            "reduced_solver": (
                "Order-168 seven-port and dual-q25 nine-port PRIMA models, same fixed "
                "continuous-time projection for all timesteps; reduced backward-Euler "
                "systems are refactorized for each dt."
            ),
            "pulse_sampling": (
                "The exact same 10-pA rectangular current protocol is sampled at each "
                "timestep using the end-of-step backward-Euler convention."
            ),
            "temporal_convergence": (
                "Full-Hines perturbation traces at 0.1 and 0.05 ms are compared with "
                "the 0.025-ms full-Hines trace sampled at identical end times."
            ),
            "primary_metric": (
                "100*||v_reduced-v_full_Hines_perturbation||_2/"
                "||v_full_Hines_perturbation||_2"
            ),
        },
        "exact_coverage": {
            "metric_rows": len(metric_rows),
            "seven_nine_comparison_rows": len(comparison_rows),
            "source_window_summary_rows": len(source_summary),
            "morphology_window_summary_rows": len(morphology_window_summary),
            "hines_temporal_convergence_rows": len(hines_convergence_rows),
            "hines_temporal_convergence_summary_rows": len(hines_convergence_summary),
            "csv_read_back": readback,
            "expected": expected_counts(),
        },
        "validation": {
            "all_morphology_sha256_checked": True,
            "all_morphology_preflights_passed": True,
            "maximum_absolute_vs_perturbation_hines_trace_delta_pct": (
                max_full_hines_absolute_coordinate_delta_pct
            ),
            "fine_hines_reference_dt_ms": FINE_REFERENCE_DT_MS,
        },
        "morphology_window_summary": morphology_window_summary,
        "hines_temporal_convergence_summary": hines_convergence_summary,
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": tail.SCIPY_VERSION,
            "neuron": __import__("neuron").__version__,
            "wall_seconds": time.perf_counter() - started,
        },
        "scientific_limits": [
            "Only two checksum-pinned individual passive linear-RC morphology reconstructions; not a population.",
            "The 0.025-ms Hines solution is a temporal reference, not an exact continuous-time solution.",
            "The PRIMA projection basis and order are held fixed across timestep values; this isolates transient integration sensitivity, not basis optimality.",
            "Large relative nine/seven ratios are reported with absolute NRMSE and error norms.",
            "No active conductances, synapses, plasticity or biological validation are included.",
            "Full Hines remains canonical. No production solver code or defaults are changed.",
        ],
    }
    report_path = results_dir / f"{RESULT_STEM}_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "exact_coverage": report["exact_coverage"],
        "validation": report["validation"],
        "morphology_window_summary": morphology_window_summary,
        "hines_temporal_convergence_summary": hines_convergence_summary,
        "runtime": report["runtime"],
    }, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
