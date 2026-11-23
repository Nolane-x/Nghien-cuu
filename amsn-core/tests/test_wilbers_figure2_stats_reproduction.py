"""Tests for original Figure 2 statistics capture and comparison helpers."""
from __future__ import annotations
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "examples" / "reproduce_wilbers_figure2_stats.py"
SPEC = importlib.util.spec_from_file_location("reproduce_wilbers_figure2_stats", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_interaction_p_finds_species_by_ap_term():
    capture = {"anova_table": [
        {"term": "APnr", "PR(>F)": 1e-30},
        {"term": "APnr:C(Species)", "PR(>F)": 1e-55},
        {"term": "Residual", "PR(>F)": None},
    ]}
    assert MODULE.interaction_p(capture) == 1e-55


def test_article_reference_checks_do_not_force_a_result():
    assert MODULE.compare_article_p(1e-60, {"kind": "less_than", "threshold": 1e-53})["matches"]
    assert not MODULE.compare_article_p(1e-40, {"kind": "less_than", "threshold": 1e-53})["matches"]
    assert MODULE.compare_article_p(0.07, {"kind": "approximately", "value": 0.07, "tolerance": 0.015})["within_tolerance"]


def test_source_script_and_workbook_ids_are_pinned():
    assert MODULE.FILES["stats_script"]["id"] == 318531
    assert MODULE.FILES["na"]["id"] == 318668
    assert MODULE.FILES["k"]["id"] == 318669
    assert MODULE.FILES["stats_script"]["sha256"] == "e220f0e8603976b99d67120e2aa91c8828d6e47bc3dc08b7b20cf4e3ce49fa5a"
