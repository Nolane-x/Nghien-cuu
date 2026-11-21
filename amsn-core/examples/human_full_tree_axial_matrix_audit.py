"""Whole-tree AMSN vs NEURON axial conductance-matrix audit.

The source SWC is converted to AMSN's exact node-centred CableTree. NEURON's
25,233-segment Import3D cable is reduced edge-by-edge to the same electrical
SWC vertices by summing actual segment.ri() centre-to-centre resistances and
the two partial endpoint caps. The soma outline/wire policy is applied by the
same electrical_node_mapping() used by AMSN.

The two resulting sparse tree Laplacians have identical vertex and edge
topology. This script compares every edge conductance and applies both
operators to deterministic random voltage vectors, without materialising a
dense 8,893 x 8,893 matrix.

This is a numerical matrix comparison for one partial morphology. It is not
biological validation and does not change production solver parameters.
"""
from __future__ import annotations

import bisect
import csv
from math import ceil, pi
from pathlib import Path
import sys

import numpy as np
import neuron
from neuron import h

import human_full_tree_axial_network_audit as audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


DATA = reference.DATA
RI_OHM_M = 0.7
NEURON_RA_OHM_CM = RI_OHM_M * 100.0
NEURON_MAX_SEGMENT_UM = 0.5
RANDOM_SEED = 20261121
RANDOM_VOLTAGE_CASES = 32
RANDOM_VOLTAGE_STD_V = 0.010
EDGE_MATCH_TOLERANCE = 1e-10
MATRIX_CONSERVATION_TOLERANCE_A = 1e-18
NETWORK_DIRECT_TOLERANCE_PCT = 1e-7


def configure_neuron_reference(sections) -> None:
    for section in sections:
        section.Ra = NEURON_RA_OHM_CM
        nseg = max(1, ceil(float(section.L) / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()
    h.define_shape()


def pt3d_pair_factor(section, profile, first_index, second_index, x0, x1):
    """Exact taper factor on a single Import3D pt3d interval, in m^-1."""
    if x1 < x0:
        return pt3d_pair_factor(
            section, profile, first_index, second_index, x1, x0
        )
    arcs = profile["arc"]
    diameters = profile["diameter"]
    arc_a = float(arcs[first_index])
    arc_b = float(arcs[second_index])
    if arc_b < arc_a:
        arc_a, arc_b = arc_b, arc_a
        first_index, second_index = second_index, first_index
    span = arc_b - arc_a
    if span <= 1e-14:
        raise RuntimeError(
            f"zero pt3d arc span in {section.name()}: "
            f"{first_index}->{second_index}"
        )
    lo_um = x0 * float(section.L)
    hi_um = x1 * float(section.L)
    frac0 = (lo_um - arc_a) / span
    frac1 = (hi_um - arc_a) / span
    if frac0 < -1e-8 or frac1 > 1.0 + 1e-8:
        raise RuntimeError(
            f"requested x interval outside pt3d pair in {section.name()}: "
            f"f={frac0:.9g}..{frac1:.9g}"
        )
    d0 = diameters[first_index] + (
        diameters[second_index] - diameters[first_index]
    ) * frac0
    d1 = diameters[first_index] + (
        diameters[second_index] - diameters[first_index]
    ) * frac1
    length_um = max(0.0, hi_um - lo_um)
    if length_um <= 1e-14:
        return 0.0
    if d0 <= 0.0 or d1 <= 0.0:
        raise RuntimeError("non-positive pt3d diameter in axial matrix audit")
    return 4.0e6 * length_um / (pi * d0 * d1)


def prepare_section_segment_centres(sections):
    """Cache NEURON segment-centre x coordinates for binary interval searches."""
    by_name = {}
    for section in sections:
        by_name[section.name()] = {
            "section": section,
            "segments": list(section),
            "x": [float(segment.x) for segment in section],
        }
    return by_name


def _endpoint_centre_index(x, centres):
    index = bisect.bisect_left(centres, x)
    for candidate in (index - 1, index):
        if 0 <= candidate < len(centres) and abs(centres[candidate] - x) <= EDGE_MATCH_TOLERANCE:
            return candidate
    return None


def neuron_edge_network_factor(
    section,
    profile,
    first_pt3d_index,
    second_pt3d_index,
    section_segments,
):
    """Reduce the NEURON segment chain across one pt3d edge to its endpoints.

    Centre-to-centre spans use actual NEURON segment.ri(). The first child
    half-edge and the final parent-endpoint half-edge use the corresponding
    actual NEURON ri() API. A partial cap ending at an arbitrary SWC pt3d node
    is integrated directly from the same linear pt3d taper.
    """
    arcs = profile["arc"]
    x_first = float(arcs[first_pt3d_index]) / float(section.L)
    x_second = float(arcs[second_pt3d_index]) / float(section.L)
    x_lo, x_hi = sorted((x_first, x_second))
    centres = section_segments["x"]
    segments = section_segments["segments"]

    left_index = _endpoint_centre_index(x_lo, centres)
    right_index = _endpoint_centre_index(x_hi, centres)
    points = [(x_lo, left_index)]
    start = bisect.bisect_right(centres, x_lo + EDGE_MATCH_TOLERANCE)
    stop = bisect.bisect_left(centres, x_hi - EDGE_MATCH_TOLERANCE)
    for index in range(start, stop):
        points.append((centres[index], index))
    points.append((x_hi, right_index))
    points.sort(key=lambda item: item[0])

    factor = 0.0
    ri_pairs = 0
    child_start_half_ri = 0
    parent_end_half_ri = 0
    direct_caps = 0
    for (x0, index0), (x1, index1) in zip(points, points[1:]):
        if x1 - x0 <= 1e-14:
            continue
        actual_ri_mohm = None
        if (
            index0 is not None
            and index1 is not None
            and index1 == index0 + 1
        ):
            actual_ri_mohm = float(segments[index1].ri())
            ri_pairs += 1
        elif (
            index0 is None
            and index1 == 0
            and abs(x0) <= EDGE_MATCH_TOLERANCE
        ):
            actual_ri_mohm = float(segments[0].ri())
            child_start_half_ri += 1
        elif (
            index0 == len(segments) - 1
            and index1 is None
            and abs(x1 - 1.0) <= EDGE_MATCH_TOLERANCE
        ):
            actual_ri_mohm = float(h.ri(1.0, sec=section))
            parent_end_half_ri += 1

        if actual_ri_mohm is not None:
            if not np.isfinite(actual_ri_mohm) or actual_ri_mohm >= 1e20:
                raise RuntimeError(
                    f"non-finite NEURON ri() in {section.name()} "
                    f"for x={x0:.12g}..{x1:.12g}"
                )
            factor += actual_ri_mohm * 1e6 / RI_OHM_M
        else:
            factor += pt3d_pair_factor(
                section, profile, first_pt3d_index, second_pt3d_index,
                x0, x1
            )
            direct_caps += 1

    direct = pt3d_pair_factor(
        section, profile, first_pt3d_index, second_pt3d_index, x_lo, x_hi
    )
    network_vs_direct_pct = (
        100.0 * abs(factor - direct) / max(abs(direct), 1e-30)
    )
    return {
        "network_factor_m_inv": factor,
        "direct_factor_m_inv": direct,
        "network_vs_direct_pct": network_vs_direct_pct,
        "ri_centre_pairs": ri_pairs,
        "ri_child_start_halves": child_start_half_ri,
        "ri_parent_end_halves": parent_end_half_ri,
        "direct_caps": direct_caps,
        "x_start": x_lo,
        "x_end": x_hi,
    }


def apply_tree_laplacian(node_count, edges, voltage):
    """Apply a tree axial Laplacian represented as (parent, child, conductance)."""
    current = np.zeros(node_count, dtype=float)
    for parent_index, child_index, conductance_s in edges:
        axial_current = conductance_s * (
            voltage[child_index] - voltage[parent_index]
        )
        current[child_index] += axial_current
        current[parent_index] -= axial_current
    return current


def run_matrix_conservation_self_checks():
    """Deterministic three-node path verifies sign and zero-sum current."""
    graph = [(0, 1, 2.0), (1, 2, 3.0)]
    voltage = np.array([0.0, 0.1, -0.2])
    current = apply_tree_laplacian(3, graph, voltage)
    expected = np.array([-0.2, 0.9, -0.7])
    if not np.allclose(current, expected, rtol=0.0, atol=1e-14):
        raise AssertionError(f"tree Laplacian sign test failed: {current} != {expected}")
    if abs(float(current.sum())) > 1e-14:
        raise AssertionError("tree Laplacian does not conserve total axial current")
    constant_current = apply_tree_laplacian(
        3, graph, np.full(3, -0.065)
    )
    if np.max(np.abs(constant_current)) > 1e-14:
        raise AssertionError("constant voltage is not in the axial Laplacian nullspace")


def write_csv(path: Path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    run_matrix_conservation_self_checks()
    morphology = SWCMorphology.from_file(DATA)
    reader, sections = reference.import_swc_with_neuron()
    configure_neuron_reference(sections)
    section_by_name = {section.name(): section for section in sections}
    profiles = {
        section.name(): audit.read_section_profile(section)
        for section in sections
    }
    segment_centres = prepare_section_segment_centres(sections)

    # Build the authoritative source-edge mapping using the same audited
    # Import3D index path and exact pt3d interval matcher as the prior audit.
    swc_edge_rows, edge_summary = audit.audit_swc_edges(
        morphology, reader, section_by_name, profiles
    )
    if edge_summary["unmapped_swc_edges"] != 0:
        raise RuntimeError(
            f"{edge_summary['unmapped_swc_edges']} active SWC edges did not map"
        )

    electrical_map = morphology.electrical_node_mapping()
    neuron_rows_by_electrical_edge = {}
    for row in swc_edge_rows:
        key = (
            electrical_map[int(row["swc_parent_id"])],
            electrical_map[int(row["swc_child_id"])],
        )
        if key in neuron_rows_by_electrical_edge:
            raise RuntimeError(f"duplicate NEURON source-edge mapping for {key}")
        neuron_rows_by_electrical_edge[key] = row

    # This is the full unresampled AMSN graph, with soma outline and wire
    # attachment vertices collapsed according to the production policy.
    amsn_tree = morphology.to_cable_tree()
    if amsn_tree.n_compartments - 1 != len(swc_edge_rows):
        raise RuntimeError(
            f"AMSN graph has {amsn_tree.n_compartments-1} edges, "
            f"but Import3D has {len(swc_edge_rows)} active SWC edges"
        )
    if set(amsn_tree.order) != {
        f"swc_{node_id}" for node_id in set(electrical_map.values())
    }:
        raise RuntimeError(
            "AMSN full-tree node set does not match the electrical SWC node set"
        )

    amsn_edges = []
    neuron_edges = []
    edge_rows = []
    paired_centre_ri_count = 0
    paired_child_start_count = 0
    paired_parent_end_count = 0
    direct_cap_count = 0
    max_neuron_network_direct_error = 0.0

    for child_index, child_name in enumerate(amsn_tree.order):
        parent_index = int(amsn_tree.parent_index[child_index])
        if parent_index < 0:
            continue
        child_id = int(child_name.removeprefix("swc_"))
        parent_id = int(amsn_tree.order[parent_index].removeprefix("swc_"))
        key = (parent_id, child_id)
        source_row = neuron_rows_by_electrical_edge.get(key)
        if source_row is None:
            raise RuntimeError(
                f"AMSN edge {parent_id}->{child_id} has no corresponding "
                "NEURON Import3D SWC edge"
            )

        # Recover the actual section/pt3d interval and collapse its fine
        # segment chain using real ri() values plus direct partial endpoint caps.
        swc_parent_id = int(source_row["swc_parent_id"])
        swc_child_id = int(source_row["swc_child_id"])
        parent_map = edge_summary["node_maps"][swc_parent_id]
        child_map = edge_summary["node_maps"][swc_child_id]
        parent_node = morphology.nodes[swc_parent_id]
        child_node = morphology.nodes[swc_child_id]
        match = audit.find_edge_pt3d_interval(
            parent_node, child_node, parent_map, child_map, profiles
        )
        if match is None:
            raise RuntimeError(
                f"failed to recover pt3d match for source edge "
                f"{swc_parent_id}->{swc_child_id}"
            )
        section_name = match["section_name"]
        section = section_by_name[section_name]
        profile = profiles[section_name]
        network = neuron_edge_network_factor(
            section,
            profile,
            match["parent_index"],
            match["child_index"],
            segment_centres[section_name],
        )

        amsn_conductance_s = float(amsn_tree.axial_g_s[child_index])
        amsn_factor = (
            1.0 / amsn_conductance_s / RI_OHM_M
        )
        amsn_resistance_ohm = 1.0 / amsn_conductance_s
        neuron_factor = network["network_factor_m_inv"]
        neuron_resistance_ohm = neuron_factor * RI_OHM_M
        neuron_conductance_s = 1.0 / neuron_resistance_ohm
        factor_difference_pct = (
            100.0 * (amsn_factor - neuron_factor)
            / max(abs(neuron_factor), 1e-30)
        )
        conductance_difference_pct = (
            100.0 * (amsn_conductance_s - neuron_conductance_s)
            / max(abs(neuron_conductance_s), 1e-30)
        )
        relative_network_direct = network["network_vs_direct_pct"]
        max_neuron_network_direct_error = max(
            max_neuron_network_direct_error, relative_network_direct
        )
        paired_centre_ri_count += network["ri_centre_pairs"]
        paired_child_start_count += network["ri_child_start_halves"]
        paired_parent_end_count += network["ri_parent_end_halves"]
        direct_cap_count += network["direct_caps"]

        amsn_edges.append((parent_index, child_index, amsn_conductance_s))
        neuron_edges.append((parent_index, child_index, neuron_conductance_s))
        edge_rows.append({
            "amsn_parent_electrical_node": parent_id,
            "amsn_child_electrical_node": child_id,
            "source_swc_parent_id": swc_parent_id,
            "source_swc_child_id": swc_child_id,
            "neuron_section": section_name,
            "amsn_axial_geometry_factor_m_inv": amsn_factor,
            "neuron_ri_network_axial_geometry_factor_m_inv": neuron_factor,
            "neuron_pt3d_direct_axial_geometry_factor_m_inv":
                network["direct_factor_m_inv"],
            "amsn_axial_resistance_ohm": amsn_resistance_ohm,
            "neuron_ri_network_axial_resistance_ohm": neuron_resistance_ohm,
            "amsn_axial_conductance_s": amsn_conductance_s,
            "neuron_ri_network_axial_conductance_s": neuron_conductance_s,
            "axial_factor_difference_pct": factor_difference_pct,
            "axial_conductance_difference_pct": conductance_difference_pct,
            "neuron_ri_vs_pt3d_direct_difference_pct": relative_network_direct,
            "neuron_ri_centre_pairs": network["ri_centre_pairs"],
            "neuron_ri_child_start_halves": network["ri_child_start_halves"],
            "neuron_ri_parent_end_halves": network["ri_parent_end_halves"],
            "direct_partial_caps": network["direct_caps"],
            "neuron_section_x_start": network["x_start"],
            "neuron_section_x_end": network["x_end"],
        })

    if len(edge_rows) != amsn_tree.n_compartments - 1:
        raise RuntimeError("not all AMSN tree edges were compared")
    if len(amsn_edges) != len(neuron_edges):
        raise RuntimeError("AMSN and NEURON graph edge counts differ")

    rel_errors = np.array([
        abs(float(row["axial_conductance_difference_pct"]))
        for row in edge_rows
    ])
    signed_errors = np.array([
        float(row["axial_conductance_difference_pct"])
        for row in edge_rows
    ])
    amsn_g = np.array([edge[2] for edge in amsn_edges])
    neuron_g = np.array([edge[2] for edge in neuron_edges])

    outdir = Path(__file__).parents[1] / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    edge_csv = outdir / "human_full_tree_axial_matrix_edges_2026-11-21.csv"
    probe_csv = outdir / "human_full_tree_axial_matrix_probes_2026-11-21.csv"
    write_csv(edge_csv, edge_rows)

    rng = np.random.default_rng(RANDOM_SEED)
    probe_rows = []
    relative_l2 = []
    max_abs_current = []
    total_current_residual = []
    for case_index in range(RANDOM_VOLTAGE_CASES):
        voltage = (
            morphology.root_id * 0.0
            + rng.normal(0.0, RANDOM_VOLTAGE_STD_V, amsn_tree.n_compartments)
            - 0.065
        )
        amsn_current = apply_tree_laplacian(
            amsn_tree.n_compartments, amsn_edges, voltage
        )
        neuron_current = apply_tree_laplacian(
            amsn_tree.n_compartments, neuron_edges, voltage
        )
        delta = amsn_current - neuron_current
        l2_error = float(
            np.linalg.norm(delta)
            / max(np.linalg.norm(neuron_current), 1e-30)
        )
        max_error = float(np.max(np.abs(delta)))
        conservation = max(
            abs(float(amsn_current.sum())),
            abs(float(neuron_current.sum())),
        )
        relative_l2.append(l2_error)
        max_abs_current.append(max_error)
        total_current_residual.append(conservation)
        probe_rows.append({
            "case_index": case_index,
            "random_seed": RANDOM_SEED,
            "voltage_std_v": RANDOM_VOLTAGE_STD_V,
            "amsn_operator_current_l2_a": float(np.linalg.norm(amsn_current)),
            "neuron_operator_current_l2_a": float(np.linalg.norm(neuron_current)),
            "operator_difference_l2_a": float(np.linalg.norm(delta)),
            "relative_operator_l2_error": l2_error,
            "max_absolute_node_current_difference_a": max_error,
            "max_abs_total_current_conservation_residual_a": conservation,
        })

    # The axial Laplacian must annihilate a constant potential exactly.
    constant_voltage = np.full(amsn_tree.n_compartments, -0.065)
    amsn_constant_current = apply_tree_laplacian(
        amsn_tree.n_compartments, amsn_edges, constant_voltage
    )
    neuron_constant_current = apply_tree_laplacian(
        amsn_tree.n_compartments, neuron_edges, constant_voltage
    )
    constant_null_max = max(
        float(np.max(np.abs(amsn_constant_current))),
        float(np.max(np.abs(neuron_constant_current))),
    )
    if constant_null_max > MATRIX_CONSERVATION_TOLERANCE_A:
        raise RuntimeError(
            f"constant-potential axial nullspace residual too large: {constant_null_max}"
        )

    write_csv(probe_csv, probe_rows)
    print(f"# NEURON={neuron.__version__}; morphology=NMO_290988")
    print(
        f"# nodes={amsn_tree.n_compartments}; edges={len(edge_rows)}; "
        f"NEURON_sections={len(sections)}; NEURON_segments={sum(s.nseg for s in sections)}"
    )
    print(
        f"# edge_conductance_abs_difference_pct_median={np.median(rel_errors):.12g}; "
        f"p95={np.percentile(rel_errors,95):.12g}; "
        f"p99={np.percentile(rel_errors,99):.12g}; "
        f"max={np.max(rel_errors):.12g}"
    )
    print(
        f"# signed_edge_conductance_difference_pct_mean={np.mean(signed_errors):.12g}; "
        f"median={np.median(signed_errors):.12g}"
    )
    print(
        f"# ri_centre_pairs={paired_centre_ri_count}; "
        f"ri_child_start_halves={paired_child_start_count}; "
        f"ri_parent_end_halves={paired_parent_end_count}; "
        f"direct_partial_caps={direct_cap_count}"
    )
    print(
        f"# max_NEURON_ri_network_vs_pt3d_direct_difference_pct="
        f"{max_neuron_network_direct_error:.12g}"
    )
    print(
        f"# random_voltage_operator_cases={RANDOM_VOLTAGE_CASES}; seed={RANDOM_SEED}; "
        f"voltage_std_mV={RANDOM_VOLTAGE_STD_V*1000:.6g}"
    )
    print(
        f"# operator_relative_L2_error_mean={np.mean(relative_l2):.12g}; "
        f"p95={np.percentile(relative_l2,95):.12g}; "
        f"max={np.max(relative_l2):.12g}"
    )
    print(
        f"# operator_max_abs_node_current_difference_A="
        f"{np.max(max_abs_current):.12g}; "
        f"max_total_current_conservation_residual_A="
        f"{np.max(total_current_residual):.12g}; "
        f"constant_voltage_nullspace_max_A={constant_null_max:.12g}"
    )
    print(f"# raw_edge_matrix_csv={edge_csv}")
    print(f"# raw_matrix_probe_csv={probe_csv}")

    if max_neuron_network_direct_error > NETWORK_DIRECT_TOLERANCE_PCT:
        raise RuntimeError(
            "NEURON ri-network reduction does not match its direct pt3d factor: "
            f"{max_neuron_network_direct_error:.12g}%"
        )


if __name__ == "__main__":
    main()
