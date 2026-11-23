"""Tests for the original Wilbers K MOD variant audit."""
from __future__ import annotations
import importlib.util
from pathlib import Path
SCRIPT=Path(__file__).parents[1]/"examples"/"audit_wilbers_k_mod_variants.py"
SPEC=importlib.util.spec_from_file_location("audit_wilbers_k_mod_variants",SCRIPT)
MODULE=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

def test_parse_mod_suffix_range_and_parameters():
    text="""
NEURON {
 SUFFIX k_human
 RANGE gbar, prop_inact, prop_h2, h2tau_inact
}
PARAMETER {
 gbar = 40 (pS/um2)
 prop_inact = 0.85
 prop_h2 = 0.4
 h2tau_inact = 450 (ms)
}
"""
    d=MODULE.parse_mod_parameters(text)
    assert d["suffix"]=="k_human"
    assert d["parameters"]=={"gbar":40.0,"prop_inact":0.85,"prop_h2":0.4,"h2tau_inact":450.0}

def test_parameter_diffs_classify_mixture_and_activation():
    d=MODULE.compare_parameters({"prop_inact":0.85,"h2tau_inact":450.0,"tha":-29.9},{"prop_inact":0.95,"h2tau_inact":225.0,"tha":-29.9,"Ra":0.02})
    assert d["change_count"]==3
    assert d["changed_parameter_groups"]["mixture_and_slow_inactivation"]==["h2tau_inact","prop_inact"]
    assert d["changed_parameter_groups"]["activation"]==["Ra"]

def test_hybrid_role_map_is_explicit():
    assert set(MODULE.HYBRID_ROLES)=={"k_hybrid1","k_hybrid2","k_hybrid3","k_hybrid4","k_hybrid5"}
    assert "activation + inactivation" in MODULE.HYBRID_ROLES["k_hybrid1"]
    assert "activation time constant" in MODULE.HYBRID_ROLES["k_hybrid4"]

def test_file_catalog_uses_original_dataverse_ids():
    assert MODULE.SOURCES["k_human"]["id"]==318647
    assert MODULE.SOURCES["k_hybrid1"]["id"]==318628
    assert MODULE.SOURCES["k_hybrid5"]["id"]==318605
    assert MODULE.SOURCES["channel_tools"]["id"]==326242
    assert MODULE.SOURCES["fit_k_human"]["id"]==326237

def test_fit_context_reads_parameter_vectors_from_original_drivers():
    helper="def K_IV_ss(cell, species='H', crits=[]):\n    return []"
    human="""
fit_channel_cma(cell=cell, fitparams=['thi1_k_human','thi2_k_human','qi1_k_human','qi2_k_human','Rd_k_human','Rg_k_human'])
fit_channel_cma(cell=cell, fitparams=['tha_k_human','qa_k_human','Ra_k_human'])
fit_channel_cma(cell=cell, fitparams=['th_act_inf_k_human','q_act_inf_k_human'])
"""
    mouse=human.replace("_human","_mouse")
    d=MODULE.fit_context(helper,human,mouse,"k_mech_IV('k_hybrid1')")
    assert len(d["human_fit_parameter_vectors"])==3
    assert d["mixture_parameters_absent_from_fit_vectors"]["prop_inact"]
    assert d["mixture_parameters_absent_from_fit_vectors"]["h2tau_inact"]
