"""Compare section-resampled passive cables with the full SWC-node cable.

This is a passive numerical reduction experiment on one partial human
morphology. The 8,903-node cable is the reference discretization; all source
and probe nodes are protected so coarse meshes use the exact same sites.
"""
from __future__ import annotations

from pathlib import Path
from time import perf_counter

import numpy as np

from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


DATA = (
    Path(__file__).parents[1]
    / "data"
    / "human"
    / "1094_Mohan_etal_2015.CNG.swc"
)
INJECTED_CURRENT_A = 10e-12
PHYSICAL_CAPS_UM = (100.0, 50.0, 25.0, 12.5)


def path_distances_um(morphology: SWCMorphology) -> dict[int, float]:
    distances = {morphology.root_id: 0.0}
    stack = [morphology.root_id]
    while stack:
        parent_id = stack.pop()
        parent = morphology.nodes[parent_id]
        for child_id in morphology.children[parent_id]:
            child = morphology.nodes[child_id]
            distances[child_id] = distances[parent_id] + float(np.linalg.norm([
                child.x_um-parent.x_um,
                child.y_um-parent.y_um,
                child.z_um-parent.z_um,
            ]))
            stack.append(child_id)
    return distances


def quantile_node(
    morphology: SWCMorphology,
    distances: dict[int, float],
    neurite_type: int,
    quantile: float,
) -> int:
    ordered = sorted(
        (
            (distances[node_id], node_id)
            for node_id, node in morphology.nodes.items()
            if node.neurite_type == neurite_type
        ),
        key=lambda pair: (pair[0], pair[1]),
    )
    return ordered[round((len(ordered)-1)*quantile)][1]


def solve_sites(tree, source_id: int, probe_ids: list[int], mapping: dict[int, str]):
    current = np.zeros(tree.n_compartments, dtype=float)
    source_name = mapping[source_id]
    current[tree.index[source_name]] = INJECTED_CURRENT_A
    voltage = tree.solve_passive_steady_state(current)
    leak = tree.parameters.e_leak_v
    source_delta = float(voltage[tree.index[source_name]] - leak)
    input_resistance = source_delta / INJECTED_CURRENT_A / 1e6
    rows = {}
    for probe_id in probe_ids:
        probe_delta = float(voltage[tree.index[mapping[probe_id]]] - leak)
        rows[probe_id] = (
            probe_delta * 1e3,
            probe_delta / INJECTED_CURRENT_A / 1e6,
            probe_delta / source_delta,
        )
    return source_delta * 1e3, input_resistance, rows


def main() -> None:
    morphology = SWCMorphology.from_file(DATA)
    distances = path_distances_um(morphology)
    root = morphology.root_id
    injections = [
        ("soma", root),
        ("basal_q75", quantile_node(morphology, distances, 3, 0.75)),
        ("apical_q75", quantile_node(morphology, distances, 4, 0.75)),
    ]
    probes = [
        ("soma", root),
        ("basal_q50", quantile_node(morphology, distances, 3, 0.50)),
        ("basal_q90", quantile_node(morphology, distances, 3, 0.90)),
        ("apical_q50", quantile_node(morphology, distances, 4, 0.50)),
        ("apical_q90", quantile_node(morphology, distances, 4, 0.90)),
    ]
    injection_ids = [node_id for _, node_id in injections]
    probe_ids = [node_id for _, node_id in probes]
    protected = set(injection_ids + probe_ids)

    baseline_start = perf_counter()
    baseline = morphology.to_cable_tree()
    baseline_build_seconds = perf_counter() - baseline_start
    baseline_mapping = {node_id: f"swc_{node_id}" for node_id in morphology.nodes}
    reference = {}
    for source_name, source_id in injections:
        source_delta, input_r, probe_rows = solve_sites(
            baseline, source_id, probe_ids, baseline_mapping
        )
        reference[source_id] = (source_delta, input_r, probe_rows)

    print("# NeuroMorpho NMO_290988; partial human L2-3 morphology; no axon")
    print("# generic passive defaults; not human-fitted: Ri=0.7 ohm*m; Rm=1 ohm*m^2; Cm=0.01 F/m^2; Eleak=-65mV")
    print(f"# baseline compartments={baseline.n_compartments}; build_seconds={baseline_build_seconds:.6f}")
    print("# all 7 source/probe nodes are protected and remain exact in every coarse mesh")
    print("max_length_um,d_lambda,compartments,sections,max_mapping_error_um,source,source_swc_id,probe,probe_swc_id,baseline_input_R_MOhm,sectioned_input_R_MOhm,input_error_rel_pct,baseline_transfer_R_MOhm,sectioned_transfer_R_MOhm,transfer_error_rel_pct,baseline_ratio,sectioned_ratio,ratio_error_rel_pct")

    for max_length in PHYSICAL_CAPS_UM:
        start = perf_counter()
        reduced = to_sectioned_cable_tree(
            morphology,
            max_segment_length_um=max_length,
            max_electrotonic_length=0.1,
            reference_frequency_hz=100.0,
            preserve_node_ids=protected,
        )
        build_seconds = perf_counter() - start
        max_mapping_error = max(reduced.swc_node_mapping_error_um.values())
        max_edge_um = max(reduced.edge_arc_length_m.values()) * 1e6
        max_edge_electro = max(reduced.edge_electrotonic_length.values())

        print(
            f"# mesh max_length={max_length:g}; compartments={reduced.tree.n_compartments}; "
            f"sections={reduced.section_count}; build_seconds={build_seconds:.6f}; "
            f"max_mapping_error={max_mapping_error:.6f}um; "
            f"max_edge={max_edge_um:.6f}um; max_electro={max_edge_electro:.8f}"
        )

        mapping = reduced.swc_node_to_compartment
        for source_name, source_id in injections:
            source_delta, input_r, probe_rows = solve_sites(
                reduced.tree, source_id, probe_ids, mapping
            )
            base_source_delta, base_input_r, base_probe_rows = reference[source_id]
            input_error = 100.0 * abs(input_r - base_input_r) / abs(base_input_r)
            for probe_name, probe_id in probes:
                probe_delta, transfer_r, ratio = probe_rows[probe_id]
                base_probe_delta, base_transfer_r, base_ratio = base_probe_rows[probe_id]
                transfer_error = (
                    100.0 * abs(transfer_r - base_transfer_r) / abs(base_transfer_r)
                )
                ratio_error = (
                    100.0 * abs(ratio - base_ratio) / abs(base_ratio)
                    if base_ratio != 0 else 0.0
                )
                print(
                    f"{max_length:g},0.1,{reduced.tree.n_compartments},"
                    f"{reduced.section_count},{max_mapping_error:.6f},"
                    f"{source_name},{source_id},{probe_name},{probe_id},"
                    f"{base_input_r:.9f},{input_r:.9f},{input_error:.9f},"
                    f"{base_transfer_r:.9f},{transfer_r:.9f},{transfer_error:.9f},"
                    f"{base_ratio:.9f},{ratio:.9f},{ratio_error:.9f}"
                )


if __name__ == "__main__":
    main()
