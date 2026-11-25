#!/usr/bin/env python3
"""Exact finite-window periodic-transfer / terminal-boundary decomposition for passive backward-Euler PRIMA models.

Convention:
  u[n] is held constant over [n*dt, (n+1)*dt).
  x[n] is the state at the end of that interval.
  (G + C/dt)x[n] - (C/dt)x[n-1] = B u[n].

The discrete transfer is H_BE(exp(j*Omega)) =
  L (G + (1-exp(-j*Omega))*C/dt)^(-1) B.

For a finite record beginning at rest, its DFT is not just H_BE*U:
  (G + (1-exp(-j*Omega))*C/dt) X
      = B U - (C/dt)x[N-1].
The terminal-state term is calculated and checked against the actual output
DFT. No production solver or defaults are modified.
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
from types import SimpleNamespace

import replay_nmo03524_prima_7v9port as jacobs_replay
import replay_nmo162186_prima_7v9port as allen_replay


def _build_external_four_layouts(module, morphology, reader, sections, base_tree):
    raw_layouts, common_ids, q25_extra_ids = module.build_port_layouts(
        morphology, reader, sections, base_tree
    )
    q25_ids = {}
    for node_id, roles in raw_layouts[9]["roles"].items():
        for role in roles:
            if role in ("basal_q25", "apical_q25"):
                if role in q25_ids:
                    raise ValueError(f"duplicate {role} role in external morphology")
                q25_ids[role] = int(node_id)
    if set(q25_ids) != {"basal_q25", "apical_q25"}:
        raise ValueError(f"external morphology q25 roles are incomplete: {q25_ids}")
    if set(q25_extra_ids) != set(q25_ids.values()):
        raise ValueError("external q25 role IDs differ from the mapper's extra-node set")
    return {
        "seven": raw_layouts[7],
        "nine_both_q25": raw_layouts[9],
    }, list(common_ids), q25_ids


def _external_module_adapter(replay_module):
    # Match the interface expected by the two-morphology conditioning runner.
    # The held-out replay modules expose these objects directly rather than
    # through a nested "baseline" module, so construct a narrow adapter.
    baseline = SimpleNamespace(
        reference=replay_module.reference,
        SWCMorphology=replay_module.SWCMorphology,
        parameter_cases=replay_module.parameter_cases,
        PassiveParameters=replay_module.PassiveParameters,
        CableTree=replay_module.CableTree,
        prima_reduce_passive_cable_multishift=(
            replay_module.prima_reduce_passive_cable_multishift
        ),
    )
    return SimpleNamespace(
        baseline=baseline,
        SWC=replay_module.SWC,
        build_four_layouts=lambda morphology, reader, sections, base_tree:
            _build_external_four_layouts(
                replay_module, morphology, reader, sections, base_tree
            ),
    )


JACOBS_ADAPTER = _external_module_adapter(jacobs_replay)
ALLEN_ADAPTER = _external_module_adapter(allen_replay)

MORPHOLOGIES = tuple(conditioning.MORPHOLOGIES) + (
    {
        "name": "NMO_03524_JacobsControl",
        "neuromorpho_id": "NMO_03524",
        "module": JACOBS_ADAPTER,
        "preflight": Path(
            "results/prima_q25_cross_morphology_boundary_preflight_2026-11-25_holdouts/"
            "NMO_03524_JacobsControl.json"
        ),
        "expected_sha256": jacobs_replay.EXPECTED_SWC_SHA256,
        "expected_records": jacobs_replay.EXPECTED_SWC_RECORDS,
    },
    {
        "name": "NMO_162186_AllenL23",
        "neuromorpho_id": "NMO_162186",
        "module": ALLEN_ADAPTER,
        "preflight": Path(
            "results/prima_q25_cross_morphology_boundary_preflight_2026-11-25_holdouts/"
            "NMO_162186_AllenL23.json"
        ),
        "expected_sha256": allen_replay.EXPECTED_SWC_SHA256,
        "expected_records": allen_replay.EXPECTED_SWC_RECORDS,
    },
)

MORPHOLOGY_COUNT = len(MORPHOLOGIES)

SOURCE_NAMES = tail.SOURCE_NAMES
LAYOUT_IDS = tail.LAYOUT_IDS
PULSE_WIDTHS_MS = tail.PULSE_WIDTHS_MS
WINDOWS_MS = (20.0, 40.0)
DT_MS = 0.00625
DT_S = DT_MS / 1000.0
# Keep helper-module pulse sampling on the exact same dt.
tail.DT_MS = DT_MS
tail.DT_S = DT_S
BASIS_ORDER = tail.BASIS_ORDER
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())
MAX_FREQUENCY_HZ = 1.0 / (2.0 * DT_S)
MASTER_FREQUENCY_STEP_HZ = 25.0
MASTER_FREQUENCIES_HZ = np.arange(
    0.0, MAX_FREQUENCY_HZ + 0.5 * MASTER_FREQUENCY_STEP_HZ,
    MASTER_FREQUENCY_STEP_HZ, dtype=np.float64,
)
RESULT_STEM = "prima_q25_four_morphology_boundary_decomposition_2026-11-25"
FINITE_IDENTITY_RELATIVE_TOLERANCE = 2e-8

EXPECTED_FREQUENCY_ROWS = (
    MORPHOLOGY_COUNT * len(LAYOUT_IDS) * len(SOURCE_NAMES) * 7 * len(MASTER_FREQUENCIES_HZ)
)
EXPECTED_CASE_METRIC_ROWS = (
    MORPHOLOGY_COUNT * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_COMPARISON_ROWS = (
    MORPHOLOGY_COUNT * len(SCENARIO_NAMES) * len(SOURCE_NAMES)
    * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
)
EXPECTED_SOURCE_SUMMARY_ROWS = (
    MORPHOLOGY_COUNT * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS)
)
EXPECTED_MORPH_WINDOW_SUMMARY_ROWS = MORPHOLOGY_COUNT * len(WINDOWS_MS)
EXPECTED_IDENTITY_ROWS = (
    MORPHOLOGY_COUNT * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(WINDOWS_MS)
    * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS)
)


def array_sha256(values: np.ndarray) -> str:
    """Hash an array after canonical float64 little-endian normalization."""
    array = np.ascontiguousarray(np.asarray(values, dtype="<f8"))
    digest = hashlib.sha256()
    digest.update(json.dumps({"shape": array.shape, "dtype": "<f8"}).encode("utf-8"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def numerical_runtime_diagnostics() -> dict[str, Any]:
    """Capture BLAS/thread settings used by this finite-window decomposition."""
    import contextlib
    import io
    import os
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        np.show_config()
    try:
        from threadpoolctl import threadpool_info
        pools = threadpool_info()
    except Exception as exc:
        pools = [{"diagnostic_error": f"{type(exc).__name__}: {exc}"}]
    names = (
        "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
        "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
        "PYTHONHASHSEED",
    )
    return {
        "thread_environment": {name: os.environ.get(name) for name in names},
        "threadpools": pools,
        "numpy_build_configuration": output.getvalue(),
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "master_frequency_points": int(MASTER_FREQUENCIES_HZ.size),
        "frequency_summary_rows": EXPECTED_FREQUENCY_ROWS,
        "case_metric_rows": EXPECTED_CASE_METRIC_ROWS,
        "nine_seven_comparison_rows": EXPECTED_COMPARISON_ROWS,
        "source_window_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
        "morphology_window_summary_rows": EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        "finite_dft_identity_rows": EXPECTED_IDENTITY_ROWS,
    }


def backward_euler_s_values(
    frequencies_hz: np.ndarray, dt_s: float,
) -> np.ndarray:
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    require(frequencies.ndim == 1 and np.all(np.isfinite(frequencies)),
            "frequencies must be a finite vector")
    require(np.isfinite(dt_s) and dt_s > 0.0, "dt_s must be finite and positive")
    omega_dt = 2.0 * np.pi * frequencies * float(dt_s)
    return (1.0 - np.exp(-1j * omega_dt)) / float(dt_s)


def zoh_frequency_factor(frequencies_hz: np.ndarray, dt_s: float) -> np.ndarray:
    """Fourier factor for samples held over [n*dt, (n+1)*dt)."""
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    return (
        float(dt_s)
        * np.sinc(frequencies * float(dt_s))
        * np.exp(-1j * np.pi * frequencies * float(dt_s))
    )


def one_sided_dft_weights(sample_count: int) -> np.ndarray:
    n = int(sample_count)
    require(n >= 2 and n % 2 == 0, "sample count must be positive and even")
    weights = np.full(n // 2 + 1, 2.0, dtype=np.float64)
    weights[0] = 1.0
    weights[-1] = 1.0
    return weights


def finite_window_frequency_indices(window_ms: float) -> tuple[np.ndarray, np.ndarray]:
    require(window_ms in WINDOWS_MS, f"unsupported observation window {window_ms}")
    sample_count = int(round(float(window_ms) / DT_MS))
    frequencies = np.fft.rfftfreq(sample_count, d=DT_S)
    indices = np.rint(frequencies / MASTER_FREQUENCY_STEP_HZ).astype(np.int64)
    require(
        np.allclose(
            MASTER_FREQUENCIES_HZ[indices], frequencies,
            rtol=0.0, atol=1e-10,
        ),
        f"{window_ms}-ms DFT bins are not covered by the master grid",
    )
    require(frequencies[-1] == MAX_FREQUENCY_HZ,
            "finite-window DFT does not reach the declared Nyquist frequency")
    return frequencies, indices


def build_sampled_protocol(
    sample_count: int,
) -> tuple[list[tuple[str, float]], np.ndarray]:
    """Return six current sequences using the tail audit's sample-edge rule."""
    n = int(sample_count)
    protocol = tail.column_protocol()
    current = np.zeros((n, len(protocol)), dtype=np.float64)
    onset = int(round(tail.PULSE_ONSET_MS / DT_MS))
    for column, (source_name, pulse_width_ms) in enumerate(protocol):
        del source_name  # source identity determines the transfer column, not this waveform
        stop = int(round((tail.PULSE_ONSET_MS + pulse_width_ms) / DT_MS))
        require(0 <= onset < stop <= n,
                "pulse samples must fit entirely inside every observation window")
        current[onset:stop, column] = tail.CURRENT_A
    return protocol, current


def weighted_transfer_error(
    full_transfer: np.ndarray,
    model_transfer: np.ndarray,
    input_dft: np.ndarray,
    frequencies_hz: np.ndarray,
    *,
    continuous_zoh_input: bool,
) -> tuple[float, float, float]:
    """Weighted relative transfer error for one output/source/pulse.

    For the discrete metric, input_dft is the exact DFT of the sample sequence.
    For the continuous-AC comparator, multiply by the exact ZOH Fourier factor.
    """
    full = np.asarray(full_transfer, dtype=np.complex128)
    model = np.asarray(model_transfer, dtype=np.complex128)
    spectrum = np.asarray(input_dft, dtype=np.complex128)
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    require(full.shape == model.shape == spectrum.shape == frequencies.shape,
            "transfer, input and frequency vectors must have identical shapes")
    weights = one_sided_dft_weights(2 * (frequencies.size - 1))
    input_power = np.square(np.abs(spectrum))
    if continuous_zoh_input:
        input_power *= np.square(np.abs(zoh_frequency_factor(frequencies, DT_S)))
    combined = weights * input_power
    error_energy = float(np.sum(combined * np.square(np.abs(model - full))))
    reference_energy = float(np.sum(combined * np.square(np.abs(full))))
    require(np.isfinite(error_energy) and np.isfinite(reference_energy),
            "non-finite weighted transfer energy")
    require(reference_energy > 0.0, "reference transfer energy must be positive")
    relative_pct = 100.0 * math.sqrt(error_energy / reference_energy)
    return relative_pct, math.sqrt(error_energy), math.sqrt(reference_energy)


def solve_full_hines_s_response(
    tree,
    s_values_per_s: np.ndarray,
    rhs_base: np.ndarray,
    output_indices: list[int],
    *,
    chunk_size: int = 50,
) -> np.ndarray:
    """Solve (G+s*C)X=RHS for many complex shifts using exact tree elimination.

    Returns shape (frequency, output, RHS-column). The reverse elimination and
    forward substitution preserve the cable tree traversal used by Hines.
    """
    shifts = np.asarray(s_values_per_s, dtype=np.complex128)
    rhs0 = np.asarray(rhs_base, dtype=np.complex128)
    outputs = np.asarray(output_indices, dtype=np.int64)
    require(shifts.ndim == 1 and shifts.size >= 1, "s grid must be a non-empty vector")
    require(rhs0.ndim == 2 and rhs0.shape[0] == tree.n_compartments,
            "Hines RHS must have shape (compartments, columns)")
    require(outputs.ndim == 1 and outputs.size >= 1, "output indices must be non-empty")
    require(np.all((outputs >= 0) & (outputs < tree.n_compartments)),
            "Hines output index out of range")
    require(chunk_size > 0, "chunk size must be positive")

    n = int(tree.n_compartments)
    response = np.empty(
        (shifts.size, outputs.size, rhs0.shape[1]), dtype=np.complex128
    )
    capacitance = np.asarray(tree.capacitance_f, dtype=np.float64)
    leak = np.asarray(tree.membrane_leak_s, dtype=np.float64)
    parent_index = np.asarray(tree.parent_index, dtype=np.int64)
    axial = np.asarray(tree.axial_g_s, dtype=np.float64)

    for start in range(0, shifts.size, chunk_size):
        stop = min(start + chunk_size, shifts.size)
        local_s = shifts[start:stop]
        diagonal = leak[:, None].astype(np.complex128) + (
            capacitance[:, None] * local_s[None, :]
        )
        rhs = np.broadcast_to(
            rhs0[:, None, :], (n, stop - start, rhs0.shape[1])
        ).copy()
        for child in range(1, n):
            p = int(parent_index[child])
            g = float(axial[child])
            diagonal[child, :] += g
            diagonal[p, :] += g
        for child in range(n - 1, 0, -1):
            p = int(parent_index[child])
            g = float(axial[child])
            pivot = diagonal[child, :]
            require(np.all(np.isfinite(pivot)) and np.all(np.abs(pivot) > 0.0),
                    "singular pivot in discrete Hines frequency solve")
            diagonal[p, :] -= (g * g) / pivot
            rhs[p, :, :] += (g / pivot)[:, None] * rhs[child, :, :]
        root = diagonal[0, :]
        require(np.all(np.isfinite(root)) and np.all(np.abs(root) > 0.0),
                "singular root in discrete Hines frequency solve")
        voltage = np.empty_like(rhs)
        voltage[0, :, :] = rhs[0, :, :] / root[:, None]
        for child in range(1, n):
            p = int(parent_index[child])
            g = float(axial[child])
            voltage[child, :, :] = (
                rhs[child, :, :] + g * voltage[p, :, :]
            ) / diagonal[child, :, None]
        response[start:stop, :, :] = np.transpose(
            voltage[outputs, :, :], (1, 0, 2)
        )
    require(np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag)),
            "non-finite full-Hines complex response")
    return response


def solve_reduced_s_response(
    model,
    s_values_per_s: np.ndarray,
    rhs_base: np.ndarray,
    output_slots: list[int],
    *,
    chunk_size: int = 50,
) -> np.ndarray:
    """Solve the congruence-projected reduced system for complex shifts."""
    shifts = np.asarray(s_values_per_s, dtype=np.complex128)
    rhs0 = np.asarray(rhs_base, dtype=np.complex128)
    outputs = np.asarray(output_slots, dtype=np.int64)
    require(rhs0.ndim == 2 and rhs0.shape[0] == model.order,
            "reduced RHS must have shape (order, columns)")
    require(outputs.ndim == 1 and outputs.size >= 1,
            "reduced output slots must be non-empty")
    require(np.all((outputs >= 0) & (outputs < model.port_count)),
            "reduced output slot out of range")
    output_basis = model.input_matrix[:, outputs].T.astype(np.float64, copy=False)
    response = np.empty(
        (shifts.size, outputs.size, rhs0.shape[1]), dtype=np.complex128
    )
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
        response[start:stop, :, :] = np.einsum(
            "ok,fkr->for", output_basis, state, optimize=True
        )
    require(np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag)),
            "non-finite reduced complex response")
    return response


def simulate_full_hines_with_terminal_states(
    tree,
    factor: dict[str, Any],
    source_tree_indices: list[int],
    output_tree_indices: list[int],
) -> tuple[np.ndarray, dict[float, np.ndarray], list[tuple[str, float]]]:
    """Replay exact Hines BE through the longest requested window and retain each x[N-1]."""
    sample_count = int(round(max(WINDOWS_MS) / DT_MS))
    protocol = tail.column_protocol()
    leak = float(factor["leak_reversal_v"])
    voltage = np.full(
        (tree.n_compartments, len(protocol)), leak, dtype=np.float64
    )
    trace = np.empty(
        (sample_count, len(output_tree_indices), len(protocol)), dtype=np.float64
    )
    boundary_steps = {
        int(round(window_ms / DT_MS)): float(window_ms)
        for window_ms in WINDOWS_MS
    }
    terminal_states: dict[float, np.ndarray] = {}
    for step in range(sample_count):
        current = tail._make_current_matrix(
            tree.n_compartments, source_tree_indices, protocol, step
        )
        voltage = tail.tree_hines_backward_euler_step(factor, voltage, current)
        trace[step, :, :] = (
            voltage[np.asarray(output_tree_indices, dtype=np.int64), :] - leak
        )
        completed = step + 1
        if completed in boundary_steps:
            terminal_states[boundary_steps[completed]] = (
                voltage - leak
            ).copy()
    require(set(terminal_states) == set(WINDOWS_MS),
            "full-Hines terminal-state coverage mismatch")
    require(np.all(np.isfinite(trace)), "non-finite full-Hines trace")
    return trace, terminal_states, protocol


def simulate_full_hines_perturbation_windows(
    tree,
    factor: dict[str, Any],
    source_tree_indices: list[int],
    output_tree_indices: list[int],
) -> tuple[np.ndarray, dict[float, np.ndarray], list[tuple[str, float]]]:
    """Replay the same Hines BE map in voltage-perturbation coordinates.

    The canonical replay above keeps absolute membrane voltages to preserve
    legacy transient parity. The transfer equations are written for
    y=V-E_leak. Starting at y=0 and using a zero leak source avoids subtracting
    two O(0.1-V) values after every timestep to recover a much smaller y.
    """
    sample_count = int(round(max(WINDOWS_MS) / DT_MS))
    protocol = tail.column_protocol()
    linear_factor = dict(factor)
    linear_factor["leak_source_a"] = np.zeros_like(factor["leak_source_a"])
    voltage = np.zeros((tree.n_compartments, len(protocol)), dtype=np.float64)
    trace = np.empty(
        (sample_count, len(output_tree_indices), len(protocol)), dtype=np.float64
    )
    boundary_steps = {
        int(round(window_ms / DT_MS)): float(window_ms)
        for window_ms in WINDOWS_MS
    }
    terminal_states: dict[float, np.ndarray] = {}
    for step in range(sample_count):
        current = tail._make_current_matrix(
            tree.n_compartments, source_tree_indices, protocol, step
        )
        voltage = tail.tree_hines_backward_euler_step(
            linear_factor, voltage, current
        )
        trace[step, :, :] = voltage[np.asarray(output_tree_indices, dtype=int), :]
        completed = step + 1
        if completed in boundary_steps:
            terminal_states[boundary_steps[completed]] = voltage.copy()
    require(set(terminal_states) == set(WINDOWS_MS),
            "full-Hines perturbation terminal-state coverage mismatch")
    require(np.all(np.isfinite(trace)),
            "non-finite full-Hines perturbation trace")
    return trace, terminal_states, protocol


def simulate_reduced_with_terminal_states(
    model,
    layout: dict[str, Any],
    common_output_ids: list[int],
    protocol: list[tuple[str, float]],
) -> tuple[np.ndarray, dict[float, np.ndarray]]:
    """Replay exact original reduced BE through 20 ms, then its audited LU tail."""
    sample_count = int(round(max(WINDOWS_MS) / DT_MS))
    factor = tail.factor_reduced_backward_euler(model, DT_S)
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
    trace = np.empty(
        (sample_count, len(common_output_ids), len(protocol)), dtype=np.float64
    )
    port_values = np.empty(
        (layout["port_count"], len(protocol)), dtype=np.float64
    )
    boundary_steps = {
        int(round(window_ms / DT_MS)): float(window_ms)
        for window_ms in WINDOWS_MS
    }
    terminal_states: dict[float, np.ndarray] = {}

    for step in range(sample_count):
        port_current.fill(0.0)
        now_s = step * DT_S
        for column, (source_name, pulse_width_ms) in enumerate(protocol):
            pulse_end = (tail.PULSE_ONSET_MS + pulse_width_ms) / 1000.0
            if tail.PULSE_ONSET_MS / 1000.0 <= now_s < pulse_end:
                port_current[source_slots[source_name], column] = tail.CURRENT_A
        state = tail.reduced_backward_euler_step_factorized(
            model, factor, state, port_current, DT_S
        )
        for column in range(len(protocol)):
            port_values[:, column] = model.port_voltages(state[:, column])
        trace[step, :, :] = port_values[output_slots, :]
        completed = step + 1
        if completed in boundary_steps:
            terminal_states[boundary_steps[completed]] = state.copy()

    require(set(terminal_states) == set(WINDOWS_MS),
            "reduced terminal-state coverage mismatch")
    require(np.all(np.isfinite(trace)), "non-finite reduced trace")
    return trace, terminal_states


def decompose_periodic_boundary_error(
    actual_error_fft: np.ndarray,
    periodic_transfer_component: np.ndarray,
    terminal_boundary_component: np.ndarray,
    one_sided_weights: np.ndarray,
    *,
    identity_scale_norm: float = 0.0,
) -> dict[str, float]:
    """Decompose finite-record error into periodic and terminal components."""
    actual = np.asarray(actual_error_fft, dtype=np.complex128)
    periodic = np.asarray(periodic_transfer_component, dtype=np.complex128)
    boundary = np.asarray(terminal_boundary_component, dtype=np.complex128)
    weights = np.asarray(one_sided_weights, dtype=np.float64)
    require(actual.shape == periodic.shape == boundary.shape == weights.shape,
            "finite-window component arrays and weights must align")
    require(
        np.all(np.isfinite(actual.real)) and np.all(np.isfinite(actual.imag))
        and np.all(np.isfinite(periodic.real)) and np.all(np.isfinite(periodic.imag))
        and np.all(np.isfinite(boundary.real)) and np.all(np.isfinite(boundary.imag))
        and np.all(np.isfinite(weights)) and np.all(weights > 0.0),
        "finite-window component decomposition contains non-finite values",
    )
    reconstructed = periodic + boundary
    # Normalize identity round-off to the output-waveform scale, not the
    # much smaller residual obtained after periodic/boundary cancellation.
    scale = (
        float(identity_scale_norm)
        if np.isfinite(identity_scale_norm) and identity_scale_norm > 0.0
        else max(float(np.linalg.norm(actual)), 1e-30)
    )
    identity_relative, identity_absolute = _finite_identity_error(
        actual, reconstructed, scale_norm=scale
    )
    actual_norm = math.sqrt(float(np.sum(weights * np.square(np.abs(actual)))))
    periodic_norm = math.sqrt(float(np.sum(weights * np.square(np.abs(periodic)))))
    boundary_norm = math.sqrt(float(np.sum(weights * np.square(np.abs(boundary)))))
    energy = actual_norm ** 2
    cross_term_pct = (
        100.0 * (energy - periodic_norm ** 2 - boundary_norm ** 2) / energy
        if energy > 0.0 else 0.0
    )
    return {
        "finite_error_norm": actual_norm,
        "periodic_transfer_norm": periodic_norm,
        "terminal_boundary_norm": boundary_norm,
        "periodic_over_finite_error_norm_pct": (
            100.0 * periodic_norm / actual_norm if actual_norm > 0.0 else 0.0
        ),
        "boundary_over_finite_error_norm_pct": (
            100.0 * boundary_norm / actual_norm if actual_norm > 0.0 else 0.0
        ),
        "periodic_boundary_cross_term_pct": cross_term_pct,
        "identity_relative_error": identity_relative,
        "identity_absolute_error": identity_absolute,
    }


def _finite_identity_error(
    actual_fft: np.ndarray,
    reconstructed_fft: np.ndarray,
    *,
    scale_norm: float = 0.0,
) -> tuple[float, float]:
    actual = np.asarray(actual_fft, dtype=np.complex128)
    reconstructed = np.asarray(reconstructed_fft, dtype=np.complex128)
    diff_norm = float(np.linalg.norm(reconstructed - actual))
    reference_norm = float(np.linalg.norm(actual))
    supplied_scale = float(scale_norm)
    denominator = (
        supplied_scale if np.isfinite(supplied_scale) and supplied_scale > 0.0
        else max(reference_norm, 1e-30)
    )
    return diff_norm / denominator, diff_norm


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv_rows(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _summarize_frequency(
    values: dict[tuple, list[tuple[np.ndarray, np.ndarray, np.ndarray]]],
) -> list[dict[str, Any]]:
    rows = []
    for key, observations in sorted(values.items()):
        cont = np.stack([item[0] for item in observations], axis=0)
        discrete = np.stack([item[1] for item in observations], axis=0)
        mapping = np.stack([item[2] for item in observations], axis=0)
        require(cont.shape[0] == len(SCENARIO_NAMES),
                f"frequency summary lacks scenario coverage: {key}")
        for index, frequency_hz in enumerate(MASTER_FREQUENCIES_HZ):
            rows.append({
                "morphology": key[0],
                "layout_id": key[1],
                "source_name": key[2],
                "output_swc_id": key[3],
                "frequency_hz": float(frequency_hz),
                "parameter_scenarios": cont.shape[0],
                "median_continuous_ac_error_pct": float(np.median(cont[:, index])),
                "p90_continuous_ac_error_pct": float(np.percentile(cont[:, index], 90)),
                "median_discrete_be_error_pct": float(np.median(discrete[:, index])),
                "p90_discrete_be_error_pct": float(np.percentile(discrete[:, index], 90)),
                "median_full_be_vs_ac_delta_pct": float(np.median(mapping[:, index])),
                "p90_full_be_vs_ac_delta_pct": float(np.percentile(mapping[:, index], 90)),
            })
    require(len(rows) == EXPECTED_FREQUENCY_ROWS,
            f"frequency summary rows {len(rows)} != {EXPECTED_FREQUENCY_ROWS}")
    return rows


def _summarize_comparisons(
    comparison_rows: list[dict[str, Any]],
    metric_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (
            row["morphology"], row["source_name"],
            row["pulse_width_ms"], row["window_ms"],
        )
        groups[key].append(row)
    output = []
    metric_index = {
        (
            row["morphology"], row["layout_id"], row["parameter_scenario"],
            row["source_name"], row["output_swc_id"],
            row["pulse_width_ms"], row["window_ms"],
        ): row
        for row in metric_rows
    }
    for key, subset in sorted(groups.items()):
        require(len(subset) == len(SCENARIO_NAMES) * 7,
                f"source/window group lacks 9 scenarios x 7 outputs: {key}")
        cont_ratios = [float(x["nine_over_seven_continuous_ac_ratio"]) for x in subset]
        be_ratios = [float(x["nine_over_seven_discrete_be_ratio"]) for x in subset]
        transient_ratios = [float(x["nine_over_seven_transient_nrmse_ratio"]) for x in subset]
        perturbation_transient_ratios = [
            float(x["nine_over_seven_perturbation_coordinate_transient_nrmse_ratio"])
            for x in subset
        ]
        periodic = []
        boundary = []
        cross = []
        for row in subset:
            nine = metric_index[(
                row["morphology"], "nine_both_q25", row["parameter_scenario"],
                row["source_name"], row["output_swc_id"],
                row["pulse_width_ms"], row["window_ms"],
            )]
            periodic.append(float(nine["transfer_component_over_finite_error_norm_pct"]))
            boundary.append(float(nine["boundary_component_over_finite_error_norm_pct"]))
            cross.append(float(nine["transfer_boundary_cross_term_pct"]))
        output.append({
            "morphology": key[0],
            "source_name": key[1],
            "pulse_width_ms": key[2],
            "window_ms": key[3],
            "scenario_output_pairs": len(subset),
            "median_nine_over_seven_continuous_ac_ratio": float(np.median(cont_ratios)),
            "p90_nine_over_seven_continuous_ac_ratio": float(np.percentile(cont_ratios, 90)),
            "median_nine_over_seven_discrete_be_ratio": float(np.median(be_ratios)),
            "p90_nine_over_seven_discrete_be_ratio": float(np.percentile(be_ratios, 90)),
            "median_nine_over_seven_transient_nrmse_ratio": float(np.median(transient_ratios)),
            "p90_nine_over_seven_transient_nrmse_ratio": float(np.percentile(transient_ratios, 90)),
            "median_nine_over_seven_perturbation_coordinate_transient_nrmse_ratio": float(
                np.median(perturbation_transient_ratios)
            ),
            "p90_nine_over_seven_perturbation_coordinate_transient_nrmse_ratio": float(
                np.percentile(perturbation_transient_ratios, 90)
            ),
            "median_nine_periodic_transfer_component_over_finite_error_norm_pct": float(
                np.median(periodic)
            ),
            "median_nine_boundary_component_of_error_norm_pct": float(np.median(boundary)),
            "median_nine_transfer_boundary_cross_term_pct": float(np.median(cross)),
            "continuous_ac_worse_pairs": sum(x > 1.0 for x in cont_ratios),
            "discrete_be_worse_pairs": sum(x > 1.0 for x in be_ratios),
            "transient_nrmse_worse_pairs": sum(x > 1.0 for x in transient_ratios),
            "perturbation_coordinate_transient_nrmse_worse_pairs": sum(
                x > 1.0 for x in perturbation_transient_ratios
            ),
        })
    require(len(output) == EXPECTED_SOURCE_SUMMARY_ROWS,
            f"source/window summary rows {len(output)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    return output


def _summarize_morphology_windows(
    source_summary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate six source × pulse summaries into one morphology/window row."""
    groups: dict[tuple[str, float], list[dict[str, Any]]] = defaultdict(list)
    for row in source_summary:
        groups[(row["morphology"], float(row["window_ms"]))].append(row)

    metric_columns = (
        "median_nine_over_seven_continuous_ac_ratio",
        "median_nine_over_seven_discrete_be_ratio",
        "median_nine_over_seven_transient_nrmse_ratio",
        "median_nine_over_seven_perturbation_coordinate_transient_nrmse_ratio",
        "median_nine_periodic_transfer_component_over_finite_error_norm_pct",
        "median_nine_boundary_component_of_error_norm_pct",
        "median_nine_transfer_boundary_cross_term_pct",
    )
    rows: list[dict[str, Any]] = []
    expected_groups_per_window = len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS)
    for key, subset in sorted(groups.items()):
        require(
            len(subset) == expected_groups_per_window,
            f"morphology/window group lacks source × pulse coverage: {key}",
        )
        local = {
            column: [float(item[column]) for item in subset]
            for column in metric_columns
        }
        rows.append({
            "morphology": key[0],
            "window_ms": key[1],
            "source_pulse_groups": len(subset),
            "median_nine_over_seven_continuous_ac_ratio": float(
                np.median(local["median_nine_over_seven_continuous_ac_ratio"])
            ),
            "median_nine_over_seven_discrete_be_ratio": float(
                np.median(local["median_nine_over_seven_discrete_be_ratio"])
            ),
            "median_nine_over_seven_absolute_transient_nrmse_ratio": float(
                np.median(local["median_nine_over_seven_transient_nrmse_ratio"])
            ),
            "median_nine_over_seven_perturbation_transient_nrmse_ratio": float(
                np.median(
                    local["median_nine_over_seven_perturbation_coordinate_transient_nrmse_ratio"]
                )
            ),
            "median_nine_periodic_transfer_component_over_finite_error_norm_pct": float(
                np.median(local["median_nine_periodic_transfer_component_over_finite_error_norm_pct"])
            ),
            "median_nine_boundary_component_of_error_norm_pct": float(
                np.median(local["median_nine_boundary_component_of_error_norm_pct"])
            ),
            "median_nine_transfer_boundary_cross_term_pct": float(
                np.median(local["median_nine_transfer_boundary_cross_term_pct"])
            ),
            "median_perturbation_transient_worse_pairs_of_63": float(np.median([
                item["perturbation_coordinate_transient_nrmse_worse_pairs"]
                for item in subset
            ])),
        })
    require(
        len(rows) == EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        f"morphology/window summary rows {len(rows)} != {EXPECTED_MORPH_WINDOW_SUMMARY_ROWS}",
    )
    return rows


def main() -> None:
    started = time.perf_counter()
    master_s_cont = 1j * 2.0 * np.pi * MASTER_FREQUENCIES_HZ
    master_s_be = backward_euler_s_values(MASTER_FREQUENCIES_HZ, DT_S)
    protocol = tail.column_protocol()
    results_dir = Path(__file__).parents[1] / "results"

    metric_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    frequency_accumulator: dict[
        tuple, list[tuple[np.ndarray, np.ndarray, np.ndarray]]
    ] = defaultdict(list)
    morphology_manifest = []
    basis_diagnostics: list[dict[str, Any]] = []
    trace_diagnostics: list[dict[str, Any]] = []
    numerical_runtime = numerical_runtime_diagnostics()
    max_identity_relative_error = 0.0
    max_model_identity_relative_error = 0.0
    max_finite_error_identity_relative_error = 0.0
    max_identity_absolute_error = 0.0

    for morph_spec in MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph_spec["expected_records"],
                f"{morph_spec['name']}: SWC count mismatch")
        digest = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
        require(digest == morph_spec["expected_sha256"],
                f"{morph_spec['name']}: source SHA-256 mismatch")
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
        require(len(common_ids) == 7,
                f"{morph_spec['name']}: expected exactly seven shared output nodes")
        expected_q25 = set(
            int(x) for x in
            preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])
        )
        require(set(int(x) for x in q25_ids.values()) == expected_q25,
                f"{morph_spec['name']}: q25 node identities differ from preflight")
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
        full_rhs = np.zeros((base_tree.n_compartments, len(SOURCE_NAMES)), dtype=np.float64)
        full_rhs[np.asarray(source_tree_indices, dtype=np.int64),
                 np.arange(len(SOURCE_NAMES))] = 1.0

        for scenario_name, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)
            hines_factor = tail.build_tree_hines_be_factor(target, DT_S)
            full_trace, full_terminal, returned_protocol = (
                simulate_full_hines_with_terminal_states(
                    target, hines_factor, source_tree_indices, output_tree_indices
                )
            )
            full_identity_trace, full_identity_terminal, identity_protocol = (
                simulate_full_hines_perturbation_windows(
                    target, hines_factor, source_tree_indices, output_tree_indices
                )
            )
            require(returned_protocol == protocol == identity_protocol,
                    "Hines canonical/perturbation protocol column orders differ")
            full_cont = solve_full_hines_s_response(
                target, master_s_cont, full_rhs, output_tree_indices, chunk_size=50
            )
            full_be = solve_full_hines_s_response(
                target, master_s_be, full_rhs, output_tree_indices, chunk_size=50
            )

            scenario_layout_metrics = {}
            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                source_slots = [
                    int(layout["source_indices"][source]) for source in SOURCE_NAMES
                ]
                source_tree_for_layout = [
                    int(layout["ports"][source_slots[i]])
                    for i in range(len(SOURCE_NAMES))
                ]
                require(source_tree_for_layout == source_tree_indices,
                        f"{morph_spec['name']}/{layout_id}: source node identity changed")
                output_node_to_slot = {
                    int(node): index for index, node in enumerate(layout["node_ids"])
                }
                require(set(int(x) for x in common_ids).issubset(output_node_to_slot),
                        f"{morph_spec['name']}/{layout_id}: shared output is absent")
                output_slots = [
                    int(layout["node_ids"].index(int(node))) for node in common_ids
                ]
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], BASIS_ORDER,
                    conditioning.SHIFTS_HZ,
                    relative_tolerance=conditioning.RELATIVE_TOLERANCE,
                )
                require(model.order == BASIS_ORDER,
                        f"{morph_spec['name']}/{layout_id}: PRIMA order mismatch")
                require(
                    np.allclose(
                        model.input_matrix[:, source_slots],
                        model.basis[np.asarray(layout["ports"])[np.asarray(source_slots)], :].T,
                        rtol=0.0, atol=2e-15,
                    ),
                    f"{morph_spec['name']}/{layout_id}: source basis mapping mismatch",
                )
                reduced_trace, reduced_terminal = (
                    simulate_reduced_with_terminal_states(
                        model, layout, [int(x) for x in common_ids], protocol
                    )
                )
                reduced_rhs = model.input_matrix[:, np.asarray(source_slots, dtype=np.int64)]
                reduced_cont = solve_reduced_s_response(
                    model, master_s_cont, reduced_rhs, output_slots, chunk_size=50
                )
                reduced_be = solve_reduced_s_response(
                    model, master_s_be, reduced_rhs, output_slots, chunk_size=50
                )

                continuous_relative = (
                    100.0 * np.abs(reduced_cont - full_cont)
                    / np.maximum(np.abs(full_cont), 1e-30)
                )
                discrete_relative = (
                    100.0 * np.abs(reduced_be - full_be)
                    / np.maximum(np.abs(full_be), 1e-30)
                )
                mapping_relative = (
                    100.0 * np.abs(full_be - full_cont)
                    / np.maximum(np.abs(full_cont), 1e-30)
                )
                for source_index, source_name in enumerate(SOURCE_NAMES):
                    for output_index, output_node in enumerate(common_ids):
                        frequency_accumulator[(
                            morph_spec["name"], layout_id, source_name, int(output_node)
                        )].append((
                            continuous_relative[:, output_index, source_index].copy(),
                            discrete_relative[:, output_index, source_index].copy(),
                            mapping_relative[:, output_index, source_index].copy(),
                        ))

                basis_diagnostics.append({
                    "morphology": morph_spec["name"],
                    "parameter_scenario": scenario_name,
                    "layout_id": layout_id,
                    "basis_sha256": array_sha256(model.basis),
                    "conductance_sha256": array_sha256(model.conductance_matrix_s),
                    "capacitance_sha256": array_sha256(model.capacitance_matrix_f),
                    "input_sha256": array_sha256(model.input_matrix),
                    "basis_orthogonality_max_abs": float(np.max(np.abs(
                        model.basis.T @ model.basis - np.eye(model.order)
                    ))),
                })
                scenario_layout_metrics[layout_id] = {
                    "trace": reduced_trace,
                    "terminal": reduced_terminal,
                    "model": model,
                    "source_slots": source_slots,
                    "output_slots": output_slots,
                    "continuous": reduced_cont,
                    "discrete": reduced_be,
                }

            trace_diagnostics.append({
                "morphology": morph_spec["name"],
                "parameter_scenario": scenario_name,
                "trace_kind": "full_hines_canonical_absolute",
                "trace_sha256": array_sha256(full_trace),
            })
            trace_diagnostics.append({
                "morphology": morph_spec["name"],
                "parameter_scenario": scenario_name,
                "trace_kind": "full_hines_perturbation",
                "trace_sha256": array_sha256(full_identity_trace),
            })
            for layout_id in LAYOUT_IDS:
                trace_diagnostics.append({
                    "morphology": morph_spec["name"],
                    "parameter_scenario": scenario_name,
                    "layout_id": layout_id,
                    "trace_kind": f"reduced_{layout_id}",
                    "trace_sha256": array_sha256(scenario_layout_metrics[layout_id]["trace"]),
                })
            for window_ms in WINDOWS_MS:
                frequencies, frequency_indices = finite_window_frequency_indices(window_ms)
                sample_count = int(round(window_ms / DT_MS))
                selected_s_be = master_s_be[frequency_indices]
                input_protocol, input_samples = build_sampled_protocol(sample_count)
                require(input_protocol == protocol,
                        "finite-window input protocol order mismatch")
                input_dft = np.fft.rfft(input_samples, axis=0)
                one_sided = one_sided_dft_weights(sample_count)
                # The transfer identity is formulated for y=V-E_leak.
                # Use the numerically stable zero-origin replay for its terminal state.
                full_state = full_identity_terminal[float(window_ms)]
                full_boundary_rhs = hines_factor["c_over_dt"][:, None] * full_state
                full_boundary = solve_full_hines_s_response(
                    target, selected_s_be, full_boundary_rhs,
                    output_tree_indices, chunk_size=50,
                )

                for layout_id in LAYOUT_IDS:
                    payload = scenario_layout_metrics[layout_id]
                    reduced_trace = payload["trace"]
                    reduced_state = payload["terminal"][float(window_ms)]
                    model = payload["model"]
                    source_slots = payload["source_slots"]
                    output_slots = payload["output_slots"]
                    reduced_boundary_rhs = (
                        (model.capacitance_matrix_f / DT_S) @ reduced_state
                    )
                    reduced_boundary = solve_reduced_s_response(
                        model, selected_s_be, reduced_boundary_rhs,
                        output_slots, chunk_size=50,
                    )
                    reduced_transfer_be = payload["discrete"][frequency_indices, :, :]
                    reduced_transfer_cont = payload["continuous"][frequency_indices, :, :]
                    full_transfer_be = full_be[frequency_indices, :, :]
                    full_transfer_cont = full_cont[frequency_indices, :, :]

                    for source_index, source_name in enumerate(SOURCE_NAMES):
                        for pulse_index, pulse_width_ms in enumerate(PULSE_WIDTHS_MS):
                            column = source_index * len(PULSE_WIDTHS_MS) + pulse_index
                            current_spectrum = input_dft[:, column]
                            full_y_canonical = full_trace[:sample_count, :, column]
                            full_y = full_identity_trace[:sample_count, :, column]
                            reduced_y = reduced_trace[:sample_count, :, column]
                            model_identity_errors = []
                            full_model_identity_errors = []
                            reduced_model_identity_errors = []
                            finite_error_identity_errors = []
                            model_identity_absolute_errors = []
                            coordinate_delta_pct = []
                            coordinate_delta_v_samples = []
                            for output_index, output_node in enumerate(common_ids):
                                full_y_fft = np.fft.rfft(full_y[:, output_index])
                                reduced_y_fft = np.fft.rfft(reduced_y[:, output_index])
                                full_h_be = full_transfer_be[:, output_index, source_index]
                                reduced_h_be = reduced_transfer_be[:, output_index, source_index]
                                full_q = full_boundary[:, output_index, column]
                                reduced_q = reduced_boundary[:, output_index, column]
                                reconstructed_full = (
                                    full_h_be * current_spectrum - full_q
                                )
                                reconstructed_reduced = (
                                    reduced_h_be * current_spectrum - reduced_q
                                )
                                full_y_norm = float(np.linalg.norm(full_y_fft))
                                reduced_y_norm = float(np.linalg.norm(reduced_y_fft))
                                full_identity_rel, full_identity_abs = _finite_identity_error(
                                    full_y_fft, reconstructed_full, scale_norm=full_y_norm
                                )
                                reduced_identity_rel, reduced_identity_abs = _finite_identity_error(
                                    reduced_y_fft, reconstructed_reduced, scale_norm=reduced_y_norm
                                )
                                max_model_identity_relative_error = max(
                                    max_model_identity_relative_error,
                                    full_identity_rel, reduced_identity_rel,
                                )
                                max_identity_relative_error = max(
                                    max_identity_relative_error,
                                    full_identity_rel, reduced_identity_rel,
                                )
                                max_identity_absolute_error = max(
                                    max_identity_absolute_error,
                                    full_identity_abs, reduced_identity_abs,
                                )
                                model_identity_errors.append(max(
                                    full_identity_rel, reduced_identity_rel
                                ))
                                full_model_identity_errors.append(full_identity_rel)
                                reduced_model_identity_errors.append(reduced_identity_rel)
                                canonical_fft = np.fft.rfft(
                                    full_y_canonical[:, output_index]
                                )
                                coordinate_delta_rel, coordinate_delta_abs = (
                                    _finite_identity_error(
                                        canonical_fft, full_y_fft,
                                        scale_norm=float(np.linalg.norm(canonical_fft)),
                                    )
                                )
                                coordinate_delta_pct.append(100.0 * coordinate_delta_rel)
                                coordinate_delta_v_samples.append(coordinate_delta_abs)

                                actual_error_fft = reduced_y_fft - full_y_fft
                                transfer_component = (
                                    reduced_h_be - full_h_be
                                ) * current_spectrum
                                boundary_component = -(reduced_q - full_q)
                                decomposition = decompose_periodic_boundary_error(
                                    actual_error_fft, transfer_component,
                                    boundary_component, one_sided,
                                    identity_scale_norm=max(full_y_norm, reduced_y_norm),
                                )
                                error_identity_rel = decomposition["identity_relative_error"]
                                error_identity_abs = decomposition["identity_absolute_error"]
                                finite_error_identity_errors.append(error_identity_rel)
                                max_finite_error_identity_relative_error = max(
                                    max_finite_error_identity_relative_error,
                                    error_identity_rel,
                                )
                                max_identity_relative_error = max(
                                    max_identity_relative_error, error_identity_rel
                                )
                                max_identity_absolute_error = max(
                                    max_identity_absolute_error, error_identity_abs
                                )
                                model_identity_absolute_errors.append(error_identity_abs)
                                actual_error_norm = decomposition["finite_error_norm"]
                                transfer_norm = decomposition["periodic_transfer_norm"]
                                boundary_norm = decomposition["terminal_boundary_norm"]
                                cross_pct = decomposition["periodic_boundary_cross_term_pct"]
                                transfer_fraction = decomposition["periodic_over_finite_error_norm_pct"]
                                boundary_fraction = decomposition["boundary_over_finite_error_norm_pct"]

                                cont_metric, cont_error_norm, cont_ref_norm = weighted_transfer_error(
                                    full_transfer_cont[:, output_index, source_index],
                                    reduced_transfer_cont[:, output_index, source_index],
                                    current_spectrum,
                                    frequencies,
                                    continuous_zoh_input=True,
                                )
                                be_metric, be_error_norm, be_ref_norm = weighted_transfer_error(
                                    full_h_be, reduced_h_be, current_spectrum,
                                    frequencies, continuous_zoh_input=False,
                                )
                                mapping_metric = 100.0 * math.sqrt(
                                    float(np.sum(
                                        one_sided * np.square(np.abs(
                                            (full_h_be - full_transfer_cont[:, output_index, source_index])
                                            * current_spectrum
                                        ))
                                    ))
                                    / max(float(np.sum(
                                        one_sided * np.square(np.abs(
                                            full_transfer_cont[:, output_index, source_index]
                                            * current_spectrum
                                        ))
                                    )), 1e-300)
                                )
                                canonical_transient_nrmse = tail.relative_l2_percent(
                                    full_y_canonical[:, output_index], reduced_y[:, output_index]
                                )
                                perturbation_transient_nrmse = tail.relative_l2_percent(
                                    full_y[:, output_index], reduced_y[:, output_index]
                                )
                                metric_rows.append({
                                    "morphology": morph_spec["name"],
                                    "neuromorpho_id": morph_spec["neuromorpho_id"],
                                    "parameter_scenario": scenario_name,
                                    "layout_id": layout_id,
                                    "basis_order": BASIS_ORDER,
                                    "source_name": source_name,
                                    "output_swc_id": int(output_node),
                                    "output_role": ";".join(layout["roles"][int(output_node)]),
                                    "pulse_width_ms": float(pulse_width_ms),
                                    "window_ms": float(window_ms),
                                    "sample_count": sample_count,
                                    "frequency_bin_count": int(frequencies.size),
                                    "frequency_step_hz": float(frequencies[1] - frequencies[0]),
                                    "nyquist_hz": float(frequencies[-1]),
                                    "continuous_ac_zoh_weighted_error_pct": cont_metric,
                                    "continuous_ac_weighted_error_norm_v_s": cont_error_norm,
                                    "continuous_ac_weighted_reference_norm_v_s": cont_ref_norm,
                                    "discrete_be_periodic_transfer_error_pct": be_metric,
                                    "discrete_be_error_norm_v": be_error_norm,
                                    "discrete_be_reference_norm_v": be_ref_norm,
                                    "full_hines_be_vs_continuous_ac_pct": mapping_metric,
                                    "finite_transient_nrmse_pct": canonical_transient_nrmse,
                                    "perturbation_coordinate_transient_nrmse_pct": perturbation_transient_nrmse,
                                    "absolute_vs_perturbation_hines_trace_delta_pct": coordinate_delta_pct[-1],
                                    "periodic_transfer_component_norm_v_samples": transfer_norm,
                                    "terminal_boundary_component_norm_v_samples": boundary_norm,
                                    "finite_error_dft_norm_v_samples": actual_error_norm,
                                    "transfer_component_over_finite_error_norm_pct": transfer_fraction,
                                    "boundary_component_over_finite_error_norm_pct": boundary_fraction,
                                    "transfer_boundary_cross_term_pct": cross_pct,
                                    "finite_dft_identity_relative_error": error_identity_rel,
                                    "max_full_model_identity_relative_error": full_identity_rel,
                                    "max_reduced_model_identity_relative_error": reduced_identity_rel,
                                })

                            identity_rows.append({
                                "morphology": morph_spec["name"],
                                "parameter_scenario": scenario_name,
                                "layout_id": layout_id,
                                "source_name": source_name,
                                "pulse_width_ms": float(pulse_width_ms),
                                "window_ms": float(window_ms),
                                "shared_outputs": len(common_ids),
                                "max_output_model_identity_relative_error": max(model_identity_errors),
                                "max_output_full_model_identity_relative_error": max(
                                    full_model_identity_errors
                                ),
                                "max_output_reduced_model_identity_relative_error": max(
                                    reduced_model_identity_errors
                                ),
                                "max_output_finite_error_identity_relative_error": max(
                                    finite_error_identity_errors
                                ),
                                "max_output_absolute_identity_error_v_samples": max(
                                    model_identity_absolute_errors
                                ),
                                "max_absolute_vs_perturbation_hines_trace_delta_pct": max(
                                    coordinate_delta_pct
                                ),
                                "max_absolute_vs_perturbation_hines_trace_delta_v_samples": max(
                                    coordinate_delta_v_samples
                                ),
                            })

            # The paired table is materialized after all scenario rows exist,
            # keyed by exact identifiers rather than append order.

    require(len(metric_rows) == EXPECTED_CASE_METRIC_ROWS,
            f"case metrics {len(metric_rows)} != {EXPECTED_CASE_METRIC_ROWS}")
    require(len(identity_rows) == EXPECTED_IDENTITY_ROWS,
            f"finite identity rows {len(identity_rows)} != {EXPECTED_IDENTITY_ROWS}")
    identity_diagnostic_path = results_dir / f"{RESULT_STEM}_finite_dft_identity.csv"
    _write_csv(identity_diagnostic_path, identity_rows)
    identity_diagnostic_readback = _read_csv_rows(identity_diagnostic_path)
    require(identity_diagnostic_readback == EXPECTED_IDENTITY_ROWS,
            "finite DFT identity diagnostic read-back count mismatch")
    print(json.dumps({
        "finite_dft_identity_diagnostic_rows": identity_diagnostic_readback,
        "max_model_identity_relative_error": max_model_identity_relative_error,
        "max_finite_error_identity_relative_error": max_finite_error_identity_relative_error,
        "max_identity_relative_error": max_identity_relative_error,
        "identity_relative_tolerance": FINITE_IDENTITY_RELATIVE_TOLERANCE,
    }, indent=2, allow_nan=False), flush=True)

    metric_index = {
        (
            row["morphology"], row["parameter_scenario"], row["layout_id"],
            row["source_name"], row["output_swc_id"],
            row["pulse_width_ms"], row["window_ms"],
        ): row
        for row in metric_rows
    }
    for row in metric_rows:
        if row["layout_id"] != "nine_both_q25":
            continue
        base_key = (
            row["morphology"], row["parameter_scenario"], "seven",
            row["source_name"], row["output_swc_id"],
            row["pulse_width_ms"], row["window_ms"],
        )
        base = metric_index.get(base_key)
        require(base is not None, f"missing seven-port pair {base_key}")
        comparison_rows.append({
            "morphology": row["morphology"],
            "parameter_scenario": row["parameter_scenario"],
            "source_name": row["source_name"],
            "output_swc_id": row["output_swc_id"],
            "output_role": row["output_role"],
            "pulse_width_ms": row["pulse_width_ms"],
            "window_ms": row["window_ms"],
            "seven_continuous_ac_error_pct": base["continuous_ac_zoh_weighted_error_pct"],
            "nine_continuous_ac_error_pct": row["continuous_ac_zoh_weighted_error_pct"],
            "nine_over_seven_continuous_ac_ratio": (
                float(row["continuous_ac_zoh_weighted_error_pct"])
                / max(float(base["continuous_ac_zoh_weighted_error_pct"]), 1e-300)
            ),
            "seven_discrete_be_error_pct": base["discrete_be_periodic_transfer_error_pct"],
            "nine_discrete_be_error_pct": row["discrete_be_periodic_transfer_error_pct"],
            "nine_over_seven_discrete_be_ratio": (
                float(row["discrete_be_periodic_transfer_error_pct"])
                / max(float(base["discrete_be_periodic_transfer_error_pct"]), 1e-300)
            ),
            "seven_transient_nrmse_pct": base["finite_transient_nrmse_pct"],
            "nine_transient_nrmse_pct": row["finite_transient_nrmse_pct"],
            "nine_over_seven_transient_nrmse_ratio": (
                float(row["finite_transient_nrmse_pct"])
                / max(float(base["finite_transient_nrmse_pct"]), 1e-300)
            ),
            "seven_perturbation_coordinate_transient_nrmse_pct": (
                base["perturbation_coordinate_transient_nrmse_pct"]
            ),
            "nine_perturbation_coordinate_transient_nrmse_pct": (
                row["perturbation_coordinate_transient_nrmse_pct"]
            ),
            "nine_over_seven_perturbation_coordinate_transient_nrmse_ratio": (
                float(row["perturbation_coordinate_transient_nrmse_pct"])
                / max(float(base["perturbation_coordinate_transient_nrmse_pct"]), 1e-300)
            ),
        })
    require(len(comparison_rows) == EXPECTED_COMPARISON_ROWS,
            f"nine/seven comparison rows {len(comparison_rows)} != {EXPECTED_COMPARISON_ROWS}")

    frequency_summary = _summarize_frequency(frequency_accumulator)
    source_summary = _summarize_comparisons(comparison_rows, metric_rows)
    morphology_window_summary = _summarize_morphology_windows(source_summary)
    stem = RESULT_STEM
    output_paths = {
        "frequency_summary": results_dir / f"{stem}_frequency_summary.csv",
        "case_metrics": results_dir / f"{stem}_case_metrics.csv",
        "nine_seven_comparisons": results_dir / f"{stem}_nine_seven_comparisons.csv",
        "source_window_summary": results_dir / f"{stem}_source_window_summary.csv",
        "morphology_window_summary": results_dir / f"{stem}_morphology_window_summary.csv",
        "finite_dft_identity": results_dir / f"{stem}_finite_dft_identity.csv",
    }
    _write_csv(output_paths["frequency_summary"], frequency_summary)
    _write_csv(output_paths["case_metrics"], metric_rows)
    _write_csv(output_paths["nine_seven_comparisons"], comparison_rows)
    _write_csv(output_paths["source_window_summary"], source_summary)
    _write_csv(output_paths["morphology_window_summary"], morphology_window_summary)
    readback = {
        name: _read_csv_rows(path) for name, path in output_paths.items()
    }
    expected = {
        "frequency_summary": EXPECTED_FREQUENCY_ROWS,
        "case_metrics": EXPECTED_CASE_METRIC_ROWS,
        "nine_seven_comparisons": EXPECTED_COMPARISON_ROWS,
        "source_window_summary": EXPECTED_SOURCE_SUMMARY_ROWS,
        "morphology_window_summary": EXPECTED_MORPH_WINDOW_SUMMARY_ROWS,
        "finite_dft_identity": EXPECTED_IDENTITY_ROWS,
    }
    for name, count in expected.items():
        require(readback[name] == count,
                f"{name} CSV read-back {readback[name]} != {count}")

    require(max_identity_relative_error <= FINITE_IDENTITY_RELATIVE_TOLERANCE,
            "finite-window DFT boundary-state identity exceeded tolerance "
            f"{FINITE_IDENTITY_RELATIVE_TOLERANCE}: {max_identity_relative_error:.6g}")

    report = {
        "schema_version": 1,
        "status": "prima_q25_four_morphology_boundary_decomposition_passed",
        "method": {
            "continuous_time_resolvent": "H_AC(j*omega) = L (G + j*omega*C)^-1 B",
            "backward_euler_discrete_transfer": (
                "H_BE(exp(j*Omega)) = L (G + (1-exp(-j*Omega))*C/dt)^-1 B"
            ),
            "backward_euler_frequency_mapping": (
                "s_BE=(1-exp(-j*2*pi*f*dt))/dt; "
                "the discrete response equals the continuous resolvent evaluated at s_BE"
            ),
            "sample_and_hold": (
                "u[n] is held constant on [n*dt,(n+1)*dt); x[n] is the state at "
                "the end of that interval; continuous comparator uses the exact "
                "zero-order-hold Fourier factor dt*sinc(f*dt)*exp(-j*pi*f*dt)"
            ),
            "finite_record_identity": (
                "(G+(1-exp(-j*Omega))*C/dt) X = B U - (C/dt)*x[N-1]; "
                "the terminal state is included explicitly, not discarded"
            ),
            "finite_record_boundary_term": (
                "Y=H_BE*U - L*(G+(1-exp(-j*Omega))*C/dt)^-1*(C/dt)*x[N-1]"
            ),
            "discrete_input": (
                f"10-pA rectangular sequence; sample interval {DT_MS:g} ms; onset 2 ms; "
                "widths 2 and 10 ms; DFT is taken over each exact observation window"
            ),
        },
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(LAYOUT_IDS),
            "basis_order": BASIS_ORDER,
            "parameter_scenarios": list(SCENARIO_NAMES),
            "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_onset_ms": tail.PULSE_ONSET_MS,
            "pulse_amplitude_pA": tail.CURRENT_A * 1e12,
            "dt_ms": DT_MS,
            "windows_ms": list(WINDOWS_MS),
            "master_frequency_grid_hz": {
                "minimum": 0.0,
                "maximum": MAX_FREQUENCY_HZ,
                "step": MASTER_FREQUENCY_STEP_HZ,
                "points": int(MASTER_FREQUENCIES_HZ.size),
            },
            "nyquist_hz": MAX_FREQUENCY_HZ,
        },
        "exact_coverage": {
            "frequency_summary_rows": len(frequency_summary),
            "case_metric_rows": len(metric_rows),
            "nine_seven_comparison_rows": len(comparison_rows),
            "source_window_summary_rows": len(source_summary),
            "morphology_window_summary_rows": len(morphology_window_summary),
            "finite_dft_identity_rows": len(identity_rows),
            "csv_read_back": readback,
            "expected": expected_counts(),
        },
        "validation": {
            "finite_identity_relative_tolerance": FINITE_IDENTITY_RELATIVE_TOLERANCE,
            "identity_normalization": "output DFT L2 norm; finite-error identity is not divided by the much smaller inter-model residual norm",
            "full_hines_identity_coordinates": (
                "The DFT identity uses a second mathematically equivalent full-Hines replay "
                "in perturbation coordinates (zero initial perturbation, zero leak source). "
                "The canonical absolute-voltage replay is retained for transient NRMSE, and "
                "its difference from perturbation coordinates is recorded separately."
            ),
            "max_model_identity_relative_error": max_model_identity_relative_error,
            "max_finite_error_identity_relative_error": max_finite_error_identity_relative_error,
            "max_finite_identity_relative_error": max_identity_relative_error,
            "max_finite_identity_absolute_error_v_samples": max_identity_absolute_error,
            "both_morphology_sha256_checked": True,
            "all_morphology_sha256_checked": True,
            "all_morphology_preflights_passed": True,
            "transient_metric_note": (
                "The canonical absolute-voltage transient NRMSE is retained for historical "
                "continuity. The perturbation-coordinate transient NRMSE is also reported "
                "and is the numerically stable comparison for these small passive residuals; "
                "the absolute-vs-perturbation trace delta is recorded per case."
            ),
        },
        "morphology_window_interpretation_summary": morphology_window_summary,
        "reproducibility_diagnostics": {
            "basis_models": basis_diagnostics,
            "trace_outputs": trace_diagnostics,
            "numerical_runtime": numerical_runtime,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": tail.SCIPY_VERSION,
            "neuron": __import__("neuron").__version__,
            "wall_seconds": time.perf_counter() - started,
        },
        "scientific_limits": [
            "The discrete transfer is exact for the declared backward-Euler state update and sample/hold convention.",
            "The continuous AC comparator is sampled on finite-record DFT bins and weighted by the ZOH input spectrum; it is not the exact sampled response of the continuous-time differential equation.",
            "The transfer-only H_BE*U term is a periodic/circular record component; the terminal-state correction is required for a finite record initialized at rest.",
            "Four individual passive linear-RC morphology reconstructions are compared; they are not populations. Control, mouse and epilepsy-surgical source conditions remain separately identified.",
            "Large relative transfer-error ratios can occur when the seven-port denominator is extremely small; absolute weighted norms and finite transient NRMSE are retained.",
            "Full Hines remains canonical. No production solver code or defaults are changed.",
            "No active-neuron, synaptic, plasticity or biological validation is claimed.",
        ],
    }
    report_path = results_dir / f"{stem}_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "exact_coverage": report["exact_coverage"],
        "validation": report["validation"],
        "reproducibility_diagnostics": {
            "basis_model_count": len(basis_diagnostics),
            "trace_output_count": len(trace_diagnostics),
            "unique_basis_hashes": len({row["basis_sha256"] for row in basis_diagnostics}),
            "thread_environment": numerical_runtime["thread_environment"],
            "threadpools": numerical_runtime["threadpools"],
        },
        "runtime": report["runtime"],
    }, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
