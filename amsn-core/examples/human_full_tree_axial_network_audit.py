"""Whole-morphology axial geometry and NEURON connection audit.

Three independent layers are kept separate:
1. Every electrically retained SWC edge is matched to an adjacent NEURON
   Import3D pt3d interval and its tapered axial geometry integral is compared.
2. Every NEURON segment-centre -> parent-node resistance (ri) is compared with
   the corresponding pt3d half/full-interval integral.
3. Every SWC branchpoint is matched to NEURON section parent-connections.

This is a geometry/topology audit, not a biological validation and not a
voltage-fit experiment. Soma-outline and zero-resistance wire edges collapsed
by AMSN's documented NeuroMorpho soma policy are counted separately.
"""
from __future__ import annotations

import csv
import os
from math import ceil, pi, sqrt
from pathlib import Path
import sys

import numpy as np
import neuron
from neuron import h

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


DATA = Path(os.environ.get("AMSN_MORPHOLOGY_PATH", str(reference.DATA)))
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
RI_OHM_M = 0.7
NEURON_RA_OHM_CM = RI_OHM_M * 100.0
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.5"))
GEOMETRY_MATCH_TOLERANCE_UM = 1e-3
DIAMETER_MATCH_TOLERANCE_UM = 1e-3
BRANCHPOINT_X_TOLERANCE = 1e-8
RI_RELATIVE_WARNING_PCT = 1e-6


def configure_neuron_reference(sections) -> None:
    """Use the same fine fixed-step morphology discretization as prior audits."""
    for section in sections:
        section.Ra = NEURON_RA_OHM_CM
        nseg = max(1, ceil(float(section.L) / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()
    h.define_shape()


def _section_name_for_import3d(imported, section_by_name) -> str:
    type_names = {1: "soma", 2: "axon", 3: "dend", 4: "apic"}
    swc_type = int(imported.type)
    if swc_type not in type_names:
        raise RuntimeError(f"Unsupported Import3D section type: {swc_type}")
    base_name = type_names[swc_type]
    name_index = int(imported.nameindex)
    hoc_name = f"{base_name}[{name_index}]" if name_index > 0 else base_name
    candidates = [hoc_name]
    if name_index == 0:
        candidates.extend([f"{base_name}[0]", base_name])
    for candidate in candidates:
        if candidate in section_by_name:
            return candidate
    raise RuntimeError(
        f"Import3D section {hoc_name} is not present in instantiated sections"
    )


def map_swc_node(reader, section_by_name, morphology, node_id):
    """Map an SWC node through Import3D's authoritative point2sec index."""
    point_index = int(reader.id2pt(node_id))
    section_index = int(reader.point2sec.x[point_index])
    imported = reader.sections.object(section_index)
    section_name = _section_name_for_import3d(imported, section_by_name)
    section = section_by_name[section_name]

    # NeuroMorpho CNG's single-point soma is represented by NEURON as a
    # sphere-like section. Its electrical centre is x=0.5.
    if section_index == 0 and int(imported.d.size()) == 1:
        node = morphology.nodes[node_id]
        return {
            "section": section,
            "section_name": section_name,
            "section_index": section_index,
            "local_index": None,
            "x": 0.5,
            "arc_um": 0.5 * float(section.L),
            "geometry_offset_um": 0.0,
            "diameter_offset_um": 0.0,
        }

    first_point_index = int(imported.id)
    local_index = (
        point_index - first_point_index
        + (0 if int(imported.first) == 1 else 1)
    )
    n3d = int(h.n3d(sec=section))
    if local_index < 0 or local_index >= n3d:
        raise RuntimeError(
            f"SWC node {node_id}: local pt3d index {local_index} outside "
            f"{section_name} with {n3d} points; Import3D first={int(imported.first)}"
        )

    node = morphology.nodes[node_id]
    xyz = np.array([
        float(h.x3d(local_index, sec=section)),
        float(h.y3d(local_index, sec=section)),
        float(h.z3d(local_index, sec=section)),
    ])
    source_xyz = np.array([node.x_um, node.y_um, node.z_um])
    geometry_offset_um = float(np.linalg.norm(source_xyz - xyz))
    diameter_offset_um = abs(
        float(h.diam3d(local_index, sec=section)) - 2.0 * node.radius_um
    )
    arc_um = float(h.arc3d(local_index, sec=section))
    return {
        "section": section,
        "section_name": section_name,
        "section_index": section_index,
        "local_index": local_index,
        "x": min(1.0, max(0.0, arc_um / float(section.L))),
        "arc_um": arc_um,
        "geometry_offset_um": geometry_offset_um,
        "diameter_offset_um": diameter_offset_um,
    }


def read_section_profile(section):
    """Return monotonically ordered pt3d arc, diameter and xyz arrays.

    A one-point root soma is represented with a constant-diameter axial profile
    over NEURON's effective section length. This is the simulator's own
    sphere-like soma approximation, not an anatomical claim.
    """
    n3d = int(h.n3d(sec=section))
    if n3d < 1:
        raise RuntimeError(f"NEURON section {section.name()} has no pt3d data")
    if n3d == 1:
        diameter = abs(float(h.diam3d(0, sec=section)))
        xyz = np.array([[
            float(h.x3d(0, sec=section)),
            float(h.y3d(0, sec=section)),
            float(h.z3d(0, sec=section)),
        ]])
        return {
            "arc": np.array([0.0, float(section.L)]),
            "diameter": np.array([diameter, diameter]),
            "xyz": np.vstack([xyz, xyz]),
            "one_point_soma": True,
        }
    arcs = np.array([float(h.arc3d(i, sec=section)) for i in range(n3d)])
    diameters = np.array([
        abs(float(h.diam3d(i, sec=section))) for i in range(n3d)
    ])
    xyz = np.array([
        [
            float(h.x3d(i, sec=section)),
            float(h.y3d(i, sec=section)),
            float(h.z3d(i, sec=section)),
        ]
        for i in range(n3d)
    ])
    if np.any(np.diff(arcs) < -1e-10):
        raise RuntimeError(f"non-monotonic pt3d arc in {section.name()}")
    return {
        "arc": arcs,
        "diameter": diameters,
        "xyz": xyz,
        "one_point_soma": False,
    }


def _nearest_point_indices(profile, target_xyz, tolerance_um):
    distances = np.linalg.norm(profile["xyz"] - np.asarray(target_xyz), axis=1)
    return np.flatnonzero(distances <= tolerance_um).tolist()


def find_edge_pt3d_interval(
    parent_node,
    child_node,
    parent_map,
    child_map,
    profiles,
):
    """Find a consecutive pt3d pair representing one original SWC edge."""
    candidate_sections = []
    for name in (child_map["section_name"], parent_map["section_name"]):
        if name not in candidate_sections:
            candidate_sections.append(name)

    candidates = []
    for section_name in candidate_sections:
        profile = profiles[section_name]
        parent_indices = _nearest_point_indices(
            profile,
            (parent_node.x_um, parent_node.y_um, parent_node.z_um),
            GEOMETRY_MATCH_TOLERANCE_UM,
        )
        child_indices = _nearest_point_indices(
            profile,
            (child_node.x_um, child_node.y_um, child_node.z_um),
            GEOMETRY_MATCH_TOLERANCE_UM,
        )
        for parent_index in parent_indices:
            for child_index in child_indices:
                if abs(parent_index - child_index) != 1:
                    continue
                start = min(parent_index, child_index)
                end = max(parent_index, child_index)
                parent_xyz = profile["xyz"][parent_index]
                child_xyz = profile["xyz"][child_index]
                parent_geom_error = float(np.linalg.norm(
                    parent_xyz - np.array([
                        parent_node.x_um, parent_node.y_um, parent_node.z_um
                    ])
                ))
                child_geom_error = float(np.linalg.norm(
                    child_xyz - np.array([
                        child_node.x_um, child_node.y_um, child_node.z_um
                    ])
                ))
                parent_diameter_error = abs(
                    profile["diameter"][parent_index] - 2.0 * parent_node.radius_um
                )
                child_diameter_error = abs(
                    profile["diameter"][child_index] - 2.0 * child_node.radius_um
                )
                score = (
                    parent_geom_error + child_geom_error
                    + parent_diameter_error + child_diameter_error
                )
                priority = 0 if section_name == child_map["section_name"] else 1
                candidates.append({
                    "section_name": section_name,
                    "start_index": start,
                    "end_index": end,
                    "parent_index": parent_index,
                    "child_index": child_index,
                    "parent_geometry_error_um": parent_geom_error,
                    "child_geometry_error_um": child_geom_error,
                    "parent_diameter_error_um": parent_diameter_error,
                    "child_diameter_error_um": child_diameter_error,
                    "score": score,
                    "priority": priority,
                    "profile": profile,
                })
    if not candidates:
        return None
    candidates.sort(key=lambda c: (c["priority"], c["score"]))
    return candidates[0]


def axial_factor_linear_taper_m_inv(length_um, diameter0_um, diameter1_um):
    """Exact integral ds/(pi*r(s)^2) for linearly tapered circular cable."""
    if length_um <= 0.0 or diameter0_um <= 0.0 or diameter1_um <= 0.0:
        raise ValueError("length and diameters must be positive")
    return 4.0e6 * length_um / (pi * diameter0_um * diameter1_um)


def profile_factor_between_x(section, profile, x0, x1):
    """Integrate ds/(pi*r^2) through a NEURON pt3d profile."""
    if x1 < x0:
        return profile_factor_between_x(section, profile, x1, x0)
    start_um = float(x0) * float(section.L)
    end_um = float(x1) * float(section.L)
    if end_um - start_um <= 1e-13:
        return 0.0
    arcs = profile["arc"]
    diameters = profile["diameter"]
    factor = 0.0
    covered = 0.0
    for index in range(len(arcs) - 1):
        arc0, arc1 = float(arcs[index]), float(arcs[index + 1])
        if arc1 - arc0 <= 1e-14:
            continue
        left = max(start_um, arc0)
        right = min(end_um, arc1)
        if right <= left:
            continue
        fraction0 = (left - arc0) / (arc1 - arc0)
        fraction1 = (right - arc0) / (arc1 - arc0)
        d0 = diameters[index] + (
            diameters[index + 1] - diameters[index]
        ) * fraction0
        d1 = diameters[index] + (
            diameters[index + 1] - diameters[index]
        ) * fraction1
        factor += axial_factor_linear_taper_m_inv(right - left, d0, d1)
        covered += right - left
    if abs(covered - (end_um - start_um)) > 1e-5:
        raise RuntimeError(
            f"pt3d axial profile in {section.name()} covered {covered:.9f} "
            f"of requested {end_um-start_um:.9f} um"
        )
    return factor


def coordinate_at_x(section, profile, x):
    """Interpolate the section's pt3d centreline coordinate at normalized x."""
    target = min(float(section.L), max(0.0, float(x) * float(section.L)))
    arcs, coords = profile["arc"], profile["xyz"]
    if profile["one_point_soma"]:
        return coords[0].copy()
    for index in range(len(arcs) - 1):
        a0, a1 = float(arcs[index]), float(arcs[index + 1])
        if a0 - 1e-12 <= target <= a1 + 1e-12:
            if a1 - a0 <= 1e-14:
                return coords[index].copy()
            fraction = (target - a0) / (a1 - a0)
            return coords[index] + (coords[index + 1] - coords[index]) * fraction
    return coords[-1].copy()


def relative_difference_pct(value, reference_value):
    return 100.0 * abs(value - reference_value) / max(abs(reference_value), 1e-30)


def audit_swc_edges(morphology, reader, section_by_name, profiles):
    electrical_map = morphology.electrical_node_mapping()
    node_maps = {
        node_id: map_swc_node(reader, section_by_name, morphology, node_id)
        for node_id in morphology.nodes
    }
    rows = []
    collapsed_edges = 0
    mapped_edges = 0
    unmapped_edges = 0

    for child_id, child in morphology.nodes.items():
        if child.parent_id == -1:
            continue
        parent = morphology.nodes[child.parent_id]
        parent_electrical = electrical_map[child.parent_id]
        child_electrical = electrical_map[child_id]
        if parent_electrical == child_electrical:
            collapsed_edges += 1
            continue

        parent_map = node_maps[child.parent_id]
        child_map = node_maps[child_id]
        match = find_edge_pt3d_interval(
            parent, child, parent_map, child_map, profiles
        )
        source_length_um = sqrt(
            (child.x_um - parent.x_um) ** 2
            + (child.y_um - parent.y_um) ** 2
            + (child.z_um - parent.z_um) ** 2
        )
        source_factor = axial_factor_linear_taper_m_inv(
            source_length_um,
            2.0 * parent.radius_um,
            2.0 * child.radius_um,
        )
        base = {
            "swc_parent_id": child.parent_id,
            "swc_child_id": child_id,
            "child_type": child.neurite_type,
            "source_length_um": source_length_um,
            "source_parent_radius_um": parent.radius_um,
            "source_child_radius_um": child.radius_um,
            "amsn_source_axial_factor_m_inv": source_factor,
            "amsn_source_resistance_ohm": source_factor * RI_OHM_M,
            "parent_import3d_section": parent_map["section_name"],
            "child_import3d_section": child_map["section_name"],
            "parent_import3d_x": parent_map["x"],
            "child_import3d_x": child_map["x"],
            "parent_geometry_mapping_error_um": parent_map["geometry_offset_um"],
            "child_geometry_mapping_error_um": child_map["geometry_offset_um"],
            "mapping_status": "unmapped",
        }
        if match is None:
            unmapped_edges += 1
            rows.append(base)
            continue

        profile = match["profile"]
        pidx, cidx = match["parent_index"], match["child_index"]
        d0, d1 = profile["diameter"][pidx], profile["diameter"][cidx]
        pt3d_length_um = abs(
            float(profile["arc"][cidx]) - float(profile["arc"][pidx])
        )
        neuron_factor = axial_factor_linear_taper_m_inv(
            pt3d_length_um, d0, d1
        )
        error_pct = 100.0 * (neuron_factor - source_factor) / source_factor
        mapped_edges += 1
        base.update({
            "mapping_status": "mapped",
            "neuron_pt3d_section": match["section_name"],
            "neuron_pt3d_parent_index": pidx,
            "neuron_pt3d_child_index": cidx,
            "neuron_pt3d_length_um": pt3d_length_um,
            "neuron_pt3d_parent_diameter_um": d0,
            "neuron_pt3d_child_diameter_um": d1,
            "neuron_axial_factor_m_inv": neuron_factor,
            "neuron_axial_resistance_ohm": neuron_factor * RI_OHM_M,
            "axial_factor_difference_pct": error_pct,
            "parent_pt3d_geometry_error_um": match["parent_geometry_error_um"],
            "child_pt3d_geometry_error_um": match["child_geometry_error_um"],
            "parent_pt3d_diameter_error_um": match["parent_diameter_error_um"],
            "child_pt3d_diameter_error_um": match["child_diameter_error_um"],
        })
        rows.append(base)

    return rows, {
        "active_swc_edges": mapped_edges + unmapped_edges,
        "mapped_swc_edges": mapped_edges,
        "unmapped_swc_edges": unmapped_edges,
        "collapsed_soma_or_wire_edges": collapsed_edges,
        "node_maps": node_maps,
    }


def audit_neuron_ri(sections, profiles):
    """Compare every segment ri() with its own pt3d parent interval.

    Internal section segment centres use the previous segment centre as parent.
    The first segment of a child section uses the connected section endpoint as
    parent. Root-section first segments are treated separately and reported.
    """
    rows = []
    max_internal_error = 0.0
    max_child_start_error = 0.0
    internal_count = 0
    child_start_count = 0
    infinite_root_count = 0
    unexpected_infinite_count = 0

    for section in sections:
        section_name = section.name()
        profile = profiles[section_name]
        segments = list(section)
        parent_segment = section.parentseg()
        child_orientation = float(section.orientation())
        for index, segment in enumerate(segments):
            actual_mohm = float(segment.ri())
            if index > 0:
                parent_x = float(segments[index - 1].x)
                expected_factor = profile_factor_between_x(
                    section, profile, parent_x, float(segment.x)
                )
                connection_type = "within_section_centres"
            elif parent_segment is not None:
                parent_x = child_orientation
                expected_factor = profile_factor_between_x(
                    section, profile, parent_x, float(segment.x)
                )
                connection_type = "child_section_start_half"
            else:
                parent_x = child_orientation
                expected_factor = profile_factor_between_x(
                    section, profile, parent_x, float(segment.x)
                )
                connection_type = "root_section_start"

            row = {
                "section": section_name,
                "segment_index": index,
                "segment_x": float(segment.x),
                "parent_section": (
                    parent_segment.sec.name()
                    if parent_segment is not None else ""
                ),
                "parent_connection_x": (
                    float(h.parent_connection(sec=section))
                    if parent_segment is not None else ""
                ),
                "section_orientation": child_orientation,
                "connection_type": connection_type,
                "ri_reported_mohm": actual_mohm,
                "pt3d_expected_axial_factor_m_inv": expected_factor,
            }
            if actual_mohm >= 1e20:
                if parent_segment is None:
                    infinite_root_count += 1
                    row["relative_difference_pct"] = ""
                    row["check_status"] = "root_no_parent_infinite"
                else:
                    unexpected_infinite_count += 1
                    row["relative_difference_pct"] = ""
                    row["check_status"] = "unexpected_infinite"
            else:
                actual_factor = actual_mohm * 1e6 / RI_OHM_M
                error_pct = relative_difference_pct(actual_factor, expected_factor)
                row["ri_axial_factor_m_inv"] = actual_factor
                row["relative_difference_pct"] = error_pct
                row["check_status"] = "checked"
                if connection_type == "within_section_centres":
                    internal_count += 1
                    max_internal_error = max(max_internal_error, error_pct)
                elif connection_type == "child_section_start_half":
                    child_start_count += 1
                    max_child_start_error = max(max_child_start_error, error_pct)
            rows.append(row)

    return rows, {
        "neuron_segment_rows": len(rows),
        "internal_segment_connections_checked": internal_count,
        "child_section_start_connections_checked": child_start_count,
        "root_unconnected_infinite_ri": infinite_root_count,
        "unexpected_infinite_ri": unexpected_infinite_count,
        "max_internal_ri_error_pct": max_internal_error,
        "max_child_start_ri_error_pct": max_child_start_error,
    }


def audit_branchpoint_connections(morphology, node_maps, sections, profiles):
    """Audit every NEURON section junction and the two axial half-resistances."""
    connections = []
    parent_half_rows = []
    for section in sections:
        parent_segment = section.parentseg()
        if parent_segment is None:
            continue
        parent_section = parent_segment.sec
        parent_x = float(h.parent_connection(sec=section))
        child_x = float(section.orientation())
        parent_profile = profiles[parent_section.name()]
        child_profile = profiles[section.name()]
        parent_xyz = coordinate_at_x(parent_section, parent_profile, parent_x)
        child_xyz = coordinate_at_x(section, child_profile, child_x)
        endpoint_gap_um = float(np.linalg.norm(parent_xyz - child_xyz))

        child_segments = list(section)
        if not child_segments:
            raise RuntimeError(f"connected section {section.name()} has no segments")
        child_first = child_segments[0]
        child_half_factor = profile_factor_between_x(
            section, child_profile, child_x, float(child_first.x)
        )
        child_actual_mohm = float(child_first.ri())
        child_actual_factor = (
            child_actual_mohm * 1e6 / RI_OHM_M
            if child_actual_mohm < 1e20 else float("nan")
        )
        child_half_error_pct = (
            relative_difference_pct(child_actual_factor, child_half_factor)
            if np.isfinite(child_actual_factor) else float("nan")
        )

        # NeuroMorpho CNG's three-point soma is represented in NEURON
        # as soma[0]. The eight Import3D wire stems are connected to its
        # electrical centre (x=0.5), while their first pt3d endpoint remains
        # at the original SWC stem coordinate. This is a documented topology
        # convention, not a geometric coincidence.
        parent_is_soma_wire_attachment = (
            parent_section.name() == "soma[0]"
            and abs(parent_x - 0.5) <= 1e-10
            and abs(child_x) <= 1e-10
        )
        parent_is_soma_sphere = bool(parent_profile["one_point_soma"])
        parent_at_endpoint = (
            abs(parent_x) <= 1e-12 or abs(parent_x - 1.0) <= 1e-12
        )
        parent_half_factor = 0.0
        parent_actual_mohm = float("nan")
        parent_half_error_pct = float("nan")
        parent_center_x = float("nan")
        if parent_at_endpoint and not parent_is_soma_sphere:
            parent_segments = list(parent_section)
            nearest_parent_segment = min(
                parent_segments,
                key=lambda candidate: abs(float(candidate.x) - parent_x),
            )
            parent_center_x = float(nearest_parent_segment.x)
            parent_half_factor = profile_factor_between_x(
                parent_section, parent_profile, parent_center_x, parent_x
            )
            parent_actual_mohm = float(h.ri(parent_x, sec=parent_section))
            if parent_actual_mohm < 1e20:
                parent_actual_factor = parent_actual_mohm * 1e6 / RI_OHM_M
                parent_half_error_pct = relative_difference_pct(
                    parent_actual_factor, parent_half_factor
                )
            parent_half_rows.append({
                "child_section": section.name(),
                "parent_section": parent_section.name(),
                "parent_connection_x": parent_x,
                "parent_nearest_segment_center_x": parent_center_x,
                "parent_half_expected_factor_m_inv": parent_half_factor,
                "parent_half_ri_reported_mohm": parent_actual_mohm,
                "parent_half_ri_error_pct": parent_half_error_pct,
            })

        if parent_is_soma_sphere or parent_is_soma_wire_attachment:
            connection_kind = "soma_wire_attachment_zero_resistance_link"
        elif parent_at_endpoint:
            connection_kind = "section_endpoint_junction"
        else:
            connection_kind = "interior_section_junction"

        connections.append({
            "child_section": section.name(),
            "parent_section": parent_section.name(),
            "connection_kind": connection_kind,
            "parent_connection_x": parent_x,
            "child_orientation": child_x,
            "parent_connection_x_um": parent_x * float(parent_section.L),
            "child_connection_x_um": child_x * float(section.L),
            "parent_connection_xyz_x_um": parent_xyz[0],
            "parent_connection_xyz_y_um": parent_xyz[1],
            "parent_connection_xyz_z_um": parent_xyz[2],
            "child_endpoint_xyz_x_um": child_xyz[0],
            "child_endpoint_xyz_y_um": child_xyz[1],
            "child_endpoint_xyz_z_um": child_xyz[2],
            "connection_endpoint_gap_um": endpoint_gap_um,
            "parent_half_expected_factor_m_inv": parent_half_factor,
            "parent_half_ri_reported_mohm": parent_actual_mohm,
            "parent_half_ri_error_pct": parent_half_error_pct,
            "child_half_expected_factor_m_inv": child_half_factor,
            "child_first_segment_ri_mohm": child_actual_mohm,
            "child_half_ri_error_pct": child_half_error_pct,
            "total_connection_half_factor_m_inv": (
                parent_half_factor + child_half_factor
            ),
            "total_connection_half_resistance_ohm": (
                RI_OHM_M * (parent_half_factor + child_half_factor)
            ),
        })

    rows = []
    for node_id, node in morphology.nodes.items():
        children = morphology.children[node_id]
        if node.neurite_type == 1 or len(children) < 2:
            continue
        mapped = node_maps[node_id]
        section_name = mapped["section_name"]
        target_x = mapped["x"]
        matching = [
            connection for connection in connections
            if connection["parent_section"] == section_name
            and abs(connection["parent_connection_x"] - target_x)
                <= BRANCHPOINT_X_TOLERANCE
        ]
        target_xyz = np.array([node.x_um, node.y_um, node.z_um])
        max_gap = max(
            (
                float(np.linalg.norm(
                    np.array([
                        c["parent_connection_xyz_x_um"],
                        c["parent_connection_xyz_y_um"],
                        c["parent_connection_xyz_z_um"],
                    ]) - target_xyz
                ))
                for c in matching
            ),
            default=float("nan"),
        )
        rows.append({
            "swc_branchpoint_id": node_id,
            "neurite_type": node.neurite_type,
            "swc_child_count": len(children),
            "import3d_parent_section": section_name,
            "import3d_branchpoint_x": target_x,
            "neuron_child_section_count_at_site": len(matching),
            "child_section_count_difference": len(matching) - len(children),
            "max_parent_connection_to_swc_point_gap_um": max_gap,
            "child_section_names": ";".join(
                c["child_section"] for c in matching
            ),
        })
    non_soma_gaps = [
        c["connection_endpoint_gap_um"]
        for c in connections
        if c["connection_kind"] != "soma_wire_attachment_zero_resistance_link"
    ]
    soma_gaps = [
        c["connection_endpoint_gap_um"]
        for c in connections
        if c["connection_kind"] == "soma_wire_attachment_zero_resistance_link"
    ]
    connection_summary = {
        "section_connection_count": len(connections),
        "soma_wire_attachment_count": len(soma_gaps),
        "max_soma_wire_attachment_offset_um": max(soma_gaps, default=0.0),
        "max_non_soma_connection_endpoint_gap_um": max(non_soma_gaps, default=0.0),
        "parent_endpoint_half_ri_checked": len(parent_half_rows),
        "max_parent_endpoint_half_ri_error_pct": max(
            (
                float(row["parent_half_ri_error_pct"])
                for row in parent_half_rows
                if np.isfinite(float(row["parent_half_ri_error_pct"]))
            ),
            default=0.0,
        ),
    }
    return rows, connections, connection_summary

def write_csv(path: Path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    reference.DATA = DATA
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    morphology = SWCMorphology.from_file(DATA)
    reader, sections = reference.import_swc_with_neuron()
    configure_neuron_reference(sections)
    section_by_name = {section.name(): section for section in sections}
    profiles = {
        section.name(): read_section_profile(section)
        for section in sections
    }

    edge_rows, edge_summary = audit_swc_edges(
        morphology, reader, section_by_name, profiles
    )
    ri_rows, ri_summary = audit_neuron_ri(sections, profiles)
    branch_rows, connection_rows, connection_summary = audit_branchpoint_connections(
        morphology, edge_summary["node_maps"], sections, profiles
    )

    outdir = Path(__file__).parents[1] / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = "" if MORPHOLOGY_LABEL == "NMO_290988" else f"{MORPHOLOGY_LABEL}_"
    edge_csv = outdir / f"{prefix}human_full_tree_axial_edges_2026-11-21.csv"
    ri_csv = outdir / f"{prefix}human_neuron_ri_connections_2026-11-21.csv"
    branch_csv = outdir / f"{prefix}human_branchpoint_connection_audit_2026-11-21.csv"
    section_csv = outdir / f"{prefix}human_neuron_section_connections_2026-11-21.csv"
    write_csv(edge_csv, edge_rows)
    write_csv(ri_csv, ri_rows)
    write_csv(branch_csv, branch_rows)
    write_csv(section_csv, connection_rows)

    active_edges = edge_summary["active_swc_edges"]
    coverage = (
        100.0 * edge_summary["mapped_swc_edges"] / active_edges
        if active_edges else 100.0
    )
    mapped_errors = [
        abs(float(row["axial_factor_difference_pct"]))
        for row in edge_rows if row.get("mapping_status") == "mapped"
    ]
    max_edge_error = max(mapped_errors, default=float("nan"))
    mapping_offsets = [
        float(row[key])
        for row in edge_rows if row.get("mapping_status") == "mapped"
        for key in (
            "parent_geometry_mapping_error_um",
            "child_geometry_mapping_error_um",
        )
    ]
    max_mapping_offset = max(mapping_offsets, default=float("nan"))
    branch_exact = sum(
        1 for row in branch_rows if row["child_section_count_difference"] == 0
    )
    branchpoint_count = len(branch_rows)
    connection_gap_max = max(
        (row["connection_endpoint_gap_um"] for row in connection_rows),
        default=float("nan"),
    )

    print(f"# NEURON={neuron.__version__}; source morphology={MORPHOLOGY_LABEL}; path={DATA}")
    print(
        f"# section_count={len(sections)}; NEURON_segments="
        f"{sum(section.nseg for section in sections)}; "
        f"max_segment_um={NEURON_MAX_SEGMENT_UM}"
    )
    print(
        f"# SWC_nodes={len(morphology.nodes)}; SWC_branchpoints="
        f"{morphology.summary().branch_point_count}; "
        f"active_edges={active_edges}; collapsed_soma_wire_edges="
        f"{edge_summary['collapsed_soma_or_wire_edges']}"
    )
    print(
        f"# active_edge_mapping={edge_summary['mapped_swc_edges']}/"
        f"{active_edges} ({coverage:.9f}%); unmapped="
        f"{edge_summary['unmapped_swc_edges']}"
    )
    print(
        f"# max_SWC_to_NEURON_pt3d_axial_factor_difference_pct={max_edge_error:.12g}; "
        f"max_node_geometry_mapping_offset_um={max_mapping_offset:.12g}"
    )
    print(
        f"# NEURON_ri_rows={ri_summary['neuron_segment_rows']}; "
        f"internal_checked={ri_summary['internal_segment_connections_checked']}; "
        f"child_start_checked={ri_summary['child_section_start_connections_checked']}; "
        f"root_infinite={ri_summary['root_unconnected_infinite_ri']}; "
        f"unexpected_infinite={ri_summary['unexpected_infinite_ri']}"
    )
    print(
        f"# max_internal_ri_error_pct={ri_summary['max_internal_ri_error_pct']:.12g}; "
        f"max_child_start_ri_error_pct={ri_summary['max_child_start_ri_error_pct']:.12g}"
    )
    print(
        f"# SWC_branchpoints_with_exact_NEURON_child_count="
        f"{branch_exact}/{branchpoint_count}"
    )
    print(
        f"# section_connections={connection_summary['section_connection_count']}; "
        f"soma_wire_attachments={connection_summary['soma_wire_attachment_count']}; "
        f"max_soma_wire_attachment_offset_um="
        f"{connection_summary['max_soma_wire_attachment_offset_um']:.12g}; "
        f"max_non_soma_endpoint_gap_um="
        f"{connection_summary['max_non_soma_connection_endpoint_gap_um']:.12g}"
    )
    print(
        f"# parent_endpoint_half_ri_checked="
        f"{connection_summary['parent_endpoint_half_ri_checked']}; "
        f"max_parent_endpoint_half_ri_error_pct="
        f"{connection_summary['max_parent_endpoint_half_ri_error_pct']:.12g}"
    )
    print(f"# raw_edge_csv={edge_csv}")
    print(f"# raw_ri_csv={ri_csv}")
    print(f"# raw_branch_csv={branch_csv}")
    print(f"# raw_section_connection_csv={section_csv}")

    if edge_summary["unmapped_swc_edges"] != 0:
        raise RuntimeError(
            f"{edge_summary['unmapped_swc_edges']} active SWC edges did not map "
            "to an adjacent NEURON pt3d interval; inspect raw edge CSV"
        )
    if branch_exact != branchpoint_count:
        mismatches = [
            row for row in branch_rows
            if row["child_section_count_difference"] != 0
        ]
        detail = [
            (row["swc_branchpoint_id"], row["swc_child_count"],
             row["neuron_child_section_count_at_site"])
            for row in mismatches[:8]
        ]
        raise RuntimeError(
            f"{len(mismatches)} SWC branchpoints do not preserve exact "
            f"NEURON child-section counts; first mismatches={detail}"
        )
    if (
        connection_summary["max_non_soma_connection_endpoint_gap_um"]
        > GEOMETRY_MATCH_TOLERANCE_UM
    ):
        raise RuntimeError(
            "non-soma section-connection endpoint gap exceeds geometry "
            f"tolerance: {connection_summary['max_non_soma_connection_endpoint_gap_um']:.12g} um"
        )
    if ri_summary["unexpected_infinite_ri"] != 0:
        raise RuntimeError(
            f"{ri_summary['unexpected_infinite_ri']} non-root segment(s) "
            "reported infinite ri()"
        )
    if ri_summary["max_internal_ri_error_pct"] > RI_RELATIVE_WARNING_PCT:
        raise RuntimeError(
            "NEURON internal segment ri() does not reproduce pt3d geometry: "
            f"{ri_summary['max_internal_ri_error_pct']:.12g}%"
        )
    if ri_summary["max_child_start_ri_error_pct"] > RI_RELATIVE_WARNING_PCT:
        raise RuntimeError(
            "NEURON child-section initial ri() does not reproduce its pt3d "
            f"half-edge: {ri_summary['max_child_start_ri_error_pct']:.12g}%"
        )
    if (
        connection_summary["max_parent_endpoint_half_ri_error_pct"]
        > RI_RELATIVE_WARNING_PCT
    ):
        raise RuntimeError(
            "NEURON parent endpoint ri() does not reproduce its pt3d half-edge: "
            f"{connection_summary['max_parent_endpoint_half_ri_error_pct']:.12g}%"
        )


if __name__ == "__main__":
    main()
