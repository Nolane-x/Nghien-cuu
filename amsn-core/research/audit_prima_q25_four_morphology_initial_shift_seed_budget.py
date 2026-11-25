#!/usr/bin/env python3
"""Quantify the initial multishift block budget for four-morphology q25 PRIMA layouts.

This is a diagnostic of the initial rational-Krylov seed stage only. It counts
independent columns contributed by each expansion shift, then reports how much
of the requested 112/168/224 state budget remains for subsequent round-robin
Krylov growth. It does not build the final reduced basis or measure response
error.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

RESEARCH = Path(__file__).resolve().parent
AMSN_ROOT = RESEARCH.parent
RESULTS = AMSN_ROOT / "results"
STEM = "prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25"
ORDERS = (112, 168, 224)
MAX_ORDER = max(ORDERS)
EXPECTED_RAW_ROWS = 4 * 9 * 4 * 6
EXPECTED_MODEL_ROWS = 4 * 9 * 4
EXPECTED_MORPH_LAYOUT_ROWS = 4 * 4


def load_runner():
    path = RESEARCH / "analyze_prima_q25_four_morphology_four_layout_boundary_ablation.py"
    spec = importlib.util.spec_from_file_location("q25_seed_budget_primary_runner", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load primary q25 runner from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_seed_rows(
    raw_rows: list[dict[str, Any]],
    *,
    shifts_hz: tuple[float, ...],
    orders: tuple[int, ...] = ORDERS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate exact seed coverage and build model- and morphology-level tables."""
    if tuple(sorted(set(orders))) != tuple(orders) or min(orders) <= 0:
        raise ValueError("basis orders must be unique, positive and ascending")
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    seen = set()
    for row in raw_rows:
        key = (
            str(row["morphology"]),
            str(row["parameter_scenario"]),
            str(row["layout_id"]),
        )
        shift = float(row["seed_shift_hz"])
        full_key = key + (shift,)
        if full_key in seen:
            raise ValueError(f"duplicate initial-seed row: {full_key}")
        seen.add(full_key)
        grouped[key].append(row)

    expected_shifts = set(float(x) for x in shifts_hz)
    if len(grouped) != EXPECTED_MODEL_ROWS:
        raise ValueError(
            f"model-layout seed groups {len(grouped)} != {EXPECTED_MODEL_ROWS}"
        )
    model_rows: list[dict[str, Any]] = []
    for key, rows in sorted(grouped.items()):
        if {float(row["seed_shift_hz"]) for row in rows} != expected_shifts:
            raise ValueError(f"{key}: incomplete expansion-shift coverage")
        rows = sorted(rows, key=lambda row: float(row["seed_shift_hz"]))
        independent = [int(row["independent_seed_columns"]) for row in rows]
        cumulative = [int(row["cumulative_seed_columns"]) for row in rows]
        if any(value < 0 for value in independent + cumulative):
            raise ValueError(f"{key}: negative seed rank")
        if any(cumulative[i] != sum(independent[: i + 1]) for i in range(len(rows))):
            raise ValueError(f"{key}: cumulative seed rank is inconsistent")
        port_count = int(rows[0]["port_count"])
        if any(int(row["port_count"]) != port_count for row in rows):
            raise ValueError(f"{key}: port count changes between shifts")
        total = cumulative[-1]
        if total > MAX_ORDER:
            raise ValueError(f"{key}: initial seed rank {total} exceeds max order {MAX_ORDER}")
        out: dict[str, Any] = {
            "morphology": key[0],
            "parameter_scenario": key[1],
            "layout_id": key[2],
            "port_count": port_count,
            "shift_count": len(rows),
            "initial_seed_columns_total": total,
            "independent_columns_per_shift": ";".join(str(x) for x in independent),
        }
        for order in orders:
            remaining = int(order) - total
            if remaining < 0:
                raise ValueError(f"{key}: initial seed rank exceeds basis order {order}")
            out[f"order_{order}_remaining_after_initial_seeds"] = remaining
            out[f"order_{order}_initial_seed_budget_pct"] = (
                100.0 * total / int(order)
            )
        model_rows.append(out)

    morph_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        morph_groups[(row["morphology"], row["layout_id"])].append(row)
    if len(morph_groups) != EXPECTED_MORPH_LAYOUT_ROWS:
        raise ValueError(
            f"morphology/layout groups {len(morph_groups)} != {EXPECTED_MORPH_LAYOUT_ROWS}"
        )
    morph_rows: list[dict[str, Any]] = []
    for key, rows in sorted(morph_groups.items()):
        if len(rows) != 9:
            raise ValueError(f"{key}: expected 9 passive scenarios, got {len(rows)}")
        totals = [int(row["initial_seed_columns_total"]) for row in rows]
        out = {
            "morphology": key[0],
            "layout_id": key[1],
            "port_count": int(rows[0]["port_count"]),
            "parameter_scenarios": len(rows),
            "min_initial_seed_columns": min(totals),
            "median_initial_seed_columns": float(statistics.median(totals)),
            "max_initial_seed_columns": max(totals),
            "initial_seed_columns_constant_across_scenarios": len(set(totals)) == 1,
        }
        for order in orders:
            remaining = [int(row[f"order_{order}_remaining_after_initial_seeds"]) for row in rows]
            budget = [float(row[f"order_{order}_initial_seed_budget_pct"]) for row in rows]
            out[f"order_{order}_median_remaining_states"] = float(statistics.median(remaining))
            out[f"order_{order}_median_initial_seed_budget_pct"] = float(statistics.median(budget))
        morph_rows.append(out)
    if len(raw_rows) != EXPECTED_RAW_ROWS:
        raise ValueError(f"raw seed rows {len(raw_rows)} != {EXPECTED_RAW_ROWS}")
    return model_rows, morph_rows


def run(output_dir: Path = RESULTS) -> dict[str, Any]:
    runner = load_runner()
    active_targets = runner.verified_numpy_dispatch_targets()
    if runner.BASIS_ORDER != 168:
        raise RuntimeError("primary q25 runner order is not 168")
    raw_rows: list[dict[str, Any]] = []
    morphology_manifest = []
    started = time.perf_counter()

    for morph_spec in runner.MORPHOLOGIES:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        source_sha = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
        if source_sha != morph_spec["expected_sha256"]:
            raise ValueError(f"{morph_spec['name']}: SWC checksum mismatch")
        preflight_path = Path(morph_spec["preflight"])
        if not preflight_path.is_file():
            raise FileNotFoundError(preflight_path)
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        if (
            preflight.get("status") != "PASS"
            or preflight.get("source", {}).get("source_sha256") != source_sha
        ):
            raise ValueError(f"{morph_spec['name']}: preflight/source checksum mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, shared_ids, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        expected_q25 = {
            int(x) for x in preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])
        }
        if set(int(x) for x in q25_ids.values()) != expected_q25:
            raise ValueError(f"{morph_spec['name']}: q25 node IDs differ from preflight")
        runner.validate_four_layout_node_sets(
            shared_ids,
            {name: layout["node_ids"] for name, layout in layouts.items()},
            q25_ids,
        )
        morphology_manifest.append({
            "morphology": morph_spec["name"],
            "neuromorpho_id": morph_spec["neuromorpho_id"],
            "swc_sha256": source_sha,
            "swc_records": morph_spec["expected_records"],
            "shared_output_node_ids": [int(x) for x in shared_ids],
            "q25_node_ids": {name: int(value) for name, value in q25_ids.items()},
        })

        for scenario_name, scales in baseline.parameter_cases().items():
            target = runner.conditioning.build_target_tree(module, base_tree, scales)
            for layout_id in runner.LAYOUT_IDS:
                layout = layouts[layout_id]
                seeds = runner.conditioning.initial_shift_seed_counts(
                    target,
                    [int(x) for x in layout["ports"]],
                    runner.conditioning.SHIFTS_HZ,
                    MAX_ORDER,
                )
                for seed in seeds:
                    raw_rows.append({
                        "morphology": morph_spec["name"],
                        "neuromorpho_id": morph_spec["neuromorpho_id"],
                        "parameter_scenario": scenario_name,
                        "layout_id": layout_id,
                        "port_count": int(layout["port_count"]),
                        **seed,
                    })

    model_rows, morphology_rows = summarize_seed_rows(
        raw_rows,
        shifts_hz=tuple(runner.conditioning.SHIFTS_HZ),
        orders=ORDERS,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / f"{STEM}_raw.csv"
    model_path = output_dir / f"{STEM}_model_summary.csv"
    morphology_path = output_dir / f"{STEM}_morphology_summary.csv"
    write_csv(raw_path, raw_rows)
    write_csv(model_path, model_rows)
    write_csv(morphology_path, morphology_rows)

    report = {
        "schema_version": 1,
        "status": "passed",
        "study": "four-morphology q25 initial multishift Krylov seed-budget diagnostic",
        "runtime": runner.numerical_runtime_diagnostics(),
        "active_numpy_dispatch_targets": active_targets,
        "scope": {
            "morphologies": morphology_manifest,
            "layouts": list(runner.LAYOUT_IDS),
            "parameter_scenarios": list(runner.conditioning.peng_replay.baseline.parameter_cases()),
            "expansion_shifts_hz": list(runner.conditioning.SHIFTS_HZ),
            "basis_orders": list(ORDERS),
            "seed_rank_cap_used_for_diagnostic": MAX_ORDER,
            "neuron_segment_cap_um": 0.5,
        },
        "coverage": {
            "raw_seed_rows": len(raw_rows),
            "model_layout_summary_rows": len(model_rows),
            "morphology_layout_summary_rows": len(morphology_rows),
            "expected_raw_seed_rows": EXPECTED_RAW_ROWS,
            "expected_model_layout_summary_rows": EXPECTED_MODEL_ROWS,
            "expected_morphology_layout_summary_rows": EXPECTED_MORPH_LAYOUT_ROWS,
            "all_models_within_all_basis_orders": True,
            "raw_seed_csv_sha256": sha256_file(raw_path),
        },
        "outputs": {
            "raw": raw_path.name,
            "model_summary": model_path.name,
            "morphology_summary": morphology_path.name,
        },
        "interpretation_limits": [
            "Counts only independent columns in the initial shifted inverse blocks, before later round-robin Krylov growth.",
            "It measures seed-budget competition and does not itself prove that this is the only cause of q25 approximation-error changes.",
            "The four morphologies are individual reconstructions, not population samples.",
            "The models are passive linear-RC; no active-neuron or biological validation is claimed.",
            "No production PRIMA order, retained port, solver or default is changed.",
        ],
        "elapsed_wall_seconds": time.perf_counter() - started,
    }
    report_path = output_dir / f"{STEM}_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=RESULTS)
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
