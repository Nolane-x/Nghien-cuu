"""Fine-mesh full-tree passive DC cross-validation and probe interpolation.

This experiment revisits the existing whole-morphology passive DC comparison,
but uses a configurable fine NEURON reference mesh (default 0.5 um) instead of 5 um. It compares:
- AMSN's exact, unresampled 8,893-node electrical tree;
- the existing electrotonically reduced AMSN mesh;
- NEURON 9.0.2 with AMSN_NEURON_MAX_SEGMENT_UM maximum segment length.

For each SWC probe, NEURON voltage is read both at the nearest segment centre
and by linear interpolation between adjacent segment-centre voltages at the
exact Import3D section arc coordinate. The current clamp remains on the
nearest segment: interpolation is diagnostic readout only, not a change in
stimulus placement.

The same Ri/Rm/Cm/Eleak and current are used throughout. No fitting or
parameter tuning is performed. This is passive DC numerical validation for
one partial morphology, not a biological fit.
"""
from __future__ import annotations

import csv
import os
from math import ceil
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.5"))
if not np.isfinite(NEURON_MAX_SEGMENT_UM) or NEURON_MAX_SEGMENT_UM <= 0:
    raise ValueError("AMSN_NEURON_MAX_SEGMENT_UM must be finite and positive")
DT_MS = 0.025
RUN_TO_MS = 200.0
FINAL_MS = 250.0
INJECTED_P_A = 10.0
RM_OHM_M2 = 1.0
RI_OHM_M = 0.7
CM_F_M2 = 0.01
ELEAK_MV = -65.0
STEADY_RESIDUAL_TOLERANCE_MV = 1e-6
AREA_DIFFERENCE_SANITY_TOLERANCE_PCT = 1e-3


def path_distances_um(morphology):
    return reference.path_distances_um(morphology)


def build_sites(morphology, reader, sections):
    distances = path_distances_um(morphology)
    injections = [
        ("soma", morphology.root_id),
        ("basal_q75", reference.quantile_node(morphology, distances, 3, 0.75)),
        ("apical_q75", reference.quantile_node(morphology, distances, 4, 0.75)),
    ]
    probes = [
        ("soma", morphology.root_id),
        ("basal_q50", reference.quantile_node(morphology, distances, 3, 0.50)),
        ("basal_q90", reference.quantile_node(morphology, distances, 3, 0.90)),
        ("apical_q50", reference.quantile_node(morphology, distances, 4, 0.50)),
        ("apical_q90", reference.quantile_node(morphology, distances, 4, 0.90)),
    ]
    section_by_name = {section.name(): section for section in sections}
    site_ids = sorted({node_id for _, node_id in injections + probes})
    mapped = {}
    for node_id in site_ids:
        nearest, total, geometry, centre, section_name, normalized = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        section = section_by_name[section_name]
        segments = list(section)
        xs = np.array([float(segment.x) for segment in segments])
        insertion = int(np.searchsorted(xs, normalized))
        lower = insertion - 1
        upper = insertion
        if lower < 0 or upper >= len(segments):
            raise RuntimeError(
                f"SWC node {node_id} at x={normalized:.9f} is outside "
                "the segment-centre interpolation interval"
            )
        x0, x1 = float(xs[lower]), float(xs[upper])
        if not (x0 <= normalized <= x1) or x1 <= x0:
            raise RuntimeError(
                f"invalid interpolation bracket for SWC node {node_id}: "
                f"{x0} <= {normalized} <= {x1}"
            )
        weight = (normalized - x0) / (x1 - x0)
        mapped[node_id] = {
            "nearest_segment": nearest,
            "section": section,
            "section_name": section_name,
            "normalized_x": float(normalized),
            "lower_segment": segments[lower],
            "upper_segment": segments[upper],
            "lower_x": x0,
            "upper_x": x1,
            "interpolation_upper_weight": float(weight),
            "total_mapping_offset_um": float(total),
            "geometry_offset_um": float(geometry),
            "nearest_centre_offset_um": float(centre),
        }
    return injections, probes, mapped



def align_source_sections(morphology, reader, sections, injections):
    """Refine only dendritic source sections so an IClamp segment centre is
    within a requested distance of the exact Import3D SWC arc.
    """
    tolerance_um = float(os.environ.get(
        "AMSN_SOURCE_ALIGNMENT_TOLERANCE_UM", "0"
    ))
    max_nseg = int(os.environ.get(
        "AMSN_SOURCE_ALIGNMENT_MAX_NSEG", "50001"
    ))
    if not np.isfinite(tolerance_um) or tolerance_um < 0:
        raise ValueError("source alignment tolerance must be finite and nonnegative")
    if max_nseg < 1:
        raise ValueError("source alignment maximum nseg must be positive")
    if tolerance_um == 0:
        return [], injections, None, None, None

    _, _, initial_sites = build_sites(morphology, reader, sections)
    changes = []
    for source_name, node_id in injections:
        if source_name == "soma":
            continue
        site = initial_sites[node_id]
        section = site["section"]
        target_x = float(site["normalized_x"])
        current_nseg = int(section.nseg)
        start_nseg = current_nseg if current_nseg % 2 else current_nseg + 1
        if start_nseg > max_nseg:
            raise RuntimeError(
                f"source section {section.name()} already has {current_nseg} "
                f"segments, above alignment maximum {max_nseg}"
            )

        candidates = np.arange(start_nseg, max_nseg + 1, 2, dtype=np.int64)
        nearest_index = np.rint(candidates * target_x - 0.5).astype(np.int64)
        nearest_index = np.clip(nearest_index, 0, candidates - 1)
        nearest_centre_x = (nearest_index + 0.5) / candidates
        offsets_um = np.abs(nearest_centre_x - target_x) * float(section.L)
        within_tolerance = np.flatnonzero(offsets_um <= tolerance_um)
        if not within_tolerance.size:
            best = int(np.argmin(offsets_um))
            raise RuntimeError(
                f"could not align {source_name} source within {tolerance_um:g} um; "
                f"best offset={offsets_um[best]:.12g} um at nseg={candidates[best]}"
            )
        chosen = int(within_tolerance[0])
        chosen_nseg = int(candidates[chosen])
        chosen_offset_um = float(offsets_um[chosen])

        section.nseg = chosen_nseg
        for segment in section:
            _ = segment.area()
        changes.append({
            "source": source_name,
            "swc_node_id": int(node_id),
            "section": section.name(),
            "target_x": target_x,
            "previous_nseg": current_nseg,
            "aligned_nseg": chosen_nseg,
            "source_centre_offset_um": chosen_offset_um,
            "tolerance_um": tolerance_um,
        })

    h.define_shape()
    aligned_injections, aligned_probes, aligned_sites = build_sites(
        morphology, reader, sections
    )
    return changes, aligned_injections, aligned_probes, aligned_sites, tolerance_um


def read_probe_voltage(site, interpolated: bool):

    if not interpolated:
        return float(site["nearest_segment"].v)
    lower = float(site["lower_segment"].v)
    upper = float(site["upper_segment"].v)
    weight = site["interpolation_upper_weight"]
    return lower * (1.0 - weight) + upper * weight


def solve_neuron_passive(source_site, sites, previous_clamps):
    for previous in previous_clamps:
        previous.amp = 0.0
    clamp = h.IClamp(source_site["nearest_segment"])
    clamp.delay = 0.0
    clamp.dur = 500.0
    clamp.amp = INJECTED_P_A / 1000.0

    h.dt = DT_MS
    h.steps_per_ms = 1.0 / DT_MS
    h.CVode().active(0)
    h.finitialize(ELEAK_MV)
    h.continuerun(RUN_TO_MS)
    early = {
        (node_id, mode): read_probe_voltage(site, mode)
        for node_id, site in sites.items()
        for mode in (False, True)
    }
    h.continuerun(FINAL_MS)
    final = {
        (node_id, mode): read_probe_voltage(site, mode)
        for node_id, site in sites.items()
        for mode in (False, True)
    }
    residual = max(
        abs(final[key] - early[key])
        for key in final
    )
    return final, residual, clamp


def solve_amsn_all(morphology, injections, probes):
    fine_tree = morphology.to_cable_tree()
    electrical_map = morphology.electrical_node_mapping()
    fine_mapping = {
        node_id: f"swc_{electrical_id}"
        for node_id, electrical_id in electrical_map.items()
    }
    protected = {
        node_id for _, node_id in injections + probes
    }
    sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=100.0,
        max_electrotonic_length=0.1,
        reference_frequency_hz=100.0,
        preserve_node_ids=protected,
    )
    fine_results = {}
    sectioned_results = {}
    for source_name, source_id in injections:
        _, fine_rows = reference.solve_amsn(
            fine_tree, fine_mapping, source_id,
            [node_id for _, node_id in probes]
        )
        _, sectioned_rows = reference.solve_amsn(
            sectioned.tree, sectioned.swc_node_to_compartment, source_id,
            [node_id for _, node_id in probes]
        )
        fine_results[source_id] = fine_rows
        sectioned_results[source_id] = sectioned_rows
    return fine_tree, sectioned, fine_results, sectioned_results


def main():
    # Reuse the established Import3D model and parameter conversion; the
    # mesh cap is supplied by AMSN_NEURON_MAX_SEGMENT_UM (default 0.5 um).
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV
    reference.INJECTED_P_A = INJECTED_P_A
    reference.DT_MS = DT_MS
    reference.RUN_TO_MS = RUN_TO_MS
    reference.FINAL_MS = FINAL_MS

    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = build_sites(morphology, reader, sections)
    (
        alignment_changes,
        injections,
        probes,
        aligned_sites,
        alignment_tolerance_um,
    ) = align_source_sections(morphology, reader, sections, injections)
    if aligned_sites is not None:
        sites = aligned_sites
    fine_tree, sectioned, fine_results, sectioned_results = solve_amsn_all(
        morphology, injections, probes
    )

    neuron_area_um2 = sum(
        float(segment.area())
        for section in sections
        for segment in section
    )
    amsn_area_um2 = float(fine_tree.area_m2.sum() * 1e12)
    area_difference_pct = (
        100.0 * (neuron_area_um2 - amsn_area_um2) / amsn_area_um2
    )
    if abs(area_difference_pct) > AREA_DIFFERENCE_SANITY_TOLERANCE_PCT:
        raise RuntimeError(
            "NEURON/AMSN normalized passive membrane area discrepancy "
            f"{area_difference_pct:.9g}% exceeds the audit sanity gate"
        )

    segment_count = sum(section.nseg for section in sections)
    print(f"# NEURON={neuron.__version__}; morphology=NMO_290988")
    print(
        f"# passive parameters: Ri={RI_OHM_M:g} ohm*m; "
        f"Rm={RM_OHM_M2:g} ohm*m^2; Cm={CM_F_M2:g} F/m^2; "
        f"Eleak={ELEAK_MV:g} mV"
    )
    print(
        f"# NEURON sections={len(sections)}; segments={segment_count}; "
        f"max_segment_length_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(
        f"# source_alignment_tolerance_um="
        f"{alignment_tolerance_um if alignment_tolerance_um is not None else 0:g}"
    )
    for change in alignment_changes:
        print(
            f"# source_alignment={change['source']}; swc_id={change['swc_node_id']}; "
            f"section={change['section']}; target_x={change['target_x']:.12g}; "
            f"nseg={change['previous_nseg']}->{change['aligned_nseg']}; "
            f"centre_offset_um={change['source_centre_offset_um']:.12g}"
        )
    print(
        f"# AMSN fine compartments={fine_tree.n_compartments}; "
        f"AMSN sectioned compartments={sectioned.tree.n_compartments}"
    )
    print(
        f"# NEURON_total_segment_area_um2={neuron_area_um2:.12f}; "
        f"AMSN_normalized_electrical_area_um2={amsn_area_um2:.12f}; "
        f"relative_difference_pct={area_difference_pct:.12g}"
    )
    for name, node_id in injections + probes:
        site = sites[node_id]
        print(
            f"# site={name}; swc_id={node_id}; section={site['section_name']}; "
            f"x={site['normalized_x']:.9f}; "
            f"nearest_centre_offset_um={site['nearest_centre_offset_um']:.9f}; "
            f"geometry_offset_um={site['geometry_offset_um']:.9g}; "
            f"interpolation_bracket={site['lower_x']:.9f}..{site['upper_x']:.9f}"
        )

    print(
        "source,source_swc_id,probe,probe_swc_id,"
        "neuron_source_nearest_delta_mV,"
        "amsn_fine_source_delta_mV,"
        "amsn_sectioned_source_delta_mV,"
        "neuron_probe_nearest_delta_mV,"
        "neuron_probe_interpolated_delta_mV,"
        "amsn_fine_probe_delta_mV,"
        "amsn_sectioned_probe_delta_mV,"
        "neuron_nearest_transfer_ratio,"
        "neuron_interpolated_transfer_ratio,"
        "amsn_fine_transfer_ratio,"
        "amsn_sectioned_transfer_ratio,"
        "nearest_vs_fine_ratio_error_pct,"
        "interpolated_vs_fine_ratio_error_pct,"
        "sectioned_vs_fine_ratio_error_pct,"
        "probe_nearest_centre_offset_um,"
        "probe_geometry_offset_um,"
        "source_nearest_centre_offset_um,"
        "source_geometry_offset_um,"
        "source_section_nseg,"
        "steady_residual_mV"
    )

    previous_clamps = []
    all_residuals = []
    for source_name, source_id in injections:
        source_site = sites[source_id]
        neuron_voltage, residual, clamp = solve_neuron_passive(
            source_site, sites, previous_clamps
        )
        previous_clamps.append(clamp)
        all_residuals.append(residual)

        source_nearest = neuron_voltage[(source_id, False)] - ELEAK_MV
        fine_input, fine_source_rows = reference.solve_amsn(
            fine_tree,
            {
                node_id: f"swc_{electrical_id}"
                for node_id, electrical_id in morphology.electrical_node_mapping().items()
            },
            source_id,
            [probe_id for _, probe_id in probes],
        )
        sectioned_input, sectioned_source_rows = reference.solve_amsn(
            sectioned.tree,
            sectioned.swc_node_to_compartment,
            source_id,
            [probe_id for _, probe_id in probes],
        )
        fine_source_delta = (
            fine_results[source_id][source_id][0]
            if source_id in fine_results[source_id]
            else fine_input * INJECTED_P_A / 1e3
        )
        sectioned_source_delta = sectioned_input * INJECTED_P_A / 1e3
        source_nearest_ratio_denominator = max(abs(source_nearest), 1e-30)

        for probe_name, probe_id in probes:
            site = sites[probe_id]
            neuron_nearest_delta = neuron_voltage[(probe_id, False)] - ELEAK_MV
            neuron_interp_delta = neuron_voltage[(probe_id, True)] - ELEAK_MV
            fine_delta, fine_transfer, fine_ratio = fine_results[source_id][probe_id]
            sectioned_delta, sectioned_transfer, sectioned_ratio = (
                sectioned_results[source_id][probe_id]
            )
            neuron_nearest_ratio = neuron_nearest_delta / source_nearest_ratio_denominator
            neuron_interp_ratio = neuron_interp_delta / source_nearest_ratio_denominator
            nearest_error = 100.0 * abs(
                neuron_nearest_ratio - fine_ratio
            ) / max(abs(fine_ratio), 1e-30)
            interp_error = 100.0 * abs(
                neuron_interp_ratio - fine_ratio
            ) / max(abs(fine_ratio), 1e-30)
            sectioned_error = 100.0 * abs(
                sectioned_ratio - fine_ratio
            ) / max(abs(fine_ratio), 1e-30)

            print(
                f"{source_name},{source_id},{probe_name},{probe_id},"
                f"{source_nearest:.12g},{fine_source_delta:.12g},"
                f"{sectioned_source_delta:.12g},"
                f"{neuron_nearest_delta:.12g},{neuron_interp_delta:.12g},"
                f"{fine_delta:.12g},{sectioned_delta:.12g},"
                f"{neuron_nearest_ratio:.12g},{neuron_interp_ratio:.12g},"
                f"{fine_ratio:.12g},{sectioned_ratio:.12g},"
                f"{nearest_error:.12g},{interp_error:.12g},{sectioned_error:.12g},"
                f"{site['nearest_centre_offset_um']:.9g},"
                f"{site['geometry_offset_um']:.9g},"
                f"{source_site['nearest_centre_offset_um']:.9g},"
                f"{source_site['geometry_offset_um']:.9g},"
                f"{source_site['section'].nseg},{residual:.9g}"
            )

    max_residual = max(all_residuals, default=0.0)
    print(f"# maximum_NEURON_steady_residual_mV={max_residual:.12g}")
    if max_residual > STEADY_RESIDUAL_TOLERANCE_MV:
        raise RuntimeError(
            f"NEURON passive DC did not reach steady state: {max_residual:.9g} mV"
        )


if __name__ == "__main__":
    main()
