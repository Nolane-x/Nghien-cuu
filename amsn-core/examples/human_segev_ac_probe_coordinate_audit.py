"""Probe-coordinate sensitivity audit for Segev passive AC impedance.

The existing AMSN-vs-NEURON frequency audit evaluates NEURON transfer
impedance at exact SWC-derived section coordinates. This experiment holds
the source reference fixed at that same exact SWC coordinate and compares
three NEURON readout rules on one identical morphology mesh:

1. exact_swc_arc: Impedance.transfer() at the mapped SWC section coordinate;
2. nearest_segment_center: Impedance.transfer() at the nearest segment centre;
3. complex_linear_interpolation: complex-linear interpolation between the
   adjacent segment-centre transfer impedances bracketing the SWC coordinate.

The interpolation is applied to the complex impedance (real and imaginary
parts), not independently to magnitude and phase. The raw CSV records the
actual values and pairwise deltas. No membrane parameter or source placement
is changed.

This is a within-NEURON probe readout audit, not biological validation.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
OUTPUT = Path(os.environ.get(
    "AMSN_PROBE_AUDIT_OUTPUT", "human-segev-ac-probe-coordinate-audit.csv"
))
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
MODES = ("exact_swc_arc", "nearest_segment_center", "complex_linear_interpolation")
PAIRS = (
    ("nearest_vs_exact", "exact_swc_arc", "nearest_segment_center"),
    ("interpolated_vs_exact", "exact_swc_arc", "complex_linear_interpolation"),
    ("interpolated_vs_nearest", "nearest_segment_center", "complex_linear_interpolation"),
)


def complex_from_measurement(magnitude_mohm: float, phase_rad: float) -> complex:
    if not np.isfinite(magnitude_mohm) or magnitude_mohm < 0.0:
        raise RuntimeError(f"invalid impedance magnitude: {magnitude_mohm}")
    if not np.isfinite(phase_rad):
        raise RuntimeError(f"invalid impedance phase: {phase_rad}")
    return magnitude_mohm * 1e6 * np.exp(1j * phase_rad)


def measure_transfer(impedance, x: float, section) -> complex:
    return complex_from_measurement(
        float(impedance.transfer(float(x), sec=section)),
        float(impedance.transfer_phase(float(x), sec=section)),
    )


def relative_complex_delta_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(value - baseline) / max(abs(baseline), 1e-30)


def relative_magnitude_delta_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(abs(value) - abs(baseline)) / max(abs(baseline), 1e-30)


def phase_delta_deg(value: complex, baseline: complex) -> float:
    if abs(value) == 0.0 or abs(baseline) == 0.0:
        return float("nan")
    return float(np.angle(value / baseline, deg=True))


def configure_reference() -> None:
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV


def main() -> None:
    configure_reference()
    morphology_path = os.environ.get("AMSN_MORPHOLOGY_PATH")
    if morphology_path:
        reference.DATA = Path(morphology_path)

    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(morphology, reader, sections)

    # Validate the site geometry once, before making any impedance calls.
    for name, node_id in injections + probes:
        site = sites[node_id]
        if not 0.0 <= site["normalized_x"] <= 1.0:
            raise RuntimeError(f"{name}/SWC {node_id}: invalid normalized x")
        if not (
            site["lower_x"] <= site["normalized_x"] <= site["upper_x"]
            and site["upper_x"] > site["lower_x"]
        ):
            raise RuntimeError(f"{name}/SWC {node_id}: invalid interpolation bracket")

    summary_values = {
        probe_name: {
            pair[0]: []
            for pair in PAIRS
        }
        for probe_name, _ in probes
    }
    per_pair_values = {}
    rows = []
    row_count = 0

    for source_name, source_id in injections:
        source_site = sites[source_id]
        source_section = source_site["section"]
        source_x = float(source_site["normalized_x"])

        for frequency_hz in FREQUENCIES_HZ:
            h.finitialize(ELEAK_MV)
            impedance = h.Impedance()
            impedance.loc(source_x, sec=source_section)
            impedance.compute(float(frequency_hz))

            for probe_name, probe_id in probes:
                site = sites[probe_id]
                exact_x = float(site["normalized_x"])
                nearest_x = float(site["nearest_segment"].x)
                lower_x = float(site["lower_x"])
                upper_x = float(site["upper_x"])
                upper_weight = float(site["interpolation_upper_weight"])

                exact_z = measure_transfer(impedance, exact_x, site["section"])
                nearest_z = measure_transfer(impedance, nearest_x, site["section"])
                lower_z = measure_transfer(impedance, lower_x, site["section"])
                upper_z = measure_transfer(impedance, upper_x, site["section"])
                interpolated_z = (
                    lower_z * (1.0 - upper_weight)
                    + upper_z * upper_weight
                )

                values = {
                    "exact_swc_arc": exact_z,
                    "nearest_segment_center": nearest_z,
                    "complex_linear_interpolation": interpolated_z,
                }
                deltas = {}
                for pair_name, baseline_name, target_name in PAIRS:
                    baseline = values[baseline_name]
                    target = values[target_name]
                    complex_delta = relative_complex_delta_pct(target, baseline)
                    magnitude_delta = relative_magnitude_delta_pct(target, baseline)
                    phase_change = phase_delta_deg(target, baseline)
                    deltas[pair_name] = (
                        complex_delta, magnitude_delta, phase_change
                    )
                    summary_values[probe_name][pair_name].append(complex_delta)
                    per_key = (source_name, probe_name, pair_name)
                    per_pair_values.setdefault(per_key, []).append(complex_delta)

                row = {
                    "morphology_label": MORPHOLOGY_LABEL,
                    "source": source_name,
                    "source_swc_id": source_id,
                    "source_section": source_section.name(),
                    "source_exact_swc_x": f"{source_x:.12g}",
                    "source_nearest_center_offset_um": (
                        f"{source_site['nearest_centre_offset_um']:.12g}"
                    ),
                    "probe": probe_name,
                    "probe_swc_id": probe_id,
                    "probe_section": site["section_name"],
                    "probe_exact_swc_x": f"{exact_x:.12g}",
                    "probe_nearest_center_x": f"{nearest_x:.12g}",
                    "probe_lower_center_x": f"{lower_x:.12g}",
                    "probe_upper_center_x": f"{upper_x:.12g}",
                    "probe_interpolation_upper_weight": f"{upper_weight:.12g}",
                    "probe_nearest_center_offset_um": (
                        f"{site['nearest_centre_offset_um']:.12g}"
                    ),
                    "probe_geometry_mapping_offset_um": (
                        f"{site['geometry_offset_um']:.12g}"
                    ),
                    "frequency_hz": f"{frequency_hz:.9g}",
                }
                for mode, impedance_value in values.items():
                    row[f"{mode}_transfer_mohm"] = (
                        f"{abs(impedance_value) / 1e6:.12g}"
                    )
                    row[f"{mode}_transfer_phase_deg"] = (
                        f"{np.angle(impedance_value, deg=True):.12g}"
                    )
                for pair_name, (complex_delta, magnitude_delta, phase_change) in deltas.items():
                    row[f"{pair_name}_complex_delta_pct"] = f"{complex_delta:.12g}"
                    row[f"{pair_name}_magnitude_delta_pct"] = f"{magnitude_delta:.12g}"
                    row[f"{pair_name}_phase_delta_deg"] = f"{phase_change:.12g}"
                rows.append(row)
                row_count += 1

    expected_rows = len(injections) * len(probes) * len(FREQUENCIES_HZ)
    if row_count != expected_rows:
        raise RuntimeError(f"expected {expected_rows} rows, produced {row_count}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    if not OUTPUT.is_file() or OUTPUT.stat().st_size <= 0:
        raise RuntimeError("probe-coordinate audit CSV was not written")

    print(f"NEURON={neuron.__version__}")
    print(f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}")
    print(
        f"NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}"
    )
    print(
        f"source_count={len(injections)}; probe_count={len(probes)}; "
        f"frequencies={len(FREQUENCIES_HZ)}; rows={row_count}"
    )
    print(
        f"passive_Ri_ohm_m={RI_OHM_M:g}; Rm_ohm_m2={RM_OHM_M2:g}; "
        f"Cm_F_m2={CM_F_M2:g}; Eleak_mV={ELEAK_MV:g}"
    )
    for probe_name, _ in probes:
        site = sites[_]
        print(
            f"probe_site={probe_name}; swc_id={_}; "
            f"section={site['section_name']}; x={site['normalized_x']:.12g}; "
            f"nearest_center_offset_um={site['nearest_centre_offset_um']:.12g}; "
            f"geometry_offset_um={site['geometry_offset_um']:.12g}; "
            f"interpolation_weight={site['interpolation_upper_weight']:.12g}"
        )
        for pair_name, _, _ in PAIRS:
            values = np.asarray(summary_values[probe_name][pair_name], dtype=float)
            print(
                f"probe_summary={probe_name}/{pair_name}; "
                f"complex_delta_median_p95_max_pct="
                f"{np.median(values):.12g},{np.percentile(values, 95):.12g},"
                f"{np.max(values):.12g}"
            )
    for (source_name, probe_name, pair_name), values in sorted(per_pair_values.items()):
        array = np.asarray(values, dtype=float)
        print(
            f"source_probe_summary={source_name}/{probe_name}/{pair_name}; "
            f"complex_delta_median_max_pct="
            f"{np.median(array):.12g},{np.max(array):.12g}"
        )
    print(f"output_csv={OUTPUT}; bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
