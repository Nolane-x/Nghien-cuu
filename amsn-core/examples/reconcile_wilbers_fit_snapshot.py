#!/usr/bin/env python3
"""Reconcile Wilbers human channel MOD defaults with archived CMA fit snapshots.

All four source files are fetched using immutable Dataverse IDs. Official
Dataverse SHA-1 and byte size plus independently pinned SHA-256 are required.
The script compares the last literal 'final best fit' dictionary against the
PARAMETER block in each compiled MOD source. It does not modify or regenerate
any mechanism and does not promote a fit snapshot into production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://dataverse.nl/api"
FILES = {
    "na_mod": {
        "id": 318629, "path": "Figures5_6/MOD/na_human.mod", "bytes": 3602,
        "sha1": "b199d70c3d0e7a2e991fd8d26c54b1318e3c0970",
        "sha256": "e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd",
        "kind": "mod", "suffix": "_na_human",
    },
    "k_mod": {
        "id": 318647, "path": "Figures5_6/MOD/k_human.mod", "bytes": 4220,
        "sha1": "d299b3430ecda7a94f6d1c37ac76b2878052c7d5",
        "sha256": "899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063",
        "kind": "mod", "suffix": "_k_human",
    },
    "na_fit": {
        "id": 326238, "path": "Figures5_6/Channel_fitting/fit_na_hh_cma_human.py", "bytes": 3663,
        "sha1": "3fac7eb5d25c2e02f6a3530d746de292548ef368",
        "sha256": "ccb66f0d63514ba8eae60b17c61394630df15238cfbf67ddfb62c0d6a80c4f27",
        "kind": "fit", "suffix": "_na_human",
    },
    "k_fit": {
        "id": 326237, "path": "Figures5_6/Channel_fitting/fit_k_hh_cma_human.py", "bytes": 3875,
        "sha1": "c819e59813acd70fae7af7151752bb1d8bbc7357",
        "sha256": "842cbfffc8031b8fa03044cd862494474f55ccc2ac2493a2cf5bc3a1fa99958c",
        "kind": "fit", "suffix": "_k_human",
    },
}
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
PARAM_RE = re.compile(rf"^\s*([A-Za-z_]\w*)\s*=\s*({NUMBER})", re.MULTILINE)


def fetch_verified(name: str, spec: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    metadata = None
    metadata_attempts = []
    for attempt in range(5):
        try:
            req = urllib.request.Request(
                f"{BASE}/files/{spec['id']}",
                headers={"User-Agent": "AMSN-Wilbers-fit-reconciliation/1.0", "Accept": "application/json", "Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read()
                status = getattr(response, "status", None)
                content_type = response.headers.get("Content-Type")
            if not raw:
                raise ValueError("Empty Dataverse file metadata")
            metadata = json.loads(raw)["data"]["dataFile"]
            metadata_attempts.append({"attempt": attempt + 1, "status": status, "content_type": content_type, "bytes": len(raw), "result": "success"})
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
            metadata_attempts.append({"attempt": attempt + 1, "error": repr(exc)})
            if attempt < 4:
                time.sleep((1.5, 3, 6, 10)[attempt])
    if metadata is None:
        raise RuntimeError(f"Could not read Dataverse metadata for {name}: {metadata_attempts}")
    if metadata["checksum"]["value"] != spec["sha1"] or int(metadata["filesize"]) != spec["bytes"]:
        raise RuntimeError(f"Official Dataverse metadata mismatch for {name}")

    attempts = []
    urls = (f"{BASE}/access/datafile/{spec['path']}/{spec['id']}", f"{BASE}/access/datafile/{spec['id']}")
    for url in urls:
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "AMSN-Wilbers-fit-reconciliation/1.0", "Cache-Control": "no-cache", "Accept": "*/*"})
                with urllib.request.urlopen(req, timeout=90) as response:
                    payload = response.read()
                    content_type = response.headers.get("Content-Type")
                    final_url = response.url.split("?", 1)[0]
                if not payload:
                    raise ValueError("Empty Dataverse source payload")
                sha1, sha256 = hashlib.sha1(payload).hexdigest(), hashlib.sha256(payload).hexdigest()
                attempts.append({"url": url, "attempt": attempt + 1, "bytes": len(payload), "content_type": content_type, "final_url": final_url, "sha1": sha1, "sha256": sha256})
                if len(payload) == spec["bytes"] and sha1 == spec["sha1"] and sha256 == spec["sha256"]:
                    return payload, {"metadata_attempts": metadata_attempts, "download_attempts": attempts}
                if attempt < 2:
                    time.sleep((2, 5)[attempt])
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
                attempts.append({"url": url, "attempt": attempt + 1, "error": repr(exc)})
                if attempt < 2:
                    time.sleep((2, 5)[attempt])
    raise RuntimeError(f"Source payload integrity mismatch for {name}: {attempts}")


def parse_mod_parameters(text: str) -> dict[str, float]:
    match = re.search(r"PARAMETER\s*\{(.*?)\n\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Could not find NMODL PARAMETER block")
    block = re.sub(r":.*$", "", match.group(1), flags=re.MULTILINE)
    return {name: float(value) for name, value in PARAM_RE.findall(block)}


def parse_final_fit_snapshot(text: str) -> tuple[dict[str, float], bool]:
    marker = "# final best fit:"
    index = text.rfind(marker)
    if index < 0:
        raise ValueError("No '# final best fit:' marker in original fitting driver")
    block = text[index + len(marker):]
    suffix = re.escape("_na_human") if "fit_na" in text[:2000] else re.escape("_k_human")
    fit_re = re.compile(rf"'([A-Za-z_]\w*{suffix})'\s*:\s*({NUMBER})")
    snapshot = {}
    for name, value in fit_re.findall(block):
        base = name[:-len("_na_human")] if suffix == re.escape("_na_human") else name[:-len("_k_human")]
        snapshot[base] = float(value)
    if not snapshot:
        raise ValueError("Could not parse final fit dictionary after marker")
    applied_after_marker = bool(re.search(r"mod_cell\s*\(\s*cell\s*,", block))
    return snapshot, applied_after_marker


def reconcile(mod_text: str, fit_text: str, suffix: str) -> dict[str, Any]:
    mod = parse_mod_parameters(mod_text)
    fitted, applied = parse_final_fit_snapshot(fit_text)
    rows = []
    for name, fit_value in sorted(fitted.items()):
        if name not in mod:
            raise ValueError(f"Fit parameter {name} is not an NMODL PARAMETER")
        mod_value = mod[name]
        delta = fit_value - mod_value
        rows.append({
            "parameter": name,
            "mod_default": mod_value,
            "fit_snapshot": fit_value,
            "absolute_delta": delta,
            "relative_delta": delta / max(abs(mod_value), 1e-15),
            "matches_within_1e-12": abs(delta) <= 1e-12,
        })
    mismatches = [row for row in rows if not row["matches_within_1e-12"]]
    return {
        "suffix": suffix,
        "parameter_count": len(rows),
        "match_count": len(rows) - len(mismatches),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "all_parameters_match": not mismatches,
        "final_fit_snapshot_applied_by_driver_after_marker": applied,
        "interpretation": (
            "The trailing literal fit snapshot is not passed to mod_cell after the '# final best fit:' marker. "
            "Do not infer a runtime change from its presence; compare it explicitly with the compiled MOD defaults."
        ),
        "parameters": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-fit-snapshot-reconciliation.json"))
    args = parser.parse_args()
    payloads, integrity = {}, {}
    for name, spec in FILES.items():
        payloads[name], integrity[name] = fetch_verified(name, spec)
    na = reconcile(payloads["na_mod"].decode("utf-8-sig"), payloads["na_fit"].decode("utf-8-sig"), "_na_human")
    k = reconcile(payloads["k_mod"].decode("utf-8-sig"), payloads["k_fit"].decode("utf-8-sig"), "_k_human")
    output = {
        "schema_version": 1,
        "status": "dataverse_human_na_k_fit_snapshots_reconciled_against_exact_mod_parameter_defaults",
        "dataset": {"doi": "10.34894/L5J0SD", "version": 3},
        "sources": {
            name: {"id": spec["id"], "path": spec["path"], "bytes": len(payloads[name]), "sha1": hashlib.sha1(payloads[name]).hexdigest(), "sha256": hashlib.sha256(payloads[name]).hexdigest(), "verification": integrity[name]}
            for name, spec in FILES.items()
        },
        "na_human": na,
        "k_human": k,
        "interpretation_limits": [
            "This is a source provenance reconciliation only; it does not apply either snapshot or modify NMODL.",
            "A printed final-best-fit dictionary may represent a candidate/alternate fit and is not automatically the canonical deployed mechanism.",
            "A runtime sensitivity replay is required before attributing AP-clamp mismatch to any parameter difference."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "na_human": {"parameter_count": na["parameter_count"], "match_count": na["match_count"], "mismatch_count": na["mismatch_count"], "mismatches": na["mismatches"]}, "k_human": {"parameter_count": k["parameter_count"], "match_count": k["match_count"], "mismatch_count": k["mismatch_count"], "mismatches": k["mismatches"]}, "output": str(args.output)}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
