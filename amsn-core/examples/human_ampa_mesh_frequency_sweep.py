"""High-frequency spatial-mesh sensitivity for a fast AMPA-like event.

A single basal-dendrite input is applied to one fixed human SWC morphology.
NEURON 9.0.2 is the fixed reference; only the AMSN sectioned-mesh reference
frequency is varied. The mesh protects the same SWC source/probe nodes at
every frequency. A fixed small dt separates spatial error from time-step
error as much as this controlled comparison permits.

This is a sensitivity/convergence experiment, not a biological parameter fit.
"""
from __future__ import annotations

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
MESH_FREQUENCIES_HZ = (100.0, 250.0, 500.0, 1000.0, 2000.0)
MAX_SEGMENT_LENGTH_UM = 100.0
MAX_ELECTROTONIC_LENGTH = 0.1

SOURCE_ID = 3784  # basal q75
PROBE_ROWS = (
    ("basal_q75_source", SOURCE_ID),
    ("soma", 1),
    ("basal_q90", 3814),
)
PROBE_IDS = tuple(node_id for _, node_id in PROBE_ROWS)
PRESERVE_IDS = set(PROBE_IDS)

ELEAK_MV = -65.0
PEAK_CONDUCTANCE_S = 0.8e-9
TAU_RISE_S = 0.0002
TAU_DECAY_S = 0.002
REVERSAL_POTENTIAL_V = 0.0
RELATIVE_VOLTAGE_FLOOR_MV = 0.02
REPORT_TIMES_MS = (0.1, 0.25, 0.5, 1.0, 2.0, 5.0)


def build_neuron_reference():
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {section.name(): section for section in sections}

    segments = {}
    offsets = {}
    for node_id in PRESERVE_IDS:
        segment, total, geometry, centre, section_name, normalized = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        segments[node_id] = segment
        offsets[node_id] = {
            "total_um": total,
            "geometry_um": geometry,
            "centre_um": centre,
            "section": section_name,
            "x": normalized,
        }

    synapse = h.Exp2Syn(segments[SOURCE_ID])
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
    for node_id, segment in segments.items():
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
        "morphology": morphology,
        "sections": sections,
        "segments": segments,
        "offsets": offsets,
        "time_s": time_s,
        "voltage_v": voltage_v,
        "conductance_s": conductance_s,
        "stimulus": stimulus,
        "synapse": synapse,
        "netcon": netcon,
    }


def run_amsn_mesh(morphology, frequency_hz):
    sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=MAX_SEGMENT_LENGTH_UM,
        max_electrotonic_length=MAX_ELECTROTONIC_LENGTH,
        reference_frequency_hz=frequency_hz,
        preserve_node_ids=PRESERVE_IDS,
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
    return sectioned, synapse, trace.time_s, voltage_v


def metrics(reference_dv_mV, candidate_dv_mV, time_ms):
    error = candidate_dv_mV - reference_dv_mV
    absolute = np.abs(error)
    mask = np.abs(reference_dv_mV) >= RELATIVE_VOLTAGE_FLOOR_MV
    relative = (
        100.0 * absolute[mask] / np.abs(reference_dv_mV[mask])
        if np.any(mask) else np.asarray([], dtype=float)
    )
    index_025 = int(round(0.25 / DT_MS))
    ref_peak_index = int(np.argmax(reference_dv_mV))
    candidate_peak_index = int(np.argmax(candidate_dv_mV))
    return {
        "n_relative": int(np.sum(mask)),
        "max_abs_mV": float(np.max(absolute)),
        "rms_mV": float(np.sqrt(np.mean(error * error))),
        "max_relative_pct": (
            float(np.max(relative)) if relative.size else 0.0
        ),
        "error_at_025_ms_mV": float(error[index_025]),
        "reference_peak_mV": float(reference_dv_mV[ref_peak_index]),
        "candidate_peak_mV": float(candidate_dv_mV[candidate_peak_index]),
        "reference_peak_time_ms": float(time_ms[ref_peak_index]),
        "candidate_peak_time_ms": float(time_ms[candidate_peak_index]),
    }


def main() -> None:
    reference_run = build_neuron_reference()
    morphology = reference_run["morphology"]
    neuron_time_s = reference_run["time_s"]
    neuron_time_ms = neuron_time_s * 1e3
    neuron_voltage_v = reference_run["voltage_v"]
    neuron_conductance_s = reference_run["conductance_s"]

    expected_steps = round(DURATION_S / DT_S)
    if len(neuron_time_s) != expected_steps + 1:
        raise RuntimeError(
            f"NEURON returned {len(neuron_time_s)} samples; "
            f"expected {expected_steps + 1}"
        )

    print("# AMSN fast-AMPA spatial mesh frequency sensitivity")
    print(f"# NEURON={neuron_version}; morphology=NMO_290988; source_SW C_id={SOURCE_ID}")
    print(
        f"# dt={DT_MS:.6f}ms duration={DURATION_MS:.3f}ms "
        f"AMPA_peak={PEAK_CONDUCTANCE_S*1e9:.6f}nS "
        f"tau_rise={TAU_RISE_S*1e3:.6f}ms tau_decay={TAU_DECAY_S*1e3:.6f}ms"
    )
    print(
        f"# NEURON_segments={sum(section.nseg for section in reference_run['sections'])}; "
        f"AMSN_max_segment={MAX_SEGMENT_LENGTH_UM:g}um; "
        f"max_d_lambda={MAX_ELECTROTONIC_LENGTH:g}"
    )
    print("# NEURON reference locations (segment-centre mapping offsets):")
    for name, node_id in PROBE_ROWS:
        offset = reference_run["offsets"][node_id]
        print(
            f"# site={name}; swc_id={node_id}; section={offset['section']}; "
            f"x={offset['x']:.8f}; total_offset={offset['total_um']:.6f}um; "
            f"geometry_offset={offset['geometry_um']:.6f}um; "
            f"segment_centre_offset={offset['centre_um']:.6f}um"
        )

    print(
        "reference_frequency_hz,compartments,sections,max_edge_um,"
        "max_electrotonic_length,probe,probe_swc_id,n_relative,"
        "max_abs_error_mV,rms_error_mV,max_relative_error_pct,"
        "error_at_0.25ms_mV,neuron_peak_mV,amsn_peak_mV,"
        "neuron_peak_time_ms,amsn_peak_time_ms"
    )

    print(
        "reference_frequency_hz,compartments,time_ms,probe,probe_swc_id,"
        "neuron_source_dv_mV,amsn_source_dv_mV,"
        "neuron_probe_dv_mV,amsn_probe_dv_mV,voltage_error_mV,"
        "neuron_g_nS,amsn_g_aligned_nS,amsn_g_same_time_nS,"
        "neuron_transfer_ratio,amsn_transfer_ratio"
    )

    for frequency_hz in MESH_FREQUENCIES_HZ:
        sectioned, synapse, amsn_time_s, amsn_voltage_v = run_amsn_mesh(
            morphology, frequency_hz
        )
        amsn_time_ms = amsn_time_s * 1e3
        np.testing.assert_allclose(
            amsn_time_s,
            neuron_time_s,
            rtol=0.0,
            atol=1e-12,
            err_msg=f"time grid mismatch at {frequency_hz:g} Hz mesh",
        )

        max_edge_um = max(sectioned.edge_arc_length_m.values()) * 1e6
        max_electrotonic = max(sectioned.edge_electrotonic_length.values())
        amsn_source_dv_mV = (
            amsn_voltage_v[SOURCE_ID] - ELEAK_MV * 1e-3
        ) * 1e3
        neuron_source_dv_mV = (
            neuron_voltage_v[SOURCE_ID] - ELEAK_MV * 1e-3
        ) * 1e3

        aligned_kernel_s = np.array([
            synapse.conductance_at(max(0.0, float(t_s) - DT_S))
            for t_s in neuron_time_s
        ])
        same_time_kernel_s = np.array([
            synapse.conductance_at(float(t_s))
            for t_s in neuron_time_s
        ])

        probe_results = {}
        for probe_name, probe_id in PROBE_ROWS:
            neuron_probe_dv_mV = (
                neuron_voltage_v[probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_probe_dv_mV = (
                amsn_voltage_v[probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            result = metrics(
                neuron_probe_dv_mV,
                amsn_probe_dv_mV,
                neuron_time_ms,
            )
            probe_results[probe_id] = result
            print(
                f"{frequency_hz:.6f},{sectioned.tree.n_compartments},"
                f"{sectioned.section_count},{max_edge_um:.9f},"
                f"{max_electrotonic:.9f},{probe_name},{probe_id},"
                f"{result['n_relative']},{result['max_abs_mV']:.12f},"
                f"{result['rms_mV']:.12f},{result['max_relative_pct']:.9f},"
                f"{result['error_at_025_ms_mV']:.12f},"
                f"{result['reference_peak_mV']:.12f},"
                f"{result['candidate_peak_mV']:.12f},"
                f"{result['reference_peak_time_ms']:.6f},"
                f"{result['candidate_peak_time_ms']:.6f}"
            )

        for probe_name, probe_id in PROBE_ROWS:
            neuron_probe_dv_mV = (
                neuron_voltage_v[probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_probe_dv_mV = (
                amsn_voltage_v[probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            neuron_ratio = np.divide(
                neuron_probe_dv_mV,
                neuron_source_dv_mV,
                out=np.full_like(neuron_probe_dv_mV, np.nan),
                where=np.abs(neuron_source_dv_mV) > 1e-12,
            )
            amsn_ratio = np.divide(
                amsn_probe_dv_mV,
                amsn_source_dv_mV,
                out=np.full_like(amsn_probe_dv_mV, np.nan),
                where=np.abs(amsn_source_dv_mV) > 1e-12,
            )
            for index, time_ms in enumerate(neuron_time_ms):
                print(
                    f"{frequency_hz:.6f},{sectioned.tree.n_compartments},"
                    f"{time_ms:.6f},{probe_name},{probe_id},"
                    f"{neuron_source_dv_mV[index]:.12f},"
                    f"{amsn_source_dv_mV[index]:.12f},"
                    f"{neuron_probe_dv_mV[index]:.12f},"
                    f"{amsn_probe_dv_mV[index]:.12f},"
                    f"{amsn_probe_dv_mV[index]-neuron_probe_dv_mV[index]:.12f},"
                    f"{neuron_conductance_s[index]*1e9:.12f},"
                    f"{aligned_kernel_s[index]*1e9:.12f},"
                    f"{same_time_kernel_s[index]*1e9:.12f},"
                    f"{neuron_ratio[index]:.12f},{amsn_ratio[index]:.12f}"
                )


if __name__ == "__main__":
    main()
