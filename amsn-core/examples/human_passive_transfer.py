"""Multi-site DC transfer experiment on one real human L2-3 morphology.

This is a passive, generic-parameter geometry study. It is not a human
electrophysiology fit. The exact linear DC Hines solver avoids allocating
time-by-compartment traces.
"""
from __future__ import annotations

from time import perf_counter
from pathlib import Path

import numpy as np

from amsn.discretization import to_electrotonic_cable_tree
from amsn.morphology import SWCMorphology


DATA = (
    Path(__file__).parents[1]
    / "data"
    / "human"
    / "1094_Mohan_etal_2015.CNG.swc"
)
D_LAMBDA_LEVELS = (0.2, 0.1, 0.05, 0.025)
INJECTED_CURRENT_A = 10e-12


def path_distances_um(morphology: SWCMorphology) -> dict[int, float]:
    """Compute deterministic root-to-node path distances without recursion."""
    distances = {morphology.root_id: 0.0}
    stack = [morphology.root_id]
    while stack:
        parent_id = stack.pop()
        parent = morphology.nodes[parent_id]
        for child_id in morphology.children[parent_id]:
            child = morphology.nodes[child_id]
            edge = float(np.linalg.norm(np.array([
                child.x_um - parent.x_um,
                child.y_um - parent.y_um,
                child.z_um - parent.z_um,
            ])))
            distances[child_id] = distances[parent_id] + edge
            stack.append(child_id)
    return distances


def quantile_node(
    morphology: SWCMorphology,
    distances: dict[int, float],
    neurite_type: int,
    quantile: float,
) -> int:
    candidates = sorted(
        (
            (distances[node_id], node_id)
            for node_id, node in morphology.nodes.items()
            if node.neurite_type == neurite_type
        ),
        key=lambda item: (item[0], item[1]),
    )
    if not candidates:
        raise ValueError(f"morphology has no SWC type {neurite_type} nodes")
    position = round((len(candidates) - 1) * quantile)
    return candidates[position][1]


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

    print("# morphology=NMO_290988; no axon; dendrites=moderate; condition=mesiotemporal_sclerosis")
    print("# passive defaults: Ri=0.7 ohm*m; Rm=1.0 ohm*m^2; Cm=0.01 F/m^2; Eleak=-65 mV")
    print("# exact DC solve: (G_leak + G_axial)V = G_leak*Eleak + I")
    print("# quantiles: sorted root-to-node path distance within SWC type 3 (basal) or 4 (apical)")
    print("d_lambda,compartments,source,source_swc_id,source_path_um,probe,probe_swc_id,probe_path_um,injected_pA,source_delta_mV,probe_delta_mV,input_R_MOhm,transfer_R_MOhm,transfer_ratio")

    for d_lambda in D_LAMBDA_LEVELS:
        build_start = perf_counter()
        cable = to_electrotonic_cable_tree(
            morphology,
            max_electrotonic_length=d_lambda,
            reference_frequency_hz=100.0,
            axial_resistivity_ohm_m=0.7,
            specific_capacitance_f_m2=0.01,
        )
        build_seconds = perf_counter() - build_start
        print(f"# mesh d_lambda={d_lambda:g}; compartments={cable.n_compartments}; build_seconds={build_seconds:.6f}")

        for source_name, source_id in injections:
            current = np.zeros(cable.n_compartments, dtype=float)
            source_index = cable.index[f"swc_{source_id}"]
            current[source_index] = INJECTED_CURRENT_A
            solve_start = perf_counter()
            voltage = cable.solve_passive_steady_state(current)
            solve_seconds = perf_counter() - solve_start
            rest = cable.parameters.e_leak_v
            source_delta = float(voltage[source_index] - rest)
            input_resistance_mohm = source_delta / INJECTED_CURRENT_A / 1e6

            for probe_name, probe_id in probes:
                probe_index = cable.index[f"swc_{probe_id}"]
                probe_delta = float(voltage[probe_index] - rest)
                transfer_resistance_mohm = probe_delta / INJECTED_CURRENT_A / 1e6
                transfer_ratio = probe_delta / source_delta
                print(
                    f"{d_lambda:g},{cable.n_compartments},"
                    f"{source_name}:{morphology.nodes[source_id].neurite_type}:{source_id},"
                    f"{source_id},{distances[source_id]:.6f},"
                    f"{probe_name}:{morphology.nodes[probe_id].neurite_type}:{probe_id},"
                    f"{probe_id},{distances[probe_id]:.6f},"
                    f"{INJECTED_CURRENT_A*1e12:.3f},"
                    f"{source_delta*1e3:.9f},{probe_delta*1e3:.9f},"
                    f"{input_resistance_mohm:.9f},"
                    f"{transfer_resistance_mohm:.9f},{transfer_ratio:.9f}"
                )
            print(f"# solve source={source_name}; seconds={solve_seconds:.6f}")


if __name__ == "__main__":
    main()
