"""Temporal convergence of fast AMPA on a refined human dendritic cable.

Spatial reference is held fixed:
- AMSN sectioned mesh at 2,000-Hz reference frequency.
- NEURON imported morphology with maximum segment length 0.5 um.

Only the fixed timestep changes. At each dt both engines use the same
morphology, protected SWC nodes, passive parameters, AMPA event and event-time
alignment. The finest dt is a numerical reference for self-convergence, not
experimental ground truth.
"""
from __future__ import annotations

from math import ceil

import numpy as np
from neuron import h, __version__ as neuron_version

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree
from amsn.synapses import DoubleExponentialSynapse


DT_VALUES_MS = (0.025, 0.0125, 0.00625, 0.003125, 0.0015625)
DURATION_MS = 5.0
NEURON_MAX_SEGMENT_UM = 0.5
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
RELATIVE_FLOORS_MV = (0.02, 0.1, 0.2, 0.5, 1.0)


def configure_neuron_nseg(sections) -> None:
    for section in sections:
        nseg = max(1, ceil(section.L / NEURON_MAX_SEGMENT_UM))
        if nseg % 2 == 0:
            nseg += 1
        section.nseg = nseg
        for segment in section:
            _ = segment.area()


def build_fixed_models():
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {section.name(): section for section in sections}
    configure_neuron_nseg(sections)

    neuron_segments = {}
    mapping_offsets = {}
    for node_id in PROTECTED_IDS:
        segment, total, geometry, centre, section_name, normalized = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        neuron_segments[node_id] = segment
        mapping_offsets[node_id] = {
            "total_um": total,
            "geometry_um": geometry,
            "centre_um": centre,
            "section": section_name,
            "x": normalized,
        }

    amsn_sectioned = to_sectioned_cable_tree(
        morphology,
        max_segment_length_um=AMSN_MAX_SEGMENT_LENGTH_UM,
        max_electrotonic_length=AMSN_MAX_ELECTROTONIC_LENGTH,
        reference_frequency_hz=AMSN_REFERENCE_FREQUENCY_HZ,
        preserve_node_ids=PROTECTED_IDS,
    )
    tree = amsn_sectioned.tree
    mapping = amsn_sectioned.swc_node_to_compartment
    amsn_indices = {
        node_id: tree.index[mapping[node_id]]
        for node_id in PROBE_IDS
    }
    neuron_segments_count = sum(section.nseg for section in sections)

    return (
        morphology,
        sections,
        neuron_segments,
        mapping_offsets,
        amsn_sectioned,
        tree,
        amsn_indices,
        neuron_segments_count,
    )


def run_neuron(dt_ms, neuron_segments, previous_inputs):
    for old_stimulus, old_synapse, old_netcon in previous_inputs:
        old_stimulus.number = 0
        old_netcon.weight[0] = 0.0

    synapse = h.Exp2Syn(neuron_segments[SOURCE_ID])
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

    h.dt = dt_ms
    h.secondorder = 0
    h.CVode().active(0)

    time_vector = h.Vector()
    conductance_vector = h.Vector()
    voltage_vectors = {}
    time_vector.record(h._ref_t)
    conductance_vector.record(synapse._ref_g)
    for node_id, segment in neuron_segments.items():
        vector = h.Vector()
        vector.record(segment._ref_v)
        voltage_vectors[node_id] = vector

    h.finitialize(ELEAK_MV)
    for _ in range(round(DURATION_MS / dt_ms)):
        h.fadvance()

    return {
        "time_ms": np.asarray(time_vector, dtype=float),
        "voltage_v": {
            node_id: np.asarray(vector, dtype=float) * 1e-3
            for node_id, vector in voltage_vectors.items()
        },
        "conductance_s": np.asarray(conductance_vector, dtype=float) * 1e-6,
        # Keep recorders/vectors live until their arrays have been consumed.
        "recorders": (time_vector, conductance_vector, voltage_vectors),
    }


def run_amsn(dt_ms, tree, synapse, amsn_indices):
    dt_s = dt_ms * 1e-3

    def conductance_fn(time_s):
        values = np.zeros(tree.n_compartments, dtype=float)
        values[amsn_indices[SOURCE_ID]] = synapse.conductance_at(time_s)
        return values

    trace = tree.simulate_synaptic(
        duration_s=DURATION_MS * 1e-3,
        dt_s=dt_s,
        synaptic_conductance_fn=conductance_fn,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
        initial_voltage_v=ELEAK_MV * 1e-3,
    )
    return {
        "time_ms": trace.time_s * 1e3,
        "voltage_v": {
            node_id: trace.voltage_v[:, amsn_indices[node_id]]
            for node_id in PROBE_IDS
        },
    }


def error_metrics(reference_mV, candidate_mV, dt_ms: float):
    error = candidate_mV - reference_mV
    mask = np.abs(reference_mV) >= RELATIVE_FLOORS_MV[0]
    relative = (
        100.0 * np.abs(error[mask]) / np.abs(reference_mV[mask])
        if np.any(mask) else np.asarray([], dtype=float)
    )
    peak_ref = int(np.argmax(reference_mV))
    peak_candidate = int(np.argmax(candidate_mV))
    metrics = {
        "n_relative": int(np.sum(mask)),
        "max_abs_mV": float(np.max(np.abs(error))),
        "rms_mV": float(np.sqrt(np.mean(error * error))),
        "max_relative_pct": float(np.max(relative)) if relative.size else 0.0,
        "ref_peak_mV": float(reference_mV[peak_ref]),
        "candidate_peak_mV": float(candidate_mV[peak_candidate]),
        "ref_peak_time_ms": float(peak_ref * dt_ms),
        "candidate_peak_time_ms": float(peak_candidate * dt_ms),
    }
    for floor in RELATIVE_FLOORS_MV:
        mask_floor = np.abs(reference_mV) >= floor
        if np.any(mask_floor):
            metrics[f"max_relative_at_{floor:g}mV_pct"] = float(
                np.max(
                    100.0 * np.abs(error[mask_floor])
                    / np.abs(reference_mV[mask_floor])
                )
            )
        else:
            metrics[f"max_relative_at_{floor:g}mV_pct"] = float("nan")
    return metrics


def compare_to_finest(current, finest, probe_id):
    # The current (coarser) step must be an integer multiple of the finest dt.
    # E.g. 0.025 ms / 0.0015625 ms = 16, so sample every 16th fine point.
    ratio_float = current["dt_ms"] / finest["dt_ms"]
    ratio = round(ratio_float)
    if ratio < 1 or not np.isclose(
        ratio_float, ratio, rtol=0.0, atol=1e-12
    ):
        raise RuntimeError(
            f"non-nested timestep ratio {ratio_float:g} "
            f"for dt={current['dt_ms']:g} ms and finest={finest['dt_ms']:g} ms"
        )
    current_time = np.asarray(current["time_ms"], dtype=float)
    finest_time = np.asarray(finest["time_ms"], dtype=float)[::ratio]
    if len(current_time) != len(finest_time):
        raise RuntimeError(
            "temporal grids could not be nested for convergence: "
            f"coarse={len(current_time)}, fine_subsample={len(finest_time)}, "
            f"ratio={ratio}"
        )
    np.testing.assert_allclose(
        current_time,
        finest_time,
        rtol=0.0,
        atol=1e-9,
        err_msg="coarse and subsampled finest time grids differ",
    )
    current_voltage = current["voltage_v"][probe_id]
    finest_voltage = finest["voltage_v"][probe_id][::ratio]
    return error_metrics(
        (finest_voltage - ELEAK_MV * 1e-3) * 1e3,
        (current_voltage - ELEAK_MV * 1e-3) * 1e3,
        current["dt_ms"],
    )


def main() -> None:
    (
        morphology,
        sections,
        neuron_segments,
        offsets,
        sectioned,
        tree,
        amsn_indices,
        neuron_segment_count,
    ) = build_fixed_models()
    amsn_synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )

    print("# fast-AMPA temporal convergence on fixed refined spatial meshes")
    print(
        f"# NEURON={neuron_version}; NEURON_max_segment={NEURON_MAX_SEGMENT_UM:g}um; "
        f"NEURON_segments={neuron_segment_count}; "
        f"AMSN_compartments={tree.n_compartments}; "
        f"AMSN_reference_frequency={AMSN_REFERENCE_FREQUENCY_HZ:g}Hz"
    )
    print(
        f"# source={SOURCE_ID}; probes={PROBE_IDS}; "
        f"AMPA={PEAK_CONDUCTANCE_S*1e9:g}nS; "
        f"tau={TAU_RISE_S*1e3:g}/{TAU_DECAY_S*1e3:g}ms; "
        f"duration={DURATION_MS:g}ms"
    )
    for name, node_id in PROBE_ROWS:
        item = offsets[node_id]
        print(
            f"# site={name}; id={node_id}; offset={item['total_um']:.6f}um; "
            f"geometry={item['geometry_um']:.6f}um; "
            f"centre={item['centre_um']:.6f}um; "
            f"section={item['section']}; x={item['x']:.8f}"
        )

    previous_inputs = []
    neuron_runs = {}
    amsn_runs = {}
    for dt_ms in DT_VALUES_MS:
        neuron_runs[dt_ms] = run_neuron(
            dt_ms, neuron_segments, previous_inputs
        )
        amsn_runs[dt_ms] = run_amsn(
            dt_ms, tree, amsn_synapse, amsn_indices
        )
        np.testing.assert_allclose(
            neuron_runs[dt_ms]["time_ms"],
            amsn_runs[dt_ms]["time_ms"],
            rtol=0.0,
            atol=1e-9,
            err_msg=f"NEURON/AMSN time-grid mismatch at {dt_ms:g}ms",
        )

    finest_dt = min(DT_VALUES_MS)
    print(
        "dt_ms,probe,probe_swc_id,n_relative,max_abs_error_mV,rms_error_mV,"
        "max_relative_error_pct,relative_ge_0.1mV_pct,relative_ge_0.2mV_pct,"
        "relative_ge_0.5mV_pct,relative_ge_1mV_pct,"
        "neuron_peak_mV,amsn_peak_mV,neuron_peak_time_ms,amsn_peak_time_ms,"
        "neuron_vs_finest_max_abs_mV,neuron_vs_finest_rms_mV,"
        "amsn_vs_finest_max_abs_mV,amsn_vs_finest_rms_mV"
    )
    for dt_ms in DT_VALUES_MS:
        neuron_run = neuron_runs[dt_ms]
        amsn_run = amsn_runs[dt_ms]
        for probe_name, probe_id in PROBE_ROWS:
            neuron_dv = (
                neuron_run["voltage_v"][probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_dv = (
                amsn_run["voltage_v"][probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            cross = error_metrics(neuron_dv, amsn_dv, dt_ms)
            neuron_self = compare_to_finest(neuron_run | {"dt_ms": dt_ms}, neuron_runs[finest_dt] | {"dt_ms": finest_dt}, probe_id)
            amsn_self = compare_to_finest(amsn_run | {"dt_ms": dt_ms}, amsn_runs[finest_dt] | {"dt_ms": finest_dt}, probe_id)
            print(
                f"{dt_ms:.7f},{probe_name},{probe_id},{cross['n_relative']},"
                f"{cross['max_abs_mV']:.12f},{cross['rms_mV']:.12f},"
                f"{cross['max_relative_pct']:.9f},"
                f"{cross['max_relative_at_0.1mV_pct']:.9f},"
                f"{cross['max_relative_at_0.2mV_pct']:.9f},"
                f"{cross['max_relative_at_0.5mV_pct']:.9f},"
                f"{cross['max_relative_at_1mV_pct']:.9f},"
                f"{cross['ref_peak_mV']:.12f},{cross['candidate_peak_mV']:.12f},"
                f"{cross['ref_peak_time_ms']:.7f},"
                f"{cross['candidate_peak_time_ms']:.7f},"
                f"{neuron_self['max_abs_mV']:.12f},{neuron_self['rms_mV']:.12f},"
                f"{amsn_self['max_abs_mV']:.12f},{amsn_self['rms_mV']:.12f}"
            )

    print()
    print(
        "dt_ms,time_ms,probe,probe_swc_id,neuron_dv_mV,amsn_dv_mV,"
        "error_mV,neuron_g_nS,amsn_g_aligned_nS"
    )
    for dt_ms in DT_VALUES_MS:
        neuron_run = neuron_runs[dt_ms]
        amsn_run = amsn_runs[dt_ms]
        dt_s = dt_ms * 1e-3
        kernel = DoubleExponentialSynapse(
            onset_s=0.0,
            peak_conductance_s=PEAK_CONDUCTANCE_S,
            tau_rise_s=TAU_RISE_S,
            tau_decay_s=TAU_DECAY_S,
            reversal_potential_v=REVERSAL_POTENTIAL_V,
        )
        aligned_g = np.array([
            kernel.conductance_at(max(0.0, t_ms*1e-3 - dt_s))
            for t_ms in neuron_run["time_ms"]
        ])
        neuron_g = neuron_run["conductance_s"]
        for probe_name, probe_id in PROBE_ROWS:
            neuron_dv = (
                neuron_run["voltage_v"][probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            amsn_dv = (
                amsn_run["voltage_v"][probe_id] - ELEAK_MV * 1e-3
            ) * 1e3
            for i, time_ms in enumerate(neuron_run["time_ms"]):
                print(
                    f"{dt_ms:.7f},{time_ms:.7f},{probe_name},{probe_id},"
                    f"{neuron_dv[i]:.12f},{amsn_dv[i]:.12f},"
                    f"{amsn_dv[i]-neuron_dv[i]:.12f},"
                    f"{neuron_g[i]*1e9:.12f},{aligned_g[i]*1e9:.12f}"
                )


if __name__ == "__main__":
    main()
