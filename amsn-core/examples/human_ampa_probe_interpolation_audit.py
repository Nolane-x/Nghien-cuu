"""Audit NEURON segment-centre sampling and AMSN control-volume area.

The NEURON reference uses a fixed 0.5-um section mesh at dt=0.0015625 ms.
For the protected SWC source/probe coordinates, this script records:
- NEURON's nearest segment-centre voltage;
- a linear interpolation between the two adjacent segment-centre voltages
  evaluated at the exact Import3D SWC arc coordinate;
- NEURON segment area at both bracketing centres and the interpolated area;
- AMSN's exact protected control-point voltage and lumped membrane area.

AMSN mesh frequencies 2,000, 4,000 and 6,000 Hz are compared to the same
NEURON run. The synapse is still delivered to the nearest NEURON segment, as
in the earlier reference experiment; interpolation changes the readout only.
It does not change the NEURON simulation or relocate the point process.

Linear interpolation is a diagnostic estimate of voltage at the SWC arc point,
not an exact analytical reconstruction of the continuous cable solution.
"""
from __future__ import annotations

from math import ceil

import numpy as np
from neuron import h, __version__ as neuron_version

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree
from amsn.synapses import DoubleExponentialSynapse


DT_MS = 0.0015625
DT_S = DT_MS * 1e-3
DURATION_MS = 5.0
DURATION_S = DURATION_MS * 1e-3

NEURON_MAX_SEGMENT_UM = 0.5
AMSN_REFERENCE_FREQUENCIES_HZ = (2000.0, 4000.0, 6000.0)
AMSN_MAX_SEGMENT_LENGTH_UM = 100.0
AMSN_MAX_ELECTROTONIC_LENGTH = 0.1

SOURCE_ID = 3784
PROBE_ROWS = (
    ("basal_q75_source", SOURCE_ID),
    ("soma", 1),
    ("basal_q90", 3814),
)
PROBE_IDS = tuple(node_id for _, node_id in PROBE_ROWS)
PROTECTED_IDS = set(PROBE_IDS)

ELEAK_MV = -65.0
PEAK_CONDUCTANCE_S = 0.8e-9
TAU_RISE_S = 0.0002
TAU_DECAY_S = 0.002
REVERSAL_POTENTIAL_V = 0.0
RELATIVE_FLOORS_MV = (0.02, 0.1, 0.2, 0.5, 1.0)


def configure_neuron_nseg(sections) -> None:
    for section in sections:
        nseg = max(1, ceil(section.L / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()


def segment_key(section_name: str, segment) -> tuple[str, float]:
    return section_name, float(segment.x)


def bracket_site(reader, section_by_name, morphology, node_id):
    nearest, total, geometry, centre, section_name, normalized = (
        reference.locate_neuron_segment(
            reader, section_by_name, morphology.nodes[node_id]
        )
    )
    section = section_by_name[section_name]
    segments = list(section)
    left_candidates = [
        segment for segment in segments
        if segment.x <= normalized + 1e-12
    ]
    right_candidates = [
        segment for segment in segments
        if segment.x >= normalized - 1e-12
    ]
    left = left_candidates[-1] if left_candidates else segments[0]
    right = right_candidates[0] if right_candidates else segments[-1]

    if abs(normalized - left.x) <= 1e-12:
        right = left
        weight = 0.0
    elif abs(right.x - normalized) <= 1e-12:
        left = right
        weight = 0.0
    elif right.x > left.x:
        weight = (normalized - left.x) / (right.x - left.x)
    else:
        raise RuntimeError(
            f"Could not bracket SWC node {node_id} at {section_name}({normalized})"
        )

    return {
        "nearest": nearest,
        "nearest_key": segment_key(section_name, nearest),
        "left": left,
        "left_key": segment_key(section_name, left),
        "right": right,
        "right_key": segment_key(section_name, right),
        "weight": float(weight),
        "section": section_name,
        "x": float(normalized),
        "total_offset_um": float(total),
        "geometry_offset_um": float(geometry),
        "centre_offset_um": float(centre),
        "left_x": float(left.x),
        "right_x": float(right.x),
        "nearest_x": float(nearest.x),
        "left_area_um2": float(left.area()),
        "right_area_um2": float(right.area()),
        "nearest_area_um2": float(nearest.area()),
    }


def run_neuron_reference(morphology):
    reader, sections = reference.import_swc_with_neuron()
    configure_neuron_nseg(sections)
    section_by_name = {section.name(): section for section in sections}

    sites = {
        node_id: bracket_site(reader, section_by_name, morphology, node_id)
        for node_id in PROBE_IDS
    }
    record_segments = {}
    for site in sites.values():
        for field in ("nearest", "left", "right"):
            key = site[f"{field}_key"]
            segment = site[field]
            record_segments.setdefault(key, segment)

    synapse_site = sites[SOURCE_ID]
    synapse = h.Exp2Syn(synapse_site["nearest"])
    synapse.tau1 = TAU_RISE_S * 1e3
    synapse.tau2 = TAU_DECAY_S * 1e3
    synapse.e = REVERSAL_POTENTIAL_V * 1e3

    stimulus = h.NetStim()
    stimulus.start = 0.0
    stimulus.number = 1
    stimulus.interval = 1000.0
    stimulus.noise = 0.0
    netcon = h.NetCon(stimulus, synapse)
    netcon.delay = 0.0
    netcon.weight[0] = PEAK_CONDUCTANCE_S * 1e6

    h.dt = DT_MS
    h.secondorder = 0
    h.CVode().active(0)

    time_vector = h.Vector()
    conductance_vector = h.Vector()
    voltage_vectors = {}
    time_vector.record(h._ref_t)
    conductance_vector.record(synapse._ref_g)
    for key, segment in record_segments.items():
        vector = h.Vector()
        vector.record(segment._ref_v)
        voltage_vectors[key] = vector

    h.finitialize(ELEAK_MV)
    for _ in range(round(DURATION_MS / DT_MS)):
        h.fadvance()

    # Copy the hoc data so record vectors can be released after this run.
    time_ms = np.asarray(time_vector, dtype=float).copy()
    conductance_s = np.asarray(conductance_vector, dtype=float).copy() * 1e-6
    recorded_voltage_v = {
        key: np.asarray(vector, dtype=float).copy() * 1e-3
        for key, vector in voltage_vectors.items()
    }

    voltage = {}
    for node_id, site in sites.items():
        nearest_v = recorded_voltage_v[site["nearest_key"]]
        left_v = recorded_voltage_v[site["left_key"]]
        right_v = recorded_voltage_v[site["right_key"]]
        weight = site["weight"]
        interp_v = left_v + weight * (right_v - left_v)
        interp_area = (
            site["left_area_um2"]
            + weight * (
                site["right_area_um2"] - site["left_area_um2"]
            )
        )
        site["interpolated_area_um2"] = float(interp_area)
        voltage[node_id] = {
            "nearest_v": nearest_v,
            "interpolated_v": interp_v,
            "readout_shift_v": interp_v - nearest_v,
        }

    return {
        "time_ms": time_ms,
        "conductance_s": conductance_s,
        "voltage": voltage,
        "sites": sites,
        "segment_count": sum(section.nseg for section in sections),
    }


def run_amsn_mesh(morphology, frequency_hz):
    sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=AMSN_MAX_SEGMENT_LENGTH_UM,
        max_electrotonic_length=AMSN_MAX_ELECTROTONIC_LENGTH,
        reference_frequency_hz=frequency_hz,
        preserve_node_ids=PROTECTED_IDS,
    )
    tree = sectioned.tree
    mapping = sectioned.swc_node_to_compartment
    indices = {
        node_id: tree.index[mapping[node_id]]
        for node_id in PROBE_IDS
    }
    synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )
    source_index = indices[SOURCE_ID]

    def conductance_fn(time_s):
        values = np.zeros(tree.n_compartments, dtype=float)
        values[source_index] = synapse.conductance_at(time_s)
        return values

    trace = tree.simulate_synaptic(
        duration_s=DURATION_S,
        dt_s=DT_S,
        synaptic_conductance_fn=conductance_fn,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
        initial_voltage_v=ELEAK_MV * 1e-3,
    )
    voltage_v = {
        node_id: trace.voltage_v[:, indices[node_id]].copy()
        for node_id in PROBE_IDS
    }
    area_um2 = {
        node_id: float(tree.area_m2[indices[node_id]] * 1e12)
        for node_id in PROBE_IDS
    }
    return {
        "compartments": tree.n_compartments,
        "sections": sectioned.section_count,
        "max_edge_um": max(sectioned.edge_arc_length_m.values()) * 1e6,
        "max_electrotonic": max(sectioned.edge_electrotonic_length.values()),
        "time_ms": trace.time_s.copy() * 1e3,
        "voltage_v": voltage_v,
        "area_um2": area_um2,
    }


def compute_metrics(reference_mV, candidate_mV, time_ms):
    error = candidate_mV - reference_mV
    absolute = np.abs(error)
    peak_ref = int(np.argmax(reference_mV))
    peak_candidate = int(np.argmax(candidate_mV))
    mask = np.abs(reference_mV) >= RELATIVE_FLOORS_MV[0]
    relative = (
        100.0 * absolute[mask] / np.abs(reference_mV[mask])
        if np.any(mask) else np.asarray([], dtype=float)
    )
    result = {
        "n_relative": int(np.sum(mask)),
        "max_abs_mV": float(np.max(absolute)),
        "rms_mV": float(np.sqrt(np.mean(error * error))),
        "max_relative_pct": float(np.max(relative)) if relative.size else 0.0,
        "peak_reference_mV": float(reference_mV[peak_ref]),
        "peak_candidate_mV": float(candidate_mV[peak_candidate]),
        "peak_reference_time_ms": float(time_ms[peak_ref]),
        "peak_candidate_time_ms": float(time_ms[peak_candidate]),
    }
    for floor in RELATIVE_FLOORS_MV:
        floor_mask = np.abs(reference_mV) >= floor
        result[f"relative_ge_{floor:g}mV_pct"] = (
            float(np.max(
                100.0 * absolute[floor_mask]
                / np.abs(reference_mV[floor_mask])
            ))
            if np.any(floor_mask) else float("nan")
        )
    return result


def main() -> None:
    morphology = SWCMorphology.from_file(reference.DATA)
    neuron = run_neuron_reference(morphology)
    time_ms = neuron["time_ms"]

    print("# NEURON segment-centre interpolation and AMSN control-volume area audit")
    print(
        f"# NEURON={neuron_version}; nseg_max={NEURON_MAX_SEGMENT_UM:g}um; "
        f"segments={neuron['segment_count']}; dt={DT_MS:.7f}ms; duration={DURATION_MS:g}ms"
    )
    print(
        f"# AMPA={PEAK_CONDUCTANCE_S*1e9:g}nS; "
        f"tau={TAU_RISE_S*1e3:g}/{TAU_DECAY_S*1e3:g}ms; "
        f"Erev={REVERSAL_POTENTIAL_V*1e3:g}mV"
    )
    for name, node_id in PROBE_ROWS:
        site = neuron["sites"][node_id]
        print(
            f"# site={name}; id={node_id}; section={site['section']}; "
            f"target_x={site['x']:.9f}; left_x={site['left_x']:.9f}; "
            f"right_x={site['right_x']:.9f}; nearest_x={site['nearest_x']:.9f}; "
            f"interp_weight={site['weight']:.9f}; "
            f"mapping_offset={site['total_offset_um']:.6f}um"
        )

    print(
        "reference_frequency_hz,compartments,probe,probe_swc_id,"
        "nearest_mapping_offset_um,interp_weight,nearest_area_um2,"
        "neuron_interpolated_area_um2,amsn_control_area_um2,"
        "amsn_to_neuron_area_ratio,"
        "nearest_max_abs_error_mV,nearest_rms_error_mV,"
        "interpolated_max_abs_error_mV,interpolated_rms_error_mV,"
        "neuron_interp_readout_shift_max_abs_mV,"
        "neuron_interp_readout_shift_rms_mV,"
        "interpolated_error_at_0.25ms_mV"
    )

    mesh_runs = {}
    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        mesh = run_amsn_mesh(morphology, frequency_hz)
        np.testing.assert_allclose(
            mesh["time_ms"], time_ms, rtol=0.0, atol=1e-9
        )
        mesh_runs[frequency_hz] = mesh
        for probe_name, node_id in PROBE_ROWS:
            site = neuron["sites"][node_id]
            nearest_ref = (
                neuron["voltage"][node_id]["nearest_v"] - ELEAK_MV * 1e-3
            ) * 1e3
            interp_ref = (
                neuron["voltage"][node_id]["interpolated_v"] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_ref = (
                mesh["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            nearest = compute_metrics(nearest_ref, amsn_ref, time_ms)
            interpolated = compute_metrics(interp_ref, amsn_ref, time_ms)
            shift = compute_metrics(nearest_ref, interp_ref, time_ms)
            neuron_area = site["interpolated_area_um2"]
            amsn_area = mesh["area_um2"][node_id]
            print(
                f"{frequency_hz:.6f},{mesh['compartments']},"
                f"{probe_name},{node_id},{site['total_offset_um']:.9f},"
                f"{site['weight']:.9f},{site['nearest_area_um2']:.9f},"
                f"{neuron_area:.9f},{amsn_area:.9f},"
                f"{amsn_area/max(neuron_area,1e-30):.9f},"
                f"{nearest['max_abs_mV']:.12f},{nearest['rms_mV']:.12f},"
                f"{interpolated['max_abs_mV']:.12f},"
                f"{interpolated['rms_mV']:.12f},"
                f"{shift['max_abs_mV']:.12f},{shift['rms_mV']:.12f},"
                f"{interpolated['error_at_0.25ms_mV'] if 'error_at_0.25ms_mV' in interpolated else (amsn_ref[int(round(0.25/DT_MS))]-interp_ref[int(round(0.25/DT_MS))]):.12f}"
            )

    print()
    print(
        "reference_frequency_hz,compartments,time_ms,probe,probe_swc_id,"
        "neuron_nearest_dv_mV,neuron_interpolated_dv_mV,amsn_dv_mV,"
        "nearest_error_mV,interpolated_error_mV,neuron_area_interp_um2,"
        "amsn_control_area_um2"
    )
    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        mesh = mesh_runs[frequency_hz]
        for probe_name, node_id in PROBE_ROWS:
            site = neuron["sites"][node_id]
            nearest_v = (
                neuron["voltage"][node_id]["nearest_v"] - ELEAK_MV * 1e-3
            ) * 1e3
            interpolated_v = (
                neuron["voltage"][node_id]["interpolated_v"] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_v = (
                mesh["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            for i, t_ms in enumerate(time_ms):
                print(
                    f"{frequency_hz:.6f},{mesh['compartments']},"
                    f"{t_ms:.7f},{probe_name},{node_id},"
                    f"{nearest_v[i]:.12f},{interpolated_v[i]:.12f},"
                    f"{amsn_v[i]:.12f},{amsn_v[i]-nearest_v[i]:.12f},"
                    f"{amsn_v[i]-interpolated_v[i]:.12f},"
                    f"{site['interpolated_area_um2']:.9f},"
                    f"{mesh['area_um2'][node_id]:.9f}"
                )


if __name__ == "__main__":
    main()
