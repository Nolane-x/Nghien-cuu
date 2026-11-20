"""Matched-support membrane-area audit for protected dendritic control points.

For q75/q90 protected nodes, AMSN assigns a lumped node area by adding the
proximal/distal half-area contributions of each incident electrical edge.
This script reconstructs the same support interval along the corresponding
NEURON section: half of the incoming edge and half of the outgoing edge.

NEURON segment areas are integrated over that same arc interval using the
fractional overlap of each NEURON segment's x-domain. This is more comparable
than comparing one 0.5-um NEURON segment with an AMSN node that aggregates
several micrometres of adjacent cable.

The experiment is geometry-only: it does not change the solver, place a
synapse, or run a voltage trace. It reports the support interval and edge
lengths so the comparison remains inspectable.
"""
from __future__ import annotations

from math import ceil

import numpy as np
from neuron import h, __version__ as neuron_version

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


NEURON_MAX_SEGMENT_UM = 0.5
AMSN_REFERENCE_FREQUENCIES_HZ = (2000.0, 4000.0, 6000.0)
AMSN_MAX_SEGMENT_LENGTH_UM = 100.0
AMSN_MAX_ELECTROTONIC_LENGTH = 0.1

SITE_ROWS = (
    ("basal_q75_source", 3784),
    ("basal_q90", 3814),
)
PROTECTED_IDS = {node_id for _, node_id in SITE_ROWS}


def configure_neuron_nseg(sections) -> None:
    for section in sections:
        nseg = max(1, ceil(section.L / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()


def map_swc_site(reader, section_by_name, morphology, node_id):
    segment, total, geometry, centre, section_name, normalized = (
        reference.locate_neuron_segment(
            reader, section_by_name, morphology.nodes[node_id]
        )
    )
    return {
        "segment": segment,
        "section": section_by_name[section_name],
        "section_name": section_name,
        "x": float(normalized),
        "mapping_offset_um": float(total),
        "geometry_offset_um": float(geometry),
        "centre_offset_um": float(centre),
    }


def integrate_neuron_area_over_x(section, x_start: float, x_end: float):
    """Integrate segment areas by fractional overlap with [x_start, x_end]."""
    if not (0.0 <= x_start < x_end <= 1.0):
        raise ValueError(
            f"invalid NEURON support x interval [{x_start}, {x_end}]"
        )
    segments = list(section)
    nseg = len(segments)
    width = 1.0 / nseg
    total_area_um2 = 0.0
    used = 0

    for i, segment in enumerate(segments):
        segment_start = i * width
        segment_end = (i + 1) * width
        overlap_start = max(x_start, segment_start)
        overlap_end = min(x_end, segment_end)
        if overlap_end <= overlap_start:
            continue
        fraction = (overlap_end - overlap_start) / width
        total_area_um2 += float(segment.area()) * fraction
        used += 1

    return total_area_um2, used


def get_incident_amsn_edges(sectioned, node_id):
    tree = sectioned.tree
    mapping = sectioned.swc_node_to_compartment
    idx = tree.index[mapping[node_id]]
    name = tree.order[idx]
    parent_idx = int(tree.parent_index[idx])

    incoming = None
    if parent_idx >= 0:
        incoming_child_name = tree.order[idx]
        incoming = {
            "neighbor_name": tree.order[parent_idx],
            "child_name": incoming_child_name,
            "length_um": sectioned.edge_arc_length_m[incoming_child_name] * 1e6,
        }

    outgoing = []
    for child_idx_value in np.flatnonzero(tree.parent_index == idx):
        child_idx = int(child_idx_value)
        child_name = tree.order[child_idx]
        outgoing.append({
            "neighbor_name": child_name,
            "child_name": child_name,
            "length_um": sectioned.edge_arc_length_m[child_name] * 1e6,
        })

    return {
        "compartment_name": name,
        "compartment_index": idx,
        "incoming": incoming,
        "outgoing": outgoing,
        "control_area_um2": float(tree.area_m2[idx] * 1e12),
        "control_length_um": float(tree.by_name[name].length_m * 1e6),
    }


def matched_neuron_support(
    reader, section_by_name, morphology, node_id, site_map, edge_data
):
    """Map AMSN incident half-edge lengths to the same NEURON section x-axis.

    This pilot deliberately requires one incoming and one outgoing edge in an
    unbranched path. Branch points and multi-section supports are rejected
    rather than silently approximated.
    """
    node = morphology.nodes[node_id]
    parent_id = node.parent_id
    children = morphology.children[node_id]
    if parent_id == -1 or len(children) != 1:
        raise RuntimeError(
            f"SWC node {node_id} is not an internal unbranched path point; "
            f"parent={parent_id}, children={children}"
        )
    if edge_data["incoming"] is None or len(edge_data["outgoing"]) != 1:
        raise RuntimeError(
            f"AMSN node {node_id} lacks exactly one incoming/outgoing edge"
        )

    parent_map = map_swc_site(
        reader, section_by_name, morphology, parent_id
    )
    child_map = map_swc_site(
        reader, section_by_name, morphology, children[0]
    )
    section = site_map["section"]
    section_name = site_map["section_name"]
    if (
        parent_map["section_name"] != section_name
        or child_map["section_name"] != section_name
    ):
        raise RuntimeError(
            f"SWC node {node_id} crosses NEURON sections: "
            f"parent={parent_map['section_name']}, site={section_name}, "
            f"child={child_map['section_name']}"
        )

    target_x = site_map["x"]
    parent_x = parent_map["x"]
    child_x = child_map["x"]
    if not (parent_x < target_x < child_x):
        raise RuntimeError(
            f"NEURON section orientation is not parent<site<child for node {node_id}: "
            f"{parent_x} < {target_x} < {child_x}"
        )

    incoming_um = edge_data["incoming"]["length_um"]
    outgoing_um = edge_data["outgoing"][0]["length_um"]
    left_half_um = 0.5 * incoming_um
    right_half_um = 0.5 * outgoing_um
    x_start_raw = target_x - left_half_um / float(section.L)
    x_end_raw = target_x + right_half_um / float(section.L)
    if x_start_raw < 0.0 or x_end_raw > 1.0:
        raise RuntimeError(
            f"AMSN support for node {node_id} extends beyond NEURON section: "
            f"[{x_start_raw}, {x_end_raw}]"
        )
    neuron_area_um2, segment_count = integrate_neuron_area_over_x(
        section, x_start_raw, x_end_raw
    )

    return {
        "parent_x": parent_x,
        "target_x": target_x,
        "child_x": child_x,
        "incoming_half_support_um": left_half_um,
        "outgoing_half_support_um": right_half_um,
        "support_length_um": left_half_um + right_half_um,
        "x_start": x_start_raw,
        "x_end": x_end_raw,
        "neuron_area_um2": neuron_area_um2,
        "amsn_area_um2": edge_data["control_area_um2"],
        "area_difference_um2": edge_data["control_area_um2"] - neuron_area_um2,
        "area_difference_pct": (
            100.0 * (edge_data["control_area_um2"] - neuron_area_um2)
            / neuron_area_um2
        ),
        "segments_overlapped": segment_count,
    }


def main() -> None:
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, neuron_sections = reference.import_swc_with_neuron()
    configure_neuron_nseg(neuron_sections)
    section_by_name = {section.name(): section for section in neuron_sections}

    site_maps = {
        node_id: map_swc_site(reader, section_by_name, morphology, node_id)
        for _, node_id in SITE_ROWS
    }

    print("# AMSN/NEURON matched-support area integration audit")
    print(
        f"# NEURON={neuron_version}; max_segment={NEURON_MAX_SEGMENT_UM:g}um; "
        f"segments={sum(section.nseg for section in neuron_sections)}"
    )
    for name, node_id in SITE_ROWS:
        mapped = site_maps[node_id]
        print(
            f"# site={name}; node={node_id}; section={mapped['section_name']}; "
            f"x={mapped['x']:.9f}; mapping_offset={mapped['mapping_offset_um']:.6f}um"
        )

    print(
        "reference_frequency_hz,amsn_compartments,site,swc_node_id,"
        "section,parent_x,target_x,child_x,incoming_edge_um,outgoing_edge_um,"
        "incoming_half_support_um,outgoing_half_support_um,"
        "matched_support_length_um,neuron_area_over_same_support_um2,"
        "amsn_control_volume_area_um2,area_difference_um2,"
        "area_difference_pct,neuron_segments_overlapped,"
        "neuron_support_x_start,neuron_support_x_end"
    )

    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        sectioned = to_sectioned_cable_tree(
            morphology,
            max_segment_length_um=AMSN_MAX_SEGMENT_LENGTH_UM,
            max_electrotonic_length=AMSN_MAX_ELECTROTONIC_LENGTH,
            reference_frequency_hz=frequency_hz,
            preserve_node_ids=PROTECTED_IDS,
        )
        for site_name, node_id in SITE_ROWS:
            edge_data = get_incident_amsn_edges(sectioned, node_id)
            support = matched_neuron_support(
                reader, section_by_name, morphology, node_id,
                site_maps[node_id], edge_data
            )
            print(
                f"{frequency_hz:.6f},{sectioned.tree.n_compartments},"
                f"{site_name},{node_id},{site_maps[node_id]['section_name']},"
                f"{support['parent_x']:.9f},{support['target_x']:.9f},"
                f"{support['child_x']:.9f},"
                f"{edge_data['incoming']['length_um']:.9f},"
                f"{edge_data['outgoing'][0]['length_um']:.9f},"
                f"{support['incoming_half_support_um']:.9f},"
                f"{support['outgoing_half_support_um']:.9f},"
                f"{support['support_length_um']:.9f},"
                f"{support['neuron_area_um2']:.9f},"
                f"{support['amsn_area_um2']:.9f},"
                f"{support['area_difference_um2']:.9f},"
                f"{support['area_difference_pct']:.9f},"
                f"{support['segments_overlapped']},"
                f"{support['x_start']:.12f},{support['x_end']:.12f}"
            )


if __name__ == "__main__":
    main()
