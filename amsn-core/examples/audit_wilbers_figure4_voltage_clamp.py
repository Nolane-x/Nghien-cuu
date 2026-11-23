#!/usr/bin/env python3
"""Audit released Wilbers Figure 4 per-recording K voltage-clamp targets."""
from __future__ import annotations
import argparse, hashlib, json, math, re, sys, tempfile
from io import BytesIO
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
import audit_wilbers_k_mod_variants as audit

DATASET={"doi":"10.34894/L5J0SD","dataset_id":317867,"version":"3.0","license":"CC0-1.0"}
FILES={
 "workbook":{"id":318667,"path":"Figure4/data_fig4.xlsx","kind":"xlsx","bytes":108029,"sha1":"30ba48520d8d27a7f4db8aaa6abc7ae0f80ba7d3"},
 "plots":{"id":318536,"path":"Figure4/plots_fig4.py","kind":"python","bytes":5373,"sha1":"f9c4e70aba0760d00bb2ae911554c5e262fe8a7a"},
 "stats":{"id":318535,"path":"Figure4/stats_fig4.py","kind":"python"},
}
RECOVERY_PROTOCOL="K_IKrecv2_1_h0_DA_0"
NACT,NINACT,NKIN,NREC=12,20,13,10


def num(v):
    if v is None or pd.isna(v): return None
    x=float(v)
    return x if math.isfinite(x) else None


def summary(values):
    a=sorted(x for x in (num(v) for v in values) if x is not None)
    n=len(a); missing=len(values)-n
    if not n: return {"n":0,"missing":missing,"mean":None,"sd":None,"sem":None,"median":None,"q1":None,"q3":None}
    mean=float(np.mean(a)); sd=float(np.std(a,ddof=1)) if n>1 else 0.0
    return {"n":n,"missing":missing,"mean":mean,"sd":sd,"sem":sd/math.sqrt(n),"median":float(np.median(a)),
            "q1":float(np.quantile(a,.25)),"q3":float(np.quantile(a,.75))}


def validate_pins():
    w,p,s=FILES["workbook"],FILES["plots"],FILES["stats"]
    if (w["id"],w["bytes"],w["sha1"])!=(318667,108029,"30ba48520d8d27a7f4db8aaa6abc7ae0f80ba7d3"):
        raise ValueError("Figure 4 workbook immutable pin changed")
    if (p["id"],p["bytes"],p["sha1"])!=(318536,5373,"f9c4e70aba0760d00bb2ae911554c5e262fe8a7a"):
        raise ValueError("Figure 4 plot source immutable pin changed")
    if s["id"]!=318535: raise ValueError("Figure 4 statistics source ID changed")


def validate_original_scripts(plots,stats):
    pc=re.sub(r"\s+","",plots); sc=re.sub(r"\s+","",stats)
    plot_rules={
      "Vhalf activation fit quality":"gof_boltz_act>0.9",
      "Vhalf inactivation fit quality":"gof_boltz_inact>0.9",
      "activation tau voltage cutoff":"volt_act_>=-10",
      "activation tau fit quality":"gof_act_>0.8",
    }
    stats_rules={
      "normality test":"normaltest",
      "variance test":"bartlett",
      "parametric test":"ttest_ind",
      "rank test":"ranksums",
      "activation tau model":"tau_act_~C(Species)*I(volt_act_**2)",
      "fast inactivation tau model":"tau_inact_fast_~C(Species)*volt_",
      "slow inactivation tau model":"tau_inact_slow_~C(Species)*volt_",
    }
    missing_plot=[k for k,v in plot_rules.items() if v not in pc]
    missing_stats=[k for k,v in stats_rules.items() if v not in sc]
    if RECOVERY_PROTOCOL not in pc+sc:
        missing_plot.append("recovery protocol selection")
    if missing_plot or missing_stats:
        raise ValueError(f"Released Figure 4 source rules missing: plot={missing_plot}; stats={missing_stats}")
    refs=lambda x: sorted(set(re.findall(r"read_excel\(\s*r?['\"]([^'\"]+)",x)))
    local_refs={"plots":refs(plots),"stats":refs(stats)}
    mismatch=any("data_fig5.xlsx" in x for values in local_refs.values() for x in values)
    return {
      "plot_filters_verified":plot_rules,"statistics_rules_verified":stats_rules,
      "recovery_protocol":RECOVERY_PROTOCOL,"original_local_workbook_references":local_refs,
      "filename_mismatch_note":(
        "Public file is Figure4/data_fig4.xlsx, while released local scripts refer to Data/data_fig5.xlsx; "
        "the audit pins public file ID 318667 and validates its schema instead of guessing the local path."
        if mismatch else "No data_fig5.xlsx local-path reference was found."
      )
    }


def read_workbook(payload):
    xls=pd.ExcelFile(BytesIO(payload),engine="openpyxl")
    choices=[]
    for sheet in xls.sheet_names:
        df=pd.read_excel(BytesIO(payload),sheet_name=sheet,engine="openpyxl")
        if {"Filename","Species"}.issubset(df.columns): choices.append((sheet,df))
    if len(choices)!=1: raise ValueError(f"Expected one cell table sheet; found {[x[0] for x in choices]}")
    sheet,df=choices[0]; df.columns=[str(x).strip() for x in df.columns]
    if df.empty: raise ValueError("Figure 4 cell-data sheet is empty")
    return sheet,df,{"sheet_names":xls.sheet_names,"selected_sheet":sheet}


def required_columns(df):
    cols=["Filename","Species","Vhalf_act","slopefactor_act","gof_boltz_act",
          "Vhalf_inact","slopefactor_inact","gof_boltz_inact","rec_protocol_name",
          "rec_fastfract","rec_ss","rec_tau1","rec_tau2"]
    for prefix in ("volt_act","tau_act","gof_act","G_Gmax","inactfract"):
        cols += [f"{prefix}_{i}" for i in range(1,NACT+1)]
    for prefix in ("volt_inact","G_Gmax_inact"):
        cols += [f"{prefix}_{i}" for i in range(1,NINACT+1)]
    for prefix in ("volt","fract_fast","fract_slow","fract_steady","tau_inact_fast","tau_inact_slow"):
        cols += [f"{prefix}_{i}" for i in range(1,NKIN+1)]
    for prefix in ("recdelay","amp1torec"):
        cols += [f"{prefix}_{i}" for i in range(1,NREC+1)]
    missing=[x for x in cols if x not in df.columns]
    if missing: raise ValueError(f"Figure 4 workbook missing columns: {missing}")
    return cols


def validate_cells(df):
    required_columns(df)
    x=df.copy()
    x["Filename"]=x["Filename"].astype(str).str.strip()
    x["Species"]=x["Species"].astype(str).str.strip()
    if x["Filename"].isin(["","nan","None"]).any(): raise ValueError("Missing Filename")
    if x["Filename"].duplicated().any(): raise ValueError("Duplicate recording Filename")
    unexpected=sorted(set(x["Species"])-{"Human","Mouse"})
    if unexpected or set(x["Species"])!={"Human","Mouse"}: raise ValueError(f"Unexpected species labels: {unexpected or x['Species'].unique().tolist()}")
    subjects={}
    for species in ("Human","Mouse"):
        ids=[]
        for filename in x.loc[x.Species==species,"Filename"]:
            parts=filename.split(".")
            if len(parts)<3: raise ValueError(f"Unexpected original Filename structure: {filename}")
            ids.append(parts[2])
        subjects[species]=len(set(ids))
    return {"rows":int(len(x)),"unique_cells":int(x.Filename.nunique()),
            "cells_by_species":{s:int(x.loc[x.Species==s,"Filename"].nunique()) for s in ("Human","Mouse")},
            "subjects_by_species":subjects,"species_values":sorted(x.Species.unique().tolist())}


def append(rows,record,variable,value,voltage=None,protocol="",fit=None,stats_ok=True,plot_ok=True,columns=""):
    value=num(value)
    if value is None: return
    rows.append({"Filename":str(record["Filename"]),"Species":str(record["Species"]),
        "variable":variable,"voltage_mV":num(voltage),"value":value,"protocol":protocol,
        "fit_quality":num(fit),"included_in_author_statistics":bool(stats_ok),
        "included_in_author_plot":bool(plot_ok),"source_columns":columns})


def build_measurements(df):
    rows=[]
    for rec in df.to_dict(orient="records"):
        for variable,col,gofcol in (("Vhalf_activation_mV","Vhalf_act","gof_boltz_act"),
                                    ("Vhalf_inactivation_mV","Vhalf_inact","gof_boltz_inact")):
            fit=num(rec.get(gofcol)); ok=fit is not None and fit>.9
            append(rows,rec,variable,rec.get(col),fit=fit,stats_ok=ok,plot_ok=ok,columns=f"{col};{gofcol}")
        for i in range(1,NACT+1):
            v=rec.get(f"volt_act_{i}"); gof=num(rec.get(f"gof_act_{i}"))
            ok=num(v) is not None and num(v)>=-10 and gof is not None and gof>.8
            append(rows,rec,"G_Gmax_activation",rec.get(f"G_Gmax_{i}"),v,
                   columns=f"volt_act_{i};G_Gmax_{i}")
            append(rows,rec,"tau_activation_ms",rec.get(f"tau_act_{i}"),v,fit=gof,
                   stats_ok=ok,plot_ok=ok,columns=f"volt_act_{i};tau_act_{i};gof_act_{i}")
        for i in range(1,NINACT+1):
            append(rows,rec,"G_Gmax_inactivation",rec.get(f"G_Gmax_inact_{i}"),rec.get(f"volt_inact_{i}"),
                   columns=f"volt_inact_{i};G_Gmax_inact_{i}")
        for i in range(1,NKIN+1):
            v=rec.get(f"volt_{i}"); fit=rec.get(f"gof_inact_{i}")
            append(rows,rec,"tau_inactivation_fast_ms",rec.get(f"tau_inact_fast_{i}"),v,fit=fit,
                   stats_ok=True,plot_ok=num(v) is not None and num(v)>=0,
                   columns=f"volt_{i};tau_inact_fast_{i};gof_inact_{i}")
            append(rows,rec,"tau_inactivation_slow_ms",rec.get(f"tau_inact_slow_{i}"),v,fit=fit,
                   columns=f"volt_{i};tau_inact_slow_{i};gof_inact_{i}")
            for variable,prefix in (("fraction_fast_inactivation","fract_fast"),
                                    ("fraction_slow_inactivation","fract_slow"),
                                    ("fraction_steady_inactivation","fract_steady")):
                append(rows,rec,variable,rec.get(f"{prefix}_{i}"),v,fit=fit,
                       columns=f"volt_{i};{prefix}_{i};gof_inact_{i}")
        if str(rec.get("rec_protocol_name","")).strip()==RECOVERY_PROTOCOL:
            for i in range(1,NREC+1):
                append(rows,rec,"recovery_fraction_of_first_current",rec.get(f"amp1torec_{i}"),
                       rec.get(f"recdelay_{i}"),protocol=RECOVERY_PROTOCOL,
                       columns=f"recdelay_{i};amp1torec_{i}")
            for variable,col in (("recovery_fast_tau_ms","rec_tau1"),("recovery_slow_tau_ms","rec_tau2"),
                                 ("recovery_fast_fraction","rec_fastfract"),("recovery_steady_fraction","rec_ss")):
                append(rows,rec,variable,rec.get(col),protocol=RECOVERY_PROTOCOL,columns=col)
    if not rows: raise ValueError("No nonmissing Figure 4 observations extracted")
    measurements=pd.DataFrame(rows)
    grouped=measurements.groupby(["Species","variable","voltage_mV","protocol"],dropna=False)
    summaries=[]
    for (species,variable,voltage,protocol),group in grouped:
        selected=group.loc[group.included_in_author_statistics,"value"].tolist()
        s=summary(selected)
        summaries.append({"Species":species,"variable":variable,"voltage_mV":voltage,"protocol":protocol,
          "n_observed":len(group),"n_in_author_statistics":s["n"],
          "n_excluded_by_author_filter":len(group)-s["n"],
          **{k:s[k] for k in ("mean","sd","sem","median","q1","q3")}})
    return rows,summaries


def scalar_audit(df):
    result={}
    for species in ("Human","Mouse"):
        c=df.loc[df.Species==species]
        r=c.loc[c.rec_protocol_name.astype(str).str.strip()==RECOVERY_PROTOCOL]
        act=c.loc[pd.to_numeric(c.gof_boltz_act,errors="coerce")>.9,"Vhalf_act"].tolist()
        inact=c.loc[pd.to_numeric(c.gof_boltz_inact,errors="coerce")>.9,"Vhalf_inact"].tolist()
        n_tau=0
        for rec in c.to_dict(orient="records"):
            for i in range(1,NACT+1):
                if num(rec.get(f"volt_act_{i}")) is not None and num(rec[f"volt_act_{i}"])>=-10 and num(rec.get(f"gof_act_{i}")) is not None and num(rec[f"gof_act_{i}"])>.8 and num(rec.get(f"tau_act_{i}")) is not None:
                    n_tau+=1
        result[species]={"cell_count":int(c.Filename.nunique()),
          "vhalf_activation_gof_gt_0_9":summary(act),
          "vhalf_inactivation_gof_gt_0_9":summary(inact),
          "activation_tau_points_voltage_ge_minus_10_gof_gt_0_8":n_tau,
          "recovery":{"protocol":RECOVERY_PROTOCOL,"recording_count":int(r.Filename.nunique()),
             "fast_tau_ms":summary(r.rec_tau1.tolist()),"slow_tau_ms":summary(r.rec_tau2.tolist()),
             "fast_fraction":summary(r.rec_fastfract.tolist()),"steady_fraction":summary(r.rec_ss.tolist())}}
    return result


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: raise ValueError(f"Empty CSV: {path}")
    pd.DataFrame(rows).to_csv(path,index=False,float_format="%.12g")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-json",type=Path,default=Path("results/wilbers_figure4_voltage_clamp_audit_2026-11-23.json"))
    p.add_argument("--per-recording-csv",type=Path,default=Path("results/wilbers_figure4_voltage_clamp_per_recording_2026-11-23.csv"))
    p.add_argument("--cohort-summary-csv",type=Path,default=Path("results/wilbers_figure4_voltage_clamp_cohort_summary_2026-11-23.csv"))
    args=p.parse_args(); validate_pins()
    with tempfile.TemporaryDirectory(prefix="wilbers-figure4-audit-") as tmp:
        cache=Path(tmp); payloads={}; integrity={}
        for name,spec in FILES.items(): payloads[name],integrity[name]=audit.fetch_verified(name,spec,cache)
        for name in ("workbook","plots"):
            spec,observed=FILES[name],integrity[name]
            if observed["id"]!=spec["id"] or observed["bytes"]!=spec["bytes"] or observed["observed_sha1"].lower()!=spec["sha1"]:
                raise RuntimeError(f"Immutable source pin mismatch: {name}")
        plots=payloads["plots"].decode("utf-8-sig"); stats=payloads["stats"].decode("utf-8-sig")
        rules=validate_original_scripts(plots,stats)
        sheet,df,excel_info=read_workbook(payloads["workbook"])
        cell_info=validate_cells(df); records,cohort=build_measurements(df)
        scalars=scalar_audit(df)
        report={"schema_version":1,"status":"official_figure4_voltage_clamp_workbook_verified_and_per_recording_audited",
          "model_validation_performed":False,"dataset":DATASET,"files":integrity,
          "workbook":{"sheet":sheet,**excel_info,"column_count":len(df.columns),"columns":[str(c) for c in df.columns],
            "table_audit":cell_info,"source_sha256":hashlib.sha256(payloads["workbook"]).hexdigest()},
          "original_analysis_scripts":rules,
          "author_filter_semantics":{
            "activation_vhalf":"gof_boltz_act > 0.9","inactivation_vhalf":"gof_boltz_inact > 0.9",
            "activation_tau":"volt_act >= -10 mV and gof_act > 0.8",
            "inactivation_tau":"all nonmissing fast/slow tau values in released stats script; no fit-quality cutoff",
            "fast_inactivation_tau_plot":"volt >= 0 mV","recovery":f"rec_protocol_name == {RECOVERY_PROTOCOL}",
            "subject_count":"third token of Filename split by '.', matching original count_n convention"},
          "scalar_audit":scalars,"measurement_row_count":len(records),"summary_row_count":len(cohort),
          "scientific_limits":[
            "The Figure 4 workbook is a per-recording derived-measurement table, not raw voltage/current time-series traces.",
            "The workbook retains cell-level Vhalf/slope/fit measures and voltage-indexed activation, inactivation, kinetics and recovery observations.",
            "Human and Mouse groups remain separate; no pooled average is used.",
            "Original plot/statistics script filters are inspected and reproduced before summary.",
            "This phase audits experimental endpoints; it does not yet run the nine K MOD equations on independent voltage steps.",
            "The AP-clamp model ranking is not reused as an independent voltage-clamp fit result.",
            "No MOD source, canonical defaults, AP-clamp output or AMSN runtime is modified."
          ]}
        args.output_json.parent.mkdir(parents=True,exist_ok=True)
        args.output_json.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
        write_csv(args.per_recording_csv,records); write_csv(args.cohort_summary_csv,cohort)
        print(json.dumps({"status":report["status"],"cells":cell_info["cells_by_species"],
          "subjects":cell_info["subjects_by_species"],"measurements":len(records),"summaries":len(cohort),
          "recovery_recordings":{s:x["recovery"]["recording_count"] for s,x in scalars.items()},
          "sources":{k:{"id":v["id"],"bytes":v["bytes"],"sha1":v["observed_sha1"]} for k,v in integrity.items()},
          "outputs":[str(args.output_json),str(args.per_recording_csv),str(args.cohort_summary_csv)]},indent=2,allow_nan=False))


if __name__=="__main__": main()
