#!/usr/bin/env python3
"""Measure q25 nodes as outputs while independently varying the PRIMA input-port basis.

For each 7/8/8/9 input layout, the same reduced basis is used to read out:
- the seven shared ports;
- basal-q25 and apical-q25, whether or not each q25 node was included in the input-port set.

The q25 readouts therefore use rows of the full-compartment PRIMA basis, not
only rows exposed as retained input ports. The script verifies that all 144
reconstructed basis/G/C/B hashes exactly match the accepted order-168 primary
report before interpreting any output metrics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

RESEARCH = Path(__file__).resolve().parent
AMSN_ROOT = RESEARCH.parent
RESULTS_DIR = AMSN_ROOT / "results"
PRIMARY_STEM = "prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25"
STEM = "prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25"

EXPECTED_CASE_ROWS = 3456
EXPECTED_COMPARISON_ROWS = 2592
EXPECTED_MORPHOLOGY_SUMMARY_ROWS = 336
EXPECTED_SOURCE_SUMMARY_ROWS = 2016
EXPECTED_IDENTITY_ROWS = 3456

METRICS = {
    "continuous_ac_error_pct": "continuous_ac_zoh_weighted_error_pct",
    "continuous_ac_error_norm_v_s": "continuous_ac_weighted_error_norm_v_s",
    "discrete_be_error_pct": "discrete_be_periodic_transfer_error_pct",
    "discrete_be_error_norm_v": "discrete_be_error_norm_v",
    "canonical_transient_nrmse_pct": "finite_transient_nrmse_pct",
    "perturbation_transient_nrmse_pct": "perturbation_coordinate_transient_nrmse_pct",
    "finite_dft_error_norm_v_samples": "finite_error_dft_norm_v_samples",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def percentile(values: list[float], q: float) -> float:
    values = sorted(float(x) for x in values)
    position = (len(values) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype="<f8"))
    digest = hashlib.sha256()
    digest.update(json.dumps({"shape": array.shape, "dtype": "<f8"}).encode())
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def verify_pinned_runtime(primary_report: dict[str, Any]) -> dict[str, Any]:
    expected_versions = {
        "python": "3.12.16",
        "numpy": "2.5.5",
        "scipy": "1.16.3",
        "neuron": "9.0.2",
        "threadpoolctl": "3.6.0",
    }
    observed_versions = {
        "python": ".".join(map(str, sys.version_info[:3])),
        "numpy": version("numpy"),
        "scipy": version("scipy"),
        "neuron": version("neuron"),
        "threadpoolctl": version("threadpoolctl"),
    }
    if observed_versions != expected_versions:
        raise RuntimeError(
            f"runtime versions differ from the pinned primary run: {observed_versions}"
        )
    runtime = primary_report["reproducibility_diagnostics"]["numerical_runtime"]
    environment = runtime["thread_environment"]
    if environment.get("OPENBLAS_CORETYPE") != "Haswell":
        raise RuntimeError("primary report is not pinned to OPENBLAS_CORETYPE=Haswell")
    if environment.get("NPY_DISABLE_CPU_FEATURES") != "X86_V4,AVX512_ICL":
        raise RuntimeError("primary report has an unexpected NumPy SIMD restriction")
    pools = [x for x in runtime.get("threadpools", []) if x.get("internal_api") == "openblas"]
    if not pools or {x.get("architecture") for x in pools} != {"Haswell"}:
        raise RuntimeError("primary report does not verify Haswell OpenBLAS")
    return {"versions": observed_versions, "thread_environment": environment, "threadpools": pools}


def _basis_report_index(report: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, str]]:
    rows = report["reproducibility_diagnostics"]["basis_models"]
    index = {
        (row["morphology"], row["parameter_scenario"], row["layout_id"]): row
        for row in rows
    }
    if len(index) != 144:
        raise ValueError(f"primary basis diagnostics {len(index)} != 144")
    return index


def solve_reduced_with_output_basis(
    model,
    s_values: np.ndarray,
    rhs_base: np.ndarray,
    output_basis: np.ndarray,
    *,
    chunk_size: int = 50,
) -> np.ndarray:
    """Solve reduced states and apply an independently selected output basis."""
    shifts = np.asarray(s_values, dtype=np.complex128)
    rhs0 = np.asarray(rhs_base, dtype=np.complex128)
    outputs = np.asarray(output_basis, dtype=np.float64)
    if outputs.ndim != 2 or outputs.shape[1] != model.order:
        raise ValueError("output_basis must have shape (observations, reduced_order)")
    response = np.empty((shifts.size, outputs.shape[0], rhs0.shape[1]), dtype=np.complex128)
    for start in range(0, shifts.size, chunk_size):
        stop = min(start + chunk_size, shifts.size)
        local_s = shifts[start:stop]
        lhs = (
            model.conductance_matrix_s[None, :, :].astype(np.complex128)
            + local_s[:, None, None] * model.capacitance_matrix_f[None, :, :]
        )
        rhs = np.broadcast_to(rhs0[None, :, :], (stop - start, model.order, rhs0.shape[1]))
        state = np.linalg.solve(lhs, rhs)
        response[start:stop, :, :] = np.einsum(
            "ok,fkr->for", outputs, state, optimize=True
        )
    if not (np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag))):
        raise FloatingPointError("non-finite reduced response for q25 observer outputs")
    return response


def simulate_reduced_with_output_basis(
    model,
    layout: dict[str, Any],
    output_basis: np.ndarray,
    protocol: list[tuple[str, float]],
    runner,
) -> tuple[np.ndarray, dict[float, np.ndarray]]:
    """Backward-Euler replay with independent measurement rows."""
    sample_count = int(round(max(runner.WINDOWS_MS) / runner.DT_MS))
    factor = runner.tail.factor_reduced_backward_euler(model, runner.DT_S)
    state = np.zeros((model.order, len(protocol)), dtype=np.float64)
    port_current = np.zeros((layout["port_count"], len(protocol)), dtype=np.float64)
    source_slots = {
        source: int(layout["source_indices"][source])
        for source in runner.SOURCE_NAMES
    }
    traces = np.empty((sample_count, output_basis.shape[0], len(protocol)), dtype=np.float64)
    boundary_steps = {
        int(round(window / runner.DT_MS)): float(window)
        for window in runner.WINDOWS_MS
    }
    terminal: dict[float, np.ndarray] = {}
    for step in range(sample_count):
        port_current.fill(0.0)
        now_s = step * runner.DT_S
        for column, (source_name, pulse_width_ms) in enumerate(protocol):
            pulse_end = (
                runner.tail.PULSE_ONSET_MS + pulse_width_ms
            ) / 1000.0
            if runner.tail.PULSE_ONSET_MS / 1000.0 <= now_s < pulse_end:
                port_current[source_slots[source_name], column] = runner.tail.CURRENT_A
        state = runner.tail.reduced_backward_euler_step_factorized(
            model, factor, state, port_current, runner.DT_S
        )
        traces[step, :, :] = output_basis @ state
        completed = step + 1
        if completed in boundary_steps:
            terminal[boundary_steps[completed]] = state.copy()
    if set(terminal) != set(runner.WINDOWS_MS):
        raise ValueError("reduced q25 observer terminal-state coverage mismatch")
    return traces, terminal


def build_comparison_rows(case_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    key_fields = (
        "morphology", "parameter_scenario", "q25_role", "output_swc_id",
        "source_name", "pulse_width_ms", "window_ms",
    )
    index = {}
    for row in case_rows:
        key = tuple(row[field] for field in key_fields) + (row["layout_id"],)
        if key in index:
            raise ValueError(f"duplicate q25 output observer key {key}")
        index[key] = row
    base_keys = {key[:-1] for key in index}
    if len(base_keys) != EXPECTED_CASE_ROWS // 4:
        raise ValueError("q25 observer paired-key coverage is incomplete")
    comparisons = []
    for base in sorted(base_keys):
        reference = index[base + ("seven",)]
        for candidate_layout in ("eight_basal_q25", "eight_apical_q25", "nine_both_q25"):
            candidate = index[base + (candidate_layout,)]
            row = {field: reference[field] for field in key_fields}
            row["candidate_layout"] = candidate_layout
            row["candidate_q25_is_retained_port"] = candidate["q25_is_retained_port"]
            for metric_name, field in METRICS.items():
                baseline_error = float(reference[field])
                candidate_error = float(candidate[field])
                row[f"seven_{metric_name}"] = baseline_error
                row[f"candidate_{metric_name}"] = candidate_error
                row[f"candidate_over_seven_{metric_name}_ratio"] = (
                    candidate_error / baseline_error if baseline_error > 0.0 else ""
                )
                row[f"candidate_minus_seven_{metric_name}"] = candidate_error - baseline_error
            comparisons.append(row)
    if len(comparisons) != EXPECTED_COMPARISON_ROWS:
        raise ValueError(f"q25 observer comparison rows {len(comparisons)} != {EXPECTED_COMPARISON_ROWS}")
    return comparisons


def build_summaries(comparison_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    morphology_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        source_key = (
            row["morphology"], row["candidate_layout"], row["q25_role"],
            row["source_name"], row["pulse_width_ms"], row["window_ms"],
        )
        morph_key = (
            row["morphology"], row["candidate_layout"], row["q25_role"], row["window_ms"],
        )
        source_groups[source_key].append(row)
        morphology_groups[morph_key].append(row)

    source_rows = []
    for key, rows in sorted(source_groups.items()):
        if len(rows) != 9:
            raise ValueError(f"q25 observer source group {key} has {len(rows)} scenarios")
        for metric_name in METRICS:
            ratios = [
                float(x[f"candidate_over_seven_{metric_name}_ratio"])
                for x in rows
                if x[f"candidate_over_seven_{metric_name}_ratio"] != ""
            ]
            deltas = [float(x[f"candidate_minus_seven_{metric_name}"]) for x in rows]
            source_rows.append({
                "morphology": key[0], "candidate_layout": key[1], "q25_role": key[2],
                "source_name": key[3], "pulse_width_ms": float(key[4]), "window_ms": float(key[5]),
                "metric": metric_name, "scenario_count": len(rows),
                "valid_ratio_scenarios": len(ratios),
                "median_candidate_over_seven_ratio": median(ratios) if ratios else "",
                "p90_candidate_over_seven_ratio": percentile(ratios, 0.90) if ratios else "",
                "median_candidate_minus_seven_error": median(deltas),
                "p90_candidate_minus_seven_error": percentile(deltas, 0.90),
                "candidate_worse_scenarios": sum(x > 0.0 for x in deltas),
                "candidate_better_scenarios": sum(x < 0.0 for x in deltas),
            })
    morphology_rows = []
    for key, rows in sorted(morphology_groups.items()):
        if len(rows) != 54:
            raise ValueError(f"q25 observer morphology group {key} has {len(rows)} pairs")
        for metric_name in METRICS:
            ratios = [
                float(x[f"candidate_over_seven_{metric_name}_ratio"])
                for x in rows
                if x[f"candidate_over_seven_{metric_name}_ratio"] != ""
            ]
            deltas = [float(x[f"candidate_minus_seven_{metric_name}"]) for x in rows]
            morphology_rows.append({
                "morphology": key[0], "candidate_layout": key[1],
                "q25_role": key[2], "window_ms": float(key[3]),
                "metric": metric_name, "paired_source_pulse_scenario_count": len(rows),
                "valid_ratio_pairs": len(ratios),
                "median_candidate_over_seven_ratio": median(ratios) if ratios else "",
                "p90_candidate_over_seven_ratio": percentile(ratios, 0.90) if ratios else "",
                "median_candidate_minus_seven_error": median(deltas),
                "p90_candidate_minus_seven_error": percentile(deltas, 0.90),
                "candidate_worse_pairs": sum(x > 0.0 for x in deltas),
                "candidate_better_pairs": sum(x < 0.0 for x in deltas),
            })
    if len(source_rows) != EXPECTED_SOURCE_SUMMARY_ROWS:
        raise ValueError(f"source q25 observer summaries {len(source_rows)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    if len(morphology_rows) != EXPECTED_MORPHOLOGY_SUMMARY_ROWS:
        raise ValueError(f"morphology q25 observer summaries {len(morphology_rows)} != {EXPECTED_MORPHOLOGY_SUMMARY_ROWS}")
    return source_rows, morphology_rows


def run(primary_results_dir: Path, output_dir: Path) -> dict[str, Any]:
    runner = load_module(
        "q25_output_observer_primary_runner",
        RESEARCH / "analyze_prima_q25_four_morphology_four_layout_boundary_ablation.py",
    )
    primary_report_path = primary_results_dir / f"{PRIMARY_STEM}_report.json"
    primary_case_path = primary_results_dir / f"{PRIMARY_STEM}_case_metrics.csv"
    primary_report = json.loads(primary_report_path.read_text(encoding="utf-8"))
    if primary_report.get("status") != "prima_q25_four_morphology_four_layout_boundary_ablation_passed":
        raise ValueError("primary four-layout run has not passed")
    if primary_report.get("scope", {}).get("basis_order") != 168:
        raise ValueError("primary four-layout report is not basis order 168")
    if version("numpy") != "2.5.5" or version("scipy") != "1.16.3" or version("neuron") != "9.0.2":
        raise RuntimeError("output observer requires the pinned numerical package versions")
    runtime = runner.numerical_runtime_diagnostics()
    if runtime["verified_openblas_coretype"] != "Haswell":
        raise RuntimeError("output observer did not run with pinned Haswell OpenBLAS")
    environment = runtime["thread_environment"]
    if environment.get("NPY_DISABLE_CPU_FEATURES") != "X86_V4,AVX512_ICL":
        raise RuntimeError("output observer NumPy SIMD restrictions differ from primary")
    primary_basis = _basis_report_index(primary_report)
    primary_case_rows = read_csv(primary_case_path)
    if len(primary_case_rows) != 12096:
        raise ValueError("primary case-metric matrix is incomplete")
    runner.tail.DT_MS = runner.DT_MS
    master_s_cont = 1j * 2.0 * np.pi * runner.MASTER_FREQUENCIES_HZ
    master_s_be = runner.backward_euler_s_values(runner.MASTER_FREQUENCIES_HZ, runner.DT_S)
    protocol = runner.tail.column_protocol()
    case_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    basis_rows: list[dict[str, Any]] = []
    max_identity = 0.0
    morphology_manifest = []
    started = time.perf_counter()

    for morph_spec in runner.MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        source_sha = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
        if source_sha != morph_spec["expected_sha256"]:
            raise ValueError(f"{morph_spec['name']}: SWC checksum mismatch")
        preflight = json.loads(morph_spec["preflight"].read_text(encoding="utf-8"))
        if preflight.get("status") != "PASS" or preflight.get("source", {}).get("source_sha256") != source_sha:
            raise ValueError(f"{morph_spec['name']}: preflight did not match source SWC")
        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, common_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        expected_q25 = set(int(x) for x in preflight["amsn"]["q25_only_swc_node_ids"])
        if set(int(x) for x in q25_ids.values()) != expected_q25:
            raise ValueError(f"{morph_spec['name']}: q25 node IDs changed")
        role_order = ("basal_q25", "apical_q25")
        electrical_map = morphology.electrical_node_mapping()
        observer_node_ids = [int(q25_ids[role]) for role in role_order]
        observer_tree_indices = [
            int(base_tree.index[f"swc_{electrical_map[node_id]}"])
            for node_id in observer_node_ids
        ]
        output_tree_indices = [
            int(base_tree.index[f"swc_{electrical_map[int(node_id)]}"])
            for node_id in common_ids
        ] + observer_tree_indices
        morphology_manifest.append({
            "morphology": morph_spec["name"], "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_sha256": source_sha,
            "shared_node_ids": [int(x) for x in common_ids],
            "q25_node_ids": {role: int(q25_ids[role]) for role in role_order},
        })

        seven_layout = layouts["seven"]
        source_tree_indices = [
            int(seven_layout["ports"][seven_layout["source_indices"][source]])
            for source in runner.SOURCE_NAMES
        ]
        full_rhs = np.zeros((base_tree.n_compartments, len(runner.SOURCE_NAMES)), dtype=np.float64)
        full_rhs[np.asarray(source_tree_indices), np.arange(len(runner.SOURCE_NAMES))] = 1.0

        for scenario_name, scales in baseline.parameter_cases().items():
            target = runner.conditioning.build_target_tree(module, base_tree, scales)
            hines_factor = runner.tail.build_tree_hines_be_factor(target, runner.DT_S)
            full_trace, full_terminal, p0 = runner.simulate_full_hines_with_terminal_states(
                target, hines_factor, source_tree_indices, output_tree_indices
            )
            full_identity_trace, full_identity_terminal, p1 = runner.simulate_full_hines_perturbation_windows(
                target, hines_factor, source_tree_indices, output_tree_indices
            )
            if p0 != protocol or p1 != protocol:
                raise ValueError("Hines replay protocol mismatch")
            full_cont = runner.solve_full_hines_s_response(
                target, master_s_cont, full_rhs, output_tree_indices, chunk_size=50
            )
            full_be = runner.solve_full_hines_s_response(
                target, master_s_be, full_rhs, output_tree_indices, chunk_size=50
            )
            for layout_id in runner.LAYOUT_IDS:
                layout = layouts[layout_id]
                source_slots = [int(layout["source_indices"][s]) for s in runner.SOURCE_NAMES]
                source_nodes = [int(layout["ports"][slot]) for slot in source_slots]
                if source_nodes != source_tree_indices:
                    raise ValueError(f"{morph_spec['name']}/{layout_id}: source nodes changed")
                common_slot_by_node = {int(node): i for i, node in enumerate(layout["node_ids"])}
                common_output_slots = [common_slot_by_node[int(node)] for node in common_ids]
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], runner.BASIS_ORDER,
                    runner.conditioning.SHIFTS_HZ,
                    relative_tolerance=runner.conditioning.RELATIVE_TOLERANCE,
                )
                if model.order != runner.BASIS_ORDER:
                    raise ValueError(f"{morph_spec['name']}/{layout_id}: basis order mismatch")
                basis_key = (morph_spec["name"], scenario_name, layout_id)
                expected_basis = primary_basis[basis_key]
                observed_hashes = {
                    "basis_sha256": array_sha256(model.basis),
                    "conductance_sha256": array_sha256(model.conductance_matrix_s),
                    "capacitance_sha256": array_sha256(model.capacitance_matrix_f),
                    "input_sha256": array_sha256(model.input_matrix),
                }
                for name, value in observed_hashes.items():
                    if value != expected_basis[name]:
                        raise RuntimeError(
                            f"{basis_key}: observer replay basis mismatch for {name}"
                        )
                basis_rows.append({
                    "morphology": morph_spec["name"], "parameter_scenario": scenario_name,
                    "layout_id": layout_id, **observed_hashes, "matched_primary_basis": True,
                })
                shared_output_basis = model.input_matrix[:, common_output_slots].T.copy()
                q25_output_basis = model.basis[np.asarray(observer_tree_indices, dtype=np.int64), :].copy()
                for q_index, role in enumerate(role_order):
                    if q25_retained[role]:
                        q25_slot = int(layout["node_ids"].index(observer_node_ids[q_index]))
                        if not np.allclose(
                            q25_output_basis[q_index],
                            model.input_matrix[:, q25_slot],
                            rtol=0.0, atol=2e-15,
                        ):
                            raise ValueError(
                                f"{basis_key}: retained q25 input/output projection differs"
                            )
                output_basis = np.vstack((shared_output_basis, q25_output_basis))
                if output_basis.shape != (9, model.order):
                    raise ValueError("observer output basis must expose seven shared and two q25 outputs")
                q25_retained = {
                    role: int(q25_ids[role]) in set(int(x) for x in layout["node_ids"])
                    for role in role_order
                }
                reduced_trace, reduced_terminal = simulate_reduced_with_output_basis(
                    model, layout, output_basis, protocol, runner
                )
                reduced_rhs = model.input_matrix[:, np.asarray(source_slots, dtype=np.int64)]
                reduced_cont = solve_reduced_with_output_basis(
                    model, master_s_cont, reduced_rhs, output_basis, chunk_size=50
                )
                reduced_be = solve_reduced_with_output_basis(
                    model, master_s_be, reduced_rhs, output_basis, chunk_size=50
                )

                for window_ms in runner.WINDOWS_MS:
                    frequencies, frequency_indices = runner.finite_window_frequency_indices(window_ms)
                    sample_count = int(round(window_ms / runner.DT_MS))
                    selected_s_be = master_s_be[frequency_indices]
                    input_protocol, input_samples = runner.build_sampled_protocol(sample_count)
                    if input_protocol != protocol:
                        raise ValueError("finite-window input protocol changed")
                    input_dft = np.fft.rfft(input_samples, axis=0)
                    one_sided = runner.one_sided_dft_weights(sample_count)
                    full_state = full_identity_terminal[float(window_ms)]
                    full_boundary_rhs = hines_factor["c_over_dt"][:, None] * full_state
                    full_boundary = runner.solve_full_hines_s_response(
                        target, selected_s_be, full_boundary_rhs, output_tree_indices, chunk_size=50
                    )
                    reduced_state = reduced_terminal[float(window_ms)]
                    reduced_boundary_rhs = (model.capacitance_matrix_f / runner.DT_S) @ reduced_state
                    reduced_boundary = solve_reduced_with_output_basis(
                        model, selected_s_be, reduced_boundary_rhs, output_basis, chunk_size=50
                    )
                    for source_index, source_name in enumerate(runner.SOURCE_NAMES):
                        for pulse_index, pulse_width_ms in enumerate(runner.PULSE_WIDTHS_MS):
                            column = source_index * len(runner.PULSE_WIDTHS_MS) + pulse_index
                            spectrum = input_dft[:, column]
                            for q_index, role in enumerate(role_order):
                                output_index = len(common_ids) + q_index
                                output_node = observer_node_ids[q_index]
                                full_cont_vector = full_cont[:, output_index, source_index]
                                reduced_cont_vector = reduced_cont[:, output_index, source_index]
                                full_be_vector = full_be[frequency_indices, output_index, source_index]
                                reduced_be_vector = reduced_be[frequency_indices, output_index, source_index]
                                cont_pct, cont_norm, cont_ref_norm = runner.weighted_transfer_error(
                                    full_cont_vector[frequency_indices], reduced_cont_vector[frequency_indices],
                                    spectrum, frequencies, continuous_zoh_input=True
                                )
                                be_pct, be_norm, be_ref_norm = runner.weighted_transfer_error(
                                    full_be_vector, reduced_be_vector, spectrum, frequencies,
                                    continuous_zoh_input=False
                                )
                                full_canonical = full_trace[:sample_count, output_index, column]
                                full_perturbation = full_identity_trace[:sample_count, output_index, column]
                                reduced_y = reduced_trace[:sample_count, output_index, column]
                                canonical_nrmse = runner.tail.relative_l2_percent(full_canonical, reduced_y)
                                perturb_nrmse = runner.tail.relative_l2_percent(full_perturbation, reduced_y)
                                full_fft = np.fft.rfft(full_perturbation)
                                reduced_fft = np.fft.rfft(reduced_y)
                                full_q = full_boundary[:, output_index, column]
                                reduced_q = reduced_boundary[:, output_index, column]
                                full_identity_rel, full_identity_abs = runner._finite_identity_error(
                                    full_fft, full_be_vector * spectrum - full_q,
                                    scale_norm=float(np.linalg.norm(full_fft))
                                )
                                reduced_identity_rel, reduced_identity_abs = runner._finite_identity_error(
                                    reduced_fft, reduced_be_vector * spectrum - reduced_q,
                                    scale_norm=float(np.linalg.norm(reduced_fft))
                                )
                                actual_error = reduced_fft - full_fft
                                transfer_component = (reduced_be_vector - full_be_vector) * spectrum
                                boundary_component = -(reduced_q - full_q)
                                decomposition = runner.decompose_periodic_boundary_error(
                                    actual_error, transfer_component, boundary_component, one_sided,
                                    identity_scale_norm=max(float(np.linalg.norm(full_fft)), float(np.linalg.norm(reduced_fft)))
                                )
                                max_identity = max(
                                    max_identity, full_identity_rel, reduced_identity_rel,
                                    decomposition["identity_relative_error"]
                                )
                                row = {
                                    "morphology": morph_spec["name"],
                                    "neuromorpho_id": morph_spec["neuromorpho_id"],
                                    "parameter_scenario": scenario_name,
                                    "basis_order": runner.BASIS_ORDER,
                                    "layout_id": layout_id,
                                    "q25_role": role,
                                    "output_swc_id": output_node,
                                    "q25_is_retained_port": q25_retained[role],
                                    "source_name": source_name,
                                    "pulse_width_ms": float(pulse_width_ms),
                                    "window_ms": float(window_ms),
                                    "sample_count": sample_count,
                                    "continuous_ac_zoh_weighted_error_pct": cont_pct,
                                    "continuous_ac_weighted_error_norm_v_s": cont_norm,
                                    "continuous_ac_weighted_reference_norm_v_s": cont_ref_norm,
                                    "discrete_be_periodic_transfer_error_pct": be_pct,
                                    "discrete_be_error_norm_v": be_norm,
                                    "discrete_be_reference_norm_v": be_ref_norm,
                                    "finite_transient_nrmse_pct": canonical_nrmse,
                                    "perturbation_coordinate_transient_nrmse_pct": perturb_nrmse,
                                    "periodic_transfer_component_norm_v_samples": decomposition["periodic_transfer_norm"],
                                    "terminal_boundary_component_norm_v_samples": decomposition["terminal_boundary_norm"],
                                    "finite_error_dft_norm_v_samples": decomposition["finite_error_norm"],
                                    "transfer_component_over_finite_error_norm_pct": decomposition["periodic_over_finite_error_norm_pct"],
                                    "boundary_component_over_finite_error_norm_pct": decomposition["boundary_over_finite_error_norm_pct"],
                                    "transfer_boundary_cross_term_pct": decomposition["periodic_boundary_cross_term_pct"],
                                    "full_model_identity_relative_error": full_identity_rel,
                                    "reduced_model_identity_relative_error": reduced_identity_rel,
                                    "finite_dft_identity_relative_error": decomposition["identity_relative_error"],
                                    "full_model_identity_absolute_error_v_samples": full_identity_abs,
                                    "reduced_model_identity_absolute_error_v_samples": reduced_identity_abs,
                                    "finite_dft_identity_absolute_error_v_samples": decomposition["identity_absolute_error"],
                                    "q25_output_basis_row_norm": float(np.linalg.norm(q25_output_basis[q_index])),
                                }
                                case_rows.append(row)
                                identity_rows.append({
                                    "morphology": morph_spec["name"],
                                    "parameter_scenario": scenario_name,
                                    "layout_id": layout_id,
                                    "q25_role": role,
                                    "source_name": source_name,
                                    "pulse_width_ms": float(pulse_width_ms),
                                    "window_ms": float(window_ms),
                                    "finite_dft_identity_relative_error": decomposition["identity_relative_error"],
                                    "full_model_identity_relative_error": full_identity_rel,
                                    "reduced_model_identity_relative_error": reduced_identity_rel,
                                })

    if len(case_rows) != EXPECTED_CASE_ROWS or len(identity_rows) != EXPECTED_IDENTITY_ROWS:
        raise ValueError(f"observer coverage mismatch: cases={len(case_rows)}, identities={len(identity_rows)}")
    if len(basis_rows) != 144 or any(not row["matched_primary_basis"] for row in basis_rows):
        raise ValueError("observer basis hashes did not reproduce the accepted primary basis matrix")
    if max_identity > 2e-8:
        raise ValueError(f"q25 observer finite-record identity error {max_identity} > 2e-8")

    comparison_rows = build_comparison_rows(case_rows)
    source_summary, morphology_summary = build_summaries(comparison_rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_map = {
        "case_metrics": output_dir / f"{STEM}_case_metrics.csv",
        "layout_vs_seven_comparisons": output_dir / f"{STEM}_layout_vs_seven_comparisons.csv",
        "source_summary": output_dir / f"{STEM}_source_summary.csv",
        "morphology_summary": output_dir / f"{STEM}_morphology_summary.csv",
        "finite_dft_identity": output_dir / f"{STEM}_finite_dft_identity.csv",
        "basis_hashes": output_dir / f"{STEM}_basis_hashes.csv",
    }
    write_csv(output_map["case_metrics"], case_rows)
    write_csv(output_map["layout_vs_seven_comparisons"], comparison_rows)
    write_csv(output_map["source_summary"], source_summary)
    write_csv(output_map["morphology_summary"], morphology_summary)
    write_csv(output_map["finite_dft_identity"], identity_rows)
    write_csv(output_map["basis_hashes"], basis_rows)
    report = {
        "schema_version": 1,
        "status": "passed",
        "study": "q25 observer-only readouts with fixed versus q25-enriched PRIMA input bases",
        "primary_reference": {
            "report_sha256": sha256_file(primary_report_path),
            "case_metrics_sha256": sha256_file(primary_case_path),
            "basis_hash_match_count": len(basis_rows),
            "basis_hash_expected": 144,
        },
        "runtime": runtime,
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(runner.LAYOUT_IDS),
            "basis_order": runner.BASIS_ORDER,
            "sources": list(runner.SOURCE_NAMES),
            "pulse_widths_ms": list(runner.PULSE_WIDTHS_MS),
            "windows_ms": list(runner.WINDOWS_MS),
            "q25_output_roles": list(role_order),
            "q25_output_swc_ids_by_morphology": {
                item["morphology"]: item["q25_node_ids"] for item in morphology_manifest
            },
            "method": (
                "For every layout, q25 voltages are read from the full-compartment basis rows. "
                "When a q25 node is not retained, it remains an observation-only output; it is "
                "not added to the input selector B. This separates output measurement from "
                "the Krylov subspace change caused by adding a retained input/output port."
            ),
        },
        "coverage": {
            "case_metrics_rows": len(case_rows),
            "candidate_vs_seven_comparisons": len(comparison_rows),
            "source_summary_rows": len(source_summary),
            "morphology_summary_rows": len(morphology_summary),
            "finite_dft_identity_rows": len(identity_rows),
            "basis_hash_rows_matched_to_primary": len(basis_rows),
            "max_finite_identity_relative_error": max_identity,
            "identity_tolerance": 2e-8,
        },
        "outputs": {name: path.name for name, path in output_map.items()},
        "interpretation_limits": [
            "This observer-only analysis does not change production code or the primary four-layout model.",
            "The 144 PRIMA basis hashes must match the accepted pinned order-168 report exactly before any output comparison is accepted.",
            "The experiment remains passive linear-RC and uses four individual morphologies, not a biological population.",
            "Large relative ratios are accompanied by absolute error changes because the seven-port q25 observer residual may be near zero.",
        ],
        "wall_seconds": time.perf_counter() - started,
    }
    report_path = output_dir / f"{STEM}_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()
    result = run(args.primary_results_dir, args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
