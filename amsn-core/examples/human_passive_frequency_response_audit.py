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


MORPHOLOGY_PATH = os.environ.get("AMSN_MORPHOLOGY_PATH")
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "nmo_290988")


def configure_reference() -> None:
    if MORPHOLOGY_PATH:
        reference.DATA = Path(MORPHOLOGY_PATH)
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
    soma_normalization = morphology.detect_neuromorpho_three_point_soma()
    electrical_map = morphology.electrical_node_mapping()
    neuron_area_um2 = float(
        sum(float(segment.area()) for section in sections for segment in section)
    )
    amsn_area_um2 = float(np.sum(cable.area_m2) * 1e12)
    area_difference_pct = (
        100.0 * (neuron_area_um2 - amsn_area_um2)
        / max(amsn_area_um2, 1e-30)
    )
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
            "morphology_label", "source", "source_swc_id", "probe", "probe_swc_id", "frequency_hz", "neuron_max_segment_um",
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
                        MORPHOLOGY_LABEL, source_name, source_id, probe_name, probe_id,
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
    print(f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}; SWC_records={len(morphology.nodes)}")
    print(
        f"NEURON_sections={len(sections)}; "
        f"NEURON_segments={sum(section.nseg for section in sections)}; "
        f"max_segment_length_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(f"AMSN_compartments={cable.n_compartments}")
    print(
        f"soma_root={soma_normalization.root_id}; "
        f"soma_node_ids={','.join(str(x) for x in soma_normalization.soma_node_ids)}; "
        f"wire_attachment_count={len(soma_normalization.wire_attachment_node_ids)}; "
        f"wire_attachment_ids={','.join(str(x) for x in soma_normalization.wire_attachment_node_ids)}"
    )
    print(f"NEURON_total_membrane_area_um2={neuron_area_um2:.12g}")
    print(f"AMSN_total_membrane_area_um2={amsn_area_um2:.12g}")
    print(f"NEURON_minus_AMSN_area_difference_pct={area_difference_pct:.12g}")
    if soma_normalization is None:
        raise RuntimeError("expected NeuroMorpho three-point soma normalization was not detected")

    # Decompose reconstructed area and Import3D's sections before interpreting
    # any electrical discrepancy. All areas are in um^2; lengths in um.
    swc_area_by_type: dict[int, float] = {}
    swc_length_by_type: dict[int, float] = {}
    for node_id, node in morphology.nodes.items():
        if node.parent_id == -1:
            continue
        parent_node = morphology.nodes[node.parent_id]
        edge_length = float(np.linalg.norm([
            node.x_um - parent_node.x_um,
            node.y_um - parent_node.y_um,
            node.z_um - parent_node.z_um,
        ]))
        edge_area = np.pi * (
            parent_node.radius_um + node.radius_um
        ) * np.hypot(edge_length, node.radius_um - parent_node.radius_um)
        swc_area_by_type[node.neurite_type] = (
            swc_area_by_type.get(node.neurite_type, 0.0) + edge_area
        )
        swc_length_by_type[node.neurite_type] = (
            swc_length_by_type.get(node.neurite_type, 0.0) + edge_length
        )

    neuron_sections_by_type: dict[str, list[dict[str, float]]] = {}
    neuron_area_by_type: dict[str, float] = {}
    for section in sections:
        section_type = section.name().split("[", 1)[0]
        section_area = sum(float(segment.area()) for segment in section)
        neuron_area_by_type[section_type] = (
            neuron_area_by_type.get(section_type, 0.0) + section_area
        )
        neuron_sections_by_type.setdefault(section_type, []).append({
            "length_um": float(section.L),
            "nseg": int(section.nseg),
            "n3d": int(h.n3d(sec=section)),
            "area_um2": float(section_area),
        })

    print(f"SWC_frustum_area_by_type_um2={swc_area_by_type}")
    print(f"SWC_path_length_by_type_um={swc_length_by_type}")
    print(f"NEURON_import3d_area_by_section_type_um2={neuron_area_by_type}")
    for section_type, type_sections in sorted(neuron_sections_by_type.items()):
        print(
            f"NEURON_section_signature_{section_type}="
            f"count:{len(type_sections)};"
            f"nseg:{sum(int(x['nseg']) for x in type_sections)};"
            f"n3d:{sum(int(x['n3d']) for x in type_sections)};"
            f"area_um2:{sum(float(x['area_um2']) for x in type_sections):.12g};"
            f"length_um:{sum(float(x['length_um']) for x in type_sections):.12g}"
        )

    print(
        f"AMSN_root_soma_area_um2={soma_normalization.root_soma_area_um2:.12g};"
        f"root_radius_um={morphology.nodes[soma_normalization.root_id].radius_um:.12g};"
        f"wire_attachment_count={len(soma_normalization.wire_attachment_node_ids)};"
        f"wire_attachment_lengths_um={soma_normalization.wire_attachment_lengths_um}"
    )
    for wire_id in soma_normalization.wire_attachment_node_ids:
        point_index = int(reader.id2pt(int(wire_id)))
        section_index = int(reader.point2sec.x[point_index])
        imported_section = reader.sections.object(section_index)
        base_type = {1: "soma", 2: "axon", 3: "dend", 4: "apic"}.get(
            int(imported_section.type), "unknown"
        )
        section_name_index = int(imported_section.nameindex)
        section_name = (
            f"{base_type}[{section_name_index}]"
            if section_name_index > 0 else base_type
        )
        print(
            f"IMPORT3D_wire_attachment_swc_id={wire_id};"
            f"point_index={point_index};section_index={section_index};"
            f"section_name={section_name};"
            f"first={int(imported_section.first)};"
            f"point_count={int(imported_section.d.size())}"
        )
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
    for source_name, source_id in injections:
        site = sites[source_id]
        print(
            f"SOURCE_SITE_{source_name}=swc:{source_id};"
            f"section:{site['section'].name()};x:{float(site['normalized_x']):.12g};"
            f"nearest_centre_offset_um:{float(site['nearest_centre_offset_um']):.12g}"
        )
    for probe_name, probe_id in probes:
        site = sites[probe_id]
        print(
            f"PROBE_SITE_{probe_name}=swc:{probe_id};"
            f"section:{site['section'].name()};x:{float(site['normalized_x']):.12g};"
            f"nearest_centre_offset_um:{float(site['nearest_centre_offset_um']):.12g}"
        )
    print(f"output_csv={OUTPUT}")


if __name__ == "__main__":
    main()
