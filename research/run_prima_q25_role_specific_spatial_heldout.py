#!/usr/bin/env python3
"""Four-morphology role-specific q25 output-dual seed sweep.

Each isolated worker compares D0, basal-only, apical-only and joint 10 kHz
output-dual seeds at order 224 while retaining the original seven input ports.
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

from amsn.ports import path_distances_um, quantile_node

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
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
RESULT_STEM = "prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout_order224_2026-11-26"
DFT_TOLERANCE = 2e-8
ROLE_SPECIFIC_SCHEDULES: dict[str, tuple[str, tuple[float, ...]]] = {
    "D0_none": ("none", ()),
    "BASAL_10K": ("basal", (10000.0,)),
    "APICAL_10K": ("apical", (10000.0,)),
    "BOTH_10K": ("both", (10000.0,)),
}
IDENTITY_SCHEDULES = tuple(ROLE_SPECIFIC_SCHEDULES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def resolve_preflight_path(spec: dict[str, Any]) -> Path:
    """Resolve registry preflight paths against the AMSN core checkout.

    Registry paths are relative to the AMSN core directory. The parent sweep
    runs from the repository root, while isolated workers use AMSN core as cwd.
    """
    path = Path(spec["preflight"])
    if not path.is_absolute():
        path = AMSN_CORE / path
    return path.resolve()


def run_worker_with_sigsegv_retry(
    command: list[str],
    *,
    worker_label: str,
    output_dir: Path,
    max_sigsegv_retries: int = 2,
) -> tuple[subprocess.CompletedProcess[str], int]:
    """Retry only an isolated worker terminated by SIGSEGV (exit -11).

    Each retry starts with a clean output directory. Other non-zero exits
    remain fail-fast; child stdout/stderr stream directly to the Actions log.
    """
    require(max_sigsegv_retries >= 0, "max_sigsegv_retries must be non-negative")
    for attempt in range(1, max_sigsegv_retries + 2):
        if attempt > 1:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
        completed = subprocess.run(
            command,
            cwd=AMSN_CORE,
            env=os.environ.copy(),
            text=True,
            # Inherit stdout/stderr so worker stage markers stream live to Actions.
            # Capturing the full child output hid all progress until a worker exited.
            timeout=30 * 60,
            check=False,
        )
        if completed.returncode == 0:
            return completed, attempt
        if completed.returncode == -11 and attempt <= max_sigsegv_retries:
            print(json.dumps({
                "event": "worker_sigsegv_retry",
                "worker": worker_label,
                "attempt": attempt,
                "max_attempts": max_sigsegv_retries + 1,
                "output_mode": "worker stdout/stderr streamed directly to the Actions log",
            }), flush=True)
            continue
        stdout_tail = (
            completed.stdout[-12000:]
            if isinstance(completed.stdout, str)
            else "(streamed directly to the Actions log)"
        )
        stderr_tail = (
            completed.stderr[-18000:]
            if isinstance(completed.stderr, str)
            else "(streamed directly to the Actions log)"
        )
        raise RuntimeError(
            f"worker failed for {worker_label} (exit={completed.returncode})"
            f" after {attempt} attempt(s)\nSTDOUT:\n{stdout_tail}\n"
            f"STDERR:\n{stderr_tail}"
        )
    raise AssertionError("unreachable worker retry state")


def cleanup_worker_checkpoints(temp_root: Path, archive_completed: bool) -> None:
    """Delete scratch workers only after a complete global archive was written."""
    if archive_completed:
        import shutil
        shutil.rmtree(temp_root, ignore_errors=True)
    else:
        print(json.dumps({
            "event": "partial_worker_checkpoints_preserved",
            "worker_directories": sum(1 for item in temp_root.glob("*/*") if item.is_dir()),
        }), flush=True)


def seed_indices_for_role(
    q25_tree_indices: dict[str, int], seed_role: str
) -> tuple[int, ...]:
    """Return q25 observation coordinates for the declared output-seed role."""
    require(
        set(q25_tree_indices) == {"basal_q25", "apical_q25"},
        f"expected both q25 observation indices, got {sorted(q25_tree_indices)}",
    )
    if seed_role in {"none", "both"}:
        # D0 still measures both q25 rows, but has no output-dual seed frequencies.
        return (
            int(q25_tree_indices["basal_q25"]),
            int(q25_tree_indices["apical_q25"]),
        )
    if seed_role == "basal":
        return (int(q25_tree_indices["basal_q25"]),)
    if seed_role == "apical":
        return (int(q25_tree_indices["apical_q25"]),)
    raise ValueError(f"unknown q25 seed role: {seed_role}")


HELDOUT_SPATIAL_SITES = (
    ("basal_q10", 3, 0.10),
    ("basal_q95", 3, 0.95),
    ("apical_q10", 4, 0.10),
    ("apical_q95", 4, 0.95),
)


def validate_heldout_spatial_node_ids(
    shared_node_ids: list[int],
    q25_node_ids: dict[str, int],
    heldout_node_ids: dict[str, int],
) -> None:
    """Require four distinct held-out readouts outside fitted/retained sites."""
    expected = {name for name, _branch, _quantile in HELDOUT_SPATIAL_SITES}
    if set(heldout_node_ids) != expected:
        raise ValueError("held-out spatial probe labels do not match the preregistered set")
    if set(q25_node_ids) != {"basal_q25", "apical_q25"}:
        raise ValueError("both q25 target nodes must be present")
    values = [int(value) for value in heldout_node_ids.values()]
    if len(values) != len(set(values)):
        raise ValueError("held-out spatial probes must map to four unique SWC nodes")
    occupied = {int(value) for value in shared_node_ids}
    occupied.update(int(value) for value in q25_node_ids.values())
    if occupied.intersection(values):
        raise ValueError("held-out spatial probes collide with shared or q25 target nodes")


def reference_path_distances_um(morphology) -> dict[int, float]:
    """Match the legacy fine-mesh mapper's NumPy path-length arithmetic exactly."""
    distances = {morphology.root_id: 0.0}
    stack = [morphology.root_id]
    while stack:
        parent_id = stack.pop()
        parent = morphology.nodes[parent_id]
        for child_id in morphology.children[parent_id]:
            child = morphology.nodes[child_id]
            distances[child_id] = distances[parent_id] + float(np.linalg.norm([
                child.x_um - parent.x_um,
                child.y_um - parent.y_um,
                child.z_um - parent.z_um,
            ]))
            stack.append(child_id)
    require(len(distances) == len(morphology.nodes),
            "legacy-compatible path traversal missed SWC nodes")
    return distances


PINNED_SPATIAL_SITE_IDS = {
    "NMO_163775": {
        "basal_q10": 7, "basal_q95": 94,
        "apical_q10": 3967, "apical_q95": 4042,
    },
    "NMO_107159": {
        "basal_q10": 6739, "basal_q95": 7206,
        "apical_q10": 4355, "apical_q95": 4820,
    },
    "NMO_03524": {
        "basal_q10": 631, "basal_q95": 702,
        "apical_q10": 863, "apical_q95": 869,
    },
}
PINNED_Q25_NODE_IDS = {
    "NMO_163775": {"basal_q25": 224, "apical_q25": 4096},
    "NMO_107159": {"basal_q25": 6609, "apical_q25": 4404},
    "NMO_03524": {"basal_q25": 272, "apical_q25": 864},
}


def build_four_layouts_from_swc(morphology, base_tree):
    """Build canonical seven inputs and q25 readouts directly from SWC.

    The seven legacy ports use the exact NumPy path-length arithmetic from
    the original fine-mesh mapper. The q25 targets use amsn.ports arithmetic,
    matching the original output-enrichment mapper. Import3D is not needed by
    the passive CableTree reduction and is deliberately excluded here.
    """
    canonical_distances = reference_path_distances_um(morphology)
    output_distances = path_distances_um(morphology)
    injections = [
        ("soma", morphology.root_id),
        ("basal_q75", int(quantile_node(morphology, canonical_distances, 3, 0.75))),
        ("apical_q75", int(quantile_node(morphology, canonical_distances, 4, 0.75))),
    ]
    probes = [
        ("soma", morphology.root_id),
        ("basal_q50", int(quantile_node(morphology, canonical_distances, 3, 0.50))),
        ("basal_q90", int(quantile_node(morphology, canonical_distances, 3, 0.90))),
        ("apical_q50", int(quantile_node(morphology, canonical_distances, 4, 0.50))),
        ("apical_q90", int(quantile_node(morphology, canonical_distances, 4, 0.90))),
    ]
    source_ids = {name: int(node_id) for name, node_id in injections}
    require(set(source_ids) == set(SOURCE_NAMES),
            f"SWC source locations are incomplete: {source_ids}")
    q25_node_ids = {
        "basal_q25": int(quantile_node(morphology, output_distances, 3, 0.25)),
        "apical_q25": int(quantile_node(morphology, output_distances, 4, 0.25)),
    }
    node_ids = list(dict.fromkeys(
        int(node_id) for _role, node_id in injections + probes
    ))
    require(len(node_ids) == 7 and len(set(node_ids)) == 7,
            f"canonical shared SWC selector must contain seven distinct nodes: {node_ids}")
    require(len(set(q25_node_ids.values())) == 2,
            f"q25 SWC target nodes are not distinct: {q25_node_ids}")
    require(not set(node_ids).intersection(q25_node_ids.values()),
            "q25 SWC target nodes collide with the canonical seven")
    electrical_map = morphology.electrical_node_mapping()
    ports = [
        int(base_tree.index[f"swc_{electrical_map[node_id]}"])
        for node_id in node_ids
    ]
    require(len(set(ports)) == 7,
            "canonical seven SWC nodes do not map to seven distinct electrical ports")
    source_indices = {
        source_name: node_ids.index(node_id)
        for source_name, node_id in source_ids.items()
    }
    roles: dict[int, list[str]] = {node_id: [] for node_id in node_ids}
    for role, node_id in injections + probes:
        if role not in roles[int(node_id)]:
            roles[int(node_id)].append(role)
    seven_layout = {
        "layout_id": "seven",
        "port_count": 7,
        "node_ids": node_ids,
        "ports": ports,
        "roles": roles,
        "source_ids": source_ids,
        "source_indices": source_indices,
    }
    return {"seven": seven_layout}, node_ids, q25_node_ids


def build_heldout_spatial_outputs(
    morphology,
    base_tree,
    shared_node_ids: list[int],
    q25_node_ids: dict[str, int],
) -> list[dict[str, Any]]:
    """Map q10/q95 readouts without using them as input or output-dual seeds."""
    distances = path_distances_um(morphology)
    heldout_node_ids = {
        name: int(quantile_node(morphology, distances, branch, quantile))
        for name, branch, quantile in HELDOUT_SPATIAL_SITES
    }
    validate_heldout_spatial_node_ids(shared_node_ids, q25_node_ids, heldout_node_ids)
    electrical_map = morphology.electrical_node_mapping()
    outputs = []
    for name, branch, quantile in HELDOUT_SPATIAL_SITES:
        swc_node_id = heldout_node_ids[name]
        electrical_index = electrical_map[swc_node_id]
        outputs.append({
            "output_role": "heldout_spatial_output",
            "output_label": name,
            "swc_node_id": swc_node_id,
            "tree_index": int(base_tree.index[f"swc_{electrical_index}"]),
            "branch_class": "basal" if branch == 3 else "apical",
            "path_distance_quantile": quantile,
        })
    return outputs


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def summarize_paired_rows(
    rows: list[dict[str, Any]],
    *,
    group_fields: tuple[str, ...],
    include_output: bool = True,
) -> list[dict[str, Any]]:
    """Summarize case-level candidate/D0 errors without pooling ratios of medians."""
    baseline: dict[tuple[Any, ...], float] = {}
    for row in rows:
        if row["schedule"] != "D0_none":
            continue
        key = (
            row["morphology"], row["scenario"], row["window_ms"],
            row["source"], row["pulse_width_ms"], row["output_label"],
        )
        require(key not in baseline, f"duplicate D0 paired key: {key}")
        baseline[key] = float(row["transient_nrmse_pct"])

    grouped: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(list)
    output_meta: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        schedule = row["schedule"]
        key = (
            row["morphology"], row["scenario"], row["window_ms"],
            row["source"], row["pulse_width_ms"], row["output_label"],
        )
        ref = baseline.get(key)
        require(ref is not None, f"missing matched D0 value: {key}")
        candidate = float(row["transient_nrmse_pct"])
        ratio = candidate / max(ref, 1e-30)
        delta = candidate - ref
        gkey_values = {field: row[field] for field in group_fields}
        gkey_values["schedule"] = schedule
        if include_output:
            gkey_values["output_role"] = row["output_role"]
            gkey_values["output_label"] = row["output_label"]
        gkey = tuple(gkey_values[field] for field in (
            *group_fields, "schedule",
            *(("output_role", "output_label") if include_output else ()),
        ))
        grouped[gkey].append((ratio, delta))
        output_meta[gkey] = gkey_values

    result: list[dict[str, Any]] = []
    for key, pairs in sorted(grouped.items(), key=lambda item: tuple(str(x) for x in item[0])):
        ratios = [x[0] for x in pairs]
        deltas = [x[1] for x in pairs]
        meta = output_meta[key]
        result.append({
            **meta,
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


def worker(morphology_id: str, scenario_name: str, output_dir: Path) -> None:
    """Run one morphology/parameter-scenario group in a clean process."""
    worker_started = time.perf_counter()
    import analyze_prima_q25_four_morphology_four_layout_boundary_ablation as core
    import audit_prima_q25_basis_conditioning as conditioning
    import audit_prima_q25_extended_backward_euler as tail

    specs = [x for x in core.MORPHOLOGIES if x["neuromorpho_id"] == morphology_id]
    require(len(specs) == 1, f"morphology ID must resolve exactly once: {morphology_id}")
    spec = specs[0]
    module = spec["module"]
    baseline = module.baseline

    scenarios = baseline.parameter_cases()
    require(scenario_name in scenarios, f"{morphology_id}: unknown scenario {scenario_name}")
    morphology = baseline.SWCMorphology.from_file(module.SWC)
    require(len(morphology.nodes) == spec["expected_records"],
            f"{morphology_id}: SWC record count mismatch")
    source_sha = hashlib.sha256(module.SWC.read_bytes()).hexdigest()
    require(source_sha == spec["expected_sha256"],
            f"{morphology_id}: SWC checksum mismatch")
    preflight_path = resolve_preflight_path(spec)
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    require(preflight.get("status") == "PASS", f"{morphology_id}: source preflight did not pass")
    require(preflight.get("source", {}).get("source_sha256") == source_sha,
            f"{morphology_id}: preflight checksum mismatch")

    print(json.dumps({"stage":"before_swc_only_layout","morphology":morphology_id,"scenario":scenario_name}), flush=True)
    base_tree = morphology.to_cable_tree()
    layouts, shared_node_ids, q25_node_ids = build_four_layouts_from_swc(
        morphology, base_tree
    )
    print(json.dumps({"stage":"after_swc_only_layout","morphology":morphology_id,"scenario":scenario_name}), flush=True)
    require(set(layouts) >= {"seven"}, f"{morphology_id}: seven-port layout missing")
    seven_layout = layouts["seven"]
    retained_indices = tuple(int(x) for x in seven_layout["ports"])
    require(len(retained_indices) == 7 and len(set(retained_indices)) == 7,
            f"{morphology_id}: canonical input selector is not exactly seven unique ports")
    source_tree_indices = [
        int(seven_layout["ports"][int(seven_layout["source_indices"][source])])
        for source in SOURCE_NAMES
    ]
    electrical_map = morphology.electrical_node_mapping()
    q25_tree_indices = {
        role: int(base_tree.index[f"swc_{electrical_map[int(node_id)]}"])
        for role, node_id in q25_node_ids.items()
    }
    heldout_sites = build_heldout_spatial_outputs(
        morphology, base_tree, list(shared_node_ids), q25_node_ids
    )
    pinned_q25 = PINNED_Q25_NODE_IDS.get(morphology_id)
    if pinned_q25 is not None:
        require(q25_node_ids == pinned_q25,
                f"{morphology_id}: q25 SWC mapping differs from pinned historical nodes: {q25_node_ids}")
    pinned_spatial = PINNED_SPATIAL_SITE_IDS.get(morphology_id)
    if pinned_spatial is not None:
        observed_spatial = {
            site["output_label"]: site["swc_node_id"] for site in heldout_sites
        }
        require(observed_spatial == pinned_spatial,
                f"{morphology_id}: spatial holdout mapping changed: {observed_spatial}")
    output_tree_indices = (
        retained_indices
        + (q25_tree_indices["basal_q25"], q25_tree_indices["apical_q25"])
        + tuple(site["tree_index"] for site in heldout_sites)
    )
    output_descriptors = [
        {
            "output_role": "shared_output",
            "output_label": f"shared_{index + 1}",
            "swc_node_id": int(shared_node_ids[index]),
        }
        for index in range(7)
    ] + [
        {
            "output_role": "q25_output",
            "output_label": role,
            "swc_node_id": int(q25_node_ids[role]),
        }
        for role in ("basal_q25", "apical_q25")
    ] + [
        {key: site[key] for key in ("output_role", "output_label", "swc_node_id")}
        for site in heldout_sites
    ]
    require(len(shared_node_ids) == 7 and len(output_tree_indices) == 13,
            f"{morphology_id}: expected 7 shared, 2 q25 and 4 held-out outputs")
    require(len(set(output_tree_indices)) == 13,
            f"{morphology_id}: output observation sites must be distinct")

    target = conditioning.build_target_tree(module, base_tree, scenarios[scenario_name])
    source_slots = {
        source: int(seven_layout["source_indices"][source]) for source in SOURCE_NAMES
    }

    # Build and verify the canonical D0 model before invoking native full-Hines.
    print(json.dumps({"stage":"before_production_d0","morphology":morphology_id,"scenario":scenario_name}), flush=True)
    production_d0 = baseline.prima_reduce_passive_cable_multishift(
        target, list(retained_indices), ORDER, conditioning.SHIFTS_HZ,
        relative_tolerance=conditioning.RELATIVE_TOLERANCE,
    )
    print(json.dumps({"stage":"after_production_d0","morphology":morphology_id,"scenario":scenario_name}), flush=True)

    hines_factor = tail.build_tree_hines_be_factor(target, DT_S)
    print(json.dumps({"stage":"before_full_hines","morphology":morphology_id,"scenario":scenario_name}), flush=True)
    full_trace, full_terminal_states, protocol = core.simulate_full_hines_perturbation_windows(
        target, hines_factor, source_tree_indices, list(output_tree_indices)
    )
    print(json.dumps({"stage":"after_full_hines","morphology":morphology_id,"scenario":scenario_name}), flush=True)
    case_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    schedule_metadata: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    model_traces: dict[str, Any] = {}
    for schedule_name, (seed_role, dual_frequencies) in ROLE_SPECIFIC_SCHEDULES.items():
        schedule_started = time.perf_counter()
        seed_indices = seed_indices_for_role(q25_tree_indices, seed_role)
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
        require(model.order == ORDER,
                f"{morphology_id}/{scenario_name}/{schedule_name}: order mismatch")
        require(tuple(model.port_indices) == retained_indices,
                f"{morphology_id}/{scenario_name}/{schedule_name}: input ports changed")
        require(model.input_matrix.shape == (ORDER, 7),
                f"{morphology_id}/{scenario_name}/{schedule_name}: input matrix shape mismatch")
        np.testing.assert_array_equal(
            model.input_matrix, model.basis[np.asarray(retained_indices), :].T
        )
        output_rows = model.basis[np.asarray(output_tree_indices), :]
        require(output_rows.shape == (13, ORDER),
                f"{morphology_id}/{scenario_name}/{schedule_name}: output map shape mismatch")

        orthogonality = float(np.max(np.abs(
            model.basis.T @ model.basis - np.eye(model.order)
        )))
        require(orthogonality < 2e-12,
                f"{morphology_id}/{scenario_name}/{schedule_name}: orthogonality failed")
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

        reduced_trace, reduced_terminal = simulate_reduced_outputs(
            model, seven_layout, output_rows, protocol
        )
        models[schedule_name] = model
        model_traces[schedule_name] = (reduced_trace, reduced_terminal)

        for window_ms in WINDOWS_MS:
            sample_count = int(round(window_ms / DT_MS))
            for output_index, descriptor in enumerate(output_descriptors):
                for column, (source_name, pulse_width_ms) in enumerate(protocol):
                    full_values = full_trace[:sample_count, output_index, column]
                    reduced_values = reduced_trace[:sample_count, output_index, column]
                    case_rows.append({
                        "morphology": spec["name"],
                        "neuromorpho_id": morphology_id,
                        "scenario": scenario_name,
                        "schedule": schedule_name,
                        "seed_role": seed_role,
                        "dual_seed_frequencies_hz": ";".join(str(x) for x in dual_frequencies),
                        "basis_order": model.order,
                        "window_ms": window_ms,
                        "source": source_name,
                        "pulse_width_ms": pulse_width_ms,
                        **descriptor,
                        "transient_nrmse_pct": nrmse_percent(full_values, reduced_values),
                    })

        schedule_metadata.append({
            "morphology": spec["name"],
            "neuromorpho_id": morphology_id,
            "scenario": scenario_name,
            "schedule": schedule_name,
            "seed_role": seed_role,
            "seed_node_indices": list(seed_indices) if dual_frequencies else [],
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
            "shared_swc_node_ids": [int(node_id) for node_id in shared_node_ids],
            "q25_swc_node_ids": {
                role: int(node_id) for role, node_id in q25_node_ids.items()
            },
            "heldout_spatial_sites": [
                {
                    "output_role": site["output_role"],
                    "output_label": site["output_label"],
                    "swc_node_id": int(site["swc_node_id"]),
                    "tree_index": int(site["tree_index"]),
                    "branch_class": site["branch_class"],
                    "path_distance_quantile": float(site["path_distance_quantile"]),
                }
                for site in heldout_sites
            ],
            "basis_sha256": sha256_array(model.basis),
            "conductance_sha256": sha256_array(model.conductance_matrix_s),
            "capacitance_sha256": sha256_array(model.capacitance_matrix_f),
            "input_sha256": sha256_array(model.input_matrix),
            "basis_orthogonality_max_abs": orthogonality,
            "conductance_condition_number": float(np.linalg.cond(model.conductance_matrix_s)),
            "capacitance_condition_number": float(np.linalg.cond(model.capacitance_matrix_f)),
            "seven_input_ports_unchanged": True,
            "wall_seconds": time.perf_counter() - schedule_started,
        })

    baseline_error: dict[tuple[float, str, float, str], float] = {
        (row["window_ms"], row["source"], row["pulse_width_ms"], row["output_label"]):
            float(row["transient_nrmse_pct"])
        for row in case_rows if row["schedule"] == "D0_none"
    }
    for schedule_name in ROLE_SPECIFIC_SCHEDULES:
        for window_ms in WINDOWS_MS:
            for descriptor in output_descriptors:
                output_role = descriptor["output_role"]
                output_label = descriptor["output_label"]
                local = [
                    row for row in case_rows
                    if row["schedule"] == schedule_name
                    and row["window_ms"] == window_ms
                    and row["output_label"] == output_label
                ]
                ratios: list[float] = []
                deltas: list[float] = []
                for row in local:
                    ref = baseline_error[
                        (window_ms, row["source"], row["pulse_width_ms"], output_label)
                    ]
                    got = float(row["transient_nrmse_pct"])
                    ratios.append(got / max(ref, 1e-30))
                    deltas.append(got - ref)
                summary_rows.append({
                    "morphology": spec["name"],
                    "neuromorpho_id": morphology_id,
                    "scenario": scenario_name,
                    "schedule": schedule_name,
                    "window_ms": window_ms,
                    "output_role": output_role,
                    "output_label": output_label,
                    "matched_cases": len(local),
                    "median_candidate_over_D0_error_ratio": median(ratios),
                    "p90_candidate_over_D0_error_ratio": float(np.percentile(ratios, 90)),
                    "worst_candidate_over_D0_error_ratio": float(max(ratios)),
                    "median_absolute_error_delta_percentage_points": median(deltas),
                    "max_abs_error_delta_percentage_points": float(max(abs(x) for x in deltas)),
                    "candidate_better_cases": sum(x < 0 for x in deltas),
                    "candidate_worse_cases": sum(x > 0 for x in deltas),
                })

    identity_rows: list[dict[str, Any]] = []
    for schedule_name in IDENTITY_SCHEDULES:
        model = models[schedule_name]
        reduced_trace, reduced_terminal = model_traces[schedule_name]
        identity_rows.append({
            "morphology": spec["name"],
            "neuromorpho_id": morphology_id,
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
    require(all(x["passed"] for x in identity_rows),
            f"{morphology_id}/{scenario_name}: finite-DFT identity failed")
    require(len(case_rows) == 624,
            f"{morphology_id}/{scenario_name}: expected 624 case rows, got {len(case_rows)}")
    require(len(summary_rows) == 104,
            f"{morphology_id}/{scenario_name}: expected 104 summaries, got {len(summary_rows)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "case_metrics.csv", case_rows)
    write_csv(output_dir / "summary.csv", summary_rows)
    (output_dir / "worker_report.json").write_text(json.dumps({
        "status": "passed",
        "morphology": spec["name"],
        "neuromorpho_id": morphology_id,
        "scenario": scenario_name,
        "source": {
            "swc_sha256": source_sha,
            "records": len(morphology.nodes),
            "preflight_status": preflight.get("status"),
            "q25_node_ids": q25_node_ids,
            "shared_node_ids": shared_node_ids,
            "heldout_spatial_sites": heldout_sites,
        },
        "coverage": {"case_metrics": len(case_rows), "summary": len(summary_rows)},
        "numerical_gates": {
            "d0_exact_production_parity": True,
            "all_reduced_g_c_cholesky_positive": True,
            "all_models_order224": all(item["actual_order"] == ORDER for item in schedule_metadata),
            "all_seven_input_ports_unchanged": all(
                item["seven_input_ports_unchanged"] for item in schedule_metadata
            ),
            "max_basis_orthogonality_abs": max(
                item["basis_orthogonality_max_abs"] for item in schedule_metadata
            ),
        },
        "schedule_metadata": schedule_metadata,
        "finite_dft_identity": identity_rows,
        "wall_seconds": time.perf_counter() - worker_started,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def worker_cli(args: argparse.Namespace) -> None:
    worker(args.morphology, args.scenario, Path(args.output_dir))


def main() -> None:
    import analyze_prima_q25_four_morphology_four_layout_boundary_ablation as core

    started = time.perf_counter()
    specs = list(core.MORPHOLOGIES)
    require(len(specs) == 4, f"expected four morphology specs, found {len(specs)}")
    scenario_names = list(core.SCENARIO_NAMES)
    require(len(scenario_names) == 9, f"expected nine passive scenarios, found {len(scenario_names)}")
    for spec in specs:
        current = list(spec["module"].baseline.parameter_cases())
        require(current == scenario_names,
                f"{spec['neuromorpho_id']}: passive scenario contract differs from the pinned set")

    temp_root = Path(tempfile.mkdtemp(prefix="prima-q25-dual-seed-workers-"))
    case_rows: list[dict[str, Any]] = []
    group_summary_rows: list[dict[str, Any]] = []
    worker_reports: list[dict[str, Any]] = []
    worker_count = 0
    archive_completed = False
    try:
        for spec in specs:
            morphology_id = spec["neuromorpho_id"]
            for scenario in scenario_names:
                worker_count += 1
                group_dir = temp_root / morphology_id / scenario
                command = [
                    sys.executable, "-X", "faulthandler",
                    str(Path(__file__).resolve()),
                    "--worker", "--morphology", morphology_id,
                    "--scenario", scenario, "--output-dir", str(group_dir),
                ]
                print(json.dumps({
                    "worker_started": worker_count,
                    "total_workers": len(specs) * len(scenario_names),
                    "morphology": morphology_id,
                    "scenario": scenario,
                }), flush=True)
                completed, worker_attempts = run_worker_with_sigsegv_retry(
                    command,
                    worker_label=f"{morphology_id}/{scenario}",
                    output_dir=group_dir,
                )
                case_local = read_csv(group_dir / "case_metrics.csv")
                summary_local = read_csv(group_dir / "summary.csv")
                report_local = json.loads(
                    (group_dir / "worker_report.json").read_text(encoding="utf-8")
                )
                require(report_local["status"] == "passed",
                        f"{morphology_id}/{scenario}: worker report status not passed")
                report_local["worker_process_attempts"] = worker_attempts
                require(len(case_local) == 624 and len(summary_local) == 104,
                        f"{morphology_id}/{scenario}: worker read-back mismatch")
                require(all(x["passed"] for x in report_local["finite_dft_identity"]),
                        f"{morphology_id}/{scenario}: worker DFT identity not passed")
                case_rows.extend(case_local)
                group_summary_rows.extend(summary_local)
                worker_reports.append(report_local)
                print(json.dumps({
                    "worker_completed": worker_count,
                    "total_workers": len(specs) * len(scenario_names),
                    "morphology": morphology_id,
                    "scenario": scenario,
                    "case_rows": len(case_local),
                    "summary_rows": len(summary_local),
                    "worker_seconds": report_local["wall_seconds"],
                }), flush=True)

        expected_case = len(specs) * len(scenario_names) * 624
        expected_group_summary = len(specs) * len(scenario_names) * 104
        require(len(case_rows) == expected_case,
                f"global case coverage mismatch: expected {expected_case}, got {len(case_rows)}")
        require(len(group_summary_rows) == expected_group_summary,
                f"group-summary coverage mismatch: expected {expected_group_summary}, got {len(group_summary_rows)}")

        case_keys = [
            (row["morphology"], row["neuromorpho_id"], row["scenario"],
             row["schedule"], row["window_ms"], row["source"],
             row["pulse_width_ms"], row["output_label"])
            for row in case_rows
        ]
        require(len(case_keys) == len(set(case_keys)),
                "duplicate global case metric keys")
        worker_gates = [item["numerical_gates"] for item in worker_reports]
        require(all(item["d0_exact_production_parity"] for item in worker_gates),
                "D0 production parity gate failed")
        require(all(item["all_reduced_g_c_cholesky_positive"] for item in worker_gates),
                "one or more reduced G/C matrices failed Cholesky")
        require(all(item["all_models_order224"] for item in worker_gates),
                "one or more role-specific models did not reach order 224")
        require(all(item["all_seven_input_ports_unchanged"] for item in worker_gates),
                "seven input-port selector changed in one or more models")

        per_morphology = summarize_paired_rows(
            case_rows, group_fields=("morphology", "window_ms")
        )
        per_scenario = summarize_paired_rows(
            case_rows, group_fields=("scenario", "window_ms")
        )
        pooled = summarize_paired_rows(
            case_rows, group_fields=("window_ms",)
        )
        dft_rows = [
            identity
            for report in worker_reports
            for identity in report["finite_dft_identity"]
        ]
        schedule_metadata = [
            item
            for report in worker_reports
            for item in report["schedule_metadata"]
        ]
        require(len(per_morphology) == 416,
                f"per-morphology summary count mismatch: {len(per_morphology)}")
        require(len(per_scenario) == 936,
                f"per-scenario summary count mismatch: {len(per_scenario)}")
        require(len(pooled) == 104, f"pooled summary count mismatch: {len(pooled)}")
        require(len(dft_rows) == 144, f"finite-DFT identity count mismatch: {len(dft_rows)}")
        require(len(schedule_metadata) == 144,
                f"schedule metadata count mismatch: {len(schedule_metadata)}")

        results_dir = AMSN_CORE / "results"
        case_path = results_dir / f"{RESULT_STEM}_case_metrics.csv"
        group_summary_path = results_dir / f"{RESULT_STEM}_group_summary.csv"
        morphology_summary_path = results_dir / f"{RESULT_STEM}_morphology_summary.csv"
        scenario_summary_path = results_dir / f"{RESULT_STEM}_scenario_summary.csv"
        pooled_summary_path = results_dir / f"{RESULT_STEM}_pooled_summary.csv"
        dft_path = results_dir / f"{RESULT_STEM}_finite_dft_identity.csv"
        metadata_path = results_dir / f"{RESULT_STEM}_basis_metadata.json"
        report_path = results_dir / f"{RESULT_STEM}_report.json"
        timing_path = results_dir / f"{RESULT_STEM}.time.txt"

        write_csv(case_path, case_rows)
        write_csv(group_summary_path, group_summary_rows)
        write_csv(morphology_summary_path, per_morphology)
        write_csv(scenario_summary_path, per_scenario)
        write_csv(pooled_summary_path, pooled)
        write_csv(dft_path, dft_rows)
        metadata_path.write_text(json.dumps(schedule_metadata, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")

        readbacks = {
            case_path.name: len(read_csv(case_path)),
            group_summary_path.name: len(read_csv(group_summary_path)),
            morphology_summary_path.name: len(read_csv(morphology_summary_path)),
            scenario_summary_path.name: len(read_csv(scenario_summary_path)),
            pooled_summary_path.name: len(read_csv(pooled_summary_path)),
            dft_path.name: len(read_csv(dft_path)),
        }
        expected_readbacks = {
            case_path.name: 22464,
            group_summary_path.name: 3744,
            morphology_summary_path.name: 416,
            scenario_summary_path.name: 936,
            pooled_summary_path.name: 104,
            dft_path.name: 144,
        }
        require(readbacks == expected_readbacks,
                f"global CSV read-back mismatch: {readbacks}")

        morphology_manifest = []
        for spec in specs:
            pf = json.loads(resolve_preflight_path(spec).read_text(encoding="utf-8"))
            morphology_manifest.append({
                "name": spec["name"],
                "neuromorpho_id": spec["neuromorpho_id"],
                "expected_swc_sha256": spec["expected_sha256"],
                "expected_records": spec["expected_records"],
                "preflight_status": pf.get("status"),
                "preflight_source_sha256": pf.get("source", {}).get("source_sha256"),
            })
            require(pf.get("status") == "PASS", f"{spec['neuromorpho_id']}: preflight failed")
            require(pf.get("source", {}).get("source_sha256") == spec["expected_sha256"],
                    f"{spec['neuromorpho_id']}: preflight SWC hash mismatch")

        report = {
            "schema_version": 1,
            "status": "passed",
            "study": "Four-morphology nine-scenario PRIMA role-specific q25 output-dual seed order-224 sweep",
            "fixed_protocol": {
                "basis_order": ORDER,
                "morphology_count": len(specs),
                "morphologies": morphology_manifest,
                "passive_scenario_count": len(scenario_names),
                "passive_scenarios": scenario_names,
                "schedules": {
                    key: {"seed_role": role, "dual_seed_frequencies_hz": list(freqs)}
                    for key, (role, freqs) in ROLE_SPECIFIC_SCHEDULES.items()
                },
                "input_ports": 7,
                "output_rows": 13,
                "heldout_spatial_output_labels": [name for name, _branch, _q in HELDOUT_SPATIAL_SITES],
                "heldout_spatial_outputs_are_excluded_from_basis_seeds": True,
                "input_expansion_shifts_hz": list(core.conditioning.SHIFTS_HZ),
                "sources": list(SOURCE_NAMES),
                "pulse_widths_ms": list(core.PULSE_WIDTHS_MS),
                "pulse_onset_ms": 2.0,
                "pulse_amplitude_pA": 10.0,
                "dt_ms": DT_MS,
                "windows_ms": list(WINDOWS_MS),
                "mesh_cap_um": 0.5,
            },
            "coverage": {
                "worker_groups_expected": 36,
                "worker_groups_passed": worker_count,
                "case_metrics_expected": 22464,
                "case_metrics_read_back": readbacks[case_path.name],
                "group_summary_expected": 3744,
                "group_summary_read_back": readbacks[group_summary_path.name],
                "morphology_summary_expected": 416,
                "morphology_summary_read_back": readbacks[morphology_summary_path.name],
                "scenario_summary_expected": 936,
                "scenario_summary_read_back": readbacks[scenario_summary_path.name],
                "pooled_summary_expected": 104,
                "pooled_summary_read_back": readbacks[pooled_summary_path.name],
                "finite_dft_identity_expected": 144,
                "finite_dft_identity_read_back": readbacks[dft_path.name],
                "basis_metadata_rows": len(schedule_metadata),
                "unique_case_keys": len(set(case_keys)),
            },
            "numerical_gates": {
                "d0_exact_production_parity_all_scenarios": all(
                    item["d0_exact_production_parity"] for item in worker_gates
                ),
                "all_reduced_g_c_cholesky_positive": all(
                    item["all_reduced_g_c_cholesky_positive"] for item in worker_gates
                ),
                "all_models_reached_order_224": all(
                    item["all_models_order224"] for item in worker_gates
                ),
                "seven_input_ports_unchanged_all_models": all(
                    item["all_seven_input_ports_unchanged"] for item in worker_gates
                ),
                "max_basis_orthogonality_abs": max(
                    item["max_basis_orthogonality_abs"] for item in worker_gates
                ),
            },
            "dft_identity": {
                "all_rows_passed": all(x["passed"] for x in dft_rows),
                "max_full_hines_relative_error": max(x["full_hines_max_relative_error"] for x in dft_rows),
                "max_reduced_relative_error": max(x["reduced_max_relative_error"] for x in dft_rows),
                "tolerance": DFT_TOLERANCE,
                "scope": "20-ms soma/2-ms record for all four declared schedules in every morphology/scenario group",
            },
            "schedule_metadata": metadata_path.name,
            "files": {
                "case_metrics": case_path.name,
                "group_summary": group_summary_path.name,
                "morphology_summary": morphology_summary_path.name,
                "scenario_summary": scenario_summary_path.name,
                "pooled_summary": pooled_summary_path.name,
                "finite_dft_identity": dft_path.name,
            },
            "scientific_limits": [
                "Four individual morphology reconstructions, not a biological population.",
                "One passive linear-RC model family; no active channels, action potentials, synapses, plasticity or calcium signalling.",
                "Output-dual seeds alter the state basis but the input selector remains exactly seven ports.",
                "Relative ratios must be interpreted with absolute percentage-point deltas because several baseline output errors are near zero.",
                "Basal-only, apical-only and joint schedules alter only state-basis seeds; the seven-port input selector remains unchanged.",
                "Finite-record DFT identity is checked on the declared soma/2-ms/20-ms record for all four schedules in every morphology/scenario group.",
                "This study does not change production solver behavior or defaults; full Hines remains canonical.",
            ],
        }
        report["runtime"] = {
            "wall_seconds": time.perf_counter() - started,
            "worker_total_seconds": sum(float(x["wall_seconds"]) for x in worker_reports),
            "max_worker_seconds": max(float(x["wall_seconds"]) for x in worker_reports),
            "worker_processes": worker_count,
            "github_actions_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_actions_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "worker_process_attempts": [
                int(item.get("worker_process_attempts", 1)) for item in worker_reports
            ],
            "worker_native_sigsegv_retries": sum(
                max(0, int(item.get("worker_process_attempts", 1)) - 1)
                for item in worker_reports
            ),
            "numerical_runtime": core.numerical_runtime_diagnostics(),
        }
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
        timing_path.write_text(
            f"elapsed_wall_seconds={report['runtime']['wall_seconds']:.6f}\n"
            f"worker_total_seconds={report['runtime']['worker_total_seconds']:.6f}\n"
            f"worker_count={worker_count}\nexit_status=0\n",
            encoding="utf-8",
        )
        manifest_path = results_dir / f"{RESULT_STEM}_manifest.json"
        manifest_files = [
            case_path, group_summary_path, morphology_summary_path,
            scenario_summary_path, pooled_summary_path, dft_path,
            metadata_path, report_path, timing_path,
        ]
        manifest = {
            "status": "passed",
            "workflow_scope": "Four-morphology role-specific q25 output-dual seed sweep",
            "source_manifest": morphology_manifest,
            "coverage": readbacks,
            "files": [
                {"path": path.name, "bytes": path.stat().st_size, "sha256": file_sha256(path)}
                for path in manifest_files
            ],
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        verified_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        require(verified_manifest["status"] == "passed", "manifest read-back failed")
        archive_completed = True
        print(json.dumps({
            "status": report["status"],
            "coverage": report["coverage"],
            "dft_identity": report["dft_identity"],
            "report": report_path.name,
            "manifest": manifest_path.name,
        }, indent=2, sort_keys=True))
    finally:
        # Preserve completed worker CSV/JSON checkpoints when any later stage fails.
        # The workflow uploads this directory on failure; remove it only after the
        # global matrices and their checksum manifest have both been written.
        cleanup_worker_checkpoints(temp_root, archive_completed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--morphology")
    parser.add_argument("--scenario")
    parser.add_argument("--output-dir")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.worker:
        require(bool(args.morphology and args.scenario and args.output_dir),
                "worker mode requires morphology, scenario and output-dir")
        worker_cli(args)
    else:
        main()
