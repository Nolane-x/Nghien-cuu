"""AC source-placement sensitivity audit for Segev passive transfer impedance.

For each exact SWC source and probe, compare three NEURON 9.0.2 source models:
1. exact_swc_arc: Impedance.loc() at the mapped exact SWC section arc;
2. nearest_segment_centre: Impedance.loc() at the nearest segment centre;
3. weighted_adjacent_centres: complex transfer responses from the two adjacent
   segment centres combined as (1-w)*Z_lower + w*Z_upper.

The weighted complex sum is the linear frequency-domain equivalent of
splitting the same total source current between the two adjacent centres.
Probe readouts are kept separate:
- exact SWC arc;
- nearest segment centre;
- complex-linear interpolation of the adjacent-centre responses.

AMSN always injects at the exact SWC electrical node. This is an AC
source-placement diagnostic, not biological validation and not a claim that
the weighted source is the unique physical continuum source.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import neuron
from neuron import h

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.morphology import SWCMorphology


RI_OHM_M = 0.7
RM_OHM_M2 = 1.0
CM_F_M2 = 0.01
ELEAK_MV = -65.0
CURRENT_A = 1e-9
NEURON_MAX_SEGMENT_UM = float(os.environ.get("AMSN_NEURON_MAX_SEGMENT_UM", "0.125"))
FREQUENCIES_HZ = (0.1, 1.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
SOURCE_MODES = (
    "exact_swc_arc",
    "nearest_segment_centre",
    "weighted_adjacent_centres",
)
PROBE_MODES = (
    "exact_swc_arc",
    "nearest_segment_centre",
    "complex_linear_interpolation",
)
MORPHOLOGY_LABEL = os.environ.get("AMSN_MORPHOLOGY_LABEL", "NMO_290988")
MORPHOLOGY_PATH = os.environ.get("AMSN_MORPHOLOGY_PATH")
OUTPUT_PREFIX = os.environ.get("AMSN_AC_SOURCE_OUTPUT_PREFIX", "")


def complex_from_transfer(impedance, x: float, section) -> complex:
    magnitude_mohm = float(impedance.transfer(float(x), sec=section))
    phase_rad = float(impedance.transfer_phase(float(x), sec=section))
    if not np.isfinite(magnitude_mohm) or magnitude_mohm < 0.0:
        raise RuntimeError(f"invalid NEURON transfer magnitude {magnitude_mohm}")
    if not np.isfinite(phase_rad):
        raise RuntimeError(f"invalid NEURON transfer phase {phase_rad}")
    return magnitude_mohm * 1e6 * np.exp(1j * phase_rad)


def complex_from_amsn(value: complex) -> complex:
    value = complex(value)
    if not np.isfinite(value.real) or not np.isfinite(value.imag):
        raise RuntimeError(f"invalid AMSN transfer impedance {value}")
    return value


def complex_error_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(value - baseline) / max(abs(baseline), 1e-30)


def magnitude_error_pct(value: complex, baseline: complex) -> float:
    return 100.0 * abs(abs(value) - abs(baseline)) / max(abs(baseline), 1e-30)


def phase_error_deg(value: complex, baseline: complex) -> float:
    if abs(value) == 0.0 or abs(baseline) == 0.0:
        return float("nan")
    return float(np.angle(value / baseline, deg=True))


def probe_readouts(impedance, probe_site: dict) -> dict[str, complex]:
    section = probe_site["section"]
    exact_x = float(probe_site["normalized_x"])
    nearest_x = float(probe_site["nearest_segment"].x)
    lower_x = float(probe_site["lower_x"])
    upper_x = float(probe_site["upper_x"])
    upper_weight = float(probe_site["interpolation_upper_weight"])
    lower_weight = 1.0 - upper_weight
    if not (
        0.0 <= upper_weight <= 1.0
        and upper_x > lower_x
        and lower_x <= exact_x <= upper_x
    ):
        raise RuntimeError("invalid probe interpolation geometry")

    exact = complex_from_transfer(impedance, exact_x, section)
    nearest = complex_from_transfer(impedance, nearest_x, section)
    lower = complex_from_transfer(impedance, lower_x, section)
    upper = complex_from_transfer(impedance, upper_x, section)
    interpolated = lower * lower_weight + upper * upper_weight
    return {
        "exact_swc_arc": exact,
        "nearest_segment_centre": nearest,
        "complex_linear_interpolation": interpolated,
    }


def compute_neuron_probe_matrix(
    source_section,
    source_x: float,
    frequency_hz: float,
    probes: list[tuple[str, int]],
    sites: dict,
) -> dict[tuple[str, str], complex]:
    h.finitialize(ELEAK_MV)
    impedance = h.Impedance()
    impedance.loc(float(source_x), sec=source_section)
    impedance.compute(float(frequency_hz))
    values = {}
    for probe_name, probe_id in probes:
        readouts = probe_readouts(impedance, sites[probe_id])
        for probe_mode, value in readouts.items():
            values[(probe_name, probe_mode)] = value
    return values


def stats(values: list[float]) -> tuple[float, float, float, float]:
    array = np.asarray(values, dtype=float)
    return (
        float(np.median(array)),
        float(np.percentile(array, 95)),
        float(np.percentile(array, 99)),
        float(np.max(array)),
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


def main() -> None:
    reference.DATA = Path(MORPHOLOGY_PATH) if MORPHOLOGY_PATH else reference.DATA
    reference.MAX_NEURON_SEGMENT_UM = NEURON_MAX_SEGMENT_UM
    reference.RI_OHM_M = RI_OHM_M
    reference.RM_OHM_M2 = RM_OHM_M2
    reference.CM_F_M2 = CM_F_M2
    reference.ELEAK_MV = ELEAK_MV

    morphology = SWCMorphology.from_file(reference.DATA)
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, sites = fine_audit.build_sites(morphology, reader, sections)
    cable = morphology.to_cable_tree()
    electrical_map = morphology.electrical_node_mapping()
    node_to_name = {
        node_id: f"swc_{electrical_map[node_id]}"
        for node_id in morphology.nodes
    }

    rows = []
    aggregate: dict[tuple, dict[str, list[float]]] = defaultdict(
        lambda: {
            "complex_error": [],
            "magnitude_error": [],
            "phase_error": [],
            "weighted_vs_nearest_delta": [],
            "weighted_error_delta": [],
        }
    )
    row_count = 0
    maximum_source_nearest_offset_um = 0.0
    maximum_source_bracket_width_um = 0.0
    maximum_weight_sum_error = 0.0

    for source_name, source_id in injections:
        source_site = sites[source_id]
        source_section = source_site["section"]
        exact_source_x = float(source_site["normalized_x"])
        nearest_source_x = float(source_site["nearest_segment"].x)
        lower_segment = source_site["lower_segment"]
        upper_segment = source_site["upper_segment"]
        lower_source_x = float(lower_segment.x)
        upper_source_x = float(upper_segment.x)
        upper_weight = float(source_site["interpolation_upper_weight"])
        lower_weight = 1.0 - upper_weight
        weight_sum_error = abs((lower_weight + upper_weight) - 1.0)
        maximum_weight_sum_error = max(maximum_weight_sum_error, weight_sum_error)
        if not (
            0.0 <= lower_weight <= 1.0
            and 0.0 <= upper_weight <= 1.0
            and lower_source_x <= exact_source_x <= upper_source_x
            and upper_source_x >= lower_source_x
            and weight_sum_error <= 1e-14
        ):
            raise RuntimeError(f"invalid source interpolation bracket for SWC node {source_id}")

        source_offset = float(source_site["nearest_centre_offset_um"])
        bracket_width_um = abs(upper_source_x - lower_source_x) * float(source_section.L)
        maximum_source_nearest_offset_um = max(maximum_source_nearest_offset_um, source_offset)
        maximum_source_bracket_width_um = max(maximum_source_bracket_width_um, bracket_width_um)
        source_index = cable.index[node_to_name[source_id]]

        for frequency_hz in FREQUENCIES_HZ:
            h.finitialize(ELEAK_MV)
            current = np.zeros(cable.n_compartments, dtype=np.complex128)
            current[source_index] = CURRENT_A
            amsn_voltage = cable.solve_passive_frequency_response(frequency_hz, current)
            amsn_transfer = {
                probe_name: complex_from_amsn(
                    amsn_voltage[cable.index[node_to_name[probe_id]]] / CURRENT_A
                )
                for probe_name, probe_id in probes
            }

            # Exact SWC and nearest-centre source controls.
            exact_source_values = compute_neuron_probe_matrix(
                source_section, exact_source_x, frequency_hz, probes, sites
            )
            nearest_source_values = compute_neuron_probe_matrix(
                source_section, nearest_source_x, frequency_hz, probes, sites
            )

            # Linear frequency-domain superposition of the two adjacent
            # segment-centre point-source responses. The weights sum to one,
            # so the equivalent total source current is unchanged.
            lower_source_values = compute_neuron_probe_matrix(
                lower_segment.sec, lower_source_x, frequency_hz, probes, sites
            )
            if (
                lower_segment.sec == upper_segment.sec
                and abs(lower_source_x - upper_source_x) <= 1e-12
            ):
                upper_source_values = lower_source_values
            else:
                upper_source_values = compute_neuron_probe_matrix(
                    upper_segment.sec, upper_source_x, frequency_hz, probes, sites
                )

            weighted_source_values = {}
            for key in lower_source_values:
                weighted_source_values[key] = (
                    lower_source_values[key] * lower_weight
                    + upper_source_values[key] * upper_weight
                )

            all_source_values = {
                "exact_swc_arc": exact_source_values,
                "nearest_segment_centre": nearest_source_values,
                "weighted_adjacent_centres": weighted_source_values,
            }
            for source_mode, values in all_source_values.items():
                for probe_name, probe_id in probes:
                    amsn_value = amsn_transfer[probe_name]
                    probe_site = sites[probe_id]
                    for probe_mode in PROBE_MODES:
                        neuron_value = values[(probe_name, probe_mode)]
                        complex_error = complex_error_pct(neuron_value, amsn_value)
                        magnitude_error = magnitude_error_pct(neuron_value, amsn_value)
                        phase_error = phase_error_deg(neuron_value, amsn_value)
                        nearest_value = nearest_source_values[(probe_name, probe_mode)]
                        weighted_value = weighted_source_values[(probe_name, probe_mode)]
                        weighted_vs_nearest = complex_error_pct(
                            weighted_value, nearest_value
                        )
                        weighted_error_delta = (
                            complex_error_pct(weighted_value, amsn_value)
                            - complex_error_pct(nearest_value, amsn_value)
                        )
                        row = {
                            "morphology_label": MORPHOLOGY_LABEL,
                            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
                            "source": source_name,
                            "source_swc_id": source_id,
                            "source_section": source_section.name(),
                            "source_exact_swc_x": exact_source_x,
                            "source_nearest_segment_x": nearest_source_x,
                            "source_lower_segment_x": lower_source_x,
                            "source_upper_segment_x": upper_source_x,
                            "source_lower_weight": lower_weight,
                            "source_upper_weight": upper_weight,
                            "source_nearest_offset_um": source_offset,
                            "source_bracket_width_um": bracket_width_um,
                            "source_current_weight_sum_error": weight_sum_error,
                            "probe": probe_name,
                            "probe_swc_id": probe_id,
                            "probe_section": probe_site["section_name"],
                            "probe_exact_swc_x": probe_site["normalized_x"],
                            "probe_nearest_segment_x": float(probe_site["nearest_segment"].x),
                            "probe_lower_segment_x": float(probe_site["lower_x"]),
                            "probe_upper_segment_x": float(probe_site["upper_x"]),
                            "probe_upper_weight": float(probe_site["interpolation_upper_weight"]),
                            "probe_mode": probe_mode,
                            "source_mode": source_mode,
                            "frequency_hz": frequency_hz,
                            "current_amplitude_a": CURRENT_A,
                            "specific_Ri_ohm_m": RI_OHM_M,
                            "specific_Rm_ohm_m2": RM_OHM_M2,
                            "specific_Cm_F_m2": CM_F_M2,
                            "Eleak_mV": ELEAK_MV,
                            "neuron_transfer_magnitude_ohm": abs(neuron_value),
                            "neuron_transfer_phase_deg": np.angle(neuron_value, deg=True),
                            "amsn_transfer_magnitude_ohm": abs(amsn_value),
                            "amsn_transfer_phase_deg": np.angle(amsn_value, deg=True),
                            "transfer_complex_error_pct": complex_error,
                            "transfer_magnitude_error_pct": magnitude_error,
                            "transfer_phase_error_deg": phase_error,
                            "weighted_vs_nearest_transfer_complex_delta_pct": weighted_vs_nearest,
                            "weighted_vs_nearest_error_delta_pct": weighted_error_delta,
                        }
                        rows.append(row)
                        key = (
                            source_name, probe_name, source_mode, probe_mode
                        )
                        aggregate[key]["complex_error"].append(complex_error)
                        aggregate[key]["magnitude_error"].append(magnitude_error)
                        aggregate[key]["phase_error"].append(phase_error)
                        aggregate[key]["weighted_vs_nearest_delta"].append(weighted_vs_nearest)
                        aggregate[key]["weighted_error_delta"].append(weighted_error_delta)
                        row_count += 1

    expected_rows = (
        len(injections) * len(probes) * len(FREQUENCIES_HZ)
        * len(SOURCE_MODES) * len(PROBE_MODES)
    )
    if row_count != expected_rows:
        raise RuntimeError(f"expected {expected_rows} AC source-alignment rows, got {row_count}")

    prefix = OUTPUT_PREFIX or f"{MORPHOLOGY_LABEL}_mesh{NEURON_MAX_SEGMENT_UM:g}um_"
    results_dir = Path(__file__).parents[1] / "results"
    raw_path = results_dir / f"{prefix}human_segev_ac_source_alignment_2026-11-21.csv"
    summary_path = results_dir / f"{prefix}human_segev_ac_source_alignment_summary_2026-11-21.csv"
    write_csv(raw_path, rows)

    summary_rows = []
    for (source_name, probe_name, source_mode, probe_mode), values in sorted(aggregate.items()):
        complex_stats = stats(values["complex_error"])
        magnitude_stats = stats(values["magnitude_error"])
        phase_stats = stats(values["phase_error"])
        summary_rows.append({
            "morphology_label": MORPHOLOGY_LABEL,
            "neuron_max_segment_um": NEURON_MAX_SEGMENT_UM,
            "source": source_name,
            "probe": probe_name,
            "source_mode": source_mode,
            "probe_mode": probe_mode,
            "frequency_count": len(FREQUENCIES_HZ),
            "complex_error_median_p95_p99_max_pct": ",".join(f"{x:.12g}" for x in complex_stats),
            "magnitude_error_median_p95_p99_max_pct": ",".join(f"{x:.12g}" for x in magnitude_stats),
            "phase_error_median_p95_p99_max_deg": ",".join(f"{x:.12g}" for x in phase_stats),
            "weighted_vs_nearest_complex_delta_max_pct": max(values["weighted_vs_nearest_delta"]),
            "weighted_vs_nearest_error_delta_median_pct": float(np.median(values["weighted_error_delta"])),
            "weighted_vs_nearest_error_delta_max_pct": max(values["weighted_error_delta"]),
        })
    expected_summary_rows = len(injections) * len(probes) * len(SOURCE_MODES) * len(PROBE_MODES)
    if len(summary_rows) != expected_summary_rows:
        raise RuntimeError(
            f"expected {expected_summary_rows} AC source summary rows, got {len(summary_rows)}"
        )
    write_csv(summary_path, summary_rows)

    max_error = max(float(row["transfer_complex_error_pct"]) for row in rows)
    print(f"NEURON={neuron.__version__}")
    print(
        f"morphology={MORPHOLOGY_LABEL}; path={reference.DATA}; "
        f"NEURON_sections={len(sections)}; NEURON_segments={sum(section.nseg for section in sections)}"
    )
    print(
        f"source_count={len(injections)}; probe_count={len(probes)}; "
        f"frequency_count={len(FREQUENCIES_HZ)}; source_modes={len(SOURCE_MODES)}; "
        f"probe_modes={len(PROBE_MODES)}; rows={len(rows)}; summary_rows={len(summary_rows)}"
    )
    print(
        f"max_source_nearest_offset_um={maximum_source_nearest_offset_um:.12g}; "
        f"max_source_bracket_width_um={maximum_source_bracket_width_um:.12g}; "
        f"max_source_weight_sum_error={maximum_weight_sum_error:.12g}"
    )
    print(f"transfer_complex_error_max_pct={max_error:.12g}")
    for source_mode in SOURCE_MODES:
        for probe_mode in PROBE_MODES:
            values = np.asarray([
                row["transfer_complex_error_pct"]
                for row in rows
                if row["source_mode"] == source_mode and row["probe_mode"] == probe_mode
            ], dtype=float)
            print(
                f"mode_summary={source_mode}/{probe_mode}; "
                f"complex_error_median_p95_max_pct="
                f"{np.median(values):.12g},{np.percentile(values,95):.12g},{np.max(values):.12g}"
            )
    print(f"raw_csv={raw_path}; bytes={raw_path.stat().st_size}")
    print(f"summary_csv={summary_path}; rows={len(summary_rows)}")


if __name__ == "__main__":
    main()
