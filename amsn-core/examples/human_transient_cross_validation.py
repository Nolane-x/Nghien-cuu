"""Passive transient pulse/step comparison: AMSN sectioned cable vs NEURON 9.0.2.

The same standardized human SWC, Import3D-compatible electrical topology,
passive parameters, source/probe nodes and current stimuli are used in both
engines. AMSN is run on the 690-compartment section-reduced cable to keep the
CI memory footprint small. The full 8,893-compartment AMSN cable has already
been cross-validated against NEURON for steady-state DC responses.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
from neuron import h

import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology
from amsn.sectioned import to_sectioned_cable_tree


DT_MS = 0.025
DT_S = DT_MS * 1e-3
TIMES_MS = (1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 250.0)
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
INJECTED_P_A = 10.0
ELEAK_MV = -65.0
DURATION_S = 0.25
PULSE_DURATION_S = 0.005


def make_amsn_current_fn(tree, source_name: str, protocol: str):
    source_index = tree.index[source_name]

    def current_fn(time_s: float) -> np.ndarray:
        current = np.zeros(tree.n_compartments, dtype=float)
        active = protocol == "step" or time_s < PULSE_DURATION_S
        if active:
            current[source_index] = INJECTED_P_A * 1e-12
        return current

    return current_fn


def extract_amsn_trace(tree, mapping, source_id, probe_ids, protocol):
    """Run one sectioned AMSN transient and retain only requested samples."""
    source_name = mapping[source_id]
    current_fn = make_amsn_current_fn(tree, source_name, protocol)
    trace = tree.simulate_passive(
        duration_s=DURATION_S,
        dt_s=DT_S,
        current_fn=current_fn,
        initial_voltage_v=tree.parameters.e_leak_v,
    )

    result = {}
    for time_ms in TIMES_MS:
        time_index = round((time_ms * 1e-3) / DT_S)
        source_delta_mV = (
            trace.voltage_v[time_index, tree.index[source_name]]
            - tree.parameters.e_leak_v
        ) * 1e3
        for probe_id in probe_ids:
            probe_name = mapping[probe_id]
            probe_delta_mV = (
                trace.voltage_v[time_index, tree.index[probe_name]]
                - tree.parameters.e_leak_v
            ) * 1e3
            ratio = (
                probe_delta_mV / source_delta_mV
                if abs(source_delta_mV) > 1e-15 else float("nan")
            )
            result[(probe_id, time_ms)] = (
                source_delta_mV, probe_delta_mV, ratio
            )

    del trace
    gc.collect()
    return result


def extract_neuron_trace(
    source_segment, probe_segments, previous_clamps, protocol
):
    """Run one NEURON transient with the same fixed-step stimulus."""
    for previous in previous_clamps:
        previous.amp = 0.0

    clamp = h.IClamp(source_segment)
    clamp.delay = 0.0
    clamp.dur = PULSE_DURATION_S * 1e3 if protocol == "pulse" else 300.0
    clamp.amp = INJECTED_P_A / 1000.0  # NEURON current units are nA.
    previous_clamps.append(clamp)

    h.dt = DT_MS
    h.steps_per_ms = 1.0 / DT_MS
    h.secondorder = 0
    h.CVode().active(0)
    h.tstop = max(TIMES_MS)
    h.finitialize(ELEAK_MV)

    result = {}
    for time_ms in TIMES_MS:
        h.continuerun(time_ms)
        source_delta_mV = float(source_segment.v) - ELEAK_MV
        for probe_id, segment in probe_segments.items():
            probe_delta_mV = float(segment.v) - ELEAK_MV
            ratio = (
                probe_delta_mV / source_delta_mV
                if abs(source_delta_mV) > 1e-15 else float("nan")
            )
            result[(probe_id, time_ms)] = (
                source_delta_mV, probe_delta_mV, ratio
            )

    clamp.amp = 0.0
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

    # Build only the compact AMSN transient tree. The full tree's DC behaviour
    # is already validated separately against NEURON.
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
            f"Expected compact AMSN sectioned cable, got {tree.n_compartments} compartments"
        )
    if any(mapping[node_id] != f"swc_{node_id}" for node_id in protected):
        raise RuntimeError("A protected source/probe SWC node was not retained exactly")

    # Use Import3D's own point-to-section mapping for the matching NEURON sites.
    neuron_segments = {}
    site_offsets = {}
    for node_id in protected:
        segment, total, geometry, centre, sec_name, x = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        neuron_segments[node_id] = segment
        site_offsets[node_id] = (total, geometry, centre, sec_name, x)

    print("# NEURON 9.0.2; Import3D SWC; record=NMO_290988")
    print("# Same passive parameters: Ri=.7ohm*m Rm=1ohm*m^2 Cm=.01F/m^2 Eleak=-65mV")
    print("# NEURON fixed dt=.025ms secondorder=0; AMSN backward-Euler dt=.025ms")
    print("# pulse protocol: 10pA for 5ms; step protocol: 10pA for full 300ms")
    print(f"# NEURON sections={len(sections)}; NEURON segments={sum(sec.nseg for sec in sections)}")
    print(f"# AMSN sectioned compartments={tree.n_compartments}; sections={sectioned.section_count}")
    print("# All seven source/probe nodes are exact protected SWC vertices in AMSN.")
    for name, node_id in sources + probes:
        total, geometry, centre, sec_name, x = site_offsets[node_id]
        print(
            f"# site {name} swc_id={node_id} section={sec_name} x={x:.8f} "
            f"mapping={total:.6f}um geometry={geometry:.6f}um "
            f"segment_centre={centre:.6f}um"
        )

    print(
        "protocol,source,source_swc_id,probe,probe_swc_id,time_ms,"
        "neuron_source_deflection_mV,amsn_sectioned_source_deflection_mV,"
        "neuron_probe_deflection_mV,amsn_sectioned_probe_deflection_mV,"
        "neuron_ratio,amsn_sectioned_ratio,"
        "source_mapping_offset_um,probe_mapping_offset_um"
    )

    previous_clamps = []
    comparison = {"pulse": {}, "step": {}}
    for protocol in ("pulse", "step"):
        for source_name, source_id in sources:
            neuron_source = neuron_segments[source_id]
            neuron_probe_segments = {
                probe_id: neuron_segments[probe_id] for probe_id in probe_ids
            }
            neuron_values = extract_neuron_trace(
                neuron_source, neuron_probe_segments,
                previous_clamps, protocol
            )
            amsn_values = extract_amsn_trace(
                tree, mapping, source_id, probe_ids, protocol
            )

            for probe_name, probe_id in probes:
                for time_ms in TIMES_MS:
                    n_source, n_probe, n_ratio = neuron_values[(probe_id, time_ms)]
                    a_source, a_probe, a_ratio = amsn_values[(probe_id, time_ms)]
                    source_offset = site_offsets[source_id][0]
                    probe_offset = site_offsets[probe_id][0]
                    comparison[protocol][
                        (source_id, probe_id, time_ms)
                    ] = (n_source, a_source, n_probe, a_probe, n_ratio, a_ratio)
                    print(
                        f"{protocol},{source_name},{source_id},{probe_name},{probe_id},"
                        f"{time_ms:g},{n_source:.9f},{a_source:.9f},"
                        f"{n_probe:.9f},{a_probe:.9f},"
                        f"{n_ratio:.9f},{a_ratio:.9f},"
                        f"{source_offset:.6f},{probe_offset:.6f}"
                    )

            del neuron_values, amsn_values
            gc.collect()

    print("# transient-summary")
    print("# source/probe relative errors include rows with |NEURON deflection| >= 0.02mV")
    print("# transfer-ratio absolute errors include rows with |NEURON source deflection| >= 0.02mV")
    print("# transfer-ratio relative errors additionally require |NEURON ratio| >= 0.05")
    print(
        "protocol,observable,n_abs_samples,n_relative_samples,"
        "max_abs_error,rms_abs_error,max_relative_error_pct"
    )
    for protocol in ("pulse", "step"):
        values_by_metric = {"source": [], "probe": [], "ratio": []}
        relative_by_metric = {"source": [], "probe": [], "ratio": []}
        for values in comparison[protocol].values():
            n_source, a_source, n_probe, a_probe, n_ratio, a_ratio = values
            values_by_metric["source"].append((n_source, a_source))
            values_by_metric["probe"].append((n_probe, a_probe))
            if abs(n_source) >= 0.02:
                values_by_metric["ratio"].append((n_ratio, a_ratio))

            if abs(n_source) >= 0.02:
                relative_by_metric["source"].append(
                    100.0 * abs(a_source-n_source) / abs(n_source)
                )
            if abs(n_probe) >= 0.02:
                relative_by_metric["probe"].append(
                    100.0 * abs(a_probe-n_probe) / abs(n_probe)
                )
            if abs(n_source) >= 0.02 and abs(n_ratio) >= 0.05:
                relative_by_metric["ratio"].append(
                    100.0 * abs(a_ratio-n_ratio) / abs(n_ratio)
                )

        for key in ("source", "probe", "ratio"):
            pairs = values_by_metric[key]
            errors = np.asarray(
                [abs(actual-expected) for expected, actual in pairs],
                dtype=float,
            )
            relative = relative_by_metric[key]
            print(
                f"{protocol},{key},{len(errors)},{len(relative)},"
                f"{np.max(errors):.9f},"
                f"{np.sqrt(np.mean(errors**2)):.9f},"
                f"{max(relative) if relative else 0.0:.9f}"
            )


if __name__ == "__main__":
    main()
