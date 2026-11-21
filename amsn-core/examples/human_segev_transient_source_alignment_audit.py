"""Compare nearest-centre versus charge-conserving split source placement.

The AMSN source remains at the exact SWC electrical node. NEURON 9.0.2
receives the same rectangular 10 pA pulse in two alternative placements:

1. nearest_segment_centre: one IClamp at the nearest segment centre;
2. weighted_adjacent_centres: two IClamps on the segment centres bracketing
   the exact SWC source arc, with amplitudes (1-w)*I and w*I.

The weighted split conserves total injected current at every active time
sample. It is a discrete source-mapping diagnostic, not asserted to be the
exact continuum point-current solution. Probe voltage is recorded at both
nearest segment centres and a linear interpolation at the exact SWC arc.

This is a native NEURON segment-level comparison against the AMSN
node-centred SWC cable, not the previously validated matched-support
projected admittance operator.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import human_segev_passive_transient_audit as base
import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


SOURCE_MODES = ("nearest_segment_centre", "weighted_adjacent_centres")
PROBE_MODES = (
    ("nearest_segment_centre", "nearest"),
    ("linear_interpolation_at_exact_swc_arc", "interpolated"),
)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    columns = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def run_neuron(
    source_site: dict,
    probes: list[tuple[str, int]],
    sites: dict,
    source_mode: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    if source_mode not in SOURCE_MODES:
        raise ValueError(f"unknown source placement mode: {source_mode}")

    old_secondorder = int(h.secondorder)
    old_dt = float(h.dt)
    clamps = []
    try:
        h.dt = base.DT_MS
        h.steps_per_ms = 1.0 / base.DT_MS
        h.secondorder = 0
        h.CVode().active(0)

        lower = source_site["lower_segment"]
        upper = source_site["upper_segment"]
        nearest = source_site["nearest_segment"]
        upper_weight = float(source_site["interpolation_upper_weight"])
        lower_weight = 1.0 - upper_weight
        if not (0.0 <= upper_weight <= 1.0):
            raise RuntimeError(f"invalid source interpolation weight {upper_weight}")

        if source_mode == "nearest_segment_centre":
            components = [(nearest, 1.0)]
        else:
            same_segment = (
                lower.sec == upper.sec
                and abs(float(lower.x) - float(upper.x)) <= 1e-12
            )
            components = (
                [(lower, 1.0)]
                if same_segment
                else [(seg, weight) for seg, weight in (
                    (lower, lower_weight), (upper, upper_weight)
                ) if weight > 0.0]
            )

        component_rows = []
        for segment, weight in components:
            clamp = h.IClamp(segment)
            clamp.delay = base.PULSE_START_MS
            clamp.dur = base.PULSE_DURATION_MS
            clamp.amp = (base.INJECTED_P_A * weight) / 1000.0
            clamps.append(clamp)
            component_rows.append({
                "section": segment.sec.name(),
                "segment_x": float(segment.x),
                "weight": float(weight),
                "amp_nA": float(clamp.amp),
            })

        total_amp_nA = sum(float(row["amp_nA"]) for row in component_rows)
        if not np.isclose(
            total_amp_nA, base.INJECTED_P_A / 1000.0, rtol=0.0, atol=1e-15
        ):
            raise RuntimeError(
                f"source split current is not conserved: total={total_amp_nA:.12g} nA"
            )

        probe_ids = [node_id for _, node_id in probes]
        nearest_segments = [sites[node_id]["nearest_segment"] for node_id in probe_ids]
        lower_probes = [sites[node_id]["lower_segment"] for node_id in probe_ids]
        upper_probes = [sites[node_id]["upper_segment"] for node_id in probe_ids]
        probe_weights = np.asarray([
            float(sites[node_id]["interpolation_upper_weight"])
            for node_id in probe_ids
        ], dtype=float)

        h.finitialize(base.ELEAK_MV)
        h.fcurrent()
        steps = int(round(base.DURATION_MS / base.DT_MS))
        time_ms = np.empty(steps + 1, dtype=float)
        nearest_trace = np.empty((steps + 1, len(probe_ids)), dtype=float)
        interpolated_trace = np.empty((steps + 1, len(probe_ids)), dtype=float)
        total_current_nA = np.empty(steps + 1, dtype=float)

        def record(row: int) -> None:
            time_ms[row] = float(h.t)
            nearest_trace[row] = [float(segment.v) for segment in nearest_segments]
            v_lower = np.asarray([float(segment.v) for segment in lower_probes])
            v_upper = np.asarray([float(segment.v) for segment in upper_probes])
            interpolated_trace[row] = v_lower * (1.0 - probe_weights) + v_upper * probe_weights
            total_current_nA[row] = sum(float(clamp.i) for clamp in clamps)

        record(0)
        for step in range(steps):
            h.fadvance()
            record(step + 1)

        expected_time = np.linspace(0.0, base.DURATION_MS, steps + 1)
        if not np.allclose(time_ms, expected_time, rtol=0.0, atol=1e-9):
            raise RuntimeError("NEURON transient time grid mismatch")
        if not (
            np.all(np.isfinite(nearest_trace))
            and np.all(np.isfinite(interpolated_trace))
            and np.all(np.isfinite(total_current_nA))
        ):
            raise RuntimeError("non-finite NEURON transient/source-current values")

        # Samples are recorded after each integration interval. Build the
        # expected clamp-current trace from integer step indices so that
        # (2.05 - 0.05) cannot round to 1.999999999999... and misclassify
        # the first pulse sample as being outside the active window.
        start_step = int(round(base.PULSE_START_MS / base.DT_MS))
        stop_step = int(round(
            (base.PULSE_START_MS + base.PULSE_DURATION_MS) / base.DT_MS
        ))
        expected_current = np.zeros_like(time_ms, dtype=float)
        expected_current[start_step + 1:stop_step + 1] = base.INJECTED_P_A / 1000.0
        max_current_error = float(np.max(np.abs(total_current_nA - expected_current)))
        if max_current_error > 1e-12:
            mismatch = np.flatnonzero(np.abs(total_current_nA - expected_current) > 1e-12)
            sample_rows = [
                {
                    "index": int(index),
                    "time_ms": float(time_ms[index]),
                    "actual_current_nA": float(total_current_nA[index]),
                    "expected_current_nA": float(expected_current[index]),
                }
                for index in mismatch[:12]
            ]
            print(
                f"SOURCE_CURRENT_DEBUG mode={source_mode}; "
                f"amp_nA={[float(clamp.amp) for clamp in clamps]}; "
                f"delay_ms={[float(clamp.delay) for clamp in clamps]}; "
                f"dur_ms={[float(clamp.dur) for clamp in clamps]}; "
                f"mismatches={sample_rows}"
            )
            raise RuntimeError(
                f"{source_mode}: total current is not conserved at every sample; "
                f"max error={max_current_error:.12g} nA"
            )

        source_meta = {
            "source_mode": source_mode,
            "source_nearest_segment_x": float(nearest.x),
            "source_lower_segment_x": float(lower.x),
            "source_upper_segment_x": float(upper.x),
            "source_interpolation_upper_weight": upper_weight,
            "source_lower_current_weight": lower_weight,
            "source_upper_current_weight": upper_weight,
            "source_component_count": len(clamps),
            "source_components": ";".join(
                f"{row['section']}@{row['segment_x']:.12g}:{row['weight']:.12g}"
                for row in component_rows
            ),
            "source_total_clamp_amplitude_nA": total_amp_nA,
            "max_total_current_error_nA": max_current_error,
        }
        return time_ms, nearest_trace, interpolated_trace, total_current_nA, source_meta
    finally:
        for clamp in clamps:
            clamp.amp = 0.0
        h.secondorder = old_secondorder
        h.dt = old_dt
        h.steps_per_ms = 1.0 / old_dt


def main() -> None:
    base.configure_reference()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(morphology, reader, sections)
    cable = morphology.to_cable_tree()
    electrical_map = morphology.electrical_node_mapping()
    node_to_name = {
        node_id: f"swc_{electrical_map[node_id]}"
        for node_id in morphology.nodes
    }

    for boundary in (
        base.PULSE_START_MS,
        base.PULSE_START_MS + base.PULSE_DURATION_MS,
        base.DURATION_MS,
    ):
        quotient = boundary / base.DT_MS
        if not np.isclose(quotient, round(quotient), rtol=0.0, atol=1e-10):
            raise ValueError(f"transient boundary {boundary:g} ms is not aligned to dt")

    label = base.MORPHOLOGY_LABEL
    mesh = base.NEURON_MAX_SEGMENT_UM
    prefix = f"{label}_mesh{mesh:g}um_"
    result_dir = Path(__file__).parents[1] / "results"
    trace_path = result_dir / f"{prefix}human_passive_source_alignment_traces_2026-11-21.csv"
    summary_path = result_dir / f"{prefix}human_passive_source_alignment_summary_2026-11-21.csv"

    traces = []
    summaries = []
    max_source_nearest_offset_um = 0.0
    max_source_bracket_width_um = 0.0
    max_time_grid_error_ms = 0.0
    max_total_current_error_nA = 0.0
    expected_samples = int(round(base.DURATION_MS / base.DT_MS)) + 1

    for source_name, source_id in injections:
        source_site = sites[source_id]
        source_index = cable.index[node_to_name[source_id]]
        probe_ids = [node_id for _, node_id in probes]
        probe_indices = [cable.index[node_to_name[node_id]] for node_id in probe_ids]
        amsn_time, amsn_trace = base.simulate_amsn(cable, source_index, probe_indices)

        nearest_offset = float(source_site["nearest_centre_offset_um"])
        max_source_nearest_offset_um = max(max_source_nearest_offset_um, nearest_offset)
        lower = source_site["lower_segment"]
        upper = source_site["upper_segment"]
        bracket_width_um = abs(float(upper.x) - float(lower.x)) * float(source_site["section"].L)
        max_source_bracket_width_um = max(max_source_bracket_width_um, bracket_width_um)

        for source_mode in SOURCE_MODES:
            neuron_time, nearest_trace, interpolated_trace, total_current, source_meta = run_neuron(
                source_site, probes, sites, source_mode
            )
            if not np.allclose(amsn_time, neuron_time, rtol=0.0, atol=1e-9):
                raise RuntimeError("AMSN and NEURON time grids differ")
            max_time_grid_error_ms = max(
                max_time_grid_error_ms,
                float(np.max(np.abs(amsn_time - neuron_time))),
            )
            max_total_current_error_nA = max(
                max_total_current_error_nA,
                float(source_meta["max_total_current_error_nA"]),
            )

            for column, (probe_name, probe_id) in enumerate(probes):
                site = sites[probe_id]
                identity = {
                    "morphology_label": label,
                    "source": source_name,
                    "source_swc_id": source_id,
                    "probe": probe_name,
                    "probe_swc_id": probe_id,
                    "source_section": source_site["section"].name(),
                    "source_exact_swc_x": float(source_site["normalized_x"]),
                    "source_nearest_centre_offset_um": nearest_offset,
                    "source_bracket_width_um": bracket_width_um,
                    "probe_section": site["section"].name(),
                    "probe_exact_swc_x": float(site["normalized_x"]),
                    "probe_nearest_centre_offset_um": float(site["nearest_centre_offset_um"]),
                    "probe_interpolation_upper_weight": float(site["interpolation_upper_weight"]),
                    "neuron_max_segment_um": mesh,
                    "dt_ms": base.DT_MS,
                    "pulse_start_ms": base.PULSE_START_MS,
                    "pulse_duration_ms": base.PULSE_DURATION_MS,
                    "injected_current_pA": base.INJECTED_P_A,
                    "specific_Rm_ohm_m2": base.RM_OHM_M2,
                    "specific_Cm_F_m2": base.CM_F_M2,
                    "Eleak_mV": base.ELEAK_MV,
                    **source_meta,
                }

                for probe_mode, probe_selector in PROBE_MODES:
                    if probe_selector == "nearest":
                        chosen = nearest_trace
                    elif probe_selector == "interpolated":
                        chosen = interpolated_trace
                    else:
                        raise RuntimeError(f"unsupported probe selector: {probe_selector}")
                    metrics = base.waveform_metrics(
                        amsn_time,
                        amsn_trace[:, column],
                        chosen[:, column],
                    )
                    summaries.append({
                        **identity,
                        "probe_readout_mode": probe_mode,
                        **metrics,
                    })

                for sample, time_ms in enumerate(amsn_time):
                    traces.append({
                        **identity,
                        "time_ms": float(time_ms),
                        "amsn_voltage_mV": float(amsn_trace[sample, column]),
                        "neuron_nearest_voltage_mV": float(nearest_trace[sample, column]),
                        "neuron_interpolated_voltage_mV": float(interpolated_trace[sample, column]),
                        "amsn_deflection_mV": float(amsn_trace[sample, column] - base.ELEAK_MV),
                        "neuron_nearest_deflection_mV": float(nearest_trace[sample, column] - base.ELEAK_MV),
                        "neuron_interpolated_deflection_mV": float(interpolated_trace[sample, column] - base.ELEAK_MV),
                        "neuron_total_iclamp_current_nA": float(total_current[sample]),
                    })

    actual_probe_modes = {row["probe_readout_mode"] for row in summaries}
    expected_probe_modes = {mode for mode, _ in PROBE_MODES}
    if actual_probe_modes != expected_probe_modes:
        raise RuntimeError(
            f"probe readout mode labels mismatch: {actual_probe_modes} != {expected_probe_modes}"
        )
    actual_source_modes = {row["source_mode"] for row in summaries}
    if actual_source_modes != set(SOURCE_MODES):
        raise RuntimeError(
            f"source placement mode labels mismatch: {actual_source_modes} != {set(SOURCE_MODES)}"
        )
    expected_summaries = len(injections) * len(probes) * len(SOURCE_MODES) * len(PROBE_MODES)
    expected_traces = len(injections) * len(probes) * len(SOURCE_MODES) * expected_samples
    if len(summaries) != expected_summaries or len(traces) != expected_traces:
        raise RuntimeError(
            f"output row-count mismatch: summary={len(summaries)}/{expected_summaries}, "
            f"trace={len(traces)}/{expected_traces}"
        )

    write_csv(trace_path, traces)
    write_csv(summary_path, summaries)
    max_nrmse = max(float(row["waveform_nrmse_pct_of_neuron_peak"]) for row in summaries)
    max_peak_error = max(float(row["peak_amplitude_error_pct"]) for row in summaries)
    max_abs_error = max(float(row["waveform_max_abs_error_mV"]) for row in summaries)

    print(f"NEURON={neuron.__version__}")
    print(
        f"morphology={label}; mesh_um={mesh:g}; dt_ms={base.DT_MS:g}; "
        f"sections={len(sections)}; segments={sum(section.nseg for section in sections)}"
    )
    print(
        f"source_count={len(injections)}; probe_count={len(probes)}; "
        f"source_modes={len(SOURCE_MODES)}; probe_readout_modes={len(PROBE_MODES)}; "
        f"samples_per_trace={expected_samples}"
    )
    print(
        f"trace_rows={len(traces)}; summary_rows={len(summaries)}; "
        f"max_source_nearest_offset_um={max_source_nearest_offset_um:.12g}; "
        f"max_source_bracket_width_um={max_source_bracket_width_um:.12g}"
    )
    print(
        f"max_time_grid_difference_ms={max_time_grid_error_ms:.12g}; "
        f"max_total_current_conservation_error_nA={max_total_current_error_nA:.12g}"
    )
    print(
        f"waveform_nrmse_max_pct={max_nrmse:.12g}; "
        f"peak_amplitude_error_max_pct={max_peak_error:.12g}; "
        f"waveform_absolute_error_max_mV={max_abs_error:.12g}"
    )
    print(f"trace_csv={trace_path}; bytes={trace_path.stat().st_size}")
    print(f"summary_csv={summary_path}; rows={len(summaries)}")


if __name__ == "__main__":
    main()
