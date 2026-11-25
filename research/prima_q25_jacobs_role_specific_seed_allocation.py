#!/usr/bin/env python3
"""Jacobs-only role-specific output-dual seed allocation study.

This research-only experiment isolates the q25 dual seed target: basal only,
apical only, or both. It preserves the canonical seven input ports, order 224,
the nine existing passive parameter scenarios, and the same full-Hines/BE
measurement protocol as the accepted four-morphology sweep.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
AMSN_CORE = REPO_ROOT / "amsn-core"
AMSN_RESEARCH = AMSN_CORE / "research"
for _path in (AMSN_CORE, AMSN_RESEARCH):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import analyze_prima_q25_four_morphology_four_layout_boundary_ablation as core
import audit_prima_q25_basis_conditioning as conditioning
import audit_prima_q25_extended_backward_euler as tail
from experimental_prima_output_aware_basis import build_output_aware_passive_basis
from run_prima_q25_peng_output_aware_dual_seed_pilot import (
    finite_record_identity,
    nrmse_percent,
    sha256_array,
    simulate_reduced_outputs,
)

ORDER = 224
DT_MS = 0.00625
DT_S = DT_MS / 1000.0
WINDOWS_MS = (20.0, 40.0)
MORPHOLOGY_ID = "NMO_03524"
RESULT_STEM = "prima_q25_jacobs_role_specific_seed_allocation_order224_2026-11-25"
OLD_STEM = "prima_q25_four_morphology_output_aware_dual_seed_order224_2026-11-25"
DFT_TOLERANCE = 2e-8
IDENTITY_SCHEDULES = (
    "D0_none",
    "APICAL_10K",
    "BASAL_10K",
    "BOTH_10K",
    "BOTH_1K_10K",
)

# Each schedule declares one role or both roles, then the dual-resolvent shifts.
SCHEDULES: dict[str, tuple[str, tuple[float, ...]]] = {
    "D0_none": ("both", ()),
    "APICAL_0": ("apical", (0.0,)),
    "APICAL_1K": ("apical", (1000.0,)),
    "APICAL_10K": ("apical", (10000.0,)),
    "BASAL_0": ("basal", (0.0,)),
    "BASAL_1K": ("basal", (1000.0,)),
    "BASAL_10K": ("basal", (10000.0,)),
    "BOTH_1K": ("both", (1000.0,)),
    "BOTH_10K": ("both", (10000.0,)),
    "BOTH_1K_10K": ("both", (1000.0, 10000.0)),
}

# Reproducibility anchors from the accepted Jacobs nominal-scenario run.
EXPECTED_NOMINAL_HASHES = {
    "D0_none": {
        "basis_sha256": "fd47b1b75a2bcf39ca25fb1711932f5fde18769ab82b72c2fc8052328b7cd32b",
        "conductance_sha256": "b602f6d82be28bd396e12176e59cd878627f99c30c150d2eb60650ee64515702",
        "capacitance_sha256": "1179792be39db5a41d530ebf27929fd11ee1a3ce01272e116a6b4337616941e5",
        "input_sha256": "7cf0c62402d8a4e1f5feec7c7212063ec0a2967d461f297708320c2836e5b21c",
    },
    "BOTH_10K": {
        "basis_sha256": "d6f83fbcb0245ac862e5b5af2518fb90c91033fc1b6e2ceb650e2172ee13bb20",
        "conductance_sha256": "dff6a10b3819a15afb86e0dcbb64b56eb2cd524539724678d486f2221c4af873",
        "capacitance_sha256": "650c2f7e3a509ab203c738c034e243a00b2464ebc0289e572e6bea4b50b4c6a3",
        "input_sha256": "dabf482f945e464cadacfa1813deda5c77375f18dbff323da6b4ce70e100e401",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def paired_summary(
    rows: list[dict[str, Any]], *, group_fields: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Summarize candidate/D0 pairs by explicit scenario and trace identifiers."""
    baseline: dict[tuple[Any, ...], float] = {}
    for row in rows:
        if row["schedule"] != "D0_none":
            continue
        key = (
            row["scenario"], row["window_ms"], row["source"],
            row["pulse_width_ms"], row["output_label"],
        )
        require(key not in baseline, f"duplicate baseline key: {key}")
        baseline[key] = float(row["transient_nrmse_pct"])

    grouped: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        key = (
            row["scenario"], row["window_ms"], row["source"],
            row["pulse_width_ms"], row["output_label"],
        )
        ref = baseline.get(key)
        require(ref is not None, f"missing D0 pair: {key}")
        candidate = float(row["transient_nrmse_pct"])
        ratio = candidate / max(ref, 1e-30)
        delta = candidate - ref
        group_values = tuple(row[field] for field in group_fields)
        group_key = (*group_values, row["schedule"], row["output_role"], row["output_label"])
        grouped[group_key].append((ratio, delta))

    result: list[dict[str, Any]] = []
    for key, pairs in sorted(grouped.items(), key=lambda item: tuple(str(x) for x in item[0])):
        ratios = [pair[0] for pair in pairs]
        deltas = [pair[1] for pair in pairs]
        result.append({
            **{field: value for field, value in zip(group_fields, key)},
            "schedule": key[len(group_fields)],
            "output_role": key[len(group_fields) + 1],
            "output_label": key[len(group_fields) + 2],
            "matched_cases": len(pairs),
            "median_candidate_over_D0_error_ratio": median(ratios),
            "p90_candidate_over_D0_error_ratio": float(np.percentile(ratios, 90)),
            "worst_candidate_over_D0_error_ratio": float(max(ratios)),
            "median_absolute_error_delta_percentage_points": median(deltas),
            "max_abs_error_delta_percentage_points": float(max(abs(x) for x in deltas)),
            "candidate_better_cases": sum(x < 0.0 for x in deltas),
            "candidate_worse_cases": sum(x > 0.0 for x in deltas),
        })
    return result


def _validate_schedule_hashes(schedule_name: str, model: Any, scenario_name: str) -> dict[str, str]:
    hashes = {
        "basis_sha256": sha256_array(model.basis),
        "conductance_sha256": sha256_array(model.conductance_matrix_s),
        "capacitance_sha256": sha256_array(model.capacitance_matrix_f),
        "input_sha256": sha256_array(model.input_matrix),
    }
    if scenario_name == "nominal" and schedule_name in EXPECTED_NOMINAL_HASHES:
        expected = EXPECTED_NOMINAL_HASHES[schedule_name]
        require(hashes == expected,
                f"{schedule_name}: accepted-run matrix replay hash mismatch: {hashes}")
    return hashes


def _validate_old_metric_replay(case_rows: list[dict[str, Any]], scenario_name: str) -> None:
    """Require bit-exact case metrics for D0 and the prior BOTH-10-kHz schedule."""
    if scenario_name != "nominal":
        return
    old_path = AMSN_CORE / "results" / f"{OLD_STEM}_case_metrics.csv"
    require(old_path.exists(), f"accepted cross-morphology metrics missing: {old_path}")
    old_lookup: dict[tuple[Any, ...], float] = {}
    old_schedule_map = {
        "D0_none": "D0_none",
        "BOTH_10K": "D1_high_10000hz",
    }
    for row in read_csv(old_path):
        if row["neuromorpho_id"] != MORPHOLOGY_ID or row["scenario"] != "nominal":
            continue
        if row["schedule"] not in old_schedule_map.values():
            continue
        key = (
            row["schedule"], float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), row["output_label"],
        )
        old_lookup[key] = float(row["transient_nrmse_pct"])

    comparisons = 0
    for row in case_rows:
        old_schedule = old_schedule_map.get(row["schedule"])
        if old_schedule is None:
            continue
        key = (
            old_schedule, float(row["window_ms"]), row["source"],
            float(row["pulse_width_ms"]), row["output_label"],
        )
        prior = old_lookup.get(key)
        require(prior is not None, f"missing accepted metric replay key: {key}")
        current = float(row["transient_nrmse_pct"])
        require(current == prior,
                f"case metric replay differs for {key}: current={current}, prior={prior}")
        comparisons += 1
    require(comparisons == 216, f"expected 216 bit-exact metric replay cases, got {comparisons}")


def worker(scenario_name: str, output_dir: Path) -> None:
    worker_started = time.perf_counter()
    specs = [x for x in core.MORPHOLOGIES if x["neuromorpho_id"] == MORPHOLOGY_ID]
    require(len(specs) == 1, "Jacobs NMO_03524 must resolve exactly once")
    spec = specs[0]
    module = spec["module"]
    baseline = module.baseline
    reference = baseline.reference
    reference.DATA = module.SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.5

    scenarios = baseline.parameter_cases()
    require(scenario_name in scenarios, f"unknown passive scenario: {scenario_name}")
    morphology = baseline.SWCMorphology.from_file(module.SWC)
    source_sha = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
    require(len(morphology.nodes) == spec["expected_records"], "Jacobs SWC record count mismatch")
    require(source_sha == spec["expected_sha256"], "Jacobs SWC checksum mismatch")
    preflight_path = Path(spec["preflight"])
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    require(preflight.get("status") == "PASS", "Jacobs preflight status is not PASS")
    require(preflight.get("source", {}).get("source_sha256") == source_sha,
            "Jacobs preflight checksum mismatch")

    reader, sections = reference.import_swc_with_neuron()
    base_tree = morphology.to_cable_tree()
    layouts, shared_node_ids, q25_node_ids = module.build_four_layouts(
        morphology, reader, sections, base_tree
    )
    seven_layout = layouts["seven"]
    retained_indices = tuple(int(x) for x in seven_layout["ports"])
    require(len(retained_indices) == 7 and len(set(retained_indices)) == 7,
            "canonical input selector must remain seven unique ports")
    source_names = tuple(core.SOURCE_NAMES)
    source_tree_indices = [
        int(seven_layout["ports"][int(seven_layout["source_indices"][source])])
        for source in source_names
    ]
    electrical_map = morphology.electrical_node_mapping()
    q25_tree_indices = {
        role: int(base_tree.index[f"swc_{electrical_map[int(node_id)]}"])
        for role, node_id in q25_node_ids.items()
    }
    output_tree_indices = retained_indices + (
        q25_tree_indices["basal_q25"], q25_tree_indices["apical_q25"]
    )
    require(len(shared_node_ids) == 7 and len(output_tree_indices) == 9,
            "expected seven shared and two q25 observation rows")
    require(len(set(output_tree_indices)) == 9, "all nine output observation nodes must be unique")

    target = conditioning.build_target_tree(module, base_tree, scenarios[scenario_name])
    hines_factor = tail.build_tree_hines_be_factor(target, DT_S)
    full_trace, full_terminal_states, protocol = core.simulate_full_hines_perturbation_windows(
        target, hines_factor, source_tree_indices, list(output_tree_indices)
    )
    source_slots = {
        source: int(seven_layout["source_indices"][source]) for source in source_names
    }
    production_d0 = baseline.prima_reduce_passive_cable_multishift(
        target, list(retained_indices), ORDER, conditioning.SHIFTS_HZ,
        relative_tolerance=conditioning.RELATIVE_TOLERANCE,
    )

    case_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    traces: dict[str, Any] = {}
    for schedule_name, (seed_role, dual_frequencies) in SCHEDULES.items():
        schedule_started = time.perf_counter()
        if seed_role == "apical":
            seed_indices = (q25_tree_indices["apical_q25"],)
        elif seed_role == "basal":
            seed_indices = (q25_tree_indices["basal_q25"],)
        else:
            seed_indices = (
                q25_tree_indices["basal_q25"], q25_tree_indices["apical_q25"]
            )

        enriched = build_output_aware_passive_basis(
            target,
            retained_indices,
            seed_indices,
            max_order=ORDER,
            input_expansion_frequencies_hz=conditioning.SHIFTS_HZ,
            output_seed_frequencies_hz=dual_frequencies,
            relative_tolerance=conditioning.RELATIVE_TOLERANCE,
        )
        model = enriched.model
        require(model.order == ORDER, f"{schedule_name}: model failed to reach order {ORDER}")
        require(tuple(model.port_indices) == retained_indices,
                f"{schedule_name}: canonical seven input ports changed")
        require(model.input_matrix.shape == (ORDER, 7),
                f"{schedule_name}: reduced input matrix must be order x 7")
        np.testing.assert_array_equal(
            model.input_matrix, model.basis[np.asarray(retained_indices), :].T
        )
        output_rows = model.basis[np.asarray(output_tree_indices), :]
        require(output_rows.shape == (9, ORDER),
                f"{schedule_name}: observation map must expose all nine output rows")
        orthogonality = float(np.max(np.abs(
            model.basis.T @ model.basis - np.eye(model.order)
        )))
        require(orthogonality < 2e-12, f"{schedule_name}: basis orthogonality gate failed")
        np.linalg.cholesky(model.conductance_matrix_s)
        np.linalg.cholesky(model.capacitance_matrix_f)

        if schedule_name == "D0_none":
            np.testing.assert_array_equal(model.basis, production_d0.basis)
            np.testing.assert_array_equal(
                model.conductance_matrix_s, production_d0.conductance_matrix_s
            )
            np.testing.assert_array_equal(
                model.capacitance_matrix_f, production_d0.capacitance_matrix_f
            )
            np.testing.assert_array_equal(model.input_matrix, production_d0.input_matrix)

        matrix_hashes = _validate_schedule_hashes(schedule_name, model, scenario_name)
        reduced_trace, reduced_terminal = simulate_reduced_outputs(
            model, seven_layout, output_rows, protocol
        )
        models[schedule_name] = model
        traces[schedule_name] = (reduced_trace, reduced_terminal)

        for window_ms in WINDOWS_MS:
            sample_count = int(round(window_ms / DT_MS))
            for output_index, _tree_index in enumerate(output_tree_indices):
                if output_index < 7:
                    output_role = "shared_output"
                    output_label = f"shared_{output_index + 1}"
                    swc_node_id = int(shared_node_ids[output_index])
                else:
                    output_role = "q25_output"
                    output_label = "basal_q25" if output_index == 7 else "apical_q25"
                    swc_node_id = int(q25_node_ids[output_label])
                for column, (source_name, pulse_width_ms) in enumerate(protocol):
                    full_values = full_trace[:sample_count, output_index, column]
                    reduced_values = reduced_trace[:sample_count, output_index, column]
                    error = nrmse_percent(full_values, reduced_values)
                    case_rows.append({
                        "morphology": spec["name"],
                        "neuromorpho_id": MORPHOLOGY_ID,
                        "scenario": scenario_name,
                        "schedule": schedule_name,
                        "seed_role": seed_role,
                        "dual_seed_frequencies_hz": ";".join(str(x) for x in dual_frequencies),
                        "basis_order": model.order,
                        "window_ms": window_ms,
                        "source": source_name,
                        "pulse_width_ms": pulse_width_ms,
                        "output_role": output_role,
                        "output_label": output_label,
                        "swc_node_id": swc_node_id,
                        "transient_nrmse_pct": error,
                    })

        metadata_rows.append({
            "morphology": spec["name"],
            "neuromorpho_id": MORPHOLOGY_ID,
            "scenario": scenario_name,
            "schedule": schedule_name,
            "seed_role": seed_role,
            "seed_node_indices": list(seed_indices),
            "seed_node_roles": [
                "basal_q25" if index == q25_tree_indices["basal_q25"] else "apical_q25"
                for index in seed_indices
            ],
            "dual_seed_frequencies_hz": list(dual_frequencies),
            "initial_input_seed_columns_per_shift": list(
                enriched.diagnostics.input_seed_columns_per_shift
            ),
            "initial_output_seed_columns_per_shift": list(
                enriched.diagnostics.output_seed_columns_per_shift
            ),
            "initial_input_seed_columns": enriched.diagnostics.initial_input_seed_columns,
            "initial_output_seed_columns": enriched.diagnostics.initial_output_seed_columns,
            "actual_order": model.order,
            **matrix_hashes,
            "basis_orthogonality_max_abs": orthogonality,
            "conductance_condition_number": float(np.linalg.cond(model.conductance_matrix_s)),
            "capacitance_condition_number": float(np.linalg.cond(model.capacitance_matrix_f)),
            "seven_input_ports_unchanged": True,
            "wall_seconds": time.perf_counter() - schedule_started,
        })

    _validate_old_metric_replay(case_rows, scenario_name)
    require(len(case_rows) == len(SCHEDULES) * 2 * 6 * 9,
            f"case row count mismatch: {len(case_rows)}")
    summary_rows = paired_summary(case_rows, group_fields=("scenario", "window_ms"))
    require(len(summary_rows) == len(SCHEDULES) * 2 * 9,
            f"scenario summary row count mismatch: {len(summary_rows)}")

    identity_rows: list[dict[str, Any]] = []
    for schedule_name in IDENTITY_SCHEDULES:
        model = models[schedule_name]
        reduced_trace, reduced_terminal = traces[schedule_name]
        identity_rows.append({
            "morphology": spec["name"],
            "neuromorpho_id": MORPHOLOGY_ID,
            "scenario": scenario_name,
            "schedule": schedule_name,
            **finite_record_identity(
                tree=target,
                model=model,
                full_trace=full_trace,
                full_terminal_states=full_terminal_states,
                reduced_trace=reduced_trace,
                reduced_terminal_states=reduced_terminal,
                output_tree_indices=list(output_tree_indices),
                source_tree_indices=source_tree_indices,
                source_slots=source_slots,
                protocol=protocol,
                window_ms=20.0,
            ),
        })
    require(len(identity_rows) == 5 and all(row["passed"] for row in identity_rows),
            f"{scenario_name}: one or more finite-DFT identity gates failed")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "case_metrics.csv", case_rows)
    write_csv(output_dir / "scenario_summary.csv", summary_rows)
    (output_dir / "worker_report.json").write_text(json.dumps({
        "status": "passed",
        "morphology": spec["name"],
        "neuromorpho_id": MORPHOLOGY_ID,
        "scenario": scenario_name,
        "source": {
            "swc_sha256": source_sha,
            "records": len(morphology.nodes),
            "preflight_status": preflight.get("status"),
            "q25_node_ids": q25_node_ids,
            "shared_node_ids": shared_node_ids,
        },
        "coverage": {
            "case_metrics": len(case_rows),
            "scenario_summary": len(summary_rows),
            "finite_dft_identity": len(identity_rows),
            "basis_metadata": len(metadata_rows),
        },
        "schedule_metadata": metadata_rows,
        "finite_dft_identity": identity_rows,
        "old_run_bit_exact_replay": scenario_name == "nominal",
        "wall_seconds": time.perf_counter() - worker_started,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_manifest(paths: list[Path]) -> list[dict[str, Any]]:
    result = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result.append({"path": path.name, "bytes": path.stat().st_size, "sha256": digest})
    return result


def main() -> None:
    started = time.perf_counter()
    specs = [x for x in core.MORPHOLOGIES if x["neuromorpho_id"] == MORPHOLOGY_ID]
    require(len(specs) == 1, "Jacobs NMO_03524 must resolve exactly once")
    spec = specs[0]
    scenario_names = list(core.SCENARIO_NAMES)
    require(len(scenario_names) == 9, f"expected nine passive scenarios: {scenario_names}")
    require(list(spec["module"].baseline.parameter_cases()) == scenario_names,
            "Jacobs passive scenario names/order differ from the pinned contract")

    temp_root = Path(tempfile.mkdtemp(prefix="prima-q25-jacobs-role-workers-"))
    case_rows: list[dict[str, Any]] = []
    worker_reports: list[dict[str, Any]] = []
    try:
        for index, scenario_name in enumerate(scenario_names, start=1):
            output_dir = temp_root / scenario_name
            command = [
                sys.executable, str(Path(__file__).resolve()),
                "--worker", "--scenario", scenario_name,
                "--output-dir", str(output_dir),
            ]
            completed = subprocess.run(
                command,
                cwd=AMSN_CORE,
                env=os.environ.copy(),
                text=True,
                capture_output=True,
                timeout=30 * 60,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Jacobs worker failed for {scenario_name} (exit={completed.returncode})\n"
                    f"STDOUT:\n{completed.stdout[-12000:]}\nSTDERR:\n{completed.stderr[-18000:]}"
                )
            local_cases = read_csv(output_dir / "case_metrics.csv")
            local_summaries = read_csv(output_dir / "scenario_summary.csv")
            worker_report = json.loads(
                (output_dir / "worker_report.json").read_text(encoding="utf-8")
            )
            require(worker_report["status"] == "passed", f"{scenario_name}: worker status failed")
            require(len(local_cases) == 1080 and len(local_summaries) == 180,
                    f"{scenario_name}: worker exact read-back count mismatch")
            require(all(item["passed"] for item in worker_report["finite_dft_identity"]),
                    f"{scenario_name}: finite DFT identity failure")
            case_rows.extend(local_cases)
            worker_reports.append(worker_report)
            print(json.dumps({
                "worker_completed": index,
                "total_workers": len(scenario_names),
                "scenario": scenario_name,
                "case_rows": len(local_cases),
                "summary_rows": len(local_summaries),
                "worker_seconds": worker_report["wall_seconds"],
            }), flush=True)

        require(len(case_rows) == 9720, f"global case coverage mismatch: {len(case_rows)}")
        case_keys = [(
            row["scenario"], row["schedule"], row["window_ms"],
            row["source"], row["pulse_width_ms"], row["output_label"],
        ) for row in case_rows]
        require(len(case_keys) == len(set(case_keys)), "duplicate global metric keys")
        scenario_summary = paired_summary(case_rows, group_fields=("scenario", "window_ms"))
        pooled_summary = paired_summary(case_rows, group_fields=("window_ms",))
        metadata_rows = [
            row for report in worker_reports for row in report["schedule_metadata"]
        ]
        dft_rows = [
            row for report in worker_reports for row in report["finite_dft_identity"]
        ]
        require(len(scenario_summary) == 1620, f"scenario summary count mismatch: {len(scenario_summary)}")
        require(len(pooled_summary) == 180, f"pooled summary count mismatch: {len(pooled_summary)}")
        require(len(metadata_rows) == 90, f"basis metadata count mismatch: {len(metadata_rows)}")
        require(len(dft_rows) == 45, f"finite DFT identity count mismatch: {len(dft_rows)}")
        require(all(row["passed"] for row in dft_rows), "global finite DFT identity gate failed")

        results_dir = AMSN_CORE / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "case_metrics": results_dir / f"{RESULT_STEM}_case_metrics.csv",
            "scenario_summary": results_dir / f"{RESULT_STEM}_scenario_summary.csv",
            "pooled_summary": results_dir / f"{RESULT_STEM}_pooled_summary.csv",
            "finite_dft_identity": results_dir / f"{RESULT_STEM}_finite_dft_identity.csv",
            "basis_metadata": results_dir / f"{RESULT_STEM}_basis_metadata.json",
            "report": results_dir / f"{RESULT_STEM}_report.json",
            "timing": results_dir / f"{RESULT_STEM}.time.txt",
            "manifest": results_dir / f"{RESULT_STEM}_manifest.json",
        }
        write_csv(paths["case_metrics"], case_rows)
        write_csv(paths["scenario_summary"], scenario_summary)
        write_csv(paths["pooled_summary"], pooled_summary)
        write_csv(paths["finite_dft_identity"], dft_rows)
        paths["basis_metadata"].write_text(
            json.dumps(metadata_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        readbacks = {
            "case_metrics": len(read_csv(paths["case_metrics"])),
            "scenario_summary": len(read_csv(paths["scenario_summary"])),
            "pooled_summary": len(read_csv(paths["pooled_summary"])),
            "finite_dft_identity": len(read_csv(paths["finite_dft_identity"])),
            "basis_metadata": len(json.loads(paths["basis_metadata"].read_text(encoding="utf-8"))),
        }
        expected = {
            "case_metrics": 9720,
            "scenario_summary": 1620,
            "pooled_summary": 180,
            "finite_dft_identity": 45,
            "basis_metadata": 90,
        }
        require(readbacks == expected, f"global exact read-back mismatch: {readbacks}")

        q25_pooled = [
            row for row in pooled_summary if row["output_role"] == "q25_output"
        ]
        baseline_floor = []
        for output_label in ("basal_q25", "apical_q25"):
            for window_ms in WINDOWS_MS:
                values = [
                    float(row["transient_nrmse_pct"]) for row in case_rows
                    if row["schedule"] == "D0_none"
                    and row["output_label"] == output_label
                    and float(row["window_ms"]) == window_ms
                ]
                baseline_floor.append({
                    "output_label": output_label,
                    "window_ms": window_ms,
                    "matched_cases": len(values),
                    "median_D0_nrmse_pct": median(values),
                    "p90_D0_nrmse_pct": float(np.percentile(values, 90)),
                    "max_D0_nrmse_pct": float(max(values)),
                })

        dft_full_max = max(float(row["full_hines_max_relative_error"]) for row in dft_rows)
        dft_reduced_max = max(float(row["reduced_max_relative_error"]) for row in dft_rows)
        report = {
            "schema_version": 1,
            "status": "passed",
            "study": "Jacobs q25 role-specific output-dual seed allocation, order 224",
            "research_only": True,
            "morphology": {
                "name": spec["name"],
                "neuromorpho_id": MORPHOLOGY_ID,
                "records": spec["expected_records"],
                "swc_sha256": spec["expected_sha256"],
                "preflight_status": "PASS",
            },
            "fixed_protocol": {
                "basis_order": ORDER,
                "scenarios": scenario_names,
                "schedule_count": len(SCHEDULES),
                "schedules": {
                    name: {"seed_role": role, "dual_seed_frequencies_hz": list(freqs)}
                    for name, (role, freqs) in SCHEDULES.items()
                },
                "input_ports": 7,
                "output_rows": 9,
                "input_expansion_shifts_hz": list(conditioning.SHIFTS_HZ),
                "sources": list(core.SOURCE_NAMES),
                "pulse_widths_ms": list(core.PULSE_WIDTHS_MS),
                "pulse_onset_ms": 2.0,
                "pulse_amplitude_pA": 10.0,
                "dt_ms": DT_MS,
                "windows_ms": list(WINDOWS_MS),
                "mesh_cap_um": 0.5,
            },
            "coverage": {
                "worker_groups_expected": 9,
                "worker_groups_passed": len(worker_reports),
                "case_metrics_expected": 9720,
                "case_metrics_read_back": readbacks["case_metrics"],
                "scenario_summary_expected": 1620,
                "scenario_summary_read_back": readbacks["scenario_summary"],
                "pooled_summary_expected": 180,
                "pooled_summary_read_back": readbacks["pooled_summary"],
                "finite_dft_identity_expected": 45,
                "finite_dft_identity_read_back": readbacks["finite_dft_identity"],
                "basis_metadata_expected": 90,
                "basis_metadata_read_back": readbacks["basis_metadata"],
                "unique_case_keys": len(set(case_keys)),
            },
            "numerical_gates": {
                "d0_exact_production_parity_all_scenarios": True,
                "prior_nominal_d0_and_both_10k_basis_hashes_match": True,
                "prior_nominal_d0_and_both_10k_case_metrics_bit_exact": True,
                "seven_input_ports_unchanged_all_models": all(
                    row["seven_input_ports_unchanged"] for row in metadata_rows
                ),
                "all_models_reached_order_224": all(
                    row["actual_order"] == ORDER for row in metadata_rows
                ),
                "all_reduced_g_c_cholesky_positive": True,
                "max_basis_orthogonality_abs": max(
                    float(row["basis_orthogonality_max_abs"]) for row in metadata_rows
                ),
                "all_finite_dft_identities_passed": all(row["passed"] for row in dft_rows),
                "finite_dft_tolerance": DFT_TOLERANCE,
                "max_full_hines_identity_relative_error": dft_full_max,
                "max_reduced_identity_relative_error": dft_reduced_max,
            },
            "q25_pooled_paired_summary": q25_pooled,
            "d0_absolute_error_floor": baseline_floor,
            "results_files": {key: path.name for key, path in paths.items() if key != "manifest"},
            "scientific_limits": [
                "One individual Jacobs human control reconstruction, not a biological population.",
                "Passive linear-RC model only; no active channels, action potentials, synapses, plasticity or calcium signalling.",
                "Role-specific dual seeds change the state basis only; the canonical seven-port input selector is unchanged.",
                "All nine original passive parameter scenarios are included, but conclusions remain morphology-specific.",
                "Relative ratios must be interpreted with absolute NRMSE and percentage-point deltas because baseline readout error can be close to the numerical floor.",
                "Finite-record DFT identity is checked on the declared soma/2-ms/20-ms record for the five named schedules per scenario.",
                "No production solver, retained-port default or PRIMA order default is changed; full Hines remains canonical.",
            ],
            "runtime": {
                "wall_seconds": time.perf_counter() - started,
                "worker_total_seconds": sum(float(x["wall_seconds"]) for x in worker_reports),
                "max_worker_seconds": max(float(x["wall_seconds"]) for x in worker_reports),
                "numerical_runtime": core.numerical_runtime_diagnostics(),
            },
        }
        paths["report"].write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        paths["timing"].write_text(
            f"elapsed_wall_seconds={report['runtime']['wall_seconds']:.6f}\n"
            f"worker_total_seconds={report['runtime']['worker_total_seconds']:.6f}\n"
            f"worker_count={len(worker_reports)}\nexit_status=0\n",
            encoding="utf-8",
        )
        manifest = {
            "status": "passed",
            "workflow_scope": "Jacobs NMO_03524 role-specific q25 output-dual seed allocation",
            "files": _file_manifest([path for key, path in paths.items() if key != "manifest"]),
            "coverage": readbacks,
            "source_sha256": spec["expected_sha256"],
        }
        paths["manifest"].write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        final_report = json.loads(paths["report"].read_text(encoding="utf-8"))
        require(final_report["status"] == "passed", "final report status mismatch")
        print(json.dumps({
            "status": final_report["status"],
            "coverage": final_report["coverage"],
            "numerical_gates": final_report["numerical_gates"],
            "q25_pooled_paired_summary": final_report["q25_pooled_paired_summary"],
            "runtime": final_report["runtime"],
        }, indent=2, sort_keys=True, allow_nan=False), flush=True)
    finally:
        import shutil
        shutil.rmtree(temp_root, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--scenario")
    parser.add_argument("--output-dir")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.worker:
        require(bool(arguments.scenario and arguments.output_dir),
                "worker mode requires --scenario and --output-dir")
        worker(arguments.scenario, Path(arguments.output_dir))
    else:
        main()
