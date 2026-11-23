#!/usr/bin/env python3
"""Integrity-check and describe the original Wilbers 2023 Figure 2 Na/K workbooks.

This script downloads the released Dataverse workbooks by immutable file ID,
verifies both Dataverse SHA-1 metadata and pinned SHA-256 bytes, inspects the
published plotting script for data-label rules, and computes descriptive
per-recording normalized-current summaries. It does not claim new inferential
statistics or reproduce the paper's original regression models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import urllib.request
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

BASE = "https://dataverse.nl/api"
FILES = {
    "na": {
        "id": 318668,
        "path": "Figure2/Na_data_fig2.xlsx",
        "bytes": 548562,
        "sha1": "cd702d7f1ca65b0b88a2565f289740546902e36b",
        "sha256": "2fac600523d596a4dccbe167d3283b2e506dfdb9c7b1caef2a490c2c5dff184a",
    },
    "k": {
        "id": 318669,
        "path": "Figure2/K_data_fig2.xlsx",
        "bytes": 302011,
        "sha1": "287720f8db3b20b167edd9e639dd67b0a1194def",
        "sha256": "f00714c534c9658b8c07d2a473d39b2fd5a99c392e6e2ab50fb52fbb3b6ca74d",
    },
    "plot_script": {
        "id": 318530,
        "path": "Figure2/plots_fig2.py",
        "bytes": 2795,
        "sha1": "5a0aeeb41269e9a0630851b0ce7ad70d188b82fa",
        "sha256": None,
    },
    "stats_script": {
        "id": 318531,
        "path": "Figure2/stats_fig2.py",
        "bytes": 2282,
        "sha1": "45ffcd0be45743c7937d3e0a323ac52832aa845e",
        "sha256": None,
    },
}

NA_GROUPS = ("Hnarrow", "Mnarrow", "Mwide", "Hwide")
AP_CHECKPOINTS = (1, 5, 200)


def fetch_verified(spec: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Verify API metadata and then both the official SHA-1 and pinned byte SHA-256."""
    meta_url = f"{BASE}/files/{spec['id']}"
    with urllib.request.urlopen(meta_url, timeout=60) as response:
        meta = json.loads(response.read())["data"]["dataFile"]
    actual_sha1 = meta["checksum"]["value"]
    actual_bytes = int(meta["filesize"])
    if actual_sha1 != spec["sha1"] or actual_bytes != spec["bytes"]:
        raise RuntimeError(
            f"Dataverse metadata mismatch for {spec['path']}: "
            f"sha1={actual_sha1}, bytes={actual_bytes}"
        )

    urls = [
        f"{BASE}/access/datafile/{spec['path']}/{spec['id']}",
        f"{BASE}/access/datafile/{spec['id']}",
    ]
    attempts = []
    for url in urls:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AMSN-Wilbers-Figure2-data-audit/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept": "*/*",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type")
                final_url = response.url.split("?", 1)[0]
            sha1 = hashlib.sha1(payload).hexdigest()
            sha256 = hashlib.sha256(payload).hexdigest()
            attempt = {
                "url": url,
                "final_url": final_url,
                "bytes": len(payload),
                "content_type": content_type,
                "sha1": sha1,
                "sha256": sha256,
                "sha1_matches": sha1 == spec["sha1"],
                "sha256_matches": spec["sha256"] is None or sha256 == spec["sha256"],
            }
            attempts.append(attempt)
            if (
                len(payload) == spec["bytes"]
                and sha1 == spec["sha1"]
                and (spec["sha256"] is None or sha256 == spec["sha256"])
            ):
                return payload, {
                    "metadata_sha1": actual_sha1,
                    "metadata_bytes": actual_bytes,
                    "attempts": attempts,
                    "accepted_endpoint": url,
                }
        except Exception as exc:
            attempts.append({"url": url, "error": repr(exc)})
    raise RuntimeError(
        f"Dataverse payload failed integrity checks for {spec['path']}: "
        + json.dumps(attempts, sort_keys=True)
    )


def numeric(value: Any) -> float | None:
    if value is None or isinstance(value, str) and not value.strip():
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def summarize(values: list[float | None]) -> dict[str, Any]:
    data = [v for v in values if v is not None and math.isfinite(v)]
    if not data:
        return {"n": 0, "missing": len(values), "mean": None, "median": None, "sd": None, "sem": None}
    sd = statistics.stdev(data) if len(data) > 1 else 0.0
    return {
        "n": len(data),
        "missing": len(values) - len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "sd": sd,
        "sem": sd / math.sqrt(len(data)) if data else None,
        "min": min(data),
        "max": max(data),
    }


def parse_na_header(header: Any) -> tuple[str, int] | None:
    match = re.fullmatch(r"relative_amp_(Hnarrow|Mnarrow|Mwide|Hwide)_\s*(\d+)", str(header).strip())
    return (match.group(1), int(match.group(2))) if match else None


def parse_k_header(header: Any) -> tuple[str, int] | None:
    match = re.fullmatch(r"amp_(h|m)_n_\s*(\d+)", str(header).strip())
    return (match.group(1), int(match.group(2))) if match else None


def na_recording_species(filename: str) -> str:
    """Exact rule from Dataverse Figure2/plots_fig2.py."""
    return "Mouse" if filename.startswith("M") else "Human"


def load_sheet_rows(payload: bytes, sheet_name: str) -> tuple[list[str], list[dict[str, Any]], str]:
    workbook = load_workbook(BytesIO(payload), read_only=True, data_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            raise RuntimeError(f"Missing workbook sheet {sheet_name!r}; found {workbook.sheetnames}")
        sheet = workbook[sheet_name]
        dimension = sheet.calculate_dimension()
        iterator = sheet.iter_rows(values_only=True)
        header_row = next(iterator)
        headers = [str(value).strip() if value is not None else "" for value in header_row]
        if len(headers) != len(set(headers)):
            duplicates = [key for key, count in Counter(headers).items() if count > 1]
            raise RuntimeError(f"Duplicate workbook header names: {duplicates}")
        rows = []
        for values in iterator:
            if all(value is None for value in values):
                continue
            rows.append(dict(zip(headers, values)))
        return headers, rows, dimension
    finally:
        workbook.close()


def summarize_na(payload: bytes, plot_script: str) -> dict[str, Any]:
    headers, rows, dimension = load_sheet_rows(payload, "data")
    _, variable_rows, variable_dimension = load_sheet_rows(payload, "variables")
    columns: dict[str, dict[int, str]] = {group: {} for group in NA_GROUPS}
    for header in headers:
        parsed = parse_na_header(header)
        if parsed:
            group, ap_number = parsed
            if ap_number in columns[group]:
                raise RuntimeError(f"Duplicate Na column {group} AP{ap_number}")
            columns[group][ap_number] = header
    for group, mapping in columns.items():
        if sorted(mapping) != list(range(1, 201)):
            raise RuntimeError(f"Na group {group} must have exactly AP1..AP200; found {len(mapping)}")

    species_counts = Counter(na_recording_species(str(row["Filename"])) for row in rows)
    expected_species_counts = {"Human": 16, "Mouse": 33}
    if dict(species_counts) != expected_species_counts:
        raise RuntimeError(
            f"Na filename-prefix species map differs from published sample counts: {dict(species_counts)}"
        )
    filenames = [str(row["Filename"]) for row in rows]
    if len(filenames) != len(set(filenames)):
        raise RuntimeError("Duplicate Na recording filenames")

    summaries = {}
    curves = {}
    for group in NA_GROUPS:
        summaries[group] = {}
        curves[group] = {}
        for species in ("Human", "Mouse"):
            selected = [row for row in rows if na_recording_species(str(row["Filename"])) == species]
            group_values: dict[int, list[float | None]] = {}
            for ap_number, header in columns[group].items():
                group_values[ap_number] = [numeric(row.get(header)) for row in selected]
            summaries[group][species] = {
                f"AP{ap}": summarize(group_values[ap]) for ap in AP_CHECKPOINTS
            }
            curves[group][species] = [
                {"ap": ap, **summarize(group_values[ap])}
                for ap in range(1, 201)
            ]

    # Preserve the source workbook's variable descriptions verbatim. The Mwide
    # description duplicates Hwide, so the source label remains unresolved.
    variable_descriptions = {}
    for row in variable_rows:
        key = row.get("variables in the table")
        value = row.get("explanation")
        if isinstance(key, str) and key.startswith("relative_amp_"):
            variable_descriptions[key.strip()] = value

    code = plot_script.replace(" ", "").replace("\n", "")
    source_script_rules = {
        "species_rule_mouse_prefix": "Filename.str.startswith('M')" in code,
        "default_species_human": "df_l['Species']='Human'" in code,
        "figure2_primary_group_hnarrow": "APwave.isin(['Hnarrow'])" in code,
        "supplementary_waveform_groups_hwide_mwide": "APwave.isin(['Hwide','Mwide'])" in code,
    }
    if not all(source_script_rules.values()):
        raise RuntimeError(f"Unexpected Figure2 plotting-script transformations: {source_script_rules}")

    return {
        "file": FILES["na"]["path"],
        "workbook_dimension": dimension,
        "variables_dimension": variable_dimension,
        "recordings": len(rows),
        "species_counts_from_published_plotting_script_rule": dict(species_counts),
        "species_rule": "Filename begins with 'M' => Mouse; all other prefixes => Human (plots_fig2.py)",
        "duplicate_filename_count": 0,
        "ap_numbers_per_group": {group: len(columns[group]) for group in NA_GROUPS},
        "raw_group_labels": list(NA_GROUPS),
        "source_plotting_script_rules": source_script_rules,
        "workbook_variable_descriptions": variable_descriptions,
        "variable_metadata_warning": (
            "The variables sheet labels both Mwide and Hwide as Human waveform 2. "
            "The plotting script treats Hwide and Mwide as distinct APwave groups; "
            "therefore do not silently correct the workbook text. Retain raw group labels "
            "until the source figure/supplementary legend resolves the discrepancy."
        ),
        "descriptive_normalized_amplitude_summary": summaries,
        "descriptive_curves": curves,
        "inferential_statistics": "Not recomputed; summaries are descriptive mean/median/SD/SEM across recordings.",
    }


def summarize_k(payload: bytes) -> dict[str, Any]:
    headers, rows, dimension = load_sheet_rows(payload, "data")
    _, variable_rows, variable_dimension = load_sheet_rows(payload, "variables")
    columns: dict[str, dict[int, str]] = {"h": {}, "m": {}}
    for header in headers:
        parsed = parse_k_header(header)
        if parsed:
            waveform, ap_number = parsed
            if ap_number in columns[waveform]:
                raise RuntimeError(f"Duplicate K column {waveform} AP{ap_number}")
            columns[waveform][ap_number] = header
    for waveform, mapping in columns.items():
        if sorted(mapping) != list(range(1, 202)):
            raise RuntimeError(f"K normalized group {waveform} must have AP1..AP201; found {len(mapping)}")

    species_counts = Counter(str(row.get("species")) for row in rows)
    expected_species_counts = {"H": 14, "M": 11}
    if dict(species_counts) != expected_species_counts:
        raise RuntimeError(f"K workbook species counts differ from published sample sizes: {dict(species_counts)}")
    filenames = [str(row["Filename"]) for row in rows]
    if len(filenames) != len(set(filenames)):
        raise RuntimeError("Duplicate K recording filenames")

    summaries = {}
    curves = {}
    paired_differences = {}
    for species, species_label in (("H", "Human"), ("M", "Mouse")):
        selected = [row for row in rows if str(row.get("species")) == species]
        summaries[species_label] = {}
        curves[species_label] = {}
        for waveform in ("h", "m"):
            group_values = {
                ap: [numeric(row.get(columns[waveform][ap])) for row in selected]
                for ap in range(1, 201)  # plotting script excludes AP201
            }
            summaries[species_label][waveform] = {
                f"AP{ap}": summarize(group_values[ap]) for ap in AP_CHECKPOINTS
            }
            curves[species_label][waveform] = [
                {"ap": ap, **summarize(group_values[ap])}
                for ap in range(1, 201)
            ]
        paired_differences[species_label] = {}
        for ap in (5, 200):
            values = []
            for row in selected:
                human_input = numeric(row.get(columns["h"][ap]))
                mouse_input = numeric(row.get(columns["m"][ap]))
                if human_input is not None and mouse_input is not None:
                    values.append(human_input - mouse_input)
                else:
                    values.append(None)
            paired_differences[species_label][f"AP{ap}_human_minus_mouse_input"] = summarize(values)

    variable_descriptions = {}
    for row in variable_rows:
        key = row.get("variables in the table")
        value = row.get("explanation")
        if isinstance(key, str) and key.startswith("amp_"):
            variable_descriptions[key.strip()] = value

    return {
        "file": FILES["k"]["path"],
        "workbook_dimension": dimension,
        "variables_dimension": variable_dimension,
        "recordings": len(rows),
        "species_counts": dict(species_counts),
        "ap_numbers_per_group": {waveform: len(columns[waveform]) for waveform in ("h", "m")},
        "analysis_ap_range": [1, 200],
        "ap201_note": "The workbook has AP1..AP201; the published plotting script filters APnr<201 and therefore uses AP1..AP200.",
        "workbook_variable_descriptions": variable_descriptions,
        "descriptive_normalized_amplitude_summary": summaries,
        "descriptive_curves": curves,
        "paired_waveform_difference": paired_differences,
        "inferential_statistics": "Not recomputed; summaries are descriptive mean/median/SD/SEM across recordings.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("wilbers-figure2-data-audit.json"))
    args = parser.parse_args()

    payloads = {}
    integrity = {}
    for name in ("na", "k", "plot_script", "stats_script"):
        payloads[name], integrity[name] = fetch_verified(FILES[name])

    plot_script = payloads["plot_script"].decode("utf-8-sig")
    stats_script = payloads["stats_script"].decode("utf-8-sig")
    report = {
        "schema_version": 1,
        "status": "dataverse_figure2_raw_workbooks_sha1_sha256_verified_and_descriptively_analyzed",
        "runtime_eligible": False,
        "dataset": {"doi": "10.34894/L5J0SD", "version": 3, "license": "CC0-1.0", "total_files": 65},
        "source_integrity": {
            name: {
                "path": FILES[name]["path"],
                "id": FILES[name]["id"],
                "bytes": len(payloads[name]),
                "sha1": hashlib.sha1(payloads[name]).hexdigest(),
                "sha256": hashlib.sha256(payloads[name]).hexdigest(),
                "download": integrity[name],
            }
            for name in FILES
        },
        "na": summarize_na(payloads["na"], plot_script),
        "k": summarize_k(payloads["k"]),
        "stat_script": {
            "path": FILES["stats_script"]["path"],
            "bytes": len(stats_script.encode("utf-8")),
            "sha1": hashlib.sha1(payloads["stats_script"]).hexdigest(),
            "sha256": hashlib.sha256(payloads["stats_script"]).hexdigest(),
            "source_code_review": "Captured and integrity-checked; original inferential code is not re-executed by this descriptive audit.",
        },
        "interpretation_limits": [
            "These are AP-clamp normalized current-amplitude observations from somatic nucleated patches, not conductance-density measurements.",
            "Na species labels are reproduced exactly from plots_fig2.py: filenames starting with M are Mouse; other filenames are Human.",
            "The Na variables worksheet has an unresolved duplicate description for Mwide and Hwide; raw group labels are retained without silently correcting metadata.",
            "K H/M species labels are explicit in the workbook; h and m suffixes denote human and mouse input waveforms according to the variables worksheet.",
            "Statistics here are descriptive only; no p-values or new inferential claims are generated.",
            "No voltage-clamp trace replay has been performed by this workbook audit.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
