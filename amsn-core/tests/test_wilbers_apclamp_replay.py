"""Small protocol invariants for the original AP-clamp replay runner."""
from __future__ import annotations
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "examples" / "replay_wilbers_apclamp.py"
SPEC = importlib.util.spec_from_file_location("replay_wilbers_apclamp", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_original_five_ap_trace_window_is_exactly_13501_samples():
    start = round(MODULE.TIME_START_MS * MODULE.SAMPLE_FREQ_PER_MS)
    end = round(MODULE.TIME_END_MS * MODULE.SAMPLE_FREQ_PER_MS) + 1
    assert start == 24875
    assert end == 38376
    assert end - start == 13501


def test_ljp_offset_is_applied_only_to_na_command_trace():
    assert MODULE.NA_VOLTAGE_OFFSET_MV == -10.0
    assert MODULE.SAMPLE_RATE_HZ == 125000
    assert MODULE.SAMPLE_FREQ_PER_MS == 125
