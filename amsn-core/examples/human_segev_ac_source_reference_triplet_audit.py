"""Three-reference passive AC source-location audit on one NEURON mesh.

Compare on one identical final mesh:
- legacy_base_center: nearest segment centre on the original 0.125 um mesh;
- exact_swc_arc: exact section coordinate mapped from the SWC arc, matching the
  coordinate used by the AMSN-vs-NEURON AC cross-validation;
- refined_center: nearest segment centre after local nseg refinement.

The CSV records the three complex impedances and pairwise complex, magnitude
and phase changes. This separates legacy-to-exact source relocation from the
additional exact-to-refined-centre snapping effect.

All source statuses are retained. Comparisons involving an unresolved legacy /
refined pair are explicitly labelled and must not be interpreted as a valid
distinct-centre control.

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
    "AMSN_AC_TRIPLET_OUTPUT", "human-segev-ac-source-reference-triplet.csv"
))
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
ELEAK_MV = -65.0
MODES = ("legacy_base_center", "exact_swc_arc", "refined_center")
PAIRS = (
    ("legacy_to_exact", "legacy_base_center", "exact_swc_arc"),
    ("exact_to_refined", "exact_swc_arc", "refined_center"),
    ("legacy_to_refined", "legacy_base_center", "refined_center"),
)


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


def measure_impedance(source_x: float, source_section, probe_sites: list[dict], frequency_hz: float):
    h.finitialize(ELEAK_MV)
    impedance = h.Impedance()
    impedance.loc(float(source_x), sec=source_section)
    impedance.compute(float(frequency_hz))

    input_z = complex_from_measurement(
        float(impedance.input(float(source_x), sec=source_section)),
        float(impedance.input_phase(float(source_x), sec=source_section)),
    )
    transfer = {}
    for probe in probe_sites:
        transfer[probe["node_id"]] = complex_from_measurement(
            float(impedance.transfer(probe["x"], sec=probe["section"])),
            float(impedance.transfer_phase(probe["x"], sec=probe["section"])),
        )
    return input_z, transfer


def add_pairwise_fields(row: dict, observable: str, values: dict[str, complex]) -> None:
    for pair_name, baseline_name, target_name in PAIRS:
        baseline = values[baseline_name]
        target = values[target_name]
        row[f"{pair_name}_{observable}_complex_delta_pct"] = (
            f"{relative_complex_delta_pct(target, baseline):.12g}"
        )
        row[f"{pair_name}_{observable}_magnitude_delta_pct"] = (
            f"{relative_magnitude_delta_pct(target, baseline):.12g}"
        )
        row[f"{pair_name}_{observable}_phase_delta_deg"] = (
            f"{phase_delta_deg(target, baseline):.12g}"
        )


def main() -> None:
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

    # Rebuild fixed probe mappings only after the final shared mesh is set.
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
            raise RuntimeError(f"refined index out of range for {source_name}")

        legacy_x = float(segments[legacy_index].x)
        exact_x = float(info["target_x"])
        refined_x = float(segments[aligned_index].x)
        status = str(refinement["alignment_status"])
        if status == "distinct_aligned" and legacy_index == aligned_index:
            raise RuntimeError("distinct_aligned status has identical segment indices")
        if status != "distinct_aligned" and legacy_index != aligned_index:
            raise RuntimeError(f"{status} unexpectedly has distinct segment indices")

        source_modes[source_id] = {
            "name": source_name,
            "section": section,
            "target_x": exact_x,
            "legacy_x": legacy_x,
            "refined_x": refined_x,
            "legacy_offset_um": abs(legacy_x - exact_x) * float(section.L),
            "refined_offset_um": abs(refined_x - exact_x) * float(section.L),
            "geometry_offset_um": info["geometry_offset_um"],
            "nseg": int(section.nseg),
            "status": status,
            "legacy_refined_pair_identifiable": status == "distinct_aligned",
        }

    status_counts = {}
    pairwise_input = {
        source["name"]: {pair[0]: [] for pair in PAIRS}
        for source in source_modes.values()
    }
    pairwise_transfer = {
        source["name"]: {pair[0]: [] for pair in PAIRS}
        for source in source_modes.values()
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0

    fieldnames = [
        "morphology_label", "source", "source_swc_id",
        "source_alignment_status", "legacy_refined_pair_identifiable",
        "source_section", "source_section_nseg", "source_exact_swc_x",
        "legacy_base_center_x", "refined_center_x",
        "legacy_source_offset_um", "refined_source_offset_um",
        "geometry_mapping_offset_um", "frequency_hz", "probe", "probe_swc_id",
    ]
    for short in ("legacy_base", "exact_swc", "refined_center"):
        fieldnames.extend([
            f"{short}_input_mohm", f"{short}_input_phase_deg",
            f"{short}_transfer_mohm", f"{short}_transfer_phase_deg",
        ])
    for pair_name, _, _ in PAIRS:
        for observable in ("input", "transfer"):
            fieldnames.extend([
                f"{pair_name}_{observable}_complex_delta_pct",
                f"{pair_name}_{observable}_magnitude_delta_pct",
                f"{pair_name}_{observable}_phase_delta_deg",
            ])

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for source_id, source in source_modes.items():
            status_counts[source["status"]] = status_counts.get(source["status"], 0) + 1
            positions = {
                "legacy_base_center": source["legacy_x"],
                "exact_swc_arc": source["target_x"],
                "refined_center": source["refined_x"],
            }
            for frequency_hz in FREQUENCIES_HZ:
                measurements = {}
                for mode in MODES:
                    measurements[mode] = measure_impedance(
                        positions[mode], source["section"], probe_sites, frequency_hz
                    )

                input_values = {
                    mode: measurements[mode][0]
                    for mode in MODES
                }
                for pair_name, baseline_name, target_name in PAIRS:
                    pairwise_input[source["name"]][pair_name].append(
                        relative_complex_delta_pct(
                            input_values[target_name], input_values[baseline_name]
                        )
                    )

                for probe in probe_sites:
                    transfer_values = {
                        mode: measurements[mode][1][probe["node_id"]]
                        for mode in MODES
                    }
                    row = {
                        "morphology_label": MORPHOLOGY_LABEL,
                        "source": source["name"],
                        "source_swc_id": source_id,
                        "source_alignment_status": source["status"],
                        "legacy_refined_pair_identifiable": str(
                            source["legacy_refined_pair_identifiable"]
                        ).lower(),
                        "source_section": source["section"].name(),
                        "source_section_nseg": source["nseg"],
                        "source_exact_swc_x": f"{source['target_x']:.12g}",
                        "legacy_base_center_x": f"{source['legacy_x']:.12g}",
                        "refined_center_x": f"{source['refined_x']:.12g}",
                        "legacy_source_offset_um": f"{source['legacy_offset_um']:.12g}",
                        "refined_source_offset_um": f"{source['refined_offset_um']:.12g}",
                        "geometry_mapping_offset_um": f"{source['geometry_offset_um']:.12g}",
                        "frequency_hz": f"{frequency_hz:.9g}",
                        "probe": probe["name"],
                        "probe_swc_id": probe["node_id"],
                    }
                    for mode, z in input_values.items():
                        short = {
                            "legacy_base_center": "legacy_base",
                            "exact_swc_arc": "exact_swc",
                            "refined_center": "refined_center",
                        }[mode]
                        row[f"{short}_input_mohm"] = f"{abs(z) / 1e6:.12g}"
                        row[f"{short}_input_phase_deg"] = f"{np.angle(z, deg=True):.12g}"
                    add_pairwise_fields(row, "input", input_values)

                    for mode, z in transfer_values.items():
                        short = {
                            "legacy_base_center": "legacy_base",
                            "exact_swc_arc": "exact_swc",
                            "refined_center": "refined_center",
                        }[mode]
                        row[f"{short}_transfer_mohm"] = f"{abs(z) / 1e6:.12g}"
                        row[f"{short}_transfer_phase_deg"] = f"{np.angle(z, deg=True):.12g}"
                    add_pairwise_fields(row, "transfer", transfer_values)
                    writer.writerow(row)
                    row_count += 1

                    for pair_name, baseline_name, target_name in PAIRS:
                        pairwise_transfer[source["name"]][pair_name].append(
                            relative_complex_delta_pct(
                                transfer_values[target_name],
                                transfer_values[baseline_name],
                            )
                        )

    expected_rows = len(source_modes) * len(probe_sites) * len(FREQUENCIES_HZ)
    if row_count != expected_rows:
        raise RuntimeError(f"expected {expected_rows} rows, wrote {row_count}")
    if not OUTPUT.is_file() or OUTPUT.stat().st_size <= 0:
        raise RuntimeError("triplet AC source-reference CSV was not written")

    print(f"NEURON={neuron.__version__}")
    print(f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}")
    print(
        f"NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}"
    )
    print(
        f"source_count={len(source_modes)}; probe_count={len(probe_sites)}; "
        f"frequencies={len(FREQUENCIES_HZ)}; rows={row_count}"
    )
    print(f"status_counts={status_counts}")
    for source in source_modes.values():
        print(
            f"source={source['name']}; status={source['status']}; "
            f"legacy_offset_um={source['legacy_offset_um']:.12g}; "
            f"refined_offset_um={source['refined_offset_um']:.12g}; "
            f"legacy_refined_pair_identifiable="
            f"{str(source['legacy_refined_pair_identifiable']).lower()}"
        )
        for pair_name, _, _ in PAIRS:
            ivals = pairwise_input[source["name"]][pair_name]
            tvals = pairwise_transfer[source["name"]][pair_name]
            print(
                f"source_pair_summary={source['name']}/{pair_name}; "
                f"input_complex_median_p95_max_pct="
                f"{np.median(ivals):.12g},{np.percentile(ivals, 95):.12g},{np.max(ivals):.12g}; "
                f"transfer_complex_median_p95_max_pct="
                f"{np.median(tvals):.12g},{np.percentile(tvals, 95):.12g},{np.max(tvals):.12g}"
            )
    print(f"output_csv={OUTPUT}; bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
