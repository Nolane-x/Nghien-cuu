#!/usr/bin/env python3
"""Instrument later PRIMA multi-shift block-Krylov growth across two holdouts.

The instrumented builder mirrors the existing modified Gram-Schmidt logic and
checks its final basis against the production builder. No production code is
changed. The audit records seed blocks, round-robin shift contributions and
candidate residual norms before acceptance/rejection.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

RESEARCH = Path(__file__).resolve().parent
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import audit_prima_q25_basis_conditioning as conditioning
from amsn.prima import _solve_shifted_passive_real

LAYOUT_IDS = conditioning.LAYOUT_IDS
ORDERS = conditioning.ORDERS
SHIFTS_HZ = conditioning.SHIFTS_HZ
RELATIVE_TOLERANCE = conditioning.RELATIVE_TOLERANCE
EXPECTED_MODEL_ROWS = 2 * 9 * len(LAYOUT_IDS) * len(ORDERS)
EXPECTED_SEED_BLOCK_ROWS = EXPECTED_MODEL_ROWS * len(SHIFTS_HZ)
RESULT_STEM = "prima_q25_krylov_growth_cross_morphology_2026-11-24"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {
        "models": EXPECTED_MODEL_ROWS,
        "seed_blocks": EXPECTED_SEED_BLOCK_ROWS,
    }


def _instrumented_orthogonalize_block(
    candidates: np.ndarray,
    basis_columns: list[np.ndarray],
    relative_tolerance: float,
    max_order: int,
    *,
    context: dict[str, Any],
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Mirror amsn.prima._orthogonalize_block and emit one row per attempted vector.

    Important implementation detail: the current production routine projects
    against basis_columns and also against the local accepted list; accepted
    vectors are appended to both. This audit deliberately preserves that exact
    behavior, then verifies the complete final basis against the production
    builder so instrumentation cannot silently change the algorithm.
    """
    accepted: list[np.ndarray] = []
    events: list[dict[str, Any]] = []
    for column in range(candidates.shape[1]):
        if len(basis_columns) >= max_order:
            break
        vector = np.array(candidates[:, column], dtype=float, copy=True)
        original_norm = float(np.linalg.norm(vector))
        if not np.isfinite(original_norm):
            raise FloatingPointError("non-finite Krylov vector")
        if original_norm == 0.0:
            events.append({
                **context, "candidate_index": column,
                "original_norm": 0.0, "residual_norm": 0.0,
                "residual_ratio": 0.0, "accepted": False,
                "rejection_reason": "zero_vector",
                "global_order_after": len(basis_columns),
            })
            continue

        for _ in range(2):
            for existing in basis_columns:
                vector -= existing * float(np.dot(existing, vector))
            for existing in accepted:
                vector -= existing * float(np.dot(existing, vector))
        residual_norm = float(np.linalg.norm(vector))
        if not np.isfinite(residual_norm):
            raise FloatingPointError("non-finite orthogonalized Krylov vector")
        residual_ratio = residual_norm / original_norm
        if residual_norm <= relative_tolerance * original_norm:
            events.append({
                **context, "candidate_index": column,
                "original_norm": original_norm, "residual_norm": residual_norm,
                "residual_ratio": residual_ratio, "accepted": False,
                "rejection_reason": "relative_tolerance",
                "global_order_after": len(basis_columns),
            })
            continue

        vector /= residual_norm
        accepted.append(vector)
        basis_columns.append(vector)
        events.append({
            **context, "candidate_index": column,
            "original_norm": original_norm, "residual_norm": residual_norm,
            "residual_ratio": residual_ratio, "accepted": True,
            "rejection_reason": "",
            "global_order_after": len(basis_columns),
        })

    if not accepted:
        block = np.empty((candidates.shape[0], 0), dtype=float)
    else:
        block = np.column_stack(accepted)
    return block, events


def instrumented_multishift_basis(
    tree,
    ports: list[int],
    max_order: int,
    shifts_hz: tuple[float, ...],
    *,
    relative_tolerance: float,
    identity: dict[str, Any],
) -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Replay seed + round-robin Krylov growth with detailed per-shift tracing."""
    n = tree.n_compartments
    order_cap = min(int(max_order), n)
    selector = np.zeros((n, len(ports)), dtype=float)
    selector[np.asarray(ports, dtype=int), np.arange(len(ports))] = 1.0
    basis_columns: list[np.ndarray] = []
    shifted_blocks: list[tuple[float, np.ndarray]] = []
    events: list[dict[str, Any]] = []
    round_rows: list[dict[str, Any]] = []

    # Seed every shift before any one chain grows.
    for shift_index, frequency_hz in enumerate(shifts_hz):
        shift = 2.0 * math.pi * frequency_hz
        start = _solve_shifted_passive_real(tree, shift, selector)
        before = len(basis_columns)
        context = {
            **identity, "stage": "seed", "round_index": 0,
            "shift_index": shift_index, "shift_hz": frequency_hz,
        }
        block, block_events = _instrumented_orthogonalize_block(
            start, basis_columns, relative_tolerance, order_cap,
            context=context,
        )
        events.extend(block_events)
        accepted = block.shape[1]
        round_rows.append({
            **identity, "stage": "seed", "round_index": 0,
            "shift_index": shift_index, "shift_hz": frequency_hz,
            "input_columns": int(start.shape[1]),
            "attempted_columns": len(block_events),
            "accepted_columns": int(accepted),
            "rejected_columns": sum(not row["accepted"] for row in block_events),
            "unprocessed_columns": int(start.shape[1] - len(block_events)),
            "global_order_before": before,
            "global_order_after": len(basis_columns),
            "median_accepted_residual_ratio": (
                float(np.median([r["residual_ratio"] for r in block_events if r["accepted"]]))
                if accepted else 0.0
            ),
            "minimum_accepted_residual_ratio": (
                float(min(r["residual_ratio"] for r in block_events if r["accepted"]))
                if accepted else 0.0
            ),
        })
        shifted_blocks.append((shift, block))

    krylov_round = 1
    while len(basis_columns) < order_cap:
        added_any = False
        updated_blocks: list[tuple[float, np.ndarray]] = []
        for shift_index, (shift, block) in enumerate(shifted_blocks):
            before = len(basis_columns)
            frequency_hz = shifts_hz[shift_index]
            if len(basis_columns) >= order_cap or block.shape[1] == 0:
                updated_blocks.append((shift, np.empty((n, 0), dtype=float)))
                round_rows.append({
                    **identity, "stage": "krylov", "round_index": krylov_round,
                    "shift_index": shift_index, "shift_hz": frequency_hz,
                    "input_columns": int(block.shape[1]),
                    "attempted_columns": 0, "accepted_columns": 0,
                    "rejected_columns": 0, "unprocessed_columns": int(block.shape[1]),
                    "global_order_before": before, "global_order_after": before,
                    "median_accepted_residual_ratio": 0.0,
                    "minimum_accepted_residual_ratio": 0.0,
                })
                continue

            candidates = _solve_shifted_passive_real(
                tree, shift, -tree.capacitance_f[:, None] * block
            )
            context = {
                **identity, "stage": "krylov", "round_index": krylov_round,
                "shift_index": shift_index, "shift_hz": frequency_hz,
            }
            following, block_events = _instrumented_orthogonalize_block(
                candidates, basis_columns, relative_tolerance, order_cap,
                context=context,
            )
            events.extend(block_events)
            accepted = following.shape[1]
            if accepted > 0:
                added_any = True
            ratios = [r["residual_ratio"] for r in block_events if r["accepted"]]
            round_rows.append({
                **identity, "stage": "krylov", "round_index": krylov_round,
                "shift_index": shift_index, "shift_hz": frequency_hz,
                "input_columns": int(block.shape[1]),
                "attempted_columns": len(block_events),
                "accepted_columns": int(accepted),
                "rejected_columns": sum(not row["accepted"] for row in block_events),
                "unprocessed_columns": int(candidates.shape[1] - len(block_events)),
                "global_order_before": before,
                "global_order_after": len(basis_columns),
                "median_accepted_residual_ratio": float(np.median(ratios)) if ratios else 0.0,
                "minimum_accepted_residual_ratio": float(min(ratios)) if ratios else 0.0,
            })
            updated_blocks.append((shift, following))

        shifted_blocks = updated_blocks
        if not added_any:
            break
        krylov_round += 1

    if not basis_columns:
        raise RuntimeError(f"no basis vectors accepted for {identity}")
    basis = np.column_stack(basis_columns)
    summary = {
        **identity,
        "requested_order": int(max_order),
        "achieved_order": int(basis.shape[1]),
        "seed_accepted_columns": int(sum(r["accepted_columns"] for r in round_rows if r["stage"] == "seed")),
        "krylov_accepted_columns": int(sum(r["accepted_columns"] for r in round_rows if r["stage"] == "krylov")),
        "krylov_rounds": int(max((r["round_index"] for r in round_rows if r["stage"] == "krylov"), default=0)),
        "shift_round_rows": len(round_rows),
        "candidate_event_rows": len(events),
    }
    return basis, events, round_rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    model_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    round_rows: list[dict[str, Any]] = []
    conditioning_morphologies = conditioning.MORPHOLOGIES

    for morph_spec in conditioning_morphologies:
        module = morph_spec["module"]
        baseline = module.baseline
        reference = baseline.reference
        reference.DATA = module.SWC
        reference.MAX_NEURON_SEGMENT_UM = 0.5
        morphology = baseline.SWCMorphology.from_file(module.SWC)
        require(len(morphology.nodes) == morph_spec["expected_records"],
                f"{morph_spec['name']}: SWC record count mismatch")
        digest = morph_spec["expected_sha256"]
        require(digest == module.EXPECTED_SWC_SHA256, "pinned SWC digest mismatch")
        preflight_path = morph_spec["preflight"]
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        require(preflight.get("status") == "PASS", f"{morph_spec['name']}: preflight failed")
        require(preflight.get("source", {}).get("source_sha256") == digest,
                f"{morph_spec['name']}: preflight digest mismatch")

        reader, sections = reference.import_swc_with_neuron()
        base_tree = morphology.to_cable_tree()
        layouts, _, q25_ids = module.build_four_layouts(
            morphology, reader, sections, base_tree
        )
        require(
            set(q25_ids.values()) == set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", [])),
            f"{morph_spec['name']}: q25 IDs differ from preflight",
        )
        scenarios = baseline.parameter_cases()
        base_parameters = base_tree.parameters

        for scenario_name, (rm_scale, cm_scale, ra_scale) in scenarios.items():
            parameters = baseline.PassiveParameters(
                specific_capacitance_f_m2=base_parameters.specific_capacitance_f_m2 * cm_scale,
                specific_membrane_resistance_ohm_m2=base_parameters.specific_membrane_resistance_ohm_m2 * rm_scale,
                axial_resistivity_ohm_m=base_parameters.axial_resistivity_ohm_m * ra_scale,
                e_leak_v=base_parameters.e_leak_v,
            )
            target = baseline.CableTree(
                [base_tree.by_name[name] for name in base_tree.order],
                parameters,
            )

            for layout_id in LAYOUT_IDS:
                layout = layouts[layout_id]
                for order in ORDERS:
                    identity = {
                        "morphology": morph_spec["name"],
                        "neuromorpho_id": morph_spec["neuromorpho_id"],
                        "swc_sha256": digest,
                        "layout_id": layout_id,
                        "port_count": int(layout["port_count"]),
                        "basis_order": int(order),
                        "parameter_scenario": scenario_name,
                    }
                    tracked_basis, events, rounds, summary = instrumented_multishift_basis(
                        target,
                        layout["ports"],
                        order,
                        SHIFTS_HZ,
                        relative_tolerance=RELATIVE_TOLERANCE,
                        identity=identity,
                    )

                    # Prove that the instrumented trace preserved the production basis.
                    production_model = baseline.prima_reduce_passive_cable_multishift(
                        target,
                        layout["ports"],
                        order,
                        SHIFTS_HZ,
                        relative_tolerance=RELATIVE_TOLERANCE,
                    )
                    require(production_model.order == order, "production builder order mismatch")
                    require(tracked_basis.shape == production_model.basis.shape,
                            "instrumented basis shape differs from production")
                    basis_delta = float(np.max(np.abs(tracked_basis - production_model.basis)))
                    require(basis_delta <= 1e-14,
                            f"instrumented basis differs from production by {basis_delta}")
                    gram = tracked_basis.T @ tracked_basis
                    ortho_error = float(np.max(np.abs(gram - np.eye(order))))
                    require(np.isfinite(ortho_error) and ortho_error <= 1e-12,
                            "instrumented basis is not orthonormal within tolerance")

                    model_rows.append({
                        **summary,
                        "basis_max_abs_difference_vs_production": basis_delta,
                        "basis_orthogonality_max_abs": ortho_error,
                        "max_round_index": max((r["round_index"] for r in rounds), default=0),
                    })
                    event_rows.extend(events)
                    round_rows.extend(rounds)

    require(len(model_rows) == EXPECTED_MODEL_ROWS,
            f"model rows {len(model_rows)} != {EXPECTED_MODEL_ROWS}")
    seed_block_rows = [r for r in round_rows if r["stage"] == "seed"]
    require(len(seed_block_rows) == EXPECTED_SEED_BLOCK_ROWS,
            f"seed block rows {len(seed_block_rows)} != {EXPECTED_SEED_BLOCK_ROWS}")
    require(all(int(r["achieved_order"]) == int(r["requested_order"]) for r in model_rows),
            "one or more tracked models failed to reach the requested order")
    require(max(float(r["basis_max_abs_difference_vs_production"]) for r in model_rows) <= 1e-14,
            "instrumented basis does not reproduce production basis")

    results_dir = Path("results")
    write_csv(results_dir / f"{RESULT_STEM}_models.csv", model_rows)
    write_csv(results_dir / f"{RESULT_STEM}_candidate_events.csv", event_rows)
    write_csv(results_dir / f"{RESULT_STEM}_shift_rounds.csv", round_rows)

    report = {
        "schema_version": 1,
        "status": "prima_q25_krylov_growth_audit_passed",
        "scope": {
            "morphologies": [
                {
                    "name": m["name"],
                    "neuromorpho_id": m["neuromorpho_id"],
                    "swc_sha256": m["expected_sha256"],
                    "swc_records": m["expected_records"],
                } for m in conditioning_morphologies
            ],
            "layouts": list(LAYOUT_IDS),
            "basis_orders": list(ORDERS),
            "parameter_scenarios": list(conditioning.peng_replay.baseline.parameter_cases()),
            "shifts_hz": list(SHIFTS_HZ),
            "relative_tolerance": RELATIVE_TOLERANCE,
        },
        "exact_coverage": {
            "models": len(model_rows),
            "seed_block_rows": len(seed_block_rows),
            "candidate_event_rows": len(event_rows),
            "shift_round_rows": len(round_rows),
            "expected_models": EXPECTED_MODEL_ROWS,
            "expected_seed_block_rows": EXPECTED_SEED_BLOCK_ROWS,
            "max_basis_difference_vs_production": max(
                float(r["basis_max_abs_difference_vs_production"]) for r in model_rows
            ),
        },
        "scientific_limits": [
            "Instrumented modified Gram-Schmidt mirrors the current private production routine; final bases are compared against the unmodified production builder for every model.",
            "Per-shift event rows distinguish initial seed blocks from later round-robin Krylov growth.",
            "The audit measures numerical subspace growth only; it does not by itself explain transfer or transient error differences.",
            "Only two individual passive morphology reconstructions are compared; they are not population samples.",
            "Full Hines remains canonical; no production solver code or defaults are changed.",
        ],
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
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
