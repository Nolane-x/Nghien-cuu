"""Spatial-floor sweep for fast AMPA with a fine NEURON reference.

NEURON is fixed at 0.5-um maximum section length and dt=0.0015625 ms.
Only the AMSN sectioned-mesh reference frequency changes (2,000-6,000 Hz).
The same protected source/probe SWC nodes, passive parameters and AMPA event
are used for every mesh.

The purpose is to determine whether the ~0.00385-mV RMS q90 cross-engine
difference from the temporal sweep is reduced by further AMSN spatial
refinement. This is a numerical representation study, not biological
validation and not proof that the NEURON grid is exact.
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
AMSN_REFERENCE_FREQUENCIES_HZ = (2000.0, 3000.0, 4000.0, 6000.0)
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
RELATIVE_FLOORS_MV = (0.02, 0.1, 0.2, 0.5, 1.0)


def configure_neuron_nseg(sections) -> None:
    for section in sections:
        nseg = max(1, ceil(section.L / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()


def run_neuron_reference(morphology):
    reader, sections = reference.import_swc_with_neuron()
    configure_neuron_nseg(sections)
    section_by_name = {section.name(): section for section in sections}

    segments = {}
    offsets = {}
    for node_id in PROTECTED_IDS:
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

    # Detach results from hoc Vector storage; the next finitialize() in a
    # separate trial would otherwise reuse registered record vectors.
    time_ms = np.asarray(time_vector, dtype=float).copy()
    conductance_s = np.asarray(conductance_vector, dtype=float).copy() * 1e-6
    voltage_v = {
        node_id: np.asarray(vector, dtype=float).copy() * 1e-3
        for node_id, vector in voltage_vectors.items()
    }
    return {
        "time_ms": time_ms,
        "conductance_s": conductance_s,
        "voltage_v": voltage_v,
        "offsets": offsets,
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
    # Copy just the protected traces and let the full compartment matrix go.
    voltage_v = {
        node_id: trace.voltage_v[:, indices[node_id]].copy()
        for node_id in PROBE_IDS
    }
    return sectioned, trace.time_s.copy() * 1e3, voltage_v, synapse


def compute_metrics(reference_mV, candidate_mV, time_ms):
    error = candidate_mV - reference_mV
    absolute = np.abs(error)
    peak_reference = int(np.argmax(reference_mV))
    peak_candidate = int(np.argmax(candidate_mV))
    mask = np.abs(reference_mV) >= RELATIVE_FLOORS_MV[0]
    relative = (
        100.0 * absolute[mask] / np.abs(reference_mV[mask])
        if np.any(mask) else np.asarray([], dtype=float)
    )
    values = {
        "n_relative": int(np.sum(mask)),
        "max_abs_mV": float(np.max(absolute)),
        "rms_mV": float(np.sqrt(np.mean(error * error))),
        "max_relative_pct": (
            float(np.max(relative)) if relative.size else 0.0
        ),
        "reference_peak_mV": float(reference_mV[peak_reference]),
        "candidate_peak_mV": float(candidate_mV[peak_candidate]),
        "reference_peak_time_ms": float(time_ms[peak_reference]),
        "candidate_peak_time_ms": float(time_ms[peak_candidate]),
        "error_at_0_25ms_mV": float(
            error[int(round(0.25 / DT_MS))]
        ),
    }
    for floor in RELATIVE_FLOORS_MV:
        floor_mask = np.abs(reference_mV) >= floor
        values[f"relative_ge_{floor:g}mV_pct"] = (
            float(np.max(
                100.0 * absolute[floor_mask]
                / np.abs(reference_mV[floor_mask])
            ))
            if np.any(floor_mask) else float("nan")
        )
    return values


def main() -> None:
    morphology = SWCMorphology.from_file(reference.DATA)
    neuron = run_neuron_reference(morphology)
    neuron_time_ms = neuron["time_ms"]
    neuron_voltage = neuron["voltage_v"]
    neuron_g = neuron["conductance_s"]

    expected_samples = round(DURATION_S / DT_S) + 1
    if len(neuron_time_ms) != expected_samples:
        raise RuntimeError(
            f"NEURON sample count {len(neuron_time_ms)} != {expected_samples}"
        )

    analytic = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )
    aligned_g = np.array([
        analytic.conductance_at(max(0.0, t_ms*1e-3 - DT_S))
        for t_ms in neuron_time_ms
    ])
    g_error_nS = (aligned_g - neuron_g) * 1e9

    print("# AMSN spatial-floor sweep at finest tested temporal resolution")
    print(
        f"# NEURON={neuron_version}; dt={DT_MS:.7f}ms; duration={DURATION_MS:g}ms; "
        f"NEURON_max_segment={NEURON_MAX_SEGMENT_UM:g}um; "
        f"NEURON_segments={neuron['segment_count']}"
    )
    print(
        f"# AMPA_peak={PEAK_CONDUCTANCE_S*1e9:g}nS; "
        f"tau={TAU_RISE_S*1e3:g}/{TAU_DECAY_S*1e3:g}ms; "
        f"Erev={REVERSAL_POTENTIAL_V*1e3:g}mV"
    )
    print(
        f"# NEURON aligned kernel max absolute error={np.max(np.abs(g_error_nS)):.12g}nS; "
        f"RMS={np.sqrt(np.mean(g_error_nS*g_error_nS)):.12g}nS"
    )
    for name, node_id in PROBE_ROWS:
        offset = neuron["offsets"][node_id]
        print(
            f"# site={name}; id={node_id}; offset={offset['total_um']:.6f}um; "
            f"geometry={offset['geometry_um']:.6f}um; "
            f"centre={offset['centre_um']:.6f}um; "
            f"section={offset['section']}; x={offset['x']:.8f}"
        )

    # Run every AMSN mesh once. Store only protected traces and scalar metadata,
    # not the full compartment-by-time matrix.
    mesh_runs = {}
    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        sectioned, amsn_time_ms, amsn_voltage, _synapse = run_amsn_mesh(
            morphology, frequency_hz
        )
        np.testing.assert_allclose(
            amsn_time_ms,
            neuron_time_ms,
            rtol=0.0,
            atol=1e-9,
            err_msg=f"NEURON/AMSN time grid mismatch at {frequency_hz:g} Hz",
        )
        mesh_runs[frequency_hz] = {
            "compartments": sectioned.tree.n_compartments,
            "sections": sectioned.section_count,
            "max_edge_um": max(sectioned.edge_arc_length_m.values()) * 1e6,
            "max_electrotonic": max(sectioned.edge_electrotonic_length.values()),
            "voltage_v": amsn_voltage,
        }

    finest_frequency = max(AMSN_REFERENCE_FREQUENCIES_HZ)
    finest_mesh = mesh_runs[finest_frequency]

    print(
        "reference_frequency_hz,compartments,sections,max_edge_um,"
        "max_electrotonic_length,probe,probe_swc_id,n_relative,"
        "max_abs_error_mV,rms_error_mV,max_relative_error_pct,"
        "relative_ge_0.1mV_pct,relative_ge_0.2mV_pct,"
        "relative_ge_0.5mV_pct,relative_ge_1mV_pct,"
        "error_at_0.25ms_mV,neuron_peak_mV,amsn_peak_mV,"
        "neuron_peak_time_ms,amsn_peak_time_ms,"
        "amsn_vs_finest_max_abs_mV,amsn_vs_finest_rms_mV"
    )

    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        mesh = mesh_runs[frequency_hz]
        for probe_name, node_id in PROBE_ROWS:
            neuron_dv_mV = (
                neuron_voltage[node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_dv_mV = (
                mesh["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            finest_dv_mV = (
                finest_mesh["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            cross = compute_metrics(
                neuron_dv_mV, amsn_dv_mV, neuron_time_ms
            )
            mesh_self = compute_metrics(
                finest_dv_mV, amsn_dv_mV, neuron_time_ms
            )
            print(
                f"{frequency_hz:.6f},{mesh['compartments']},"
                f"{mesh['sections']},{mesh['max_edge_um']:.9f},"
                f"{mesh['max_electrotonic']:.9f},{probe_name},{node_id},"
                f"{cross['n_relative']},{cross['max_abs_mV']:.12f},"
                f"{cross['rms_mV']:.12f},{cross['max_relative_pct']:.9f},"
                f"{cross['relative_ge_0.1mV_pct']:.9f},"
                f"{cross['relative_ge_0.2mV_pct']:.9f},"
                f"{cross['relative_ge_0.5mV_pct']:.9f},"
                f"{cross['relative_ge_1mV_pct']:.9f},"
                f"{cross['error_at_0_25ms_mV']:.12f},"
                f"{cross['reference_peak_mV']:.12f},"
                f"{cross['candidate_peak_mV']:.12f},"
                f"{cross['reference_peak_time_ms']:.7f},"
                f"{cross['candidate_peak_time_ms']:.7f},"
                f"{mesh_self['max_abs_mV']:.12f},"
                f"{mesh_self['rms_mV']:.12f}"
            )

    print()
    print(
        "reference_frequency_hz,compartments,time_ms,probe,probe_swc_id,"
        "neuron_dv_mV,amsn_dv_mV,error_mV,neuron_g_nS,amsn_g_aligned_nS"
    )
    for frequency_hz in AMSN_REFERENCE_FREQUENCIES_HZ:
        mesh = mesh_runs[frequency_hz]
        for probe_name, node_id in PROBE_ROWS:
            neuron_dv_mV = (
                neuron_voltage[node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_dv_mV = (
                mesh["voltage_v"][node_id] - ELEAK_MV * 1e-3
            ) * 1e3
            for i, time_ms in enumerate(neuron_time_ms):
                print(
                    f"{frequency_hz:.6f},{mesh['compartments']},"
                    f"{time_ms:.7f},{probe_name},{node_id},"
                    f"{neuron_dv_mV[i]:.12f},{amsn_dv_mV[i]:.12f},"
                    f"{amsn_dv_mV[i]-neuron_dv_mV[i]:.12f},"
                    f"{neuron_g[i]*1e9:.12f},{aligned_g[i]*1e9:.12f}"
                )


if __name__ == "__main__":
    main()
