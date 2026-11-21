"""Passive frequency-domain impedance audit against NEURON 9.0.2.

Compares complex input and transfer impedance on one partial human temporal
cortex L2-3 morphology. AMSN solves the full SWC electrical tree with a
complex-valued Hines solver; NEURON uses Import3D and Impedance.compute().
All passive parameters and source/probe identities are fixed. This is a
numerical passive-model comparison, not a biological validation.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import neuron_cross_validation as reference
import human_fine_mesh_passive_dc_audit as fine_audit
from amsn.morphology import SWCMorphology


RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.5"))
CURRENT_A = 1e-9
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
OUTPUT = Path(os.environ.get("AMSN_FREQUENCY_OUTPUT", "human-passive-frequency-response.csv"))


def configure_reference() -> None:
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV


def complex_from_magnitude_phase(magnitude: float, phase_rad: float) -> complex:
    if not np.isfinite(magnitude) or magnitude < 0.0:
        raise RuntimeError(f"invalid impedance magnitude: {magnitude}")
    if not np.isfinite(phase_rad):
        raise RuntimeError(f"invalid impedance phase: {phase_rad}")
    return magnitude * np.exp(1j * phase_rad)


def relative_complex_error_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(value - baseline) / max(abs(baseline), 1e-30)


def magnitude_error_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(abs(value) - abs(baseline)) / max(abs(baseline), 1e-30)


def phase_error_deg(value: complex, baseline: complex) -> float:
    return abs(float(np.angle(value / baseline, deg=True)))


def summary(values: list[float]) -> tuple[float, float, float]:
    array = np.asarray(values, dtype=float)
    return (
        float(np.median(array)),
        float(np.percentile(array, 95)),
        float(np.max(array)),
    )


def main() -> None:
    configure_reference()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(
        morphology, reader, sections
    )
    cable = morphology.to_cable_tree()
    electrical_map = morphology.electrical_node_mapping()
    node_to_name = {
        node_id: f"swc_{electrical_id}"
        for node_id, electrical_id in electrical_map.items()
    }

    input_complex_errors: list[float] = []
    transfer_complex_errors: list[float] = []
    transfer_magnitude_errors: list[float] = []
    transfer_phase_errors: list[float] = []
    transfer_by_frequency = {frequency: [] for frequency in FREQUENCIES_HZ}
    magnitude_by_frequency = {frequency: [] for frequency in FREQUENCIES_HZ}
    phase_by_frequency = {frequency: [] for frequency in FREQUENCIES_HZ}
    input_by_frequency = {frequency: [] for frequency in FREQUENCIES_HZ}
    row_count = 0

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "source", "source_swc_id", "probe", "probe_swc_id", "frequency_hz", "neuron_max_segment_um",
            "neuron_input_mohm", "neuron_input_phase_deg",
            "amsn_input_mohm", "amsn_input_phase_deg",
            "input_magnitude_error_pct", "input_phase_error_deg",
            "input_complex_error_pct",
            "neuron_transfer_mohm", "neuron_transfer_phase_deg",
            "amsn_transfer_mohm", "amsn_transfer_phase_deg",
            "transfer_magnitude_error_pct", "transfer_phase_error_deg",
            "transfer_complex_error_pct",
            "source_nearest_centre_offset_um",
            "probe_nearest_centre_offset_um",
        ])

        for source_name, source_id in injections:
            source_site = sites[source_id]
            source_section = source_site["section"]
            source_x = float(source_site["normalized_x"])
            source_index = cable.index[node_to_name[source_id]]
            current = np.zeros(cable.n_compartments, dtype=np.complex128)
            current[source_index] = CURRENT_A

            for frequency_hz in FREQUENCIES_HZ:
                amsn_voltage = cable.solve_passive_frequency_response(
                    frequency_hz, current
                )
                amsn_input = amsn_voltage[source_index] / CURRENT_A

                h.finitialize(ELEAK_MV)
                impedance = h.Impedance()
                impedance.loc(source_x, sec=source_section)
                impedance.compute(float(frequency_hz))
                neuron_input = complex_from_magnitude_phase(
                    float(impedance.input(source_x, sec=source_section)) * 1e6,
                    float(impedance.input_phase(source_x, sec=source_section)),
                )
                amsn_input_error = relative_complex_error_pct(
                    amsn_input, neuron_input
                )
                amsn_input_magnitude_error = magnitude_error_pct(
                    amsn_input, neuron_input
                )
                amsn_input_phase_error = phase_error_deg(
                    amsn_input, neuron_input
                )
                input_complex_errors.append(amsn_input_error)
                input_by_frequency[frequency_hz].append(amsn_input_error)

                for probe_name, probe_id in probes:
                    probe_site = sites[probe_id]
                    probe_index = cable.index[node_to_name[probe_id]]
                    amsn_transfer = amsn_voltage[probe_index] / CURRENT_A
                    neuron_transfer = complex_from_magnitude_phase(
                        float(impedance.transfer(
                            float(probe_site["normalized_x"]),
                            sec=probe_site["section"],
                        )) * 1e6,
                        float(impedance.transfer_phase(
                            float(probe_site["normalized_x"]),
                            sec=probe_site["section"],
                        )),
                    )

                    transfer_complex_error = relative_complex_error_pct(
                        amsn_transfer, neuron_transfer
                    )
                    transfer_magnitude_error = magnitude_error_pct(
                        amsn_transfer, neuron_transfer
                    )
                    transfer_phase_error = phase_error_deg(
                        amsn_transfer, neuron_transfer
                    )
                    transfer_complex_errors.append(transfer_complex_error)
                    transfer_magnitude_errors.append(transfer_magnitude_error)
                    transfer_phase_errors.append(transfer_phase_error)
                    transfer_by_frequency[frequency_hz].append(transfer_complex_error)
                    magnitude_by_frequency[frequency_hz].append(transfer_magnitude_error)
                    phase_by_frequency[frequency_hz].append(transfer_phase_error)
                    row_count += 1

                    writer.writerow([
                        source_name, source_id, probe_name, probe_id,
                        f"{frequency_hz:.9g}",
                        f"{NEURON_MAX_SEGMENT_UM:.9g}",
                        f"{abs(neuron_input) / 1e6:.12g}",
                        f"{np.angle(neuron_input, deg=True):.12g}",
                        f"{abs(amsn_input) / 1e6:.12g}",
                        f"{np.angle(amsn_input, deg=True):.12g}",
                        f"{amsn_input_magnitude_error:.12g}",
                        f"{amsn_input_phase_error:.12g}",
                        f"{amsn_input_error:.12g}",
                        f"{abs(neuron_transfer) / 1e6:.12g}",
                        f"{np.angle(neuron_transfer, deg=True):.12g}",
                        f"{abs(amsn_transfer) / 1e6:.12g}",
                        f"{np.angle(amsn_transfer, deg=True):.12g}",
                        f"{transfer_magnitude_error:.12g}",
                        f"{transfer_phase_error:.12g}",
                        f"{transfer_complex_error:.12g}",
                        f"{source_site['nearest_centre_offset_um']:.12g}",
                        f"{probe_site['nearest_centre_offset_um']:.12g}",
                    ])

    if row_count != len(injections) * len(probes) * len(FREQUENCIES_HZ):
        raise RuntimeError(f"unexpected row count: {row_count}")
    if not OUTPUT.is_file() or OUTPUT.stat().st_size <= 0:
        raise RuntimeError("frequency-response CSV was not written")

    print(f"NEURON={neuron.__version__}")
    print(f"morphology=NMO_290988; SWC_records={len(morphology.nodes)}")
    print(
        f"NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}; "
        f"max_segment_length_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(f"AMSN_compartments={cable.n_compartments}")
    print(f"passive_Ri_ohm_m={RI_OHM_M:g}; Rm_ohm_m2={RM_OHM_M2:g}; "
          f"Cm_F_m2={CM_F_M2:g}; Eleak_mV={ELEAK_MV:g}")
    print(f"frequencies_hz={','.join(str(x) for x in FREQUENCIES_HZ)}")
    print(f"source_count={len(injections)}; probe_count={len(probes)}; rows={row_count}")
    print(
        "input_complex_error_pct_median_p95_max="
        + ",".join(f"{x:.12g}" for x in summary(input_complex_errors))
    )
    print(
        "transfer_complex_error_pct_median_p95_max="
        + ",".join(f"{x:.12g}" for x in summary(transfer_complex_errors))
    )
    print(
        "transfer_magnitude_error_pct_median_p95_max="
        + ",".join(f"{x:.12g}" for x in summary(transfer_magnitude_errors))
    )
    print(
        "transfer_phase_error_deg_median_p95_max="
        + ",".join(f"{x:.12g}" for x in summary(transfer_phase_errors))
    )
    for frequency_hz in FREQUENCIES_HZ:
        transfer_stats = summary(transfer_by_frequency[frequency_hz])
        magnitude_stats = summary(magnitude_by_frequency[frequency_hz])
        phase_stats = summary(phase_by_frequency[frequency_hz])
        input_stats = summary(input_by_frequency[frequency_hz])
        print(
            f"by_frequency_hz={frequency_hz:g}; "
            f"transfer_complex_median_p95_max_pct="
            f"{transfer_stats[0]:.12g},{transfer_stats[1]:.12g},{transfer_stats[2]:.12g}; "
            f"transfer_magnitude_max_pct={magnitude_stats[2]:.12g}; "
            f"transfer_phase_max_deg={phase_stats[2]:.12g}; "
            f"input_complex_max_pct={input_stats[2]:.12g}"
        )
    print(f"output_csv={OUTPUT}")


if __name__ == "__main__":
    main()
