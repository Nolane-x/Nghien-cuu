#!/usr/bin/env python3
"""Verify the raw Wilbers AP-clamp trace and replay the original 5-AP protocol.

The published AP-clamp helper code and original human/mouse MOD mechanisms are
downloaded by immutable Dataverse file ID and SHA-1/size checked. The H_wide
trace is SHA-1 checked against Dataverse and independently SHA-256 hashed.
NEURON 9.0.2 then executes the original APclamp_tools helper functions for
human/mouse Na and K mechanisms using the source's exact trace slice and LJP
offset rules. Failures/non-finite outputs are recorded as evidence rather than
silently repaired. No AMSN runtime code is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

BASE = "https://dataverse.nl/api"
FILES = {
    "trace": {
        "id": 318541, "path": "Figures5_6/APclamp/H_wide.csv",
        "bytes": 15095411, "sha1": "e209550ce746483de580459f7d8e40de91ec3667",
    },
    "amps_na": {
        "id": 318540, "path": "Figures5_6/APclamp/amps_na.csv",
        "bytes": 11751, "sha1": "75eb8b1b17becf31cac4d42869e44679bc9aa42a",
    },
    "amps_k": {
        "id": 318543, "path": "Figures5_6/APclamp/amps_k.csv",
        "bytes": 10297, "sha1": "7b7c6906d39fae9382f20deb310621fa48c07cf0",
    },
    "apclamp_tools": {
        "id": 318538, "path": "Figures5_6/APclamp/apclamp_tools.py",
        "bytes": 5082, "sha1": "be15b4567ada212035e33281ed097031c1a3cece",
    },
    "apclamp_na": {
        "id": 318544, "path": "Figures5_6/APclamp/apclamp_na.py",
        "bytes": 5856, "sha1": "912469a0c3a0da144657ce2c055cf326e0d5fd7e",
    },
    "apclamp_k": {
        "id": 318542, "path": "Figures5_6/APclamp/apclamp_k.py",
        "bytes": 1501, "sha1": "629098ed765e1a7b86b36180e7f9a5f9cf4f3ffe",
    },
    "na_human": {
        "id": 318629, "path": "Figures5_6/MOD/na_human.mod",
        "bytes": 3602, "sha1": "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
    },
    "na_mouse": {
        "id": 318631, "path": "Figures5_6/MOD/na_mouse.mod",
        "bytes": 3616, "sha1": "f06a781f23a996fa3ecd6f7c68aacb12646e2f61",
    },
    "k_human": {
        "id": 318647, "path": "Figures5_6/MOD/k_human.mod",
        "bytes": 4220, "sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
    },
    "k_mouse": {
        "id": 318649, "path": "Figures5_6/MOD/k_mouse.mod",
        "bytes": 4189, "sha1": "1d83124eefc45aa7321a5a21337f080c2519ceed",
    },
}

SAMPLE_FREQ_PER_MS = 125
SAMPLE_RATE_HZ = 125000
TIME_START_MS = 199
TIME_END_MS = 307
NA_VOLTAGE_OFFSET_MV = -10.0


def fetch_verified(name: str, spec: dict[str, Any], cache: Path) -> tuple[bytes, dict[str, Any]]:
    metadata_url = f"{BASE}/files/{spec['id']}"
    with urllib.request.urlopen(metadata_url, timeout=60) as response:
        metadata = json.loads(response.read())["data"]["dataFile"]
    official_sha1 = metadata["checksum"]["value"]
    official_bytes = int(metadata["filesize"])
    if official_sha1 != spec["sha1"] or official_bytes != spec["bytes"]:
        raise RuntimeError(
            f"Dataverse metadata mismatch for {name}: "
            f"sha1={official_sha1}, bytes={official_bytes}"
        )

    attempts = []
    for url in (
        f"{BASE}/access/datafile/{spec['path']}/{spec['id']}",
        f"{BASE}/access/datafile/{spec['id']}",
    ):
        request = urllib.request.Request(url, headers={
            "User-Agent": "AMSN-Wilbers-APclamp-reproduction/1.0",
            "Cache-Control": "no-cache", "Pragma": "no-cache", "Accept": "*/*",
        })
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
                final_url = response.url.split("?", 1)[0]
            sha1 = hashlib.sha1(payload).hexdigest()
            sha256 = hashlib.sha256(payload).hexdigest()
            attempts.append({
                "url": url, "final_url": final_url, "bytes": len(payload),
                "content_type": content_type, "sha1": sha1, "sha256": sha256,
            })
            if len(payload) == spec["bytes"] and sha1 == official_sha1:
                (cache / name).write_bytes(payload)
                return payload, {
                    "official_sha1": official_sha1,
                    "official_bytes": official_bytes,
                    "observed_sha1": sha1,
                    "observed_sha256": sha256,
                    "attempts": attempts,
                }
        except Exception as exc:
            attempts.append({"url": url, "error": repr(exc)})
    raise RuntimeError(
        f"Download did not match official Dataverse SHA-1 for {name}: "
        + json.dumps(attempts, sort_keys=True)
    )


def load_original_helper(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("wilbers_apclamp_tools_original", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create Python import spec for original apclamp_tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    required = ("init_na", "Ina_AP1_5", "init_k", "Ik_AP1_5")
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise RuntimeError(f"Original helper module missing functions: {missing}")
    return module


def finite_summary(values: Any) -> dict[str, Any]:
    array = np.asarray(values, dtype=float).reshape(-1)
    finite = array[np.isfinite(array)]
    return {
        "count": int(array.size),
        "finite_count": int(finite.size),
        "nonfinite_count": int(array.size - finite.size),
        "values": [float(x) if np.isfinite(x) else None for x in array],
        "minimum": float(finite.min()) if finite.size else None,
        "maximum": float(finite.max()) if finite.size else None,
    }


def normalized(values: Any, by: str) -> list[float | None]:
    array = np.asarray(values, dtype=float).reshape(-1)
    finite = array[np.isfinite(array)]
    if not finite.size:
        return [None] * int(array.size)
    denominator = float(array[0]) if by == "first" else float(np.nanmax(array))
    if not math.isfinite(denominator) or abs(denominator) < 1e-30:
        return [None] * int(array.size)
    return [float(x / denominator) if np.isfinite(x) else None for x in array]


def execute_model(helper: Any, h: Any, ion: str, species: str, trace: np.ndarray, t: np.ndarray) -> dict[str, Any]:
    cell = None
    try:
        if ion == "na":
            cell = helper.init_na(f"na_{species}")
            amplitudes = helper.Ina_AP1_5(cell, t, trace)
            normalization = "AP1 (same as original Na source plot)"
        else:
            cell = helper.init_k(f"k_{species}")
            amplitudes = helper.Ik_AP1_5(cell, t, trace)
            normalization = "maximum amplitude (same as original K source plot)"
        summary = finite_summary(amplitudes)
        return {
            "status": "completed",
            "mechanism": f"{ion}_{species}",
            "amplitude": summary,
            "normalized": normalized(amplitudes, "first" if ion == "na" else "max"),
            "normalization": normalization,
        }
    except Exception as exc:
        return {
            "status": "error",
            "mechanism": f"{ion}_{species}",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    finally:
        if cell is not None:
            try:
                h.delete_section(sec=cell)
            except Exception:
                pass


def summarize_experimental_csv(payload: bytes, ion: str) -> dict[str, Any]:
    from io import BytesIO
    frame = pd.read_csv(BytesIO(payload))
    output: dict[str, Any] = {
        "columns": list(frame.columns),
        "rows": int(len(frame)),
    }
    if ion == "na":
        required = {"Species", "APnr", "relative_amp"}
        if required.issubset(frame.columns):
            selected = frame.loc[frame["APnr"] <= 5]
            output["first_five_by_species"] = {
                str(species): {
                    "n": int(len(group)),
                    "mean_by_ap": {
                        str(int(ap)): float(value)
                        for ap, value in group.groupby("APnr")["relative_amp"].mean().items()
                    },
                }
                for species, group in selected.groupby("Species")
            }
    else:
        required = {"species", "APnr", "amp"}
        if required.issubset(frame.columns):
            selected = frame.loc[frame["APnr"] <= 5]
            output["first_five_by_species"] = {
                str(species): {
                    "n": int(len(group)),
                    "mean_by_ap": {
                        str(int(ap)): float(value)
                        for ap, value in group.groupby("APnr")["amp"].mean().items()
                    },
                }
                for species, group in selected.groupby("species")
            }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-apclamp-replay.json"))
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-apclamp-") as tmp:
        root = Path(tmp)
        cache = root / "downloaded"
        cache.mkdir()
        payloads, integrity = {}, {}
        for name, spec in FILES.items():
            payloads[name], integrity[name] = fetch_verified(name, spec, cache)

        trace = np.loadtxt(BytesIO(payloads["trace"]), delimiter=",", skiprows=1)
        trace = np.asarray(trace)
        if trace.ndim == 2 and trace.shape[1] == 1:
            trace = trace[:, 0]
        if trace.ndim != 1:
            raise RuntimeError(f"Original trace loader expects a 1-D csv; observed shape {trace.shape}")
        peak_indices, peak_props = find_peaks(trace, prominence=50)
        start_index = round(TIME_START_MS * SAMPLE_FREQ_PER_MS)
        end_index = round(TIME_END_MS * SAMPLE_FREQ_PER_MS) + 1
        source_slice = trace[start_index:end_index]
        if len(source_slice) != 13501:
            raise RuntimeError(f"Expected the source's 13,501-sample slice, got {len(source_slice)}")
        t = np.linspace(TIME_START_MS, TIME_END_MS, len(source_slice))
        na_trace = source_slice + NA_VOLTAGE_OFFSET_MV
        k_trace = source_slice.copy()

        # Compile the four untouched source mechanisms exactly as the source
        # script compiles the shared MOD directory.
        mod_dir = root / "Mod"
        mod_dir.mkdir()
        for name in ("na_human", "na_mouse", "k_human", "k_mouse"):
            (mod_dir / f"{name}.mod").write_bytes(payloads[name])
        compiler = shutil.which("nrnivmodl")
        if compiler is None:
            raise RuntimeError("nrnivmodl missing; NEURON is not installed")
        build = subprocess.run([compiler], cwd=mod_dir, text=True, capture_output=True, timeout=240)
        if build.returncode:
            raise RuntimeError(
                f"Original human/mouse mechanisms failed to compile.\n"
                f"STDOUT:\n{build.stdout[-10000:]}\nSTDERR:\n{build.stderr[-10000:]}"
            )
        libs = list(mod_dir.rglob("libnrnmech.so")) or list(mod_dir.rglob("libnrnmech.dylib"))
        if len(libs) != 1:
            raise RuntimeError(f"Expected one compiled NEURON library, found {libs}")

        from neuron import h
        if h.nrn_load_dll(str(libs[0])) == 0:
            raise RuntimeError("NEURON failed to load the compiled source mechanisms")
        helper_path = cache / "apclamp_tools.py"
        helper = load_original_helper(helper_path)
        h.celsius = 34.0
        h.dt = 1000.0 / SAMPLE_RATE_HZ

        models = {}
        for ion, command in (("na", na_trace), ("k", k_trace)):
            for species in ("human", "mouse"):
                models[f"{ion}_{species}"] = execute_model(helper, h, ion, species, command, t)
                try:
                    import matplotlib.pyplot as plt
                    plt.close("all")
                except Exception:
                    pass

        trace_info = {
            "file_id": FILES["trace"]["id"],
            "bytes": len(payloads["trace"]),
            "sha1": hashlib.sha1(payloads["trace"]).hexdigest(),
            "sha256": hashlib.sha256(payloads["trace"]).hexdigest(),
            "shape": [int(x) for x in np.asarray(np.loadtxt(BytesIO(payloads["trace"]), delimiter=",", skiprows=1)).shape],
            "sample_count": int(trace.size),
            "min_mV": float(np.min(trace)),
            "max_mV": float(np.max(trace)),
            "mean_mV": float(np.mean(trace)),
            "sd_mV": float(np.std(trace)),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "dt_ms": 1000.0 / SAMPLE_RATE_HZ,
            "whole_trace_prominence_50_peak_count": int(len(peak_indices)),
            "first_peaks_time_ms": [float(x / SAMPLE_FREQ_PER_MS) for x in peak_indices[:20]],
        }
        protocol = {
            "source_scripts": {
                "na": "apclamp_na.py",
                "k": "apclamp_k.py",
                "shared_helper": "apclamp_tools.py",
            },
            "source_time_start_ms": TIME_START_MS,
            "source_time_end_ms": TIME_END_MS,
            "slice_start_index": start_index,
            "slice_end_index_exclusive": end_index,
            "slice_samples": int(len(source_slice)),
            "ap_train_voltage_peaks_in_slice": [float(x) for x in (find_peaks(source_slice, prominence=50)[0] / SAMPLE_FREQ_PER_MS + TIME_START_MS)],
            "na_voltage_offset_mV": NA_VOLTAGE_OFFSET_MV,
            "k_voltage_offset_mV": 0.0,
            "command_sample_rate_hz": SAMPLE_RATE_HZ,
            "temperature_c": 34.0,
            "model_section": "single 10 um diameter section, Ra=200 ohm cm, Cm=1 uF/cm2",
        }
        report = {
            "schema_version": 1,
            "status": "raw_human_apclamp_trace_verified_and_original_neuron_helpers_replayed",
            "runtime_eligible": False,
            "runtime_versions": {
                "python": __import__("platform").python_version(),
                "neuron": __import__("neuron").__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
            },
            "source_integrity": {
                name: {
                    "id": FILES[name]["id"],
                    "path": FILES[name]["path"],
                    "bytes": len(payloads[name]),
                    "sha1": hashlib.sha1(payloads[name]).hexdigest(),
                    "sha256": hashlib.sha256(payloads[name]).hexdigest(),
                    "verification": integrity[name],
                }
                for name in FILES
            },
            "raw_trace": trace_info,
            "protocol": protocol,
            "experimental_first_five_ap_amplitudes": {
                "na": summarize_experimental_csv(payloads["amps_na"], "na"),
                "k": summarize_experimental_csv(payloads["amps_k"], "k"),
            },
            "original_model_replay": models,
            "interpretation_limits": [
                "The original source helper code and unmodified human/mouse MOD files were executed; no mechanism correction was applied.",
                "Na waveform offset is -10 mV per the original apclamp_na.py; K receives no offset per apclamp_k.py.",
                "This command replay is only the first five APs from the H_wide waveform; it is not a 200-AP trace reproduction.",
                "The K source trap0 anomalies may produce unstable or non-finite simulation output; do not conceal failed or non-finite results.",
                "No AMSN runtime active-channel mechanism or production defaults are changed.",
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "trace": trace_info,
            "protocol": protocol,
            "models": models,
            "output": str(args.output),
        }, indent=2, allow_nan=False))


if __name__ == "__main__":
    from io import BytesIO
    main()
