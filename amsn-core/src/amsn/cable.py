"""Passive multicompartment cable tree with an implicit Hines solver.

The solver uses SI units and backward Euler. Compartments form one rooted
tree. Standard compartments use the sum of two half-cylinder axial
resistances; SWC-derived compartments can provide explicit edge geometry
factors for tapered segments.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class CableCompartment:
    name: str
    length_m: float
    diameter_m: float
    parent: str | None = None
    # Optional exact/lumped geometry overrides used by the SWC converter.
    # `membrane_area_m2` controls capacitance and membrane leak area.
    # `axial_geometry_factor_m_inv` is integral(ds / cross_section_area)
    # along the incoming parent edge; multiplying by axial resistivity gives R.
    membrane_area_m2: float | None = None
    axial_geometry_factor_m_inv: float | None = None


@dataclass(frozen=True, slots=True)
class PassiveParameters:
    specific_capacitance_f_m2: float = 0.01       # 1 uF/cm^2
    specific_membrane_resistance_ohm_m2: float = 1.0  # 10,000 ohm*cm^2
    axial_resistivity_ohm_m: float = 0.7           # 70 ohm*cm
    e_leak_v: float = -0.065

    def __post_init__(self) -> None:
        positive = {
            "specific_capacitance_f_m2": self.specific_capacitance_f_m2,
            "specific_membrane_resistance_ohm_m2": self.specific_membrane_resistance_ohm_m2,
            "axial_resistivity_ohm_m": self.axial_resistivity_ohm_m,
        }
        for name, value in positive.items():
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not np.isfinite(self.e_leak_v):
            raise ValueError("e_leak_v must be finite")


@dataclass(frozen=True)
class SimulationTrace:
    time_s: np.ndarray
    voltage_v: np.ndarray  # shape: (time, compartment)


class CableTree:
    def __init__(self, compartments: Sequence[CableCompartment],
                 parameters: PassiveParameters = PassiveParameters()):
        if not compartments:
            raise ValueError("at least one compartment is required")
        self.parameters = parameters
        names = [c.name for c in compartments]
        if len(names) != len(set(names)):
            raise ValueError("compartment names must be unique")
        self.by_name = {c.name: c for c in compartments}
        for c in compartments:
            if (not np.isfinite(c.length_m) or not np.isfinite(c.diameter_m)
                    or c.length_m <= 0 or c.diameter_m <= 0):
                raise ValueError(f"{c.name}: length and diameter must be finite and positive")
            if c.membrane_area_m2 is not None and (
                    not np.isfinite(c.membrane_area_m2) or c.membrane_area_m2 <= 0):
                raise ValueError(f"{c.name}: membrane area must be finite and positive")
            if c.axial_geometry_factor_m_inv is not None and (
                    not np.isfinite(c.axial_geometry_factor_m_inv)
                    or c.axial_geometry_factor_m_inv <= 0):
                raise ValueError(f"{c.name}: axial geometry factor must be finite and positive")
            if c.parent is not None and c.parent not in self.by_name:
                raise ValueError(f"{c.name}: unknown parent {c.parent}")
            if c.parent == c.name:
                raise ValueError(f"{c.name}: compartment cannot parent itself")
        roots = [c.name for c in compartments if c.parent is None]
        if len(roots) != 1:
            raise ValueError(f"expected one root compartment, found {len(roots)}")
        self.root_name = roots[0]
        self.order = self._topological_order()
        self.index = {name: i for i, name in enumerate(self.order)}
        ordered = [self.by_name[name] for name in self.order]
        self.area_m2 = np.array([
            c.membrane_area_m2 if c.membrane_area_m2 is not None
            else np.pi * c.diameter_m * c.length_m
            for c in ordered
        ], dtype=float)
        self.capacitance_f = parameters.specific_capacitance_f_m2 * self.area_m2
        self.membrane_leak_s = (
            self.area_m2 / parameters.specific_membrane_resistance_ohm_m2
        )
        self.parent_index = np.full(len(ordered), -1, dtype=int)
        self.axial_g_s = np.zeros(len(ordered), dtype=float)
        for i, c in enumerate(ordered):
            if c.parent is None:
                continue
            p = self.index[c.parent]
            self.parent_index[i] = p
            parent = ordered[p]
            if c.axial_geometry_factor_m_inv is not None:
                # Exact tapered-edge resistance supplied by the SWC converter.
                resistance = (parameters.axial_resistivity_ohm_m
                              * c.axial_geometry_factor_m_inv)
            else:
                r_i = (parameters.axial_resistivity_ohm_m * (c.length_m / 2.0)
                       / (np.pi * (c.diameter_m / 2.0) ** 2))
                r_p = (parameters.axial_resistivity_ohm_m * (parent.length_m / 2.0)
                       / (np.pi * (parent.diameter_m / 2.0) ** 2))
                resistance = r_i + r_p
            if not np.isfinite(resistance) or resistance <= 0:
                raise ValueError(f"{c.name}: axial resistance must be finite and positive")
            self.axial_g_s[i] = 1.0 / resistance
        if np.any(self.capacitance_f <= 0) or np.any(self.membrane_leak_s <= 0):
            raise ValueError("derived capacitance and membrane conductance must be positive")

    def _topological_order(self) -> list[str]:
        children: dict[str, list[str]] = {name: [] for name in self.by_name}
        for c in self.by_name.values():
            if c.parent is not None:
                children[c.parent].append(c.name)
        queue = deque([self.root_name])
        order: list[str] = []
        while queue:
            name = queue.popleft()
            order.append(name)
            queue.extend(children[name])
        if len(order) != len(self.by_name):
            raise ValueError("compartments contain a cycle or disconnected component")
        return order

    @property
    def n_compartments(self) -> int:
        return len(self.order)

    def step_linear(self, voltage_v: np.ndarray, dt_s: float,
                    membrane_conductance_s: np.ndarray,
                    membrane_source_a: np.ndarray,
                    injected_current_a: np.ndarray | None = None) -> np.ndarray:
        """Advance one implicit step for C*dV/dt = -g*V + source + I + axial."""
        n = self.n_compartments
        v = np.asarray(voltage_v, dtype=float)
        gm = np.asarray(membrane_conductance_s, dtype=float)
        source = np.asarray(membrane_source_a, dtype=float)
        current = np.zeros(n) if injected_current_a is None else np.asarray(injected_current_a, dtype=float)
        if v.shape != (n,) or gm.shape != (n,) or source.shape != (n,) or current.shape != (n,):
            raise ValueError("voltage, conductance, source and current must have shape (n_compartments,)")
        if dt_s <= 0 or not np.isfinite(dt_s):
            raise ValueError("dt_s must be finite and positive")
        if np.any(gm < 0) or not np.all(np.isfinite(gm)):
            raise ValueError("membrane conductances must be finite and non-negative")
        if not (np.all(np.isfinite(v)) and np.all(np.isfinite(source)) and np.all(np.isfinite(current))):
            raise ValueError("state and input arrays must be finite")

        c_over_dt = self.capacitance_f / dt_s
        diagonal = c_over_dt + gm
        rhs = c_over_dt * v + source + current
        for i in range(1, n):
            g = self.axial_g_s[i]
            diagonal[i] += g
            diagonal[self.parent_index[i]] += g

        # Hines elimination: the morphology is a tree, so each non-root
        # compartment has exactly one parent and no fill-in is required.
        for i in range(n - 1, 0, -1):
            p = self.parent_index[i]
            g = self.axial_g_s[i]
            if diagonal[i] <= 0:
                raise FloatingPointError("non-positive diagonal during Hines elimination")
            diagonal[p] -= (g * g) / diagonal[i]
            rhs[p] += (g / diagonal[i]) * rhs[i]

        out = np.empty(n, dtype=float)
        out[0] = rhs[0] / diagonal[0]
        for i in range(1, n):
            p = self.parent_index[i]
            out[i] = (rhs[i] + self.axial_g_s[i] * out[p]) / diagonal[i]
        if not np.all(np.isfinite(out)):
            raise FloatingPointError("non-finite voltage generated by Hines solver")
        return out

    def step_passive(self, voltage_v: np.ndarray, dt_s: float,
                     injected_current_a: np.ndarray | None = None) -> np.ndarray:
        source = self.membrane_leak_s * self.parameters.e_leak_v
        return self.step_linear(voltage_v, dt_s, self.membrane_leak_s,
                                source, injected_current_a)

    def simulate_passive(self, duration_s: float, dt_s: float,
                         current_fn: Callable[[float], np.ndarray] | None = None,
                         initial_voltage_v: float | Sequence[float] | None = None) -> SimulationTrace:
        if duration_s <= 0 or dt_s <= 0:
            raise ValueError("duration_s and dt_s must be positive")
        steps_float = duration_s / dt_s
        steps = int(round(steps_float))
        if not np.isclose(steps * dt_s, duration_s, rtol=1e-9, atol=1e-15):
            raise ValueError("duration_s must be an integer multiple of dt_s")
        if initial_voltage_v is None:
            v = np.full(self.n_compartments, self.parameters.e_leak_v, dtype=float)
        elif np.isscalar(initial_voltage_v):
            v = np.full(self.n_compartments, float(initial_voltage_v), dtype=float)
        else:
            v = np.asarray(initial_voltage_v, dtype=float).copy()
        if v.shape != (self.n_compartments,):
            raise ValueError("initial_voltage_v has wrong shape")
        time = np.linspace(0.0, duration_s, steps + 1)
        trace = np.empty((steps + 1, self.n_compartments), dtype=float)
        trace[0] = v
        for k in range(steps):
            injected = (np.zeros(self.n_compartments) if current_fn is None
                        else np.asarray(current_fn(time[k]), dtype=float))
            v = self.step_passive(v, dt_s, injected)
            trace[k + 1] = v
        return SimulationTrace(time, trace)
