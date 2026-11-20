"""Cross-simulator passive DC comparison using NEURON Import3D.

NEURON imports the exact same standardized SWC as AMSN, applies equivalent
passive SI parameters after unit conversion, and uses a <=5 um segment cap.
Seven source/probe locations are matched to NEURON's nearest segment centres.
The run compares NEURON against both AMSN's full SWC-node cable and its
section-reduced cable. This is a passive DC comparison, not a human fit.
"""
from __future__ import annotations

from math import ceil, pi
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

    return reader, sections


def locate_neuron_segment(reader, section_by_name, node):
    """Map a raw SWC node through Import3D's own point-to-section index.

    This avoids a nearest-in-3D search that could choose an adjacent branch
    where branches pass close to or cross one another.
    """
    point_index = int(reader.id2pt(node.node_id))
    section_index = int(reader.point2sec.x[point_index])
    imported_section = reader.sections.object(section_index)
    type_names = {1: "soma", 2: "axon", 3: "dend", 4: "apic"}
    swc_type = int(imported_section.type)
    if swc_type not in type_names:
        raise RuntimeError(
            f"Unsupported Import3D section type {swc_type} "
            f"for SWC node {node.node_id}"
        )
    name_index = int(imported_section.nameindex)
    base_name = type_names[swc_type]
    hoc_name = (
        f"{base_name}[{name_index}]"
        if name_index > 0 else base_name
    )
    # Import3D's hoc name() omits the [0] suffix, but Python Section.name()
    # usually retains the array index created by "~create soma[n]".
    candidates = [hoc_name]
    if name_index == 0:
        candidates.extend([f"{base_name}[0]", base_name])
    section_name = next(
        (candidate for candidate in candidates if candidate in section_by_name),
        None,
    )
    if section_name is None:
        same_type = sorted(
            name for name in section_by_name
            if name == base_name or name.startswith(base_name + "[")
        )
        raise RuntimeError(
            f"Import3D maps SWC node {node.node_id} to hoc section {hoc_name}, "
            f"but no matching Python section exists; {base_name} sections={same_type[:12]}"
        )
    sec = section_by_name[section_name]

    # The one-point root is represented by NEURON as a sphere-like 3-point
    # cylinder. Its biological centre is at x=0.5, not at pt3d endpoint 0.
    if section_index == 0 and int(imported_section.d.size()) == 1:
        arc_um = 0.5 * sec.L
        geometric_error = 0.0
    else:
        first_point_index = int(imported_section.id)
        # Import3D's first==1 omits a duplicated parent pt3d point for a wire
        # section; otherwise local point zero is that parent duplicate.
        local_point_index = (
            point_index - first_point_index
            + (0 if int(imported_section.first) == 1 else 1)
        )
        n3d = int(h.n3d(sec=sec))
        if local_point_index < 0 or local_point_index >= n3d:
            raise RuntimeError(
                f"SWC node {node.node_id}: local Import3D point "
                f"{local_point_index} outside {section_name} with {n3d} points; "
                f"first={int(imported_section.first)}"
            )
        xyz = np.array([
            h.x3d(local_point_index, sec=sec),
            h.y3d(local_point_index, sec=sec),
            h.z3d(local_point_index, sec=sec),
        ], dtype=float)
        target = np.array([node.x_um, node.y_um, node.z_um], dtype=float)
        geometric_error = float(np.linalg.norm(target - xyz))
        arc_um = float(h.arc3d(local_point_index, sec=sec))

    normalized = min(1.0, max(0.0, arc_um / sec.L))
    segments = list(sec)
    segment = min(
        segments,
        key=lambda candidate: abs(candidate.x-normalized) * sec.L,
    )
    centre_error = abs(segment.x * sec.L - arc_um)
    total_error = float(np.hypot(geometric_error, centre_error))
    return segment, total_error, geometric_error, centre_error, section_name, normalized


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

    reader, sections = import_swc_with_neuron()
    section_by_name = {sec.name(): sec for sec in sections}
    segment_mapping = {}
    mapping_errors = {}
    record_ids = set(injection_ids + probe_ids)
    for node_id in record_ids:
        segment, total, geometry, centre, section_name, normalized = locate_neuron_segment(
            reader, section_by_name, morphology.nodes[node_id]
        )
        segment_mapping[node_id] = segment
        mapping_errors[node_id] = (total, geometry, centre, section_name, normalized)

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
    neuron_area_um2 = sum(segment.area() for sec in sections for segment in sec)
    neuron_pt3d_frustum_um2 = 0.0
    neuron_pt3d_cylinder_um2 = 0.0
    for sec in sections:
        for point_index in range(1, int(h.n3d(sec=sec))):
            x0, y0, z0 = (
                h.x3d(point_index-1, sec=sec),
                h.y3d(point_index-1, sec=sec),
                h.z3d(point_index-1, sec=sec),
            )
            x1, y1, z1 = (
                h.x3d(point_index, sec=sec),
                h.y3d(point_index, sec=sec),
                h.z3d(point_index, sec=sec),
            )
            d0 = 0.5 * h.diam3d(point_index-1, sec=sec)
            d1 = 0.5 * h.diam3d(point_index, sec=sec)
            length = float(np.linalg.norm([x1-x0, y1-y0, z1-z0]))
            neuron_pt3d_cylinder_um2 += pi * (d0+d1) * length
            neuron_pt3d_frustum_um2 += pi * (d0+d1) * np.hypot(length, d1-d0)

    print(f"# NEURON={neuron.__version__}; Import3D SWC; record=NMO_290988")
    print("# identical passive physical parameters: Ri=.7 ohm*m; Rm=1 ohm*m^2; Cm=.01 F/m^2; Eleak=-65mV")
    print(f"# NEURON sections={len(sections)}; NEURON segments={neuron_segments}; max_segment_um={MAX_NEURON_SEGMENT_UM}")
    print(f"# AMSN fine={fine.n_compartments}; AMSN sectioned={reduced.tree.n_compartments}")
    amsn_area_um2 = morphology.summary().estimated_membrane_area_um2
    area_error_pct = 100.0 * (neuron_area_um2-amsn_area_um2) / amsn_area_um2
    print(f"# NEURON total segment area={neuron_area_um2:.9f} um^2")
    print(f"# AMSN frustum geometry area={amsn_area_um2:.9f} um^2")
    print(f"# NEURON_vs_AMSN_area_difference={area_error_pct:.6f}%")
    print(f"# NEURON_pt3d_cylinder_area={neuron_pt3d_cylinder_um2:.9f} um^2")
    print(f"# NEURON_pt3d_frustum_area={neuron_pt3d_frustum_um2:.9f} um^2")
    source_by_type = {}
    for node in morphology.nodes.values():
        if node.parent_id == -1:
            continue
        parent = morphology.nodes[node.parent_id]
        length = float(np.linalg.norm([
            node.x_um-parent.x_um,
            node.y_um-parent.y_um,
            node.z_um-parent.z_um,
        ]))
        area = np.pi * (parent.radius_um+node.radius_um) * np.hypot(
            length, node.radius_um-parent.radius_um
        )
        source_by_type[node.neurite_type] = source_by_type.get(node.neurite_type, 0.0) + area
    print(f"# source_SW C_frustum_area_by_child_type={source_by_type}")
    for name, node_id in injections + probes:
        total, geometry, centre, section_name, normalized = mapping_errors[node_id]
        print(
            f"# site {name} swc_id={node_id}; section={section_name}; x={normalized:.8f}; "
            f"mapping_total_um={total:.6f}; geometry_um={geometry:.6f}; "
            f"segment_centre_um={centre:.6f}"
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
