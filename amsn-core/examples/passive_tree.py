"""Run a small passive cable tree example (all values are SI units)."""
import numpy as np

from amsn.cable import CableCompartment, CableTree

cell = CableTree([
    CableCompartment("soma", 20e-6, 20e-6),
    CableCompartment("apical_1", 100e-6, 2e-6, "soma"),
    CableCompartment("apical_2", 100e-6, 1.5e-6, "apical_1"),
    CableCompartment("basal_1", 80e-6, 1.2e-6, "soma"),
])


def current(t):
    values = np.zeros(cell.n_compartments)
    if 0.005 <= t < 0.010:
        values[cell.index["apical_2"]] = 30e-12
    return values

trace = cell.simulate_passive(0.020, 1e-5, current_fn=current)
print("Compartments:", cell.n_compartments)
print("Peak voltage (mV):", float(trace.voltage_v.max() * 1e3))
print("Terminal voltage (mV):", (trace.voltage_v[-1] * 1e3).round(3).tolist())
