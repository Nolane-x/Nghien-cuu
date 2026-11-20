"""Isolate NEURON Exp2Syn event timing from cable/morphology errors.

Records NEURON's conductance state on a fixed time grid and compares it with
AMSN's analytic double-exponential kernel at the same timestamp and at +/- dt.
This is a numerical mechanism audit, not a biological parameter fit.
"""
from __future__ import annotations

import numpy as np
from neuron import h

from amsn.synapses import DoubleExponentialSynapse


DT_MS = 0.025
DT_S = DT_MS * 1e-3
DURATION_MS = 5.0
PEAK_CONDUCTANCE_S = 0.8e-9
TAU_RISE_S = 0.0002
TAU_DECAY_S = 0.002
REVERSAL_POTENTIAL_V = 0.0


def main() -> None:
    section = h.Section(name="kernel_audit")
    section.L = 20.0
    section.diam = 20.0
    section.Ra = 100.0
    section.cm = 1.0

    mechanism = h.Exp2Syn(section(0.5))
    mechanism.tau1 = TAU_RISE_S * 1e3
    mechanism.tau2 = TAU_DECAY_S * 1e3
    mechanism.e = REVERSAL_POTENTIAL_V * 1e3

    source = h.NetStim()
    source.start = 0.0
    source.number = 1
    source.interval = 1000.0
    source.noise = 0.0
    connection = h.NetCon(source, mechanism)
    connection.delay = 0.0
    # Exp2Syn NetCon weight is in uS; convert the requested peak S to uS.
    connection.weight[0] = PEAK_CONDUCTANCE_S * 1e6

    h.dt = DT_MS
    h.secondorder = 0
    h.CVode().active(0)

    recorded_time = h.Vector()
    recorded_conductance = h.Vector()
    recorded_time.record(h._ref_t)
    recorded_conductance.record(mechanism._ref_g)

    h.finitialize(-65.0)
    h.continuerun(DURATION_MS)

    times_ms = np.asarray(recorded_time, dtype=float)
    neuron_g_s = np.asarray(recorded_conductance, dtype=float) * 1e-6
    kernel = DoubleExponentialSynapse(
        onset_s=0.0,
        peak_conductance_s=PEAK_CONDUCTANCE_S,
        tau_rise_s=TAU_RISE_S,
        tau_decay_s=TAU_DECAY_S,
        reversal_potential_v=REVERSAL_POTENTIAL_V,
    )

    print("# NEURON Exp2Syn kernel-only event timing audit")
    print(
        f"# dt={DT_MS:.6f}ms event_start=0ms weight_peak={PEAK_CONDUCTANCE_S*1e9:.6f}nS "
        f"tau1={TAU_RISE_S*1e3:.6f}ms tau2={TAU_DECAY_S*1e3:.6f}ms"
    )
    print("time_ms,neuron_g_nS,amsn_g_at_same_time_nS,amsn_g_one_dt_earlier_nS,amsn_g_one_dt_later_nS")
    rows = []
    for t_ms, observed_s in zip(times_ms, neuron_g_s):
        t_s = float(t_ms) * 1e-3
        same = kernel.conductance_at(t_s)
        earlier = kernel.conductance_at(max(0.0, t_s - DT_S))
        later = kernel.conductance_at(t_s + DT_S)
        rows.append((float(t_ms), float(observed_s), same, earlier, later))
        print(
            f"{t_ms:.6f},{observed_s*1e9:.12f},{same*1e9:.12f},"
            f"{earlier*1e9:.12f},{later*1e9:.12f}"
        )

    matrix = np.asarray(rows, dtype=float)
    # Exclude the zero/near-zero conductance tail from relative-error metrics.
    observed = matrix[:, 1]
    masks = {
        "same_time": (observed >= 0.02e-9, matrix[:, 2]),
        "one_dt_earlier": (observed >= 0.02e-9, matrix[:, 3]),
        "one_dt_later": (observed >= 0.02e-9, matrix[:, 4]),
    }
    print("alignment,n_samples,max_abs_error_nS,rms_abs_error_nS,max_relative_error_pct")
    for label, (mask, expected) in masks.items():
        abs_error = np.abs(expected[mask] - observed[mask])
        relative_error = 100.0 * abs_error / observed[mask]
        print(
            f"{label},{int(np.sum(mask))},{np.max(abs_error)*1e9:.12f},"
            f"{np.sqrt(np.mean(abs_error**2))*1e9:.12f},"
            f"{np.max(relative_error):.9f}"
        )


if __name__ == "__main__":
    main()
