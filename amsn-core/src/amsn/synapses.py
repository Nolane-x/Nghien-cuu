"""Conductance-based synaptic kernels for AMSN.

These are mathematical conductance waveforms, not complete receptor models.
A double-exponential kernel is useful for controlled AMPA-like test inputs;
it does not include receptor binding states, desensitization, subunit
composition, stochastic vesicle release or voltage-dependent Mg2+ block.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, isfinite, log


@dataclass(frozen=True, slots=True)
class DoubleExponentialSynapse:
    """Peak-normalized double-exponential synaptic conductance waveform.

    The conductance is zero before onset_s and then follows:

        g(t) = g_peak * (exp(-t/tau_decay) - exp(-t/tau_rise)) / scale

    The scale is computed so the peak equals peak_conductance_s.
    SI units are used throughout.
    """

    onset_s: float
    peak_conductance_s: float
    tau_rise_s: float
    tau_decay_s: float
    reversal_potential_v: float = 0.0
    _peak_offset_s: float = field(init=False, repr=False, compare=False)
    _peak_scale: float = field(init=False, repr=False, compare=False)
    _alpha_limit: bool = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        values = {
            "onset_s": self.onset_s,
            "peak_conductance_s": self.peak_conductance_s,
            "tau_rise_s": self.tau_rise_s,
            "tau_decay_s": self.tau_decay_s,
            "reversal_potential_v": self.reversal_potential_v,
        }
        for name, value in values.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.onset_s < 0.0:
            raise ValueError("onset_s must be non-negative")
        if self.peak_conductance_s < 0.0:
            raise ValueError("peak_conductance_s must be non-negative")
        if self.tau_rise_s <= 0.0 or self.tau_decay_s <= 0.0:
            raise ValueError("synaptic time constants must be positive")
        if self.tau_rise_s > self.tau_decay_s:
            raise ValueError("tau_rise_s must not exceed tau_decay_s")

        # When the constants are equal to the precision supplied (including
        # rounded literature values), the normalized double exponential has
        # the alpha-function limit g/g_peak = x*exp(1-x), x=t/tau.
        relative_gap = (
            self.tau_decay_s - self.tau_rise_s
        ) / self.tau_decay_s
        alpha_limit = relative_gap <= 1e-8
        if alpha_limit:
            peak_offset = self.tau_rise_s
            peak_scale = 1.0
        else:
            peak_offset = (
                self.tau_rise_s * self.tau_decay_s
                / (self.tau_decay_s - self.tau_rise_s)
                * log(self.tau_decay_s / self.tau_rise_s)
            )
            peak_scale = (
                exp(-peak_offset / self.tau_decay_s)
                - exp(-peak_offset / self.tau_rise_s)
            )
            if not (peak_scale > 0.0 and isfinite(peak_scale)):
                raise ValueError("could not normalize double-exponential waveform")
        object.__setattr__(self, "_peak_offset_s", peak_offset)
        object.__setattr__(self, "_peak_scale", peak_scale)
        object.__setattr__(self, "_alpha_limit", alpha_limit)

    @property
    def peak_time_s(self) -> float:
        """Absolute time of peak conductance."""
        return self.onset_s + self._peak_offset_s

    def conductance_at(self, time_s: float) -> float:
        """Return conductance in siemens at an absolute simulation time."""
        if not isfinite(time_s):
            raise ValueError("time_s must be finite")
        if time_s <= self.onset_s or self.peak_conductance_s == 0.0:
            return 0.0
        elapsed = time_s - self.onset_s
        if self._alpha_limit:
            scaled_time = elapsed / self.tau_rise_s
            waveform = scaled_time * exp(1.0 - scaled_time)
            return self.peak_conductance_s * waveform
        waveform = (
            exp(-elapsed / self.tau_decay_s)
            - exp(-elapsed / self.tau_rise_s)
        )
        return self.peak_conductance_s * max(0.0, waveform) / self._peak_scale
