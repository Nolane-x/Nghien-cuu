#!/usr/bin/env python3
"""One-morphology output-aware dual-seed PRIMA pilot for Peng NMO_163775.

This research-only pilot keeps the canonical seven-port input selector fixed
and adds q25 output-dual resolvent vectors only to the state basis. It compares
five predeclared dual-seed schedules at order 224 against the same full-Hines
reference. It does not modify or invoke a new production solver path.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np

import audit_prima_q25_basis_conditioning as conditioning
import audit_prima_q25_extended_backward_euler as tail
import analyze_prima_q25_four_morphology_four_layout_boundary_ablation as core
from experimental_prima_output_aware_basis import build_output_aware_passive_basis

ORDER = 224
DT_MS = 0.00625
DT_S = DT_MS / 1000.0
WINDOWS_MS = (20.0, 40.0)
RESULT_STEM = "prima_q25_peng_output_aware_dual_seed_pilot_order224_2026-11-25"
EXPECTED_SOURCE_SHA256 = conditioning.peng_replay.EXPECTED_SWC_SHA256
EXPECTED_SOURCE_RECORDS = conditioning.peng_replay.EXPECTED_SWC_RECORDS
OUTPUT_DUAL_SCHEDULES = {
    "D0_none": (),
    "D1_low_0hz": (0.0,),
    "D1_mid_1000hz": (1000.0,),
    "D1_high_10000hz": (10000.0,),
    "D2_mid_high": (1000.0, 10000.0),
}
IDENTITY_SCHEDULES = ("D0_none", "D2_mid_high")
FINITE_IDENTITY_RELATIVE_TOLERANCE = 2e-8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def nrmse_percent(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.float64)
    got = np.asarray(candidate, dtype=np.float64)
    require(ref.shape == got.shape, "reference/candidate trace shape mismatch")
    require(np.all(np.isfinite(ref)) and np.all(np.isfinite(got)),
            "transient metric received non-finite values")
    return float(100.0 * np.linalg.norm(got - ref) / max(float(np.linalg.norm(ref)), 1e-30))


def solve_projected_outputs(
    model,
    s_values_per_s: np.ndarray,
    rhs_base: np.ndarray,
    output_rows: np.ndarray,
    *,
    chunk_size: int = 32,
) -> np.ndarray:
    """Solve a reduced transfer with an output map L V independent of B."""
    shifts = np.asarray(s_values_per_s, dtype=np.complex128)
    rhs0 = np.asarray(rhs_base, dtype=np.complex128)
    outputs = np.asarray(output_rows, dtype=np.float64)
    require(rhs0.ndim == 2 and rhs0.shape[0] == model.order,
            "projected RHS shape mismatch")
    require(outputs.ndim == 2 and outputs.shape[1] == model.order,
            "projected output-row shape mismatch")
    response = np.empty((shifts.size, outputs.shape[0], rhs0.shape[1]),
                        dtype=np.complex128)
    for start in range(0, shifts.size, chunk_size):
        stop = min(start + chunk_size, shifts.size)
        local_s = shifts[start:stop]
        lhs = (
            model.conductance_matrix_s[None, :, :].astype(np.complex128)
            + local_s[:, None, None] * model.capacitance_matrix_f[None, :, :]
        )
        rhs = np.broadcast_to(
            rhs0[None, :, :], (stop - start, model.order, rhs0.shape[1])
        )
        state = np.linalg.solve(lhs, rhs)
        response[start:stop] = np.einsum("ok,fkr->for", outputs, state, optimize=True)
    require(np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag)),
            "non-finite projected output response")
    return response


def simulate_reduced_outputs(
    model,
    layout: dict[str, Any],
    output_rows: np.ndarray,
    protocol: list[tuple[str, float]],
) -> tuple[np.ndarray, dict[float, np.ndarray]]:
    """Replay reduced BE and observe any full-compartment basis rows."""
    sample_count = int(round(max(WINDOWS_MS) / DT_MS))
    factor = tail.factor_reduced_backward_euler(model, DT_S)
    state = np.zeros((model.order, len(protocol)), dtype=np.float64)
    port_current = np.zeros((layout["port_count"], len(protocol)), dtype=np.float64)
    source_slots = {source: int(layout["source_indices"][source]) for source in core.SOURCE_NAMES}
    trace = np.empty((sample_count, output_rows.shape[0], len(protocol)), dtype=np.float64)
    boundary_steps = {
        int(round(window_ms / DT_MS)): float(window_ms) for window_ms in WINDOWS_MS
    }
    terminal_states: dict[float, np.ndarray] = {}
    onset_s = tail.PULSE_ONSET_MS / 1000.0

    for step in range(sample_count):
        port_current.fill(0.0)
        now_s = step * DT_S
        for column, (source_name, pulse_width_ms) in enumerate(protocol):
            stop_s = onset_s + pulse_width_ms / 1000.0
            if onset_s <= now_s < stop_s:
                port_current[source_slots[source_name], column] = tail.CURRENT_A
        state = tail.reduced_backward_euler_step_factorized(
            model, factor, state, port_current, DT_S
        )
        trace[step] = output_rows @ state
        completed = step + 1
        if completed in boundary_steps:
            terminal_states[boundary_steps[completed]] = state.copy()

    require(set(terminal_states) == set(WINDOWS_MS),
            "reduced terminal-state window coverage mismatch")
    require(np.all(np.isfinite(trace)), "non-finite reduced output trace")
    return trace, terminal_states


def finite_record_identity(
    *,
    tree,
    model,
    full_trace: np.ndarray,
    full_terminal_states: dict[float, np.ndarray],
    reduced_trace: np.ndarray,
    reduced_terminal_states: dict[float, np.ndarray],
    output_tree_indices: list[int],
    source_tree_indices: list[int],
    source_slots: dict[str, int],
    protocol: list[tuple[str, float]],
    window_ms: float = 20.0,
) -> dict[str, Any]:
    """Check the exact finite-record BE DFT identity on every selected output.

    This pilot gate uses the complete DFT grid for the predeclared soma/2-ms
    record at 20 ms. It is not a claim that every source/pulse combination has
    been frequency-audited in this initial pilot.
    """
    require(window_ms in WINDOWS_MS, "unsupported pilot DFT window")
    column = protocol.index(("soma", 2.0))
    sample_count = int(round(window_ms / DT_MS))
    frequencies_hz, _ = core.finite_window_frequency_indices(window_ms)
    s_be = core.backward_euler_s_values(frequencies_hz, DT_S)
    sampled_protocol, current_matrix = core.build_sampled_protocol(sample_count)
    require(sampled_protocol == protocol, "sampled input protocol mismatch")
    input_spectrum = np.fft.rfft(current_matrix[:, column])

    actual_full = np.fft.rfft(full_trace[:sample_count, :, column], axis=0)
    actual_reduced = np.fft.rfft(reduced_trace[:sample_count, :, column], axis=0)

    source_name, _ = protocol[column]
    source_tree_index = int(source_tree_indices[core.SOURCE_NAMES.index(source_name)])
    full_rhs = np.zeros((tree.n_compartments, 1), dtype=np.float64)
    full_rhs[source_tree_index, 0] = 1.0
    full_input = core.solve_full_hines_s_response(
        tree, s_be, full_rhs, output_tree_indices, chunk_size=32
    )[:, :, 0]
    full_terminal_rhs = (
        np.asarray(tree.capacitance_f, dtype=np.float64) / DT_S
        * full_terminal_states[window_ms][:, column]
    )[:, None]
    full_boundary = core.solve_full_hines_s_response(
        tree, s_be, full_terminal_rhs, output_tree_indices, chunk_size=32
    )[:, :, 0]
    full_reconstructed = full_input * input_spectrum[:, None] - full_boundary
    full_rel, full_abs = core._finite_identity_error(
        actual_full, full_reconstructed,
        scale_norm=float(np.linalg.norm(actual_full)),
    )

    reduced_rhs = model.input_matrix[:, int(source_slots[source_name])][:, None]
    reduced_input = solve_projected_outputs(
        model, s_be, reduced_rhs, model.basis[np.asarray(output_tree_indices), :]
    )[:, :, 0]
    reduced_terminal_rhs = (
        model.capacitance_matrix_f / DT_S
        @ reduced_terminal_states[window_ms][:, column]
    )[:, None]
    reduced_boundary = solve_projected_outputs(
        model, s_be, reduced_terminal_rhs,
        model.basis[np.asarray(output_tree_indices), :],
    )[:, :, 0]
    reduced_reconstructed = reduced_input * input_spectrum[:, None] - reduced_boundary
    reduced_rel, reduced_abs = core._finite_identity_error(
        actual_reduced, reduced_reconstructed,
        scale_norm=float(np.linalg.norm(actual_reduced)),
    )

    return {
        "window_ms": window_ms,
        "input_record": {"source": source_name, "pulse_width_ms": protocol[column][1]},
        "frequency_bins": int(frequencies_hz.size),
        "full_hines_max_relative_error": float(full_rel),
        "full_hines_max_absolute_error": float(full_abs),
        "reduced_max_relative_error": float(reduced_rel),
        "reduced_max_absolute_error": float(reduced_abs),
        "tolerance": FINITE_IDENTITY_RELATIVE_TOLERANCE,
        "passed": bool(
            full_rel <= FINITE_IDENTITY_RELATIVE_TOLERANCE
            and reduced_rel <= FINITE_IDENTITY_RELATIVE_TOLERANCE
        ),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty pilot output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    morph_spec = next(
        item for item in core.MORPHOLOGIES
        if item["neuromorpho_id"] == "NMO_163775"
    )
    require(morph_spec["name"] == "NMO_163775_Peng_mouse_Control",
            "pilot must remain pinned to Peng NMO_163775")
    module = morph_spec["module"]
    baseline = module.baseline
    reference = baseline.reference
    reference.DATA = module.SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.5

    morphology = baseline.SWCMorphology.from_file(module.SWC)
    require(len(morphology.nodes) == EXPECTED_SOURCE_RECORDS,
            "Peng SWC record count mismatch")
    source_sha256 = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
    require(source_sha256 == EXPECTED_SOURCE_SHA256,
            "Peng SWC checksum mismatch")
    preflight = json.loads(morph_spec["preflight"].read_text(encoding="utf-8"))
    require(preflight.get("status") == "PASS", "Peng morphology preflight failed")
    require(preflight.get("source", {}).get("source_sha256") == source_sha256,
            "Peng preflight/source checksum mismatch")

    reader, sections = reference.import_swc_with_neuron()
    base_tree = morphology.to_cable_tree()
    layouts, shared_node_ids, q25_node_ids = module.build_four_layouts(
        morphology, reader, sections, base_tree
    )
    seven_layout = layouts["seven"]
    retained_indices = tuple(int(x) for x in seven_layout["ports"])
    source_tree_indices = [
        int(seven_layout["ports"][int(seven_layout["source_indices"][source])])
        for source in core.SOURCE_NAMES
    ]
    electrical_map = morphology.electrical_node_mapping()
    q25_tree_indices = {
        role: int(base_tree.index[f"swc_{electrical_map[int(node_id)]}"])
        for role, node_id in q25_node_ids.items()
    }
    output_tree_indices = retained_indices + (
        q25_tree_indices["basal_q25"], q25_tree_indices["apical_q25"]
    )
    require(len(retained_indices) == 7 and len(set(retained_indices)) == 7,
            "seven-port input selector must contain seven unique indices")
    require(len(output_tree_indices) == 9 and len(set(output_tree_indices)) == 9,
            "seven shared and two q25 observation sites must be distinct")

    scenario_cases = baseline.parameter_cases()
    require("nominal" in scenario_cases, "nominal passive parameter case is missing")
    target = conditioning.build_target_tree(module, base_tree, scenario_cases["nominal"])
    hines_factor = tail.build_tree_hines_be_factor(target, DT_S)
    full_trace, full_terminal_states, protocol = core.simulate_full_hines_perturbation_windows(
        target, hines_factor, source_tree_indices, list(output_tree_indices)
    )
    source_slots = {source: int(seven_layout["source_indices"][source]) for source in core.SOURCE_NAMES}

    # D0 parity is checked on the actual full Peng morphology, not only the toy fixture.
    production_d0 = baseline.prima_reduce_passive_cable_multishift(
        target, list(retained_indices), ORDER, conditioning.SHIFTS_HZ,
        relative_tolerance=conditioning.RELATIVE_TOLERANCE,
    )

    result_rows: list[dict[str, Any]] = []
    schedule_metadata: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    model_traces: dict[str, Any] = {}
    for schedule_name, dual_frequencies in OUTPUT_DUAL_SCHEDULES.items():
        schedule_started = time.perf_counter()
        enriched = build_output_aware_passive_basis(
            target,
            retained_indices,
            (q25_tree_indices["basal_q25"], q25_tree_indices["apical_q25"]),
            max_order=ORDER,
            input_expansion_frequencies_hz=conditioning.SHIFTS_HZ,
            output_seed_frequencies_hz=dual_frequencies,
            relative_tolerance=conditioning.RELATIVE_TOLERANCE,
        )
        model = enriched.model
        require(model.order == ORDER, f"{schedule_name}: did not reach order {ORDER}")
        require(tuple(model.port_indices) == retained_indices,
                f"{schedule_name}: input port list changed from canonical seven")
        require(model.input_matrix.shape == (ORDER, 7),
                f"{schedule_name}: reduced input matrix must remain order x 7")
        np.testing.assert_array_equal(
            model.input_matrix, model.basis[np.asarray(retained_indices), :].T
        )
        output_rows = model.basis[np.asarray(output_tree_indices), :]
        require(output_rows.shape == (9, ORDER),
                f"{schedule_name}: output map does not expose seven shared plus two q25 rows")
        gram_error = float(np.max(np.abs(model.basis.T @ model.basis - np.eye(ORDER))))
        require(gram_error < 2e-12, f"{schedule_name}: basis orthogonality failed")
        np.linalg.cholesky(model.conductance_matrix_s)
        np.linalg.cholesky(model.capacitance_matrix_f)

        if schedule_name == "D0_none":
            np.testing.assert_array_equal(model.basis, production_d0.basis)
            np.testing.assert_array_equal(
                model.conductance_matrix_s, production_d0.conductance_matrix_s
            )
            np.testing.assert_array_equal(
                model.capacitance_matrix_f, production_d0.capacitance_matrix_f
            )
            np.testing.assert_array_equal(model.input_matrix, production_d0.input_matrix)

        reduced_trace, reduced_terminal = simulate_reduced_outputs(
            model, seven_layout, output_rows, protocol
        )
        models[schedule_name] = model
        model_traces[schedule_name] = (reduced_trace, reduced_terminal)

        for window_ms in WINDOWS_MS:
            sample_count = int(round(window_ms / DT_MS))
            for output_index, tree_index in enumerate(output_tree_indices):
                if output_index < 7:
                    role = "shared_output"
                    output_label = f"shared_{output_index + 1}"
                    swc_node_id = int(shared_node_ids[output_index])
                else:
                    role = "q25_output"
                    output_label = "basal_q25" if output_index == 7 else "apical_q25"
                    swc_node_id = int(q25_node_ids[output_label])
                for column, (source_name, pulse_width_ms) in enumerate(protocol):
                    full_values = full_trace[:sample_count, output_index, column]
                    reduced_values = reduced_trace[:sample_count, output_index, column]
                    error_pct = nrmse_percent(full_values, reduced_values)
                    result_rows.append({
                        "schedule": schedule_name,
                        "dual_seed_frequencies_hz": ";".join(str(x) for x in dual_frequencies),
                        "basis_order": model.order,
                        "morphology": morph_spec["name"],
                        "scenario": "nominal",
                        "window_ms": window_ms,
                        "source": source_name,
                        "pulse_width_ms": pulse_width_ms,
                        "output_role": role,
                        "output_label": output_label,
                        "swc_node_id": swc_node_id,
                        "transient_nrmse_pct": error_pct,
                    })

        schedule_metadata.append({
            "schedule": schedule_name,
            "output_dual_frequencies_hz": list(dual_frequencies),
            "input_seed_columns_per_shift": list(enriched.diagnostics.input_seed_columns_per_shift),
            "output_seed_columns_per_shift": list(enriched.diagnostics.output_seed_columns_per_shift),
            "initial_input_seed_columns": enriched.diagnostics.initial_input_seed_columns,
            "initial_output_seed_columns": enriched.diagnostics.initial_output_seed_columns,
            "actual_order": model.order,
            "basis_sha256": sha256_array(model.basis),
            "conductance_sha256": sha256_array(model.conductance_matrix_s),
            "capacitance_sha256": sha256_array(model.capacitance_matrix_f),
            "input_sha256": sha256_array(model.input_matrix),
            "basis_orthogonality_max_abs": gram_error,
            "conductance_condition_number": float(np.linalg.cond(model.conductance_matrix_s)),
            "capacitance_condition_number": float(np.linalg.cond(model.capacitance_matrix_f)),
            "wall_seconds": time.perf_counter() - schedule_started,
            "seven_input_ports_unchanged": True,
        })

    baseline_error = {
        (row["window_ms"], row["source"], row["pulse_width_ms"],
         row["output_label"]): row["transient_nrmse_pct"]
        for row in result_rows if row["schedule"] == "D0_none"
    }
    summary_rows: list[dict[str, Any]] = []
    for schedule_name in OUTPUT_DUAL_SCHEDULES:
        for window_ms in WINDOWS_MS:
            for output_role, output_label in (
                [("shared_output", f"shared_{i}") for i in range(1, 8)]
                + [("q25_output", "basal_q25"), ("q25_output", "apical_q25")]
            ):
                cases = [
                    row for row in result_rows
                    if row["schedule"] == schedule_name
                    and row["window_ms"] == window_ms
                    and row["output_label"] == output_label
                ]
                ratios = []
                deltas = []
                for row in cases:
                    key = (window_ms, row["source"], row["pulse_width_ms"], output_label)
                    baseline = float(baseline_error[key])
                    current = float(row["transient_nrmse_pct"])
                    ratios.append(current / max(baseline, 1e-30))
                    deltas.append(current - baseline)
                worse = sum(x > 0.0 for x in deltas)
                better = sum(x < 0.0 for x in deltas)
                summary_rows.append({
                    "schedule": schedule_name,
                    "window_ms": window_ms,
                    "output_role": output_role,
                    "output_label": output_label,
                    "matched_cases": len(cases),
                    "median_candidate_over_D0_error_ratio": float(np.median(ratios)),
                    "p90_candidate_over_D0_error_ratio": float(np.percentile(ratios, 90)),
                    "median_absolute_error_delta_percentage_points": float(np.median(deltas)),
                    "candidate_worse_cases": worse,
                    "candidate_better_cases": better,
                })

    # A complete finite-record identity audit is run on the baseline and the
    # most strongly enriched schedule, for the predeclared soma/2-ms 20-ms record.
    identity_results = []
    for schedule_name in IDENTITY_SCHEDULES:
        model = models[schedule_name]
        reduced_trace, reduced_terminal = model_traces[schedule_name]
        identity_results.append({
            "schedule": schedule_name,
            **finite_record_identity(
                tree=target,
                model=model,
                full_trace=full_trace,
                full_terminal_states=full_terminal_states,
                reduced_trace=reduced_trace,
                reduced_terminal_states=reduced_terminal,
                output_tree_indices=list(output_tree_indices),
                source_tree_indices=source_tree_indices,
                source_slots=source_slots,
                protocol=protocol,
                window_ms=20.0,
            ),
        })
    require(all(item["passed"] for item in identity_results),
            "pilot finite-record DFT identity gate failed")

    # Exact paired coverage: five schedules x six current records x nine outputs
    # x two windows. D0 must be included as the parity/reference schedule.
    expected_case_rows = len(OUTPUT_DUAL_SCHEDULES) * len(protocol) * 9 * len(WINDOWS_MS)
    require(len(result_rows) == expected_case_rows,
            f"pilot case row coverage mismatch: expected {expected_case_rows}, got {len(result_rows)}")
    expected_summary_rows = len(OUTPUT_DUAL_SCHEDULES) * 9 * len(WINDOWS_MS)
    require(len(summary_rows) == expected_summary_rows,
            "pilot schedule/output/window summary coverage mismatch")

    results_dir = Path(__file__).parents[1] / "results"
    case_path = results_dir / f"{RESULT_STEM}_case_metrics.csv"
    summary_path = results_dir / f"{RESULT_STEM}_summary.csv"
    report_path = results_dir / f"{RESULT_STEM}_report.json"
    write_csv(case_path, result_rows)
    write_csv(summary_path, summary_rows)
    case_readback = sum(1 for _ in case_path.open("r", encoding="utf-8")) - 1
    summary_readback = sum(1 for _ in summary_path.open("r", encoding="utf-8")) - 1
    require(case_readback == expected_case_rows, "pilot case CSV read-back mismatch")
    require(summary_readback == expected_summary_rows, "pilot summary CSV read-back mismatch")

    report = {
        "schema_version": 1,
        "status": "passed",
        "study": "Peng NMO_163775 nominal-scenario output-aware dual-seed pilot",
        "source": {
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "records": len(morphology.nodes),
            "swc_sha256": source_sha256,
            "preflight_status": preflight.get("status"),
            "shared_output_node_ids": shared_node_ids,
            "q25_node_ids": q25_node_ids,
        },
        "fixed_protocol": {
            "basis_order": ORDER,
            "input_ports": 7,
            "output_rows": 9,
            "input_expansion_shifts_hz": list(conditioning.SHIFTS_HZ),
            "dual_seed_schedules": {
                key: list(value) for key, value in OUTPUT_DUAL_SCHEDULES.items()
            },
            "scenario": "nominal",
            "sources": list(core.SOURCE_NAMES),
            "pulse_widths_ms": list(tail.PULSE_WIDTHS_MS),
            "pulse_onset_ms": tail.PULSE_ONSET_MS,
            "pulse_amplitude_pA": tail.CURRENT_A * 1e12,
            "dt_ms": DT_MS,
            "windows_ms": list(WINDOWS_MS),
            "mesh_cap_um": 0.5,
        },
        "schedule_metadata": schedule_metadata,
        "finite_dft_identity": identity_results,
        "coverage": {
            "case_metrics_expected": expected_case_rows,
            "case_metrics_read_back": case_readback,
            "summary_expected": expected_summary_rows,
            "summary_read_back": summary_readback,
        },
        "files": {
            "case_metrics": case_path.name,
            "summary": summary_path.name,
        },
        "scientific_limits": [
            "Single Peng morphology and nominal passive scenario only; not a multi-morphology conclusion.",
            "A finite-record DFT identity is checked for the predeclared soma/2-ms 20-ms record on D0 and D2-mid-high only.",
            "All six source/pulse records are evaluated in the time domain, but the DFT identity has not been swept across all source/pulse/window combinations.",
            "The prototype enriches the state basis with q25 output-dual seeds while preserving the seven-port input selector; it is not a nine-port input model.",
            "This is passive linear-RC model-reduction evidence, not biological validation.",
            "No production solver/default changes are made; full Hines remains canonical.",
        ],
    }
    report["runtime"] = {
        "wall_seconds": time.perf_counter() - started,
        "numerical_runtime": core.numerical_runtime_diagnostics(),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    timing_path = results_dir / f"{RESULT_STEM}.time.txt"
    timing_path.write_text(
        f"elapsed_wall_seconds={report['runtime']['wall_seconds']:.6f}\n"
        "exit_status=0\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "case_metrics_rows": case_readback,
        "summary_rows": summary_readback,
        "identity": identity_results,
        "results": [case_path.name, summary_path.name, report_path.name, timing_path.name],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PILOT FAILED: {type(exc).__name__}: {exc}", file=__import__("sys").stderr)
        raise
