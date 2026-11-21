"""Matched-support axial-resistance audit against NEURON 9.0.2.

The audit compares the exact half-edge control-volume support around preserved
SWC sites. It computes tapered-cable integrals from the original SWC and from
NEURON Import3D pt3d, then independently checks NEURON's segment.ri() values
against the same pt3d integral for every adjacent segment-centre pair inside
the support.

For a linearly tapered circular cable with endpoint diameters d0 and d1:
    integral(ds / (pi * r(s)**2)) = 4 * length / (pi * d0 * d1)
where the helper converts micrometres to SI geometry (m^-1).

This is a geometry/numerics audit, not a biological validation or voltage fit.
It rejects sites whose parent, site and child do not lie on one ordered section.
"""
from __future__ import annotations

import csv
from bisect import bisect_right
from math import ceil, isfinite, pi, sqrt
import sys

import numpy as np
from neuron import h, __version__ as neuron_version

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


NEURON_MAX_SEGMENT_UM = 0.5
AMSN_REFERENCE_FREQUENCIES_HZ = (2000.0, 4000.0, 6000.0)
AMSN_MAX_SEGMENT_LENGTH_UM = 100.0
AMSN_MAX_ELECTROTONIC_LENGTH = 0.1
RI_OHM_M = 0.7
FIXED_BASAL_SITES = (
    ("basal_q75_source", 3784),
    ("basal_q90", 3814),
)
RI_INTERNAL_TOLERANCE_PCT = 1e-7
NETWORK_INTEGRAL_TOLERANCE_PCT = 1e-7
EPS_UM = 1e-9


def configure_neuron_nseg(sections) -> None:
    for section in sections:
        nseg = max(1, ceil(section.L / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()


def map_swc_position(reader, section_by_name, morphology, node_id):
    """Map an SWC point to Import3D's section arc without scanning all segments."""
    point_index = int(reader.id2pt(node_id))
    section_index = int(reader.point2sec.x[point_index])
    imported = reader.sections.object(section_index)
    type_names = {1: "soma", 2: "axon", 3: "dend", 4: "apic"}
    swc_type = int(imported.type)
    if swc_type not in type_names:
        raise RuntimeError(
            f"Unsupported Import3D section type {swc_type} for SWC node {node_id}"
        )
    base_name = type_names[swc_type]
    name_index = int(imported.nameindex)
    hoc_name = f"{base_name}[{name_index}]" if name_index > 0 else base_name
    candidates = [hoc_name]
    if name_index == 0:
        candidates.extend([f"{base_name}[0]", base_name])
    section_name = next(
        (name for name in candidates if name in section_by_name), None
    )
    if section_name is None:
        raise RuntimeError(
            f"Import3D maps SWC node {node_id} to missing section {hoc_name}"
        )
    section = section_by_name[section_name]

    if section_index == 0 and int(imported.d.size()) == 1:
        arc_um = 0.5 * float(section.L)
        geometry_error_um = 0.0
    else:
        first_point_index = int(imported.id)
        local_index = (
            point_index - first_point_index
            + (0 if int(imported.first) == 1 else 1)
        )
        n3d = int(h.n3d(sec=section))
        if local_index < 0 or local_index >= n3d:
            raise RuntimeError(
                f"SWC node {node_id}: local pt3d index {local_index} outside "
                f"{section_name} with {n3d} points"
            )
        xyz = (
            float(h.x3d(local_index, sec=section)),
            float(h.y3d(local_index, sec=section)),
            float(h.z3d(local_index, sec=section)),
        )
        node = morphology.nodes[node_id]
        geometry_error_um = sqrt(
            (node.x_um - xyz[0]) ** 2
            + (node.y_um - xyz[1]) ** 2
            + (node.z_um - xyz[2]) ** 2
        )
        arc_um = float(h.arc3d(local_index, sec=section))

    return {
        "section": section,
        "section_name": section_name,
        "x": min(1.0, max(0.0, arc_um / float(section.L))),
        "arc_um": arc_um,
        "geometry_offset_um": geometry_error_um,
    }


def linear_diameter_factor_m_inv(length_um: float, d0_um: float, d1_um: float) -> float:
    """Exact integral ds/(pi*r^2) for a linear taper, in inverse metres."""
    values = (float(length_um), float(d0_um), float(d1_um))
    if not all(isfinite(value) for value in values):
        raise ValueError("axial geometry inputs must be finite")
    length_um, d0_um, d1_um = values
    if length_um < 0.0 or d0_um <= 0.0 or d1_um <= 0.0:
        raise ValueError("length must be non-negative and diameters positive")
    if length_um == 0.0:
        return 0.0
    return 4.0e6 * length_um / (pi * d0_um * d1_um)


def run_geometry_self_checks() -> None:
    """Small deterministic checks for units, taper and interval additivity."""
    cylinder = linear_diameter_factor_m_inv(10.0, 10.0, 10.0)
    expected_cylinder = 4.0e6 * 10.0 / (pi * 100.0)
    assert abs(cylinder - expected_cylinder) <= expected_cylinder * 1e-14

    whole = linear_diameter_factor_m_inv(17.0, 4.0, 13.0)
    split_fraction = 0.37
    middle_diameter = 4.0 + (13.0 - 4.0) * split_fraction
    split = (
        linear_diameter_factor_m_inv(17.0 * split_fraction, 4.0, middle_diameter)
        + linear_diameter_factor_m_inv(
            17.0 * (1.0 - split_fraction), middle_diameter, 13.0
        )
    )
    assert abs(whole - split) <= whole * 1e-13
    reversed_whole = linear_diameter_factor_m_inv(17.0, 13.0, 4.0)
    assert abs(whole - reversed_whole) <= whole * 1e-14


def path_distances_um(morphology: SWCMorphology) -> dict[int, float]:
    return reference.path_distances_um(morphology)


def quantile_candidate(candidates, distances, quantile: float) -> int:
    ordered = sorted((distances[node_id], node_id) for node_id in candidates)
    if not ordered:
        raise RuntimeError("no valid internal unbranched sites for requested neurite")
    return ordered[round((len(ordered) - 1) * quantile)][1]


def select_site_rows(morphology, reader, section_by_name, distances):
    """Keep prior basal sites and add another basal branch plus apical sites."""
    position_cache = {}

    def position(node_id):
        if node_id not in position_cache:
            position_cache[node_id] = map_swc_position(
                reader, section_by_name, morphology, node_id
            )
        return position_cache[node_id]

    def is_ordered_internal_site(node_id):
        node = morphology.nodes[node_id]
        children = morphology.children[node_id]
        if node.parent_id == -1 or len(children) != 1:
            return False
        parent_position = position(node.parent_id)
        site_position = position(node_id)
        child_position = position(children[0])
        same_section = (
            parent_position["section_name"]
            == site_position["section_name"]
            == child_position["section_name"]
        )
        ordered = (
            parent_position["x"] + 1e-12
            < site_position["x"]
            < child_position["x"] - 1e-12
        )
        return same_section and ordered

    for _, node_id in FIXED_BASAL_SITES:
        if not is_ordered_internal_site(node_id):
            raise RuntimeError(
                f"fixed basal site {node_id} is not an ordered unbranched "
                "point within one NEURON section"
            )

    source_section = position(FIXED_BASAL_SITES[0][1])["section_name"]
    valid_by_type = {3: [], 4: []}
    for node_id, node in morphology.nodes.items():
        if node.neurite_type in valid_by_type and is_ordered_internal_site(node_id):
            valid_by_type[node.neurite_type].append(node_id)

    fixed_ids = {value for _, value in FIXED_BASAL_SITES}
    alternate_basal = [
        node_id for node_id in valid_by_type[3]
        if position(node_id)["section_name"] != source_section
        and node_id not in fixed_ids
    ]
    if not alternate_basal:
        raise RuntimeError("could not find a valid basal site on another NEURON section")

    apical = valid_by_type[4]
    if len(apical) < 2:
        raise RuntimeError(
            f"need at least two valid apical internal sites; found {len(apical)}"
        )

    rows = [
        *FIXED_BASAL_SITES,
        ("basal_other_branch_q75", quantile_candidate(alternate_basal, distances, 0.75)),
        ("apical_q75", quantile_candidate(apical, distances, 0.75)),
        ("apical_q90", quantile_candidate(apical, distances, 0.90)),
    ]
    ids = [node_id for _, node_id in rows]
    if len(set(ids)) != len(ids):
        raise RuntimeError(f"site selection produced duplicate SWC IDs: {rows}")

    mapped = {}
    for label, node_id in rows:
        node = morphology.nodes[node_id]
        parent = position(node.parent_id)
        site = position(node_id)
        child = position(morphology.children[node_id][0])
        mapped[node_id] = {
            **site,
            "parent_x": parent["x"],
            "child_x": child["x"],
            "mapping_offset_um": sqrt(
                site["geometry_offset_um"] ** 2
                + min(
                    abs(site["x"] - segment.x) * site["section"].L
                    for segment in site["section"]
                ) ** 2
            ),
        }
    return rows, mapped


def get_incident_amsn_edges(sectioned, node_id):
    tree = sectioned.tree
    name = sectioned.swc_node_to_compartment[node_id]
    index = tree.index[name]
    parent_index = int(tree.parent_index[index])
    incoming = None
    if parent_index >= 0:
        child_name = tree.order[index]
        incoming = {
            "child_name": child_name,
            "length_um": sectioned.edge_arc_length_m[child_name] * 1e6,
        }

    outgoing = []
    for child_index_value in np.flatnonzero(tree.parent_index == index):
        child_name = tree.order[int(child_index_value)]
        outgoing.append({
            "child_name": child_name,
            "length_um": sectioned.edge_arc_length_m[child_name] * 1e6,
        })
    if incoming is None or len(outgoing) != 1:
        raise RuntimeError(
            f"site {node_id} must have exactly one incoming and one outgoing "
            "AMSN electrical edge"
        )
    return incoming, outgoing[0]


def integrate_swc_from_site(morphology, node_id, direction: int, distance_um: float):
    """Integrate exact SWC taper geometry for a proximal (-1) or distal (+1) ray."""
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 (parent) or +1 (child)")
    remaining = float(distance_um)
    if remaining <= 0.0:
        raise ValueError("support distance must be positive")
    current_id = node_id
    factor = 0.0
    traversed = 0.0

    while remaining > EPS_UM:
        current = morphology.nodes[current_id]
        if direction < 0:
            neighbour_id = current.parent_id
            if neighbour_id == -1:
                raise RuntimeError(
                    f"proximal support for node {node_id} reaches the morphology root"
                )
        else:
            children = morphology.children[current_id]
            if len(children) != 1:
                raise RuntimeError(
                    f"distal support for node {node_id} reaches a branch point "
                    "before the required half-edge distance"
                )
            neighbour_id = children[0]

        neighbour = morphology.nodes[neighbour_id]
        segment_length = sqrt(
            (neighbour.x_um - current.x_um) ** 2
            + (neighbour.y_um - current.y_um) ** 2
            + (neighbour.z_um - current.z_um) ** 2
        )
        if segment_length <= 0.0:
            raise RuntimeError(
                f"zero-length SWC edge encountered at {current_id}->{neighbour_id}"
            )
        take = min(remaining, segment_length)
        fraction = take / segment_length
        end_radius = current.radius_um + (
            neighbour.radius_um - current.radius_um
        ) * fraction
        factor += linear_diameter_factor_m_inv(
            take, 2.0 * current.radius_um, 2.0 * end_radius
        )
        traversed += take
        remaining -= take
        if remaining <= EPS_UM:
            break
        current_id = neighbour_id

    if remaining > EPS_UM:
        raise RuntimeError(
            f"could only integrate {traversed:.9f} of {distance_um:.9f} um "
            f"from SWC node {node_id}"
        )
    return factor, traversed


def read_neuron_profile(section):
    n3d = int(h.n3d(sec=section))
    if n3d < 2:
        raise RuntimeError(f"NEURON section {section.name()} has fewer than two pt3d points")
    arcs = [float(h.arc3d(i, sec=section)) for i in range(n3d)]
    diameters = [abs(float(h.diam3d(i, sec=section))) for i in range(n3d)]
    if any(arcs[i + 1] < arcs[i] for i in range(n3d - 1)):
        raise RuntimeError(f"non-monotonic pt3d arc in {section.name()}")
    return arcs, diameters


def integrate_neuron_profile_factor(section, profile, x_start: float, x_end: float):
    """Reproduce NEURON's pt3d tapered axial-geometry integral over an x interval."""
    if not (0.0 <= x_start < x_end <= 1.0):
        raise ValueError(f"invalid NEURON support x interval [{x_start}, {x_end}]")
    arcs, diameters = profile
    start_um = x_start * float(section.L)
    end_um = x_end * float(section.L)
    index = max(0, bisect_right(arcs, start_um) - 1)
    factor = 0.0
    covered_um = 0.0

    while index < len(arcs) - 1 and arcs[index] < end_um:
        arc0, arc1 = arcs[index], arcs[index + 1]
        if arc1 - arc0 > 1e-15:
            left = max(start_um, arc0)
            right = min(end_um, arc1)
            if right > left:
                fraction0 = (left - arc0) / (arc1 - arc0)
                fraction1 = (right - arc0) / (arc1 - arc0)
                d0 = diameters[index] + (
                    diameters[index + 1] - diameters[index]
                ) * fraction0
                d1 = diameters[index] + (
                    diameters[index + 1] - diameters[index]
                ) * fraction1
                factor += linear_diameter_factor_m_inv(right - left, d0, d1)
                covered_um += right - left
        index += 1

    if abs(covered_um - (end_um - start_um)) > 1e-6:
        raise RuntimeError(
            f"NEURON pt3d profile covered {covered_um:.9f} of "
            f"{end_um - start_um:.9f} um in {section.name()}"
        )
    return factor


def neuron_network_factor(section, profile, x_start: float, x_end: float):
    """Sum real NEURON centre-to-centre ri plus exact endpoint caps."""
    segments = list(section)
    points = [(x_start, None)]
    for index, segment in enumerate(segments):
        if x_start + 1e-12 < float(segment.x) < x_end - 1e-12:
            points.append((float(segment.x), index))
    points.append((x_end, None))

    factor = 0.0
    checked_pairs = 0
    max_ri_error_pct = 0.0
    network_resistance_mohm = 0.0

    for (x0, index0), (x1, index1) in zip(points, points[1:]):
        exact_piece = integrate_neuron_profile_factor(section, profile, x0, x1)
        if (
            index0 is not None
            and index1 is not None
            and index1 == index0 + 1
        ):
            actual_ri_mohm = float(segments[index1].ri())
            expected_ri_mohm = exact_piece * RI_OHM_M * 1e-6
            error_pct = (
                100.0 * abs(actual_ri_mohm - expected_ri_mohm)
                / max(abs(expected_ri_mohm), 1e-30)
            )
            max_ri_error_pct = max(max_ri_error_pct, error_pct)
            checked_pairs += 1
            network_resistance_mohm += actual_ri_mohm
            factor += actual_ri_mohm * 1e6 / RI_OHM_M
        else:
            network_resistance_mohm += exact_piece * RI_OHM_M * 1e-6
            factor += exact_piece

    return {
        "factor_m_inv": factor,
        "resistance_ohm": factor * RI_OHM_M,
        "resistance_mohm": network_resistance_mohm,
        "ri_pairs_checked": checked_pairs,
        "ri_max_relative_error_pct": max_ri_error_pct,
    }


def audit_one_site(morphology, sectioned, node_id, site_map, profile):
    incoming, outgoing = get_incident_amsn_edges(sectioned, node_id)
    incoming_half_um = 0.5 * incoming["length_um"]
    outgoing_half_um = 0.5 * outgoing["length_um"]

    amsn_in_factor, incoming_traversed = integrate_swc_from_site(
        morphology, node_id, -1, incoming_half_um
    )
    amsn_out_factor, outgoing_traversed = integrate_swc_from_site(
        morphology, node_id, +1, outgoing_half_um
    )
    amsn_factor = amsn_in_factor + amsn_out_factor

    section = site_map["section"]
    x_start = site_map["x"] - incoming_half_um / float(section.L)
    x_end = site_map["x"] + outgoing_half_um / float(section.L)
    neuron_direct_factor = integrate_neuron_profile_factor(
        section, profile, x_start, x_end
    )
    neuron_network = neuron_network_factor(
        section, profile, x_start, x_end
    )
    neuron_factor = neuron_network["factor_m_inv"]

    support_length_um = incoming_half_um + outgoing_half_um
    neuron_support_length_um = (x_end - x_start) * float(section.L)
    length_error_pct = (
        100.0 * abs(neuron_support_length_um - support_length_um)
        / max(support_length_um, 1e-30)
    )
    network_vs_direct_pct = (
        100.0 * abs(neuron_factor - neuron_direct_factor)
        / max(abs(neuron_direct_factor), 1e-30)
    )
    difference_pct = (
        100.0 * (amsn_factor - neuron_factor)
        / max(abs(neuron_factor), 1e-30)
    )

    if length_error_pct > 1e-5:
        raise RuntimeError(
            f"support-length mismatch at SWC node {node_id}: {length_error_pct:.6g}%"
        )
    if network_vs_direct_pct > NETWORK_INTEGRAL_TOLERANCE_PCT:
        raise RuntimeError(
            f"NEURON ri network/direct integral mismatch at {node_id}: "
            f"{network_vs_direct_pct:.6g}%"
        )
    if neuron_network["ri_pairs_checked"] < 1:
        raise RuntimeError(
            f"no adjacent NEURON segment-centre ri pairs fell inside support "
            f"for SWC node {node_id}"
        )
    if neuron_network["ri_max_relative_error_pct"] > RI_INTERNAL_TOLERANCE_PCT:
        raise RuntimeError(
            f"NEURON segment.ri() disagrees with pt3d integral at {node_id}: "
            f"{neuron_network['ri_max_relative_error_pct']:.6g}%"
        )

    return {
        "incoming_half_um": incoming_half_um,
        "outgoing_half_um": outgoing_half_um,
        "support_length_um": support_length_um,
        "incoming_factor_m_inv": amsn_in_factor,
        "outgoing_factor_m_inv": amsn_out_factor,
        "amsn_factor_m_inv": amsn_factor,
        "neuron_direct_factor_m_inv": neuron_direct_factor,
        "neuron_factor_m_inv": neuron_factor,
        "factor_difference_m_inv": amsn_factor - neuron_factor,
        "relative_difference_pct": difference_pct,
        "amsn_resistance_ohm": amsn_factor * RI_OHM_M,
        "neuron_resistance_ohm": neuron_factor * RI_OHM_M,
        "ri_pairs_checked": neuron_network["ri_pairs_checked"],
        "ri_max_relative_error_pct": neuron_network["ri_max_relative_error_pct"],
        "network_vs_direct_pct": network_vs_direct_pct,
        "support_length_error_pct": length_error_pct,
        "x_start": x_start,
        "x_end": x_end,
    }


def main() -> None:
    run_geometry_self_checks()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    configure_neuron_nseg(sections)
    section_by_name = {section.name(): section for section in sections}
    distances = path_distances_um(morphology)
    site_rows, site_maps = select_site_rows(
        morphology, reader, section_by_name, distances
    )
    profiles = {
        site_maps[node_id]["section_name"]: read_neuron_profile(
            site_maps[node_id]["section"]
        )
        for _, node_id in site_rows
    }

    print("# AMSN / NEURON matched-support axial-resistance audit")
    print(
        f"# NEURON={neuron_version}; NEURON_Ri={RI_OHM_M:g} ohm*m; "
        f"NEURON_max_segment={NEURON_MAX_SEGMENT_UM:g} um; "
        f"segments={sum(section.nseg for section in sections)}"
    )
    print(
        "# NEURON ri() is checked between adjacent segment centres; partial "
        "support caps are integrated from the same pt3d profile."
    )
    print(
        "# Site IDs are deterministic quantiles among internal, unbranched "
        "points that map parent/site/child to one ordered NEURON section."
    )
    for label, node_id in site_rows:
        mapped = site_maps[node_id]
        print(
            f"# site={label}; node={node_id}; section={mapped['section_name']}; "
            f"x={mapped['x']:.9f}; geometry_offset={mapped['geometry_offset_um']:.9g} um; "
            f"mapping_offset={mapped['mapping_offset_um']:.9g} um"
        )

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow([
        "reference_frequency_hz",
        "amsn_compartments",
        "site",
        "swc_node_id",
        "neuron_section",
        "parent_x",
        "target_x",
        "child_x",
        "incoming_edge_um",
        "outgoing_edge_um",
        "incoming_half_support_um",
        "outgoing_half_support_um",
        "matched_support_length_um",
        "amsn_incoming_half_factor_m_inv",
        "amsn_outgoing_half_factor_m_inv",
        "amsn_total_factor_m_inv",
        "neuron_pt3d_direct_factor_m_inv",
        "neuron_ri_network_factor_m_inv",
        "factor_difference_m_inv",
        "relative_factor_difference_pct",
        "amsn_equivalent_resistance_ohm",
        "neuron_equivalent_resistance_ohm",
        "neuron_ri_pairs_checked",
        "neuron_ri_max_relative_error_pct",
        "neuron_network_vs_direct_pct",
        "support_length_error_pct",
        "neuron_support_x_start",
        "neuron_support_x_end",
    ])

    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        sectioned = to_sectioned_cable_tree(
            morphology,
            max_segment_length_um=AMSN_MAX_SEGMENT_LENGTH_UM,
            max_electrotonic_length=AMSN_MAX_ELECTROTONIC_LENGTH,
            reference_frequency_hz=frequency_hz,
            preserve_node_ids={node_id for _, node_id in site_rows},
        )
        for label, node_id in site_rows:
            mapped = site_maps[node_id]
            result = audit_one_site(
                morphology,
                sectioned,
                node_id,
                mapped,
                profiles[mapped["section_name"]],
            )
            incoming, outgoing = get_incident_amsn_edges(sectioned, node_id)
            writer.writerow([
                f"{frequency_hz:.6f}",
                sectioned.tree.n_compartments,
                label,
                node_id,
                mapped["section_name"],
                f"{mapped['parent_x']:.12f}",
                f"{mapped['x']:.12f}",
                f"{mapped['child_x']:.12f}",
                f"{incoming['length_um']:.9f}",
                f"{outgoing['length_um']:.9f}",
                f"{result['incoming_half_um']:.9f}",
                f"{result['outgoing_half_um']:.9f}",
                f"{result['support_length_um']:.9f}",
                f"{result['incoming_factor_m_inv']:.12g}",
                f"{result['outgoing_factor_m_inv']:.12g}",
                f"{result['amsn_factor_m_inv']:.12g}",
                f"{result['neuron_direct_factor_m_inv']:.12g}",
                f"{result['neuron_factor_m_inv']:.12g}",
                f"{result['factor_difference_m_inv']:.12g}",
                f"{result['relative_difference_pct']:.12g}",
                f"{result['amsn_resistance_ohm']:.12g}",
                f"{result['neuron_resistance_ohm']:.12g}",
                result["ri_pairs_checked"],
                f"{result['ri_max_relative_error_pct']:.12g}",
                f"{result['network_vs_direct_pct']:.12g}",
                f"{result['support_length_error_pct']:.12g}",
                f"{result['x_start']:.12f}",
                f"{result['x_end']:.12f}",
            ])


if __name__ == "__main__":
    main()
