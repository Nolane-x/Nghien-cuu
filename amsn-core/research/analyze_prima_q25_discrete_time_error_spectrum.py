#!/usr/bin/env python3
"""Exact finite-window DFT decomposition of backward-Euler PRIMA errors."""
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

SOURCE_NAMES = tail.SOURCE_NAMES
LAYOUT_IDS = tail.LAYOUT_IDS
PULSE_WIDTHS_MS = tail.PULSE_WIDTHS_MS
WINDOWS_MS = tail.WINDOWS_MS
DT_MS = tail.DT_MS
DT_S = tail.DT_S
BASIS_ORDER = tail.BASIS_ORDER
SCENARIO_NAMES = tuple(conditioning.peng_replay.baseline.parameter_cases())
BANDS_HZ = (
    ("0_100_hz", 0.0, 100.0),
    ("100_500_hz", 100.0, 500.0),
    ("500_2000_hz", 500.0, 2000.0),
    ("2000_5000_hz", 2000.0, 5000.0),
)
RESULT_STEM = "prima_q25_discrete_time_error_spectrum_2026-11-24"
EXPECTED_TRACE_ROWS = 2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS)
EXPECTED_BAND_ROWS = EXPECTED_TRACE_ROWS * len(BANDS_HZ)
EXPECTED_COMPARISON_ROWS = 2 * len(SCENARIO_NAMES) * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7 * len(WINDOWS_MS) * len(BANDS_HZ)
EXPECTED_LAYOUT_SUMMARY_ROWS = 2 * len(LAYOUT_IDS) * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS) * len(BANDS_HZ)
EXPECTED_COMPARISON_SUMMARY_ROWS = 2 * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * len(WINDOWS_MS) * len(BANDS_HZ)
EXPECTED_PARITY_ROWS = 2 * len(SCENARIO_NAMES) * len(LAYOUT_IDS) * len(SOURCE_NAMES) * len(PULSE_WIDTHS_MS) * 7
PARSEVAL_RELATIVE_TOLERANCE = 5e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "trace_rows": EXPECTED_TRACE_ROWS,
        "band_energy_rows": EXPECTED_BAND_ROWS,
        "band_comparison_rows": EXPECTED_COMPARISON_ROWS,
        "layout_band_summary_rows": EXPECTED_LAYOUT_SUMMARY_ROWS,
        "comparison_band_summary_rows": EXPECTED_COMPARISON_SUMMARY_ROWS,
        "archived_20ms_parity_rows": EXPECTED_PARITY_ROWS,
    }


def _band_mask(frequencies_hz: np.ndarray, lower_hz: float, upper_hz: float, *, include_upper: bool) -> np.ndarray:
    if include_upper:
        return (frequencies_hz >= lower_hz) & (frequencies_hz <= upper_hz)
    return (frequencies_hz >= lower_hz) & (frequencies_hz < upper_hz)


def parseval_band_decomposition(
    error_v: np.ndarray, reference_v: np.ndarray, dt_s: float,
) -> tuple[list[dict[str, float | int | str]], dict[str, float | int]]:
    """Decompose a real trace; band energies must sum to sum(error**2)."""
    error = np.asarray(error_v, dtype=np.float64)
    reference = np.asarray(reference_v, dtype=np.float64)
    require(error.ndim == 1 and reference.shape == error.shape, "error/reference shapes differ")
    require(error.size >= 2 and error.size % 2 == 0, "sample count must be positive and even")
    require(np.all(np.isfinite(error)) and np.all(np.isfinite(reference)), "non-finite trace")
    require(np.isfinite(dt_s) and dt_s > 0.0, "dt_s must be finite and positive")

    n = int(error.size)
    frequencies = np.fft.rfftfreq(n, d=float(dt_s))
    spectrum = np.fft.rfft(error)
    weights = np.full(spectrum.size, 2.0, dtype=np.float64)
    weights[0] = 1.0
    weights[-1] = 1.0  # Nyquist bin for even-length real input
    one_sided_energy = weights * np.square(np.abs(spectrum)) / n

    time_energy = float(np.dot(error, error))
    frequency_energy = float(np.sum(one_sided_energy))
    parseval_abs = abs(frequency_energy - time_energy)
    parseval_rel = parseval_abs / max(time_energy, np.finfo(np.float64).tiny)
    require(parseval_rel <= PARSEVAL_RELATIVE_TOLERANCE,
            f"Parseval mismatch: relative error {parseval_rel:.6g}")

    reference_norm = max(float(np.linalg.norm(reference)), 1e-30)
    total_nrmse = 100.0 * math.sqrt(time_energy) / reference_norm
    rows: list[dict[str, float | int | str]] = []
    covered = np.zeros(frequencies.size, dtype=np.int8)
    band_energy_sum = 0.0
    for index, (name, low, high) in enumerate(BANDS_HZ):
        mask = _band_mask(frequencies, low, high, include_upper=index == len(BANDS_HZ) - 1)
        require(np.any(mask), f"no frequency bins in {name}")
        covered[mask] += 1
        energy = float(np.sum(one_sided_energy[mask]))
        band_energy_sum += energy
        rows.append({
            "band": name,
            "band_min_hz": low,
            "band_max_hz": high,
            "frequency_bin_count": int(np.count_nonzero(mask)),
            "band_error_energy_v2_samples": energy,
            "band_error_rms_v": math.sqrt(energy / n),
            "band_nrmse_pct": 100.0 * math.sqrt(energy) / reference_norm,
            "band_error_energy_share_pct": 100.0 * energy / time_energy if time_energy > 0.0 else 0.0,
        })
    require(np.all(covered == 1), "bands do not partition all DFT bins exactly once")
    band_parseval_rel = abs(band_energy_sum - time_energy) / max(time_energy, np.finfo(np.float64).tiny)
    require(band_parseval_rel <= PARSEVAL_RELATIVE_TOLERANCE, "band totals fail Parseval")
    return rows, {
        "sample_count": n,
        "frequency_bin_count": int(frequencies.size),
        "frequency_step_hz": float(frequencies[1] - frequencies[0]),
        "nyquist_hz": float(frequencies[-1]),
        "time_error_energy_v2_samples": time_energy,
        "frequency_error_energy_v2_samples": frequency_energy,
        "parseval_absolute_error_v2_samples": parseval_abs,
        "parseval_relative_error": parseval_rel,
        "band_parseval_relative_error": band_parseval_rel,
        "time_domain_nrmse_pct": total_nrmse,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def csv_row_count(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def summarize(band_rows: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    layout_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in band_rows:
        key = (row["morphology"], row["layout_id"], row["source_name"], row["pulse_width_ms"], row["window_ms"], row["band"])
        layout_groups[key].append(row)
    layout_summary = []
    for key, subset in sorted(layout_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES) * 7, f"layout group coverage mismatch: {key}")
        band_nrmse = [float(x["band_nrmse_pct"]) for x in subset]
        shares = [float(x["band_error_energy_share_pct"]) for x in subset]
        totals = [float(x["total_nrmse_pct"]) for x in subset]
        layout_summary.append({
            "morphology": key[0], "layout_id": key[1], "source_name": key[2],
            "pulse_width_ms": key[3], "window_ms": key[4], "band": key[5],
            "scenario_output_pairs": len(subset),
            "median_band_nrmse_pct": float(np.median(band_nrmse)),
            "p90_band_nrmse_pct": float(np.percentile(band_nrmse, 90)),
            "median_band_error_energy_share_pct": float(np.median(shares)),
            "median_total_nrmse_pct": float(np.median(totals)),
        })
    require(len(layout_summary) == EXPECTED_LAYOUT_SUMMARY_ROWS,
            f"layout summaries {len(layout_summary)} != {EXPECTED_LAYOUT_SUMMARY_ROWS}")

    comparison_groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in comparisons:
        key = (row["morphology"], row["source_name"], row["pulse_width_ms"], row["window_ms"], row["band"])
        comparison_groups[key].append(row)
    comparison_summary = []
    for key, subset in sorted(comparison_groups.items()):
        require(len(subset) == len(SCENARIO_NAMES) * 7, f"comparison group coverage mismatch: {key}")
        ratios = [float(x["nine_over_seven_band_nrmse_ratio"]) for x in subset
                  if x["nine_over_seven_band_nrmse_ratio"] is not None]
        comparison_summary.append({
            "morphology": key[0], "source_name": key[1], "pulse_width_ms": key[2],
            "window_ms": key[3], "band": key[4], "scenario_output_pairs": len(subset),
            "defined_ratio_pairs": len(ratios), "undefined_ratio_pairs": len(subset) - len(ratios),
            "median_nine_over_seven_band_nrmse_ratio": float(np.median(ratios)) if ratios else None,
            "p90_nine_over_seven_band_nrmse_ratio": float(np.percentile(ratios, 90)) if ratios else None,
            "worse_pairs": sum(x > 1.0 for x in ratios),
            "better_pairs": sum(x < 1.0 for x in ratios),
            "tied_pairs": sum(x == 1.0 for x in ratios),
            "median_seven_band_nrmse_pct": float(np.median([float(x["seven_band_nrmse_pct"]) for x in subset])),
            "median_nine_band_nrmse_pct": float(np.median([float(x["nine_band_nrmse_pct"]) for x in subset])),
        })
    require(len(comparison_summary) == EXPECTED_COMPARISON_SUMMARY_ROWS,
            f"comparison summaries {len(comparison_summary)} != {EXPECTED_COMPARISON_SUMMARY_ROWS}")
    return layout_summary, comparison_summary


def main() -> None:
    started = time.perf_counter()
    band_rows: list[dict[str, Any]] = []
    parity_rows: list[dict[str, Any]] = []
    morphology_manifest = []
    max_parseval_rel = 0.0
    max_parseval_abs = 0.0
    max_parity_abs = 0.0
    max_parity_rel = 0.0
    protocol = tail.column_protocol()
    results_dir = Path(__file__).parents[1] / "results"

    for morph in conditioning.MORPHOLOGIES:
        module = morph["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph["expected_records"], f"{morph['name']}: SWC count mismatch")
        digest = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
        require(digest == morph["expected_sha256"], f"{morph['name']}: source hash mismatch")
        preflight = json.loads(morph["preflight"].read_text(encoding="utf-8"))
        require(preflight.get("status") == "PASS", f"{morph['name']}: preflight failed")
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph['name']}: preflight hash mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, common_ids, q25_ids = module.build_four_layouts(morphology, reader, sections, base_tree)
        expected_q25 = set(int(x) for x in preflight.get("amsn", {}).get("q25_only_swc_node_ids", []))
        require(set(int(x) for x in q25_ids.values()) == expected_q25, f"{morph['name']}: q25 node map mismatch")
        morphology_manifest.append({
            "morphology": morph["name"], "neuromorpho_id": morph["neuromorpho_id"],
            "swc_records": morph["expected_records"], "swc_sha256": digest,
            "shared_output_node_ids": [int(x) for x in common_ids],
            "q25_node_ids": {k: int(v) for k, v in q25_ids.items()},
        })
        archived = tail.load_archived_transient(tail.TRANSIENT_FILES[morph["neuromorpho_id"]], morph["name"])

        for scenario, scales in baseline.parameter_cases().items():
            target = conditioning.build_target_tree(module, base_tree, scales)
            hines_factor = tail.build_tree_hines_be_factor(target, DT_S)
            full_layout = layouts["nine_both_q25"]
            source_indices = [int(full_layout["ports"][int(full_layout["source_indices"][name])]) for name in SOURCE_NAMES]
            seven_slots = {int(node): slot for slot, node in enumerate(layouts["seven"]["node_ids"])}
            output_indices = [int(layouts["seven"]["ports"][seven_slots[int(node)]]) for node in common_ids]
            full_trace, returned_protocol = tail.simulate_full_hines_windows(
                target, hines_factor, hines_factor["c_over_dt"], source_indices, output_indices,
                duration_ms=max(WINDOWS_MS),
            )
            require(returned_protocol == protocol, "full-Hines protocol order mismatch")

            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], BASIS_ORDER, conditioning.SHIFTS_HZ,
                    relative_tolerance=conditioning.RELATIVE_TOLERANCE,
                )
                require(model.order == BASIS_ORDER, f"{morph['name']}/{layout_id}: basis order mismatch")
                reduced = tail.simulate_reduced_windows(
                    model, layout, [int(x) for x in common_ids], protocol, duration_ms=max(WINDOWS_MS),
                )
                for source_index, source_name in enumerate(SOURCE_NAMES):
                    for pulse_index, pulse_width in enumerate(PULSE_WIDTHS_MS):
                        column = source_index * len(PULSE_WIDTHS_MS) + pulse_index
                        for output_index, output_node in enumerate(common_ids):
                            output_role = ";".join(layout["roles"][int(output_node)])
                            for window_ms in WINDOWS_MS:
                                samples = int(round(window_ms / DT_MS))
                                full_values = full_trace[:samples, output_index, column]
                                reduced_values = reduced[:samples, output_index, column]
                                pieces, diag = parseval_band_decomposition(reduced_values - full_values, full_values, DT_S)
                                direct = tail.relative_l2_percent(full_values, reduced_values)
                                require(math.isclose(diag["time_domain_nrmse_pct"], direct, rel_tol=5e-13, abs_tol=1e-15),
                                        "Parseval total does not reproduce time-domain NRMSE")
                                max_parseval_rel = max(max_parseval_rel, diag["parseval_relative_error"], diag["band_parseval_relative_error"])
                                max_parseval_abs = max(max_parseval_abs, diag["parseval_absolute_error_v2_samples"])
                                meta = {
                                    "morphology": morph["name"], "neuromorpho_id": morph["neuromorpho_id"],
                                    "parameter_scenario": scenario, "layout_id": layout_id, "basis_order": BASIS_ORDER,
                                    "source_name": source_name, "output_swc_id": int(output_node), "output_role": output_role,
                                    "pulse_width_ms": float(pulse_width), "window_ms": float(window_ms),
                                    "dt_ms": DT_MS, "pulse_onset_ms": tail.PULSE_ONSET_MS,
                                    "pulse_amplitude_pA": tail.CURRENT_A * 1e12, "sample_count": samples,
                                    "frequency_step_hz": diag["frequency_step_hz"], "nyquist_hz": diag["nyquist_hz"],
                                    "total_nrmse_pct": diag["time_domain_nrmse_pct"],
                                    "total_error_energy_v2_samples": diag["time_error_energy_v2_samples"],
                                    "parseval_relative_error": diag["parseval_relative_error"],
                                }
                                for piece in pieces:
                                    band_rows.append({**meta, **piece})
                                if window_ms == 20.0:
                                    archive = archived[(scenario, source_name, float(pulse_width), int(output_node))]
                                    archived_value = float(archive["seven_port_nrmse_pct"] if layout_id == "seven" else archive["candidate_nrmse_pct"])
                                    abs_delta = abs(direct - archived_value)
                                    rel_delta = 100.0 * abs_delta / max(abs(archived_value), 1e-30)
                                    max_parity_abs = max(max_parity_abs, abs_delta)
                                    max_parity_rel = max(max_parity_rel, rel_delta)
                                    parity_rows.append({
                                        "morphology": morph["name"], "layout_id": layout_id,
                                        "parameter_scenario": scenario, "source_name": source_name,
                                        "output_swc_id": int(output_node), "pulse_width_ms": float(pulse_width),
                                        "computed_20ms_nrmse_pct": direct, "archived_20ms_nrmse_pct": archived_value,
                                        "absolute_delta_pct_points": abs_delta, "relative_delta_pct": rel_delta,
                                    })

    require(len(band_rows) == EXPECTED_BAND_ROWS, f"band rows {len(band_rows)} != {EXPECTED_BAND_ROWS}")
    require(len(parity_rows) == EXPECTED_PARITY_ROWS, f"parity rows {len(parity_rows)} != {EXPECTED_PARITY_ROWS}")
    require(all(tail.archived_parity_within_absolute_tolerance(float(x["computed_20ms_nrmse_pct"]), float(x["archived_20ms_nrmse_pct"])) for x in parity_rows),
            f"20-ms archived parity failed: max absolute delta {max_parity_abs:.8g} percentage points")

    row_index = {
        (x["morphology"], x["layout_id"], x["parameter_scenario"], x["source_name"],
         x["output_swc_id"], x["pulse_width_ms"], x["window_ms"], x["band"]): x
        for x in band_rows
    }
    comparisons = []
    for candidate in band_rows:
        if candidate["layout_id"] != "nine_both_q25":
            continue
        key = (candidate["morphology"], "seven", candidate["parameter_scenario"], candidate["source_name"],
               candidate["output_swc_id"], candidate["pulse_width_ms"], candidate["window_ms"], candidate["band"])
        base = row_index.get(key)
        require(base is not None, f"missing seven-port comparison {key}")
        base_value = float(base["band_nrmse_pct"])
        nine_value = float(candidate["band_nrmse_pct"])
        comparisons.append({
            "morphology": candidate["morphology"], "parameter_scenario": candidate["parameter_scenario"],
            "source_name": candidate["source_name"], "output_swc_id": candidate["output_swc_id"],
            "output_role": candidate["output_role"], "pulse_width_ms": candidate["pulse_width_ms"],
            "window_ms": candidate["window_ms"], "band": candidate["band"],
            "seven_band_nrmse_pct": base_value, "nine_band_nrmse_pct": nine_value,
            "nine_over_seven_band_nrmse_ratio": nine_value / base_value if base_value > 0.0 else None,
            "seven_band_energy_share_pct": base["band_error_energy_share_pct"],
            "nine_band_energy_share_pct": candidate["band_error_energy_share_pct"],
        })
    require(len(comparisons) == EXPECTED_COMPARISON_ROWS,
            f"band comparison rows {len(comparisons)} != {EXPECTED_COMPARISON_ROWS}")
    layout_summary, comparison_summary = summarize(band_rows, comparisons)

    stem = RESULT_STEM
    paths = {
        "band_energy": results_dir / f"{stem}_band_energy.csv",
        "band_comparisons": results_dir / f"{stem}_band_comparisons.csv",
        "layout_summary": results_dir / f"{stem}_layout_band_summary.csv",
        "comparison_summary": results_dir / f"{stem}_comparison_band_summary.csv",
        "parity": results_dir / f"{stem}_20ms_parity.csv",
    }
    write_csv(paths["band_energy"], band_rows)
    write_csv(paths["band_comparisons"], comparisons)
    write_csv(paths["layout_summary"], layout_summary)
    write_csv(paths["comparison_summary"], comparison_summary)
    write_csv(paths["parity"], parity_rows)
    readback = {
        "band_energy_rows": csv_row_count(paths["band_energy"]),
        "band_comparison_rows": csv_row_count(paths["band_comparisons"]),
        "layout_band_summary_rows": csv_row_count(paths["layout_summary"]),
        "comparison_band_summary_rows": csv_row_count(paths["comparison_summary"]),
        "archived_20ms_parity_rows": csv_row_count(paths["parity"]),
    }
    expected = expected_counts()
    for actual_key, expected_key in (
        ("band_energy_rows", "band_energy_rows"),
        ("band_comparison_rows", "band_comparison_rows"),
        ("layout_band_summary_rows", "layout_band_summary_rows"),
        ("comparison_band_summary_rows", "comparison_band_summary_rows"),
        ("archived_20ms_parity_rows", "archived_20ms_parity_rows"),
    ):
        require(readback[actual_key] == expected[expected_key], f"CSV read-back mismatch: {actual_key}")

    report = {
        "schema_version": 1,
        "status": "prima_q25_discrete_time_error_spectrum_passed",
        "method": {
            "transform": "real DFT of actual finite-window sampled backward-Euler output-error traces",
            "parseval": "one-sided rFFT; DC and Nyquist weight 1, interior bins weight 2",
            "band_energy": "sum(weight * abs(rfft(error))**2) / sample_count",
            "bands_hz": [{"name": name, "minimum": low, "maximum": high,
                          "upper_edge_inclusive": i == len(BANDS_HZ) - 1}
                         for i, (name, low, high) in enumerate(BANDS_HZ)],
            "not_a_transfer_proxy": "decomposition of simulated finite-window output error, not a continuous-time transfer approximation",
        },
        "scope": {
            "morphologies": morphology_manifest, "layouts": list(LAYOUT_IDS), "basis_order": BASIS_ORDER,
            "parameter_scenarios": list(SCENARIO_NAMES), "sources": list(SOURCE_NAMES),
            "pulse_widths_ms": list(PULSE_WIDTHS_MS), "pulse_onset_ms": tail.PULSE_ONSET_MS,
            "pulse_amplitude_pA": tail.CURRENT_A * 1e12, "dt_ms": DT_MS,
            "windows_ms": list(WINDOWS_MS), "nyquist_hz": 5000.0,
        },
        "exact_coverage": {
            "trace_rows": EXPECTED_TRACE_ROWS, "band_energy_rows": len(band_rows),
            "band_comparison_rows": len(comparisons), "layout_band_summary_rows": len(layout_summary),
            "comparison_band_summary_rows": len(comparison_summary), "archived_20ms_parity_rows": len(parity_rows),
            "csv_read_back": readback, "expected": expected,
        },
        "validation": {
            "parseval_relative_tolerance": PARSEVAL_RELATIVE_TOLERANCE,
            "max_parseval_relative_error": max_parseval_rel,
            "max_parseval_absolute_error_v2_samples": max_parseval_abs,
            "archived_20ms_absolute_tolerance_pct_points": tail.ARCHIVED_PARITY_ABSOLUTE_TOLERANCE_PCT_POINTS,
            "max_archived_20ms_absolute_delta_pct_points": max_parity_abs,
            "max_archived_20ms_relative_delta_pct": max_parity_rel,
        },
        "runtime": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "neuron": __import__("neuron").__version__, "wall_seconds": time.perf_counter() - started,
        },
        "scientific_limits": [
            "Exact finite-window decomposition of simulated output-error samples, not a frequency-response reconstruction.",
            "DFT frequency resolution changes with the observation window.",
            "Only two individual passive linear-RC morphologies are included; they are not populations.",
            "Large ratios can arise when seven-port band errors are very small; absolute band NRMSE and energy shares are retained.",
            "Full Hines remains canonical. No production solver code or defaults are changed.",
            "No active-neuron, synaptic, plasticity or biological validation is claimed.",
        ],
    }
    (results_dir / f"{stem}_report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "exact_coverage": report["exact_coverage"],
                      "validation": report["validation"], "runtime": report["runtime"]},
                     indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
