#!/usr/bin/env python3
"""Localize Krylov-prefix source/output transfer residuals by AC frequency.

This deterministic post-processing consumes the verified 95,256-row transfer
matrix from the preceding audit. It does not rerun PRIMA or change production.
Rectangular pulse spectral weights are reported only at sampled frequencies;
they are not a continuous-frequency quadrature.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

RESULTS = Path(__file__).parents[1] / "results"
INPUT = RESULTS / "prima_q25_krylov_transfer_stages_cross_morphology_2026-11-24_frequency.csv"
RESULT_STEM = "prima_q25_transfer_frequency_localization_2026-11-24"
MORPHOLOGIES = (
    "NMO_163775_Peng_mouse_Control",
    "NMO_107159_Tamas_human_pyramidal_Control",
)
LAYOUTS = ("seven", "eight_basal_q25", "eight_apical_q25", "nine_both_q25")
CANDIDATES = ("eight_basal_q25", "eight_apical_q25", "nine_both_q25")
ORDERS = (112, 168)
STAGE_NAMES = ("seed", "krylov_round_1", "krylov_round_2", "krylov_round_3")
STAGE_BY_ORDER = {112: ("seed", "krylov_round_1", "krylov_round_2"),
                  168: STAGE_NAMES}
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 100.0, 300.0, 1000.0, 3000.0, 6000.0, 10000.0)
SOURCES = ("soma", "basal_q75", "apical_q75")
PULSE_WIDTHS_MS = (2.0, 10.0)
SHARED_OUTPUTS = {
    "NMO_163775_Peng_mouse_Control": {
        1: "soma", 144: "basal_q75", 3926: "apical_q75",
        3948: "apical_q90", 4104: "apical_q50",
        4180: "basal_q50", 40: "basal_q90",
    },
    "NMO_107159_Tamas_human_pyramidal_Control": {
        1: "soma", 6363: "basal_q75", 4735: "apical_q75",
        5564: "basal_q50", 7023: "basal_q90",
        4301: "apical_q50", 4623: "apical_q90",
    },
}
SCENARIOS = (
    "nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
    "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20",
)
EXPECTED_INPUT_ROWS = 95256
EXPECTED_OUTPUT_FREQUENCY_ROWS = 10584
EXPECTED_SOURCE_FREQUENCY_ROWS = 1512
EXPECTED_VS_SEVEN_ROWS = 7938
EXPECTED_VS_SEVEN_SOURCE_ROWS = 1134
EXPECTED_PULSE_WEIGHT_ROWS = 18
REQUIRED_COLUMNS = {
    "morphology", "layout_id", "basis_order", "stage", "round_index",
    "basis_dimension", "parameter_scenario", "source_name", "output_swc_id",
    "output_role", "frequency_hz", "absolute_error_ohm",
    "relative_absolute_error_pct",
}
PORT_COUNT = {"seven": 7, "eight_basal_q25": 8,
              "eight_apical_q25": 8, "nine_both_q25": 9}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "input_frequency_rows": EXPECTED_INPUT_ROWS,
        "output_frequency_rows": EXPECTED_OUTPUT_FREQUENCY_ROWS,
        "source_frequency_rows": EXPECTED_SOURCE_FREQUENCY_ROWS,
        "vs_seven_output_frequency_rows": EXPECTED_VS_SEVEN_ROWS,
        "vs_seven_source_frequency_rows": EXPECTED_VS_SEVEN_SOURCE_ROWS,
        "pulse_spectrum_weight_rows": EXPECTED_PULSE_WEIGHT_ROWS,
    }


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    if lo == hi:
        return ordered[lo]
    frac = position - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def load_frequency_rows() -> list[dict[str, Any]]:
    require(INPUT.is_file(), f"missing upstream transfer-frequency matrix: {INPUT}")
    rows = []
    with INPUT.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None, "missing AC frequency CSV header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        require(not missing, f"missing AC frequency columns: {sorted(missing)}")
        for line_number, raw in enumerate(reader, start=2):
            row = dict(raw)
            row["basis_order"] = int(row["basis_order"])
            row["round_index"] = int(row["round_index"])
            row["basis_dimension"] = int(row["basis_dimension"])
            row["output_swc_id"] = int(row["output_swc_id"])
            row["frequency_hz"] = float(row["frequency_hz"])
            row["absolute_error_ohm"] = float(row["absolute_error_ohm"])
            row["relative_absolute_error_pct"] = float(row["relative_absolute_error_pct"])
            require(row["morphology"] in MORPHOLOGIES,
                    f"row {line_number}: unknown morphology")
            require(row["layout_id"] in LAYOUTS, f"row {line_number}: unknown layout")
            require(row["basis_order"] in ORDERS, f"row {line_number}: unknown order")
            require(row["stage"] in STAGE_BY_ORDER[row["basis_order"]],
                    f"row {line_number}: stage does not match order")
            require(row["source_name"] in SOURCES, f"row {line_number}: unknown source")
            require(row["parameter_scenario"] in SCENARIOS,
                    f"row {line_number}: unknown passive scenario")
            require(row["frequency_hz"] in FREQUENCIES_HZ,
                    f"row {line_number}: unknown frequency")
            require(row["output_swc_id"] in SHARED_OUTPUTS[row["morphology"]],
                    f"row {line_number}: output SWC node is not in the pinned shared set")
            require(row["output_role"] == SHARED_OUTPUTS[row["morphology"]][row["output_swc_id"]],
                    f"row {line_number}: output role does not match the pinned SWC node")
            require(math.isfinite(row["absolute_error_ohm"]) and row["absolute_error_ohm"] >= 0,
                    f"row {line_number}: invalid absolute transfer error")
            require(math.isfinite(row["relative_absolute_error_pct"]) and row["relative_absolute_error_pct"] >= 0,
                    f"row {line_number}: invalid relative transfer error")
            rows.append(row)
    require(len(rows) == EXPECTED_INPUT_ROWS,
            f"input rows {len(rows)} != {EXPECTED_INPUT_ROWS}")
    return rows


def group_output_frequency(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"], row["stage"],
            row["round_index"], row["basis_dimension"], row["source_name"],
            row["output_swc_id"], row["output_role"], row["frequency_hz"],
        )
        groups[key].append(row)
    output = []
    for key, subset in sorted(groups.items()):
        require(len(subset) == len(SCENARIOS),
                f"scenario coverage mismatch for output-frequency group {key}")
        relative = [float(x["relative_absolute_error_pct"]) for x in subset]
        absolute = [float(x["absolute_error_ohm"]) for x in subset]
        output.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "stage": key[3], "round_index": key[4], "basis_dimension": key[5],
            "source_name": key[6], "output_swc_id": key[7], "output_role": key[8],
            "frequency_hz": key[9], "parameter_scenarios": len(subset),
            "median_relative_transfer_error_pct": statistics.median(relative),
            "p90_relative_transfer_error_pct": percentile(relative, 0.90),
            "max_relative_transfer_error_pct": max(relative),
            "median_absolute_transfer_error_ohm": statistics.median(absolute),
            "max_absolute_transfer_error_ohm": max(absolute),
        })
    require(len(output) == EXPECTED_OUTPUT_FREQUENCY_ROWS,
            f"output-frequency rows {len(output)} != {EXPECTED_OUTPUT_FREQUENCY_ROWS}")
    return output


def group_source_frequency(output_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in output_rows:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"], row["stage"],
            row["round_index"], row["basis_dimension"], row["source_name"],
            row["frequency_hz"],
        )
        groups[key].append(row)
    output = []
    for key, subset in sorted(groups.items()):
        require(len(subset) == 7, f"source-frequency group must contain seven outputs: {key}")
        values = [float(x["median_relative_transfer_error_pct"]) for x in subset]
        output.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "stage": key[3], "round_index": key[4], "basis_dimension": key[5],
            "source_name": key[6], "frequency_hz": key[7],
            "shared_outputs": len(subset),
            "median_output_relative_error_pct": statistics.median(values),
            "p90_output_relative_error_pct": percentile(values, 0.90),
            "max_output_relative_error_pct": max(values),
        })
    require(len(output) == EXPECTED_SOURCE_FREQUENCY_ROWS,
            f"source-frequency rows {len(output)} != {EXPECTED_SOURCE_FREQUENCY_ROWS}")
    return output


def compare_with_seven(output_rows: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    index = {
        (
            r["morphology"], r["layout_id"], r["basis_order"], r["stage"],
            r["source_name"], r["output_swc_id"], r["frequency_hz"],
        ): r for r in output_rows
    }
    paired = []
    for candidate in output_rows:
        layout = candidate["layout_id"]
        if layout == "seven":
            continue
        key = (
            candidate["morphology"], "seven", candidate["basis_order"],
            candidate["stage"], candidate["source_name"],
            candidate["output_swc_id"], candidate["frequency_hz"],
        )
        baseline = index.get(key)
        require(baseline is not None, f"missing seven-port transfer group for {key}")
        denominator = float(baseline["median_relative_transfer_error_pct"])
        numerator = float(candidate["median_relative_transfer_error_pct"])
        require(denominator > 0.0, f"zero seven-port denominator for {key}")
        paired.append({
            "morphology": candidate["morphology"],
            "layout_id": layout,
            "basis_order": candidate["basis_order"],
            "stage": candidate["stage"],
            "round_index": candidate["round_index"],
            "source_name": candidate["source_name"],
            "output_swc_id": candidate["output_swc_id"],
            "output_role": candidate["output_role"],
            "frequency_hz": candidate["frequency_hz"],
            "candidate_relative_error_pct": numerator,
            "seven_relative_error_pct": denominator,
            "candidate_over_seven_ratio": numerator / denominator,
            "candidate_max_absolute_error_ohm": candidate["max_absolute_transfer_error_ohm"],
            "seven_max_absolute_error_ohm": baseline["max_absolute_transfer_error_ohm"],
        })
    require(len(paired) == EXPECTED_VS_SEVEN_ROWS,
            f"paired output-frequency rows {len(paired)} != {EXPECTED_VS_SEVEN_ROWS}")

    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in paired:
        key = (
            row["morphology"], row["layout_id"], row["basis_order"], row["stage"],
            row["round_index"], row["source_name"], row["frequency_hz"],
        )
        groups[key].append(row)
    summary = []
    for key, subset in sorted(groups.items()):
        require(len(subset) == 7, f"paired source-frequency group must contain seven outputs: {key}")
        ratios = [float(x["candidate_over_seven_ratio"]) for x in subset]
        summary.append({
            "morphology": key[0], "layout_id": key[1], "basis_order": key[2],
            "stage": key[3], "round_index": key[4], "source_name": key[5],
            "frequency_hz": key[6], "shared_outputs": len(subset),
            "median_candidate_over_seven_ratio": statistics.median(ratios),
            "p90_candidate_over_seven_ratio": percentile(ratios, 0.90),
            "worse_output_groups": sum(x > 1.0 for x in ratios),
            "better_output_groups": sum(x < 1.0 for x in ratios),
        })
    require(len(summary) == EXPECTED_VS_SEVEN_SOURCE_ROWS,
            f"paired source-frequency summary rows {len(summary)} != {EXPECTED_VS_SEVEN_SOURCE_ROWS}")
    return paired, summary


def pulse_spectrum_rows() -> list[dict[str, Any]]:
    output = []
    for width_ms in PULSE_WIDTHS_MS:
        duration_s = width_ms * 1e-3
        for frequency_hz in FREQUENCIES_HZ:
            amplitude = abs(float(np.sinc(frequency_hz * duration_s)))
            output.append({
                "pulse_width_ms": width_ms,
                "frequency_hz": frequency_hz,
                "normalized_rectangular_pulse_spectral_amplitude": amplitude,
                "normalized_rectangular_pulse_spectral_power": amplitude * amplitude,
                "interpretation": "sampled continuous-time rectangular-pulse spectrum; not a frequency-grid quadrature weight",
            })
    require(len(output) == EXPECTED_PULSE_WEIGHT_ROWS,
            "pulse spectrum sample coverage mismatch")
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = load_frequency_rows()
    output_rows = group_output_frequency(rows)
    source_rows = group_source_frequency(output_rows)
    paired_rows, paired_summary = compare_with_seven(output_rows)
    pulse_rows = pulse_spectrum_rows()

    # Keep a concise worst list per frequency and a globally ranked 100-row table.
    worst = sorted(
        output_rows,
        key=lambda x: float(x["max_relative_transfer_error_pct"]),
        reverse=True,
    )[:100]

    write_csv(RESULTS / f"{RESULT_STEM}_by_output_frequency.csv", output_rows)
    write_csv(RESULTS / f"{RESULT_STEM}_by_source_frequency.csv", source_rows)
    write_csv(RESULTS / f"{RESULT_STEM}_vs_seven_by_output_frequency.csv", paired_rows)
    write_csv(RESULTS / f"{RESULT_STEM}_vs_seven_by_source_frequency.csv", paired_summary)
    write_csv(RESULTS / f"{RESULT_STEM}_pulse_spectrum_samples.csv", pulse_rows)
    write_csv(RESULTS / f"{RESULT_STEM}_worst_output_frequency_groups.csv", worst)

    report = {
        "schema_version": 1,
        "status": "prima_q25_transfer_frequency_localization_passed",
        "source_input": str(INPUT),
        "exact_coverage": {
            "input_frequency_rows": len(rows),
            "output_frequency_rows": len(output_rows),
            "source_frequency_rows": len(source_rows),
            "vs_seven_output_frequency_rows": len(paired_rows),
            "vs_seven_source_frequency_rows": len(paired_summary),
            "pulse_spectrum_weight_rows": len(pulse_rows),
            "worst_output_frequency_groups": len(worst),
            "expected": expected_counts(),
        },
        "frequency_grid_hz": list(FREQUENCIES_HZ),
        "rectangular_pulse_spectrum_note": (
            "The normalized sinc amplitude/power values describe the continuous-time "
            "rectangular pulse spectrum only at sampled frequencies. The nine-point "
            "grid is sparse/log-spaced and is not integrated as a continuous spectrum."
        ),
        "scientific_limits": [
            "This post-processes an already validated passive linear-RC AC transfer matrix; it does not rerun PRIMA.",
            "Complex transfer residuals are AC metrics and are not identical to time-domain pulse NRMSE.",
            "Relative error ratios use seven-port error as denominator and may amplify small denominators; absolute transfer error remains in the output-level table.",
            "Pulse spectral samples are descriptive only and are not a quadrature or a predicted pulse error.",
            "Only two individual morphologies are compared; no biological or population-level inference is made.",
            "Full Hines remains canonical; production code and defaults are unchanged.",
        ],
    }
    (RESULTS / f"{RESULT_STEM}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
