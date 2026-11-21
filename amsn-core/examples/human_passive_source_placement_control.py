"""Controlled passive source-placement comparison on an identical NEURON mesh.

The source section is locally refined to a mesh that preserves every original
segment centre (the refined nseg is an odd multiple of the base nseg) and also
places a segment centre within 0.001 um of the exact Import3D SWC arc.

Two current-clamp conditions are then compared on this same refined mesh:
1. legacy_center: clamp at the original 0.125-um mesh's nearest segment centre,
   which is preserved exactly as a node in the nested refined mesh;
2. swc_aligned: clamp at the refined mesh segment centre nearest the exact SWC
   electrical node.

The morphology, section nseg, cable geometry, passive parameters, dt, current,
and probe discretization are identical between modes. Only the IClamp segment
location changes. Probe voltages are read at nearest-centre and interpolated
exact-SWC-arc locations.

This is numerical source-location sensitivity, not biological validation.
"""
from __future__ import annotations

import csv
from math import ceil
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import neuron_cross_validation as reference
import human_fine_mesh_passive_dc_audit as fine_audit
from amsn.morphology import SWCMorphology


BASE_MAX_SEGMENT_UM = 0.125
SOURCE_ALIGNMENT_TOLERANCE_UM = 0.001
MAX_REFINED_NSEG = 200001
RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
INJECTED_P_A = 10.0
DT_MS = 0.025
RUN_TO_MS = 200.0
FINAL_MS = 250.0
STEADY_RESIDUAL_TOLERANCE_MV = 1e-6
AREA_DIFFERENCE_SANITY_TOLERANCE_PCT = 1e-3


def configure_reference_parameters():
    reference.MAX_NEURON_SEGMENT_UM = BASE_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV
    reference.INJECTED_P_A = INJECTED_P_A
    reference.DT_MS = DT_MS
    reference.RUN_TO_MS = RUN_TO_MS
    reference.FINAL_MS = FINAL_MS


def choose_nested_refinement(section, target_x, legacy_x, tolerance_um):
    """Choose the smallest odd multiple of nseg meeting the alignment target.

    If n_new = n_old * odd_multiplier, every old segment centre remains an
    exact centre in the refined mesh, providing a same-mesh legacy control.
    """
    base_nseg = int(section.nseg)
    if base_nseg % 2 == 0:
        raise RuntimeError(f"{section.name()} nseg must be odd")
    maximum_multiplier = MAX_REFINED_NSEG // base_nseg
    if maximum_multiplier % 2 == 0:
        maximum_multiplier -= 1
    for multiplier in range(1, maximum_multiplier + 1, 2):
        candidate_nseg = base_nseg * multiplier
        index = int(round(target_x * candidate_nseg - 0.5))
        index = min(candidate_nseg - 1, max(0, index))
        centre_x = (index + 0.5) / candidate_nseg
        offset_um = abs(centre_x - target_x) * float(section.L)
        if offset_um <= tolerance_um:
            legacy_index = int(round(legacy_x * candidate_nseg - 0.5))
            legacy_index = min(
                candidate_nseg - 1, max(0, legacy_index)
            )
            legacy_centre_x = (legacy_index + 0.5) / candidate_nseg
            if abs(legacy_centre_x - legacy_x) > 1e-12:
                raise RuntimeError(
                    f"old centre x={legacy_x:.15g} not retained by "
                    f"nested nseg={candidate_nseg} in {section.name()}"
                )
            return {
                "nseg": candidate_nseg,
                "aligned_index": index,
                "aligned_x": centre_x,
                "aligned_offset_um": offset_um,
                "legacy_index": legacy_index,
                "legacy_x": legacy_centre_x,
                "legacy_offset_um": abs(legacy_centre_x - target_x)
                    * float(section.L),
                "base_nseg": base_nseg,
                "multiplier": multiplier,
            }
    raise RuntimeError(
        f"could not align {section.name()} source within {tolerance_um:g} um "
        f"using odd nseg multiples up to {MAX_REFINED_NSEG}"
    )


def main():
    configure_reference_parameters()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, initial_sites = fine_audit.build_sites(
        morphology, reader, sections
    )

    # Capture original 0.125-um nearest-centre source locations.
    source_geometry = {}
    for source_name, source_id in injections:
        if source_name == "soma":
            continue
        site = initial_sites[source_id]
        section = site["section"]
        source_geometry[source_id] = {
            "source_name": source_name,
            "section": section,
            "target_x": float(site["normalized_x"]),
            "legacy_x": float(site["nearest_segment"].x),
            "base_nseg": int(section.nseg),
            "geometry_offset_um": float(site["geometry_offset_um"]),
        }

    # Refine the two dendritic source sections. Odd multiples preserve all
    # original segment centres exactly while adding a centre near the SWC x.
    refinements = {}
    for source_id, info in source_geometry.items():
        refinements[source_id] = choose_nested_refinement(
            info["section"],
            info["target_x"],
            info["legacy_x"],
            SOURCE_ALIGNMENT_TOLERANCE_UM,
        )
        info["section"].nseg = refinements[source_id]["nseg"]
        for segment in info["section"]:
            _ = segment.area()
    h.define_shape()

    # Re-map probes on the shared, refined mesh.
    injections, probes, sites = fine_audit.build_sites(
        morphology, reader, sections
    )
    source_sites = {}
    for source_name, source_id in injections:
        if source_name == "soma":
            source_sites[source_id] = {
                "legacy": dict(sites[source_id]),
                "aligned": dict(sites[source_id]),
                "legacy_offset_um": 0.0,
                "aligned_offset_um": 0.0,
                "section_nseg": int(sites[source_id]["section"].nseg),
            }
            continue

        info = source_geometry[source_id]
        refinement = refinements[source_id]
        section = info["section"]
        segments = list(section)
        aligned = dict(sites[source_id])
        legacy = dict(sites[source_id])
        legacy["nearest_segment"] = segments[refinement["legacy_index"]]
        aligned["nearest_segment"] = segments[refinement["aligned_index"]]
        legacy["nearest_centre_offset_um"] = refinement["legacy_offset_um"]
        aligned["nearest_centre_offset_um"] = refinement["aligned_offset_um"]
        legacy["total_mapping_offset_um"] = float(np.hypot(
            info["geometry_offset_um"], refinement["legacy_offset_um"]
        ))
        aligned["total_mapping_offset_um"] = float(np.hypot(
            info["geometry_offset_um"], refinement["aligned_offset_um"]
        ))
        source_sites[source_id] = {
            "legacy": legacy,
            "aligned": aligned,
            "legacy_offset_um": refinement["legacy_offset_um"],
            "aligned_offset_um": refinement["aligned_offset_um"],
            "section_nseg": int(section.nseg),
        }

    fine_tree, sectioned, fine_results, sectioned_results = (
        fine_audit.solve_amsn_all(morphology, injections, probes)
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
            f"NEURON/AMSN area discrepancy {area_difference_pct:.9g}%"
        )

    total_segments = sum(section.nseg for section in sections)
    print(f"# NEURON={neuron.__version__}; morphology=NMO_290988")
    print(
        f"# base_mesh_max_segment_um={BASE_MAX_SEGMENT_UM}; "
        f"source_alignment_tolerance_um={SOURCE_ALIGNMENT_TOLERANCE_UM}"
    )
    print(
        f"# NEURON_sections={len(sections)}; NEURON_segments={total_segments}; "
        f"AMSN_full_nodes={fine_tree.n_compartments}; "
        f"AMSN_sectioned_nodes={sectioned.tree.n_compartments}"
    )
    print(
        f"# passive_Ri_ohm_m={RI_OHM_M}; Rm_ohm_m2={RM_OHM_M2}; "
        f"Cm_F_m2={CM_F_M2}; Eleak_mV={ELEAK_MV}; "
        f"I_pA={INJECTED_P_A}; dt_ms={DT_MS}"
    )
    print(
        f"# NEURON_total_segment_area_um2={neuron_area_um2:.12f}; "
        f"AMSN_area_um2={amsn_area_um2:.12f}; "
        f"area_difference_pct={area_difference_pct:.12g}"
    )
    for source_id, info in source_geometry.items():
        refinement = refinements[source_id]
        print(
            f"# source_refinement={info['source_name']}; swc_id={source_id}; "
            f"section={info['section'].name()}; "
            f"nseg={refinement['base_nseg']}->{refinement['nseg']} "
            f"(odd_multiple={refinement['multiplier']}); "
            f"legacy_offset_um={refinement['legacy_offset_um']:.12g}; "
            f"aligned_offset_um={refinement['aligned_offset_um']:.12g}"
        )

    print(
        "source,source_swc_id,mode,probe,probe_swc_id,"
        "source_delta_mV,amsn_fine_source_delta_mV,source_input_error_pct,"
        "neuron_probe_nearest_delta_mV,neuron_probe_interpolated_delta_mV,"
        "amsn_fine_probe_delta_mV,neuron_nearest_transfer_ratio,"
        "neuron_interpolated_transfer_ratio,amsn_fine_transfer_ratio,"
        "nearest_ratio_error_pct,interpolated_ratio_error_pct,"
        "source_centre_offset_um,probe_centre_offset_um,"
        "source_section_nseg,steady_residual_mV"
    )

    all_clamps = []
    maximum_residual = 0.0
    for source_name, source_id in injections:
        for mode in ("legacy", "aligned"):
            source_site = source_sites[source_id][mode]
            neuron_voltage, residual, clamp = fine_audit.solve_neuron_passive(
                source_site, sites, all_clamps
            )
            all_clamps.append(clamp)
            maximum_residual = max(maximum_residual, residual)

            source_delta = neuron_voltage[(source_id, False)] - ELEAK_MV
            amsn_source_delta = fine_results[source_id][source_id][0]
            source_error_pct = 100.0 * abs(
                source_delta - amsn_source_delta
            ) / max(abs(amsn_source_delta), 1e-30)

            for probe_name, probe_id in probes:
                site = sites[probe_id]
                nearest_delta = (
                    neuron_voltage[(probe_id, False)] - ELEAK_MV
                )
                interpolated_delta = (
                    neuron_voltage[(probe_id, True)] - ELEAK_MV
                )
                amsn_probe_delta, _, amsn_ratio = (
                    fine_results[source_id][probe_id]
                )
                nearest_ratio = nearest_delta / max(abs(source_delta), 1e-30)
                interpolated_ratio = (
                    interpolated_delta / max(abs(source_delta), 1e-30)
                )
                nearest_error = 100.0 * abs(
                    nearest_ratio - amsn_ratio
                ) / max(abs(amsn_ratio), 1e-30)
                interpolated_error = 100.0 * abs(
                    interpolated_ratio - amsn_ratio
                ) / max(abs(amsn_ratio), 1e-30)
                print(
                    f"{source_name},{source_id},{mode},{probe_name},{probe_id},"
                    f"{source_delta:.12g},{amsn_source_delta:.12g},"
                    f"{source_error_pct:.12g},{nearest_delta:.12g},"
                    f"{interpolated_delta:.12g},{amsn_probe_delta:.12g},"
                    f"{nearest_ratio:.12g},{interpolated_ratio:.12g},"
                    f"{amsn_ratio:.12g},{nearest_error:.12g},"
                    f"{interpolated_error:.12g},"
                    f"{source_site['nearest_centre_offset_um']:.9g},"
                    f"{site['nearest_centre_offset_um']:.9g},"
                    f"{source_site['section'].nseg},{residual:.9g}"
                )

    print(f"# maximum_NEURON_steady_residual_mV={maximum_residual:.12g}")
    if maximum_residual > STEADY_RESIDUAL_TOLERANCE_MV:
        raise RuntimeError(
            f"passive DC not steady: {maximum_residual:.9g} mV"
        )


if __name__ == "__main__":
    main()
