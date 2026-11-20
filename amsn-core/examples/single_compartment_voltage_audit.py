"""Single-compartment voltage/current audit: AMSN versus NEURON 9.0.2.

The test intentionally removes morphology mapping and axial coupling. A single
NEURON segment and one AMSN compartment share the exact NEURON-reported
membrane area, specific capacitance, leak resistance, leak reversal potential,
initial voltage and Exp2Syn event. The same fixed-step time grid is used.

The event-time kernel alignment is checked alongside voltage and synaptic
current. This is a numerical integration audit, not a biological calibration.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from neuron import h, __version__ as neuron_version

from amsn.cable import CableCompartment, CableTree, PassiveParameters
from amsn.synapses import DoubleExponentialSynapse


# Shared SI biophysics.
LENGTH_M = 20e-6
DIAMETER_M = 20e-6
SPECIFIC_CAPACITANCE_F_M2 = 0.01
SPECIFIC_MEMBRANE_RESISTANCE_OHM_M2 = 1.0
AXIAL_RESISTIVITY_OHM_M = 0.7  # unused for one compartment, recorded for provenance
E_LEAK_V = -0.065
INITIAL_VOLTAGE_V = E_LEAK_V

# Same AMPA-like engineering kernel as the preceding cross-validation.
PEAK_CONDUCTANCE_S = 0.8e-9
TAU_RISE_S = 0.0002
TAU_DECAY_S = 0.002
REVERSAL_POTENTIAL_V = 0.0
DURATION_S = 0.005
DT_VALUES_S = (25e-6, 12.5e-6, 6.25e-6)
VOLTAGE_RELATIVE_FLOOR_MV = 0.02


@dataclass
class NeuronRun:
    time_s: np.ndarray
    voltage_v: np.ndarray
    conductance_s: np.ndarray
    outward_current_a: np.ndarray
    area_m2: float


def run_neuron(dt_s: float, run_index: int) -> NeuronRun:
    """Run one isolated NEURON passive segment with one Exp2Syn event."""
    dt_ms = dt_s * 1e3
    section = h.Section(name=f"single_compartment_audit_{run_index}")
    section.L = LENGTH_M * 1e6
    section.diam = DIAMETER_M * 1e6
    section.nseg = 1
    section.Ra = AXIAL_RESISTIVITY_OHM_M * 100.0
    section.cm = SPECIFIC_CAPACITANCE_F_M2 * 100.0
    section.insert("pas")

    segment = section(0.5)
    segment.g_pas = (
        1.0 / SPECIFIC_MEMBRANE_RESISTANCE_OHM_M2
    ) * 1e-4  # S/cm2
    segment.e_pas = E_LEAK_V * 1e3  # mV
    area_m2 = float(segment.area()) * 1e-12  # um2 -> m2

    synapse = h.Exp2Syn(segment)
    synapse.tau1 = TAU_RISE_S * 1e3  # ms
    synapse.tau2 = TAU_DECAY_S * 1e3  # ms
    synapse.e = REVERSAL_POTENTIAL_V * 1e3  # mV

    stimulus = h.NetStim()
    stimulus.start = 0.0
    stimulus.number = 1
    stimulus.interval = 1000.0
    stimulus.noise = 0.0
    netcon = h.NetCon(stimulus, synapse)
    netcon.delay = 0.0
    # NEURON Exp2Syn weight uses uS; requested peak conductance is in S.
    netcon.weight[0] = PEAK_CONDUCTANCE_S * 1e6

    h.dt = dt_ms
    h.secondorder = 0
    h.CVode().active(0)

    time_record = h.Vector()
    voltage_record = h.Vector()
    conductance_record = h.Vector()
    current_record = h.Vector()
    time_record.record(h._ref_t)
    voltage_record.record(segment._ref_v)
    conductance_record.record(synapse._ref_g)
    current_record.record(synapse._ref_i)

    h.finitialize(INITIAL_VOLTAGE_V * 1e3)
    steps = round(DURATION_S / dt_s)
    for _ in range(steps):
        h.fadvance()

    time_s = np.asarray(time_record, dtype=float) * 1e-3
    voltage_v = np.asarray(voltage_record, dtype=float) * 1e-3
    conductance_s = np.asarray(conductance_record, dtype=float) * 1e-6
    outward_current_a = np.asarray(current_record, dtype=float) * 1e-9

    # Keep references alive until the vectors have been copied.
    _ = (section, segment, synapse, stimulus, netcon)
    return NeuronRun(
        time_s=time_s,
        voltage_v=voltage_v,
        conductance_s=conductance_s,
        outward_current_a=outward_current_a,
        area_m2=area_m2,
    )


def run_amsn(dt_s: float, area_m2: float):
    """Run one AMSN compartment with the exact NEURON membrane area."""
    compartment = CableCompartment(
        name="soma",
        length_m=LENGTH_M,
        diameter_m=DIAMETER_M,
        parent=None,
        membrane_area_m2=area_m2,
    )
    parameters = PassiveParameters(
        specific_capacitance_f_m2=SPECIFIC_CAPACITANCE_F_M2,
        specific_membrane_resistance_ohm_m2=SPECIFIC_MEMBRANE_RESISTANCE_OHM_M2,
        axial_resistivity_ohm_m=AXIAL_RESISTIVITY_OHM_M,
        e_leak_v=E_LEAK_V,
    )
    tree = CableTree([compartment], parameters)
    synapse = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )

    def conductance_at(time_s: float) -> np.ndarray:
        return np.array([synapse.conductance_at(time_s)], dtype=float)

    trace = tree.simulate_synaptic(
        duration_s=DURATION_S,
        dt_s=dt_s,
        synaptic_conductance_fn=conductance_at,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
        initial_voltage_v=INITIAL_VOLTAGE_V,
    )
    return tree, synapse, trace


def summarize(label: str, errors: np.ndarray) -> tuple[float, float]:
    absolute = np.abs(errors)
    max_error = float(np.max(absolute))
    rms_error = float(np.sqrt(np.mean(errors * errors)))
    print(f"# {label}: max_abs={max_error:.12g}; rms={rms_error:.12g}")
    return max_error, rms_error


def run_case(dt_s: float, run_index: int) -> None:
    neuron = run_neuron(dt_s, run_index)
    tree, synapse, amsn = run_amsn(dt_s, neuron.area_m2)

    if len(neuron.time_s) != len(amsn.time_s):
        raise RuntimeError(
            f"sample count mismatch at dt={dt_s:g}s: "
            f"NEURON={len(neuron.time_s)}, AMSN={len(amsn.time_s)}"
        )
    np.testing.assert_allclose(
        neuron.time_s, amsn.time_s, rtol=0.0, atol=1e-12,
        err_msg="NEURON and AMSN time grids differ",
    )

    dt_ms = dt_s * 1e3
    amsn_voltage = amsn.voltage_v[:, 0]
    amsn_voltage_mV = amsn_voltage * 1e3
    neuron_voltage_mV = neuron.voltage_v * 1e3
    voltage_error_uV = (amsn_voltage_mV - neuron_voltage_mV) * 1e3

    # The NEURON fixed-step record is offset by one dt in this exact NetStim
    # protocol. Compare its recorded g(t) with AMSN's analytic g(t-dt), which
    # is the conductance held over the preceding implicit voltage step.
    aligned_kernel_s = np.array([
        synapse.conductance_at(max(0.0, float(t_s) - dt_s))
        for t_s in neuron.time_s
    ])
    same_time_kernel_s = np.array([
        synapse.conductance_at(float(t_s))
        for t_s in neuron.time_s
    ])
    g_error_nS = (aligned_kernel_s - neuron.conductance_s) * 1e9
    same_time_g_error_nS = (
        same_time_kernel_s - neuron.conductance_s
    ) * 1e9

    amsn_outward_current_a = (
        aligned_kernel_s
        * (amsn_voltage - REVERSAL_POTENTIAL_V)
    )
    current_error_pA = (
        amsn_outward_current_a - neuron.outward_current_a
    ) * 1e12

    # Ignore the initial numerical zero and late values near the leak baseline
    # for relative voltage error, but report absolute error over the full trace.
    deflection_mV = np.abs(neuron_voltage_mV - E_LEAK_V * 1e3)
    relative_mask = deflection_mV >= VOLTAGE_RELATIVE_FLOOR_MV
    relative_voltage_error_pct = (
        100.0 * np.abs(voltage_error_uV[relative_mask] * 1e-3)
        / deflection_mV[relative_mask]
    )

    print()
    print(
        f"# dt={dt_ms:.6f}ms; samples={len(neuron.time_s)}; "
        f"area={neuron.area_m2*1e12:.9f}um2; "
        f"C={tree.capacitance_f[0]*1e12:.9f}pF; "
        f"gleak={tree.membrane_leak_s[0]*1e9:.9f}nS"
    )
    print(
        f"# NEURON={neuron_version}; secondorder=0; CVode=off; "
        f"Exp2Syn={TAU_RISE_S*1e3:.6f}/{TAU_DECAY_S*1e3:.6f}ms; "
        f"peak={PEAK_CONDUCTANCE_S*1e9:.6f}nS"
    )
    summarize("voltage_error_uV", voltage_error_uV)
    summarize("aligned_conductance_error_nS", g_error_nS)
    summarize("same_timestamp_conductance_error_nS", same_time_g_error_nS)
    summarize("outward_current_error_pA", current_error_pA)
    if relative_voltage_error_pct.size:
        print(
            "# voltage_relative_error: "
            f"samples={relative_voltage_error_pct.size}; "
            f"max={np.max(relative_voltage_error_pct):.9f}%"
        )

    print(
        "dt_ms,time_ms,neuron_v_mV,amsn_v_mV,voltage_error_uV,"
        "neuron_g_nS,amsn_g_aligned_nS,amsn_g_same_time_nS,"
        "neuron_i_out_nA,amsn_i_out_nA,current_error_pA"
    )
    for index, time_s in enumerate(neuron.time_s):
        amsn_current_nA = amsn_outward_current_a[index] * 1e9
        print(
            f"{dt_ms:.6f},{time_s*1e3:.6f},"
            f"{neuron_voltage_mV[index]:.12f},"
            f"{amsn_voltage_mV[index]:.12f},"
            f"{voltage_error_uV[index]:.12f},"
            f"{neuron.conductance_s[index]*1e9:.12f},"
            f"{aligned_kernel_s[index]*1e9:.12f},"
            f"{same_time_kernel_s[index]*1e9:.12f},"
            f"{neuron.outward_current_a[index]*1e9:.12f},"
            f"{amsn_current_nA:.12f},"
            f"{current_error_pA[index]:.12f}"
        )


def main() -> None:
    print("# AMSN single-compartment voltage/current audit vs NEURON")
    print(
        "# matched one-compartment membrane; identical NEURON-reported area; "
        "SI parameters; one Exp2Syn event at t=0"
    )
    print(
        f"# Rm={SPECIFIC_MEMBRANE_RESISTANCE_OHM_M2:g}ohm*m2; "
        f"Cm={SPECIFIC_CAPACITANCE_F_M2:g}F/m2; "
        f"Ra={AXIAL_RESISTIVITY_OHM_M:g}ohm*m; "
        f"Eleak={E_LEAK_V*1e3:g}mV; Erev={REVERSAL_POTENTIAL_V*1e3:g}mV"
    )
    for index, dt_s in enumerate(DT_VALUES_S):
        run_case(dt_s, index)


if __name__ == "__main__":
    main()
