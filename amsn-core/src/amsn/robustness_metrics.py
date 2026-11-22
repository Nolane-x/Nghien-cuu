"""Numerically safe relative L2 error metrics for reduced-model validation."""
from __future__ import annotations

import numpy as np


def _validated_pair(reference, approximation, floor: float):
    ref = np.asarray(reference)
    approx = np.asarray(approximation)
    if ref.shape != approx.shape:
        raise ValueError(
            f"reference and approximation shapes differ: {ref.shape} != {approx.shape}"
        )
    if ref.size == 0:
        raise ValueError("error metrics require non-empty arrays")
    if not np.all(np.isfinite(ref)) or not np.all(np.isfinite(approx)):
        raise ValueError("reference and approximation must contain only finite values")
    value = float(floor)
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError("floor must be finite and positive")
    return ref, approx, value


def relative_l2_percent(reference, approximation, *, floor: float = 1e-30) -> float:
    """Return 100 * ||approximation-reference||_2 / max(||reference||_2, floor)."""
    ref, approx, denominator_floor = _validated_pair(reference, approximation, floor)
    denominator = max(float(np.linalg.norm(ref)), denominator_floor)
    return float(100.0 * np.linalg.norm(approx - ref) / denominator)


def columnwise_relative_l2_percent(
    reference,
    approximation,
    *,
    floor: float = 1e-30,
    axis: int = 0,
) -> np.ndarray:
    """Return relative L2 error per column (or along the requested axis)."""
    ref, approx, denominator_floor = _validated_pair(reference, approximation, floor)
    denominator = np.maximum(np.linalg.norm(ref, axis=axis), denominator_floor)
    numerator = np.linalg.norm(approx - ref, axis=axis)
    result = 100.0 * numerator / denominator
    if not np.all(np.isfinite(result)):
        raise FloatingPointError("non-finite columnwise relative error")
    return np.asarray(result, dtype=float)
