#!/usr/bin/env python3
"""Pulse-spectrum-weighted source-to-output transfer validation for q25.

Recomputes Hines and PRIMA transfer responses on a dense band-limited grid,
weights the complex transfer residual by the spectrum of the tested 2 ms and
10 ms rectangular current pulses, then joins each result to the already
validated time-domain transient NRMSE for the exact source/output/scenario.
This is a passive linear-RC numerical audit only.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
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

MORPHOLOGIES = conditioning.MORPHOLOGIES
SOURCES = ("soma", "basal_q75", "apical_q75")
LAYOUTS = ("seven", "nine_both_q25")
SHIFTS_HZ = conditioning.SHIFTS_HZ
ORDER = 168
PULSE_WIDTHS_MS = (2.0, 10.0)
PULSE_ONSET_MS = 2.0
CURRENT_PA = 10.0
DT_MS = 0.1
DURATION_MS = 20.0
FREQUENCIES_HZ = tuple(sorted(set(
    [0.0, 0.1, 1.0]
    + [float(x) for x in range(10, 501, 10)]
    + [float(x) for x in range(600, 5001, 100)]
)))
EXPECTED_FREQUENCY_ROWS = (
    2 * len(conditioning.peng_replay.baseline.parameter_cases())
    * len(LAYOUTS) * len(SOURCES) * 7 * len(FREQUENCIES_HZ)
)
EXPECTED_WEIGHTED_ROWS = (
    2 * len(conditioning.peng_replay.baseline.parameter_cases())
    * len(LAYOUTS) * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
)
EXPECTED_SUMMARY_ROWS = 2 * len(LAYOUTS) * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
EXPECTED_SOURCE_SUMMARY_ROWS = 2 * len(LAYOUTS) * len(SOURCES) * len(PULSE_WIDTHS_MS)
EXPECTED_PAIRED_ROWS = (
    2 * len(conditioning.peng_replay.baseline.parameter_cases())
    * len(SOURCES) * 7 * len(PULSE_WIDTHS_MS)
)
EXPECTED_PAIRED_SOURCE_ROWS = 2 * len(SOURCES) * len(PULSE_WIDTHS_MS)
EXPECTED_PULSE_WEIGHT_ROWS = len(PULSE_WIDTHS_MS) * len(FREQUENCIES_HZ)
EXPECTED_TRANSIENT_INPUT_ROWS = EXPECTED_WEIGHTED_ROWS
RESULT_STEM = "prima_q25_pulse_spectrum_weighted_transfer_2026-11-24"
TRANSIENT_STEMS = {
    "NMO_163775_Peng_mouse_Control": (
        "NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24_transient.csv"
    ),
    "NMO_107159_Tamas_human_pyramidal_Control": (
        "NMO_107159_TamasHumanPyramidalControl_prima_q25_four_layout_replication_2026-11-24_transient.csv"
    ),
}

# The 9-port transient file also contains two q25-only output rows. The
# spectral bridge compares only the seven exact SWC outputs shared with
# the canonical 7-port model, so pin and filter these node IDs explicitly.
TRANSIENT_SHARED_OUTPUT_IDS = {
    "NMO_163775_Peng_mouse_Control": frozenset((1, 144, 3926, 3948, 4104, 4180, 40)),
    "NMO_107159_Tamas_human_pyramidal_Control": frozenset((1, 6363, 4735, 5564, 7023, 4301, 4623)),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "frequency_hz": len(FREQUENCIES_HZ),
        "frequency_rows": EXPECTED_FREQUENCY_ROWS,
        "weighted_output_rows": EXPECTED_WEIGHTED_ROWS,
        "weighted_summary_rows": EXPECTED_SUMMARY_ROWS,
        "weighted_source_summary_rows": EXPECTED_SOURCE_SUMMARY_ROWS,
        "vs_seven_paired_rows": EXPECTED_PAIRED_ROWS,
        "vs_seven_source_summary_rows": EXPECTED_PAIRED_SOURCE_ROWS,
        "transient_input_rows": EXPECTED_TRANSIENT_INPUT_ROWS,
        "pulse_spectrum_sample_rows": EXPECTED_PULSE_WEIGHT_ROWS,
    }


def build_frequency_grid() -> np.ndarray:
    values = np.asarray(FREQUENCIES_HZ, dtype=float)
    require(values[0] == 0.0 and values[-1] == 5000.0,
            "pulse-weighted grid must cover DC through the 0.1 ms Nyquist limit")
    require(np.all(np.diff(values) > 0.0), "frequency grid must be strictly increasing")
    return values


def weighted_complex_transfer_error(
    reference: np.ndarray,
    approximation: np.ndarray,
    frequencies_hz: np.ndarray,
    pulse_width_ms: float,
) -> tuple[float, float]:
    """Return pulse-spectrum-weighted and unweighted complex relative L2 (%)."""
    ref = np.asarray(reference, dtype=np.complex128)
    approx = np.asarray(approximation, dtype=np.complex128)
    f = np.asarray(frequencies_hz, dtype=float)
    require(ref.shape == approx.shape == f.shape, "transfer arrays must share the frequency grid")
    require(np.all(np.isfinite(ref)) and np.all(np.isfinite(approx)),
            "transfer arrays contain non-finite values")
    duration_s = pulse_width_ms * 1e-3
    pulse_amplitude = np.abs(np.sinc(f * duration_s))
    power_weight = pulse_amplitude ** 2
    delta_power = np.abs(approx - ref) ** 2
    ref_power = np.abs(ref) ** 2
    weighted_denominator = float(np.trapezoid(ref_power * power_weight, x=f))
    weighted_numerator = float(np.trapezoid(delta_power * power_weight, x=f))
    unweighted_denominator = float(np.trapezoid(ref_power, x=f))
    unweighted_numerator = float(np.trapezoid(delta_power, x=f))
    require(weighted_denominator > 0.0 and unweighted_denominator > 0.0,
            "full-Hines transfer spectrum has zero energy in the evaluated band")
    weighted = 100.0 * math.sqrt(weighted_numerator / weighted_denominator)
    unweighted = 100.0 * math.sqrt(unweighted_numerator / unweighted_denominator)
    return weighted, unweighted


def load_transient_reference() -> dict[tuple, float]:
    results_dir = Path(__file__).parents[1] / "results"
    lookup: dict[tuple, float] = {}
    total = 0
    for morphology_name, filename in TRANSIENT_STEMS.items():
        path = results_dir / filename
        require(path.is_file(), f"missing validated time-domain transient input: {path}")
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {
                "layout_id", "basis_order", "parameter_scenario", "source_name",
                "pulse_width_ms", "port_swc_id", "port_nrmse_pct",
            }
            missing = required - set(reader.fieldnames or [])
            require(not missing, f"{path}: transient input lacks columns {sorted(missing)}")
            for line, row in enumerate(reader, start=2):
                if int(row["basis_order"]) != ORDER or row["layout_id"] not in LAYOUTS:
                    continue
                output_node_id = int(row["port_swc_id"])
                if output_node_id not in TRANSIENT_SHARED_OUTPUT_IDS[morphology_name]:
                    continue
                key = (
                    morphology_name, row["layout_id"], row["parameter_scenario"],
                    row["source_name"], float(row["pulse_width_ms"]),
                    output_node_id,
                )
                value = float(row["port_nrmse_pct"])
                require(math.isfinite(value) and value >= 0.0,
                        f"{path}:{line}: invalid transient NRMSE")
                require(key not in lookup, f"{path}:{line}: duplicate transient identity {key}")
                lookup[key] = value
                total += 1
    require(total == EXPECTED_TRANSIENT_INPUT_ROWS,
            f"time-domain transient rows {total} != {EXPECTED_TRANSIENT_INPUT_ROWS}")
    return lookup


def weighted_summary(rows: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    output_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"], row["source_name"],
            row["output_swc_id"], row["output_role"], row["pulse_width_ms"],
        )
        output_groups[key].append(row)
    output = []
    for key, subset in sorted(output_groups.items()):
        require(len(subset) == 9, f"expected nine passive scenarios for {key}")
        values = [float(x["pulse_weighted_transfer_error_pct"]) for x in subset]
        unweighted = [float(x["unweighted_transfer_error_pct"]) for x in subset]
        output.append({
            "morphology": key[0], "layout_id": key[1], "source_name": key[2],
            "output_swc_id": key[3], "output_role": key[4],
            "pulse_width_ms": key[5], "parameter_scenarios": len(subset),
            "median_pulse_weighted_transfer_error_pct": statistics.median(values),
            "p90_pulse_weighted_transfer_error_pct": float(np.percentile(values, 90)),
            "max_pulse_weighted_transfer_error_pct": max(values),
            "median_unweighted_transfer_error_pct": statistics.median(unweighted),
        })
    require(len(output) == EXPECTED_SUMMARY_ROWS,
            f"weighted output summary rows {len(output)} != {EXPECTED_SUMMARY_ROWS}")

    source_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in output:
        key = (row["morphology"], row["layout_id"], row["source_name"], row["pulse_width_ms"])
        source_groups[key].append(row)
    source = []
    for key, subset in sorted(source_groups.items()):
        require(len(subset) == 7, f"weighted source summary must aggregate seven outputs: {key}")
        values = [float(x["median_pulse_weighted_transfer_error_pct"]) for x in subset]
        source.append({
            "morphology": key[0], "layout_id": key[1], "source_name": key[2],
            "pulse_width_ms": key[3], "shared_outputs": len(subset),
            "median_output_pulse_weighted_error_pct": statistics.median(values),
            "p90_output_pulse_weighted_error_pct": float(np.percentile(values, 90)),
            "max_output_pulse_weighted_error_pct": max(values),
        })
    require(len(source) == EXPECTED_SOURCE_SUMMARY_ROWS,
            f"weighted source summary rows {len(source)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    return output, source


def _average_ranks(values: list[float]) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + 1 + j) / 2.0
        i = j
    return ranks


def safe_corr(x: list[float], y: list[float], *, spearman: bool = False) -> float | None:
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if spearman:
        xa, ya = _average_ranks(xa.tolist()), _average_ranks(ya.tolist())
    if len(xa) < 2 or np.std(xa) == 0.0 or np.std(ya) == 0.0:
        return None
    value = float(np.corrcoef(xa, ya)[0, 1])
    return value if math.isfinite(value) else None


def pair_with_seven(
    weighted_rows: list[dict[str, Any]],
    transient_lookup: dict[tuple, float],
) -> tuple[list[dict], list[dict]]:
    index = {
        (
            r["morphology"], r["layout_id"], r["parameter_scenario"],
            r["source_name"], r["pulse_width_ms"], r["output_swc_id"],
        ): r for r in weighted_rows
    }
    paired = []
    for candidate in weighted_rows:
        if candidate["layout_id"] != "nine_both_q25":
            continue
        key = (
            candidate["morphology"], "seven", candidate["parameter_scenario"],
            candidate["source_name"], candidate["pulse_width_ms"],
            candidate["output_swc_id"],
        )
        baseline = index.get(key)
        require(baseline is not None, f"missing seven-port weighted reference for {key}")
        tkey_candidate = (
            candidate["morphology"], "nine_both_q25", candidate["parameter_scenario"],
            candidate["source_name"], candidate["pulse_width_ms"], candidate["output_swc_id"],
        )
        tkey_baseline = (
            candidate["morphology"], "seven", candidate["parameter_scenario"],
            candidate["source_name"], candidate["pulse_width_ms"], candidate["output_swc_id"],
        )
        wt_candidate = float(candidate["pulse_weighted_transfer_error_pct"])
        wt_baseline = float(baseline["pulse_weighted_transfer_error_pct"])
        td_candidate = transient_lookup[tkey_candidate]
        td_baseline = transient_lookup[tkey_baseline]
        require(wt_baseline > 0.0, f"zero weighted seven-port denominator for {key}")
        require(td_baseline > 0.0, f"zero transient seven-port denominator for {key}")
        paired.append({
            "morphology": candidate["morphology"],
            "parameter_scenario": candidate["parameter_scenario"],
            "source_name": candidate["source_name"],
            "pulse_width_ms": candidate["pulse_width_ms"],
            "output_swc_id": candidate["output_swc_id"],
            "output_role": candidate["output_role"],
            "seven_weighted_transfer_error_pct": wt_baseline,
            "nine_weighted_transfer_error_pct": wt_candidate,
            "nine_over_seven_weighted_transfer_ratio": wt_candidate / wt_baseline,
            "seven_transient_nrmse_pct": td_baseline,
            "nine_transient_nrmse_pct": td_candidate,
            "nine_over_seven_transient_ratio": td_candidate / td_baseline,
        })
    require(len(paired) == EXPECTED_PAIRED_ROWS,
            f"paired weighted/time-domain rows {len(paired)} != {EXPECTED_PAIRED_ROWS}")

    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in paired:
        key = (row["morphology"], row["source_name"], row["pulse_width_ms"])
        groups[key].append(row)
    summary = []
    for key, subset in sorted(groups.items()):
        wt = [float(x["nine_over_seven_weighted_transfer_ratio"]) for x in subset]
        td = [float(x["nine_over_seven_transient_ratio"]) for x in subset]
        log_wt = [math.log(max(x, 1e-300)) for x in wt]
        log_td = [math.log(max(x, 1e-300)) for x in td]
        summary.append({
            "morphology": key[0], "source_name": key[1], "pulse_width_ms": key[2],
            "matched_outputs_scenarios": len(subset),
            "median_nine_over_seven_weighted_transfer_ratio": statistics.median(wt),
            "p90_nine_over_seven_weighted_transfer_ratio": float(np.percentile(wt, 90)),
            "median_nine_over_seven_transient_ratio": statistics.median(td),
            "worse_transient_pairs": sum(x > 1.0 for x in td),
            "better_transient_pairs": sum(x < 1.0 for x in td),
            "pearson_log_ratio_correlation": safe_corr(log_wt, log_td),
            "spearman_log_ratio_correlation": safe_corr(log_wt, log_td, spearman=True),
        })
    require(len(summary) == EXPECTED_PAIRED_SOURCE_ROWS,
            f"paired source summaries {len(summary)} != {EXPECTED_PAIRED_SOURCE_ROWS}")
    return paired, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    frequency_grid = build_frequency_grid()
    transient_lookup = load_transient_reference()
    pulse_weights = {
        width: np.abs(np.sinc(frequency_grid * width * 1e-3)) ** 2
        for width in PULSE_WIDTHS_MS
    }
    frequency_rows: list[dict[str, Any]] = []
    weighted_rows: list[dict[str, Any]] = []
    spectrum_rows: list[dict[str, Any]] = []

    for width in PULSE_WIDTHS_MS:
        for f, weight in zip(frequency_grid, pulse_weights[width]):
            spectrum_rows.append({
                "pulse_width_ms": width,
                "frequency_hz": float(f),
                "normalized_pulse_spectral_power": float(weight),
                "pulse_spectrum_model": "sinc(f*T)^2 for an ideal continuous-time rectangular pulse",
            })

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
        require(preflight.get("status") == "PASS", f"{morph_spec['name']}: preflight not PASS")
        digest = morph_spec["expected_sha256"]
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph_spec['name']}: SWC source digest differs from preflight")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        all_layouts, common_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        layouts = {name: all_layouts[name] for name in LAYOUTS}
        seven = layouts["seven"]
        node_to_tree_index = {
            node_id: seven["ports"][slot]
            for slot, node_id in enumerate(seven["node_ids"])
        }
        common_roles = {
            node_id: ";".join(seven["roles"][node_id])
            for node_id in common_ids
        }
        require(len(common_ids) == 7, "expected exactly seven shared output SWC IDs")

        for scenario_name, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)

            # Full-Hines transfer matrix is independent of reduced port layout;
            # compute it once for each source/frequency and reuse for 7/9 ROMs.
            hines: dict[tuple[str, float], dict[int, complex]] = {}
            for source_name in SOURCES:
                current = np.zeros(target.n_compartments, dtype=np.complex128)
                source_slot = seven["source_indices"][source_name]
                current[seven["ports"][source_slot]] = 1.0 + 0.0j
                for frequency_hz in frequency_grid:
                    full = target.solve_passive_frequency_response(float(frequency_hz), current)
                    hines[(source_name, float(frequency_hz))] = {
                        node: complex(full[node_to_tree_index[node]]) for node in common_ids
                    }

            for layout_id, layout in layouts.items():
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], ORDER, SHIFTS_HZ
                )
                np.linalg.cholesky(model.conductance_matrix_s)
                np.linalg.cholesky(model.capacitance_matrix_f)
                port_basis = model.basis[np.asarray(layout["ports"], dtype=int), :]
                source_slots = [layout["source_indices"][name] for name in SOURCES]
                rhs = port_basis[np.asarray(source_slots, dtype=int), :].T
                node_to_port_slot = {node: slot for slot, node in enumerate(layout["node_ids"])}
                pair_spectra: dict[tuple[str, int], dict[str, list[complex]]] = {}
                for source_name in SOURCES:
                    for output_node in common_ids:
                        pair_spectra[(source_name, output_node)] = {
                            "reference": [], "reduced": []
                        }

                for frequency_hz in frequency_grid:
                    omega = 2.0 * math.pi * float(frequency_hz)
                    lhs = model.conductance_matrix_s.astype(np.complex128) + 1j * omega * model.capacitance_matrix_f
                    states = np.linalg.solve(lhs, rhs)
                    reduced_ports = port_basis @ states
                    for source_index, source_name in enumerate(SOURCES):
                        for output_node in common_ids:
                            reference_value = hines[(source_name, float(frequency_hz))][output_node]
                            reduced_value = complex(reduced_ports[node_to_port_slot[output_node], source_index])
                            difference = reduced_value - reference_value
                            absolute_error = float(abs(difference))
                            relative_abs_pct = 100.0 * absolute_error / max(abs(reference_value), 1e-30)
                            frequency_rows.append({
                                "morphology": morph_spec["name"],
                                "layout_id": layout_id,
                                "parameter_scenario": scenario_name,
                                "source_name": source_name,
                                "output_swc_id": output_node,
                                "output_role": common_roles[output_node],
                                "frequency_hz": float(frequency_hz),
                                "full_hines_real_ohm": reference_value.real,
                                "full_hines_imag_ohm": reference_value.imag,
                                "reduced_real_ohm": reduced_value.real,
                                "reduced_imag_ohm": reduced_value.imag,
                                "absolute_transfer_error_ohm": absolute_error,
                                "relative_transfer_error_pct": relative_abs_pct,
                            })
                            pair = pair_spectra[(source_name, output_node)]
                            pair["reference"].append(reference_value)
                            pair["reduced"].append(reduced_value)

                for (source_name, output_node), values in pair_spectra.items():
                    ref_values = np.asarray(values["reference"], dtype=np.complex128)
                    approx_values = np.asarray(values["reduced"], dtype=np.complex128)
                    for width in PULSE_WIDTHS_MS:
                        weighted, unweighted = weighted_complex_transfer_error(
                            ref_values, approx_values, frequency_grid, width
                        )
                        abs_err = np.abs(approx_values - ref_values)
                        relative = abs_err / np.maximum(np.abs(ref_values), 1e-30) * 100.0
                        weighted_rows.append({
                            "morphology": morph_spec["name"],
                            "layout_id": layout_id,
                            "parameter_scenario": scenario_name,
                            "source_name": source_name,
                            "output_swc_id": output_node,
                            "output_role": common_roles[output_node],
                            "pulse_width_ms": width,
                            "frequency_samples": len(frequency_grid),
                            "frequency_min_hz": float(frequency_grid[0]),
                            "frequency_max_hz": float(frequency_grid[-1]),
                            "nyquist_hz_for_dt_0p1ms": 5000.0,
                            "pulse_weighted_transfer_error_pct": weighted,
                            "unweighted_transfer_error_pct": unweighted,
                            "median_frequency_relative_error_pct": float(np.median(relative)),
                            "max_frequency_relative_error_pct": float(np.max(relative)),
                            "median_absolute_transfer_error_ohm": float(np.median(abs_err)),
                            "max_absolute_transfer_error_ohm": float(np.max(abs_err)),
                        })

    require(len(frequency_rows) == EXPECTED_FREQUENCY_ROWS,
            f"frequency detail rows {len(frequency_rows)} != {EXPECTED_FREQUENCY_ROWS}")
    require(len(weighted_rows) == EXPECTED_WEIGHTED_ROWS,
            f"weighted output rows {len(weighted_rows)} != {EXPECTED_WEIGHTED_ROWS}")

    transient_lookup = load_transient_reference()
    for width in PULSE_WIDTHS_MS:
        weights = pulse_weights[width]
        require(np.all(np.isfinite(weights)) and np.all(weights >= 0.0),
                "invalid rectangular pulse spectrum weights")

    output_summary, source_summary = weighted_summary(weighted_rows)
    paired_rows, paired_source = pair_with_seven(weighted_rows, transient_lookup)

    results = Path(__file__).parents[1] / "results"
    write_csv(results / f"{RESULT_STEM}_frequency.csv", frequency_rows)
    write_csv(results / f"{RESULT_STEM}_weighted_output.csv", weighted_rows)
    write_csv(results / f"{RESULT_STEM}_weighted_output_summary.csv", output_summary)
    write_csv(results / f"{RESULT_STEM}_weighted_source_summary.csv", source_summary)
    write_csv(results / f"{RESULT_STEM}_vs_seven_time_domain_pairs.csv", paired_rows)
    write_csv(results / f"{RESULT_STEM}_vs_seven_source_summary.csv", paired_source)
    write_csv(results / f"{RESULT_STEM}_pulse_spectrum_samples.csv", spectrum_rows)

    report = {
        "schema_version": 1,
        "status": "prima_q25_pulse_spectrum_weighted_transfer_passed",
        "frequency_grid_hz": list(FREQUENCIES_HZ),
        "pulse_widths_ms": list(PULSE_WIDTHS_MS),
        "exact_coverage": {
            "frequency_rows": len(frequency_rows),
            "weighted_output_rows": len(weighted_rows),
            "weighted_output_summary_rows": len(output_summary),
            "weighted_source_summary_rows": len(source_summary),
            "vs_seven_time_domain_pair_rows": len(paired_rows),
            "vs_seven_source_summary_rows": len(paired_source),
            "pulse_spectrum_sample_rows": len(spectrum_rows),
            "expected": expected_counts(),
        },
        "integration_note": (
            "Integrates |H_candidate(f)-H_Hines(f)|^2 times |sinc(f*T)|^2 "
            "from DC to 5 kHz using a nonuniform trapezoidal frequency grid. "
            "The onset phase has unit magnitude and cancels in this energy ratio. "
            "This is a band-limited spectral proxy, not the finite-window transient NRMSE."
        ),
        "scientific_limits": [
            "This uses passive linear-RC transfer functions and ideal rectangular-pulse spectra only.",
            "Frequency integration is truncated at 5 kHz (Nyquist for dt=0.1 ms); finite 20 ms observation-window effects are not modeled.",
            "The weighted spectral error is compared against, but is not identical to, the archived finite-window transient NRMSE.",
            "Only two individual morphology reconstructions are compared; no population or biological conclusion is established.",
            "Full Hines remains canonical; no production code or defaults are changed.",
        ],
        "runtime": {
            "python": __import__("sys").version.split()[0],
            "numpy": np.__version__,
            "neuron": __import__("neuron").__version__,
            "wall_seconds": time.perf_counter() - started,
        },
    }
    (results / f"{RESULT_STEM}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
