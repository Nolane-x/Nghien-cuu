"""Protocol invariants and small helper tests for the Wilbers AP-clamp replay runner."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[1] / "examples" / "replay_wilbers_apclamp.py"
SPEC = importlib.util.spec_from_file_location("replay_wilbers_apclamp", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_original_five_ap_trace_window_is_exactly_13501_samples():
    assert MODULE.protocol_end_ms(5) == 307
    assert MODULE.expected_protocol_samples(5) == 13501


def test_original_200_ap_trace_window_is_exactly_622876_samples():
    assert MODULE.protocol_end_ms(200) == 5182
    assert MODULE.expected_protocol_samples(200) == 622876


def test_only_five_or_two_hundred_aps_are_supported():
    with pytest.raises(ValueError):
        MODULE.protocol_end_ms(100)


def test_ljp_offset_is_applied_only_to_na_command_trace():
    assert MODULE.NA_VOLTAGE_OFFSET_MV == -10.0
    assert MODULE.SAMPLE_RATE_HZ == 125000
    assert MODULE.SAMPLE_FREQ_PER_MS == 125


def test_curve_metrics_compare_equal_length_series():
    result = MODULE.compare_curve([1.0, 0.9], [1.0, 0.8])
    assert result["n"] == 2
    assert abs(result["mae"] - 0.05) < 1e-12
    assert abs(result["rmse"] - (0.01 / 2) ** 0.5) < 1e-12


def test_ap1_normalization_is_explicit_and_rejects_zero_denominator():
    assert MODULE.normalize_by_first([2.0, 1.0, 0.5]) == [1.0, 0.5, 0.25]
    assert MODULE.normalize_by_first([0.0, 1.0]) == [None, None]
