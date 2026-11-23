"""Tests for the independent Wilbers Figure 4 voltage-clamp audit."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
EXAMPLES=Path(__file__).parents[1]/"examples"
if str(EXAMPLES) not in sys.path: sys.path.insert(0,str(EXAMPLES))
import audit_wilbers_figure4_voltage_clamp as M


def test_source_pins_are_locked():
    M.validate_pins()
    assert M.FILES["workbook"]["id"]==318667
    assert M.FILES["workbook"]["bytes"]==108029
    assert M.FILES["plots"]["sha1"]=="f9c4e70aba0760d00bb2ae911554c5e262fe8a7a"


def test_released_filter_and_statistics_rules_are_required():
    plots="""
    df[df.gof_boltz_act>0.9]
    df[df.gof_boltz_inact>0.9]
    df_l_act.loc[(df_l_act.volt_act_>=-10)&(df_l_act.gof_act_>0.8)]
    rec_protocol_name == 'K_IKrecv2_1_h0_DA_0'
    """
    stats="""
    stats.normaltest(); stats.bartlett(); stats.ttest_ind(); stats.ranksums()
    tau_act_ ~ C(Species)*I(volt_act_**2)
    tau_inact_fast_ ~ C(Species)*volt_
    tau_inact_slow_ ~ C(Species)*volt_
    """
    result=M.validate_original_scripts(plots,stats)
    assert result["plot_filters_verified"]["activation tau voltage cutoff"]=="volt_act_>=-10"
    assert result["statistics_rules_verified"]["rank test"]=="ranksums"


def test_missing_source_rules_fail_closed():
    with pytest.raises(ValueError,match="Released Figure 4 source rules missing"):
        M.validate_original_scripts("pass","pass")


def _table():
    row={"Filename":"H21.29.190.11.41.01.nwb","Species":"Human",
      "Vhalf_act":-5.0,"slopefactor_act":12.0,"gof_boltz_act":.95,
      "Vhalf_inact":-53.0,"slopefactor_inact":13.0,"gof_boltz_inact":.96,
      "rec_protocol_name":"K_IKrecv2_1_h0_DA_0","rec_fastfract":.4,"rec_ss":.7,
      "rec_tau1":200.0,"rec_tau2":2000.0}
    for i in range(1,M.NACT+1):
        row[f"volt_act_{i}"]=-60+(i-1)*10; row[f"tau_act_{i}"]=1.0+i
        row[f"gof_act_{i}"]=.9 if i>=6 else .6; row[f"G_Gmax_{i}"]=min(1.0,i/12)
        row[f"inactfract_{i}"]=.3
    for i in range(1,M.NINACT+1):
        row[f"volt_inact_{i}"]=-110+(i-1)*10; row[f"G_Gmax_inact_{i}"]=1-i/30
    for i in range(1,M.NKIN+1):
        row[f"volt_{i}"]=-60+(i-1)*10; row[f"fract_fast_{i}"]=.3
        row[f"fract_slow_{i}"]=.4; row[f"fract_steady_{i}"]=.3
        row[f"tau_inact_fast_{i}"]=20+i; row[f"tau_inact_slow_{i}"]=200+i
        row[f"gof_inact_{i}"]=.9
    for i in range(1,M.NREC+1):
        row[f"recdelay_{i}"]=50*i; row[f"amp1torec_{i}"]=.2+i*.05
    return pd.DataFrame([row,{**row,"Filename":"M21.07.301.11.41.01.nwb","Species":"Mouse"}])


def test_schema_validation_keeps_human_and_mouse_separate():
    df=_table(); result=M.validate_cells(df)
    assert result["rows"]==2
    assert result["cells_by_species"]=={"Human":1,"Mouse":1}
    with pytest.raises(ValueError,match="missing columns"):
        M.validate_cells(df.drop(columns=["tau_inact_slow_13"]))


def test_measurements_apply_original_filters_without_losing_cell_ids():
    rows,summaries=M.build_measurements(_table())
    act=[x for x in rows if x["variable"]=="tau_activation_ms" and x["Species"]=="Human"]
    assert sum(x["included_in_author_statistics"] for x in act)==7
    assert sum(not x["included_in_author_statistics"] for x in act)==5
    rec=[x for x in rows if x["variable"]=="recovery_fraction_of_first_current"]
    assert len(rec)==20 and {x["Species"] for x in rec}=={"Human","Mouse"}
    assert {x["Filename"] for x in rows}=={"H21.29.190.11.41.01.nwb","M21.07.301.11.41.01.nwb"}
    assert any(x["variable"]=="G_Gmax_inactivation" for x in rows)
    assert any(x["variable"]=="tau_inactivation_slow_ms" for x in rows)


def test_summary_tracks_missing_values_and_sem():
    out=M.summary([1.0,2.0,None,float("nan")])
    assert out["n"]==2 and out["missing"]==2
    assert out["mean"]==pytest.approx(1.5)
    assert out["sd"]==pytest.approx(np.sqrt(.5))
    assert out["sem"]==pytest.approx(.5)


def test_workbook_parser_selects_one_cell_table_sheet():
    data=_table(); payload=__import__("io").BytesIO()
    with pd.ExcelWriter(payload,engine="openpyxl") as w:
        data.to_excel(w,sheet_name="data",index=False)
        pd.DataFrame({"notes":[1]}).to_excel(w,sheet_name="notes",index=False)
    sheet,frame,info=M.read_workbook(payload.getvalue())
    assert sheet=="data" and len(frame)==2
    assert info["sheet_names"]==["data","notes"]
