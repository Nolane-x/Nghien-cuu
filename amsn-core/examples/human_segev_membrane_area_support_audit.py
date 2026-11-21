"""Matched-support membrane area audit for Segev human morphologies.

AMSN's node-centred CableTree assigns half of every SWC frustum's membrane
surface area to each endpoint control volume. This audit reproduces that same
support on NEURON Import3D:

- Read NEURON's actual segment.area() values after a fine 0.125 um mesh.
- For each active SWC edge, intersect each half-edge control-volume region
  with the NEURON segment intervals on the mapped Import3D section.
- Distribute each actual segment.area() in proportion to its pt3d tapered
  surface area on each intersection.
- Accumulate the distributed area at the matching electrical SWC endpoint.
- Compare per-node NEURON support area against CableTree.area_m2.

This is deliberately a support-mapping audit before comparing leak and
capacitance operators. It does not assume that total area equality alone
proves that area is assigned to the correct electrical nodes.
"""
from __future__ import annotations

import csv
import os
from math import floor, ceil, pi, sqrt
from pathlib import Path

import numpy as np
import neuron

import human_full_tree_axial_network_audit as audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


RI_OHM_M = 0.7
MORPHOLOGY_PATH = Path(os.environ.get(
    "AMSN_MORPHOLOGY_PATH", str(reference.DATA)
))
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
NEURON_MAX_SEGMENT_UM = float(os.environ.get(
    "AMSN_NEURON_MAX_SEGMENT_UM", "0.125"
))
AREA_COVERAGE_TOLERANCE_PCT = 1e-6


def frustum_surface_area_um2(length_um: float, diameter0_um: float, diameter1_um: float) -> float:
    if length_um < 0 or diameter0_um <= 0 or diameter1_um <= 0:
        raise ValueError("invalid frustum geometry for membrane area")
    radius0 = 0.5 * diameter0_um
    radius1 = 0.5 * diameter1_um
    return pi * (radius0 + radius1) * sqrt(
        length_um * length_um + (radius1 - radius0) ** 2
    )


def profile_area_between_x(section, profile, x0: float, x1: float) -> float:
    """Integrate tapered pt3d surface area on a normalized section interval."""
    low_x, high_x = sorted((float(x0), float(x1)))
    length = float(section.L)
    start_um = max(0.0, min(length, low_x * length))
    end_um = max(0.0, min(length, high_x * length))
    if end_um <= start_um + 1e-14:
        return 0.0

    arcs = profile["arc"]
    diameters = profile["diameter"]
    covered_um = 0.0
    area_um2 = 0.0
    for index in range(len(arcs) - 1):
        arc0 = float(arcs[index])
        arc1 = float(arcs[index + 1])
        if arc1 <= arc0 + 1e-14:
            continue
        left = max(start_um, arc0)
        right = min(end_um, arc1)
        if right <= left:
            continue
        f0 = (left - arc0) / (arc1 - arc0)
        f1 = (right - arc0) / (arc1 - arc0)
        d0 = float(diameters[index]) + (
            float(diameters[index + 1]) - float(diameters[index])
        ) * f0
        d1 = float(diameters[index]) + (
            float(diameters[index + 1]) - float(diameters[index])
        ) * f1
        area_um2 += frustum_surface_area_um2(right - left, d0, d1)
        covered_um += right - left

    if abs(covered_um - (end_um - start_um)) > 1e-5:
        raise RuntimeError(
            f"pt3d area profile in {section.name()} covered {covered_um:.12g} "
            f"of requested {end_um-start_um:.12g} um"
        )
    return area_um2


def edge_half_surface_areas(parent, child) -> tuple[float, float, float]:
    length = float(np.linalg.norm([
        child.x_um - parent.x_um,
        child.y_um - parent.y_um,
        child.z_um - parent.z_um,
    ]))
    if length <= 0:
        raise RuntimeError("zero-length SWC edge encountered in area support audit")
    r0 = float(parent.radius_um)
    r1 = float(child.radius_um)
    rmid = 0.5 * (r0 + r1)
    half_length = 0.5 * length
    proximal = pi * (r0 + rmid) * sqrt(
        half_length * half_length + (rmid - r0) ** 2
    )
    distal = pi * (rmid + r1) * sqrt(
        half_length * half_length + (r1 - rmid) ** 2
    )
    return proximal, distal, length


def allocate_interval(
    node_id: int,
    section,
    section_data: dict,
    x0: float,
    x1: float,
    neuron_area_by_node: dict[int, float],
) -> tuple[float, float]:
    """Allocate actual segment area to a node using pt3d overlap proportions.

    Returns (allocated actual NEURON area, geometric pt3d area used for the
    overlap). Each segment's measured area is partitioned only once across
    the SWC half-edge intervals that intersect it.
    """
    low_x, high_x = sorted((float(x0), float(x1)))
    if high_x <= low_x + 1e-14:
        return 0.0, 0.0

    nseg = section_data["nseg"]
    first = max(0, int(floor(low_x * nseg)))
    last = min(nseg - 1, int(ceil(high_x * nseg) - 1))
    allocated_actual = 0.0
    allocated_geometry = 0.0

    for index in range(first, last + 1):
        seg_left = index / nseg
        seg_right = (index + 1) / nseg
        overlap_left = max(low_x, seg_left)
        overlap_right = min(high_x, seg_right)
        if overlap_right <= overlap_left + 1e-14:
            continue

        part_geometry = profile_area_between_x(
            section, section_data["profile"], overlap_left, overlap_right
        )
        if part_geometry <= 0:
            continue
        segment_geometry = float(section_data["geometry_area"][index])
        segment_actual = float(section_data["actual_area"][index])
        if segment_geometry <= 0 or not np.isfinite(segment_geometry):
            raise RuntimeError(
                f"{section.name()} segment {index}: invalid geometric area "
                f"{segment_geometry}"
            )
        portion = part_geometry / segment_geometry
        if portion < -1e-10 or portion > 1.0 + 1e-7:
            raise RuntimeError(
                f"{section.name()} segment {index}: invalid area fraction {portion}"
            )
        actual_part = segment_actual * portion
        section_data["allocated_geometry"][index] += part_geometry
        section_data["allocated_actual"][index] += actual_part
        neuron_area_by_node[node_id] += actual_part
        allocated_actual += actual_part
        allocated_geometry += part_geometry

    return allocated_actual, allocated_geometry


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    reference.DATA = MORPHOLOGY_PATH
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    audit.DATA = MORPHOLOGY_PATH
    audit.MORPHOLOGY_LABEL = MORPHOLOGY_LABEL
    audit.NEURON_MAX_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    audit.reference.DATA = MORPHOLOGY_PATH

    morphology = SWCMorphology.from_file(MORPHOLOGY_PATH)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {section.name(): section for section in sections}
    profiles = {
        section.name(): audit.read_section_profile(section)
        for section in sections
    }

    edge_rows, edge_summary = audit.audit_swc_edges(
        morphology, reader, section_by_name, profiles
    )
    if edge_summary["unmapped_swc_edges"] != 0:
        raise RuntimeError(
            f"unmapped active SWC edges: {edge_summary['unmapped_swc_edges']}"
        )
    node_maps = edge_summary["node_maps"]
    electrical_map = morphology.electrical_node_mapping()
    cable = morphology.to_cable_tree()
    cable_node_ids = {
        int(name.removeprefix("swc_")): index
        for name, index in cable.index.items()
    }
    if set(cable_node_ids) != set(electrical_map.values()):
        raise RuntimeError("AMSN area-control-volume node map is not the electrical SWC map")

    amsn_area = {
        node_id: float(cable.area_m2[index] * 1e12)
        for node_id, index in cable_node_ids.items()
    }
    neuron_area = {node_id: 0.0 for node_id in amsn_area}
    edge_allocations: dict[tuple[int, int], dict] = {}
    section_data = {}
    segment_count = 0
    neuron_total_area = 0.0
    soma_section_area = 0.0
    soma_section_count = 0

    # Prepare actual segment areas and their exact pt3d-geometry equivalents.
    for section in sections:
        name = section.name()
        profile = profiles[name]
        segments = list(section)
        actual_area = np.asarray([float(seg.area()) for seg in segments], dtype=float)
        if not np.all(np.isfinite(actual_area)) or np.any(actual_area < 0):
            raise RuntimeError(f"{name}: non-finite/negative NEURON segment area")
        neuron_total_area += float(actual_area.sum())
        segment_count += len(segments)
        section_type = name.split("[", 1)[0]
        if section_type == "soma" or bool(profile.get("one_point_soma", False)):
            soma_section_count += 1
            soma_section_area += float(actual_area.sum())
            neuron_area[morphology.root_id] += float(actual_area.sum())
            continue

        nseg = int(section.nseg)
        geometry_area = np.asarray([
            profile_area_between_x(section, profile, index / nseg, (index + 1) / nseg)
            for index in range(nseg)
        ], dtype=float)
        if np.any(geometry_area <= 0) or not np.all(np.isfinite(geometry_area)):
            bad = np.flatnonzero((geometry_area <= 0) | ~np.isfinite(geometry_area))
            raise RuntimeError(
                f"{name}: invalid geometric segment-area intervals {bad[:8].tolist()}"
            )
        section_data[name] = {
            "profile": profile,
            "segments": segments,
            "nseg": nseg,
            "actual_area": actual_area,
            "geometry_area": geometry_area,
            "allocated_geometry": np.zeros(nseg, dtype=float),
            "allocated_actual": np.zeros(nseg, dtype=float),
        }

    # Partition each active SWC frustum at its geometric midpoint. Its proximal
    # half belongs to the parent electrical node, distal half to the child.
    for row in edge_rows:
        parent_id = int(row["swc_parent_id"])
        child_id = int(row["swc_child_id"])
        electrical_parent = int(electrical_map[parent_id])
        electrical_child = int(electrical_map[child_id])
        if electrical_parent == electrical_child:
            raise RuntimeError("collapsed soma/wire edge unexpectedly remains in active edge table")

        parent_node = morphology.nodes[parent_id]
        child_node = morphology.nodes[child_id]
        match = audit.find_edge_pt3d_interval(
            parent_node,
            child_node,
            node_maps[parent_id],
            node_maps[child_id],
            profiles,
        )
        if match is None:
            raise RuntimeError(f"could not map area-support edge {parent_id}->{child_id}")
        section_name = match["section_name"]
        if section_name not in section_data:
            raise RuntimeError(
                f"active SWC edge {parent_id}->{child_id} mapped into excluded soma section {section_name}"
            )
        section = section_by_name[section_name]
        profile = profiles[section_name]
        arc_parent = float(profile["arc"][match["parent_index"]])
        arc_child = float(profile["arc"][match["child_index"]])
        midpoint_arc = 0.5 * (arc_parent + arc_child)
        x_parent = arc_parent / float(section.L)
        x_mid = midpoint_arc / float(section.L)
        x_child = arc_child / float(section.L)

        neuron_parent_area, parent_geom_area = allocate_interval(
            electrical_parent,
            section,
            section_data[section_name],
            x_parent,
            x_mid,
            neuron_area,
        )
        neuron_child_area, child_geom_area = allocate_interval(
            electrical_child,
            section,
            section_data[section_name],
            x_mid,
            x_child,
            neuron_area,
        )
        amsn_parent_area, amsn_child_area, swc_length = edge_half_surface_areas(
            parent_node, child_node
        )
        edge_allocations[(electrical_parent, electrical_child)] = {
            "source_swc_parent_id": parent_id,
            "source_swc_child_id": child_id,
            "neur_section": section_name,
            "swc_length_um": swc_length,
            "amsn_parent_half_area_um2": amsn_parent_area,
            "amsn_child_half_area_um2": amsn_child_area,
            "neuron_parent_half_area_um2": neuron_parent_area,
            "neuron_child_half_area_um2": neuron_child_area,
            "pt3d_parent_half_area_um2": parent_geom_area,
            "pt3d_child_half_area_um2": child_geom_area,
        }

    # Every non-soma segment's measured area must be fully assigned to the
    # collection of SWC half-edge support intervals on its Import3D section.
    section_rows = []
    max_segment_closure_pct = 0.0
    for name, data in section_data.items():
        geom = data["geometry_area"]
        allocated_geom = data["allocated_geometry"]
        actual = data["actual_area"]
        allocated_actual = data["allocated_actual"]
        per_segment_error = 100.0 * np.abs(allocated_geom - geom) / np.maximum(geom, 1e-30)
        max_segment_closure_pct = max(
            max_segment_closure_pct, float(np.max(per_segment_error))
        )
        geometry_total = float(geom.sum())
        allocated_geometry_total = float(allocated_geom.sum())
        actual_total = float(actual.sum())
        allocated_actual_total = float(allocated_actual.sum())
        geometry_coverage_error_pct = (
            100.0 * abs(allocated_geometry_total - geometry_total)
            / max(geometry_total, 1e-30)
        )
        actual_area_coverage_error_pct = (
            100.0 * abs(allocated_actual_total - actual_total)
            / max(actual_total, 1e-30)
        )
        section_rows.append({
            "section": name,
            "nseg": data["nseg"],
            "neuron_segment_area_um2": actual_total,
            "pt3d_geometric_segment_area_um2": geometry_total,
            "allocated_pt3d_geometry_area_um2": allocated_geometry_total,
            "allocated_neuron_segment_area_um2": allocated_actual_total,
            "geometry_coverage_error_pct": geometry_coverage_error_pct,
            "actual_area_coverage_error_pct": actual_area_coverage_error_pct,
            "max_segment_support_closure_error_pct": float(np.max(per_segment_error)),
        })

    if max_segment_closure_pct > AREA_COVERAGE_TOLERANCE_PCT:
        raise RuntimeError(
            f"NEURON segment area support does not close over SWC half-edges: "
            f"max per-segment closure error {max_segment_closure_pct:.12g}%"
        )
    max_section_actual_closure = max(
        (row["actual_area_coverage_error_pct"] for row in section_rows),
        default=0.0,
    )
    if max_section_actual_closure > AREA_COVERAGE_TOLERANCE_PCT:
        raise RuntimeError(
            "not all actual NEURON segment area was allocated to electrical "
            f"SWC support; max section residual {max_section_actual_closure:.12g}%"
        )

    neuron_support_total = float(sum(neuron_area.values()))
    total_difference_pct = (
        100.0 * (neuron_support_total - sum(amsn_area.values()))
        / max(sum(amsn_area.values()), 1e-30)
    )

    node_rows = []
    abs_node_errors = []
    signed_node_errors = []
    for node_id, amsn_value in amsn_area.items():
        neuron_value = float(neuron_area[node_id])
        signed = 100.0 * (neuron_value - amsn_value) / max(amsn_value, 1e-30)
        absolute = abs(signed)
        node = morphology.nodes[node_id]
        degree = len(morphology.children[node_id]) + (1 if node.parent_id != -1 else 0)
        abs_node_errors.append(absolute)
        signed_node_errors.append(signed)
        node_rows.append({
            "morphology_label": MORPHOLOGY_LABEL,
            "electrical_node_id": node_id,
            "swc_neurite_type": node.neurite_type,
            "swc_x_um": node.x_um,
            "swc_y_um": node.y_um,
            "swc_z_um": node.z_um,
            "electrical_degree": degree,
            "amsn_control_volume_area_um2": amsn_value,
            "neuron_segment_area_support_um2": neuron_value,
            "signed_area_difference_pct": signed,
            "absolute_area_difference_pct": absolute,
        })

    edge_rows_out = []
    abs_edge_errors = []
    for key, data in edge_allocations.items():
        for side, amsn_key, neuron_key, geometry_key in (
            ("parent", "amsn_parent_half_area_um2", "neuron_parent_half_area_um2", "pt3d_parent_half_area_um2"),
            ("child", "amsn_child_half_area_um2", "neuron_child_half_area_um2", "pt3d_child_half_area_um2"),
        ):
            amsn_value = float(data[amsn_key])
            neuron_value = float(data[neuron_key])
            signed = 100.0 * (neuron_value - amsn_value) / max(amsn_value, 1e-30)
            abs_edge_errors.append(abs(signed))
            edge_rows_out.append({
                "morphology_label": MORPHOLOGY_LABEL,
                "source_swc_parent_id": data["source_swc_parent_id"],
                "source_swc_child_id": data["source_swc_child_id"],
                "neuron_section": data["neur_section"],
                "swc_edge_length_um": data["swc_length_um"],
                "control_volume_side": side,
                "amsn_half_edge_area_um2": amsn_value,
                "neuron_segment_area_support_um2": neuron_value,
                "pt3d_geometric_half_edge_area_um2": data[geometry_key],
                "signed_area_difference_pct": signed,
                "absolute_area_difference_pct": abs(signed),
            })

    result_dir = Path(__file__).parents[1] / "results"
    prefix = "" if MORPHOLOGY_LABEL == "NMO_290988" else f"{MORPHOLOGY_LABEL}_"
    node_csv = result_dir / f"{prefix}human_membrane_area_control_volumes_2026-11-21.csv"
    edge_csv = result_dir / f"{prefix}human_membrane_area_half_edges_2026-11-21.csv"
    section_csv = result_dir / f"{prefix}human_membrane_area_section_coverage_2026-11-21.csv"
    write_csv(node_csv, node_rows)
    write_csv(edge_csv, edge_rows_out)
    write_csv(section_csv, section_rows)

    def stats(values):
        arr = np.asarray(values, dtype=float)
        return (
            float(np.median(arr)),
            float(np.percentile(arr, 95)),
            float(np.percentile(arr, 99)),
            float(np.max(arr)),
        )

    node_stats = stats(abs_node_errors)
    edge_stats = stats(abs_edge_errors)
    amsn_total_area = float(sum(amsn_area.values()))
    neuron_total_area = float(sum(neuron_area.values()))
    segment_total_area = float(neuron_total_area)
    print(f"# NEURON={neuron.__version__}; morphology={MORPHOLOGY_LABEL}; path={MORPHOLOGY_PATH}")
    print(
        f"# NEURON_sections={len(sections)}; NEURON_segments={segment_count}; "
        f"max_segment_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(
        f"# electrical_nodes={len(amsn_area)}; active_edges={len(edge_rows)}; "
        f"soma_sections={soma_section_count}; soma_section_area_um2={soma_section_area:.12g}"
    )
    print(
        f"# AMSN_total_control_volume_area_um2={amsn_total_area:.12g}; "
        f"NEURON_allocated_control_volume_area_um2={neuron_total_area:.12g}; "
        f"NEURON_raw_segment_area_um2={neuron_total_area:.12g}; "
        f"total_area_difference_pct={total_difference_pct:.12g}"
    )
    print(
        f"# node_abs_area_error_median_p95_p99_max_pct="
        f"{node_stats[0]:.12g},{node_stats[1]:.12g},{node_stats[2]:.12g},{node_stats[3]:.12g}"
    )
    print(
        f"# edge_half_abs_area_error_median_p95_p99_max_pct="
        f"{edge_stats[0]:.12g},{edge_stats[1]:.12g},{edge_stats[2]:.12g},{edge_stats[3]:.12g}"
    )
    print(
        f"# max_segment_support_closure_error_pct={max_segment_closure_pct:.12g}; "
        f"max_section_actual_area_coverage_error_pct={max_section_actual_closure:.12g}"
    )
    print(f"# raw_node_control_volume_csv={node_csv}")
    print(f"# raw_edge_half_area_csv={edge_csv}")
    print(f"# raw_section_coverage_csv={section_csv}")


if __name__ == "__main__":
    main()
