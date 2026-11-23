"""Unit tests for the Wilbers Figure 2 workbook audit helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "examples" / "audit_wilbers_figure2_data.py"
SPEC = importlib.util.spec_from_file_location("audit_wilbers_figure2_data", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_na_header_parser_preserves_all_four_source_group_codes():
    assert MODULE.parse_na_header("relative_amp_Hnarrow_  1") == ("Hnarrow", 1)
    assert MODULE.parse_na_header("relative_amp_Mnarrow_ 200") == ("Mnarrow", 200)
    assert MODULE.parse_na_header("relative_amp_Mwide_  5") == ("Mwide", 5)
    assert MODULE.parse_na_header("relative_amp_Hwide_200") == ("Hwide", 200)
    assert MODULE.parse_na_header("not_a_source_column") is None


def test_k_header_parser_separates_human_and_mouse_input_waveforms():
    assert MODULE.parse_k_header("amp_h_n_  1") == ("h", 1)
    assert MODULE.parse_k_header("amp_m_n_ 200") == ("m", 200)
    assert MODULE.parse_k_header("amp_h_  1") is None


def test_na_species_rule_matches_recording_filename_prefix():
    assert MODULE.na_recording_species("M21.29.31520.41.01.nwb") == "Mouse"
    assert MODULE.na_recording_species("H22.10.12345.41.01.nwb") == "Human"


def test_summary_reports_mean_median_and_sample_uncertainty():
    result = MODULE.summarize([1.0, 2.0, 3.0, None])
    assert result["n"] == 3
    assert result["missing"] == 1
    assert result["mean"] == 2.0
    assert result["median"] == 2.0
    assert abs(result["sd"] - 1.0) < 1e-12
    assert abs(result["sem"] - (1 / (3**0.5))) < 1e-12
