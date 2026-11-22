#!/usr/bin/env python3
"""Reproduce the equal-order seven-vs-nine-port PRIMA analysis.

Unzip the 7-port and 9-port Actions artifacts into separate directories. Each
directory must contain the six matching transient-sweep CSVs. Only the Python
standard library is required; matching uses exact SWC node IDs.
"""
from __future__ import annotations
import argparse, csv, math, statistics
from collections import Counter
from pathlib import Path

DATE="2026-11-22"
ORDERS=(56,112,168)
MODELS={"four_shift_order56_control", *(f"six_shift_order{x}" for x in ORDERS)}
MORPHOLOGIES={"NMO_68174_cell1125","NMO_68175_cell1204","NMO_290988_Mohan2015"}
MESHES={"0.125","0.0625"}
SCENARIOS=6

def read_inputs(directory: Path, ports: int):
    pattern=f"*_ordermatch_{ports}port_human_passive_prima_extended_order_transient_sweep_{DATE}.csv"
    paths=sorted(directory.rglob(pattern))
    if len(paths)!=6:
        raise ValueError(f"expected six {ports}-port CSVs in {directory}; found {len(paths)}")
    data={}
    for path in paths:
        morph=path.name.split("_mesh",1)[0]
        mesh=path.name.split("_mesh",1)[1].split("um_",1)[0]
        key=(morph,mesh)
        if key in data: raise ValueError(f"duplicate configuration: {key}")
        with path.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        expected=232 if ports==7 else 280
        metric_counts=Counter(r["metric"] for r in rows)
        required=Counter({"frequency_response":40,"transient_port":SCENARIOS*ports*4,"transient_all_ports":SCENARIOS*4})
        if len(rows)!=expected or metric_counts!=required:
            raise ValueError(f"row/metric coverage mismatch in {path.name}: {len(rows)}, {dict(metric_counts)}")
        if {r["model_id"] for r in rows}!=MODELS:
            raise ValueError(f"model identity mismatch in {path.name}")
        for mid in MODELS:
            mr=[r for r in rows if r["model_id"]==mid]
            if Counter(r["metric"] for r in mr)!=Counter({"frequency_response":10,"transient_port":SCENARIOS*ports,"transient_all_ports":SCENARIOS}):
                raise ValueError(f"per-model coverage mismatch: {path.name} {mid}")
            fr=[r for r in mr if r["metric"]=="frequency_response"]
            rank=56 if mid=="four_shift_order56_control" else int(mid.removeprefix("six_shift_order"))
            if {int(r["requested_order"]) for r in fr}!={rank} or {int(r["prima_order"]) for r in fr}!={rank}:
                raise ValueError(f"requested/achieved PRIMA rank mismatch: {path.name} {mid}")
            if len({float(r["frequency_hz"]) for r in fr})!=10:
                raise ValueError(f"frequency coverage mismatch: {path.name} {mid}")
            tr=[r for r in mr if r["metric"]=="transient_port"]
            pairs={(r["scenario_id"],r["port_swc_id"]) for r in tr}
            per_scenario=Counter(r["scenario_id"] for r in tr)
            if len(pairs)!=SCENARIOS*ports or len(per_scenario)!=SCENARIOS or any(n!=ports for n in per_scenario.values()):
                raise ValueError(f"transient scenario/SWC-node coverage mismatch: {path.name} {mid}")
            if any(not node for _,node in pairs): raise ValueError(f"empty SWC node id: {path.name} {mid}")
        data[key]=rows
    if {m for m,_ in data}!=MORPHOLOGIES or {mesh for _,mesh in data}!=MESHES:
        raise ValueError(f"morphology/mesh matrix incomplete for {ports}-port data: {sorted(data)}")
    return data

def write_csv(path: Path, rows):
    if not rows: raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def analyze(seven,nine,out:Path):
    if set(seven)!=set(nine): raise ValueError("7-port and 9-port configuration sets differ")
    pairs=[]; rms_rows=[]; q25_rows=[]
    for (morph,mesh),rows7 in sorted(seven.items()):
        rows9=nine[(morph,mesh)]
        for order in ORDERS:
            mid=f"six_shift_order{order}"
            a=[r for r in rows7 if r["metric"]=="transient_port" and r["model_id"]==mid]
            b=[r for r in rows9 if r["metric"]=="transient_port" and r["model_id"]==mid]
            da={(r["scenario_id"],r["port_swc_id"]):r for r in a}
            db={(r["scenario_id"],r["port_swc_id"]):r for r in b}
            common=set(da)&set(db); only7=set(da)-set(db); only9=set(db)-set(da)
            if len(common)!=42 or only7 or len(only9)!=12:
                raise ValueError(f"shared/q25 port mismatch: {(morph,mesh,order)} {len(common)} {len(only7)} {len(only9)}")
            for scenario,node in sorted(common):
                e7=float(da[(scenario,node)]["transient_port_nrmse_pct"])
                e9=float(db[(scenario,node)]["transient_port_nrmse_pct"])
                if not (math.isfinite(e7) and math.isfinite(e9) and e7>=0 and e9>=0):
                    raise ValueError(f"invalid NRMSE for {(morph,mesh,order,scenario,node)}")
                ratio=e9/e7 if e7 else (1.0 if e9==0 else math.inf)
                pairs.append({"morphology":morph,"mesh_um":mesh,"order":order,"scenario_id":scenario,"port_swc_id":node,"port_roles":da[(scenario,node)]["port_roles"],"seven_port_error_pct":e7,"nine_port_error_pct":e9,"error_ratio_9_over_7":ratio,"change_pct":(ratio-1)*100 if math.isfinite(ratio) else "inf"})
            for scenario in sorted({s for s,_ in common}):
                nodes=sorted(n for s,n in common if s==scenario)
                v7=[float(da[(scenario,n)]["transient_port_nrmse_pct"]) for n in nodes]
                v9=[float(db[(scenario,n)]["transient_port_nrmse_pct"]) for n in nodes]
                x=math.sqrt(sum(v*v for v in v7)/len(v7)); y=math.sqrt(sum(v*v for v in v9)/len(v9))
                rms_rows.append({"morphology":morph,"mesh_um":mesh,"order":order,"scenario_id":scenario,"seven_shared_ports_rms_nrmse_pct":x,"nine_shared_ports_rms_nrmse_pct":y,"ratio_9_over_7":y/x if x else math.inf})
            for scenario,node in sorted(only9):
                r=db[(scenario,node)]
                q25_rows.append({"morphology":morph,"mesh_um":mesh,"order":order,"scenario_id":scenario,"port_swc_id":node,"port_roles":r["port_roles"],"nine_port_q25_nrmse_pct":float(r["transient_port_nrmse_pct"])})

    pair_summary=[]
    for order in ORDERS:
        p=[r for r in pairs if r["order"]==order]; ratios=[r["error_ratio_9_over_7"] for r in p]
        q=[r["ratio_9_over_7"] for r in rms_rows if r["order"]==order]
        pair_summary.append({"order":order,"matched_shared_port_pairs":len(p),"nine_port_regressions":sum(x>1+1e-9 for x in ratios),"nine_port_improvements":sum(x<1-1e-9 for x in ratios),"ties_within_1e-9_ratio":sum(abs(x-1)<=1e-9 for x in ratios),"median_error_ratio_9_over_7":statistics.median(ratios),"mean_error_ratio_9_over_7":statistics.mean(ratios),"worst_error_ratio_9_over_7":max(ratios),"best_error_ratio_9_over_7":min(ratios),"median_shared_port_rms_ratio_9_over_7":statistics.median(q),"max_shared_port_rms_ratio_9_over_7":max(q),"max_seven_port_single_output_nrmse_pct":max(r["seven_port_error_pct"] for r in p),"max_nine_port_single_output_nrmse_pct":max(r["nine_port_error_pct"] for r in p)})

    frequency=[]; transient=[]
    for ports,configs in ((7,seven),(9,nine)):
        for order in ORDERS:
            mid=f"six_shift_order{order}"
            fr=[r for rows in configs.values() for r in rows if r["metric"]=="frequency_response" and r["model_id"]==mid]
            tr=[r for rows in configs.values() for r in rows if r["metric"]=="transient_port" and r["model_id"]==mid]
            ar=[r for rows in configs.values() for r in rows if r["metric"]=="transient_all_ports" and r["model_id"]==mid]
            mx=lambda field:max(float(r[field]) for r in fr)
            reductions=[float(r["state_count_reduction_pct"]) for r in fr]
            frequency.append({"port_count":ports,"order":order,"state_reduction_min_pct":min(reductions),"state_reduction_max_pct":max(reductions),"max_impedance_vs_hines_pct":mx("impedance_vs_hines_pct"),"max_admittance_vs_hines_pct":mx("admittance_vs_hines_pct"),"max_impedance_vs_neuron_pct":mx("impedance_vs_neuron_pct"),"max_admittance_vs_neuron_pct":mx("admittance_vs_neuron_pct"),"max_neuron_impedance_condition":mx("neuron_impedance_condition")})
            pe=[float(r["transient_port_nrmse_pct"]) for r in tr]; ae=[float(r["transient_port_nrmse_pct"]) for r in ar]
            transient.append({"port_count":ports,"order":order,"individual_port_rows":len(pe),"median_individual_port_nrmse_pct":statistics.median(pe),"max_individual_port_nrmse_pct":max(pe),"all_port_scenario_rows":len(ae),"median_all_port_nrmse_pct":statistics.median(ae),"max_all_port_nrmse_pct":max(ae)})

    q25_summary=[]
    for order in ORDERS:
        v=[r["nine_port_q25_nrmse_pct"] for r in q25_rows if r["order"]==order]
        q25_summary.append({"order":order,"q25_output_rows":len(v),"median_q25_nrmse_pct":statistics.median(v),"max_q25_nrmse_pct":max(v),"min_q25_nrmse_pct":min(v)})
    out.mkdir(parents=True,exist_ok=True)
    tables={"equal_order_shared_port_pairs":pairs,"equal_order_shared_port_rms":rms_rows,"equal_order_shared_port_summary":pair_summary,"equal_order_q25_only":q25_rows,"equal_order_q25_summary":q25_summary,"equal_order_frequency_error_summary":frequency,"equal_order_transient_error_summary":transient}
    for name,rows in tables.items(): write_csv(out/f"{name}_{DATE}.csv",rows)
    print(f"Validated 6 morphology/mesh pairs; {len(pairs)} shared-port pairs; {len(q25_rows)} q25-only observations.")
    for row in pair_summary: print(row)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seven-dir",type=Path,required=True)
    p.add_argument("--nine-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    analyze(read_inputs(a.seven_dir,7),read_inputs(a.nine_dir,9),a.output_dir)

if __name__=="__main__": main()
