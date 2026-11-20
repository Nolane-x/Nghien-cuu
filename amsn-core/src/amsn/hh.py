"""Classic Hodgkin-Huxley 1952 membrane kinetics as a solver smoke test.

This is a squid giant-axon benchmark at the canonical 6.3 C reference
condition, NOT a parameterization of a human cortical pyramidal neuron.
Voltage is measured relative to the resting potential (-65 mV).
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .cable import CableTree, SimulationTrace
from .units import ms_cm2_to_s_m2


def _vtrap(x: np.ndarray, y: float) -> np.ndarray:
    """Stable x/(exp(x/y)-1), including the x -> 0 limit."""
    z = x / y
    out = np.empty_like(x, dtype=float)
    small = np.abs(z) < 1e-7
    out[small] = y * (1.0 - z[small] / 2.0)
    out[~small] = x[~small] / np.expm1(z[~small])
    return out


@dataclass
class HHState:
    m: np.ndarray
    h: np.ndarray
    n: np.ndarray


@dataclass(frozen=True)
class HHParameters:
    g_na_ms_cm2: float = 120.0
    g_k_ms_cm2: float = 36.0
    g_leak_ms_cm2: float = 0.3
    e_na_v: float = 0.115
    e_k_v: float = -0.012
    e_leak_v: float = 0.010613
    temperature_c: float = 6.3
    q10: float = 3.0


class HodgkinHuxley1952:
    def __init__(self, n_compartments: int, parameters: HHParameters = HHParameters()):
        if n_compartments < 1:
            raise ValueError("n_compartments must be positive")
        self.parameters = parameters
        self.state = self.steady_state(np.zeros(n_compartments, dtype=float))

    @staticmethod
    def rates(voltage_relative_v: np.ndarray) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
        # The canonical equations use mV relative to rest and rates in ms^-1.
        v = np.asarray(voltage_relative_v, dtype=float) * 1e3
        alpha_m = 0.1 * _vtrap(25.0 - v, 10.0)
        beta_m = 4.0 * np.exp(-v / 18.0)
        alpha_h = 0.07 * np.exp(-v / 20.0)
        beta_h = 1.0 / (np.exp((30.0 - v) / 10.0) + 1.0)
        alpha_n = 0.01 * _vtrap(10.0 - v, 10.0)
        beta_n = 0.125 * np.exp(-v / 80.0)
        return (alpha_m, beta_m), (alpha_h, beta_h), (alpha_n, beta_n)

    def steady_state(self, voltage_relative_v: np.ndarray) -> HHState:
        rates = self.rates(voltage_relative_v)
        gates = [a / (a + b) for a, b in rates]
        return HHState(*gates)

    def advance_gates(self, voltage_relative_v: np.ndarray, dt_s: float) -> None:
        if dt_s <= 0:
            raise ValueError("dt_s must be positive")
        q10_factor = self.parameters.q10 ** ((self.parameters.temperature_c - 6.3) / 10.0)
        dt_ms = dt_s * 1e3
        for attr, (alpha, beta) in zip(("m", "h", "n"), self.rates(voltage_relative_v)):
            total = (alpha + beta) * q10_factor
            x_inf = alpha / (alpha + beta)
            tau_ms = 1.0 / total
            old = getattr(self.state, attr)
            setattr(self.state, attr, x_inf + (old - x_inf) * np.exp(-dt_ms / tau_ms))

    def membrane_conductance_and_source(self, area_m2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        p = self.parameters
        gna_density = ms_cm2_to_s_m2(p.g_na_ms_cm2) * self.state.m**3 * self.state.h
        gk_density = ms_cm2_to_s_m2(p.g_k_ms_cm2) * self.state.n**4
        gl_density = ms_cm2_to_s_m2(p.g_leak_ms_cm2)
        gna = gna_density * area_m2
        gk = gk_density * area_m2
        gl = gl_density * area_m2
        total = gna + gk + gl
        source = gna * p.e_na_v + gk * p.e_k_v + gl * p.e_leak_v
        return total, source


def simulate_hh(tree: CableTree, duration_s: float, dt_s: float,
                current_fn=None, initial_voltage_v: float = 0.0,
                parameters: HHParameters = HHParameters()) -> SimulationTrace:
    """Split HH gate update + implicit voltage solve over a cable tree."""
    if duration_s <= 0 or dt_s <= 0:
        raise ValueError("duration_s and dt_s must be positive")
    steps = int(round(duration_s / dt_s))
    if not np.isclose(steps * dt_s, duration_s, rtol=1e-9, atol=1e-15):
        raise ValueError("duration_s must be an integer multiple of dt_s")
    hh = HodgkinHuxley1952(tree.n_compartments, parameters)
    v = np.full(tree.n_compartments, initial_voltage_v, dtype=float)
    hh.state = hh.steady_state(v)
    time = np.linspace(0.0, duration_s, steps + 1)
    trace = np.empty((steps + 1, tree.n_compartments), dtype=float)
    trace[0] = v
    for k in range(steps):
        hh.advance_gates(v, dt_s)
        gm, source = hh.membrane_conductance_and_source(tree.area_m2)
        current = (np.zeros(tree.n_compartments) if current_fn is None
                   else np.asarray(current_fn(time[k]), dtype=float))
        v = tree.step_linear(v, dt_s, gm, source, current)
        trace[k + 1] = v
    return SimulationTrace(time, trace)
