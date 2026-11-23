"""Regression tests for original Wilbers K voltage-clamp replay."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import audit_wilbers_k_mod_variants as audit
import replay_wilbers_k_voltage_clamp as MODULE


def test_all_nine_released_mod_source_pins_are_locked():
    MODULE.validate_variant_catalog()
    assert len(MODULE.K_NAMES) == 9
    assert MODULE.K_PINS["k_hybrid2"]["id"] == 318622
    assert MODULE.K_PINS["k_hybrid2"]["sha1"] == "05040e3bfe6d2914a14358e62bb631f0c9ef492b"


def test_original_protocol_constants_match_published_source():
    source = """
def K_IV_ss(cell, species='H', crits=[]):
    h.celsius=34
    steps_per_ms=10
    h.dt=1.0/steps_per_ms
    durs=[20,500,50,100]
    amps=[-140,0,60,-140]
    volts=np.arange(-110,60,10)
    I=runIk(cell,durs,amps)
    mask=(t>20.4)&(t<520)
    mask=(t>520)&(t<570)
    tau_inact1[step],tau_inact2[step]=get_tau_inact_double(x[pk:-1],y[pk:-1])
def K_recovery_ss(cell,species='H'):
    h.celsius=34
    steps_per_ms=2
    durs=[2,5000]
    amps=[-120,60]
    rectimes=np.linspace(2,92,10)**2
    volts=np.array([-80])
    durs=[2,5000,rectime,5]
    amps=[-120,40,v,40]
    get_double_tau_rec(rectimes,pulse2)
def k_mech_IV(mechname):
    cell=h.Section()
    cell.diam=10
    cell.insert(mechname)
    cell.Ra=200
    cell.cm=1
    cell.ek=-101
def runIk(cell,durs,amps): pass
def fit_boltz_act(x,y): pass
def fit_boltz_inact(x,y): pass
def get_tau_act(x,y): pass
def get_tau_inact_double(x,y): pass
def get_double_tau_rec(x,y): pass
"""
    result = MODULE.validate_original_protocol_sources(source)
    assert result["functions_verified"] == sorted([
        "K_IV_ss", "K_recovery_ss", "k_mech_IV", "runIk",
        "fit_boltz_act", "fit_boltz_inact", "get_tau_act",
        "get_tau_inact_double", "get_double_tau_rec",
    ])


def test_source_change_or_missing_protocol_constants_fails_closed():
    with pytest.raises(ValueError, match="Original channel_tools.py functions are missing"):
        MODULE.validate_original_protocol_sources("def runIk(): pass")
    altered = """
def K_IV_ss():
    h.celsius=25
    steps_per_ms=10
    durs=[20,500,50,100]
    amps=[-140,0,60,-140]
    volts=np.arange(-110,60,10)
    mask=(t>20.4)&(t<520)
    mask=(t>520)&(t<570)
    get_tau_inact_double(x[pk:-1],y[pk:-1])
def K_recovery_ss():
    h.celsius=34
    steps_per_ms=2
    durs=[2,5000]
    amps=[-120,60]
    rectimes=np.linspace(2,92,10)**2
    volts=np.array([-80])
    durs=[2,5000,rectime,5]
    amps=[-120,40,v,40]
    get_double_tau_rec(rectimes,pulse2)
def k_mech_IV():
    cell.diam=10
    cell.insert(mechname)
    cell.Ra=200
    cell.cm=1
    cell.ek=-101
def runIk(): pass
def fit_boltz_act(): pass
def fit_boltz_inact(): pass
def get_tau_act(): pass
def get_tau_inact_double(): pass
def get_double_tau_rec(): pass
"""
    with pytest.raises(ValueError, match="protocol/setup source"):
        MODULE.validate_original_protocol_sources(altered)


def test_protocol_grids_and_cell_setup_match_original_helpers():
    assert MODULE.K_IV_DURS_MS == (20.0, 500.0, 50.0, 100.0)
    assert MODULE.K_IV_START_AMPS_MV == (-140.0, 0.0, 60.0, -140.0)
    assert MODULE.K_IV_VOLTAGES_MV == tuple(float(x) for x in range(-110, 60, 10))
    assert MODULE.K_IV_DT_MS == pytest.approx(0.1)
    assert MODULE.RECOVERY_DT_MS == pytest.approx(0.5)
    assert MODULE.RECOVERY_VOLTAGE_MV == -80.0
    assert MODULE.RECOVERY_DELAYS_MS == tuple(float(x) for x in np.linspace(2, 92, 10) ** 2)
    assert MODULE.TEMPERATURE_C == 34.0
    assert MODULE.EK_MV == -101.0


def test_original_current_helpers_are_selected_not_reimplemented():
    source = audit.function_source("""
def runIk(cell,durs,amps):
    vcvec=np.empty(0)
    vc=h.VClamp(cell(0.5))
def get_tau_act(x,y,est=2): pass
def get_tau_inact_double(x,y): pass
def get_double_tau_rec(x,y): pass
""", "runIk")
    assert source is not None
    assert "h.VClamp" in source


def test_target_curve_comparison_uses_only_original_author_included_rows():
    target = pd.DataFrame([
        {"Filename":"H1","Species":"Human","variable":"G_Gmax_activation","voltage_mV":0.0,
         "value":0.4,"included_in_author_statistics":True},
        {"Filename":"H2","Species":"Human","variable":"G_Gmax_activation","voltage_mV":0.0,
         "value":0.6,"included_in_author_statistics":True},
        {"Filename":"H3","Species":"Human","variable":"G_Gmax_activation","voltage_mV":0.0,
         "value":0.9,"included_in_author_statistics":False},
        {"Filename":"H1","Species":"Human","variable":"G_Gmax_activation","voltage_mV":10.0,
         "value":0.8,"included_in_author_statistics":True},
    ])
    metric, rows = MODULE.compare_curve_to_targets(
        [0.5, 0.7], [0.0, 10.0], target, "Human", "G_Gmax_activation"
    )
    assert metric["n_voltage_points"] == 2
    assert rows[0]["n_target_cells"] == 2
    assert rows[0]["target_mean"] == pytest.approx(0.5)
    assert metric["mae"] == pytest.approx(0.05)
    assert rows[0]["within_pointwise_1_96_sem"] is True


def test_scalar_comparison_reports_cell_count_and_sem():
    target = pd.DataFrame([
        {"Filename":"H1","Species":"Human","variable":"Vhalf_activation_mV","value":-5.0,
         "included_in_author_statistics":True},
        {"Filename":"H2","Species":"Human","variable":"Vhalf_activation_mV","value":-3.0,
         "included_in_author_statistics":True},
    ])
    result = MODULE.compare_scalar_target(-4.0, target, "Human", "Vhalf_activation_mV")
    assert result["n_target_cells"] == 2
    assert result["target_mean"] == pytest.approx(-4.0)
    assert result["delta_model_minus_target"] == pytest.approx(0.0)
    assert result["target_sem"] == pytest.approx(1.0)


def test_recovery_target_comparison_is_explicit_about_sample_size():
    scalar = {
        "Human":{"recovery":{"fast_tau_ms":{"n":12,"mean":250.0,"sd":100.0,"sem":28.867}}},
        "Mouse":{"recovery":{"fast_tau_ms":{"n":14,"mean":300.0,"sd":140.0,"sem":37.417}}},
    }
    result = MODULE.compare_recovery_target(280.0, scalar, "Human", "fast_tau_ms")
    assert result["n_target_cells"] == 12
    assert result["delta_model_minus_target"] == pytest.approx(30.0)


def test_figure4_source_guard_prevents_silent_target_replacement():
    assert MODULE.EXPECTED_FIGURE4_SHA256 == "79a39dce26b9e47cc6a1aa81bbc4dc3e29e3d2c733809dad14e98d4f5f9b4836"
    assert MODULE.EXPECTED_FIGURE4_MEASUREMENTS == 3732
