"""Passive mesh-sensitivity experiment on a synthetic branched cable tree.

This is a numerical-method smoke study, not a human-neuron result.
"""
from time import perf_counter

import numpy as np

from amsn.discretization import refine_swc_morphology
from amsn.morphology import SWCMorphology


SYNTHETIC_SWC = """# Synthetic branching cable; not a biological reconstruction.
1 1 0 0 0 8.0 -1
2 3 0 0 100 2.0 1
3 3 0 0 300 1.2 2
4 3 100 0 500 0.7 3
5 3 -100 0 500 0.7 3
6 4 0 0 -100 1.5 1
7 4 0 0 -300 1.0 6
"""


def run_mesh(max_electrotonic_length: float) -> tuple[int, float, float, float]:
    morphology = SWCMorphology.from_text(SYNTHETIC_SWC)
    refined = refine_swc_morphology(
        morphology,
        max_electrotonic_length=max_electrotonic_length,
        reference_frequency_hz=100.0,
        axial_resistivity_ohm_m=0.7,
        specific_capacitance_f_m2=0.01,
    )
    cable = refined.to_cable_tree()
    soma_index = cable.index["swc_1"]
    distal_index = cable.index["swc_5"]
    injected_current = 100e-12

    def stimulus(_time_s: float) -> np.ndarray:
        current = np.zeros(cable.n_compartments)
        current[soma_index] = injected_current
        return current

    start = perf_counter()
    trace = cable.simulate_passive(
        duration_s=0.15,
        dt_s=1e-4,
        current_fn=stimulus,
        initial_voltage_v=cable.parameters.e_leak_v,
    )
    elapsed = perf_counter() - start
    resting = cable.parameters.e_leak_v
    soma_delta = float(trace.voltage_v[-1, soma_index] - resting)
    distal_delta = float(trace.voltage_v[-1, distal_index] - resting)
    input_resistance_mohm = soma_delta / injected_current / 1e6
    transfer_ratio = distal_delta / soma_delta
    return cable.n_compartments, input_resistance_mohm, transfer_ratio, elapsed


if __name__ == "__main__":
    print("synthetic morphology; passive parameters are generic, not human-fitted")
    print("d_lambda  compartments  Rin_MOhm  distal_to_soma  sim_seconds")
    for d_lambda in (0.2, 0.1, 0.05, 0.025):
        n, rin, transfer, elapsed = run_mesh(d_lambda)
        print(f"{d_lambda:7.3f}  {n:12d}  {rin:8.4f}  {transfer:14.8f}  {elapsed:11.6f}")
