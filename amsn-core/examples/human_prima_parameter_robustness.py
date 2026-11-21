"""Human passive PRIMA robustness to +/-20% passive-parameter changes."""
from __future__ import annotations
import csv, os
from pathlib import Path
import numpy as np
import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.cable import CableTree, PassiveParameters
from amsn.morphology import SWCMorphology
from amsn.prima import prima_reduce_passive_cable_multishift, reproject_passive_cable_basis

LABEL=os.environ["AMSN_MORPHOLOGY_LABEL"]
SWC=Path(os.environ["AMSN_MORPHOLOGY_PATH"])
EXPECTED=int(os.environ["AMSN_EXPECTED_SWC_RECORDS"])
ORDER=int(os.environ.get("AMSN_PRIMA_PARAMETER_ORDER","56"))
FREQS=(0.1,1.0,10.0,100.0,300.0,1000.0,3000.0,6000.0,10000.0)
SHIFTS=(0.0,100.0,1000.0,3000.0)

def port_z(tree, ports, hz):
    z=np.empty((len(ports),len(ports)),dtype=np.complex128)
    for j,source in enumerate(ports):
        current=np.zeros(tree.n_compartments,dtype=np.complex128)
        current[source]=1.0
        z[:,j]=tree.solve_passive_frequency_response(hz,current)[ports]
    return z

def transient(tree, model, ports, source):
    dt=1e-4; steps=200; rev=tree.parameters.e_leak_v
    v=np.full(tree.n_compartments,rev); x=np.zeros(model.order)
    fi=np.zeros(tree.n_compartments); pi=np.zeros(len(ports))
    full=[]; reduced=[]
    for k in range(steps):
        fi.fill(0.0); pi.fill(0.0)
        if 0.002 <= k*dt < 0.012:
            fi[ports[source]]=10e-12; pi[source]=10e-12
        v=tree.step_passive(v,dt,fi)
        x=model.step_backward_euler(x,dt,pi)
        full.append(v[ports]-rev); reduced.append(model.port_voltages(x))
    full=np.asarray(full); reduced=np.asarray(reduced); err=reduced-full
    overall=100*np.linalg.norm(err)/max(np.linalg.norm(full),1e-30)
    port=np.linalg.norm(err,axis=0)/np.maximum(np.linalg.norm(full,axis=0),1e-30)*100
    return float(overall),float(np.max(port)),int(np.argmax(port))

def main():
    reference.DATA=SWC
    reference.MAX_NEURON_SEGMENT_UM=0.125
    morph=SWCMorphology.from_file(SWC)
    if len(morph.nodes)!=EXPECTED: raise RuntimeError("SWC count mismatch")
    reader,sections=reference.import_swc_with_neuron()
    injections,probes,sites=fine_audit.build_sites(morph,reader,sections)
    ids=list(dict.fromkeys([i for _,i in injections+probes]))
    if len(ids)!=7: raise RuntimeError("expected seven unique ports")
    mapping=morph.electrical_node_mapping()
    names={nid:f"swc_{mapping[nid]}" for nid in morph.nodes}
    base=morph.to_cable_tree()
    ports=[base.index[names[nid]] for nid in ids]
    basal_id=next(nid for name,nid in injections if name=="basal_q75")
    source=ids.index(basal_id)
    p0=base.parameters
    nominal=prima_reduce_passive_cable_multishift(base,ports,ORDER,SHIFTS)
    cases={
      "nominal":(1,1,1),"Rm_minus20":(.8,1,1),"Rm_plus20":(1.2,1,1),
      "Cm_minus20":(1,.8,1),"Cm_plus20":(1,1.2,1),
      "Ra_minus20":(1,1,.8),"Ra_plus20":(1,1,1.2),
      "all_minus20":(.8,.8,.8),"all_plus20":(1.2,1.2,1.2)
    }
    rows=[]
    for case,(rm,cm,ra) in cases.items():
        p=PassiveParameters(p0.specific_capacitance_f_m2*cm,
          p0.specific_membrane_resistance_ohm_m2*rm,
          p0.axial_resistivity_ohm_m*ra,p0.e_leak_v)
        target=CableTree([base.by_name[n] for n in base.order],p)
        frozen=reproject_passive_cable_basis(base,target,nominal)
        fresh=prima_reduce_passive_cable_multishift(target,ports,ORDER,SHIFTS)
        for model in (frozen,fresh):
            np.linalg.cholesky(model.conductance_matrix_s)
            np.linalg.cholesky(model.capacitance_matrix_f)
        metrics={}
        for tag,model in (("frozen",frozen),("fresh",fresh)):
            ze=[]; ye=[]
            for hz in FREQS:
                z0=port_z(target,ports,hz); y0=np.linalg.solve(z0,np.eye(len(ports)))
                zr=model.impedance_matrix(hz); yr=np.linalg.solve(zr,np.eye(len(ports)))
                ze.append((100*np.linalg.norm(zr-z0)/max(np.linalg.norm(z0),1e-30),hz))
                ye.append((100*np.linalg.norm(yr-y0)/max(np.linalg.norm(y0),1e-30),hz))
            tr=transient(target,model,ports,source)
            metrics[tag+"_max_Z_error_pct"],metrics[tag+"_max_Z_hz"]=max(ze)
            metrics[tag+"_max_Y_error_pct"],metrics[tag+"_max_Y_hz"]=max(ye)
            metrics[tag+"_all_ports_transient_nrmse_pct"]=tr[0]
            metrics[tag+"_max_port_transient_nrmse_pct"]=tr[1]
            metrics[tag+"_worst_port_index"]=tr[2]
        rows.append({"morphology_label":LABEL,"scenario":case,"Rm_scale":rm,"Cm_scale":cm,"Ra_scale":ra,
          "full_compartment_order":target.n_compartments,"reduced_order":frozen.order,
          "state_reduction_pct":100*(1-frozen.order/target.n_compartments),**metrics,
          "passivity_check":"passed"})
    output=Path(__file__).parents[1]/"results"/f"{LABEL}_human_prima_parameter_robustness_2026-11-21.csv"
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"morphology={LABEL}; compartments={base.n_compartments}; ports={len(ports)}; order={nominal.order}")
    for r in rows:
        print("scenario=%s; frozen_Z=%.9g%%; frozen_Y=%.9g%%; fresh_Z=%.9g%%; fresh_Y=%.9g%%; frozen_transient=%.9g%%" %
          (r["scenario"],r["frozen_max_Z_error_pct"],r["frozen_max_Y_error_pct"],
           r["fresh_max_Z_error_pct"],r["fresh_max_Y_error_pct"],r["frozen_max_port_transient_nrmse_pct"]))
    print(f"output_csv={output}; rows={len(rows)}; passivity=passed")

if __name__=="__main__": main()
