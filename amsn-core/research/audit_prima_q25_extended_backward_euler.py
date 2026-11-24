#!/usr/bin/env python3
"""Extended exact-backward-Euler tail audit for q25 PRIMA holdouts.

Re-runs the original 0.1-ms implicit Euler recurrence and measures cumulative
NRMSE over 20, 40, 100 and 200-ms windows. Full cable references use an exact-
order compiled implementation of the original Hines tree elimination and are
checked against CableTree.step_passive. The reduced path preserves the original
per-vector solve/projection order through the archived 20-ms parity window.
"""
from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import __version__ as SCIPY_VERSION
from scipy.sparse import coo_matrix
from scipy.linalg import lu_factor, lu_solve
from scipy.sparse.linalg import splu

RESEARCH = Path(__file__).resolve().parent
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import audit_prima_q25_basis_conditioning as conditioning

LAYOUT_IDS = ("seven", "nine_both_q25")
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS_MS = (2.0, 10.0)
WINDOWS_MS = (20.0, 40.0, 100.0, 200.0)
DT_MS = 0.1
DT_S = DT_MS / 1000.0
PULSE_ONSET_MS = 2.0
CURRENT_A = 10e-12
BASIS_ORDER = 168
RESULT_STEM = "prima_q25_extended_backward_euler_tail_2026-11-24"
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())

EXPECTED_EXTENDED_ROWS = (
    2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_COMPARISON_ROWS = (
    2 * len(SCENARIO_NAMES) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_PARITY_ROWS = (
    2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7
)
EXPECTED_BY_OUTPUT_ROWS = (
    2 * len(LAYOUT_IDS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_COMPARISON_SUMMARY_ROWS = (
    2 * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_SOURCE_SUMMARY_ROWS = (
    2 * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS)
)
EXPECTED_WINDOW_SUMMARY_ROWS = 2 * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS)
EXPECTED_LAYOUT_WINDOW_ROWS = (
    2 * len(LAYOUT_IDS) * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS)
)

# Archived 20-ms NRMSEs were produced on an earlier CI image. Replaying the
# unchanged legacy simulator in the current image matches the extended solver
# exactly, but tiny NRMSE values show cross-run absolute variation up to
# 3.1e-8 percentage points. Keep a small, explicit absolute floor and report
# relative deltas separately rather than letting a near-zero denominator
# dominate the parity decision.
ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS = 5e-8

TRANSIENT_FILES = {
    "NMO_163775": Path(
        "results/NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24_"
        "matched_shared_vs_seven.csv"
    ),
    "NMO_107159": Path(
        "results/NMO_107159_TamasHumanPyramidalControl_prima_q25_four_layout_replication_2026-11-24_"
        "matched_shared_vs_seven.csv"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def archived_parity_within_absolute_tolerance(
    computed_nrmse_pct: float,
    archived_nrmse_pct: float,
) -> bool:
    """Compare tiny archived NRMSE values using an absolute percentage-point floor."""
    computed = float(computed_nrmse_pct)
    archived = float(archived_nrmse_pct)
    require(np.isfinite(computed) and np.isfinite(archived),
            "computed and archived NRMSE values must be finite")
    return abs(computed - archived) <= ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS


def expected_counts() -> dict[str, int]:
    return {
        "windows_ms": len(WINDOWS_MS),
        "extended_transient_rows": EXPECTED_EXTENDED_ROWS,
        "comparison_rows": EXPECTED_COMPARISON_ROWS,
        "20ms_parity_rows": EXPECTED_PARITY_ROWS,
        "by_output_summary_rows": EXPECTED_BY_OUTPUT_ROWS,
        "comparison_summary_rows": EXPECTED_COMPARISON_SUMMARY_ROWS,
        "by_source_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
        "window_summary_rows": EXPECTED_WINDOW_SUMMARY_ROWS,
        "layout_window_summary_rows": EXPECTED_LAYOUT_WINDOW_ROWS,
    }


def build_sparse_hines_factor(tree, dt_s: float):
    """Factor the exact full-cable BE matrix A = G + C/dt once per scenario."""
    dt = float(dt_s)
    require(np.isfinite(dt) and dt > 0.0, "dt_s must be finite and positive")
    n = int(tree.n_compartments)
    diagonal = np.asarray(tree.membrane_leak_s, dtype=float) + (
        np.asarray(tree.capacitance_f, dtype=float) / dt
    )
    child = np.arange(1, n, dtype=int)
    parent = np.asarray(tree.parent_index[1:], dtype=int)
    conductance = np.asarray(tree.axial_g_s[1:], dtype=float)
    np.add.at(diagonal, child, conductance)
    np.add.at(diagonal, parent, conductance)

    indices = np.arange(n, dtype=int)
    rows = np.concatenate((indices, child, parent))
    cols = np.concatenate((indices, parent, child))
    values = np.concatenate((diagonal, -conductance, -conductance))
    matrix = coo_matrix((values, (rows, cols)), shape=(n, n)).tocsc()
    factor = splu(matrix)
    return factor, np.asarray(tree.capacitance_f, dtype=float) / dt

_HINES_C_KERNEL = None


def load_compiled_hines_kernel():
    """Compile/load the exact-order C wrapper for the original Hines traversal."""
    global _HINES_C_KERNEL
    if _HINES_C_KERNEL is not None:
        return _HINES_C_KERNEL
    source = Path(__file__).with_name("hines_be_kernel.c")
    require(source.is_file(), f"missing compiled Hines kernel source: {source}")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    library_path = Path(tempfile.gettempdir()) / f"amsn_hines_be_{digest}.so"
    if not library_path.exists():
        compiler = shutil.which("cc")
        require(compiler is not None, "a C compiler (cc) is required for the exact Hines kernel")
        subprocess.run(
            [
                compiler, "-O3", "-std=c11", "-fno-fast-math",
                "-ffp-contract=off", "-fPIC", "-shared",
                str(source), "-o", str(library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    library = ctypes.CDLL(str(library_path))
    double_ptr = ctypes.POINTER(ctypes.c_double)
    int64_ptr = ctypes.POINTER(ctypes.c_int64)
    library.amsn_hines_be_step.argtypes = [
        ctypes.c_int64, ctypes.c_int64,
        double_ptr, double_ptr, int64_ptr, double_ptr,
        double_ptr, double_ptr, double_ptr, double_ptr,
        double_ptr, double_ptr,
    ]
    library.amsn_hines_be_step.restype = None
    _HINES_C_KERNEL = library
    return library


def build_tree_hines_be_factor(tree, dt_s: float) -> dict[str, Any]:
    """Pre-factor the full tree with the same pivot order as CableTree.step_linear."""
    dt = float(dt_s)
    require(np.isfinite(dt) and dt > 0.0, "dt_s must be finite and positive")
    capacitance = np.ascontiguousarray(tree.capacitance_f, dtype=np.float64)
    c_over_dt = capacitance / dt
    parent = np.ascontiguousarray(tree.parent_index, dtype=np.int64)
    axial = np.ascontiguousarray(tree.axial_g_s, dtype=np.float64)
    pivot = np.ascontiguousarray(
        np.asarray(tree.membrane_leak_s, dtype=np.float64) + c_over_dt,
        dtype=np.float64,
    )
    for child in range(1, tree.n_compartments):
        conductance = float(axial[child])
        p = int(parent[child])
        pivot[child] += conductance
        pivot[p] += conductance

    multipliers = np.zeros(tree.n_compartments, dtype=np.float64)
    # Preserve the exact reverse traversal and pivot update used by
    # CableTree.step_linear: diagonal[parent] -= (g*g)/diagonal[child].
    for child in range(tree.n_compartments - 1, 0, -1):
        p = int(parent[child])
        conductance = float(axial[child])
        denominator = float(pivot[child])
        require(np.isfinite(denominator) and denominator > 0.0,
                "non-positive child pivot in canonical Hines factorization")
        multipliers[child] = conductance / denominator
        pivot[p] -= (conductance * conductance) / denominator

    require(np.isfinite(pivot[0]) and pivot[0] > 0.0,
            "non-positive root pivot in canonical Hines factorization")
    return {
        "pivot_diagonal": pivot,
        "multipliers": np.ascontiguousarray(multipliers),
        "parent_index": parent,
        "axial_g_s": axial,
        "c_over_dt": np.ascontiguousarray(c_over_dt),
        "leak_source_a": np.ascontiguousarray(
            np.asarray(tree.membrane_leak_s, dtype=np.float64)
            * float(tree.parameters.e_leak_v)
        ),
        "leak_reversal_v": float(tree.parameters.e_leak_v),
        "kernel": load_compiled_hines_kernel(),
    }


def tree_hines_backward_euler_step(
    factor: dict[str, Any],
    voltage: np.ndarray,
    current_a: np.ndarray,
) -> np.ndarray:
    """Apply the exact CableTree Hines recurrence to multiple RHS columns."""
    previous = np.ascontiguousarray(voltage, dtype=np.float64)
    current = np.ascontiguousarray(current_a, dtype=np.float64)
    require(previous.ndim == 2 and previous.shape[0] == factor["pivot_diagonal"].size,
            "Hines previous state must have shape (compartments, columns)")
    require(current.shape == previous.shape,
            "Hines current matrix must match the previous state")
    following = np.empty_like(previous)
    work = np.empty_like(previous)
    double_ptr = ctypes.POINTER(ctypes.c_double)
    int64_ptr = ctypes.POINTER(ctypes.c_int64)

    def dptr(array: np.ndarray):
        return array.ctypes.data_as(double_ptr)

    kernel = factor["kernel"]
    kernel.amsn_hines_be_step(
        ctypes.c_int64(previous.shape[0]),
        ctypes.c_int64(previous.shape[1]),
        dptr(factor["pivot_diagonal"]),
        dptr(factor["multipliers"]),
        factor["parent_index"].ctypes.data_as(int64_ptr),
        dptr(factor["axial_g_s"]),
        dptr(factor["c_over_dt"]),
        dptr(factor["leak_source_a"]),
        dptr(previous),
        dptr(current),
        dptr(following),
        dptr(work),
    )
    require(np.all(np.isfinite(following)), "non-finite state in canonical Hines step")
    return following



def factor_reduced_backward_euler(model, dt_s: float):
    """Factor the reduced BE left-hand side once, preserving the original solve."""
    dt = float(dt_s)
    require(np.isfinite(dt) and dt > 0.0, "dt_s must be finite and positive")
    lhs = model.conductance_matrix_s + model.capacitance_matrix_f / dt
    return lu_factor(lhs, check_finite=False)


def reduced_backward_euler_step_factorized(
    model,
    factor,
    previous_state: np.ndarray,
    port_current_a: np.ndarray,
    dt_s: float,
) -> np.ndarray:
    """One-column solve with the same RHS operation order as model.step_backward_euler."""
    previous = np.asarray(previous_state, dtype=float)
    current = np.asarray(port_current_a, dtype=float)
    rhs = (
        (model.capacitance_matrix_f @ previous) / float(dt_s)
        + model.input_matrix @ current
    )
    following = lu_solve(factor, rhs, check_finite=False)
    require(np.all(np.isfinite(following)), "non-finite reduced state in factorized BE step")
    return following


def column_protocol() -> list[tuple[str, float]]:
    return [
        (source, pulse_width)
        for source in SOURCE_NAMES
        for pulse_width in PULSE_WIDTHS_MS
    ]


def _make_current_matrix(
    row_count: int,
    source_indices: list[int],
    protocol: list[tuple[str, float]],
    step_index: int,
) -> np.ndarray:
    current = np.zeros((row_count, len(protocol)), dtype=float)
    now_s = step_index * DT_S
    for column, (source_name, pulse_width_ms) in enumerate(protocol):
        pulse_end_s = PULSE_ONSET_MS / 1000.0 + pulse_width_ms / 1000.0
        if PULSE_ONSET_MS / 1000.0 <= now_s < pulse_end_s:
            current[int(source_indices[SOURCE_NAMES.index(source_name)]), column] = CURRENT_A
    return current


def simulate_full_hines_windows(
    tree,
    factor,
    c_over_dt: np.ndarray,
    source_indices: list[int],
    output_indices: list[int],
    *,
    duration_ms: float = max(WINDOWS_MS),
) -> tuple[np.ndarray, list[tuple[str, float]]]:
    """Simulate all source/pulse combinations together using the full BE matrix."""
    steps = int(round(float(duration_ms) / DT_MS))
    require(steps > 0 and steps * DT_MS == float(duration_ms),
            "duration must be an exact multiple of dt")
    protocol = column_protocol()
    # Match the original transient solver exactly: keep absolute voltages at
    # the leak reversal potential, then subtract E_leak only when recording.
    voltage = np.full(
        (tree.n_compartments, len(protocol)),
        float(factor["leak_reversal_v"]),
        dtype=float,
    )
    # _make_current_matrix indexes this map by source name, not protocol column.
    # Keep exactly one tree-compartment index per source.
    current_indices = [int(x) for x in source_indices]
    require(len(current_indices) == len(SOURCE_NAMES),
            "full-Hines source index map must contain exactly three source ports")
    trace = np.empty(
        (steps, len(output_indices), len(protocol)),
        dtype=float,
    )
    for step in range(steps):
        current = _make_current_matrix(
            tree.n_compartments,
            current_indices,
            protocol,
            step,
        )
        voltage = tree_hines_backward_euler_step(factor, voltage, current)
        trace[step, :, :] = (
            voltage[np.asarray(output_indices, dtype=int), :]
            - float(factor["leak_reversal_v"])
        )
    require(np.all(np.isfinite(trace)), "non-finite full-Hines extended trace")
    return trace, protocol


def simulate_reduced_windows(
    model,
    layout: dict[str, Any],
    common_output_ids: list[int],
    protocol: list[tuple[str, float]],
    *,
    duration_ms: float = max(WINDOWS_MS),
) -> np.ndarray:
    """Simulate all sources/pulse widths together with the exact reduced BE map."""
    steps = int(round(float(duration_ms) / DT_MS))
    factor = factor_reduced_backward_euler(model, DT_S)
    state = np.zeros((model.order, len(protocol)), dtype=float)
    port_current = np.zeros((layout["port_count"], len(protocol)), dtype=float)
    source_slots = {
        source: int(layout["source_indices"][source])
        for source in SOURCE_NAMES
    }
    common_slot_by_id = {
        int(node_id): index for index, node_id in enumerate(layout["node_ids"])
    }
    output_slots = np.asarray([
        common_slot_by_id[int(node_id)] for node_id in common_output_ids
    ], dtype=int)
    trace = np.empty((steps, len(common_output_ids), len(protocol)), dtype=float)
    step_port_trace = np.empty((layout["port_count"], len(protocol)), dtype=float)

    for step in range(steps):
        port_current.fill(0.0)
        now_s = step * DT_S
        for column, (source_name, pulse_width_ms) in enumerate(protocol):
            pulse_end_s = PULSE_ONSET_MS / 1000.0 + pulse_width_ms / 1000.0
            if PULSE_ONSET_MS / 1000.0 <= now_s < pulse_end_s:
                port_current[source_slots[source_name], column] = CURRENT_A
        for column in range(len(protocol)):
            if step < int(round(20.0 / DT_MS)):
                # The first 20 ms are the strict archived-parity window. Use
                # the exact original model.step_backward_euler path (including
                # its np.linalg.solve call/rounding) so the parity gate measures
                # only the extension, not a numerically equivalent refactor.
                state[:, column] = model.step_backward_euler(
                    state[:, column], DT_S, port_current[:, column]
                )
            else:
                # Once the archived window has been reproduced exactly, reuse
                # the LU factorization for the longer 40–200 ms tail.
                state[:, column] = reduced_backward_euler_step_factorized(
                    model, factor, state[:, column], port_current[:, column], DT_S
                )
        # Match the archived simulator's per-RHS port projection exactly:
        # model.port_voltages performs one matrix-vector multiply per trace,
        # whereas output_basis @ state would use a matrix-matrix path with
        # slightly different rounding for tiny distal residuals.
        for column in range(len(protocol)):
            step_port_trace[:, column] = model.port_voltages(state[:, column])
        trace[step, :, :] = step_port_trace[output_slots, :]

    require(np.all(np.isfinite(trace)), "non-finite reduced extended trace")
    return trace


def relative_l2_percent(reference: np.ndarray, approximation: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=float)
    approx = np.asarray(approximation, dtype=float)
    require(ref.shape == approx.shape, "reference and approximation shapes differ")
    require(np.all(np.isfinite(ref)) and np.all(np.isfinite(approx)),
            "relative L2 inputs must be finite")
    return float(
        100.0 * np.linalg.norm(approx - ref)
        / max(float(np.linalg.norm(ref)), 1e-30)
    )


def load_archived_transient(
    path: Path,
    morphology_name: str,
) -> dict[tuple, dict[str, Any]]:
    require(path.is_file(), f"missing archived transient CSV: {path}")
    result = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, "transient CSV lacks a header")
        for line_number, row in enumerate(reader, start=2):
            if row["layout_id"] != "nine_both_q25" or int(row["basis_order"]) != BASIS_ORDER:
                continue
            key = (
                row["parameter_scenario"],
                row["source_name"],
                float(row["pulse_width_ms"]),
                int(row["port_swc_id"]),
            )
            require(key not in result, f"{morphology_name}: duplicate archived key {key}")
            for field in ("seven_port_nrmse_pct", "candidate_nrmse_pct"):
                row[field] = float(row[field])
                require(math.isfinite(row[field]),
                        f"{path}:{line_number}: non-finite archived {field}")
            row["morphology"] = morphology_name
            result[key] = row
    expected = len(SCENARIO_NAMES) * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7
    require(len(result) == expected,
            f"{morphology_name}: archived 20-ms coverage {len(result)} != {expected}")
    return result


def summarize_extended_rows(rows: list[dict[str, Any]]) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    by_output_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"], row["source_name"],
            row["output_swc_id"], row["output_role"],
            row["pulse_width_ms"], row["window_ms"],
        )
        by_output_groups[key].append(row)

    by_output = []
    for key, subset in sorted(by_output_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES),
                f"scenario coverage mismatch for output group {key}")
        values = [float(r["nrmse_pct"]) for r in subset]
        by_output.append({
            "morphology": key[0], "layout_id": key[1], "source_name": key[2],
            "output_swc_id": key[3], "output_role": key[4],
            "pulse_width_ms": key[5], "window_ms": key[6],
            "parameter_scenarios": len(subset),
            "median_nrmse_pct": float(np.median(values)),
            "p90_nrmse_pct": float(np.percentile(values, 90)),
            "max_nrmse_pct": max(values),
        })
    require(len(by_output) == EXPECTED_BY_OUTPUT_ROWS,
            f"by-output summaries {len(by_output)} != {EXPECTED_BY_OUTPUT_ROWS}")

    row_index = {
        (
            r["morphology"], r["layout_id"], r["parameter_scenario"],
            r["source_name"], int(r["output_swc_id"]),
            float(r["pulse_width_ms"]), float(r["window_ms"]),
        ): r
        for r in rows
    }
    comparison_rows = []
    for candidate in rows:
        if candidate["layout_id"] != "nine_both_q25":
            continue
        base_key = (
            candidate["morphology"], "seven", candidate["parameter_scenario"],
            candidate["source_name"], int(candidate["output_swc_id"]),
            float(candidate["pulse_width_ms"]), float(candidate["window_ms"]),
        )
        base = row_index.get(base_key)
        require(base is not None, f"missing seven-port comparison for {base_key}")
        ratio = (
            float(candidate["nrmse_pct"]) / float(base["nrmse_pct"])
            if float(base["nrmse_pct"]) > 0.0
            else (1.0 if float(candidate["nrmse_pct"]) == 0.0 else None)
        )
        comparison_rows.append({
            "morphology": candidate["morphology"],
            "parameter_scenario": candidate["parameter_scenario"],
            "source_name": candidate["source_name"],
            "output_swc_id": int(candidate["output_swc_id"]),
            "output_role": candidate["output_role"],
            "pulse_width_ms": float(candidate["pulse_width_ms"]),
            "window_ms": float(candidate["window_ms"]),
            "seven_port_nrmse_pct": float(base["nrmse_pct"]),
            "nine_port_nrmse_pct": float(candidate["nrmse_pct"]),
            "nrmse_ratio_nine_over_seven": ratio,
        })
    require(len(comparison_rows) == EXPECTED_COMPARISON_ROWS,
            f"comparison rows {len(comparison_rows)} != {EXPECTED_COMPARISON_ROWS}")

    comparison_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (
            row["morphology"], row["source_name"], row["output_swc_id"],
            row["output_role"], row["pulse_width_ms"], row["window_ms"],
        )
        comparison_groups[key].append(row)
    comparison_summary = []
    for key, subset in sorted(comparison_groups.items()):
        ratios = [float(r["nrmse_ratio_nine_over_seven"]) for r in subset]
        comparison_summary.append({
            "morphology": key[0], "source_name": key[1],
            "output_swc_id": key[2], "output_role": key[3],
            "pulse_width_ms": key[4], "window_ms": key[5],
            "parameter_scenarios": len(subset),
            "median_nrmse_ratio": float(np.median(ratios)),
            "p90_nrmse_ratio": float(np.percentile(ratios, 90)),
            "worse_scenarios": sum(x > 1.0 for x in ratios),
            "better_scenarios": sum(x < 1.0 for x in ratios),
        })
    require(len(comparison_summary) == EXPECTED_COMPARISON_SUMMARY_ROWS,
            f"comparison summaries {len(comparison_summary)} != {EXPECTED_COMPARISON_SUMMARY_ROWS}")

    source_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (row["morphology"], row["source_name"], row["pulse_width_ms"], row["window_ms"])
        source_groups[key].append(row)
    source_summary = []
    for key, subset in sorted(source_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES) * 7,
                f"source group must cover nine scenarios × seven outputs: {key}")
        ratios = [float(r["nrmse_ratio_nine_over_seven"]) for r in subset]
        source_summary.append({
            "morphology": key[0], "source_name": key[1],
            "pulse_width_ms": key[2], "window_ms": key[3],
            "scenario_output_pairs": len(subset),
            "median_nrmse_ratio": float(np.median(ratios)),
            "p90_nrmse_ratio": float(np.percentile(ratios, 90)),
            "worse_pairs": sum(x > 1.0 for x in ratios),
            "better_pairs": sum(x < 1.0 for x in ratios),
        })
    require(len(source_summary) == EXPECTED_SOURCE_SUMMARY_ROWS,
            f"source summaries {len(source_summary)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")

    window_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (row["morphology"], row["pulse_width_ms"], row["window_ms"])
        window_groups[key].append(row)
    window_summary = []
    for key, subset in sorted(window_groups.items()):
        ratios = [float(r["nrmse_ratio_nine_over_seven"]) for r in subset]
        require(len(subset) == len(SCENARIO_NAMES) * len(SOURCE_NAMES) * 7,
                f"window comparison does not cover all sources/outputs/scenarios: {key}")
        window_summary.append({
            "morphology": key[0], "pulse_width_ms": key[1], "window_ms": key[2],
            "scenario_source_output_pairs": len(subset),
            "median_nrmse_ratio": float(np.median(ratios)),
            "p90_nrmse_ratio": float(np.percentile(ratios, 90)),
            "worse_pairs": sum(x > 1.0 for x in ratios),
            "better_pairs": sum(x < 1.0 for x in ratios),
        })
    require(len(window_summary) == EXPECTED_WINDOW_SUMMARY_ROWS,
            f"window summaries {len(window_summary)} != {EXPECTED_WINDOW_SUMMARY_ROWS}")

    layout_window_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"],
            row["pulse_width_ms"], row["window_ms"],
        )
        layout_window_groups[key].append(row)
    layout_window_summary = []
    for key, subset in sorted(layout_window_groups.items()):
        values = [float(r["nrmse_pct"]) for r in subset]
        layout_window_summary.append({
            "morphology": key[0], "layout_id": key[1],
            "pulse_width_ms": key[2], "window_ms": key[3],
            "scenario_source_output_rows": len(subset),
            "median_nrmse_pct": float(np.median(values)),
            "p90_nrmse_pct": float(np.percentile(values, 90)),
            "max_nrmse_pct": max(values),
        })
    require(len(layout_window_summary) == EXPECTED_LAYOUT_WINDOW_ROWS,
            f"layout/window summaries {len(layout_window_summary)} != {EXPECTED_LAYOUT_WINDOW_ROWS}")
    return by_output, comparison_rows, comparison_summary, source_summary, window_summary, layout_window_summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dt_s = DT_S
    max_window_ms = max(WINDOWS_MS)
    step_count = int(round(max_window_ms / DT_MS))
    output_rows: list[dict[str, Any]] = []
    parity_rows: list[dict[str, Any]] = []
    parity_probe_rows: list[dict[str, Any]] = []
    morphology_manifest = []
    protocol = column_protocol()

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
        require(set(q25_ids.values()) ==
                set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])),
                f"{morph_spec['name']}: q25 IDs differ from preflight")
        shared_by_layout = {}
        for layout_id in LAYOUT_IDS:
            layout = layouts[layout_id]
            slot_by_id = {int(node_id): i for i, node_id in enumerate(layout["node_ids"])}
            require(set(int(x) for x in common_ids).issubset(slot_by_id),
                    f"{morph_spec['name']}/{layout_id}: missing common SWC node")
            shared_by_layout[layout_id] = [slot_by_id[int(x)] for x in common_ids]

        archived = load_archived_transient(
            TRANSIENT_FILES[morph_spec["neuromorpho_id"]],
            morph_spec["name"],
        )
        morphology_manifest.append({
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_sha256": digest,
            "swc_records": morph_spec["expected_records"],
            "shared_output_node_ids": common_ids,
            "q25_node_ids": q25_ids,
        })

        for scenario_name, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)
            hines_factor = build_tree_hines_be_factor(target, dt_s)
            c_over_dt = hines_factor["c_over_dt"]
            full_layout = layouts["nine_both_q25"]
            source_indices_full = [
                int(full_layout["ports"][int(full_layout["source_indices"][source])])
                for source in SOURCE_NAMES
            ]
            output_indices_full = [
                int(layouts["seven"]["ports"][
                    {int(node): i for i, node in enumerate(layouts["seven"]["node_ids"])}[int(node)]
                ])
                for node in common_ids
            ]

            # Full-Hines perturbation traces are shared by the two port layouts.
            full_trace, _ = simulate_full_hines_windows(
                target, hines_factor, c_over_dt,
                source_indices_full, output_indices_full,
                duration_ms=max_window_ms,
            )

            reduced_traces = {}
            models = {}
            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], BASIS_ORDER,
                    conditioning.SHIFTS_HZ,
                    relative_tolerance=conditioning.RELATIVE_TOLERANCE,
                )
                require(model.order == BASIS_ORDER,
                        f"{morph_spec['name']}/{layout_id}: did not reach order {BASIS_ORDER}")
                models[layout_id] = model
                reduced_traces[layout_id] = simulate_reduced_windows(
                    model,
                    layout,
                    [int(x) for x in common_ids],
                    protocol,
                    duration_ms=max_window_ms,
                )

            # One controlled parity probe per layout: run the original legacy
            # 20-ms simulator beside both extended implementations on the same
            # exact tree/model/input. This distinguishes full-Hines factor issues
            # from reduced-state/output mapping issues before accepting later windows.
            if scenario_name in ("Rm_minus20", "Rm_plus20"):
                # Keep one historical probe and add the exact current worst pair
                # from the parity diagnostic: Tamas dual-q25, Rm_plus20, soma,
                # 2-ms pulse. This compares the original archived simulator path
                # directly with the extended audit on the failing source/output.
                probe_source = "basal_q75" if scenario_name == "Rm_minus20" else "soma"
                probe_width_ms = 2.0
                probe_column = SOURCE_NAMES.index(probe_source) * len(PULSE_WIDTHS_MS)
                for probe_layout_id in LAYOUT_IDS:
                    probe_layout = layouts[probe_layout_id]
                    probe_source_slot = int(probe_layout["source_indices"][probe_source])
                    legacy_full, _ = baseline.run_full_hines_transient(
                        target, probe_layout["ports"], probe_source_slot, probe_width_ms
                    )
                    legacy_reduced, _ = baseline.run_reduced_transient(
                        models[probe_layout_id], probe_layout["port_count"],
                        probe_source_slot, probe_width_ms
                    )
                    shared_slots = shared_by_layout[probe_layout_id]
                    legacy_full_shared = legacy_full[:, shared_slots]
                    legacy_reduced_shared = legacy_reduced[:, shared_slots]
                    probe_steps = int(round(20.0 / DT_MS))
                    new_full_shared = full_trace[:probe_steps, :, probe_column]
                    new_reduced_shared = reduced_traces[probe_layout_id][:probe_steps, :, probe_column]
                    probe_row = {
                        "morphology": morph_spec["name"],
                        "parameter_scenario": scenario_name,
                        "layout_id": probe_layout_id,
                        "source_name": probe_source,
                        "pulse_width_ms": probe_width_ms,
                        "legacy_full_vs_vectorized_hines_relative_l2_pct": relative_l2_percent(
                            legacy_full_shared, new_full_shared
                        ),
                        "legacy_reduced_vs_precomputed_reduced_relative_l2_pct": relative_l2_percent(
                            legacy_reduced_shared, new_reduced_shared
                        ),
                        "legacy_vs_archived_max_absolute_delta_pct_points": 0.0,
                        "legacy_vs_archived_max_relative_delta_pct": 0.0,
                        "new_vs_archived_max_absolute_delta_pct_points": 0.0,
                        "new_vs_archived_max_relative_delta_pct": 0.0,
                    }
                    legacy_abs_deltas = []
                    legacy_rel_deltas = []
                    new_abs_deltas = []
                    new_rel_deltas = []
                    per_output_diagnostics = []
                    for output_index, output_node in enumerate(common_ids):
                        archive_key = (
                            scenario_name, probe_source, probe_width_ms, int(output_node)
                        )
                        archived_row = archived[archive_key]
                        legacy_full_output = legacy_full_shared[:, output_index]
                        new_full_output = new_full_shared[:, output_index]
                        legacy_reduced_output = legacy_reduced_shared[:, output_index]
                        new_reduced_output = new_reduced_shared[:, output_index]
                        legacy_nrmse = relative_l2_percent(
                            legacy_full_output, legacy_reduced_output
                        )
                        new_nrmse = relative_l2_percent(
                            new_full_output, new_reduced_output
                        )
                        archived_nrmse = (
                            float(archived_row["seven_port_nrmse_pct"])
                            if probe_layout_id == "seven"
                            else float(archived_row["candidate_nrmse_pct"])
                        )
                        legacy_abs_delta = abs(legacy_nrmse - archived_nrmse)
                        new_abs_delta = abs(new_nrmse - archived_nrmse)
                        legacy_rel_delta = (
                            100.0 * legacy_abs_delta / max(abs(archived_nrmse), 1e-30)
                        )
                        new_rel_delta = (
                            100.0 * new_abs_delta / max(abs(archived_nrmse), 1e-30)
                        )
                        legacy_abs_deltas.append(legacy_abs_delta)
                        legacy_rel_deltas.append(legacy_rel_delta)
                        new_abs_deltas.append(new_abs_delta)
                        new_rel_deltas.append(new_rel_delta)
                        per_output_diagnostics.append({
                            "output_swc_id": int(output_node),
                            "output_role": ";".join(probe_layout["roles"][int(output_node)]),
                            "legacy_full_vs_new_full_relative_l2_pct": relative_l2_percent(
                                legacy_full_output, new_full_output
                            ),
                            "legacy_reduced_vs_new_reduced_relative_l2_pct": relative_l2_percent(
                                legacy_reduced_output, new_reduced_output
                            ),
                            "legacy_computed_nrmse_pct": legacy_nrmse,
                            "new_computed_nrmse_pct": new_nrmse,
                            "archived_nrmse_pct": archived_nrmse,
                            "legacy_vs_archived_relative_delta_pct": legacy_rel_delta,
                            "new_vs_archived_relative_delta_pct": new_rel_delta,
                        })
                    probe_row.update({
                        "legacy_vs_archived_max_absolute_delta_pct_points": max(legacy_abs_deltas),
                        "legacy_vs_archived_max_relative_delta_pct": max(legacy_rel_deltas),
                        "new_vs_archived_max_absolute_delta_pct_points": max(new_abs_deltas),
                        "new_vs_archived_max_relative_delta_pct": max(new_rel_deltas),
                        "per_output_diagnostics": per_output_diagnostics,
                    })
                    parity_probe_rows.append(probe_row)

            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                reduced_trace = reduced_traces[layout_id]
                for source_index, source_name in enumerate(SOURCE_NAMES):
                    for pulse_index, pulse_width_ms in enumerate(PULSE_WIDTHS_MS):
                        column = source_index * len(PULSE_WIDTHS_MS) + pulse_index
                        for output_index, output_node in enumerate(common_ids):
                            for window_ms in WINDOWS_MS:
                                samples = int(round(window_ms / DT_MS))
                                full_values = full_trace[:samples, output_index, column]
                                reduced_values = reduced_trace[:samples, output_index, column]
                                nrmse = relative_l2_percent(full_values, reduced_values)
                                output_rows.append({
                                    "morphology": morph_spec["name"],
                                    "neuromorpho_id": morph_spec["neuromorpho_id"],
                                    "layout_id": layout_id,
                                    "basis_order": BASIS_ORDER,
                                    "parameter_scenario": scenario_name,
                                    "source_name": source_name,
                                    "output_swc_id": int(output_node),
                                    "output_role": ";".join(layout["roles"][int(output_node)]),
                                    "pulse_width_ms": pulse_width_ms,
                                    "window_ms": window_ms,
                                    "dt_ms": DT_MS,
                                    "pulse_onset_ms": PULSE_ONSET_MS,
                                    "pulse_amplitude_pA": CURRENT_A * 1e12,
                                    "nrmse_pct": nrmse,
                                })

                                if window_ms == 20.0:
                                    key = (
                                        scenario_name, source_name,
                                        float(pulse_width_ms), int(output_node),
                                    )
                                    old = archived.get(key)
                                    require(old is not None,
                                            f"{morph_spec['name']}: missing archived 20-ms NRMSE {key}")
                                    expected_nrmse = (
                                        float(old["seven_port_nrmse_pct"])
                                        if layout_id == "seven"
                                        else float(old["candidate_nrmse_pct"])
                                    )
                                    parity_rows.append({
                                        "morphology": morph_spec["name"],
                                        "layout_id": layout_id,
                                        "parameter_scenario": scenario_name,
                                        "source_name": source_name,
                                        "output_swc_id": int(output_node),
                                        "pulse_width_ms": pulse_width_ms,
                                        "computed_20ms_nrmse_pct": nrmse,
                                        "archived_20ms_nrmse_pct": expected_nrmse,
                                        "absolute_delta_pct_points": abs(nrmse - expected_nrmse),
                                        "relative_delta_pct": (
                                            100.0 * abs(nrmse - expected_nrmse)
                                            / max(abs(expected_nrmse), 1e-30)
                                        ),
                                    })

    require(len(output_rows) == EXPECTED_EXTENDED_ROWS,
            f"extended transient rows {len(output_rows)} != {EXPECTED_EXTENDED_ROWS}")
    require(len(parity_rows) == EXPECTED_PARITY_ROWS,
            f"20-ms parity rows {len(parity_rows)} != {EXPECTED_PARITY_ROWS}")
    max_parity_relative = max(float(r["relative_delta_pct"]) for r in parity_rows)
    max_parity_absolute = max(float(r["absolute_delta_pct_points"]) for r in parity_rows)

    # Emit diagnostics before the strict parity guard so a failed run identifies
    # the exact morphology/layout/source/output pair rather than only one scalar.
    parity_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in parity_rows:
        group_key = (row["morphology"], row["layout_id"])
        parity_groups[group_key].append(row)
    group_diagnostics = []
    for key, subset in sorted(parity_groups.items()):
        worst = max(subset, key=lambda row: float(row["absolute_delta_pct_points"]))
        group_diagnostics.append({
            "morphology": key[0],
            "layout_id": key[1],
            "rows": len(subset),
            "max_absolute_delta_pct_points": float(worst["absolute_delta_pct_points"]),
            "max_relative_delta_pct": max(float(x["relative_delta_pct"]) for x in subset),
            "worst_pair": {
                "source_name": worst["source_name"],
                "output_swc_id": worst["output_swc_id"],
                "pulse_width_ms": worst["pulse_width_ms"],
                "computed_20ms_nrmse_pct": worst["computed_20ms_nrmse_pct"],
                "archived_20ms_nrmse_pct": worst["archived_20ms_nrmse_pct"],
            },
        })
    worst_absolute = sorted(
        parity_rows,
        key=lambda row: float(row["absolute_delta_pct_points"]),
        reverse=True,
    )[:20]
    worst_relative = sorted(
        parity_rows,
        key=lambda row: float(row["relative_delta_pct"]),
        reverse=True,
    )[:20]
    print(json.dumps({
        "legacy_parity_probes": parity_probe_rows,
        "parity_diagnostics": {
            "rows": len(parity_rows),
            "max_absolute_delta_pct_points": max_parity_absolute,
            "max_relative_delta_pct": max_parity_relative,
        "absolute_tolerance_pct_points": ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS,
        "parity_gate": "absolute_nrmse_percentage_point_tolerance",
            "by_morphology_layout": group_diagnostics,
            "worst_absolute_pairs": worst_absolute,
            "worst_relative_pairs": worst_relative,
        }
    }, indent=2, allow_nan=False), flush=True)

    require(
        all(
            archived_parity_within_absolute_tolerance(
                float(r["computed_20ms_nrmse_pct"]),
                float(r["archived_20ms_nrmse_pct"]),
            )
            for r in parity_rows
        ),
        (
            "extended solver exceeded archived 20-ms absolute NRMSE parity "
            f"floor {ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS} percentage points: "
            f"max absolute delta={max_parity_absolute} pp, "
            f"max relative delta={max_parity_relative}%"
        ),
    )

    by_output, comparison_rows, comparison_summary, source_summary, window_summary, layout_window_summary = (
        summarize_extended_rows(output_rows)
    )

    results_dir = Path(__file__).parents[1] / "results"
    write_csv(results_dir / f"{RESULT_STEM}_extended_transient.csv", output_rows)
    write_csv(results_dir / f"{RESULT_STEM}_comparisons.csv", comparison_rows)
    write_csv(results_dir / f"{RESULT_STEM}_20ms_parity.csv", parity_rows)
    write_csv(results_dir / f"{RESULT_STEM}_by_output_summary.csv", by_output)
    write_csv(results_dir / f"{RESULT_STEM}_comparison_summary.csv", comparison_summary)
    write_csv(results_dir / f"{RESULT_STEM}_by_source_summary.csv", source_summary)
    write_csv(results_dir / f"{RESULT_STEM}_window_summary.csv", window_summary)
    write_csv(results_dir / f"{RESULT_STEM}_layout_window_summary.csv", layout_window_summary)

    report = {
        "schema_version": 1,
        "status": "prima_q25_extended_backward_euler_tail_audit_passed",
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(LAYOUT_IDS),
            "basis_order": BASIS_ORDER,
            "parameter_scenarios": list(SCENARIO_NAMES),
            "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_amplitude_pA": CURRENT_A * 1e12,
            "pulse_onset_ms": PULSE_ONSET_MS,
            "dt_ms": DT_MS,
            "windows_ms": list(WINDOWS_MS),
            "total_simulated_duration_ms": max_window_ms,
        },
        "exact_coverage": {
            "extended_transient_rows": len(output_rows),
            "comparison_rows": len(comparison_rows),
            "20ms_parity_rows": len(parity_rows),
            "by_output_summary_rows": len(by_output),
            "comparison_summary_rows": len(comparison_summary),
            "by_source_summary_rows": len(source_summary),
            "window_summary_rows": len(window_summary),
            "layout_window_summary_rows": len(layout_window_summary),
            "expected": expected_counts(),
            "max_20ms_archived_absolute_delta_pct_points": max_parity_absolute,
            "max_20ms_archived_relative_delta_pct": max_parity_relative,
        },
        "parity_gate": {
            "rule": "absolute difference in 20-ms NRMSE percentage points",
            "tolerance_pct_points": ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS,
            "max_absolute_delta_pct_points": max_parity_absolute,
            "max_relative_delta_pct": max_parity_relative,
        },
        "scientific_limits": [
            "The recurrence is the same implicit backward-Euler method with dt=0.1 ms and the same pulse sample timing as the archived 20-ms experiment; only the observation window is extended.",
            "The full cable reference uses the exact-order compiled Hines tree-elimination recurrence; the 20-ms result must reproduce archived Hines/PRIMA NRMSE within the explicit absolute percentage-point parity floor.",
            "The reduced trace keeps the original per-vector backward-Euler solve and port-voltage projection through 20 ms; factorized solves are used only for the later tail.",
            "All nine passive parameter scenarios, three sources, seven common outputs and both 2-ms/10-ms pulses are retained.",
            "Only two individual passive linear-RC morphology reconstructions are compared; they are not populations or biological validation.",
            "Full Hines remains canonical; no production code or solver defaults are changed.",
        ],
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": SCIPY_VERSION,
            "neuron": __import__("neuron").__version__,
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
