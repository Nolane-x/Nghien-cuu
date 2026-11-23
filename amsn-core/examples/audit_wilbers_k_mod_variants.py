#!/usr/bin/env python3
"""Audit released Wilbers potassium MOD variants against the canonical human K MOD."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, tempfile, time, urllib.error, urllib.request
from pathlib import Path
from typing import Any

BASE="https://dataverse.nl/api"
SOURCES={
 "k_human":{"id":318647,"path":"Figures5_6/MOD/k_human.mod","kind":"mod"},
 "k_mouse":{"id":318649,"path":"Figures5_6/MOD/k_mouse.mod","kind":"mod"},
 "k_human_h1":{"id":318627,"path":"Figures5_6/MOD/k_human_h1.mod","kind":"mod"},
 "k_human_hm12inf":{"id":318604,"path":"Figures5_6/MOD/k_human_hm12inf.mod","kind":"mod"},
 "k_hybrid1":{"id":318628,"path":"Figures5_6/MOD/k_hybrid1.mod","kind":"mod"},
 "k_hybrid2":{"id":318622,"path":"Figures5_6/MOD/k_hybrid2.mod","kind":"mod"},
 "k_hybrid3":{"id":318609,"path":"Figures5_6/MOD/k_hybrid3.mod","kind":"mod"},
 "k_hybrid4":{"id":318619,"path":"Figures5_6/MOD/k_hybrid4.mod","kind":"mod"},
 "k_hybrid5":{"id":318605,"path":"Figures5_6/MOD/k_hybrid5.mod","kind":"mod"},
 "channel_kinetics":{"id":326241,"path":"Figures5_6/Channel_fitting/channel_kinetics.py","kind":"python"},
 "channel_tools":{"id":326242,"path":"Figures5_6/Channel_fitting/channel_tools.py","kind":"python"},
 "fit_k_human":{"id":326237,"path":"Figures5_6/Channel_fitting/fit_k_hh_cma_human.py","kind":"python"},
 "fit_k_mouse":{"id":326240,"path":"Figures5_6/Channel_fitting/fit_k_hh_cma_mouse.py","kind":"python"},
}
HYBRID_ROLES={
 "k_hybrid1":"human G/Gmax activation + inactivation",
 "k_hybrid2":"human G/Gmax activation",
 "k_hybrid3":"human G/Gmax inactivation",
 "k_hybrid4":"human activation time constant",
 "k_hybrid5":"human G/Gmax activation + activation time constant",
}
GROUPS={
 "mixture_and_slow_inactivation":("prop_inact","prop_h2","h2tau_inact","h2tau_inact_rec","inact_rate_factor"),
 "activation":("tha","qa","Ra","th_act_inf","q_act_inf"),
 "inactivation_kinetics":("thi1","thi2","qi1","qi2","Rd","Rg"),
}
NUM=r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"

def fetch_verified(name:str,spec:dict[str,Any],cache:Path):
    metadata=None; meta_attempts=[]
    for attempt in range(5):
        try:
            req=urllib.request.Request(
                f"{BASE}/files/{spec['id']}",
                headers={"User-Agent":"AMSN-Wilbers-K-variant-audit/1.0","Accept":"application/json","Cache-Control":"no-cache"},
            )
            with urllib.request.urlopen(req,timeout=60) as r:
                body=r.read(); content_type=r.headers.get("Content-Type"); status=r.status
            if not body: raise ValueError("empty Dataverse metadata response")
            metadata=json.loads(body)["data"]["dataFile"]
            meta_attempts.append({"attempt":attempt+1,"status":status,"content_type":content_type,"body_bytes":len(body),"result":"ok"})
            break
        except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError,ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
            meta_attempts.append({"attempt":attempt+1,"error":repr(e)})
            if attempt<4: time.sleep((1.5,3,6,10)[attempt])
    if metadata is None: raise RuntimeError(f"Dataverse metadata unavailable for {name}: {json.dumps(meta_attempts)}")
    expected_sha1=str(metadata["checksum"]["value"]).lower()
    expected_bytes=int(metadata["filesize"])
    expected_name=str(metadata.get("filename") or "")
    if expected_name and Path(spec["path"]).name!=expected_name:
        raise RuntimeError(f"Dataverse ID/name mismatch for {name}: metadata={expected_name}")
    attempts=[]
    for url in (f"{BASE}/access/datafile/{spec['path']}/{spec['id']}",f"{BASE}/access/datafile/{spec['id']}"):
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"AMSN-Wilbers-K-variant-audit/1.0","Accept":"*/*","Cache-Control":"no-cache","Pragma":"no-cache"})
                with urllib.request.urlopen(req,timeout=120) as r:
                    data=r.read(); content_type=r.headers.get("Content-Type"); final_url=r.url.split("?")[0]; status=r.status
                if not data: raise ValueError("empty data response")
                sha1=hashlib.sha1(data).hexdigest(); sha256=hashlib.sha256(data).hexdigest()
                attempts.append({"url":url,"attempt":attempt+1,"status":status,"content_type":content_type,"final_url":final_url,"bytes":len(data),"sha1":sha1,"sha256":sha256})
                if len(data)==expected_bytes and sha1==expected_sha1:
                    (cache/Path(spec["path"]).name).write_bytes(data)
                    return data,{"id":spec["id"],"path":spec["path"],"bytes":len(data),"official_sha1":expected_sha1,"observed_sha1":sha1,"sha256":sha256,"metadata_attempts":meta_attempts,"download_attempts":attempts}
                if attempt<2: time.sleep((2,5)[attempt])
            except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError,ValueError) as e:
                attempts.append({"url":url,"attempt":attempt+1,"error":repr(e)})
                if attempt<2: time.sleep((2,5)[attempt])
    raise RuntimeError(f"Source payload failed official Dataverse SHA-1/size for {name}: {json.dumps({'metadata':meta_attempts,'downloads':attempts},sort_keys=True)}")

def parse_mod_parameters(text:str):
    suffix=re.search(r"\bSUFFIX\s+([A-Za-z_]\w*)",text)
    block=re.search(r"\bPARAMETER\s*\{(.*?)\}",text,re.S)
    range_line=re.search(r"\bRANGE\s+([^\n]+)",text)
    if not suffix or not block: raise ValueError("MOD needs SUFFIX and PARAMETER block")
    values={}
    for raw in block.group(1).splitlines():
        line=raw.split(":",1)[0].strip()
        m=re.match(rf"^([A-Za-z_]\w*)\s*=\s*({NUM})",line)
        if m: values[m.group(1)]=float(m.group(2))
    return {"suffix":suffix.group(1),"range":range_line.group(1).strip() if range_line else "","parameters":values}

def compare_parameters(canonical,variant):
    changes=[]
    for name in sorted(set(canonical)|set(variant)):
        a=canonical.get(name); b=variant.get(name)
        if a is None or b is None:
            if a!=b: changes.append({"parameter":name,"canonical":a,"variant":b,"kind":"added_or_removed"})
        elif abs(a-b)>max(1e-14,abs(a)*1e-10):
            changes.append({"parameter":name,"canonical":a,"variant":b,"absolute_delta":b-a,"relative_delta_pct":100*(b-a)/a if a else None})
    names={x["parameter"] for x in changes}
    groups={k:sorted(names.intersection(v)) for k,v in GROUPS.items()}
    groups["other"]=sorted(names.difference({n for v in GROUPS.values() for n in v}))
    return {"change_count":len(changes),"changed_parameters":changes,"changed_parameter_groups":groups}

def function_source(source,name):
    m=re.search(rf"(?ms)^def\s+{re.escape(name)}\s*\(.*?(?=^def\s+|\Z)",source)
    return m.group(0).strip() if m else None

def fit_context(channel_tools,fit_human,fit_mouse,kinetics):
    k_iv=function_source(channel_tools,"K_IV_ss")
    if not k_iv: raise RuntimeError("channel_tools.py K_IV_ss missing")
    def vectors(source):
        out=[]
        for m in re.finditer(r"fitparams\s*=\s*\[(.*?)\]",source,re.S):
            names=re.findall(r"['\"]([^'\"]+)['\"]",m.group(1))
            if names: out.append(names)
        return out
    human_vectors=vectors(fit_human); mouse_vectors=vectors(fit_mouse)
    fitted={n.split("_k_")[0] for vector in human_vectors+mouse_vectors for n in vector}
    mixture=("prop_inact","prop_h2","h2tau_inact","h2tau_inact_rec","inact_rate_factor")
    roles={n:v for n,v in HYBRID_ROLES.items() if re.search(rf"k_mech_IV\(['\"]{n}['\"]",kinetics)}
    return {
        "k_iv_ss_source_function":k_iv,
        "human_fit_parameter_vectors":human_vectors,
        "mouse_fit_parameter_vectors":mouse_vectors,
        "mixture_parameters_absent_from_fit_vectors":{n:n not in fitted for n in mixture},
        "hybrid_roles_from_original_channel_kinetics_source":roles,
    }

def compile_mod(payload,suffix,root):
    folder=root/suffix; folder.mkdir(parents=True,exist_ok=True); (folder/f"{suffix}.mod").write_bytes(payload)
    compiler=shutil.which("nrnivmodl")
    if not compiler: return {"status":"not_run","reason":"nrnivmodl missing"}
    p=subprocess.run([compiler],cwd=folder,text=True,capture_output=True,timeout=180)
    libs=list(folder.rglob("libnrnmech.so"))+list(folder.rglob("libnrnmech.dylib"))
    return {"status":"compiled" if p.returncode==0 and libs else "failed","return_code":p.returncode,"library_count":len(libs),"stdout_tail":p.stdout[-2500:],"stderr_tail":p.stderr[-2500:]}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=Path("wilbers-k-mod-variant-audit.json")); args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="wilbers-k-mod-audit-") as tmp:
        root=Path(tmp); downloads=root/"downloads"; downloads.mkdir()
        payloads={}; integrity={}
        for name,spec in SOURCES.items(): payloads[name],integrity[name]=fetch_verified(name,spec,downloads)
        parsed={name:parse_mod_parameters(payloads[name].decode("utf-8-sig")) for name,spec in SOURCES.items() if spec["kind"]=="mod"}
        canonical=parsed["k_human"]; variants={}; compiled={}
        for name,spec in SOURCES.items():
            if spec["kind"]!="mod" or name=="k_human": continue
            variants[name]={**parsed[name],"source_role":HYBRID_ROLES.get(name,"named original K variant; role to be inferred from verified parameter differences"),"parameter_diff_vs_k_human":compare_parameters(canonical["parameters"],parsed[name]["parameters"])}
        for name in parsed: compiled[name]=compile_mod(payloads[name],name,root/"compiled")
        context=fit_context(payloads["channel_tools"].decode("utf-8-sig"),payloads["fit_k_human"].decode("utf-8-sig"),payloads["fit_k_mouse"].decode("utf-8-sig"),payloads["channel_kinetics"].decode("utf-8-sig"))
        report={
          "schema_version":1,"status":"official_dataverse_verified_k_mod_variant_diff_and_compile_completed","runtime_eligible":False,
          "dataset":{"doi":"10.34894/L5J0SD","version":3,"license":"CC0-1.0"},
          "runtime":{"python":__import__("platform").python_version(),"neuron":__import__("neuron").__version__},
          "source_integrity":integrity,"canonical_k_human":canonical,"variants":variants,"compile_results":compiled,
          "compile_failures":{k:v for k,v in compiled.items() if v["status"]!="compiled"},
          "original_fitting_context":context,
          "limits":[
            "Every payload matched official Dataverse file ID, SHA-1 and exact byte size.",
            "Parameter diffs identify released-source variants; they do not establish causal AP-clamp improvement.",
            "Hybrid role descriptions are transcribed from original channel_kinetics.py.",
            "No AP-clamp replay or candidate promotion occurs in this provenance gate.",
            "No original MOD bytes, canonical defaults or production runtime are modified."
          ]
        }
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":report["status"],"source_count":len(integrity),"mod_count":len(parsed),"compiled_count":sum(v["status"]=="compiled" for v in compiled.values()),"compile_failures":sorted(report["compile_failures"]),"hybrid_roles":context["hybrid_roles_from_original_channel_kinetics_source"],"human_fit_vectors":context["human_fit_parameter_vectors"],"mouse_fit_vectors":context["mouse_fit_parameter_vectors"],"output":str(args.output)},indent=2))

if __name__=="__main__": main()
