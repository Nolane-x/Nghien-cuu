"""Tests for source-fit snapshot vs canonical NMODL parameter reconciliation."""
from __future__ import annotations
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "examples" / "reconcile_wilbers_fit_snapshot.py"
SPEC = importlib.util.spec_from_file_location("reconcile_wilbers_fit_snapshot", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_mod_parameter_parser_reads_only_parameter_block():
    text = """NEURON { SUFFIX test }
PARAMETER {
    gbar = 40 (pS/um2)
    thi1 = 40.5 (mV)
    Rd = 0.001 (/ms) : comment
}
ASSIGNED { v (mV) }
"""
    assert MODULE.parse_mod_parameters(text) == {"gbar": 40.0, "thi1": 40.5, "Rd": 0.001}


def test_fit_snapshot_extraction_uses_terminal_final_best_fit_block():
    text = """cell = mod_cell(cell, inact_fit['params'])
# final best fit:
{
 'thi1_k_human': 20.386620488986296,
 'thi2_k_human': -84.16487679230283,
}
"""
    data, applied = MODULE.parse_final_fit_snapshot(text)
    assert data == {"thi1": 20.386620488986296, "thi2": -84.16487679230283}
    assert applied is False


def test_reconciliation_reports_parameter_mismatches_without_applying_them():
    mod = """PARAMETER {
    thi1 = 40.5659148938157 (mV)
    thi2 = -75.93822659307075 (mV)
    qi2 = 0.40183382749400054 (mV)
}"""
    fit = """# final best fit:
{
 'thi1_k_human': 20.386620488986296,
 'thi2_k_human': -84.16487679230283,
 'qi2_k_human': 6.809126450666186
}
"""
    result = MODULE.reconcile(mod, fit, "_k_human")
    assert result["parameter_count"] == 3
    assert result["match_count"] == 0
    assert result["mismatch_count"] == 3
    assert result["final_fit_snapshot_applied_by_driver_after_marker"] is False
