"""Controlled passive source-placement comparison on an identical NEURON mesh.

The source section is locally refined (within NEURON's nseg limit) to place a
segment centre within 0.001 um of the exact Import3D SWC arc.

Two current-clamp conditions are then compared on this same refined mesh:
1. legacy_center: clamp at the refined-mesh centre nearest the source centre
   used by the original 0.125-um mesh; the tiny remapping offset is recorded;
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
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import neuron_cross_validation as reference
import human_fine_mesh_passive_dc_audit as fine_audit
from amsn.morphology import SWCMorphology


BASE_MAX_SEGMENT_UM = float(os.environ.get('AMSN_NEURON_MAX_SEGMENT_UM', '0.125'))
SOURCE_ALIGNMENT_TOLERANCE_UM = float(os.environ.get('AMSN_SOURCE_ALIGNMENT_TOLERANCE_UM', '0.002'))
SOURCE_ALREADY_ALIGNED_MAX_OFFSET_UM = float(os.environ.get('AMSN_SOURCE_ALREADY_ALIGNED_MAX_OFFSET_UM', '0.05'))
MAX_REFINED_NSEG = int(os.environ.get('AMSN_SOURCE_ALIGNMENT_MAX_NSEG', '32767'))
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
    morphology_path = os.environ.get("AMSN_MORPHOLOGY_PATH")
    if morphology_path:
        reference.DATA = Path(morphology_path)
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV
    reference.INJECTED_P_A = INJECTED_P_A
    reference.DT_MS = DT_MS
    reference.RUN_TO_MS = RUN_TO_MS
    reference.FINAL_MS = FINAL_MS


def choose_nested_refinement(section, target_x, legacy_x, tolerance_um):
    """Choose one NEURON mesh with distinct legacy and SWC-aligned centres.

    NEURON caps nseg at 32767. The earlier odd-multiple scheme preserved each
    original segment centre exactly, but some long Segev sections could not be
    further refined within that cap. Instead, search odd nseg values from the
    current mesh upward, map the original legacy coordinate to its nearest
    centre on the candidate mesh, and map the exact SWC coordinate separately.
    Both modes then share the same final nseg; the physical remap from the old
    legacy centre is measured and reported rather than hidden.
    """
    base_nseg = int(section.nseg)
    max_nseg = int(MAX_REFINED_NSEG)
    if not 1 <= base_nseg <= max_nseg:
        raise RuntimeError(
            f"{section.name()} base nseg {base_nseg} exceeds cap {max_nseg}"
        )

    base_legacy_index = int(round(legacy_x * base_nseg - 0.5))
    base_aligned_index = int(round(target_x * base_nseg - 0.5))
    base_legacy_index = min(base_nseg - 1, max(0, base_legacy_index))
    base_aligned_index = min(base_nseg - 1, max(0, base_aligned_index))
    base_legacy_x = (base_legacy_index + 0.5) / base_nseg
    base_aligned_x = (base_aligned_index + 0.5) / base_nseg
    base_aligned_offset_um = abs(base_aligned_x - target_x) * float(section.L)

    # If the original mesh already places the clamp at the exact SWC node
    # within tolerance, do not manufacture a different segment just to make
    # the two modes look different. Record it as already aligned.
    if (
        base_legacy_index == base_aligned_index
        and base_aligned_offset_um <= max(tolerance_um, SOURCE_ALREADY_ALIGNED_MAX_OFFSET_UM)
    ):
        return {
            "nseg": base_nseg,
            "aligned_index": base_aligned_index,
            "aligned_x": base_aligned_x,
            "aligned_offset_um": base_aligned_offset_um,
            "legacy_index": base_legacy_index,
            "legacy_x": base_legacy_x,
            "legacy_offset_um": base_aligned_offset_um,
            "legacy_remap_offset_um": abs(base_legacy_x - legacy_x)
                * float(section.L),
            "base_nseg": base_nseg,
            "multiplier": 1.0,
            "already_aligned": True,
        }

    first_nseg = base_nseg if base_nseg % 2 else base_nseg + 1
    best = None
    for candidate_nseg in range(first_nseg, max_nseg + 1, 2):
        legacy_index = int(round(legacy_x * candidate_nseg - 0.5))
        aligned_index = int(round(target_x * candidate_nseg - 0.5))
        legacy_index = min(candidate_nseg - 1, max(0, legacy_index))
        aligned_index = min(candidate_nseg - 1, max(0, aligned_index))
        if legacy_index == aligned_index:
            continue

        legacy_x_refined = (legacy_index + 0.5) / candidate_nseg
        aligned_x = (aligned_index + 0.5) / candidate_nseg
        legacy_remap_um = abs(legacy_x_refined - legacy_x) * float(section.L)
        legacy_offset_um = abs(legacy_x_refined - target_x) * float(section.L)
        aligned_offset_um = abs(aligned_x - target_x) * float(section.L)
        if aligned_offset_um > tolerance_um:
            continue

        best = {
            "nseg": candidate_nseg,
            "aligned_index": aligned_index,
            "aligned_x": aligned_x,
            "aligned_offset_um": aligned_offset_um,
            "legacy_index": legacy_index,
            "legacy_x": legacy_x_refined,
            "legacy_offset_um": legacy_offset_um,
            "legacy_remap_offset_um": legacy_remap_um,
            "base_nseg": base_nseg,
            "multiplier": candidate_nseg / base_nseg,
            "already_aligned": False,
        }
        break

    if best is None:
        base_legacy_index = int(round(legacy_x * base_nseg - 0.5))
        base_aligned_index = int(round(target_x * base_nseg - 0.5))
        best_possible_offset = float("inf")
        for candidate_nseg in range(first_nseg, max_nseg + 1, 2):
            aligned_index = int(round(target_x * candidate_nseg - 0.5))
            aligned_index = min(candidate_nseg - 1, max(0, aligned_index))
            aligned_x = (aligned_index + 0.5) / candidate_nseg
            best_possible_offset = min(
                best_possible_offset,
                abs(aligned_x - target_x) * float(section.L),
            )
        raise RuntimeError(
            f"could not create distinct legacy/aligned centres in {section.name()} "
            f"within {tolerance_um:g} um under nseg cap {max_nseg}; "
            f"base_nseg={base_nseg}; legacy_index={base_legacy_index}; "
            f"base_aligned_index={base_aligned_index}; "
            f"best_aligned_offset_um={best_possible_offset:.9g}"
        )
    return best

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

    # Refine the two dendritic source sections. Both source modes are mapped
    # onto the same final mesh; the legacy coordinate remap is recorded.
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
    morphology_label = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
    print(
        f"# NEURON={neuron.__version__}; morphology={morphology_label}; "
        f"path={reference.DATA}"
    )
    print(
        f"# base_mesh_max_segment_um={BASE_MAX_SEGMENT_UM}; "
        f"source_alignment_tolerance_um={SOURCE_ALIGNMENT_TOLERANCE_UM}; "
        f"already_aligned_max_offset_um={SOURCE_ALREADY_ALIGNED_MAX_OFFSET_UM}"
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
            f"(refinement_ratio={refinement['multiplier']:.6g}); "
            f"legacy_source_offset_um={refinement['legacy_offset_um']:.12g}; "
            f"legacy_mesh_remap_um={refinement['legacy_remap_offset_um']:.12g}; "
            f"aligned_source_offset_um={refinement['aligned_offset_um']:.12g}; "
            f"legacy_index={refinement['legacy_index']}; "
            f"aligned_index={refinement['aligned_index']}; "
            f"already_aligned={refinement['already_aligned']}"
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
    electrical_map = morphology.electrical_node_mapping()
    fine_mapping = {
        node_id: f"swc_{electrical_id}"
        for node_id, electrical_id in electrical_map.items()
    }
    for source_name, source_id in injections:
        if source_name == "soma":
            continue
        amsn_input_mohm, _ = reference.solve_amsn(
            fine_tree,
            fine_mapping,
            source_id,
            [probe_id for _, probe_id in probes],
        )
        amsn_source_delta = amsn_input_mohm * INJECTED_P_A / 1000.0
        for mode in ("legacy", "aligned"):
            source_site = source_sites[source_id][mode]
            neuron_voltage, residual, clamp = fine_audit.solve_neuron_passive(
                source_site, sites, all_clamps
            )
            all_clamps.append(clamp)
            maximum_residual = max(maximum_residual, residual)

            source_delta = neuron_voltage[(source_id, False)] - ELEAK_MV
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
