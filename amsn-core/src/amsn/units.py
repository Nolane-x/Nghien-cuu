"""Unit conversion helpers. The numerical core uses SI units internally."""
from __future__ import annotations

UM_TO_M = 1e-6
NM_TO_M = 1e-9
MS_TO_S = 1e-3
MV_TO_V = 1e-3
PA_TO_A = 1e-12
NA_TO_A = 1e-9


def um_to_m(value: float) -> float:
    return value * UM_TO_M


def ms_to_s(value: float) -> float:
    return value * MS_TO_S


def mv_to_v(value: float) -> float:
    return value * MV_TO_V


def pa_to_a(value: float) -> float:
    return value * PA_TO_A


def na_to_a(value: float) -> float:
    return value * NA_TO_A


def ohm_cm_to_ohm_m(value: float) -> float:
    """Convert resistivity in ohm*cm to ohm*m."""
    return value * 1e-2


def ohm_cm2_to_ohm_m2(value: float) -> float:
    """Convert specific membrane resistance in ohm*cm^2 to ohm*m^2."""
    return value * 1e-4


def uf_cm2_to_f_m2(value: float) -> float:
    """Convert specific capacitance in microfarad/cm^2 to F/m^2."""
    return value * 1e-2


def ms_cm2_to_s_m2(value: float) -> float:
    """Convert conductance density in mS/cm^2 to S/m^2."""
    return value * 10.0
