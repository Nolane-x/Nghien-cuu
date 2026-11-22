#!/usr/bin/env python3
"""Download, hash, compile and diagnostically probe the original Wilbers Na/K MOD files."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

SOURCES = {
    "na_human": {
        "path": "Figures5_6/MOD/na_human.mod", "file_id": 318629,
        "sha256": "e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd",
        "reference_temperature_c": 25.0, "voltage_symbols": ("tha", "thi1", "thi2"),
        "observables": ("minf", "hinf", "mtau", "htau"),
    },
    "k_human": {
        "path": "Figures5_6/MOD/k_human.mod", "file_id": 318647,
        "sha256": "899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063",
        "reference_temperature_c": 34.0, "voltage_symbols": ("tha", "thi1", "thi2"),
        "observables": ("minf", "hinf", "mtau", "h1tau", "h2tau"),
    },
}
DATAFILE_BASE = "https://dataverse.nl/api/access/datafile"


def download_verified(source: dict[str, Any]) -> bytes:
    url = f"{DATAFILE_BASE}/{source['path']}/{source['file_id']}"
    request = urllib.request.Request(url, headers={"User-Agent": "AMSN-Wilbers-source-reproduction/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    observed = hashlib.sha256(payload).hexdigest()
    if observed != source["sha256"]:
        raise RuntimeError(f"SHA-256 mismatch for {source['path']}: expected {source['sha256']}, observed {observed}")
    return payload


def finite_value(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def compile_and_probe(name: str, source: dict[str, Any], work: Path) -> dict[str, Any]:
    payload = download_verified(source)
    build_dir = work / name
    build_dir.mkdir(parents=True)
    (build_dir / f"{name}.mod").write_bytes(payload)
    compiler = shutil.which("nrnivmodl")
    if compiler is None:
        raise RuntimeError("nrnivmodl was not found; install the pinned NEURON build")
    compiled = subprocess.run([compiler], cwd=build_dir, text=True, capture_output=True, timeout=180)
    if compiled.returncode:
        raise RuntimeError(f"nrnivmodl failed for {name} (exit {compiled.returncode})\nSTDOUT:\n{compiled.stdout[-12000:]}\nSTDERR:\n{compiled.stderr[-12000:]}")
    libraries = list(build_dir.rglob("libnrnmech.so"))
    if not libraries:
        libraries = list(build_dir.rglob("libnrnmech.dylib"))
    if not libraries:
        libraries = list(build_dir.rglob("nrnmech.dll"))
    if len(libraries) != 1:
        raise RuntimeError(f"Expected one compiled mechanism library for {name}, found {libraries}")

    from neuron import h
    loaded = h.nrn_load_dll(str(libraries[0]))
    if loaded == 0:
        raise RuntimeError(f"NEURON failed to load compiled library for {name}")
    section = h.Section(name=f"wilbers_{name}_probe")
    section.L = 10.0
    section.diam = 10.0
    section.Ra = 200.0
    section.cm = 1.0
    section.insert(name)
    h.celsius = source["reference_temperature_c"]
    h.dt = 0.001
    segment = section(0.5)
    if name == "na_human":
        segment.ena = 53.0
    else:
        segment.ek = -101.0
    mechanism = getattr(segment, name)
    singularities = {symbol: float(getattr(mechanism, symbol)) for symbol in source["voltage_symbols"]}
    observations = []
    for symbol, value in singularities.items():
        for label, voltage in ((f"{symbol}-epsilon", value-1e-5), (symbol, value), (f"{symbol}+epsilon", value+1e-5)):
            h.finitialize(voltage)
            h.fcurrent()
            values = {field: finite_value(getattr(mechanism, field)) for field in source["observables"]}
            observations.append({"point": label, "command_voltage_mV": voltage, "values": values, "all_finite": all(v is not None for v in values.values())})
    nonfinite = [row["point"] for row in observations if not row["all_finite"]]
    h.delete_section(sec=section)
    return {
        "source_path": source["path"], "file_id": source["file_id"], "download_bytes": len(payload),
        "sha256_verified": True, "compiled": True, "loaded_into_neuron": True,
        "neuron_version": __import__("neuron").__version__,
        "reference_temperature_c": source["reference_temperature_c"],
        "singular_voltage_parameters_mV": singularities, "observations": observations,
        "nonfinite_probe_points": nonfinite,
        "trap0_diagnostic": ("non-finite rates observed at one or more probe points" if nonfinite else "all probed observables were finite; this does not prove the source formula is correct"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-nmodl-probe.json"))
    args = parser.parse_args()
    results = {}
    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-") as tmp:
        work = Path(tmp)
        for name, source in SOURCES.items():
            results[name] = compile_and_probe(name, source, work)
    report = {
        "schema_version": 1, "status": "original_sources_downloaded_hash_verified_compiled_and_probed",
        "runtime_eligible": False,
        "source_urls": {name: f"{DATAFILE_BASE}/{source['path']}/{source['file_id']}" for name, source in SOURCES.items()},
        "results": results,
        "interpretation": "Compilation and point probes are not a reproduction of published voltage-clamp/AP-clamp experiments. Investigate non-finite observations against unchanged source and a stable analytic reference. No AMSN runtime mechanism or defaults are changed.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
