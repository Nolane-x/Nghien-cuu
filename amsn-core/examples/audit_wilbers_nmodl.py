#!/usr/bin/env python3
"""Reproduce and diagnose the original Wilbers human Na/K NMODL mechanisms.

The released MOD sources are downloaded byte-for-byte, SHA-256 checked and
compiled unchanged. A second, diagnostic-only copy changes only the removable
trap0 limit handling so the source implementation can be compared against a
stable analytic reference. The corrected copy is NEVER treated as the author's
mechanism or as an AMSN runtime model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

SOURCES: dict[str, dict[str, Any]] = {
    "na_human": {
        "path": "Figures5_6/MOD/na_human.mod",
        "file_id": 318629,
        "sha1": "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
        "sha256": "e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd",
        "reference_temperature_c": 25.0,
        "voltage_symbols": ("tha", "thi1", "thi2"),
        "observables": ("minf", "hinf", "mtau", "htau"),
        "time_constants": ("mtau", "htau"),
        "protocol_voltages_mV": [float(v) for v in range(-80, 11, 5)],
        "protocol_name": "Na voltage-clamp test-step grid; hold -120 mV for 2 ms, then test for 10 ms",
        "expected_source_nonfinite": [],
    },
    "k_human": {
        "path": "Figures5_6/MOD/k_human.mod",
        "file_id": 318647,
        "sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
        "sha256": "899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063",
        "reference_temperature_c": 34.0,
        "voltage_symbols": ("tha", "thi1", "thi2"),
        "observables": ("minf", "hinf", "mtau", "h1tau", "h2tau"),
        "time_constants": ("mtau", "h1tau", "h2tau"),
        "protocol_voltages_mV": [float(v) for v in range(-110, 51, 10)],
        "protocol_name": "K voltage-clamp test-step grid; hold -140 mV for 20 ms, test 500 ms, +60 mV for 50 ms, tail -140 mV",
        "expected_source_nonfinite": ["tha", "thi1", "thi2"],
        "expected_source_negative_time_constants": [
            "thi1:negative-epsilon", "thi1:negative", "thi1:negative+epsilon", "thi2:negative"
        ],
    },
}
DATAFILE_BASE = "https://dataverse.nl/api/access/datafile"
EPSILON_MV = 1e-5
RELATIVE_EPSILON = 1e-6


def download_verified(source: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Fetch the immutable Dataverse file ID and verify both official SHA-1 and pinned SHA-256."""
    metadata_url = f"https://dataverse.nl/api/files/{source['file_id']}"
    with urllib.request.urlopen(metadata_url, timeout=60) as response:
        metadata_payload = response.read()
    metadata = json.loads(metadata_payload)["data"]["dataFile"]
    official_sha1 = metadata["checksum"]["value"]
    official_size = int(metadata["filesize"])
    if official_sha1 != source["sha1"]:
        raise RuntimeError(
            f"Dataverse metadata SHA-1 changed for file {source['file_id']}: "
            f"expected {source['sha1']}, observed {official_sha1}"
        )

    urls = [
        f"{DATAFILE_BASE}/{source['path']}/{source['file_id']}",
        f"{DATAFILE_BASE}/{source['file_id']}",
    ]
    attempts = []
    for url in urls:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AMSN-Wilbers-source-reproduction/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept": "*/*",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
                content_encoding = response.headers.get("Content-Encoding")
                final_url = response.url.split("?", 1)[0]
            observed_sha1 = hashlib.sha1(payload).hexdigest()
            observed_sha256 = hashlib.sha256(payload).hexdigest()
            attempt = {
                "url": url,
                "final_url": final_url,
                "bytes": len(payload),
                "content_type": content_type,
                "content_encoding": content_encoding,
                "sha1": observed_sha1,
                "sha256": observed_sha256,
                "sha1_matches_dataverse": observed_sha1 == official_sha1,
                "sha256_matches_pinned_source": observed_sha256 == source["sha256"],
            }
            attempts.append(attempt)
            if (
                len(payload) == official_size
                and observed_sha1 == official_sha1
                and observed_sha256 == source["sha256"]
            ):
                return payload, {
                    "dataverse_metadata_sha1": official_sha1,
                    "dataverse_metadata_bytes": official_size,
                    "download_attempts": attempts,
                    "accepted_endpoint": url,
                }
        except Exception as exc:
            attempts.append({"url": url, "error": repr(exc)})

    raise RuntimeError(
        "Dataverse source download did not match both official SHA-1 and pinned SHA-256. "
        f"file_id={source['file_id']}; official_sha1={official_sha1}; "
        f"official_bytes={official_size}; attempts={json.dumps(attempts, sort_keys=True)}"
    )


def finite_value(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def stable_trap0_reference(v: float, th: float, a: float, q: float) -> float:
    """Stable reference for a*(v-th)/(1-exp(-(v-th)/q))."""
    if q == 0:
        raise ValueError("q must be non-zero")
    x = (v - th) / q
    if abs(x) < RELATIVE_EPSILON:
        # First-order Taylor expansion of x/(1-exp(-x)).
        return a * q * (1.0 + x / 2.0)
    return a * (v - th) / (-math.expm1(-x))


def make_diagnostic_clone(payload: bytes, name: str) -> bytes:
    """Create a separate suffix with the corrected trap0 branch and limit."""
    source = payload.decode("utf-8")
    if "\r\n" in source:
        source = source.replace("\r\n", "\n")
    suffix = f"{name}_stableprobe"
    suffix_count = source.count(f"SUFFIX {name}")
    if suffix_count != 1:
        raise RuntimeError(f"Expected one SUFFIX {name} declaration, found {suffix_count}")
    source = source.replace(f"SUFFIX {name}", f"SUFFIX {suffix}", 1)

    branch_old = "if (fabs((v+th)/q) > 1e-6) {"
    branch_new = "if (fabs((v-th)/q) > 1e-6) {"
    fallback_old = "trap0 = q*(1--(v-th)/q/2)"
    fallback_new = "trap0 = a*q*(1+(v-th)/q/2)"
    if source.count(branch_old) != 1 or source.count(fallback_old) != 1:
        raise RuntimeError(f"Unexpected trap0 source layout for {name}; refusing fuzzy patch")
    source = source.replace(branch_old, branch_new, 1)
    source = source.replace(fallback_old, fallback_new, 1)
    return source.encode("utf-8")


def voltage_probe_points(source: dict[str, Any], mechanism: Any) -> list[dict[str, Any]]:
    points: dict[float, set[str]] = {}
    def add(voltage: float, label: str) -> None:
        key = round(float(voltage), 8)
        points.setdefault(key, set()).add(label)

    for symbol in source["voltage_symbols"]:
        value = float(getattr(mechanism, symbol))
        for sign, signed in (("positive", value), ("negative", -value)):
            add(signed - EPSILON_MV, f"{symbol}:{sign}-epsilon")
            add(signed, f"{symbol}:{sign}")
            add(signed + EPSILON_MV, f"{symbol}:{sign}+epsilon")
    for voltage in source["protocol_voltages_mV"]:
        add(voltage, "published-protocol-test-step")
    # Include the stated holding/tail levels so the rate model is audited
    # over the voltage levels used in the source protocol.
    for voltage in (-120.0, -140.0, 40.0, 60.0):
        add(voltage, "published-protocol-hold-or-conditioning")
    return [
        {"voltage_mV": voltage, "labels": sorted(labels)}
        for voltage, labels in sorted(points.items())
    ]


def load_mechanism_fields(segment: Any, suffix: str, fields: tuple[str, ...]) -> dict[str, float | None]:
    mechanism = getattr(segment, suffix)
    return {field: finite_value(getattr(mechanism, field)) for field in fields}


def relative_difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return abs(left - right) / max(abs(right), 1e-12)


def compile_compare_and_probe(
    name: str, source: dict[str, Any], work: Path
) -> dict[str, Any]:
    payload, download_metadata = download_verified(source)
    clone_payload = make_diagnostic_clone(payload, name)
    build_dir = work / name
    build_dir.mkdir(parents=True)
    (build_dir / f"{name}.mod").write_bytes(payload)
    stable_suffix = f"{name}_stableprobe"
    (build_dir / f"{stable_suffix}.mod").write_bytes(clone_payload)

    compiler = shutil.which("nrnivmodl")
    if compiler is None:
        raise RuntimeError("nrnivmodl was not found; install the pinned NEURON build")
    compiled = subprocess.run(
        [compiler], cwd=build_dir, text=True, capture_output=True, timeout=180
    )
    if compiled.returncode:
        raise RuntimeError(
            f"nrnivmodl failed for {name} (exit {compiled.returncode})\n"
            f"STDOUT:\n{compiled.stdout[-12000:]}\n"
            f"STDERR:\n{compiled.stderr[-12000:]}"
        )
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

    sections = {}
    segments = {}
    mechanisms = {}
    for suffix in (name, stable_suffix):
        sec = h.Section(name=f"wilbers_{suffix}")
        sec.L = 10.0
        sec.diam = 10.0
        sec.Ra = 200.0
        sec.cm = 1.0
        sec.insert(suffix)
        sections[suffix] = sec
        segments[suffix] = sec(0.5)
        mechanisms[suffix] = getattr(segments[suffix], suffix)
        if name == "na_human":
            segments[suffix].ena = 53.0
        else:
            segments[suffix].ek = -101.0

    h.celsius = source["reference_temperature_c"]
    h.dt = 0.001
    singularities = {
        symbol: float(getattr(mechanisms[name], symbol))
        for symbol in source["voltage_symbols"]
    }
    points = voltage_probe_points(source, mechanisms[name])

    observations = []
    for point in points:
        voltage = point["voltage_mV"]
        h.finitialize(voltage)
        h.fcurrent()
        original = load_mechanism_fields(segments[name], name, source["observables"])
        stable = load_mechanism_fields(segments[stable_suffix], stable_suffix, source["observables"])
        differences = {
            field: relative_difference(original[field], stable[field])
            for field in source["observables"]
        }
        original_taus = [original[field] for field in source["time_constants"]]
        stable_taus = [stable[field] for field in source["time_constants"]]
        observations.append({
            "voltage_mV": voltage,
            "labels": point["labels"],
            "source": original,
            "stable_diagnostic_clone": stable,
            "relative_difference_source_vs_stable": differences,
            "source_all_finite": all(v is not None for v in original.values()),
            "stable_all_finite": all(v is not None for v in stable.values()),
            "source_all_time_constants_positive": all(v is not None and v > 0 for v in original_taus),
            "stable_all_time_constants_positive": all(v is not None and v > 0 for v in stable_taus),
        })

    protocol_rows = [
        row for row in observations
        if "published-protocol-test-step" in row["labels"]
    ]
    source_nonfinite = [
        row for row in observations
        if not row["source_all_finite"]
    ]
    source_invalid_time_constants = [
        row for row in observations
        if not row["source_all_time_constants_positive"]
    ]
    source_negative_time_constants = [
        row for row in observations
        if any(
            original[field] is not None and original[field] <= 0
            for field in source["time_constants"]
            for original in [row["source"]]
        )
    ]
    stable_failures = [
        row for row in observations
        if not row["stable_all_finite"] or not row["stable_all_time_constants_positive"]
    ]
    source_protocol_failures = [
        row for row in protocol_rows
        if not row["source_all_finite"] or not row["source_all_time_constants_positive"]
    ]
    expected = set(source["expected_source_nonfinite"])
    observed_exact_nonfinite = {
        label.split(":")[0]
        for row in source_nonfinite
        for label in row["labels"]
        if label.endswith(":positive") or label.endswith(":negative")
    }
    # The exact positive singulars are the previously reproduced K failure
    # points. Na remains tabulated and is expected to stay finite here.
    observed_positive_nonfinite = {
        label.split(":")[0]
        for row in source_nonfinite
        for label in row["labels"]
        if label.endswith(":positive")
    }

    if stable_failures:
        raise RuntimeError(
            f"Stable analytic diagnostic clone failed positive/finite rate checks for {name}: "
            f"{[row['labels'] for row in stable_failures]}"
        )
    if source_protocol_failures:
        raise RuntimeError(
            f"Original mechanism has a non-finite or non-positive time constant on "
            f"published protocol grid for {name}: {[row['labels'] for row in source_protocol_failures]}"
        )
    if observed_positive_nonfinite != expected:
        raise RuntimeError(
            f"Original source exact-positive singular probes differ from expected for {name}: "
            f"expected={sorted(expected)}, observed={sorted(observed_positive_nonfinite)}"
        )
    observed_negative_tau_labels = sorted({
        label
        for row in source_negative_time_constants
        for label in row["labels"]
    })
    expected_negative_tau_labels = sorted(source.get("expected_source_negative_time_constants", []))
    if observed_negative_tau_labels != expected_negative_tau_labels:
        raise RuntimeError(
            f"Original source negative time-constant probes differ from expected for {name}: "
            f"expected={expected_negative_tau_labels}, observed={observed_negative_tau_labels}"
        )

    protocol_max_relative: dict[str, float | None] = {}
    for field in source["observables"]:
        values = [
            row["relative_difference_source_vs_stable"][field]
            for row in protocol_rows
            if row["relative_difference_source_vs_stable"][field] is not None
        ]
        protocol_max_relative[field] = max(values) if values else None
    finite_protocol_differences = [v for v in protocol_max_relative.values() if v is not None]
    if any(v > 1e-10 for v in finite_protocol_differences):
        raise RuntimeError(
            f"Original vs stable diagnostic rates differ on the published static command grid for {name}: "
            f"{protocol_max_relative}"
        )

    max_relative: dict[str, float | None] = {}
    for field in source["observables"]:
        values = [
            row["relative_difference_source_vs_stable"][field]
            for row in observations
            if row["relative_difference_source_vs_stable"][field] is not None
        ]
        max_relative[field] = max(values) if values else None

    for suffix in sections:
        h.delete_section(sec=sections[suffix])

    return {
        "source_path": source["path"],
        "file_id": source["file_id"],
        "download_bytes": len(payload),
        "sha256_verified": hashlib.sha256(payload).hexdigest() == source["sha256"],
        "download_metadata": download_metadata,
        "compiled_original_and_stable_diagnostic_clone": True,
        "loaded_into_neuron": True,
        "neuron_version": __import__("neuron").__version__,
        "reference_temperature_c": source["reference_temperature_c"],
        "singular_voltage_parameters_mV": singularities,
        "protocol_name": source["protocol_name"],
        "protocol_voltage_count": len(source["protocol_voltages_mV"]),
        "probe_count": len(observations),
        "source_nonfinite_probe_count": len(source_nonfinite),
        "source_nonfinite_probe_labels": [row["labels"] for row in source_nonfinite],
        "source_invalid_time_constant_probe_count": len(source_invalid_time_constants),
        "source_invalid_time_constant_probe_labels": [row["labels"] for row in source_invalid_time_constants],
        "source_negative_time_constant_probe_count": len(source_negative_time_constants),
        "source_negative_time_constant_probe_labels": [row["labels"] for row in source_negative_time_constants],
        "source_protocol_step_failures": [],
        "protocol_grid_max_relative_difference": protocol_max_relative,
        "protocol_grid_max_relative_difference_tolerance": 1e-10,
        "stable_clone_all_probe_rates_finite_and_time_constants_positive": True,
        "max_relative_difference_source_vs_stable_clone": max_relative,
        "observations": observations,
        "interpretation": (
            "The stable clone is a diagnostic reference only. It is not the published "
            "mechanism, is not a biological validation, and is not eligible for AMSN runtime."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-nmodl-probe.json"))
    args = parser.parse_args()
    results = {}
    with tempfile.TemporaryDirectory(prefix="amsn-wilbers-") as tmp:
        work = Path(tmp)
        for name, source in SOURCES.items():
            results[name] = compile_compare_and_probe(name, source, work)

    report = {
        "schema_version": 2,
        "status": "original_sources_hash_verified_compiled_and_compared_with_stable_diagnostic_clone",
        "runtime_eligible": False,
        "stable_clone_is_not_author_source": True,
        "stable_clone_changes": {
            "branch_condition": "fabs((v-th)/q)",
            "limit_expansion": "a*q*(1+(v-th)/(2*q))",
            "scope": "temporary diagnostic-only clone; original Dataverse bytes remain unchanged",
        },
        "source_urls": {
            name: f"{DATAFILE_BASE}/{source['path']}/{source['file_id']}"
            for name, source in SOURCES.items()
        },
        "results": results,
        "interpretation": (
            "Original mechanism rates are compared against a diagnostic-only clone using "
            "the mathematically stable trap0 limit. Published command-grid time constants "
            "must remain finite and positive. These pointwise checks are not a complete "
            "reproduction of the voltage-clamp/AP-clamp recordings. No AMSN runtime "
            "mechanism or production defaults are changed."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
