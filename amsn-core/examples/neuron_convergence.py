"""NEURON timestep and spatial-resolution convergence for the human passive cable.

This experiment separates temporal integration error from spatial discretization
error in the independent reference simulator. It reuses the same standardized
SWC and the exact source/probe anatomical node IDs as the cross-validation test.
"""
from __future__ import annotations

from math import ceil, sqrt
from pathlib import Path

import numpy as np
from neuron import h

import neuron_cross_validation as reference


MAX_SEGMENT_UMS = (5.0, 2.5)
DT_MS_VALUES = (0.025, 0.0125)
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
REFERENCE_CONFIG = (2.5, 0.0125)


def main() -> None:
    morphology = reference.SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    section_by_name = {sec.name(): sec for sec in sections}

    # Resolve the exact anatomical nodes once. Their NEURON segment centres
    # are recalculated after each nseg change.
    all_ids = {node_id for _, node_id in SOURCE_ROWS + PROBE_ROWS}
    resolved = {}
    for node_id in all_ids:
        node = morphology.nodes[node_id]
        imported_segment, total_error, geometry_error, centre_error, name, x = (
            reference.locate_neuron_segment(reader, section_by_name, node)
        )
        resolved[node_id] = (name, x, total_error, geometry_error, centre_error)

    output_rows = []
    deflections: dict[tuple[float, float, str, int, str, int, float], float] = {}
    previous_clamps = []
    total_configs = len(MAX_SEGMENT_UMS) * len(DT_MS_VALUES)

    print("# NEURON timestep/spatial convergence; version=" + str(__import__("neuron").__version__))
    print("# same partial human morphology NMO_290988; passive parameters Ri=.7ohm*m Rm=1ohm*m^2 Cm=.01F/m^2 Eleak=-65mV")
    print("# 10pA source current; fixed-step CVode off; sample times in ms")
    print(f"# sources={len(SOURCE_ROWS)}; probes={len(PROBE_ROWS)}; time_points={len(TIMES_MS)}; configurations={total_configs}")
    header = (
        "max_segment_um,dt_ms,neuron_segments,sections,total_area_um2,"
        "source,source_swc_id,probe,probe_swc_id,time_ms,"
        "source_deflection_mV,probe_deflection_mV,transfer_ratio,"
        "source_mapping_offset_um,probe_mapping_offset_um"
    )
    print(header)

    for max_segment_um in MAX_SEGMENT_UMS:
        for sec in sections:
            nseg = max(1, ceil(sec.L / max_segment_um))
            if nseg % 2 == 0:
                nseg += 1
            sec.nseg = nseg
        neuron_segment_count = sum(sec.nseg for sec in sections)
        neuron_area_um2 = sum(
            segment.area() for sec in sections for segment in sec
        )

        mapped_segments = {}
        mapping_offsets = {}
        for node_id in all_ids:
            node = morphology.nodes[node_id]
            segment, total_error, geometry_error, centre_error, name, x = (
                reference.locate_neuron_segment(reader, section_by_name, node)
            )
            mapped_segments[node_id] = segment
            mapping_offsets[node_id] = total_error

        for dt_ms in DT_MS_VALUES:
            h.dt = dt_ms
            h.steps_per_ms = 1.0 / dt_ms
            h.CVode().active(0)
            h.tstop = max(TIMES_MS)

            for source_name, source_id in SOURCE_ROWS:
                for previous in previous_clamps:
                    previous.amp = 0.0
                clamp = h.IClamp(mapped_segments[source_id])
                clamp.delay = 0.0
                clamp.dur = max(TIMES_MS) + 10.0
                clamp.amp = INJECTED_P_A / 1000.0
                previous_clamps.append(clamp)

                h.finitialize(ELEAK_MV)
                sample_values: dict[int, dict[float, float]] = {
                    probe_id: {} for _, probe_id in PROBE_ROWS
                }
                source_values: dict[float, float] = {}

                for time_ms in TIMES_MS:
                    h.continuerun(time_ms)
                    source_values[time_ms] = (
                        float(mapped_segments[source_id].v) - ELEAK_MV
                    )
                    for _, probe_id in PROBE_ROWS:
                        sample_values[probe_id][time_ms] = (
                            float(mapped_segments[probe_id].v) - ELEAK_MV
                        )

                clamp.amp = 0.0
                for probe_name, probe_id in PROBE_ROWS:
                    for time_ms in TIMES_MS:
                        source_delta = source_values[time_ms]
                        probe_delta = sample_values[probe_id][time_ms]
                        ratio = (
                            probe_delta / source_delta
                            if abs(source_delta) > 1e-15 else float("nan")
                        )
                        row = (
                            max_segment_um, dt_ms, neuron_segment_count,
                            len(sections), neuron_area_um2,
                            source_name, source_id, probe_name, probe_id,
                            time_ms, source_delta, probe_delta, ratio,
                            mapping_offsets[source_id], mapping_offsets[probe_id],
                        )
                        output_rows.append(row)
                        deflections[
                            (max_segment_um, dt_ms, source_name, source_id,
                             probe_name, probe_id, time_ms)
                        ] = probe_delta
                        print(
                            f"{max_segment_um:g},{dt_ms:g},{neuron_segment_count},"
                            f"{len(sections)},{neuron_area_um2:.9f},"
                            f"{source_name},{source_id},{probe_name},{probe_id},"
                            f"{time_ms:g},{source_delta:.9f},{probe_delta:.9f},"
                            f"{ratio:.9f},{mapping_offsets[source_id]:.6f},"
                            f"{mapping_offsets[probe_id]:.6f}"
                        )

    ref_cap, ref_dt = REFERENCE_CONFIG
    ref_keys = [
        (source_name, source_id, probe_name, probe_id, time_ms)
        for source_name, source_id in SOURCE_ROWS
        for probe_name, probe_id in PROBE_ROWS
        for time_ms in TIMES_MS
    ]
    reference_values = {
        key: deflections[(ref_cap, ref_dt, *key)]
        for key in ref_keys
    }

    print("# convergence-summary vs max_segment=2.5um, dt=0.0125ms")
    print("max_segment_um,dt_ms,neuron_segments,max_abs_error_mV,rms_error_mV,max_relative_error_pct_for_abs_ref_ge_0.05mV")
    for max_segment_um in MAX_SEGMENT_UMS:
        for dt_ms in DT_MS_VALUES:
            errors = []
            relative = []
            for key in ref_keys:
                value = deflections[(max_segment_um, dt_ms, *key)]
                baseline = reference_values[key]
                errors.append(abs(value - baseline))
                if abs(baseline) >= 0.05:
                    relative.append(100.0 * abs(value-baseline) / abs(baseline))
            neuron_segment_count = next(
                row[2] for row in output_rows
                if row[0] == max_segment_um and row[1] == dt_ms
            )
            rms = sqrt(sum(value*value for value in errors) / len(errors))
            print(
                f"{max_segment_um:g},{dt_ms:g},{neuron_segment_count},"
                f"{max(errors):.9f},{rms:.9f},"
                f"{max(relative) if relative else 0.0:.9f}"
            )


if __name__ == "__main__":
    main()
