#!/usr/bin/env python3
"""Run a four-layout PRIMA basis-order convergence sweep around order 168.

The already completed order-168 matrix is the reference point. This driver
replays orders 112, 224 and 280 under the identical morphology, port, source,
passive-scenario, timestep and finite-window protocol, then runs the paired
basal/apical post-analysis for every order. Large frequency CSVs are retained
for Actions artifacts and are intentionally not intended for Git commits.
"""
from __future__ import annotations

import csv
import gc
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

RESEARCH = Path(__file__).resolve().parent
AMSN_ROOT = RESEARCH.parent
RESULTS_DIR = AMSN_ROOT / "results"

REFERENCE_ORDER = 168
ORDERS_TO_RUN = (112, 224)
ALL_ORDERS = (112, 168, 224)
BASE_RESULT_STEM = "prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25"
ORDER_SWEEP_STEM = "prima_q25_four_morphology_four_layout_basis_order_sweep_2026-11-25"

EXPECTED_CASE_ROWS = 12096
EXPECTED_COMPARISON_ROWS = 9072
EXPECTED_SOURCE_POSTHOC_ROWS = 1008
EXPECTED_MORPHOLOGY_POSTHOC_ROWS = 168
EXPECTED_INTERACTION_POSTHOC_ROWS = 336


def result_stem_for_order(order: int) -> str:
    if isinstance(order, bool) or not isinstance(order, int) or order <= 0:
        raise ValueError("basis order must be a positive integer")
    if order == REFERENCE_ORDER:
        return BASE_RESULT_STEM
    if order not in ORDERS_TO_RUN:
        raise ValueError(f"basis order {order} is not in the declared sweep")
    return f"{ORDER_SWEEP_STEM}_order_{order}"


def validate_order_grid(
    orders_to_run: tuple[int, ...] = ORDERS_TO_RUN,
    reference_order: int = REFERENCE_ORDER,
) -> tuple[int, ...]:
    values = tuple(orders_to_run)
    if not values or any(isinstance(x, bool) or not isinstance(x, int) or x <= 0 for x in values):
        raise ValueError("sweep orders must be a non-empty tuple of positive integers")
    if len(values) != len(set(values)):
        raise ValueError("sweep orders must be unique")
    if reference_order in values:
        raise ValueError("the existing reference order must not be recomputed")
    if tuple(sorted(values)) != values:
        raise ValueError("sweep orders must be in ascending order")
    return tuple(sorted(set(values + (reference_order,))))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty convergence table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _posthoc_paths(stem: str) -> dict[str, Path]:
    return {
        "source": RESULTS_DIR / f"{stem}_posthoc_source_summary.csv",
        "morphology": RESULTS_DIR / f"{stem}_posthoc_morphology_summary.csv",
        "interaction": RESULTS_DIR / f"{stem}_posthoc_interaction_summary.csv",
        "report": RESULTS_DIR / f"{stem}_posthoc_report.json",
    }


def run() -> dict[str, Any]:
    validate_order_grid()
    required_reference_files = (
        RESULTS_DIR / f"{BASE_RESULT_STEM}_case_metrics.csv",
        RESULTS_DIR / f"{BASE_RESULT_STEM}_layout_vs_seven_comparisons.csv",
        RESULTS_DIR / f"{BASE_RESULT_STEM}_report.json",
    )
    missing = [str(path) for path in required_reference_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "the validated order-168 reference matrix must be committed before "
            f"the convergence sweep starts; missing: {missing}"
        )

    runner = _load_module(
        "q25_four_layout_order_sweep_runner",
        RESEARCH / "analyze_prima_q25_four_morphology_four_layout_boundary_ablation.py",
    )
    posthoc = _load_module(
        "q25_four_layout_order_sweep_posthoc",
        RESEARCH / "summarize_prima_q25_four_layout_interactions.py",
    )

    reference_report = json.loads(required_reference_files[2].read_text(encoding="utf-8"))
    if reference_report.get("status") != "prima_q25_four_morphology_four_layout_boundary_ablation_passed":
        raise ValueError("order-168 reference report does not declare a passed numerical run")
    if int(reference_report.get("scope", {}).get("basis_order", -1)) != REFERENCE_ORDER:
        raise ValueError("order-168 reference report has an unexpected basis order")
    if int(reference_report.get("exact_coverage", {}).get("case_metric_rows", -1)) != EXPECTED_CASE_ROWS:
        raise ValueError("order-168 reference case-metric coverage is incomplete")
    if int(reference_report.get("exact_coverage", {}).get("layout_vs_seven_comparison_rows", -1)) != EXPECTED_COMPARISON_ROWS:
        raise ValueError("order-168 reference matched-comparison coverage is incomplete")

    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    summary_sources: list[dict[str, Any]] = []
    summary_morphologies: list[dict[str, Any]] = []
    summary_interactions: list[dict[str, Any]] = []

    # The reference is re-summarized from its committed raw paired rows so all
    # orders use one identical post-analysis implementation.
    reference_posthoc = posthoc.run(RESULTS_DIR, BASE_RESULT_STEM)
    reference_paths = _posthoc_paths(BASE_RESULT_STEM)
    for category, target in (
        ("source", summary_sources),
        ("morphology", summary_morphologies),
        ("interaction", summary_interactions),
    ):
        rows = _read_csv(reference_paths[category])
        for row in rows:
            target.append({"basis_order": REFERENCE_ORDER, **row})
    results.append({
        "basis_order": REFERENCE_ORDER,
        "result_stem": BASE_RESULT_STEM,
        "source": "previously validated four-layout run",
        "status": "reference_loaded",
        "case_metrics_rows": EXPECTED_CASE_ROWS,
        "comparison_rows": EXPECTED_COMPARISON_ROWS,
        "posthoc_source_rows": reference_posthoc["coverage"]["source_summary_rows"],
        "posthoc_morphology_rows": reference_posthoc["coverage"]["morphology_summary_rows"],
        "posthoc_interaction_rows": reference_posthoc["coverage"]["interaction_summary_rows"],
        "case_metrics_sha256": reference_posthoc["input"]["case_metrics_sha256"],
        "comparisons_sha256": reference_posthoc["input"]["comparison_sha256"],
        "runtime_seconds": reference_report.get("runtime", {}).get("wall_seconds"),
        "max_finite_identity_relative_error": reference_report.get("validation", {}).get("max_finite_identity_relative_error"),
        "max_basis_orthogonality_error": max(
            float(item["basis_orthogonality_max_abs"])
            for item in reference_report["reproducibility_diagnostics"]["basis_models"]
        ),
        "unique_basis_hashes": len({
            item["basis_sha256"]
            for item in reference_report["reproducibility_diagnostics"]["basis_models"]
        }),
    })

    for order in ORDERS_TO_RUN:
        stem = result_stem_for_order(order)
        order_started = time.perf_counter()
        try:
            runner.BASIS_ORDER = order
            runner.tail.BASIS_ORDER = order
            runner.RESULT_STEM = stem
            runner.main()

            report_path = RESULTS_DIR / f"{stem}_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report.get("status") != "prima_q25_four_morphology_four_layout_boundary_ablation_passed":
                raise ValueError(f"order {order}: numerical runner did not pass")
            if int(report.get("scope", {}).get("basis_order", -1)) != order:
                raise ValueError(f"order {order}: report basis_order mismatch")
            coverage = report.get("exact_coverage", {})
            if int(coverage.get("case_metric_rows", -1)) != EXPECTED_CASE_ROWS:
                raise ValueError(f"order {order}: incomplete case metrics")
            if int(coverage.get("layout_vs_seven_comparison_rows", -1)) != EXPECTED_COMPARISON_ROWS:
                raise ValueError(f"order {order}: incomplete matched comparisons")

            posthoc_report = posthoc.run(RESULTS_DIR, stem)
            paths = _posthoc_paths(stem)
            expected_posthoc = {
                "source": EXPECTED_SOURCE_POSTHOC_ROWS,
                "morphology": EXPECTED_MORPHOLOGY_POSTHOC_ROWS,
                "interaction": EXPECTED_INTERACTION_POSTHOC_ROWS,
            }
            for category, target in (
                ("source", summary_sources),
                ("morphology", summary_morphologies),
                ("interaction", summary_interactions),
            ):
                rows = _read_csv(paths[category])
                if len(rows) != expected_posthoc[category]:
                    raise ValueError(
                        f"order {order}: {category} post-analysis rows "
                        f"{len(rows)} != {expected_posthoc[category]}"
                    )
                for row in rows:
                    target.append({"basis_order": order, **row})

            basis_models = report["reproducibility_diagnostics"]["basis_models"]
            results.append({
                "basis_order": order,
                "result_stem": stem,
                "source": "fresh finite-window four-layout rerun",
                "status": "passed",
                "case_metrics_rows": int(coverage["case_metric_rows"]),
                "comparison_rows": int(coverage["layout_vs_seven_comparison_rows"]),
                "posthoc_source_rows": posthoc_report["coverage"]["source_summary_rows"],
                "posthoc_morphology_rows": posthoc_report["coverage"]["morphology_summary_rows"],
                "posthoc_interaction_rows": posthoc_report["coverage"]["interaction_summary_rows"],
                "case_metrics_sha256": posthoc_report["input"]["case_metrics_sha256"],
                "comparisons_sha256": posthoc_report["input"]["comparison_sha256"],
                "runtime_seconds": report.get("runtime", {}).get("wall_seconds"),
                "max_finite_identity_relative_error": report.get("validation", {}).get("max_finite_identity_relative_error"),
                "max_basis_orthogonality_error": max(
                    float(item["basis_orthogonality_max_abs"]) for item in basis_models
                ),
                "unique_basis_hashes": len({item["basis_sha256"] for item in basis_models}),
                "elapsed_driver_seconds": time.perf_counter() - order_started,
            })
        except Exception as exc:
            results.append({
                "basis_order": order,
                "result_stem": stem,
                "source": "fresh finite-window four-layout rerun",
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_driver_seconds": time.perf_counter() - order_started,
            })
        finally:
            gc.collect()

    # The per-order summaries are compact and can be committed to Git.
    source_path = RESULTS_DIR / f"{ORDER_SWEEP_STEM}_source_summary.csv"
    morphology_path = RESULTS_DIR / f"{ORDER_SWEEP_STEM}_morphology_summary.csv"
    interaction_path = RESULTS_DIR / f"{ORDER_SWEEP_STEM}_interaction_summary.csv"
    if summary_sources:
        _write_csv(source_path, summary_sources)
    if summary_morphologies:
        _write_csv(morphology_path, summary_morphologies)
    if summary_interactions:
        _write_csv(interaction_path, summary_interactions)

    passed_orders = sorted(
        int(item["basis_order"])
        for item in results
        if item["status"] in {"passed", "reference_loaded"}
    )
    failed_orders = [
        int(item["basis_order"])
        for item in results
        if item["status"] == "failed"
    ]
    combined_expected = {
        "source_summary_rows": len(passed_orders) * EXPECTED_SOURCE_POSTHOC_ROWS,
        "morphology_summary_rows": len(passed_orders) * EXPECTED_MORPHOLOGY_POSTHOC_ROWS,
        "interaction_summary_rows": len(passed_orders) * EXPECTED_INTERACTION_POSTHOC_ROWS,
    }
    combined_actual = {
        "source_summary_rows": len(summary_sources),
        "morphology_summary_rows": len(summary_morphologies),
        "interaction_summary_rows": len(summary_interactions),
    }
    for name, expected in combined_expected.items():
        if combined_actual[name] != expected:
            raise ValueError(f"{name}: {combined_actual[name]} != {expected}")

    output_files = {
        "source_summary": source_path.name,
        "morphology_summary": morphology_path.name,
        "interaction_summary": interaction_path.name,
    }
    payload = {
        "schema_version": 1,
        "status": "passed" if not failed_orders and len(passed_orders) == len(ALL_ORDERS) else "partial",
        "reference_order": REFERENCE_ORDER,
        "orders_requested": list(ALL_ORDERS),
        "orders_recomputed": list(ORDERS_TO_RUN),
        "orders_passed": passed_orders,
        "orders_failed": failed_orders,
        "fixed_protocol": {
            "layouts": ["seven", "eight_basal_q25", "eight_apical_q25", "nine_both_q25"],
            "morphology_count": 4,
            "passive_parameter_scenarios": 9,
            "sources": ["soma", "basal_q75", "apical_q75"],
            "pulse_widths_ms": [2.0, 10.0],
            "pulse_amplitude_pA": 10.0,
            "pulse_onset_ms": 2.0,
            "dt_ms": 0.00625,
            "windows_ms": [20.0, 40.0],
            "expansion_shifts_hz": [0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0],
            "neuron_segment_cap_um": 0.5,
        },
        "coverage_per_order": {
            "case_metrics_rows": EXPECTED_CASE_ROWS,
            "matched_comparison_rows": EXPECTED_COMPARISON_ROWS,
            "posthoc_source_rows": EXPECTED_SOURCE_POSTHOC_ROWS,
            "posthoc_morphology_rows": EXPECTED_MORPHOLOGY_POSTHOC_ROWS,
            "posthoc_interaction_rows": EXPECTED_INTERACTION_POSTHOC_ROWS,
        },
        "combined_coverage": combined_actual,
        "outputs": output_files,
        "order_runs": results,
        "wall_seconds": time.perf_counter() - started,
        "interpretation_limits": [
            "The sweep evaluates numerical stability of the four-layout passive PRIMA approximation across basis orders; it is not a biological validation.",
            "The order-168 matrix is the already completed and validated reference, while orders 112 and 224 are recomputed with the same runner.",
            "Ratios are accompanied by absolute errors in per-order post-analysis CSVs because very small baseline residuals can inflate ratios.",
            "The four morphologies are individual reconstructions and must remain separate strata.",
            "No production solver or default is modified.",
        ],
    }
    manifest_path = RESULTS_DIR / f"{ORDER_SWEEP_STEM}_report.json"
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    return payload


def main() -> None:
    payload = run()
    if payload["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
