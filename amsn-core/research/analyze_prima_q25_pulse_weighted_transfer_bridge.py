#!/usr/bin/env python3
"""Bridge AC transfer residuals to exact 2-ms / 10-ms pulse spectra.

The audit uses a dense continuous-frequency grid (0–5 kHz, 5-Hz spacing),
weights complex transfer errors by the Fourier magnitude of each rectangular
current pulse, then joins the result to the archived time-domain transient
NRMSE rows. It is a continuous-time spectral proxy, not an exact recreation
of the finite-step backward-Euler transient solver.
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

LAYOUTS = ("seven", "nine_both_q25")
ORDER = 168
SOURCES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS_MS = (2.0, 10.0)
PULSE_AMPLITUDE_A = 10e-12
PULSE_ONSET_MS = 2.0
DT_MS = 0.1
FREQUENCY_MAX_HZ = 5000.0
FREQUENCY_STEP_HZ = 5.0
FREQUENCIES_HZ = np.arange(
    0.0, FREQUENCY_MAX_HZ + 0.5 * FREQUENCY_STEP_HZ, FREQUENCY_STEP_HZ,
    dtype=float,
)
BANDS_HZ = (
    ("0_100_Hz", 0.0, 100.0),
    ("100_500_Hz", 100.0, 500.0),
    ("500_2000_Hz", 500.0, 2000.0),
    ("2000_5000_Hz", 2000.0, 5000.0),
)
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())
MORPHOLOGIES = conditioning.MORPHOLOGIES
RESULT_STEM = "prima_q25_pulse_weighted_transfer_bridge_2026-11-24"
EXPECTED_MODEL_ROWS = 2 * len(SCENARIO_NAMES) * len(LAYOUTS) * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
EXPECTED_BAND_ROWS = EXPECTED_MODEL_ROWS * len(BANDS_HZ)
EXPECTED_COMPARISON_ROWS = 2 * len(SCENARIO_NAMES) * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
EXPECTED_OUTPUT_SUMMARY_ROWS = 2 * len(LAYOUTS) * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
EXPECTED_COMPARISON_SUMMARY_ROWS = 2 * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
EXPECTED_SOURCE_SUMMARY_ROWS = 2 * len(SOURCES) * len(PULSE_WIDTHS_MS)
EXPECTED_BAND_SUMMARY_ROWS = 2 * len(LAYOUTS) * len(SOURCES) * len(PULSE_WIDTHS_MS) * len(BANDS_HZ)

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
REQUIRED_TRANSIENT_COLUMNS = {
    "layout_id", "basis_order", "parameter_scenario", "source_name",
    "pulse_width_ms", "port_swc_id", "port_roles",
    "seven_port_nrmse_pct", "candidate_nrmse_pct",
    "candidate_over_seven_error_ratio",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "frequency_points": int(FREQUENCIES_HZ.size),
        "model_weighted_rows": EXPECTED_MODEL_ROWS,
        "band_energy_rows": EXPECTED_BAND_ROWS,
        "transient_bridge_rows": EXPECTED_COMPARISON_ROWS,
        "by_output_summary_rows": EXPECTED_OUTPUT_SUMMARY_ROWS,
        "comparison_summary_rows": EXPECTED_COMPARISON_SUMMARY_ROWS,
        "by_source_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
        "band_summary_rows": EXPECTED_BAND_SUMMARY_ROWS,
    }


def validate_frequency_grid(
    frequencies: np.ndarray,
    *,
    require_full_grid: bool = False,
) -> None:
    values = np.asarray(frequencies, dtype=float)
    require(values.ndim == 1 and values.size >= 2, "frequency grid must be a vector")
    require(np.all(np.isfinite(values)), "frequency grid must be finite")
    require(values[0] >= 0.0 and np.all(np.diff(values) > 0.0),
            "frequency grid must be non-negative and strictly increasing")
    require(np.allclose(np.diff(values), 5.0, rtol=0.0, atol=1e-12),
            "frequency grid must use 5-Hz spacing")
    if require_full_grid:
        require(values.size == 1001, "expected 1,001 frequency points")
        require(values[0] == 0.0 and values[-1] == 5000.0,
                "frequency endpoints mismatch")


def batched_hines_frequency_response(
    tree,
    frequencies_hz: np.ndarray,
    source_indices: list[int],
    output_indices: list[int],
    *,
    chunk_size: int = 100,
) -> np.ndarray:
    """Vectorized exact complex-Hines solve for many frequencies and sources.

    Returns H(f) in V/A with shape (frequency, output, source). The elimination
    ordering and tree coefficients mirror CableTree.solve_passive_frequency_response.
    """
    frequencies = np.asarray(frequencies_hz, dtype=float)
    validate_frequency_grid(frequencies)
    require(bool(source_indices) and bool(output_indices), "source/output lists must be non-empty")
    require(all(0 <= int(x) < tree.n_compartments for x in source_indices),
            "source compartment index out of bounds")
    require(all(0 <= int(x) < tree.n_compartments for x in output_indices),
            "output compartment index out of bounds")
    require(chunk_size > 0, "chunk_size must be positive")

    n = tree.n_compartments
    n_sources = len(source_indices)
    response = np.empty(
        (frequencies.size, len(output_indices), n_sources),
        dtype=np.complex128,
    )
    for start in range(0, frequencies.size, chunk_size):
        stop = min(start + chunk_size, frequencies.size)
        local_frequencies = frequencies[start:stop]
        omega = 2.0 * math.pi * local_frequencies
        diagonal = (
            tree.membrane_leak_s[:, None].astype(np.complex128)
            + 1j * omega[None, :] * tree.capacitance_f[:, None]
        )
        rhs = np.zeros((n, stop - start, n_sources), dtype=np.complex128)
        for source_slot, source_index in enumerate(source_indices):
            rhs[int(source_index), :, source_slot] = 1.0 + 0.0j

        for child in range(1, n):
            parent = int(tree.parent_index[child])
            conductance = float(tree.axial_g_s[child])
            diagonal[child, :] += conductance
            diagonal[parent, :] += conductance

        for child in range(n - 1, 0, -1):
            parent = int(tree.parent_index[child])
            conductance = float(tree.axial_g_s[child])
            pivot = diagonal[child, :]
            require(np.all(np.isfinite(pivot)) and np.all(np.abs(pivot) > 0.0),
                    "singular pivot in vectorized Hines elimination")
            diagonal[parent, :] -= conductance * conductance / pivot
            rhs[parent, :, :] += (
                conductance / pivot
            )[:, None] * rhs[child, :, :]

        root = diagonal[0, :]
        require(np.all(np.isfinite(root)) and np.all(np.abs(root) > 0.0),
                "singular root pivot in vectorized Hines elimination")
        voltage = np.empty_like(rhs)
        voltage[0, :, :] = rhs[0, :, :] / root[:, None]
        for child in range(1, n):
            parent = int(tree.parent_index[child])
            conductance = float(tree.axial_g_s[child])
            voltage[child, :, :] = (
                rhs[child, :, :] + conductance * voltage[parent, :, :]
            ) / diagonal[child, :, None]

        selected = voltage[np.asarray(output_indices, dtype=int), :, :]
        response[start:stop, :, :] = np.transpose(selected, (1, 0, 2))

    require(np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag)),
            "non-finite vectorized Hines frequency response")
    return response


def reduced_frequency_response(
    model,
    layout,
    output_node_ids: list[int],
    source_names: tuple[str, ...],
    frequencies_hz: np.ndarray,
    *,
    chunk_size: int = 50,
) -> np.ndarray:
    """Compute reduced source-to-output transfer responses for all frequencies."""
    frequencies = np.asarray(frequencies_hz, dtype=float)
    validate_frequency_grid(frequencies)
    node_to_slot = {int(node_id): i for i, node_id in enumerate(layout["node_ids"])}
    output_slots = [node_to_slot[int(node)] for node in output_node_ids]
    output_port_indices = np.asarray(
        [layout["ports"][slot] for slot in output_slots], dtype=int
    )
    source_slots = [int(layout["source_indices"][name]) for name in source_names]
    output_basis = model.basis[output_port_indices, :]
    input_reduced = model.input_matrix[:, np.asarray(source_slots, dtype=int)]
    order = int(model.order)
    response = np.empty(
        (frequencies.size, len(output_node_ids), len(source_names)),
        dtype=np.complex128,
    )

    for start in range(0, frequencies.size, chunk_size):
        stop = min(start + chunk_size, frequencies.size)
        omega = 2.0 * math.pi * frequencies[start:stop]
        lhs = (
            model.conductance_matrix_s[None, :, :].astype(np.complex128)
            + 1j * omega[:, None, None] * model.capacitance_matrix_f[None, :, :]
        )
        rhs = np.broadcast_to(
            input_reduced[None, :, :],
            (stop - start, order, len(source_names)),
        )
        state = np.linalg.solve(lhs, rhs)
        response[start:stop, :, :] = np.einsum(
            "ok,fks->fos", output_basis, state, optimize=True
        )

    require(np.all(np.isfinite(response.real)) and np.all(np.isfinite(response.imag)),
            "non-finite reduced frequency response")
    return response


def rectangular_pulse_power_spectrum(
    frequencies_hz: np.ndarray,
    pulse_width_ms: float,
    amplitude_a: float = PULSE_AMPLITUDE_A,
) -> np.ndarray:
    """Magnitude-squared Fourier transform of a rectangular current pulse.

    The time shift (2 ms onset) changes phase only, so it does not enter the
    power spectrum used by Parseval-weighted error integration.
    """
    frequencies = np.asarray(frequencies_hz, dtype=float)
    width_s = float(pulse_width_ms) / 1000.0
    require(width_s > 0.0 and amplitude_a > 0.0, "pulse width and amplitude must be positive")
    spectrum = float(amplitude_a) * width_s * np.sinc(frequencies * width_s)
    return np.square(np.abs(spectrum))


def integrate_weighted_error(
    frequencies_hz: np.ndarray,
    full_transfer: np.ndarray,
    reduced_transfer: np.ndarray,
    pulse_width_ms: float,
    amplitude_a: float = PULSE_AMPLITUDE_A,
) -> dict[str, float]:
    frequencies = np.asarray(frequencies_hz, dtype=float)
    full = np.asarray(full_transfer, dtype=np.complex128)
    reduced = np.asarray(reduced_transfer, dtype=np.complex128)
    require(full.shape == reduced.shape == frequencies.shape,
            "full/reduced transfer arrays must align with the frequency grid")
    require(np.all(np.isfinite(full)) and np.all(np.isfinite(reduced)),
            "transfer arrays must be finite")
    power = rectangular_pulse_power_spectrum(frequencies, pulse_width_ms, amplitude_a)
    error_power = np.square(np.abs(reduced - full))
    full_power = np.square(np.abs(full))
    error_energy = float(np.trapezoid(error_power * power, frequencies))
    reference_energy = float(np.trapezoid(full_power * power, frequencies))
    uniform_error_energy = float(np.trapezoid(error_power, frequencies))
    uniform_reference_energy = float(np.trapezoid(full_power, frequencies))
    require(reference_energy > 0.0 and uniform_reference_energy > 0.0,
            "reference transfer energy must be positive")
    return {
        "pulse_weighted_relative_l2_pct": float(100.0 * math.sqrt(error_energy / reference_energy)),
        "uniform_frequency_relative_l2_pct": float(100.0 * math.sqrt(uniform_error_energy / uniform_reference_energy)),
        "pulse_weighted_error_energy": error_energy,
        "pulse_weighted_reference_energy": reference_energy,
    }


def integrate_band_energy(
    frequencies_hz: np.ndarray,
    full_transfer: np.ndarray,
    reduced_transfer: np.ndarray,
    pulse_width_ms: float,
) -> list[dict[str, Any]]:
    frequencies = np.asarray(frequencies_hz, dtype=float)
    full = np.asarray(full_transfer, dtype=np.complex128)
    reduced = np.asarray(reduced_transfer, dtype=np.complex128)
    power = rectangular_pulse_power_spectrum(frequencies, pulse_width_ms)
    total_error = float(np.trapezoid(np.square(np.abs(reduced - full)) * power, frequencies))
    total_reference = float(np.trapezoid(np.square(np.abs(full)) * power, frequencies))
    require(total_error >= 0.0 and total_reference > 0.0, "invalid total band energy")
    result = []
    for band_name, lower, upper in BANDS_HZ:
        mask = (frequencies >= lower) & (frequencies <= upper)
        local_f = frequencies[mask]
        require(local_f.size >= 2, f"band {band_name} has insufficient samples")
        local_error = float(np.trapezoid(
            np.square(np.abs(reduced[mask] - full[mask])) * power[mask], local_f
        ))
        local_reference = float(np.trapezoid(
            np.square(np.abs(full[mask])) * power[mask], local_f
        ))
        result.append({
            "band_name": band_name,
            "band_min_hz": lower,
            "band_max_hz": upper,
            "band_error_energy": local_error,
            "band_reference_energy": local_reference,
            "band_error_share_pct": (
                100.0 * local_error / total_error if total_error > 0.0 else 0.0
            ),
            "band_relative_l2_pct": (
                100.0 * math.sqrt(local_error / local_reference)
                if local_reference > 0.0 else 0.0
            ),
        })
    require(
        abs(sum(float(r["band_error_energy"]) for r in result) - total_error)
        <= max(total_error * 1e-9, 1e-300),
        "band error energies do not sum to the total",
    )
    return result


def load_transient_rows(path: Path, morphology_name: str) -> dict[tuple, dict[str, Any]]:
    require(path.is_file(), f"missing archived transient input: {path}")
    output: dict[tuple, dict[str, Any]] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, "transient CSV is missing a header")
        missing = REQUIRED_TRANSIENT_COLUMNS - set(reader.fieldnames)
        require(not missing, f"transient CSV missing columns: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            if row["layout_id"] != "nine_both_q25" or int(row["basis_order"]) != ORDER:
                continue
            key = (
                row["parameter_scenario"],
                row["source_name"],
                float(row["pulse_width_ms"]),
                int(row["port_swc_id"]),
            )
            require(key not in output, f"{path}:{line_number}: duplicate transient pair {key}")
            for column in (
                "seven_port_nrmse_pct", "candidate_nrmse_pct",
                "candidate_over_seven_error_ratio",
            ):
                row[column] = float(row[column])
                require(math.isfinite(row[column]), f"{path}:{line_number}: non-finite {column}")
            row["morphology"] = morphology_name
            output[key] = row
    expected = len(SCENARIO_NAMES) * len(SOURCES) * len(PULSE_WIDTHS_MS) * 7
    require(len(output) == expected,
            f"{morphology_name}: transient dual-q25 rows {len(output)} != {expected}")
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_rows(
    model_rows: list[dict[str, Any]],
    band_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    output_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["source_name"], row["output_swc_id"], row["output_role"],
            row["pulse_width_ms"],
        )
        output_groups[key].append(row)
    output_summary = []
    for key, subset in sorted(output_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES), f"scenario coverage mismatch for {key}")
        output_summary.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "source_name": key[3], "output_swc_id": key[4], "output_role": key[5],
            "pulse_width_ms": key[6], "parameter_scenarios": len(subset),
            "median_pulse_weighted_error_pct": float(np.median([
                r["pulse_weighted_relative_l2_pct"] for r in subset
            ])),
            "p90_pulse_weighted_error_pct": float(np.percentile([
                r["pulse_weighted_relative_l2_pct"] for r in subset
            ], 90)),
            "median_uniform_frequency_error_pct": float(np.median([
                r["uniform_frequency_relative_l2_pct"] for r in subset
            ])),
        })
    require(len(output_summary) == EXPECTED_OUTPUT_SUMMARY_ROWS,
            f"output summary rows {len(output_summary)} != {EXPECTED_OUTPUT_SUMMARY_ROWS}")

    band_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in band_rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"],
            row["source_name"], row["pulse_width_ms"], row["band_name"],
        )
        band_groups[key].append(row)
    band_summary = []
    for key, subset in sorted(band_groups.items()):
        error_energy = sum(float(r["band_error_energy"]) for r in subset)
        reference_energy = sum(float(r["band_reference_energy"]) for r in subset)
        all_error_energy = sum(float(r["pulse_weighted_error_energy"]) for r in subset)
        band_summary.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "source_name": key[3], "pulse_width_ms": key[4], "band_name": key[5],
            "scenario_output_pairs": len(subset),
            "pooled_band_relative_l2_error_pct": (
                100.0 * math.sqrt(error_energy / reference_energy)
                if reference_energy > 0 else 0.0
            ),
            "share_of_total_weighted_error_energy_pct": (
                100.0 * error_energy / all_error_energy if all_error_energy > 0 else 0.0
            ),
        })
    require(len(band_summary) == EXPECTED_BAND_SUMMARY_ROWS,
            f"band summary rows {len(band_summary)} != {EXPECTED_BAND_SUMMARY_ROWS}")

    comparison_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (
            row["morphology"], row["source_name"], row["output_swc_id"],
            row["output_role"], row["pulse_width_ms"],
        )
        comparison_groups[key].append(row)
    comparison_summary = []
    for key, subset in sorted(comparison_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES), f"comparison scenario coverage mismatch {key}")
        spectral = [float(r["pulse_weighted_error_ratio_nine_over_seven"]) for r in subset]
        transient = [float(r["transient_nrmse_ratio_nine_over_seven"]) for r in subset]
        comparison_summary.append({
            "morphology": key[0], "source_name": key[1],
            "output_swc_id": key[2], "output_role": key[3],
            "pulse_width_ms": key[4], "parameter_scenarios": len(subset),
            "median_pulse_weighted_spectral_ratio": float(np.median(spectral)),
            "p90_pulse_weighted_spectral_ratio": float(np.percentile(spectral, 90)),
            "median_transient_nrmse_ratio": float(np.median(transient)),
            "p90_transient_nrmse_ratio": float(np.percentile(transient, 90)),
            "spectral_worse_scenarios": sum(x > 1.0 for x in spectral),
            "transient_worse_scenarios": sum(x > 1.0 for x in transient),
        })
    require(len(comparison_summary) == EXPECTED_COMPARISON_SUMMARY_ROWS,
            f"comparison summary rows {len(comparison_summary)} != {EXPECTED_COMPARISON_SUMMARY_ROWS}")

    source_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        key = (row["morphology"], row["source_name"], row["pulse_width_ms"])
        source_groups[key].append(row)
    source_summary = []
    for key, subset in sorted(source_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES) * 7,
                f"source output coverage mismatch {key}")
        spectral = [float(r["pulse_weighted_error_ratio_nine_over_seven"]) for r in subset]
        transient = [float(r["transient_nrmse_ratio_nine_over_seven"]) for r in subset]
        source_summary.append({
            "morphology": key[0], "source_name": key[1], "pulse_width_ms": key[2],
            "output_scenario_pairs": len(subset),
            "median_pulse_weighted_spectral_ratio": float(np.median(spectral)),
            "p90_pulse_weighted_spectral_ratio": float(np.percentile(spectral, 90)),
            "median_transient_nrmse_ratio": float(np.median(transient)),
            "p90_transient_nrmse_ratio": float(np.percentile(transient, 90)),
            "spectral_worse_pairs": sum(x > 1.0 for x in spectral),
            "transient_worse_pairs": sum(x > 1.0 for x in transient),
        })
    require(len(source_summary) == EXPECTED_SOURCE_SUMMARY_ROWS,
            f"source summary rows {len(source_summary)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    return output_summary, band_summary, comparison_summary, source_summary


def main() -> None:
    validate_frequency_grid(FREQUENCIES_HZ, require_full_grid=True)
    started = time.perf_counter()
    results_dir = Path(__file__).parents[1] / "results"
    model_rows: list[dict[str, Any]] = []
    band_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    transient_by_morphology: dict[str, dict[tuple, dict[str, Any]]] = {}
    morphology_manifest = []

    for morph_spec in MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph_spec["expected_records"],
                f"{morph_spec['name']}: morphology record count mismatch")
        preflight = json.loads(morph_spec["preflight"].read_text(encoding="utf-8"))
        require(preflight.get("status") == "PASS", f"{morph_spec['name']}: preflight failed")
        digest = morph_spec["expected_sha256"]
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph_spec['name']}: preflight digest mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, common_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        require(
            set(q25_ids.values()) == set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])),
            f"{morph_spec['name']}: q25 IDs differ from preflight",
        )
        require(len(common_ids) == 7, f"{morph_spec['name']}: expected seven shared outputs")
        morphology_manifest.append({
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_sha256": digest,
            "swc_records": morph_spec["expected_records"],
            "shared_output_node_ids": common_ids,
            "q25_node_ids": q25_ids,
        })

        transient = load_transient_rows(
            TRANSIENT_FILES[morph_spec["neuromorpho_id"]],
            morph_spec["name"],
        )
        transient_by_morphology[morph_spec["name"]] = transient

        for scenario_name, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)
            # Resolve physical source ports from the validated seven-port layout.
            source_tree_indices = [
                int(layouts["seven"]["ports"][
                    int(layouts["seven"]["source_indices"][source])
                ])
                for source in SOURCES
            ]
            common_output_tree_indices = [
                int(layouts["seven"]["ports"][
                    {int(node): i for i, node in enumerate(layouts["seven"]["node_ids"])}[int(node)]
                ])
                for node in common_ids
            ]
            full = batched_hines_frequency_response(
                target,
                FREQUENCIES_HZ,
                source_tree_indices,
                common_output_tree_indices,
                chunk_size=100,
            )

            for layout_id in LAYOUTS:
                layout = layouts[layout_id]
                node_to_slot = {int(node): i for i, node in enumerate(layout["node_ids"])}
                require(set(int(x) for x in common_ids).issubset(node_to_slot),
                        f"{morph_spec['name']}/{layout_id}: shared output node missing")
                candidate_source_nodes = {
                    source: int(layout["ports"][int(layout["source_indices"][source])])
                    for source in SOURCES
                }
                require(
                    all(candidate_source_nodes[source] == source_tree_indices[i]
                        for i, source in enumerate(SOURCES)),
                    f"{morph_spec['name']}/{layout_id}: source node identity changed",
                )
                for node_id in common_ids:
                    require(
                        ";".join(layout["roles"][node_id]) == ";".join(layouts["seven"]["roles"][node_id]),
                        f"{morph_spec['name']}/{layout_id}: output role mapping changed",
                    )

                for order in (ORDER,):
                    model = baseline.prima_reduce_passive_cable_multishift(
                        target, layout["ports"], order, conditioning.SHIFTS_HZ,
                        relative_tolerance=conditioning.RELATIVE_TOLERANCE,
                    )
                    require(model.order == ORDER, "PRIMA model failed to reach order 168")
                    reduced = reduced_frequency_response(
                        model,
                        layout,
                        [int(x) for x in common_ids],
                        SOURCES,
                        FREQUENCIES_HZ,
                        chunk_size=50,
                    )

                    for output_slot, output_node in enumerate(common_ids):
                        output_role = ";".join(layout["roles"][output_node])
                        for source_slot, source in enumerate(SOURCES):
                            full_transfer = full[:, output_slot, source_slot]
                            reduced_transfer = reduced[:, output_slot, source_slot]
                            for pulse_width_ms in PULSE_WIDTHS_MS:
                                metric = integrate_weighted_error(
                                    FREQUENCIES_HZ,
                                    full_transfer,
                                    reduced_transfer,
                                    pulse_width_ms,
                                )
                                model_row = {
                                    "morphology": morph_spec["name"],
                                    "neuromorpho_id": morph_spec["neuromorpho_id"],
                                    "layout_id": layout_id,
                                    "basis_order": ORDER,
                                    "parameter_scenario": scenario_name,
                                    "source_name": source,
                                    "output_swc_id": int(output_node),
                                    "output_role": output_role,
                                    "pulse_width_ms": pulse_width_ms,
                                    "pulse_onset_ms": PULSE_ONSET_MS,
                                    "pulse_amplitude_pA": PULSE_AMPLITUDE_A * 1e12,
                                    "frequency_min_hz": float(FREQUENCIES_HZ[0]),
                                    "frequency_max_hz": float(FREQUENCIES_HZ[-1]),
                                    "frequency_step_hz": FREQUENCY_STEP_HZ,
                                    "frequency_points": int(FREQUENCIES_HZ.size),
                                    **metric,
                                }
                                model_rows.append(model_row)
                                local_bands = integrate_band_energy(
                                    FREQUENCIES_HZ,
                                    full_transfer,
                                    reduced_transfer,
                                    pulse_width_ms,
                                )
                                for band in local_bands:
                                    band_rows.append({
                                        "morphology": morph_spec["name"],
                                        "layout_id": layout_id,
                                        "basis_order": ORDER,
                                        "parameter_scenario": scenario_name,
                                        "source_name": source,
                                        "output_swc_id": int(output_node),
                                        "output_role": output_role,
                                        "pulse_width_ms": pulse_width_ms,
                                        "pulse_weighted_error_energy": metric["pulse_weighted_error_energy"],
                                        "pulse_weighted_reference_energy": metric["pulse_weighted_reference_energy"],
                                        **band,
                                    })



    require(len(model_rows) == EXPECTED_MODEL_ROWS,
            f"weighted model rows {len(model_rows)} != {EXPECTED_MODEL_ROWS}")
    require(len(band_rows) == EXPECTED_BAND_ROWS,
            f"band-energy rows {len(band_rows)} != {EXPECTED_BAND_ROWS}")
    # Join the completed pulse-weighted transfer matrix to the exact archived
    # transient rows only after both seven- and nine-port weighted rows exist.
    model_lookup = {
        (
            r["morphology"], r["layout_id"], r["parameter_scenario"],
            r["source_name"], int(r["output_swc_id"]), float(r["pulse_width_ms"]),
        ): r
        for r in model_rows
    }
    for candidate in model_rows:
        if candidate["layout_id"] != "nine_both_q25":
            continue
        key = (
            candidate["parameter_scenario"], candidate["source_name"],
            float(candidate["pulse_width_ms"]), int(candidate["output_swc_id"]),
        )
        transient_row = transient_by_morphology[candidate["morphology"]].get(key)
        require(transient_row is not None,
                f"missing archived transient pair {candidate['morphology']} {key}")
        require(transient_row["port_roles"] == candidate["output_role"],
                f"transient output role mismatch for {candidate['morphology']} {key}")
        baseline_key = (
            candidate["morphology"], "seven", candidate["parameter_scenario"],
            candidate["source_name"], int(candidate["output_swc_id"]),
            float(candidate["pulse_width_ms"]),
        )
        baseline = model_lookup.get(baseline_key)
        require(baseline is not None, f"missing seven-port weighted baseline {baseline_key}")
        comparison_rows.append({
            "morphology": candidate["morphology"],
            "basis_order": ORDER,
            "parameter_scenario": candidate["parameter_scenario"],
            "source_name": candidate["source_name"],
            "output_swc_id": int(candidate["output_swc_id"]),
            "output_role": candidate["output_role"],
            "pulse_width_ms": float(candidate["pulse_width_ms"]),
            "seven_port_pulse_weighted_error_pct": float(baseline["pulse_weighted_relative_l2_pct"]),
            "nine_port_pulse_weighted_error_pct": float(candidate["pulse_weighted_relative_l2_pct"]),
            "pulse_weighted_error_ratio_nine_over_seven": (
                float(candidate["pulse_weighted_relative_l2_pct"])
                / max(float(baseline["pulse_weighted_relative_l2_pct"]), 1e-300)
            ),
            "transient_seven_port_nrmse_pct": transient_row["seven_port_nrmse_pct"],
            "transient_nine_port_nrmse_pct": transient_row["candidate_nrmse_pct"],
            "transient_nrmse_ratio_nine_over_seven": transient_row["candidate_over_seven_error_ratio"],
        })

    require(len(model_rows) == EXPECTED_MODEL_ROWS,
            f"weighted model rows {len(model_rows)} != {EXPECTED_MODEL_ROWS}")
    require(len(band_rows) == EXPECTED_BAND_ROWS,
            f"band-energy rows {len(band_rows)} != {EXPECTED_BAND_ROWS}")
    require(len(comparison_rows) == EXPECTED_COMPARISON_ROWS,
            f"transient bridge rows {len(comparison_rows)} != {EXPECTED_COMPARISON_ROWS}")

    output_summary, band_summary, comparison_summary, source_summary = summarize_rows(
        model_rows, band_rows, comparison_rows
    )

    results_dir = Path(__file__).parents[1] / "results"
    write_csv(results_dir / f"{RESULT_STEM}_model_weighted.csv", model_rows)
    write_csv(results_dir / f"{RESULT_STEM}_band_energy.csv", band_rows)
    write_csv(results_dir / f"{RESULT_STEM}_by_output_summary.csv", output_summary)
    write_csv(results_dir / f"{RESULT_STEM}_transient_bridge.csv", comparison_rows)
    write_csv(results_dir / f"{RESULT_STEM}_comparison_summary.csv", comparison_summary)
    write_csv(results_dir / f"{RESULT_STEM}_by_source_summary.csv", source_summary)
    write_csv(results_dir / f"{RESULT_STEM}_band_summary.csv", band_summary)

    report = {
        "schema_version": 1,
        "status": "prima_q25_pulse_weighted_transfer_bridge_passed",
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(LAYOUTS),
            "basis_order": ORDER,
            "parameter_scenarios": list(SCENARIO_NAMES),
            "sources": list(SOURCES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS),
            "pulse_amplitude_pA": PULSE_AMPLITUDE_A * 1e12,
            "pulse_onset_ms": PULSE_ONSET_MS,
            "time_domain_dt_ms_for_reference": DT_MS,
            "frequency_grid_hz": {
                "minimum": float(FREQUENCIES_HZ[0]),
                "maximum": float(FREQUENCIES_HZ[-1]),
                "step": FREQUENCY_STEP_HZ,
                "points": int(FREQUENCIES_HZ.size),
            },
            "pulse_spectral_weight": "|I(f)|^2 = (I0*T*sinc(f*T))^2",
            "frequency_bands_hz": [
                {"name": name, "min": lower, "max": upper}
                for name, lower, upper in BANDS_HZ
            ],
        },
        "exact_coverage": {
            "model_weighted_rows": len(model_rows),
            "band_energy_rows": len(band_rows),
            "transient_bridge_rows": len(comparison_rows),
            "by_output_summary_rows": len(output_summary),
            "comparison_summary_rows": len(comparison_summary),
            "by_source_summary_rows": len(source_summary),
            "band_summary_rows": len(band_summary),
            "expected": expected_counts(),
        },
        "scientific_limits": [
            "Pulse-weighted transfer error integrates continuous-time AC transfer residuals against the squared Fourier magnitude of a rectangular input pulse using Parseval weighting.",
            "This spectral proxy is not an exact reproduction of the finite-duration, finite-dt backward-Euler transient simulator; onset changes phase but not the power weighting.",
            "Only two individual passive linear-RC morphologies are compared; they are not populations.",
            "Large ratios can occur when the seven-port denominator is extremely small; absolute weighted errors and transient NRMSE are kept beside ratios.",
            "No biological, active-neuron or production-default claim is made; full Hines remains canonical.",
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
