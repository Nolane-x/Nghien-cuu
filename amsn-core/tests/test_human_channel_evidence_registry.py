"""Structural checks for source-backed human NaV/KV evidence.

These tests validate data provenance and unit bookkeeping only. They do not
validate a channel mechanism or imply that the literature values are runtime
parameters.
"""
from __future__ import annotations

import json
from pathlib import Path


EVIDENCE_PATH = (
    Path(__file__).parents[1]
    / "research"
    / "references"
    / "human_nav_kv_evidence_2023.json"
)


def load_evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_evidence_is_explicitly_not_runtime_ready():
    data = load_evidence()
    assert data["status"] == "source_backed_research_transcription_not_runtime_ready"
    assert data["runtime_eligible"] is False


def test_wilbers_patch_measurements_are_somatic_and_unit_consistent():
    data = load_evidence()
    study = data["studies"]["wilbers_2023"]
    patch = study["measured_somatic_nucleated_patch_conductance_density"]
    assert patch["evidence_class"] == "direct_experimental_measurement"
    assert patch["scope"] == "somatic nucleated-patch membrane; not AIS or axon"
    assert patch["na"]["n_recordings"] == 17
    assert patch["k"]["n_recordings"] == 13
    assert patch["na"]["si_mean_S_m2"] == patch["na"]["mean"]
    assert patch["k"]["si_mean_S_m2"] == patch["k"]["mean"]
    assert patch["na"]["mean_S_cm2"] == patch["na"]["mean"] * 1e-4
    assert patch["k"]["mean_S_cm2"] == patch["k"]["mean"] * 1e-4


def test_model_fit_parameters_are_not_mislabelled_as_measurements():
    data = load_evidence()
    study = data["studies"]["wilbers_2023"]
    measured = study["measured_somatic_nucleated_patch_conductance_density"]
    fitted = study["single_compartment_hh_model_fit"]
    assert fitted["evidence_class"] == "computational_model_parameter_fit"
    assert fitted["runtime_eligible"] is False
    assert fitted["model_scope"].startswith("single compartment")
    assert measured["na"]["mean"] != fitted["maximal_conductance_density"]["na"]["value"]


def test_eyal_values_remain_model_estimates_and_compartment_specific():
    data = load_evidence()
    study = data["studies"]["eyal_2018"]
    assert study["evidence_class"] == "model_estimated_conductance_density"
    assert study["modeled_cells"] == 6
    assert "rodents" in study["critical_assumption"]
    estimates = study["model_estimates"]
    assert estimates["na_axon"]["mean_S_m2"] == estimates["na_axon"]["mean"] * 10000
    assert estimates["na_soma"]["mean_S_m2"] == estimates["na_soma"]["mean"] * 10000
    assert "dendritic sodium-channel" in study["missing_evidence"][0]


def test_voltage_dependence_retains_liquid_junction_caveat():
    data = load_evidence()
    vdep = data["studies"]["wilbers_2023"]["measured_voltage_dependence"]
    assert vdep["data_corrected_for_15mV_liquid_junction_potential"] is False
    assert vdep["v_half"]["na_activation"]["n"] == 19
    assert vdep["v_half"]["k_inactivation"]["n"] == 11
    assert vdep["slope_factors"]["status"] == "not_transcribed_as_runtime_parameters"
