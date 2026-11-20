"""Reference-segment mapping and spatial convergence audit for fast AMPA.

AMSN uses one fixed 2,000-Hz sectioned mesh with protected SWC sites. The
NEURON reference is independently refined by maximum section segment lengths
of 5, 2, 1 and 0.5 um. At each resolution the exact same SWC source/probe nodes,
passive parameters, dt and Exp2Syn event are used.

This experiment separates two contributors that were mixed in the first
frequency sweep:
1. AMSN electrical mesh/coarsening error relative to a fine NEURON cable.
2. NEURON segment-centre sampling/mapping error as its own nseg is refined.

The 0.5-um NEURON result is the finest numerical reference in this experiment,
not experimental truth and not a mathematically exact solution.
"""
from __future__ import annotations

from math import ceil

import numpy as np
from neuron import h, __version__ as neuron_version

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree
from amsn.synapses import DoubleExponentialSynapse


DT_MS = 0.00625
DT_S = DT_MS * 1e-3
DURATION_MS = 5.0
DURATION_S = DURATION_MS * 1e-3
NEURON_MAX_SEGMENT_LENGTHS_UM = (5.0, 2.0, 1.0, 0.5)
AMSN_REFERENCE_FREQUENCY_HZ = 2000.0
AMSN_MAX_SEGMENT_LENGTH_UM = 100.0
AMSN_MAX_ELECTROTONIC_LENGTH = 0.1

SOURCE_ID = 3784  # basal q75
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
RELATIVE_VOLTAGE_FLOOR_MV = 0.02
RELATIVE_FLOORS_MV = (0.02, 0.1, 0.2, 0.5, 1.0)


def configure_neuron_nseg(sections, max_segment_length_um: float) -> None:
    """Refine each imported NEURON section while retaining x=0.5 when possible."""
    for section in sections:
        nseg = max(1, ceil(section.L / max_segment_length_um))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            # Force area refresh after changing nseg before selecting probes.
            _ = segment.area()


def build_amsn_reference(morphology):
    sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=AMSN_MAX_SEGMENT_LENGTH_UM,
        max_electrotonic_length=AMSN_MAX_ELECTROTONIC_LENGTH,
        reference_frequency_hz=AMSN_REFERENCE_FREQUENCY_HZ,
        preserve_node_ids=PROTECTED_IDS,
    )
    tree = sectioned.tree
    mapping = sectioned.swc_node_to_compartment
    synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )
    source_index = tree.index[mapping[SOURCE_ID]]

    def conductance_fn(time_s: float) -> np.ndarray:
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
        node_id: trace.voltage_v[:, tree.index[mapping[node_id]]]
        for node_id in PROBE_IDS
    }
    return sectioned, trace.time_s, voltage_v


def run_neuron_resolution(
    reader,
    sections,
    section_by_name,
    morphology,
    max_segment_length_um: float,
    previous_inputs,
):
    configure_neuron_nseg(sections, max_segment_length_um)
    segment_mapping = {}
    offsets = {}
    for node_id in PROTECTED_IDS:
        segment, total, geometry, centre, section_name, normalized = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        segment_mapping[node_id] = segment
        offsets[node_id] = {
            "total_um": total,
            "geometry_um": geometry,
            "centre_um": centre,
            "section": section_name,
            "x": normalized,
        }

    # Disable earlier trials before reinitializing NEURON's global event queue.
    for old_stimulus, old_synapse, old_netcon in previous_inputs:
        old_stimulus.number = 0
        old_netcon.weight[0] = 0.0

    synapse = h.Exp2Syn(segment_mapping[SOURCE_ID])
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
    previous_inputs.append((stimulus, synapse, netcon))

    h.dt = DT_MS
    h.secondorder = 0
    h.CVode().active(0)

    time_vector = h.Vector()
    conductance_vector = h.Vector()
    voltage_vectors = {}
    time_vector.record(h._ref_t)
    conductance_vector.record(synapse._ref_g)
    for node_id, segment in segment_mapping.items():
        vector = h.Vector()
        vector.record(segment._ref_v)
        voltage_vectors[node_id] = vector

    h.finitialize(ELEAK_MV)
    for _ in range(round(DURATION_MS / DT_MS)):
        h.fadvance()

    time_s = np.asarray(time_vector, dtype=float) * 1e-3
    voltage_v = {
        node_id: np.asarray(vector, dtype=float) * 1e-3
        for node_id, vector in voltage_vectors.items()
    }
    conductance_s = np.asarray(conductance_vector, dtype=float) * 1e-6

    return {
        "time_s": time_s,
        "voltage_v": voltage_v,
        "conductance_s": conductance_s,
        "offsets": offsets,
        "segment_count": sum(section.nseg for section in sections),
    }


def summarize_error(reference_mV, candidate_mV):
    error = candidate_mV - reference_mV
    mask = np.abs(reference_mV) >= RELATIVE_VOLTAGE_FLOOR_MV
    relative = (
        100.0 * np.abs(error[mask]) / np.abs(reference_mV[mask])
        if np.any(mask) else np.asarray([], dtype=float)
    )
    peak_reference = int(np.argmax(reference_mV))
    peak_candidate = int(np.argmax(candidate_mV))
    return {
        "n_relative": int(np.sum(mask)),
        "max_abs_mV": float(np.max(np.abs(error))),
        "rms_mV": float(np.sqrt(np.mean(error * error))),
        "max_relative_pct": (
            float(np.max(relative)) if relative.size else 0.0
        ),
        "peak_reference_mV": float(reference_mV[peak_reference]),
        "peak_candidate_mV": float(candidate_mV[peak_candidate]),
        "peak_reference_time_ms": peak_reference * DT_MS,
        "peak_candidate_time_ms": peak_candidate * DT_MS,
    }


def main() -> None:
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {section.name(): section for section in sections}
    amsn_sectioned, amsn_time_s, amsn_voltage_v = build_amsn_reference(morphology)
    amsn_time_ms = amsn_time_s * 1e3

    print("# NEURON segment-size convergence for one fast AMPA basal input")
    print(
        f"# NEURON={neuron_version}; SWC=NMO_290988; source={SOURCE_ID}; "
        f"dt={DT_MS:.6f}ms; duration={DURATION_MS:.3f}ms"
    )
    print(
        f"# AMSN fixed mesh={amsn_sectioned.tree.n_compartments} compartments; "
        f"reference_frequency={AMSN_REFERENCE_FREQUENCY_HZ:g}Hz; "
        f"max_edge={max(amsn_sectioned.edge_arc_length_m.values())*1e6:.6f}um"
    )
    print(
        f"# AMPA peak={PEAK_CONDUCTANCE_S*1e9:.6f}nS; "
        f"tau={TAU_RISE_S*1e3:.6f}/{TAU_DECAY_S*1e3:.6f}ms; "
        f"Erev={REVERSAL_POTENTIAL_V*1e3:.6f}mV"
    )

    previous_inputs = []
    trials = {}
    print(
        "neuron_max_segment_um,neuron_segments,probe,probe_swc_id,"
        "mapping_offset_um,geometry_offset_um,segment_centre_offset_um,"
        "amsn_vs_neuron_max_abs_mV,amsn_vs_neuron_rms_mV,"
        "amsn_vs_neuron_max_relative_pct,neuron_vs_finest_max_abs_mV,"
        "neuron_vs_finest_rms_mV,neuron_peak_mV,amsn_peak_mV,"
        "neuron_peak_time_ms,amsn_peak_time_ms"
    )
    for max_segment_um in NEURON_MAX_SEGMENT_LENGTHS_UM:
        trial = run_neuron_resolution(
            reader,
            sections,
            section_by_name,
            morphology,
            max_segment_um,
            previous_inputs,
        )
        np.testing.assert_allclose(
            trial["time_s"], amsn_time_s, rtol=0.0, atol=1e-12
        )
        trials[max_segment_um] = trial

    finest = trials[min(NEURON_MAX_SEGMENT_LENGTHS_UM)]
    finest_time_ms = finest["time_s"] * 1e3
    for max_segment_um in NEURON_MAX_SEGMENT_LENGTHS_UM:
        trial = trials[max_segment_um]
        np.testing.assert_allclose(
            trial["time_s"], finest["time_s"],
            rtol=0.0, atol=1e-12,
            err_msg="NEURON segment sweep time grids differ",
        )
        np.testing.assert_allclose(
            trial["time_s"], amsn_time_s,
            rtol=0.0, atol=1e-12,
            err_msg="NEURON and AMSN time grids differ",
        )
        for probe_name, node_id in PROBE_ROWS:
            neuron_dv_mV = (
                trial["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_dv_mV = (
                amsn_voltage_v[node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            finest_dv_mV = (
                finest["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_metrics = summarize_error(neuron_dv_mV, amsn_dv_mV)
            ref_metrics = summarize_error(finest_dv_mV, neuron_dv_mV)
            offsets = trial["offsets"][node_id]
            print(
                f"{max_segment_um:.6f},{trial['segment_count']},"
                f"{probe_name},{node_id},{offsets['total_um']:.9f},"
                f"{offsets['geometry_um']:.9f},{offsets['centre_um']:.9f},"
                f"{amsn_metrics['max_abs_mV']:.12f},"
                f"{amsn_metrics['rms_mV']:.12f},"
                f"{amsn_metrics['max_relative_pct']:.9f},"
                f"{ref_metrics['max_abs_mV']:.12f},"
                f"{ref_metrics['rms_mV']:.12f},"
                f"{amsn_metrics['peak_reference_mV']:.12f},"
                f"{amsn_metrics['peak_candidate_mV']:.12f},"
                f"{amsn_metrics['peak_reference_time_ms']:.6f},"
                f"{amsn_metrics['peak_candidate_time_ms']:.6f}"
            )

    print()
    print(
        "neuron_max_segment_um,neuron_segments,time_ms,probe,probe_swc_id,"
        "neuron_v_mV,amsn_v_mV,voltage_error_mV,neuron_mapping_offset_um"
    )
    for max_segment_um in NEURON_MAX_SEGMENT_LENGTHS_UM:
        trial = trials[max_segment_um]
        for probe_name, node_id in PROBE_ROWS:
            neuron_v_mV = trial["voltage_v"][node_id] * 1e3
            amsn_v_mV = amsn_voltage_v[node_id] * 1e3
            offset_um = trial["offsets"][node_id]["total_um"]
            for index, time_ms in enumerate(finest_time_ms):
                print(
                    f"{max_segment_um:.6f},{trial['segment_count']},"
                    f"{time_ms:.6f},{probe_name},{node_id},"
                    f"{neuron_v_mV[index]:.12f},"
                    f"{amsn_v_mV[index]:.12f},"
                    f"{amsn_v_mV[index]-neuron_v_mV[index]:.12f},"
                    f"{offset_um:.9f}"
                )


if __name__ == "__main__":
    main()
