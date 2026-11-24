#!/usr/bin/env python3
"""Reproducible synthesis of four matched 7-port/9-port PRIMA morphology holdouts.

This script validates the archived per-morphology JSON/CSV outputs before it
writes the cross-morphology CSV and Markdown report. It does not rerun NEURON
or alter the production solver.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "amsn-core" / "results"
REPORT_PATH = ROOT / "amsn-core" / "research" / "PRIMA_CROSS_MORPHOLOGY_SYNTHESIS_2026-11-24.md"
CSV_PATH = RESULTS / "prima_cross_morphology_synthesis_2026-11-24.csv"

EXPECTED_COVERAGE = {
    "models": 36,
    "frequency": 324,
    "transient": 1728,
    "matched_shared": 756,
    "q25_only": 216,
    "hines_shared": 378,
}
PROTOCOL_KEYS = (
    "dt_ms",
    "duration_ms",
    "expansion_shifts_hz",
    "frequencies_hz",
    "orders",
    "parameter_scenarios",
    "pulse_amplitude_pA",
    "pulse_onset_ms",
    "pulse_widths_ms",
    "shift_strategy",
    "sources",
)
CASES = (
    {
        "id": "NMO_162186",
        "prefix": "NMO_162186_prima_7v9port_matched_order_2026-11-23",
        "workflow_run": "https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520",
    },
    {
        "id": "NMO_03524",
        "prefix": "NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23",
        "workflow_run": "https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785",
    },
    {
        "id": "NMO_163775",
        "prefix": "NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24",
        "workflow_run": "https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600",
    },
    {
        "id": "NMO_107159",
        "prefix": "NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24",
        "workflow_run": "https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588",
    },
)
CSV_FIELDS = (
    "morphology_id",
    "morphology_label",
    "experimental_condition",
    "brain_region",
    "axon_complete",
    "physical_integrity",
    "mesh_max_segment_um",
    "swc_record_count",
    "electrical_compartments",
    "swc_sha256",
    "basis_order",
    "matched_shared_output_pairs",
    "nine_port_worse_pairs",
    "nine_port_better_pairs",
    "ties_within_1e_15_pct_points",
    "median_error_ratio_nine_over_seven",
    "max_error_ratio_nine_over_seven",
    "max_seven_port_nrmse_pct",
    "max_nine_port_nrmse_pct",
    "q25_observations",
    "median_q25_nrmse_pct",
    "max_q25_nrmse_pct",
    "hines_shared_checks",
    "hines_max_absolute_difference_v",
    "hines_max_relative_l2_difference_pct",
    "workflow_run",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def close_enough(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=2e-12, abs_tol=1e-15)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"{path}: expected a JSON object")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def protocol_signature(protocol: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        tuple(protocol[key]) if isinstance(protocol[key], list) else protocol[key]
        for key in PROTOCOL_KEYS
    )


def validate_exact_coverage(coverage: dict[str, Any], morphology_id: str) -> None:
    normalized = {key: int(coverage.get(key, -1)) for key in EXPECTED_COVERAGE}
    require(
        normalized == EXPECTED_COVERAGE,
        f"{morphology_id}: exact coverage mismatch: {normalized}",
    )


def validate_summary_files(
    report: dict[str, Any],
    matched_csv: list[dict[str, str]],
    q25_csv: list[dict[str, str]],
    morphology_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    report_matched = {int(row["basis_order"]): row for row in report["matched_shared_summary"]}
    csv_matched = {int(row["basis_order"]): row for row in matched_csv}
    report_q25 = {int(row["basis_order"]): row for row in report["q25_summary"]}
    csv_q25 = {int(row["basis_order"]): row for row in q25_csv}
    require(set(report_matched) == {112, 168}, f"{morphology_id}: JSON matched orders missing")
    require(set(csv_matched) == {112, 168}, f"{morphology_id}: CSV matched orders missing")
    require(set(report_q25) == {112, 168}, f"{morphology_id}: JSON q25 orders missing")
    require(set(csv_q25) == {112, 168}, f"{morphology_id}: CSV q25 orders missing")

    matched_rows: list[dict[str, Any]] = []
    q25_rows: list[dict[str, Any]] = []
    for order in (112, 168):
        source = report_matched[order]
        archived = csv_matched[order]
        for key in (
            "matched_shared_output_pairs",
            "nine_port_worse_pairs",
            "nine_port_better_pairs",
            "ties_within_1e_15_pct_points",
        ):
            require(
                int(source[key]) == int(archived[key]),
                f"{morphology_id} order {order}: matched CSV disagrees on {key}",
            )
        for key in (
            "median_error_ratio_nine_over_seven",
            "max_error_ratio_nine_over_seven",
            "max_seven_port_nrmse_pct",
            "max_nine_port_nrmse_pct",
        ):
            require(
                close_enough(source[key], archived[key]),
                f"{morphology_id} order {order}: matched CSV disagrees on {key}",
            )
        require(
            int(archived["nine_port_worse_pairs"])
            + int(archived["nine_port_better_pairs"])
            + int(archived["ties_within_1e_15_pct_points"])
            == int(archived["matched_shared_output_pairs"]),
            f"{morphology_id} order {order}: paired outcomes do not sum to coverage",
        )

        qsource = report_q25[order]
        qarchived = csv_q25[order]
        require(
            int(qsource["q25_observations"]) == int(qarchived["q25_observations"]),
            f"{morphology_id} order {order}: q25 CSV disagrees on observation count",
        )
        for key in ("median_q25_nrmse_pct", "max_q25_nrmse_pct"):
            require(
                close_enough(qsource[key], qarchived[key]),
                f"{morphology_id} order {order}: q25 CSV disagrees on {key}",
            )
        matched_rows.append(dict(archived))
        q25_rows.append(dict(qarchived))
    return matched_rows, q25_rows


def load_case(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    prefix = spec["prefix"]
    report_path = root / "amsn-core" / "results" / f"{prefix}_report.json"
    matched_path = root / "amsn-core" / "results" / f"{prefix}_matched_summary.csv"
    q25_path = root / "amsn-core" / "results" / f"{prefix}_q25_summary.csv"
    hines_path = root / "amsn-core" / "results" / f"{prefix}_hines_shared.csv"

    report = read_json(report_path)
    morphology_id = spec["id"]
    require(
        report.get("status") == "matched_7port_9port_prima_holdout_replay_passed",
        f"{morphology_id}: source report is not marked as a passed matched replay",
    )
    validate_exact_coverage(report.get("exact_coverage", {}), morphology_id)

    morphology = report.get("morphology", {})
    protocol = report.get("protocol", {})
    require(morphology.get("label"), f"{morphology_id}: morphology label missing")
    require(morphology.get("swc_sha256"), f"{morphology_id}: SWC hash missing")
    require(protocol.get("mesh_max_segment_um") in (0.125, 0.5), f"{morphology_id}: unexpected mesh cap")
    for key in PROTOCOL_KEYS:
        require(key in protocol, f"{morphology_id}: protocol field {key} missing")

    matched_rows, q25_rows = validate_summary_files(
        report,
        read_csv(matched_path),
        read_csv(q25_path),
        morphology_id,
    )

    hines_rows = read_csv(hines_path)
    require(
        len(hines_rows) == EXPECTED_COVERAGE["hines_shared"],
        f"{morphology_id}: expected 378 Hines checks, found {len(hines_rows)}",
    )
    hines_abs = [float(row["max_absolute_hines_trace_difference_v"]) for row in hines_rows]
    hines_rel = [float(row["relative_l2_difference_pct"]) for row in hines_rows]
    max_hines_abs = max(hines_abs, default=float("inf"))
    max_hines_rel = max(hines_rel, default=float("inf"))
    require(
        all(value == 0.0 for value in hines_abs + hines_rel),
        f"{morphology_id}: shared Hines traces are not exactly equal",
    )

    return {
        "id": morphology_id,
        "morphology": morphology,
        "protocol": protocol,
        "matched": matched_rows,
        "q25": q25_rows,
        "hines_checks": len(hines_rows),
        "hines_max_abs": max_hines_abs,
        "hines_max_rel": max_hines_rel,
        "coverage": report["exact_coverage"],
        "scientific_limits": report.get("scientific_limits", []),
        "workflow_run": spec["workflow_run"],
    }


def load_dataset(root: Path) -> list[dict[str, Any]]:
    cases = [load_case(root, spec) for spec in CASES]
    require(len({case["id"] for case in cases}) == 4, "Expected four unique morphology holdouts")
    reference = protocol_signature(cases[0]["protocol"])
    for case in cases[1:]:
        require(
            protocol_signature(case["protocol"]) == reference,
            f"{case['id']}: protocol differs beyond the documented mesh-cap variation",
        )
    return cases


def build_rows(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        morphology = case["morphology"]
        for matched, q25 in zip(case["matched"], case["q25"], strict=True):
            rows.append(
                {
                    "morphology_id": case["id"],
                    "morphology_label": morphology.get("label", ""),
                    "experimental_condition": morphology.get("experimental_condition", ""),
                    "brain_region": morphology.get("brain_region", ""),
                    "axon_complete": str(bool(morphology.get("axon_complete", False))).lower(),
                    "physical_integrity": morphology.get("physical_integrity", ""),
                    "mesh_max_segment_um": case["protocol"]["mesh_max_segment_um"],
                    "swc_record_count": morphology.get("swc_record_count", ""),
                    "electrical_compartments": morphology.get("electrical_compartments", ""),
                    "swc_sha256": morphology.get("swc_sha256", ""),
                    "basis_order": int(matched["basis_order"]),
                    "matched_shared_output_pairs": int(matched["matched_shared_output_pairs"]),
                    "nine_port_worse_pairs": int(matched["nine_port_worse_pairs"]),
                    "nine_port_better_pairs": int(matched["nine_port_better_pairs"]),
                    "ties_within_1e_15_pct_points": int(matched["ties_within_1e_15_pct_points"]),
                    "median_error_ratio_nine_over_seven": float(matched["median_error_ratio_nine_over_seven"]),
                    "max_error_ratio_nine_over_seven": float(matched["max_error_ratio_nine_over_seven"]),
                    "max_seven_port_nrmse_pct": float(matched["max_seven_port_nrmse_pct"]),
                    "max_nine_port_nrmse_pct": float(matched["max_nine_port_nrmse_pct"]),
                    "q25_observations": int(q25["q25_observations"]),
                    "median_q25_nrmse_pct": float(q25["median_q25_nrmse_pct"]),
                    "max_q25_nrmse_pct": float(q25["max_q25_nrmse_pct"]),
                    "hines_shared_checks": case["hines_checks"],
                    "hines_max_absolute_difference_v": case["hines_max_abs"],
                    "hines_max_relative_l2_difference_pct": case["hines_max_rel"],
                    "workflow_run": case["workflow_run"],
                }
            )
    return rows


def render_csv(rows: list[dict[str, Any]]) -> str:
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def fmt(value: float) -> str:
    return f"{float(value):.6g}"


def render_markdown(cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> str:
    total = {
        key: sum(int(case["coverage"][key]) for case in cases)
        for key in EXPECTED_COVERAGE
    }
    order112 = [row for row in rows if row["basis_order"] == 112]
    order168 = [row for row in rows if row["basis_order"] == 168]
    near_parity_112 = sum(0.99 <= row["median_error_ratio_nine_over_seven"] <= 1.01 for row in order112)
    near_parity_168 = sum(0.99 <= row["median_error_ratio_nine_over_seven"] <= 1.01 for row in order168)

    lines = [
        "# PRIMA matched 7-port / 9-port synthesis across four morphologies",
        "",
        "**Date:** 24 November 2026  ",
        "**Status:** reproducible synthesis of archived, successful single-morphology workflows; no production solver defaults changed.  ",
        "**Scope:** passive linear-RC reduced models compared with full Hines references; not active-neuron or biological validation.",
        "",
        "## Research question",
        "",
        "Does adding basal-q25 and apical-q25 output ports impose a consistent accuracy cost on the seven shared outputs, or does that cost depend on morphology and basis order?",
        "",
        "The analysis reads each morphology's report JSON, matched-summary CSV, q25-summary CSV and all 378 shared-Hines rows. It checks their agreement, complete coverage, common protocol and exact Hines trace equality before generating the summary. It does not rerun the underlying NEURON simulations.",
        "",
        "## Holdout metadata and mesh strata",
        "",
        "| Holdout | Experimental context | Axon metadata | Mesh cap (µm) | SWC records | Electrical compartments |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for case in cases:
        m = case["morphology"]
        lines.append(
            f"| {case['id']} | {m.get('experimental_condition', 'not reported')} | "
            f"{'complete' if m.get('axon_complete') else 'incomplete / not marked complete'} | "
            f"{fmt(case['protocol']['mesh_max_segment_um'])} | "
            f"{m.get('swc_record_count', '—')} | {m.get('electrical_compartments', '—')} |"
        )
    lines.extend(
        [
            "",
            "Two holdouts use a 0.125 µm NEURON segment cap (NMO_162186 and NMO_03524); two use 0.5 µm (NMO_163775 and NMO_107159). NMO_163775 is a mouse Control-condition reconstruction whose NeuroMorpho record says No Diameter; its standardized SWC radii are not measured biological diameters. NMO_107159 is a human pyramidal comparison cell with Diameter/3D/Angles metadata, not a rosehip interneuron. The cell-level contexts are not a matched biological population.",
            "",
            "## Protocol and coverage checks",
            "",
            "All four reports use the same orders (112, 168), six extended-10-kHz shifts (0, 100, 1,000, 3,000, 6,000, 10,000 Hz), nine passive parameter scenarios, nine AC frequencies (0.1 Hz–10 kHz), three current-source locations, two pulse widths (2/10 ms), 10 pA pulses, 2 ms onset, 20 ms duration and dt = 0.1 ms. The mesh cap is the documented protocol difference.",
            "",
            "| Output across four holdouts | Verified rows |",
            "|---|---:|",
            f"| Model configurations | {total['models']:,} |",
            f"| AC frequency matrices | {total['frequency']:,} |",
            f"| Per-port transient measurements | {total['transient']:,} |",
            f"| Paired shared-output comparisons | {total['matched_shared']:,} |",
            f"| q25-only output observations | {total['q25_only']:,} |",
            f"| Shared full-Hines consistency checks | {total['hines_shared']:,} |",
            "",
            "The four archived Hines CSVs each contain 378 rows. Across all 1,512 checks, the maximum absolute trace difference is exactly 0 V and the maximum relative L2 difference is exactly 0%. This confirms that the two layouts use identical shared-node Hines reference traces within each matched experiment.",
            "",
            "## Matched shared-output results",
            "",
            "Each ratio is the median or maximum of the paired nine-port / seven-port transient NRMSE ratios over 378 matched shared-output pairs at that basis order. Ratios are dimensionless; NRMSE columns are percentages.",
            "",
            "| Holdout | Mesh (µm) | Order | 9-port worse / better / tie | Median 9/7 ratio | Max 9/7 ratio | Max 7-port NRMSE (%) | Max 9-port NRMSE (%) | Max q25 NRMSE (%) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['morphology_id']} | {fmt(row['mesh_max_segment_um'])} | {row['basis_order']} | "
            f"{row['nine_port_worse_pairs']} / {row['nine_port_better_pairs']} / {row['ties_within_1e_15_pct_points']} | "
            f"{fmt(row['median_error_ratio_nine_over_seven'])} | {fmt(row['max_error_ratio_nine_over_seven'])} | "
            f"{fmt(row['max_seven_port_nrmse_pct'])} | {fmt(row['max_nine_port_nrmse_pct'])} | "
            f"{fmt(row['max_q25_nrmse_pct'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- At order 112, {near_parity_112}/4 holdouts fall within a descriptive 0.99–1.01 median-ratio band. NMO_03524 is effectively at parity; NMO_162186, NMO_163775 and NMO_107159 show larger relative nine-port penalties.",
            f"- At order 168, {near_parity_168}/4 holdouts fall within that same descriptive band. NMO_162186, NMO_03524 and NMO_107159 are near parity; NMO_163775 remains the exception with a 14.501× median ratio.",
            "- The large ratios must not be read without the absolute errors. For NMO_163775 at order 168, the maximum nine-port shared-output NRMSE is 6.0657e−7%, despite its 14.501× median ratio. This is a relative regression against an already very small seven-port baseline, not evidence of a large absolute voltage error.",
            "- The q25-only outputs are represented at both orders in all four experiments. Order 168 reduces the maximum q25 NRMSE substantially on NMO_162186, NMO_163775 and NMO_107159; NMO_03524 is already at very small q25 error at order 112.",
            "- The result rejects a universal rule that nine ports always require order 168, but it also rejects assuming order 112 is uniformly safe. Port-count cost depends on morphology under this passive protocol.",
            "",
            "The 0.125 µm and 0.5 µm strata prevent a pooled interpretation of absolute error or runtime across all four morphologies. The paired ratio is valid within each morphology/order comparison because its seven- and nine-port candidates share that run's geometry, parameters, mesh, sources and exact output identities. It is not a substitute for a mesh-convergence study.",
            "",
            "## Research decision",
            "",
            "1. Keep full Hines as the canonical reference and do not change production defaults from these passive holdouts.",
            "2. Treat order 168 as a strong candidate for q25-enriched output layouts, but retain NMO_163775 as an unresolved relative-error exception and compare its absolute error against an application-defined tolerance before any recommendation.",
            "3. Do not pool absolute NRMSE, wall time or memory across different mesh caps, morphology classes or source conditions.",
            "",
            "## Next experiments",
            "",
            "1. **Mesh-harmonization factorial:** rerun at least one morphology from each existing mesh stratum at both 0.125 and 0.5 µm, with identical seven/nine ports, orders, shifts and parameter scenarios. Separate mesh sensitivity from morphology effects and preserve per-run resource measurements.",
            "2. **Ablation/localization:** for the NMO_163775 order-168 residual, localize which shared ports, sources, pulse widths and passive-parameter scenarios dominate the 9/7 ratio; report absolute NRMSE and the seven-port denominator for every worst pair.",
            "3. **Separate field-coupled solver track:** audit the 23 November 2026 bioRxiv preprint on hierarchical matrix compression for Cable-BEM (DOI 10.64898/2026.11.20.768225). It reports 2.7–6.1× memory reduction for one L2/3 bidomain case and markedly different errors for HSS/HODLR versus H/H2 formats at tolerance 10⁻³. This is a distinct bidomain / extracellular-field problem, not a directly comparable PRIMA result; benchmark it separately only if extracellular coupling or multicellular ephaptic effects become an AMSN requirement.",
            "",
            "## Source reports and workflows",
            "",
        ]
    )
    for case in cases:
        prefix = next(spec["prefix"] for spec in CASES if spec["id"] == case["id"])
        lines.append(
            f"- **{case['id']}**: [report JSON](../results/{prefix}_report.json), "
            f"[matched summary](../results/{prefix}_matched_summary.csv), "
            f"[q25 summary](../results/{prefix}_q25_summary.csv), "
            f"[Hines checks](../results/{prefix}_hines_shared.csv), "
            f"[successful workflow]({case['workflow_run']})."
        )
    lines.extend(
        [
            "",
            "External lead: Esparza Rivera & Gomez, *Hierarchical Matrix Compression for Fast Bidomain Simulation of Multicellular Neuron Models*, bioRxiv v1 posted 23 November 2026, DOI [10.64898/2026.11.20.768225](https://doi.org/10.64898/2026.11.20.768225). It is a preprint and requires independent reproduction before adoption.",
            "",
            "## Limitations",
            "",
            "- Four single-cell morphology holdouts are not a representative human or mouse population.",
            "- All comparisons are passive linear-RC numerical checks against full Hines; they do not validate active ion channels, nonlinear synapses, plasticity, calcium signaling or biological function.",
            "- Relative ratios can be large when the seven-port denominator is very small; both relative and absolute errors must be reported.",
            "- Two mesh caps are present, and the Peng record has no measured diameter metadata. Absolute cross-holdout errors are not pooled.",
            "- The synthesis validates archived result consistency and coverage; it does not rerun the original simulations.",
            "",
            "Full Hines remains canonical. No production order default, solver behavior or runtime path is changed.",
            "",
        ]
    )
    return "\n".join(lines)


def expected_outputs(root: Path) -> dict[Path, str]:
    cases = load_dataset(root)
    rows = build_rows(cases)
    return {
        root / "amsn-core" / "results" / CSV_PATH.name: render_csv(rows),
        root / "amsn-core" / "research" / REPORT_PATH.name: render_markdown(cases, rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the generated CSV and Markdown report")
    mode.add_argument("--check", action="store_true", help="fail if generated files are missing or stale")
    args = parser.parse_args()
    outputs = expected_outputs(ROOT)
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"WROTE {path.relative_to(ROOT)}")
        return 0
    stale: list[str] = []
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
    if stale:
        raise SystemExit("Generated synthesis is missing or stale: " + ", ".join(stale))
    print(f"OK: {len(outputs)} generated files match all four validated source datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
