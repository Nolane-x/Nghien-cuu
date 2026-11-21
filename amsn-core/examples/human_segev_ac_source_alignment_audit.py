"""Same-mesh AC impedance sensitivity to NEURON source-reference placement.

For Segev human L2/3 SWCs, compare the legacy segment-centre source coordinate
(from the 0.125 um base mesh) with the nearest SWC-aligned segment centre after
local refinement. Both reference locations use one identical final NEURON mesh;
only Impedance.loc() changes. This isolates AC source-reference placement from
morphology, membrane parameters, probes, and mesh changes.

Rows with pre_aligned or unresolved_nseg_cap status are retained but excluded
from sensitivity summaries: those rows do not contain two distinct source sites.
This is a numerical-method audit, not biological validation.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import human_fine_mesh_passive_dc_audit as fine_audit
import human_passive_source_placement_control as placement
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
OUTPUT = Path(os.environ.get(
    "AMSN_AC_SOURCE_OUTPUT", "human-segev-ac-source-alignment.csv"
))
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
ELEAK_MV = -65.0


def complex_from_measurement(magnitude_mohm: float, phase_rad: float) -> complex:
    if not np.isfinite(magnitude_mohm) or magnitude_mohm < 0.0:
        raise RuntimeError(f"invalid impedance magnitude: {magnitude_mohm}")
    if not np.isfinite(phase_rad):
        raise RuntimeError(f"invalid impedance phase: {phase_rad}")
    return magnitude_mohm * 1e6 * np.exp(1j * phase_rad)


def relative_complex_delta_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(value - baseline) / max(abs(baseline), 1e-30)


def relative_magnitude_delta_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(abs(value) - abs(baseline)) / max(abs(baseline), 1e-30)


def phase_delta_deg(value: complex, baseline: complex) -> float:
    if abs(value) == 0.0 or abs(baseline) == 0.0:
        return float("nan")
    return float(np.angle(value / baseline, deg=True))


def impedance_at(impedance, x: float, section, probe=None) -> complex:
    if probe is None:
        magnitude = float(impedance.input(x, sec=section))
        phase = float(impedance.input_phase(x, sec=section))
    else:
        magnitude = float(impedance.transfer(probe["x"], sec=probe["section"]))
        phase = float(impedance.transfer_phase(probe["x"], sec=probe["section"]))
    return complex_from_measurement(magnitude, phase)


def main() -> None:
    # Reuse the exact importer, passive constants, source selection and
    # alignment classifier already exercised by the DC placement control.
    placement.configure_reference_parameters()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, initial_sites = fine_audit.build_sites(
        morphology, reader, sections
    )

    source_geometry = {}
    for source_name, source_id in injections:
        if source_name == "soma":
            continue
        site = initial_sites[source_id]
        section = site["section"]
        source_geometry[source_id] = {
            "source_name": source_name,
            "source_id": source_id,
            "section": section,
            "target_x": float(site["normalized_x"]),
            "legacy_x": float(site["nearest_segment"].x),
            "geometry_offset_um": float(site["geometry_offset_um"]),
        }

    if not source_geometry:
        raise RuntimeError("no non-somatic source sites were selected")

    refinements = {}
    for source_id, info in source_geometry.items():
        refinement = placement.choose_nested_refinement(
            info["section"],
            info["target_x"],
            info["legacy_x"],
            placement.SOURCE_ALIGNMENT_TOLERANCE_UM,
        )
        refinements[source_id] = refinement
        info["section"].nseg = int(refinement["nseg"])
        for segment in info["section"]:
            _ = segment.area()
    h.define_shape()

    # Re-resolve probes after all local section refinements. Their physical
    # SWC coordinates stay fixed across legacy and aligned source conditions.
    injections, probes, sites = fine_audit.build_sites(
        morphology, reader, sections
    )
    probe_sites = [
        {
            "name": name,
            "node_id": node_id,
            "section": sites[node_id]["section"],
            "x": float(sites[node_id]["normalized_x"]),
        }
        for name, node_id in probes
    ]

    source_modes = {}
    for source_name, source_id in injections:
        if source_name == "soma":
            continue
        info = source_geometry[source_id]
        refinement = refinements[source_id]
        section = info["section"]
        segments = list(section)
        legacy_index = int(refinement["legacy_index"])
        aligned_index = int(refinement["aligned_index"])
        if not (0 <= legacy_index < len(segments)):
            raise RuntimeError(f"legacy index out of range for {source_name}")
        if not (0 <= aligned_index < len(segments)):
            raise RuntimeError(f"aligned index out of range for {source_name}")

        legacy_x = float(segments[legacy_index].x)
        aligned_x = float(segments[aligned_index].x)
        status = str(refinement["alignment_status"])
        if status == "distinct_aligned" and legacy_index == aligned_index:
            raise RuntimeError("distinct_aligned status has identical segment indices")
        if status != "distinct_aligned" and legacy_index != aligned_index:
            raise RuntimeError(f"{status} unexpectedly has distinct segment indices")

        source_modes[source_id] = {
            "name": source_name,
            "section": section,
            "target_x": info["target_x"],
            "legacy_x": legacy_x,
            "aligned_x": aligned_x,
            "legacy_offset_um": float(refinement["legacy_offset_um"]),
            "aligned_offset_um": float(refinement["aligned_offset_um"]),
            "geometry_offset_um": info["geometry_offset_um"],
            "nseg": int(section.nseg),
            "status": status,
            "identifiable": status == "distinct_aligned",
        }

    row_count = 0
    transfer_deltas_by_source = {info["name"]: [] for info in source_modes.values()}
    input_deltas_by_source = {info["name"]: [] for info in source_modes.values()}
    status_counts = {}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "morphology_label", "source", "source_swc_id",
            "source_alignment_status", "source_pair_identifiable",
            "source_section", "source_section_nseg", "source_target_x",
            "legacy_x", "aligned_x", "legacy_source_offset_um",
            "aligned_source_offset_um", "geometry_mapping_offset_um",
            "frequency_hz", "probe", "probe_swc_id",
            "legacy_input_mohm", "legacy_input_phase_deg",
            "aligned_input_mohm", "aligned_input_phase_deg",
            "input_complex_delta_pct", "input_magnitude_delta_pct",
            "input_phase_delta_deg",
            "legacy_transfer_mohm", "legacy_transfer_phase_deg",
            "aligned_transfer_mohm", "aligned_transfer_phase_deg",
            "transfer_complex_delta_pct", "transfer_magnitude_delta_pct",
            "transfer_phase_delta_deg",
        ])

        for source_id, source in source_modes.items():
            status_counts[source["status"]] = status_counts.get(source["status"], 0) + 1
            per_probe = []
            for frequency_hz in FREQUENCIES_HZ:
                mode_results = {}
                for mode_name in ("legacy", "aligned"):
                    source_x = source[f"{mode_name}_x"]
                    h.finitialize(ELEAK_MV)
                    impedance = h.Impedance()
                    impedance.loc(source_x, sec=source["section"])
                    impedance.compute(float(frequency_hz))
                    input_z = impedance_at(
                        impedance, source_x, source["section"]
                    )
                    transfer_z = {
                        probe["node_id"]: impedance_at(
                            impedance, source_x, source["section"], probe
                        )
                        for probe in probe_sites
                    }
                    mode_results[mode_name] = (input_z, transfer_z)

                legacy_input, legacy_transfer = mode_results["legacy"]
                aligned_input, aligned_transfer = mode_results["aligned"]
                input_complex_delta = relative_complex_delta_pct(
                    aligned_input, legacy_input
                )
                input_magnitude_delta = relative_magnitude_delta_pct(
                    aligned_input, legacy_input
                )
                input_phase_delta = phase_delta_deg(
                    aligned_input, legacy_input
                )
                if source["identifiable"]:
                    input_deltas_by_source[source["name"]].append(
                        input_complex_delta
                    )

                for probe in probe_sites:
                    legacy_z = legacy_transfer[probe["node_id"]]
                    aligned_z = aligned_transfer[probe["node_id"]]
                    transfer_complex_delta = relative_complex_delta_pct(
                        aligned_z, legacy_z
                    )
                    transfer_magnitude_delta = relative_magnitude_delta_pct(
                        aligned_z, legacy_z
                    )
                    transfer_phase_change = phase_delta_deg(aligned_z, legacy_z)
                    if source["identifiable"]:
                        transfer_deltas_by_source[source["name"]].append(
                            transfer_complex_delta
                        )
                    writer.writerow([
                        MORPHOLOGY_LABEL, source["name"], source_id,
                        source["status"], str(source["identifiable"]).lower(),
                        source["section"].name(), source["nseg"],
                        f"{source['target_x']:.12g}",
                        f"{source['legacy_x']:.12g}",
                        f"{source['aligned_x']:.12g}",
                        f"{source['legacy_offset_um']:.12g}",
                        f"{source['aligned_offset_um']:.12g}",
                        f"{source['geometry_offset_um']:.12g}",
                        f"{frequency_hz:.9g}", probe["name"], probe["node_id"],
                        f"{abs(legacy_input) / 1e6:.12g}",
                        f"{np.angle(legacy_input, deg=True):.12g}",
                        f"{abs(aligned_input) / 1e6:.12g}",
                        f"{np.angle(aligned_input, deg=True):.12g}",
                        f"{input_complex_delta:.12g}",
                        f"{input_magnitude_delta:.12g}",
                        f"{input_phase_delta:.12g}",
                        f"{abs(legacy_z) / 1e6:.12g}",
                        f"{np.angle(legacy_z, deg=True):.12g}",
                        f"{abs(aligned_z) / 1e6:.12g}",
                        f"{np.angle(aligned_z, deg=True):.12g}",
                        f"{transfer_complex_delta:.12g}",
                        f"{transfer_magnitude_delta:.12g}",
                        f"{transfer_phase_change:.12g}",
                    ])
                    row_count += 1

    expected_rows = len(source_modes) * len(probe_sites) * len(FREQUENCIES_HZ)
    if row_count != expected_rows:
        raise RuntimeError(f"expected {expected_rows} rows, wrote {row_count}")
    if not OUTPUT.is_file() or OUTPUT.stat().st_size <= 0:
        raise RuntimeError("AC source-alignment CSV was not written")

    print(f"NEURON={neuron.__version__}")
    print(f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}")
    print(
        f"NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}"
    )
    print(f"source_count={len(source_modes)}; probe_count={len(probe_sites)}")
    print(f"frequencies_hz={','.join(str(x) for x in FREQUENCIES_HZ)}")
    print(f"rows={row_count}; status_counts={status_counts}")
    for source_id, source in source_modes.items():
        input_values = input_deltas_by_source[source["name"]]
        transfer_values = transfer_deltas_by_source[source["name"]]
        if not source["identifiable"]:
            print(
                f"source_summary={source['name']}; status={source['status']}; "
                "identifiable=false; sensitivity_metrics=excluded"
            )
            continue
        print(
            f"source_summary={source['name']}; status={source['status']}; "
            f"identifiable=true; legacy_offset_um={source['legacy_offset_um']:.12g}; "
            f"aligned_offset_um={source['aligned_offset_um']:.12g}; "
            f"input_complex_median_p95_max_pct="
            f"{np.median(input_values):.12g},"
            f"{np.percentile(input_values, 95):.12g},"
            f"{np.max(input_values):.12g}; "
            f"transfer_complex_median_p95_max_pct="
            f"{np.median(transfer_values):.12g},"
            f"{np.percentile(transfer_values, 95):.12g},"
            f"{np.max(transfer_values):.12g}"
        )
    print(f"output_csv={OUTPUT}; bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
