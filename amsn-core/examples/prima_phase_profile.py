#!/usr/bin/env python3
"""Profile PRIMA build phases and solver costs on a provenance-pinned human morphology.

The PRIMA builder itself is not reimplemented. cProfile observes the existing
prima_reduce_passive_cable_multishift implementation and attributes Python
self-time to its shifted Hines solve, block orthogonalization, congruence
projection and top-level orchestration. Full-Hines measurements run in a
separate process (workflow step) so peak RSS is not mixed with PRIMA.
"""
from __future__ import annotations

import argparse
import cProfile
import csv
import json
import os
import platform
import pstats
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from amsn.prima import PassiveReducedModel, prima_reduce_passive_cable_multishift

ORDERS = (84, 112, 168)
EXPANSION_SHIFTS_HZ = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
FREQUENCIES_HZ = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
DEFAULT_REPEATS = 2
DT_S = 0.1e-3
TRANSIENT_STEPS = 100
PULSE_START_STEP = 20
PULSE_STOP_STEP = 40
PULSE_CURRENT_A = 10e-12

PROFILE_FUNCTIONS = {
    "shifted_hines_solve": "_solve_shifted_passive_real",
    "orthogonalization": "_orthogonalize_block",
    "congruence_projection": "_project_passive_basis",
    "multishift_orchestration": "prima_reduce_passive_cable_multishift",
}


def profile_prima_build(
    tree,
    retained_indices,
    max_order: int,
    expansion_frequencies_hz=EXPANSION_SHIFTS_HZ,
):
    """Run the real PRIMA builder once and return model + non-overlapping self-time."""
    profiler = cProfile.Profile()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    profiler.enable()
    model = prima_reduce_passive_cable_multishift(
        tree,
        retained_indices,
        max_order=max_order,
        expansion_frequencies_hz=expansion_frequencies_hz,
    )
    profiler.disable()
    cpu_seconds = time.process_time() - cpu_start
    wall_seconds = time.perf_counter() - wall_start

    stats = pstats.Stats(profiler)
    totals = {
        name: {"calls": 0, "self_seconds": 0.0, "cumulative_seconds": 0.0}
        for name in PROFILE_FUNCTIONS
    }
    for (filename, _line, function_name), values in stats.stats.items():
        if Path(filename).name != "prima.py" or function_name not in PROFILE_FUNCTIONS.values():
            continue
        primitive_calls, calls, self_seconds, cumulative_seconds, _callers = values
        item = next(key for key, value in PROFILE_FUNCTIONS.items() if value == function_name)
        totals[item]["calls"] += int(calls)
        totals[item]["self_seconds"] += float(self_seconds)
        totals[item]["cumulative_seconds"] += float(cumulative_seconds)

    selected_self = sum(item["self_seconds"] for item in totals.values())
    total_python_self = sum(
        float(values[2])
        for (filename, _line, _name), values in stats.stats.items()
        if filename != "~"
    )
    total_function_self = float(stats.total_tt)
    other_python_self = max(0.0, total_python_self - selected_self)
    native_function_self = max(0.0, total_function_self - total_python_self)
    totals["other_python_self"] = {
        "calls": 0,
        "self_seconds": other_python_self,
        "cumulative_seconds": other_python_self,
    }
    totals["native_function_self"] = {
        "calls": 0,
        "self_seconds": native_function_self,
        "cumulative_seconds": native_function_self,
    }
    summary = {
        "phases": totals,
        "profiled_python_self_seconds": total_python_self,
        "profiled_total_function_self_seconds": total_function_self,
        "profiled_total_calls": int(stats.total_calls),
        "build_wall_seconds": wall_seconds,
        "build_process_cpu_seconds": cpu_seconds,
    }
    return model, summary


def measure_unprofiled_build(
    tree,
    retained_indices,
    max_order: int,
    expansion_frequencies_hz=EXPANSION_SHIFTS_HZ,
):
    """Measure the same builder without cProfile instrumentation."""
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    model = prima_reduce_passive_cable_multishift(
        tree,
        retained_indices,
        max_order=max_order,
        expansion_frequencies_hz=expansion_frequencies_hz,
    )
    return (
        model,
        time.perf_counter() - start_wall,
        time.process_time() - start_cpu,
    )


def measure_reduced_frequency(model: PassiveReducedModel, frequencies_hz=FREQUENCIES_HZ):
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    frequencies = tuple(frequencies_hz)
    checksums = []
    for frequency_hz in frequencies:
        impedance = model.impedance_matrix(float(frequency_hz))
        if not (np.all(np.isfinite(impedance.real)) and np.all(np.isfinite(impedance.imag))):
            raise FloatingPointError("reduced frequency solve produced non-finite impedance")
        checksums.append(float(np.linalg.norm(impedance)))
    return {
        "solve_calls": len(frequencies),
        "wall_seconds": time.perf_counter() - start_wall,
        "cpu_seconds": time.process_time() - start_cpu,
        "finite_checksum": all(np.isfinite(value) for value in checksums),
    }


def measure_hines_frequency(tree, retained_indices, frequencies_hz=FREQUENCIES_HZ):
    """Build the same retained-port impedance matrix using one Hines solve per source."""
    ports = tuple(int(value) for value in retained_indices)
    frequencies = tuple(frequencies_hz)
    current = np.zeros(tree.n_compartments, dtype=np.complex128)
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    checksums = []
    for frequency_hz in frequencies:
        impedance = np.empty((len(ports), len(ports)), dtype=np.complex128)
        for column, source_index in enumerate(ports):
            current.fill(0.0)
            current[source_index] = 1.0
            response = tree.solve_passive_frequency_response(float(frequency_hz), current)
            impedance[:, column] = response[np.asarray(ports, dtype=int)]
        if not (np.all(np.isfinite(impedance.real)) and np.all(np.isfinite(impedance.imag))):
            raise FloatingPointError("full-Hines frequency solve produced non-finite impedance")
        checksums.append(float(np.linalg.norm(impedance)))
    return {
        "solve_calls": len(frequencies) * len(ports),
        "wall_seconds": time.perf_counter() - start_wall,
        "cpu_seconds": time.process_time() - start_cpu,
        "finite_checksum": all(np.isfinite(value) for value in checksums),
    }


def measure_reduced_transient(model: PassiveReducedModel, source_port: int = 0):
    if source_port < 0 or source_port >= model.port_count:
        raise ValueError("source_port is outside the retained-port range")
    state = np.zeros(model.order, dtype=float)
    current = np.zeros(model.port_count, dtype=float)
    peak_delta_v = 0.0
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    for step in range(TRANSIENT_STEPS):
        current.fill(0.0)
        if PULSE_START_STEP <= step < PULSE_STOP_STEP:
            current[source_port] = PULSE_CURRENT_A
        state = model.step_backward_euler(state, DT_S, current)
        port_values = model.port_voltages(state)
        if not np.all(np.isfinite(port_values)):
            raise FloatingPointError("reduced transient produced non-finite port voltage")
        peak_delta_v = max(peak_delta_v, float(np.max(np.abs(port_values))))
    wall_seconds = time.perf_counter() - start_wall
    return {
        "steps": TRANSIENT_STEPS,
        "wall_seconds": wall_seconds,
        "cpu_seconds": time.process_time() - start_cpu,
        "seconds_per_step": wall_seconds / TRANSIENT_STEPS,
        "peak_port_perturbation_v": peak_delta_v,
    }


def measure_hines_transient(tree, retained_indices, source_port: int = 0):
    ports = tuple(int(value) for value in retained_indices)
    if source_port < 0 or source_port >= len(ports):
        raise ValueError("source_port is outside the retained-port range")
    voltage = np.full(tree.n_compartments, tree.parameters.e_leak_v, dtype=float)
    current = np.zeros(tree.n_compartments, dtype=float)
    peak_delta_v = 0.0
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    for step in range(TRANSIENT_STEPS):
        current.fill(0.0)
        if PULSE_START_STEP <= step < PULSE_STOP_STEP:
            current[ports[source_port]] = PULSE_CURRENT_A
        voltage = tree.step_passive(voltage, DT_S, current)
        port_delta = voltage[np.asarray(ports, dtype=int)] - tree.parameters.e_leak_v
        if not np.all(np.isfinite(port_delta)):
            raise FloatingPointError("full-Hines transient produced non-finite port voltage")
        peak_delta_v = max(peak_delta_v, float(np.max(np.abs(port_delta))))
    wall_seconds = time.perf_counter() - start_wall
    return {
        "steps": TRANSIENT_STEPS,
        "wall_seconds": wall_seconds,
        "cpu_seconds": time.process_time() - start_cpu,
        "seconds_per_step": wall_seconds / TRANSIENT_STEPS,
        "peak_port_perturbation_v": peak_delta_v,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]):
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _runner_cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(errors="replace").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def prepare_morphology():
    label = os.environ["AMSN_MORPHOLOGY_LABEL"]
    swc_path = Path(os.environ["AMSN_MORPHOLOGY_PATH"])
    expected = int(os.environ["AMSN_EXPECTED_SWC_RECORDS"])
    if not swc_path.is_file():
        raise FileNotFoundError(f"morphology SWC is missing: {swc_path}")

    import human_fine_mesh_passive_dc_audit as fine_audit
    import neuron_cross_validation as reference
    from amsn.morphology import SWCMorphology

    reference.DATA = swc_path
    reference.MAX_NEURON_SEGMENT_UM = float(
        os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125")
    )
    morphology = SWCMorphology.from_file(swc_path)
    if len(morphology.nodes) != expected:
        raise RuntimeError(f"SWC records {len(morphology.nodes)} != expected {expected}")

    reader, sections = reference.import_swc_with_neuron()
    injections, probes, mapped = fine_audit.build_sites(morphology, reader, sections)
    port_node_ids = list(dict.fromkeys(node_id for _role, node_id in injections + probes))
    if len(port_node_ids) != 7 or len(set(port_node_ids)) != 7:
        raise RuntimeError(f"expected exactly seven unique source/probe nodes, got {len(port_node_ids)}")
    if set(port_node_ids) - set(mapped):
        raise RuntimeError("one or more retained ports failed the Import3D mapping")

    electrical_mapping = morphology.electrical_node_mapping()
    tree = morphology.to_cable_tree()
    ports = [tree.index[f"swc_{electrical_mapping[node_id]}"] for node_id in port_node_ids]
    if len(set(ports)) != 7:
        raise RuntimeError("SWC-to-AMSN mapping collapsed one or more retained ports")
    return label, swc_path, morphology, tree, tuple(ports), tuple(port_node_ids)


def run_prima_mode(args):
    label, swc_path, morphology, tree, ports, node_ids = prepare_morphology()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    build_rows: list[dict[str, Any]] = []
    solver_rows: list[dict[str, Any]] = []

    # One unrecorded build warms import/BLAS paths. Timed repeats follow.
    prima_reduce_passive_cable_multishift(
        tree, ports, max_order=ORDERS[0],
        expansion_frequencies_hz=EXPANSION_SHIFTS_HZ,
    )

    for order in ORDERS:
        unprofiled_model, unprofiled_wall_seconds, unprofiled_cpu_seconds = (
            measure_unprofiled_build(tree, ports, order, EXPANSION_SHIFTS_HZ)
        )
        if unprofiled_model.order != order:
            raise RuntimeError(
                f"unprofiled builder requested order {order}, achieved {unprofiled_model.order}"
            )
        for replicate in range(1, args.repeats + 1):
            model, summary = profile_prima_build(
                tree, ports, order, EXPANSION_SHIFTS_HZ
            )
            if model.order != order:
                raise RuntimeError(f"requested PRIMA order {order}, achieved {model.order}")
            np.linalg.cholesky(model.conductance_matrix_s)
            np.linalg.cholesky(model.capacitance_matrix_f)
            storage_bytes = (
                model.basis.nbytes
                + model.conductance_matrix_s.nbytes
                + model.capacitance_matrix_f.nbytes
                + model.input_matrix.nbytes
            )
            phase_names = (
                "shifted_hines_solve",
                "orthogonalization",
                "congruence_projection",
                "multishift_orchestration",
                "other_python_self",
                "native_function_self",
            )
            if set(summary["phases"]) != set(phase_names):
                raise RuntimeError("profile phase coverage changed unexpectedly")
            for phase in phase_names:
                item = summary["phases"][phase]
                build_rows.append({
                    "morphology": label,
                    "swc_records": len(morphology.nodes),
                    "full_compartments": tree.n_compartments,
                    "retained_ports": len(ports),
                    "prima_order": order,
                    "replicate": replicate,
                    "phase": phase,
                    "calls": item["calls"],
                    "self_seconds": item["self_seconds"],
                    "cumulative_seconds": item["cumulative_seconds"],
                    "build_wall_seconds": summary["build_wall_seconds"],
                    "build_process_cpu_seconds": summary["build_process_cpu_seconds"],
                    "profiled_python_self_seconds": summary["profiled_python_self_seconds"],
                    "profiled_total_function_self_seconds": summary["profiled_total_function_self_seconds"],
                    "profiled_total_calls": summary["profiled_total_calls"],
                    "unprofiled_build_wall_seconds": unprofiled_wall_seconds,
                    "unprofiled_build_process_cpu_seconds": unprofiled_cpu_seconds,
                    "cprofile_wall_overhead_ratio": (
                        summary["build_wall_seconds"] / unprofiled_wall_seconds
                    ),
                    "numeric_storage_bytes": storage_bytes,
                    "expansion_shifts_hz": ";".join(str(value) for value in EXPANSION_SHIFTS_HZ),
                })

            for phase, result in (
                ("frequency", measure_reduced_frequency(model)),
                ("transient", measure_reduced_transient(model)),
            ):
                solver_rows.append({
                    "morphology": label,
                    "engine": "PRIMA",
                    "prima_order": order,
                    "replicate": replicate,
                    "phase": phase,
                    "solve_calls": result.get("solve_calls", ""),
                    "steps": result.get("steps", ""),
                    "wall_seconds": result["wall_seconds"],
                    "cpu_seconds": result["cpu_seconds"],
                    "seconds_per_operation": (
                        result["wall_seconds"] / result["solve_calls"]
                        if result.get("solve_calls") else result["seconds_per_step"]
                    ),
                    "peak_port_perturbation_v": result.get("peak_port_perturbation_v", ""),
                    "finite_check": result.get("finite_checksum", True),
                    "frequency_hz": ";".join(str(value) for value in FREQUENCIES_HZ) if phase == "frequency" else "",
                })

    _write_csv(output_dir / "build_phase_profile.csv", build_rows)
    _write_csv(output_dir / "solver_profile.csv", solver_rows)
    metadata = {
        "mode": "prima",
        "morphology": label,
        "swc_path": str(swc_path),
        "swc_records": len(morphology.nodes),
        "full_compartments": tree.n_compartments,
        "retained_port_swc_ids": list(node_ids),
        "retained_port_indices": list(ports),
        "retained_port_count": len(ports),
        "orders": list(ORDERS),
        "expansion_shifts_hz": list(EXPANSION_SHIFTS_HZ),
        "frequencies_hz": list(FREQUENCIES_HZ),
        "repeats": args.repeats,
        "dt_s": DT_S,
        "transient_steps": TRANSIENT_STEPS,
        "pulse_start_step": PULSE_START_STEP,
        "pulse_stop_step": PULSE_STOP_STEP,
        "pulse_current_a": PULSE_CURRENT_A,
        "runner_cpu_model": _runner_cpu_model(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "method": "cProfile self-time of the existing PRIMA implementation",
        "phase_interpretation": "named phase self_seconds exclude child calls; cumulative_seconds include nested NumPy/native work and overlap with the parent orchestrator; native_function_self is reported separately rather than assigned to a phase",
        "full_hines_is_separate_process": True,
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(
        f"mode=prima; morphology={label}; compartments={tree.n_compartments}; "
        f"orders={ORDERS}; build_rows={len(build_rows)}; solver_rows={len(solver_rows)}"
    )
    for order in ORDERS:
        group = [
            row for row in build_rows
            if row["prima_order"] == order and row["phase"] == "shifted_hines_solve"
        ]
        print(
            f"order={order}; median_build_wall_s="
            f"{statistics.median(row['build_wall_seconds'] for row in group):.6g}; "
            f"median_shift_solve_self_s="
            f"{statistics.median(row['self_seconds'] for row in group):.6g}"
        )


def run_hines_mode(args):
    label, swc_path, morphology, tree, ports, node_ids = prepare_morphology()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for replicate in range(1, args.repeats + 1):
        for phase, result in (
            ("frequency", measure_hines_frequency(tree, ports)),
            ("transient", measure_hines_transient(tree, ports)),
        ):
            rows.append({
                "morphology": label,
                "engine": "full_Hines",
                "prima_order": "",
                "replicate": replicate,
                "phase": phase,
                "solve_calls": result.get("solve_calls", ""),
                "steps": result.get("steps", ""),
                "wall_seconds": result["wall_seconds"],
                "cpu_seconds": result["cpu_seconds"],
                "seconds_per_operation": (
                    result["wall_seconds"] / result["solve_calls"]
                    if result.get("solve_calls") else result["seconds_per_step"]
                ),
                "peak_port_perturbation_v": result.get("peak_port_perturbation_v", ""),
                "finite_check": result.get("finite_checksum", True),
                "frequency_hz": ";".join(str(value) for value in FREQUENCIES_HZ) if phase == "frequency" else "",
            })
    _write_csv(output_dir / "solver_profile.csv", rows)
    metadata = {
        "mode": "full_hines",
        "morphology": label,
        "swc_path": str(swc_path),
        "swc_records": len(morphology.nodes),
        "full_compartments": tree.n_compartments,
        "retained_port_swc_ids": list(node_ids),
        "retained_port_indices": list(ports),
        "retained_port_count": len(ports),
        "frequencies_hz": list(FREQUENCIES_HZ),
        "repeats": args.repeats,
        "dt_s": DT_S,
        "transient_steps": TRANSIENT_STEPS,
        "pulse_start_step": PULSE_START_STEP,
        "pulse_stop_step": PULSE_STOP_STEP,
        "pulse_current_a": PULSE_CURRENT_A,
        "runner_cpu_model": _runner_cpu_model(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "method": "full CableTree Hines solver; independent process from PRIMA",
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(
        f"mode=full_hines; morphology={label}; compartments={tree.n_compartments}; "
        f"solver_rows={len(rows)}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("prima", "hines"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    args = parser.parse_args()
    if args.repeats < 2:
        parser.error("--repeats must be at least 2")
    # The NEURON reference builder reads this setting when the sections are made.
    os.environ.setdefault("NEURON_NOGUI", "1")
    if args.mode == "prima":
        run_prima_mode(args)
    else:
        run_hines_mode(args)


if __name__ == "__main__":
    main()
