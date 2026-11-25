#!/usr/bin/env python3
"""Paired basal/apical q25 effect and interaction analysis for the four-layout ablation.

This is post-processing only. It does not rebuild PRIMA models or alter the
primary numerical runner. Every comparison is paired by morphology, passive
scenario, source, output SWC node, pulse width and observation window.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

RESULT_STEM = "prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25"
LAYOUTS = ("seven", "eight_basal_q25", "eight_apical_q25", "nine_both_q25")
CANDIDATES = LAYOUTS[1:]
EXPECTED_METRIC_ROWS = 12096
EXPECTED_COMPARISON_ROWS = 9072
EXPECTED_BASE_KEYS = 3024
EXPECTED_SOURCE_SUMMARY_ROWS = 1008
EXPECTED_MORPHOLOGY_SUMMARY_ROWS = 168
EXPECTED_INTERACTION_ROWS = 168

# value, unit, interpretation
METRICS = {
    "continuous_ac_error_pct": (
        "continuous_ac_zoh_weighted_error_pct", "percent",
        "Continuous-time resolvent error with the declared ZOH input weighting",
    ),
    "continuous_ac_error_norm_v_s": (
        "continuous_ac_weighted_error_norm_v_s", "V·s",
        "Absolute weighted continuous-AC error norm",
    ),
    "discrete_be_error_pct": (
        "discrete_be_periodic_transfer_error_pct", "percent",
        "Discrete backward-Euler periodic-transfer error",
    ),
    "discrete_be_error_norm_v": (
        "discrete_be_error_norm_v", "V",
        "Absolute weighted discrete backward-Euler error norm",
    ),
    "canonical_transient_nrmse_pct": (
        "finite_transient_nrmse_pct", "percent",
        "Canonical absolute-voltage finite-window transient NRMSE",
    ),
    "perturbation_transient_nrmse_pct": (
        "perturbation_coordinate_transient_nrmse_pct", "percent",
        "Numerically stable perturbation-coordinate finite-window transient NRMSE",
    ),
    "finite_dft_error_norm_v_samples": (
        "finite_error_dft_norm_v_samples", "V·samples",
        "Absolute finite-record DFT error norm after the terminal-state correction",
    ),
}

BASE_KEY_FIELDS = (
    "morphology", "parameter_scenario", "source_name", "output_swc_id",
    "pulse_width_ms", "window_ms",
)
COMPARISON_RATIO_FIELDS = {
    "continuous_ac_error_pct": "candidate_over_seven_continuous_ac_ratio",
    "discrete_be_error_pct": "candidate_over_seven_discrete_be_ratio",
    "canonical_transient_nrmse_pct": "candidate_over_seven_transient_nrmse_ratio",
    "perturbation_transient_nrmse_pct": (
        "candidate_over_seven_perturbation_coordinate_transient_nrmse_ratio"
    ),
}


def _number(row: dict[str, str], field: str) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"missing or invalid numeric field {field!r}") from exc
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{field!r} must be finite and non-negative, got {value!r}")
    return value


def _key(row: dict[str, Any]) -> tuple[str, str, str, int, float, float]:
    return (
        str(row["morphology"]),
        str(row["parameter_scenario"]),
        str(row["source_name"]),
        int(row["output_swc_id"]),
        float(row["pulse_width_ms"]),
        float(row["window_ms"]),
    )


def median(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        raise ValueError("cannot summarize an empty value collection")
    return float(statistics.median(materialized))


def percentile(values: Iterable[float], fraction: float) -> float:
    """Linearly interpolated percentile with a closed [0, 1] probability."""
    data = sorted(float(x) for x in values)
    if not data:
        raise ValueError("cannot summarize an empty value collection")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("percentile fraction must lie in [0, 1]")
    position = (len(data) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[lower]
    weight = position - lower
    return data[lower] * (1.0 - weight) + data[upper] * weight


def metric_contrasts(
    seven: float, basal: float, apical: float, combined: float,
) -> dict[str, float | None]:
    """Return paired main-effect deltas and two descriptive interaction contrasts.

    The additive contrast is E_both - E_basal - E_apical + E_seven.
    The multiplicative contrast is E_both*E_seven/(E_basal*E_apical).
    A multiplicative value above one means the combined error is above the
    no-interaction prediction on a log-error scale. These are numerical
    contrasts, not causal or biological interaction effects.
    """
    values = (seven, basal, apical, combined)
    if any(not math.isfinite(x) or x < 0.0 for x in values):
        raise ValueError("all four errors must be finite and non-negative")
    result: dict[str, float | None] = {
        "basal_delta_vs_seven": basal - seven,
        "apical_delta_vs_seven": apical - seven,
        "combined_delta_vs_seven": combined - seven,
        "additive_interaction_delta": combined - basal - apical + seven,
        "multiplicative_interaction_ratio": None,
        "log_multiplicative_interaction": None,
    }
    if seven > 0.0 and basal > 0.0 and apical > 0.0 and combined > 0.0:
        log_ratio = (
            math.log(combined) + math.log(seven)
            - math.log(basal) - math.log(apical)
        )
        result["log_multiplicative_interaction"] = log_ratio
        result["multiplicative_interaction_ratio"] = math.exp(log_ratio)
    return result


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def index_metric_rows(
    rows: list[dict[str, str]], *, enforce_expected: bool = True,
) -> dict[tuple, dict[str, Any]]:
    expected_count = EXPECTED_METRIC_ROWS if enforce_expected else len(rows)
    if len(rows) != expected_count:
        raise ValueError(f"case-metric rows {len(rows)} != {expected_count}")
    indexed: dict[tuple, dict[str, Any]] = {}
    for raw in rows:
        layout = raw.get("layout_id")
        if layout not in LAYOUTS:
            raise ValueError(f"unexpected layout_id: {layout!r}")
        key = _key(raw)
        full_key = key + (layout,)
        if full_key in indexed:
            raise ValueError(f"duplicate case-metric key: {full_key}")
        clean: dict[str, Any] = dict(raw)
        for metric_name, (field, _unit, _description) in METRICS.items():
            clean[metric_name] = _number(raw, field)
        indexed[full_key] = clean

    by_case: dict[tuple, set[str]] = defaultdict(set)
    for full_key in indexed:
        by_case[full_key[:-1]].add(full_key[-1])
    if enforce_expected and len(by_case) != EXPECTED_BASE_KEYS:
        raise ValueError(
            f"matched case keys {len(by_case)} != {EXPECTED_BASE_KEYS}"
        )
    for key, observed in by_case.items():
        if observed != set(LAYOUTS):
            raise ValueError(f"case {key} lacks an exact four-layout set: {observed}")
    return indexed


def validate_comparison_rows(
    rows: list[dict[str, str]],
    metric_index: dict[tuple, dict[str, Any]],
    *,
    enforce_expected: bool = True,
) -> None:
    expected_count = EXPECTED_COMPARISON_ROWS if enforce_expected else len(rows)
    if len(rows) != expected_count:
        raise ValueError(f"comparison rows {len(rows)} != {expected_count}")
    seen = set()
    for raw in rows:
        candidate = raw.get("candidate_layout")
        if candidate not in CANDIDATES:
            raise ValueError(f"unexpected candidate layout: {candidate!r}")
        key = _key(raw)
        pair_key = key + (candidate,)
        if pair_key in seen:
            raise ValueError(f"duplicate comparison key: {pair_key}")
        seen.add(pair_key)
        baseline = metric_index[key + ("seven",)]
        observed = metric_index[key + (candidate,)]
        for metric_name, field in COMPARISON_RATIO_FIELDS.items():
            ratio = _number(raw, field)
            expected_ratio = (
                observed[metric_name] / baseline[metric_name]
                if baseline[metric_name] > 0.0 else math.inf
            )
            if not math.isfinite(expected_ratio) or not math.isclose(
                ratio, expected_ratio, rel_tol=5e-8, abs_tol=1e-12
            ):
                raise ValueError(
                    f"comparison mismatch for {pair_key}/{metric_name}: "
                    f"{ratio} != {expected_ratio}"
                )
    if enforce_expected and len(seen) != EXPECTED_COMPARISON_ROWS:
        raise ValueError("comparison matrix does not cover every candidate layout")


def _metric_series(
    metric_index: dict[tuple, dict[str, Any]],
    base_keys: list[tuple],
    metric_name: str,
    candidate: str,
) -> tuple[list[float], list[float]]:
    baseline_values, candidate_values = [], []
    for key in base_keys:
        baseline_values.append(metric_index[key + ("seven",)][metric_name])
        candidate_values.append(metric_index[key + (candidate,)][metric_name])
    return baseline_values, candidate_values


def build_summaries(
    metric_index: dict[tuple, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build source-level, morphology-level and basal/apical interaction tables."""
    base_keys = sorted({key[:-1] for key in metric_index})
    source_groups: dict[tuple, list[tuple]] = defaultdict(list)
    morphology_groups: dict[tuple, list[tuple]] = defaultdict(list)
    interaction_groups: dict[tuple, list[tuple]] = defaultdict(list)

    for key in base_keys:
        morphology, scenario, source, output, pulse, window = key
        for candidate in CANDIDATES:
            source_groups[(morphology, candidate, source, pulse, window)].append(key)
            morphology_groups[(morphology, candidate, window)].append(key)
        interaction_groups[(morphology, source, pulse, window)].append(key)

    source_rows: list[dict[str, Any]] = []
    for group, keys in sorted(source_groups.items()):
        if len(keys) != 63:
            raise ValueError(f"source group lacks 9 scenarios x 7 outputs: {group}")
        morphology, candidate, source, pulse, window = group
        for metric_name, (_field, unit, description) in METRICS.items():
            base_values, candidate_values = _metric_series(
                metric_index, keys, metric_name, candidate
            )
            ratios = [
                c / b if b > 0.0 else math.inf
                for b, c in zip(base_values, candidate_values)
            ]
            deltas = [c - b for b, c in zip(base_values, candidate_values)]
            source_rows.append({
                "morphology": morphology,
                "candidate_layout": candidate,
                "source_name": source,
                "pulse_width_ms": pulse,
                "window_ms": window,
                "metric": metric_name,
                "unit": unit,
                "description": description,
                "paired_scenario_output_count": len(keys),
                "median_candidate_over_seven_ratio": (
                    median(ratios) if all(math.isfinite(x) for x in ratios) else ""
                ),
                "p90_candidate_over_seven_ratio": (
                    percentile(ratios, 0.90) if all(math.isfinite(x) for x in ratios) else ""
                ),
                "median_absolute_error_delta": median(deltas),
                "p90_absolute_error_delta": percentile(deltas, 0.90),
                "candidate_worse_pairs": sum(x > 0.0 for x in deltas),
                "candidate_better_pairs": sum(x < 0.0 for x in deltas),
                "candidate_tied_pairs": sum(x == 0.0 for x in deltas),
                "candidate_worse_fraction": sum(x > 0.0 for x in deltas) / len(deltas),
            })

    morphology_rows: list[dict[str, Any]] = []
    for group, keys in sorted(morphology_groups.items()):
        if len(keys) != 378:
            raise ValueError(
                f"morphology group lacks 9 scenarios x 3 sources x 2 pulses x 7 outputs: {group}"
            )
        morphology, candidate, window = group
        for metric_name, (_field, unit, description) in METRICS.items():
            base_values, candidate_values = _metric_series(
                metric_index, keys, metric_name, candidate
            )
            ratios = [
                c / b if b > 0.0 else math.inf
                for b, c in zip(base_values, candidate_values)
            ]
            deltas = [c - b for b, c in zip(base_values, candidate_values)]
            morphology_rows.append({
                "morphology": morphology,
                "candidate_layout": candidate,
                "window_ms": window,
                "metric": metric_name,
                "unit": unit,
                "description": description,
                "paired_scenario_source_pulse_output_count": len(keys),
                "median_candidate_over_seven_ratio": (
                    median(ratios) if all(math.isfinite(x) for x in ratios) else ""
                ),
                "p90_candidate_over_seven_ratio": (
                    percentile(ratios, 0.90) if all(math.isfinite(x) for x in ratios) else ""
                ),
                "median_absolute_error_delta": median(deltas),
                "p90_absolute_error_delta": percentile(deltas, 0.90),
                "candidate_worse_pairs": sum(x > 0.0 for x in deltas),
                "candidate_better_pairs": sum(x < 0.0 for x in deltas),
                "candidate_tied_pairs": sum(x == 0.0 for x in deltas),
                "candidate_worse_fraction": sum(x > 0.0 for x in deltas) / len(deltas),
            })

    interaction_rows: list[dict[str, Any]] = []
    for group, keys in sorted(interaction_groups.items()):
        if len(keys) != 63:
            raise ValueError(f"interaction group lacks 9 scenarios x 7 outputs: {group}")
        morphology, source, pulse, window = group
        for metric_name, (_field, unit, description) in METRICS.items():
            additive, multiplicative, log_multiplicative = [], [], []
            basal_deltas, apical_deltas, combined_deltas = [], [], []
            valid_log = 0
            for key in keys:
                values = {
                    layout: metric_index[key + (layout,)][metric_name]
                    for layout in LAYOUTS
                }
                contrast = metric_contrasts(
                    values["seven"], values["eight_basal_q25"],
                    values["eight_apical_q25"], values["nine_both_q25"],
                )
                basal_deltas.append(float(contrast["basal_delta_vs_seven"]))
                apical_deltas.append(float(contrast["apical_delta_vs_seven"]))
                combined_deltas.append(float(contrast["combined_delta_vs_seven"]))
                additive.append(float(contrast["additive_interaction_delta"]))
                log_value = contrast["log_multiplicative_interaction"]
                multiplier = contrast["multiplicative_interaction_ratio"]
                if log_value is not None and multiplier is not None:
                    log_multiplicative.append(float(log_value))
                    multiplicative.append(float(multiplier))
                    valid_log += 1
            interaction_rows.append({
                "morphology": morphology,
                "source_name": source,
                "pulse_width_ms": pulse,
                "window_ms": window,
                "metric": metric_name,
                "unit": unit,
                "description": description,
                "paired_scenario_output_count": len(keys),
                "median_basal_delta_vs_seven": median(basal_deltas),
                "median_apical_delta_vs_seven": median(apical_deltas),
                "median_combined_delta_vs_seven": median(combined_deltas),
                "median_additive_interaction_delta": median(additive),
                "p90_additive_interaction_delta": percentile(additive, 0.90),
                "multiplicative_interaction_valid_pairs": valid_log,
                "median_log_multiplicative_interaction": (
                    median(log_multiplicative) if valid_log else ""
                ),
                "median_multiplicative_interaction_ratio": (
                    math.exp(median(log_multiplicative)) if valid_log else ""
                ),
                "p90_multiplicative_interaction_ratio": (
                    percentile(multiplicative, 0.90) if valid_log else ""
                ),
                "interpretation": (
                    "ratio > 1: combined error exceeds the multiplicative no-interaction "
                    "prediction; ratio < 1: combined error is below it"
                ),
            })

    if len(source_rows) != EXPECTED_SOURCE_SUMMARY_ROWS:
        raise ValueError(f"source summaries {len(source_rows)} != {EXPECTED_SOURCE_SUMMARY_ROWS}")
    if len(morphology_rows) != EXPECTED_MORPHOLOGY_SUMMARY_ROWS:
        raise ValueError(
            f"morphology summaries {len(morphology_rows)} != {EXPECTED_MORPHOLOGY_SUMMARY_ROWS}"
        )
    if len(interaction_rows) != EXPECTED_INTERACTION_ROWS:
        raise ValueError(f"interaction summaries {len(interaction_rows)} != {EXPECTED_INTERACTION_ROWS}")
    return source_rows, morphology_rows, interaction_rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty summary: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(results_dir: Path, stem: str = RESULT_STEM) -> dict[str, Any]:
    metric_path = results_dir / f"{stem}_case_metrics.csv"
    comparison_path = results_dir / f"{stem}_layout_vs_seven_comparisons.csv"
    metric_rows = _read_csv(metric_path)
    comparison_rows = _read_csv(comparison_path)
    metric_index = index_metric_rows(metric_rows)
    validate_comparison_rows(comparison_rows, metric_index)
    source_rows, morphology_rows, interaction_rows = build_summaries(metric_index)

    output_paths = {
        "source_summary": results_dir / f"{stem}_posthoc_source_summary.csv",
        "morphology_summary": results_dir / f"{stem}_posthoc_morphology_summary.csv",
        "interaction_summary": results_dir / f"{stem}_posthoc_interaction_summary.csv",
    }
    _write_csv(output_paths["source_summary"], source_rows)
    _write_csv(output_paths["morphology_summary"], morphology_rows)
    _write_csv(output_paths["interaction_summary"], interaction_rows)

    report = {
        "schema_version": 1,
        "status": "passed",
        "analysis": "paired basal-q25, apical-q25 and combined q25 layout contrasts",
        "input": {
            "case_metrics_rows": len(metric_rows),
            "comparison_rows": len(comparison_rows),
            "case_metrics_sha256": _sha256(metric_path),
            "comparison_sha256": _sha256(comparison_path),
        },
        "coverage": {
            "matched_case_keys": len(metric_index) // len(LAYOUTS),
            "source_summary_rows": len(source_rows),
            "morphology_summary_rows": len(morphology_rows),
            "interaction_summary_rows": len(interaction_rows),
        },
        "layout_semantics": {
            "baseline": "seven",
            "basal_only": "eight_basal_q25",
            "apical_only": "eight_apical_q25",
            "combined": "nine_both_q25",
        },
        "interaction_definition": {
            "additive": "E_both - E_basal - E_apical + E_seven",
            "multiplicative_ratio": "E_both * E_seven / (E_basal * E_apical)",
            "interpretation": (
                "Descriptive paired numerical contrasts only. They do not establish "
                "causality, biological interaction or population-level generalization."
            ),
        },
        "metrics": {
            name: {"field": details[0], "unit": details[1], "description": details[2]}
            for name, details in METRICS.items()
        },
        "outputs": {name: path.name for name, path in output_paths.items()},
        "limits": [
            "Four individual morphology reconstructions are not a population sample.",
            "The analysis inherits the passive linear-RC and declared numerical-protocol limits of the primary experiment.",
            "Ratios are shown with absolute deltas because near-zero baseline residuals can make ratios unstable.",
            "The multiplicative interaction ratio is a log-error-scale descriptor, not a causal or biological interaction effect.",
        ],
    }
    report_path = results_dir / f"{stem}_posthoc_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
    )
    parser.add_argument("--stem", default=RESULT_STEM)
    args = parser.parse_args()
    report = run(args.results_dir, args.stem)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
