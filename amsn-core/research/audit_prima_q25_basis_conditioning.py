#!/usr/bin/env python3
"""Compare PRIMA q25 basis conditioning on the Peng mouse and Tamas human holdouts.

This is a structural audit of the already validated four-layout ablations.
It does not rerun the full transient matrix, alter production defaults, or
infer a biological mechanism.
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

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import replay_nmo163775_four_layout_ablation as peng_replay
import replay_nmo107159_four_layout_replication as tamas_replay
from amsn.prima import _orthogonalize_block, _solve_shifted_passive_real

LAYOUT_IDS = (
    "seven",
    "eight_basal_q25",
    "eight_apical_q25",
    "nine_both_q25",
)
ORDERS = (112, 168)
SHIFTS_HZ = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)
RELATIVE_TOLERANCE = 1e-12
EXPECTED_MODEL_ROWS = 2 * 9 * len(LAYOUT_IDS) * len(ORDERS)
EXPECTED_SEED_ROWS = EXPECTED_MODEL_ROWS * len(SHIFTS_HZ)
EXPECTED_PORT_ROWS = 2 * 9 * len(ORDERS) * sum((7, 8, 8, 9))
RESULT_STEM = "prima_q25_cross_morphology_conditioning_2026-11-24"

MORPHOLOGIES = (
    {
        "name": "NMO_163775_Peng_mouse_Control",
        "module": peng_replay,
        "preflight": Path("results/NMO_163775_PengControl_holdout/preflight.json"),
        "expected_sha256": peng_replay.EXPECTED_SWC_SHA256,
        "expected_records": peng_replay.EXPECTED_SWC_RECORDS,
    },
    {
        "name": "NMO_107159_Tamas_human_pyramidal_Control",
        "module": tamas_replay,
        "preflight": Path("results/NMO_107159_TamasHumanPyramidalControl_holdout/preflight.json"),
        "expected_sha256": tamas_replay.EXPECTED_SWC_SHA256,
        "expected_records": tamas_replay.EXPECTED_SWC_RECORDS,
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_counts() -> dict[str, int]:
    return {"models": EXPECTED_MODEL_ROWS, "shift_seeds": EXPECTED_SEED_ROWS, "port_leverage": EXPECTED_PORT_ROWS}


def finite_condition(eigenvalues: np.ndarray, label: str) -> float:
    values = np.asarray(eigenvalues, dtype=float)
    require(values.ndim == 1 and values.size > 0, f"{label}: empty eigenvalue set")
    require(np.all(np.isfinite(values)), f"{label}: non-finite eigenvalues")
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    require(minimum > 0.0 and maximum >= minimum, f"{label}: not positive definite")
    return maximum / minimum


def generalized_rate_spectrum(
    conductance: np.ndarray, capacitance: np.ndarray
) -> tuple[float, float, float]:
    """Return min/max generalized RC decay rates and their ratio."""
    lower = np.linalg.cholesky(capacitance)
    left = np.linalg.solve(lower, conductance)
    whitened = np.linalg.solve(lower, left.T).T
    whitened = 0.5 * (whitened + whitened.T)
    values = np.linalg.eigvalsh(whitened)
    require(np.all(np.isfinite(values)) and float(values[0]) > 0.0,
            "generalized RC operator has a non-positive or non-finite eigenvalue")
    return float(values[0]), float(values[-1]), float(values[-1] / values[0])


def initial_shift_seed_counts(
    tree,
    ports: list[int],
    shifts_hz: tuple[float, ...],
    max_order: int,
) -> list[dict[str, Any]]:
    """Count independent basis columns contributed by each initial shift block.

    This mirrors the initial seeding stage of prima_reduce_passive_cable_multishift
    using its own Hines shifted solve and twice-reorthogonalized block routine.
    It deliberately reports only seed contributions, not the later round-robin
    Krylov growth.
    """
    n = tree.n_compartments
    selector = np.zeros((n, len(ports)), dtype=float)
    selector[np.asarray(ports, dtype=int), np.arange(len(ports))] = 1.0
    basis_columns: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    for frequency_hz in shifts_hz:
        shift_per_s = 2.0 * math.pi * frequency_hz
        start = _solve_shifted_passive_real(tree, shift_per_s, selector)
        block = _orthogonalize_block(
            start, basis_columns, RELATIVE_TOLERANCE, max_order
        )
        rows.append({
            "frequency_hz": frequency_hz,
            "independent_seed_columns": int(block.shape[1]),
            "cumulative_seed_columns": int(len(basis_columns)),
            "remaining_order_after_seed": int(max_order - len(basis_columns)),
        })
    return rows


def build_target_tree(module, base_tree, scales: tuple[float, float, float]):
    rm_scale, cm_scale, ra_scale = scales
    p = base_tree.parameters
    parameters = module.baseline.PassiveParameters(
        specific_capacitance_f_m2=p.specific_capacitance_f_m2 * cm_scale,
        specific_membrane_resistance_ohm_m2=p.specific_membrane_resistance_ohm_m2 * rm_scale,
        axial_resistivity_ohm_m=p.axial_resistivity_ohm_m * ra_scale,
        e_leak_v=p.e_leak_v,
    )
    return module.baseline.CableTree(
        [base_tree.by_name[name] for name in base_tree.order],
        parameters,
    )


def audit_morphology(morphology_spec: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    module = morphology_spec["module"]
    baseline = module.baseline
    reference = baseline.reference
    reference.DATA = module.SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.5

    morphology = baseline.SWCMorphology.from_file(module.SWC)
    require(len(morphology.nodes) == morphology_spec["expected_records"],
            f"{morphology_spec['name']}: SWC record count mismatch")
    preflight = json.loads(morphology_spec["preflight"].read_text(encoding="utf-8"))
    digest = morphology_spec["expected_sha256"]
    require(preflight.get("status") == "PASS", f"{morphology_spec['name']}: preflight did not pass")
    require(preflight.get("source", {}).get("source_sha256") == digest,
            f"{morphology_spec['name']}: preflight source digest mismatch")

    reader, sections = reference.import_swc_with_neuron()
    base_tree = morphology.to_cable_tree()
    layouts, common_ids, q25_ids = module.build_four_layouts(
        morphology, reader, sections, base_tree
    )
    preflight_q25 = set(preflight.get("amsn", {}).get("q25_only_swc_node_ids", []))
    require(set(q25_ids.values()) == preflight_q25,
            f"{morphology_spec['name']}: q25 nodes differ from preflight")

    model_rows: list[dict[str, Any]] = []
    port_rows: list[dict[str, Any]] = []
    shift_seed_rows: list[dict[str, Any]] = []
    scenarios = baseline.parameter_cases()
    for scenario_name, scales in scenarios.items():
        target = build_target_tree(module, base_tree, scales)
        for layout_id in LAYOUT_IDS:
            layout = layouts[layout_id]
            for order in ORDERS:
                started = time.perf_counter()
                model = baseline.prima_reduce_passive_cable_multishift(
                    target, layout["ports"], order, SHIFTS_HZ,
                    relative_tolerance=RELATIVE_TOLERANCE,
                )
                build_seconds = time.perf_counter() - started
                require(model.order == order,
                        f"{morphology_spec['name']}/{layout_id}: achieved order {model.order}, expected {order}")

                basis = model.basis
                gram = basis.T @ basis
                gram_error = gram - np.eye(order)
                gram_eigs = np.linalg.eigvalsh(0.5 * (gram + gram.T))
                g_eigs = np.linalg.eigvalsh(model.conductance_matrix_s)
                c_eigs = np.linalg.eigvalsh(model.capacitance_matrix_f)
                rate_min, rate_max, rate_ratio = generalized_rate_spectrum(
                    model.conductance_matrix_s,
                    model.capacitance_matrix_f,
                )
                require(np.all(np.isfinite(basis)), "basis has non-finite entries")
                require(np.all(g_eigs > 0.0) and np.all(c_eigs > 0.0),
                        "projected G or C lost positive definiteness")

                port_ids = layout["node_ids"]
                role_map = layout["roles"]
                for node_id, port_index in zip(port_ids, layout["ports"]):
                    row_vector = basis[port_index, :]
                    port_rows.append({
                        "morphology": morphology_spec["name"],
                        "layout_id": layout_id,
                        "basis_order": order,
                        "parameter_scenario": scenario_name,
                        "port_swc_id": int(node_id),
                        "port_roles": ";".join(role_map[node_id]),
                        "basis_row_l2_norm": float(np.linalg.norm(row_vector)),
                        "basis_row_max_abs": float(np.max(np.abs(row_vector))),
                        "basis_row_leverage": float(np.dot(row_vector, row_vector)),
                    })

                seed_counts = initial_shift_seed_counts(
                    target, layout["ports"], SHIFTS_HZ, order
                )
                for row in seed_counts:
                    shift_seed_rows.append({
                        "morphology": morphology_spec["name"],
                        "layout_id": layout_id,
                        "basis_order": order,
                        "parameter_scenario": scenario_name,
                        "seed_shift_hz": row["frequency_hz"],
                        "independent_seed_columns": row["independent_seed_columns"],
                        "cumulative_seed_columns": row["cumulative_seed_columns"],
                        "remaining_order_after_seed": row["remaining_order_after_seed"],
                    })

                model_rows.append({
                    "morphology": morphology_spec["name"],
                    "neuromorpho_id": preflight.get("source", {}).get("neuromorpho_id"),
                    "swc_sha256": digest,
                    "full_order": target.n_compartments,
                    "layout_id": layout_id,
                    "port_count": layout["port_count"],
                    "q25_node_ids": ";".join(str(q25_ids[k]) for k in ("basal_q25", "apical_q25")),
                    "basis_order": order,
                    "parameter_scenario": scenario_name,
                    "expansion_shifts_hz": ";".join(str(x) for x in SHIFTS_HZ),
                    "basis_build_seconds": build_seconds,
                    "basis_orthogonality_frobenius": float(np.linalg.norm(gram_error, ord="fro")),
                    "basis_orthogonality_max_abs": float(np.max(np.abs(gram_error))),
                    "basis_gram_min_eigenvalue": float(gram_eigs[0]),
                    "basis_gram_max_eigenvalue": float(gram_eigs[-1]),
                    "basis_condition_number": finite_condition(gram_eigs, "basis Gram"),
                    "conductance_min_eigenvalue_S": float(g_eigs[0]),
                    "conductance_max_eigenvalue_S": float(g_eigs[-1]),
                    "conductance_condition_number": finite_condition(g_eigs, "reduced G"),
                    "capacitance_min_eigenvalue_F": float(c_eigs[0]),
                    "capacitance_max_eigenvalue_F": float(c_eigs[-1]),
                    "capacitance_condition_number": finite_condition(c_eigs, "reduced C"),
                    "rc_rate_min_per_s": rate_min,
                    "rc_rate_max_per_s": rate_max,
                    "rc_rate_dynamic_range": rate_ratio,
                    "min_cholesky_diag_G": float(np.min(np.diag(np.linalg.cholesky(model.conductance_matrix_s)))),
                    "min_cholesky_diag_C": float(np.min(np.diag(np.linalg.cholesky(model.capacitance_matrix_f)))),
                    "passivity_check": "cholesky_passed",
                })

    require(len(model_rows) == len(scenarios) * len(LAYOUT_IDS) * len(ORDERS),
            f"{morphology_spec['name']}: model audit coverage mismatch")
    return model_rows, port_rows, shift_seed_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.perf_counter()
    all_models: list[dict[str, Any]] = []
    all_port_rows: list[dict[str, Any]] = []
    all_shift_seed_rows: list[dict[str, Any]] = []
    for morphology_spec in MORPHOLOGIES:
        models, ports, shift_seeds = audit_morphology(morphology_spec)
        all_models.extend(models)
        all_port_rows.extend(ports)
        all_shift_seed_rows.extend(shift_seeds)

    require(len(all_models) == EXPECTED_MODEL_ROWS,
            f"model row count {len(all_models)} != {EXPECTED_MODEL_ROWS}")
    require(len(all_port_rows) == EXPECTED_PORT_ROWS,
            f"port leverage row count {len(all_port_rows)} != {EXPECTED_PORT_ROWS}")
    require(len(all_shift_seed_rows) == EXPECTED_SEED_ROWS,
            f"shift seed row count {len(all_shift_seed_rows)} != {EXPECTED_SEED_ROWS}")

    # Model-level summary includes only basis- and matrix-conditioning metrics.
    summary: list[dict[str, Any]] = []
    for morph in MORPHOLOGIES:
        morph_name = morph["name"]
        for layout_id in LAYOUT_IDS:
            for order in ORDERS:
                subset = [
                    row for row in all_models
                    if row["morphology"] == morph_name
                    and row["layout_id"] == layout_id
                    and row["basis_order"] == order
                ]
                summary.append({
                    "morphology": morph_name,
                    "layout_id": layout_id,
                    "basis_order": order,
                    "model_scenarios": len(subset),
                    "median_basis_orthogonality_max_abs": float(np.median([r["basis_orthogonality_max_abs"] for r in subset])),
                    "max_basis_orthogonality_max_abs": float(max(r["basis_orthogonality_max_abs"] for r in subset)),
                    "median_basis_condition_number": float(np.median([r["basis_condition_number"] for r in subset])),
                    "median_conductance_condition_number": float(np.median([r["conductance_condition_number"] for r in subset])),
                    "median_capacitance_condition_number": float(np.median([r["capacitance_condition_number"] for r in subset])),
                    "median_rc_rate_dynamic_range": float(np.median([r["rc_rate_dynamic_range"] for r in subset])),
                    "median_basis_build_seconds": float(np.median([r["basis_build_seconds"] for r in subset])),
                })

    results_dir = Path("results")
    write_csv(results_dir / f"{RESULT_STEM}_models.csv", all_models)
    write_csv(results_dir / f"{RESULT_STEM}_port_leverage.csv", all_port_rows)
    write_csv(results_dir / f"{RESULT_STEM}_shift_seeds.csv", all_shift_seed_rows)
    write_csv(results_dir / f"{RESULT_STEM}_summary.csv", summary)

    report = {
        "schema_version": 1,
        "status": "prima_q25_cross_morphology_conditioning_audit_passed",
        "scope": {
            "morphologies": [
                {
                    "name": m["name"],
                    "neuromorpho_id": m["module"].LABEL,
                    "swc_sha256": m["expected_sha256"],
                    "swc_records": m["expected_records"],
                } for m in MORPHOLOGIES
            ],
            "layouts": list(LAYOUT_IDS),
            "basis_orders": list(ORDERS),
            "scenarios": list(peng_replay.baseline.parameter_cases()),
            "expansion_shifts_hz": list(SHIFTS_HZ),
            "relative_tolerance": RELATIVE_TOLERANCE,
        },
        "exact_coverage": {
            "models": len(all_models),
            "port_leverage_rows": len(all_port_rows),
            "shift_seed_rows": len(all_shift_seed_rows),
            "expected_models": EXPECTED_MODEL_ROWS,
            "expected_port_leverage_rows": EXPECTED_PORT_ROWS,
            "expected_shift_seed_rows": EXPECTED_SEED_ROWS,
        },
        "summary": summary,
        "scientific_limits": [
            "The audit measures numerical basis orthogonality, projected matrix spectra and initial shift-seed allocation; it does not establish a causal mechanism for transient error differences.",
            "Only two individual passive morphology reconstructions are compared; they do not represent species or cell-class populations.",
            "The basis and matrices are passive linear-RC only; no active channels, nonlinear synapses, plasticity or biological validity are assessed.",
            "Full Hines remains canonical; no production solver defaults or behavior are changed.",
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
        "summary": summary,
        "runtime": report["runtime"],
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
