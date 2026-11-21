"""Transient passive step-response comparison for Segev human L2/3 cells.

AMSN's unresampled SWC CableTree and NEURON 9.0.2 Import3D are driven by the
same 10 pA rectangular current pulse. Both solvers use fixed-step fully
implicit backward Euler (dt=0.05 ms). NEURON receives the stimulus at the
nearest segment centre to the exact SWC source arc; the source offset is
reported for every run. Probe traces are read both at the nearest segment
centre and by linear interpolation between adjacent segment centres bracketing
the exact SWC arc coordinate.

This compares the native fine NEURON segment-level transient against AMSN's
node-centred SWC transient. It is not the matched-support projected operator
and not biological validation.
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
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
DT_MS = 0.05
DURATION_MS = 30.0
PULSE_START_MS = 2.0
PULSE_DURATION_MS = 10.0
INJECTED_P_A = 10.0
INJECTED_A = INJECTED_P_A * 1e-12
OUTPUT_PREFIX = os.environ.get("AMSN_TRANSIENT_OUTPUT_PREFIX", "")
MORPHOLOGY_PATH = os.environ.get("AMSN_MORPHOLOGY_PATH")
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")


def configure_reference() -> None:
    if MORPHOLOGY_PATH:
        reference.DATA = Path(MORPHOLOGY_PATH)
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty output CSV: {path}")
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def pulse_is_active(time_ms: float) -> bool:
    return PULSE_START_MS <= time_ms < PULSE_START_MS + PULSE_DURATION_MS


def relative_error_pct(value: float, reference_value: float) -> float:
    return 100.0 * abs(value - reference_value) / max(abs(reference_value), 1e-12)


def waveform_metrics(
    time_ms: np.ndarray,
    amsn_voltage_mV: np.ndarray,
    neuron_voltage_mV: np.ndarray,
) -> dict:
    """Compare voltage deflections around the identical leak reversal."""
    amsn_delta = np.asarray(amsn_voltage_mV, dtype=float) - ELEAK_MV
    neuron_delta = np.asarray(neuron_voltage_mV, dtype=float) - ELEAK_MV
    difference = amsn_delta - neuron_delta
    peak_amsn_index = int(np.argmax(np.abs(amsn_delta)))
    peak_neuron_index = int(np.argmax(np.abs(neuron_delta)))
    peak_amsn = float(amsn_delta[peak_amsn_index])
    peak_neuron = float(neuron_delta[peak_neuron_index])
    rmse = float(np.sqrt(np.mean(difference * difference)))
    scale = max(float(np.max(np.abs(neuron_delta))), 1e-12)
    amsn_auc = float(np.trapz(amsn_delta, x=time_ms))
    neuron_auc = float(np.trapz(neuron_delta, x=time_ms))
    pulse_window = (time_ms >= 10.0) & (time_ms < 12.0)
    recovery_index = int(np.argmin(np.abs(time_ms - DURATION_MS)))
    amsn_late = float(np.mean(amsn_delta[pulse_window]))
    neuron_late = float(np.mean(neuron_delta[pulse_window]))
    return {
        "amsn_peak_deflection_mV": peak_amsn,
        "neuron_peak_deflection_mV": peak_neuron,
        "peak_amplitude_error_pct": relative_error_pct(
            abs(peak_amsn), abs(peak_neuron)
        ),
        "amsn_peak_time_ms": float(time_ms[peak_amsn_index]),
        "neuron_peak_time_ms": float(time_ms[peak_neuron_index]),
        "peak_time_difference_ms": float(
            time_ms[peak_amsn_index] - time_ms[peak_neuron_index]
        ),
        "waveform_rmse_mV": rmse,
        "waveform_max_abs_error_mV": float(np.max(np.abs(difference))),
        "waveform_nrmse_pct_of_neuron_peak": 100.0 * rmse / scale,
        "amsn_signed_auc_mV_ms": amsn_auc,
        "neuron_signed_auc_mV_ms": neuron_auc,
        "auc_error_pct": relative_error_pct(amsn_auc, neuron_auc),
        "amsn_pulse_late_mean_mV": amsn_late,
        "neuron_pulse_late_mean_mV": neuron_late,
        "pulse_late_mean_error_pct": relative_error_pct(amsn_late, neuron_late),
        "amsn_recovery_deflection_at_30ms_mV": float(amsn_delta[recovery_index]),
        "neuron_recovery_deflection_at_30ms_mV": float(neuron_delta[recovery_index]),
    }


def simulate_amsn(tree, source_index: int, probe_indices: list[int]) -> tuple[np.ndarray, np.ndarray]:
    steps_float = DURATION_MS / DT_MS
    steps = int(round(steps_float))
    if not np.isclose(steps * DT_MS, DURATION_MS, rtol=1e-12, atol=1e-12):
        raise RuntimeError("duration is not an integer multiple of dt")
    time_ms = np.linspace(0.0, DURATION_MS, steps + 1)
    voltage = np.full(tree.n_compartments, ELEAK_MV * 1e-3, dtype=float)
    trace = np.empty((steps + 1, len(probe_indices)), dtype=float)
    trace[0] = voltage[probe_indices] * 1000.0
    for step in range(steps):
        now_ms = float(time_ms[step])
        current = np.zeros(tree.n_compartments, dtype=float)
        if pulse_is_active(now_ms):
            current[source_index] = INJECTED_A
        voltage = tree.step_passive(voltage, DT_MS * 1e-3, current)
        trace[step + 1] = voltage[probe_indices] * 1000.0
    return time_ms, trace


def simulate_neuron(
    source_site: dict,
    probes: list[tuple[str, int]],
    sites: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    old_secondorder = float(h.secondorder)
    old_dt = float(h.dt)
    clamp = None
    try:
        h.dt = DT_MS
        h.steps_per_ms = 1.0 / DT_MS
        h.secondorder = 0  # fully implicit backward Euler, like CableTree.step_passive
        h.CVode().active(0)

        source_segment = source_site["nearest_segment"]
        clamp = h.IClamp(source_segment)
        clamp.delay = PULSE_START_MS
        clamp.dur = PULSE_DURATION_MS
        clamp.amp = INJECTED_P_A / 1000.0  # NEURON IClamp amplitude is nA.

        probe_ids = [node_id for _, node_id in probes]
        nearest_segments = [sites[node_id]["nearest_segment"] for node_id in probe_ids]
        lower_segments = [sites[node_id]["lower_segment"] for node_id in probe_ids]
        upper_segments = [sites[node_id]["upper_segment"] for node_id in probe_ids]
        upper_weights = np.asarray([
            float(sites[node_id]["interpolation_upper_weight"])
            for node_id in probe_ids
        ], dtype=float)

        h.finitialize(ELEAK_MV)
        h.fcurrent()
        steps = int(round(DURATION_MS / DT_MS))
        time_ms = np.empty(steps + 1, dtype=float)
        nearest_trace = np.empty((steps + 1, len(probe_ids)), dtype=float)
        interpolated_trace = np.empty((steps + 1, len(probe_ids)), dtype=float)
        clamp_current_nA = np.empty(steps + 1, dtype=float)

        def record(row: int) -> None:
            time_ms[row] = float(h.t)
            nearest_trace[row] = [float(segment.v) for segment in nearest_segments]
            lower = np.asarray([float(segment.v) for segment in lower_segments])
            upper = np.asarray([float(segment.v) for segment in upper_segments])
            interpolated_trace[row] = lower * (1.0 - upper_weights) + upper * upper_weights
            clamp_current_nA[row] = float(clamp.i)

        record(0)
        for step in range(steps):
            h.fadvance()
            record(step + 1)

        expected_time = np.linspace(0.0, DURATION_MS, steps + 1)
        if not np.allclose(time_ms, expected_time, rtol=0.0, atol=1e-9):
            raise RuntimeError("NEURON time samples do not match the requested fixed-step grid")
        if not np.all(np.isfinite(nearest_trace)) or not np.all(np.isfinite(interpolated_trace)):
            raise RuntimeError("NEURON transient contains non-finite voltage samples")
        return time_ms, nearest_trace, interpolated_trace, clamp_current_nA
    finally:
        if clamp is not None:
            clamp.amp = 0.0
        h.secondorder = old_secondorder
        h.dt = old_dt
        h.steps_per_ms = 1.0 / old_dt


def main() -> None:
    configure_reference()
    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(morphology, reader, sections)

    cable = morphology.to_cable_tree()
    electrical_map = morphology.electrical_node_mapping()
    node_to_name = {
        node_id: f"swc_{electrical_map[node_id]}"
        for node_id in morphology.nodes
    }
    source_and_probe_ids = {node_id for _, node_id in injections + probes}
    missing = source_and_probe_ids - set(node_to_name)
    if missing:
        raise RuntimeError(f"source/probe SWC IDs missing from electrical map: {sorted(missing)}")

    prefix = OUTPUT_PREFIX or (
        "" if MORPHOLOGY_LABEL == "NMO_290988" else f"{MORPHOLOGY_LABEL}_"
    )
    results_dir = Path(__file__).parents[1] / "results"
    trace_path = results_dir / f"{prefix}human_passive_transient_traces_2026-11-21.csv"
    summary_path = results_dir / f"{prefix}human_passive_transient_summary_2026-11-21.csv"

    trace_rows: list[dict] = []
    summary_rows: list[dict] = []
    maximum_source_offset_um = 0.0
    maximum_probe_offset_um = 0.0
    max_time_grid_error_ms = 0.0
    total_trace_rows = 0
    current_grid_samples = int(round(DURATION_MS / DT_MS)) + 1

    for source_name, source_id in injections:
        source_site = sites[source_id]
        source_offset = float(source_site["nearest_centre_offset_um"])
        maximum_source_offset_um = max(maximum_source_offset_um, source_offset)
        source_index = cable.index[node_to_name[source_id]]
        probe_ids = [node_id for _, node_id in probes]
        probe_indices = [cable.index[node_to_name[node_id]] for node_id in probe_ids]

        amsn_time, amsn_trace = simulate_amsn(cable, source_index, probe_indices)
        neuron_time, neuron_nearest, neuron_interpolated, clamp_current = simulate_neuron(
            source_site, probes, sites
        )
        if amsn_time.shape != neuron_time.shape:
            raise RuntimeError("AMSN and NEURON transient sample counts differ")
        max_time_grid_error_ms = max(
            max_time_grid_error_ms,
            float(np.max(np.abs(amsn_time - neuron_time))),
        )
        if not np.allclose(amsn_time, neuron_time, rtol=0.0, atol=1e-9):
            raise RuntimeError("AMSN and NEURON time grids are not identical")

        for probe_column, (probe_name, probe_id) in enumerate(probes):
            site = sites[probe_id]
            probe_offset = float(site["nearest_centre_offset_um"])
            maximum_probe_offset_um = max(maximum_probe_offset_um, probe_offset)
            amsn_voltage = amsn_trace[:, probe_column]
            neuron_nearest_voltage = neuron_nearest[:, probe_column]
            neuron_interpolated_voltage = neuron_interpolated[:, probe_column]
            identity = {
                "morphology_label": MORPHOLOGY_LABEL,
                "source": source_name,
                "source_swc_id": source_id,
                "probe": probe_name,
                "probe_swc_id": probe_id,
                "source_section": source_site["section"].name(),
                "source_exact_swc_x": float(source_site["normalized_x"]),
                "source_nearest_centre_offset_um": source_offset,
                "probe_section": site["section"].name(),
                "probe_exact_swc_x": float(site["normalized_x"]),
                "probe_nearest_centre_offset_um": probe_offset,
                "probe_interpolation_upper_weight": float(site["interpolation_upper_weight"]),
                "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                "dt_ms": DT_MS,
                "pulse_start_ms": PULSE_START_MS,
                "pulse_duration_ms": PULSE_DURATION_MS,
                "injected_current_pA": INJECTED_P_A,
                "specific_Rm_ohm_m2": RM_OHM_M2,
                "specific_Cm_F_m2": CM_F_M2,
                "Eleak_mV": ELEAK_MV,
            }
            for mode, neuron_voltage in (
                ("nearest_segment_centre", neuron_nearest_voltage),
                ("linear_interpolation_at_exact_swc_arc", neuron_interpolated_voltage),
            ):
                metrics = waveform_metrics(amsn_time, amsn_voltage, neuron_voltage)
                summary_rows.append({
                    **identity,
                    "probe_readout_mode": mode,
                    **metrics,
                })

            for sample_index, time_ms in enumerate(amsn_time):
                trace_rows.append({
                    **identity,
                    "time_ms": float(time_ms),
                    "amsn_voltage_mV": float(amsn_voltage[sample_index]),
                    "neuron_nearest_voltage_mV": float(neuron_nearest_voltage[sample_index]),
                    "neuron_interpolated_voltage_mV": float(neuron_interpolated_voltage[sample_index]),
                    "amsn_deflection_mV": float(amsn_voltage[sample_index] - ELEAK_MV),
                    "neuron_nearest_deflection_mV": float(neuron_nearest_voltage[sample_index] - ELEAK_MV),
                    "neuron_interpolated_deflection_mV": float(neuron_interpolated_voltage[sample_index] - ELEAK_MV),
                    "neuron_iclamp_current_nA": float(clamp_current[sample_index]),
                    "amsn_injected_current_pA": (
                        INJECTED_P_A
                        if pulse_is_active(max(0.0, float(time_ms) - DT_MS))
                        else 0.0
                    ),
                })
                total_trace_rows += 1

    expected_summary_rows = len(injections) * len(probes) * 2
    expected_trace_rows = len(injections) * len(probes) * current_grid_samples
    if len(summary_rows) != expected_summary_rows:
        raise RuntimeError(f"expected {expected_summary_rows} summary rows, got {len(summary_rows)}")
    if total_trace_rows != expected_trace_rows:
        raise RuntimeError(f"expected {expected_trace_rows} trace rows, got {total_trace_rows}")
    if maximum_source_offset_um > NEURON_MAX_SEGMENT_UM / 2.0 + 1e-6:
        raise RuntimeError(
            f"source segment-centre offset exceeds half mesh cap: {maximum_source_offset_um:.12g} um"
        )
    if maximum_probe_offset_um > NEURON_MAX_SEGMENT_UM / 2.0 + 1e-6:
        raise RuntimeError(
            f"probe segment-centre offset exceeds half mesh cap: {maximum_probe_offset_um:.12g} um"
        )

    write_csv(trace_path, trace_rows)
    write_csv(summary_path, summary_rows)
    if not trace_path.is_file() or trace_path.stat().st_size <= 0:
        raise RuntimeError("transient trace CSV was not persisted")
    if not summary_path.is_file() or summary_path.stat().st_size <= 0:
        raise RuntimeError("transient summary CSV was not persisted")

    max_nrmse = max(float(row["waveform_nrmse_pct_of_neuron_peak"]) for row in summary_rows)
    max_peak_error = max(float(row["peak_amplitude_error_pct"]) for row in summary_rows)
    max_waveform_abs_error = max(float(row["waveform_max_abs_error_mV"]) for row in summary_rows)
    print(f"NEURON={neuron.__version__}")
    print(f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}; SWC_records={len(morphology.nodes)}")
    print(
        f"NEURON_sections={len(sections)}; NEURON_segments={sum(section.nseg for section in sections)}; "
        f"mesh_cap_um={NEURON_MAX_SEGMENT_UM:g}"
    )
    print(
        f"AMSN_compartments={cable.n_compartments}; source_count={len(injections)}; "
        f"probe_count={len(probes)}; dt_ms={DT_MS:g}; duration_ms={DURATION_MS:g}; "
        f"sample_count={current_grid_samples}; trace_rows={total_trace_rows}"
    )
    print(
        f"stimulus_pA={INJECTED_P_A:g}; delay_ms={PULSE_START_MS:g}; "
        f"duration_ms={PULSE_DURATION_MS:g}; integrator=backward_euler"
    )
    print(
        f"max_source_nearest_centre_offset_um={maximum_source_offset_um:.12g}; "
        f"max_probe_nearest_centre_offset_um={maximum_probe_offset_um:.12g}; "
        f"time_grid_max_abs_difference_ms={max_time_grid_error_ms:.12g}"
    )
    print(
        f"waveform_nrmse_pct_max={max_nrmse:.12g}; "
        f"peak_amplitude_error_pct_max={max_peak_error:.12g}; "
        f"waveform_absolute_error_mV_max={max_waveform_abs_error:.12g}"
    )
    print(f"trace_csv={trace_path}; bytes={trace_path.stat().st_size}")
    print(f"summary_csv={summary_path}; rows={len(summary_rows)}")


if __name__ == "__main__":
    main()
