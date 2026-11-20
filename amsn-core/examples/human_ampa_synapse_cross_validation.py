"""AMPA-like double-exponential conductance cross-validation: AMSN vs NEURON.

NEURON Exp2Syn and AMSN DoubleExponentialSynapse use the same peak conductance,
rise/decay time constants and reversal potential. One event is delivered at
each of the three anatomical source sites; voltages are recorded at the same
five probes and fixed times.
"""
from __future__ import annotations

import gc

import numpy as np
from neuron import h

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree
from amsn.synapses import DoubleExponentialSynapse


DT_MS = 0.025
DT_S = DT_MS * 1e-3
TIMES_MS = (0.25, 0.5, 0.75, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 250.0)
SOURCE_ROWS = (
    ("soma", 1),
    ("basal_q75", 3784),
    ("apical_q75", 5920),
)
PROBE_ROWS = (
    ("soma", 1),
    ("basal_q50", 3355),
    ("basal_q90", 3814),
    ("apical_q50", 6897),
    ("apical_q90", 5164),
)
ELEAK_MV = -65.0
PEAK_CONDUCTANCE_S = 0.8e-9
TAU_RISE_S = 0.0002
TAU_DECAY_S = 0.002
REVERSAL_POTENTIAL_V = 0.0
DURATION_S = 0.25


def extract_amsn_synaptic_trace(tree, mapping, source_id, probe_ids, synapse):
    """Run one AMSN double-exponential conductance event."""
    synapse_index = tree.index[mapping[source_id]]

    def conductance_fn(time_s: float) -> np.ndarray:
        values = np.zeros(tree.n_compartments, dtype=float)
        values[synapse_index] = synapse.conductance_at(time_s)
        return values

    trace = tree.simulate_synaptic(
        duration_s=DURATION_S,
        dt_s=DT_S,
        synaptic_conductance_fn=conductance_fn,
        reversal_potential_v=synapse.reversal_potential_v,
        initial_voltage_v=tree.parameters.e_leak_v,
    )
    result = {}
    for time_ms in TIMES_MS:
        index = round(time_ms / DT_MS)
        source_delta = (
            trace.voltage_v[index, synapse_index]
            - tree.parameters.e_leak_v
        ) * 1e3
        for probe_id in probe_ids:
            probe_index = tree.index[mapping[probe_id]]
            probe_delta = (
                trace.voltage_v[index, probe_index]
                - tree.parameters.e_leak_v
            ) * 1e3
            ratio = (
                probe_delta / source_delta
                if abs(source_delta) > 1e-15 else float("nan")
            )
            result[(probe_id, time_ms)] = (source_delta, probe_delta, ratio)
    del trace
    gc.collect()
    return result


def extract_neuron_exp2syn_trace(
    source_segment,
    probe_segments,
    previous_inputs,
):
    """Run one NEURON Exp2Syn event with peak-normalized NetCon weight."""
    for previous_stim, previous_synapse, previous_netcon in previous_inputs:
        previous_stim.number = 0
        previous_netcon.weight[0] = 0.0

    synapse = h.Exp2Syn(source_segment)
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
    # Exp2Syn normalizes its kinetic waveform to unit peak. NetCon weight is
    # in uS, so convert the target peak from S to uS.
    netcon.weight[0] = PEAK_CONDUCTANCE_S * 1e6
    previous_inputs.append((stimulus, synapse, netcon))

    h.dt = DT_MS
    h.steps_per_ms = 1.0 / DT_MS
    h.secondorder = 0
    h.CVode().active(0)
    h.tstop = max(TIMES_MS)
    h.finitialize(ELEAK_MV)

    result = {}
    for time_ms in TIMES_MS:
        h.continuerun(time_ms)
        source_delta = float(source_segment.v) - ELEAK_MV
        for probe_id, segment in probe_segments.items():
            probe_delta = float(segment.v) - ELEAK_MV
            ratio = (
                probe_delta / source_delta
                if abs(source_delta) > 1e-15 else float("nan")
            )
            result[(probe_id, time_ms)] = (source_delta, probe_delta, ratio)
    return result


def main() -> None:
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {sec.name(): sec for sec in sections}
    sources = list(SOURCE_ROWS)
    probes = list(PROBE_ROWS)
    source_ids = [node_id for _, node_id in sources]
    probe_ids = [node_id for _, node_id in probes]
    protected = set(source_ids + probe_ids)

    sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=100.0,
        max_electrotonic_length=0.1,
        reference_frequency_hz=100.0,
        preserve_node_ids=protected,
    )
    tree = sectioned.tree
    mapping = sectioned.swc_node_to_compartment
    if tree.n_compartments >= 1000:
        raise RuntimeError(
            f"Expected compact AMSN cable, got {tree.n_compartments} compartments"
        )

    neuron_segments = {}
    offsets = {}
    for node_id in protected:
        segment, total, geometry, centre, section_name, x = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        neuron_segments[node_id] = segment
        offsets[node_id] = (total, geometry, centre, section_name, x)

    print("# NEURON 9.0.2 Exp2Syn vs AMSN DoubleExponentialSynapse")
    print("# record=NMO_290988; three-point soma and eight wire attachments normalized")
    print("# passive: Ri=.7ohm*m Rm=1ohm*m^2 Cm=.01F/m^2 Eleak=-65mV")
    print(
        f"# AMPA-like test kernel: peak={PEAK_CONDUCTANCE_S*1e9:.3f}nS "
        f"tau_rise={TAU_RISE_S*1e3:.3f}ms tau_decay={TAU_DECAY_S*1e3:.3f}ms "
        f"Erev={REVERSAL_POTENTIAL_V*1e3:.3f}mV onset=0ms"
    )
    print(
        f"# dt={DT_MS:.4f}ms NEURON_segments={sum(sec.nseg for sec in sections)} "
        f"AMSN_compartments={tree.n_compartments}"
    )
    for name, node_id in sources + probes:
        total, geometry, centre, sec_name, x = offsets[node_id]
        print(
            f"# site {name} swc_id={node_id} section={sec_name} x={x:.8f} "
            f"map={total:.6f}um geometry={geometry:.6f}um centre={centre:.6f}um"
        )
    print(
        "source,source_swc_id,probe,probe_swc_id,time_ms,"
        "neuron_source_deflection_mV,amsn_source_deflection_mV,"
        "neuron_probe_deflection_mV,amsn_probe_deflection_mV,"
        "neuron_ratio,amsn_ratio,source_mapping_offset_um,probe_mapping_offset_um"
    )

    synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )
    previous_inputs = []
    comparison = {}
    for source_name, source_id in sources:
        neuron_probe_segments = {
            probe_id: neuron_segments[probe_id] for probe_id in probe_ids
        }
        neuron_values = extract_neuron_exp2syn_trace(
            neuron_segments[source_id],
            neuron_probe_segments,
            previous_inputs,
        )
        amsn_values = extract_amsn_synaptic_trace(
            tree, mapping, source_id, probe_ids, synapse
        )

        for probe_name, probe_id in probes:
            for time_ms in TIMES_MS:
                n_source, n_probe, n_ratio = neuron_values[(probe_id, time_ms)]
                a_source, a_probe, a_ratio = amsn_values[(probe_id, time_ms)]
                comparison[(source_id, probe_id, time_ms)] = (
                    n_source, a_source, n_probe, a_probe, n_ratio, a_ratio
                )
                print(
                    f"{source_name},{source_id},{probe_name},{probe_id},{time_ms:g},"
                    f"{n_source:.9f},{a_source:.9f},"
                    f"{n_probe:.9f},{a_probe:.9f},"
                    f"{n_ratio:.9f},{a_ratio:.9f},"
                    f"{offsets[source_id][0]:.6f},{offsets[probe_id][0]:.6f}"
                )
        del neuron_values, amsn_values
        gc.collect()

    print("# summary: relative source/probe voltage errors require |NEURON deflection|>=0.02mV")
    print("# ratio absolute errors require |NEURON source deflection|>=0.02mV; relative also requires |NEURON ratio|>=0.05")
    print("observable,n_abs_samples,n_relative_samples,max_abs_error,rms_abs_error,max_relative_error_pct")
    metrics = {"source": [], "probe": [], "ratio": []}
    relative = {"source": [], "probe": [], "ratio": []}
    for values in comparison.values():
        n_source, a_source, n_probe, a_probe, n_ratio, a_ratio = values
        metrics["source"].append((n_source, a_source))
        metrics["probe"].append((n_probe, a_probe))
        if abs(n_source) >= 0.02:
            metrics["ratio"].append((n_ratio, a_ratio))
        if abs(n_source) >= 0.02:
            relative["source"].append(
                100.0*abs(a_source-n_source)/abs(n_source)
            )
        if abs(n_probe) >= 0.02:
            relative["probe"].append(
                100.0*abs(a_probe-n_probe)/abs(n_probe)
            )
        if abs(n_source) >= 0.02 and abs(n_ratio) >= 0.05:
            relative["ratio"].append(
                100.0*abs(a_ratio-n_ratio)/abs(n_ratio)
            )
    for key in ("source", "probe", "ratio"):
        errors = np.asarray(
            [abs(actual-expected) for expected, actual in metrics[key]],
            dtype=float,
        )
        print(
            f"{key},{len(errors)},{len(relative[key])},"
            f"{np.max(errors):.9f},{np.sqrt(np.mean(errors**2)):.9f},"
            f"{max(relative[key]) if relative[key] else 0.0:.9f}"
        )


if __name__ == "__main__":
    main()
