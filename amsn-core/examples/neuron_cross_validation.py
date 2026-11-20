"""Cross-simulator passive DC comparison using NEURON Import3D.

NEURON imports the exact same standardized SWC as AMSN, applies equivalent
passive SI parameters after unit conversion, and uses a <=5 um segment cap.
Seven source/probe locations are matched to NEURON's nearest segment centres.
The run compares NEURON against both AMSN's full SWC-node cable and its
section-reduced cable. This is a passive DC comparison, not a human fit.
"""
from __future__ import annotations

from math import ceil
from pathlib import Path

import numpy as np
import neuron
from neuron import h

from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


DATA = (
    Path(__file__).parents[1]
    / "data"
    / "human"
    / "1094_Mohan_etal_2015.CNG.swc"
)
RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
INJECTED_P_A = 10.0
MAX_NEURON_SEGMENT_UM = 5.0
RUN_TO_MS = 200.0
FINAL_MS = 250.0
DT_MS = 0.025


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


def import_swc_with_neuron():
    """Instantiate sections with NEURON's headless Import3D reader."""
    h.load_file("stdrun.hoc")
    h.load_file("import3d.hoc")
    reader = h.Import3d_SWC_read()
    reader.input(str(DATA))
    importer = h.Import3d_GUI(reader, 0)
    importer.instantiate(None)
    h.define_shape()

    sections = sorted(list(h.allsec()), key=lambda sec: sec.name())
    if not sections:
        raise RuntimeError("NEURON Import3D did not instantiate any sections")

    for sec in sections:
        # Unit conversion to NEURON's cm, uF/cm2, S/cm2 and mV conventions.
        sec.Ra = RI_OHM_M * 100.0
        sec.cm = CM_F_M2 * 100.0
        sec.insert("pas")
        for segment in sec:
            segment.g_pas = (1.0 / RM_OHM_M2) * 1e-4
            segment.e_pas = ELEAK_MV

        # Geometry-based fine reference: no segment is longer than 5 um.
        sec.nseg = max(1, ceil(sec.L / MAX_NEURON_SEGMENT_UM))
        for segment in sec:
            _ = segment.area()

    return sections


def classify_section(sec) -> int | None:
    name = sec.name().lower()
    if "soma" in name:
        return 1
    if "apic" in name:
        return 4
    if "dend" in name:
        return 3
    if "axon" in name:
        return 2
    return None


def locate_neuron_segment(sections, node):
    """Find the nearest segment centre within the imported neurite class."""
    class_sections = [
        sec for sec in sections
        if classify_section(sec) == node.neurite_type
    ]
    candidates = class_sections or sections
    target = np.array([node.x_um, node.y_um, node.z_um], dtype=float)
    best = None

    for sec in candidates:
        n3d = int(h.n3d(sec=sec))
        if n3d < 1 or sec.L <= 0:
            continue
        segments = list(sec)
        if not segments:
            continue
        for point_index in range(n3d):
            xyz = np.array([
                h.x3d(point_index, sec=sec),
                h.y3d(point_index, sec=sec),
                h.z3d(point_index, sec=sec),
            ], dtype=float)
            geometric_error = float(np.linalg.norm(target - xyz))
            arc_um = float(h.arc3d(point_index, sec=sec))
            normalized = min(1.0, max(0.0, arc_um / sec.L))
            segment = min(
                segments,
                key=lambda candidate: abs(candidate.x-normalized) * sec.L,
            )
            centre_error = abs(segment.x * sec.L - arc_um)
            total_error = float(np.hypot(geometric_error, centre_error))
            key = (total_error, geometric_error, sec.name(), segment.x)
            if best is None or key < best[0]:
                best = (key, segment, geometric_error, centre_error)

    if best is None:
        raise RuntimeError(
            f"Unable to locate SWC node {node.node_id} in NEURON geometry"
        )
    return best[1], best[0][0], best[2], best[3]


def solve_amsn(tree, mapping, source_id, probe_ids):
    current = np.zeros(tree.n_compartments, dtype=float)
    source_name = mapping[source_id]
    current[tree.index[source_name]] = INJECTED_P_A * 1e-12
    voltage = tree.solve_passive_steady_state(current)
    leak = tree.parameters.e_leak_v
    source_delta_mV = (voltage[tree.index[source_name]] - leak) * 1e3
    input_resistance_mohm = source_delta_mV / INJECTED_P_A * 1e3
    rows = {}
    for probe_id in probe_ids:
        probe_delta_mV = (voltage[tree.index[mapping[probe_id]]] - leak) * 1e3
        rows[probe_id] = (
            probe_delta_mV,
            probe_delta_mV / INJECTED_P_A * 1e3,
            probe_delta_mV / source_delta_mV,
        )
    return input_resistance_mohm, rows


def solve_neuron(source_segment, probe_segments, previous_clamps):
    for previous in previous_clamps:
        previous.amp = 0.0
    clamp = h.IClamp(source_segment)
    clamp.delay = 0.0
    clamp.dur = 500.0
    clamp.amp = INJECTED_P_A / 1000.0  # NEURON uses nA: 10 pA = 0.01 nA.

    h.dt = DT_MS
    h.steps_per_ms = 1.0 / DT_MS
    h.CVode().active(0)
    h.finitialize(ELEAK_MV)
    h.continuerun(RUN_TO_MS)
    early = {key: float(segment.v) for key, segment in probe_segments.items()}
    h.continuerun(FINAL_MS)
    final = {key: float(segment.v) for key, segment in probe_segments.items()}
    residual_mV = max(abs(final[key]-early[key]) for key in final)
    clamp.amp = 0.0
    return final, residual_mV, clamp


def relative_error(value: float, reference: float) -> float:
    return 100.0 * abs(value-reference) / max(abs(reference), 1e-30)


def main() -> None:
    morphology = SWCMorphology.from_file(DATA)
    distances = path_distances_um(morphology)
    injections = [
        ("soma", morphology.root_id),
        ("basal_q75", quantile_node(morphology, distances, 3, 0.75)),
        ("apical_q75", quantile_node(morphology, distances, 4, 0.75)),
    ]
    probes = [
        ("soma", morphology.root_id),
        ("basal_q50", quantile_node(morphology, distances, 3, 0.50)),
        ("basal_q90", quantile_node(morphology, distances, 3, 0.90)),
        ("apical_q50", quantile_node(morphology, distances, 4, 0.50)),
        ("apical_q90", quantile_node(morphology, distances, 4, 0.90)),
    ]
    injection_ids = [node_id for _, node_id in injections]
    probe_ids = [node_id for _, node_id in probes]
    protected = set(injection_ids + probe_ids)

    sections = import_swc_with_neuron()
    segment_mapping = {}
    mapping_errors = {}
    record_ids = set(injection_ids + probe_ids)
    for node_id in record_ids:
        segment, total, geometry, centre = locate_neuron_segment(
            sections, morphology.nodes[node_id]
        )
        segment_mapping[node_id] = segment
        mapping_errors[node_id] = (total, geometry, centre)

    fine = morphology.to_cable_tree()
    fine_mapping = {node_id: f"swc_{node_id}" for node_id in morphology.nodes}
    reduced = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=100.0,
        max_electrotonic_length=0.1,
        reference_frequency_hz=100.0,
        preserve_node_ids=protected,
    )
    neuron_segments = sum(sec.nseg for sec in sections)
    neuron_area_um2 = sum(
        segment.area() for sec in sections for segment in sec
    )

    print(f"# NEURON={neuron.__version__}; Import3D SWC; record=NMO_290988")
    print("# identical passive physical parameters: Ri=.7 ohm*m; Rm=1 ohm*m^2; Cm=.01 F/m^2; Eleak=-65mV")
    print(f"# NEURON sections={len(sections)}; NEURON segments={neuron_segments}; max_segment_um={MAX_NEURON_SEGMENT_UM}")
    print(f"# AMSN fine={fine.n_compartments}; AMSN sectioned={reduced.tree.n_compartments}")
    amsn_area_um2 = morphology.summary().estimated_membrane_area_um2
    area_error_pct = 100.0 * (neuron_area_um2-amsn_area_um2) / amsn_area_um2
    print(f"# NEURON total segment area={neuron_area_um2:.9f} um^2")
    print(f"# AMSN frustum geometry area={amsn_area_um2:.9f} um^2")
    print(f"# NEURON_vs_AMSN_area_difference={area_error_pct:.6f}%")
    for name, node_id in injections + probes:
        total, geometry, centre = mapping_errors[node_id]
        print(
            f"# site {name} swc_id={node_id}; mapping_total_um={total:.6f}; "
            f"geometry_um={geometry:.6f}; segment_centre_um={centre:.6f}"
        )
    print("source,source_swc_id,probe,probe_swc_id,neuron_input_R_MOhm,amsn_fine_input_R_MOhm,amsn_sectioned_input_R_MOhm,neuron_transfer_R_MOhm,amsn_fine_transfer_R_MOhm,amsn_sectioned_transfer_R_MOhm,neuron_ratio,amsn_fine_ratio,amsn_sectioned_ratio,neuron_vs_fine_ratio_error_pct,neuron_vs_sectioned_ratio_error_pct,neuron_mapping_error_um,steady_residual_mV")

    previous_clamps = []
    residuals = []
    for source_name, source_id in injections:
        record_segments = {
            node_id: segment_mapping[node_id]
            for node_id in set(probe_ids + [source_id])
        }
        neuron_voltage, residual, clamp = solve_neuron(
            segment_mapping[source_id], record_segments, previous_clamps
        )
        previous_clamps.append(clamp)
        residuals.append(residual)

        fine_input, fine_rows = solve_amsn(
            fine, fine_mapping, source_id, probe_ids
        )
        sectioned_input, sectioned_rows = solve_amsn(
            reduced.tree, reduced.swc_node_to_compartment, source_id, probe_ids
        )

        source_delta = neuron_voltage[source_id] - ELEAK_MV
        neuron_input = source_delta / INJECTED_P_A * 1e3
        for probe_name, probe_id in probes:
            probe_delta = neuron_voltage[probe_id] - ELEAK_MV
            neuron_transfer = probe_delta / INJECTED_P_A * 1e3
            neuron_ratio = probe_delta / source_delta
            fine_delta, fine_transfer, fine_ratio = fine_rows[probe_id]
            sectioned_delta, sectioned_transfer, sectioned_ratio = sectioned_rows[probe_id]
            print(
                f"{source_name},{source_id},{probe_name},{probe_id},"
                f"{neuron_input:.9f},{fine_input:.9f},{sectioned_input:.9f},"
                f"{neuron_transfer:.9f},{fine_transfer:.9f},{sectioned_transfer:.9f},"
                f"{neuron_ratio:.9f},{fine_ratio:.9f},{sectioned_ratio:.9f},"
                f"{relative_error(neuron_ratio,fine_ratio):.9f},"
                f"{relative_error(neuron_ratio,sectioned_ratio):.9f},"
                f"{mapping_errors[probe_id][0]:.6f},{residual:.9f}"
            )
    print(f"# max residual from {RUN_TO_MS:g}ms to {FINAL_MS:g}ms: {max(residuals):.9f}mV")


if __name__ == "__main__":
    main()
