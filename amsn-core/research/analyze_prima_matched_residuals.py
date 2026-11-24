#!/usr/bin/env python3
"""Localize paired 7-port/9-port PRIMA transient residuals by source and output.

The analysis consumes the validated per-morphology matched_shared.csv files.
It does not rerun NEURON. Every ratio is paired at identical morphology,
basis order, parameter scenario, source, pulse width and shared SWC output ID.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from synthesize_prima_cross_morphology import CASES, ROOT

EXPECTED_ORDERS = (112, 168)
EXPECTED_PER_ORDER = 378
EXPECTED_TOTAL_PER_MORPHOLOGY = 756
EXPECTED_SCENARIOS = 9
EXPECTED_SOURCES = ("soma", "basal_q75", "apical_q75")
EXPECTED_PULSE_WIDTHS = (2.0, 10.0)
EXPECTED_SHARED_PORTS = 7
OUTPUT = ROOT / "amsn-core" / "results" / "prima_matched_residual_diagnostics_2026-11-24.csv"
REPORT = ROOT / "amsn-core" / "research" / "PRIMA_MATCHED_RESIDUAL_DIAGNOSTICS_2026-11-24.md"
OUTPUT_FIELDS = (
    "morphology_id", "basis_order", "source_name", "port_swc_id", "port_role",
    "paired_observations", "nine_port_worse_pairs", "nine_port_better_pairs",
    "ties_within_1e_15_pct_points", "median_error_ratio_nine_over_seven",
    "p90_error_ratio_nine_over_seven", "max_error_ratio_nine_over_seven",
    "median_seven_port_nrmse_pct", "median_nine_port_nrmse_pct",
    "max_seven_port_nrmse_pct", "max_nine_port_nrmse_pct",
    "median_absolute_delta_pct_points", "max_absolute_delta_pct_points",
    "workflow_run",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def nearest_rank(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("cannot compute a quantile from an empty sequence")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def close_enough(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=2e-10, abs_tol=1e-13)


def load_all_rows(root: Path = ROOT) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in CASES:
        path = root / "amsn-core" / "results" / f"{spec['prefix']}_matched_shared.csv"
        raw = read_csv(path)
        require(len(raw) == EXPECTED_TOTAL_PER_MORPHOLOGY,
                f"{spec['id']}: expected {EXPECTED_TOTAL_PER_MORPHOLOGY} rows, got {len(raw)}")
        seen: set[tuple[Any, ...]] = set()
        by_order: dict[int, int] = defaultdict(int)
        roles_by_node: dict[int, set[str]] = defaultdict(set)
        scenario_names: set[str] = set()
        source_names: set[str] = set()
        pulse_widths: set[float] = set()

        for item in raw:
            try:
                order = int(item["basis_order"])
                scenario = item["parameter_scenario"]
                source = item["source_name"]
                pulse = float(item["pulse_width_ms"])
                node = int(item["port_swc_id"])
                role = item["port_roles"]
                e7 = float(item["seven_port_nrmse_pct"])
                e9 = float(item["nine_port_nrmse_pct"])
                ratio = float(item["error_ratio_nine_over_seven"])
                delta = float(item["nine_port_minus_seven_port_pct_points"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{spec['id']}: malformed paired row: {item}") from exc

            require(order in EXPECTED_ORDERS, f"{spec['id']}: unexpected order {order}")
            require(all(math.isfinite(value) for value in (e7, e9, ratio, delta)),
                    f"{spec['id']}: non-finite metric in {item}")
            require(e7 > 0.0, f"{spec['id']}: zero seven-port denominator")
            require(e9 >= 0.0, f"{spec['id']}: negative nine-port NRMSE")
            require(close_enough(ratio, e9 / e7), f"{spec['id']}: stored ratio is not e9/e7")
            require(close_enough(delta, e9 - e7), f"{spec['id']}: stored delta is inconsistent")

            key = (order, scenario, source, pulse, node)
            require(key not in seen, f"{spec['id']}: duplicate paired key {key}")
            seen.add(key)
            by_order[order] += 1
            roles_by_node[node].add(role)
            scenario_names.add(scenario)
            source_names.add(source)
            pulse_widths.add(pulse)
            output.append({
                "morphology_id": spec["id"],
                "workflow_run": spec["workflow_run"],
                "basis_order": order,
                "parameter_scenario": scenario,
                "source_name": source,
                "pulse_width_ms": pulse,
                "port_swc_id": node,
                "port_role": role,
                "seven_port_nrmse_pct": e7,
                "nine_port_nrmse_pct": e9,
                "error_ratio_nine_over_seven": ratio,
                "delta_pct_points": delta,
            })

        require(by_order == {112: EXPECTED_PER_ORDER, 168: EXPECTED_PER_ORDER},
                f"{spec['id']}: per-order coverage mismatch {dict(by_order)}")
        require(len(scenario_names) == EXPECTED_SCENARIOS,
                f"{spec['id']}: expected nine scenarios, got {sorted(scenario_names)}")
        require(source_names == set(EXPECTED_SOURCES),
                f"{spec['id']}: source coverage mismatch {sorted(source_names)}")
        require(pulse_widths == set(EXPECTED_PULSE_WIDTHS),
                f"{spec['id']}: pulse-width coverage mismatch {sorted(pulse_widths)}")
        require(len(roles_by_node) == EXPECTED_SHARED_PORTS,
                f"{spec['id']}: expected seven shared outputs, got {len(roles_by_node)}")
        require(all(len(roles) == 1 for roles in roles_by_node.values()),
                f"{spec['id']}: shared output role is inconsistent")
    return output


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(bool(rows), "cannot summarize an empty group")
    ratios = [float(row["error_ratio_nine_over_seven"]) for row in rows]
    e7 = [float(row["seven_port_nrmse_pct"]) for row in rows]
    e9 = [float(row["nine_port_nrmse_pct"]) for row in rows]
    deltas = [float(row["delta_pct_points"]) for row in rows]
    return {
        "paired_observations": len(rows),
        "nine_port_worse_pairs": sum(delta > 1e-15 for delta in deltas),
        "nine_port_better_pairs": sum(delta < -1e-15 for delta in deltas),
        "ties_within_1e_15_pct_points": sum(abs(delta) <= 1e-15 for delta in deltas),
        "median_error_ratio_nine_over_seven": statistics.median(ratios),
        "p90_error_ratio_nine_over_seven": nearest_rank(ratios, 0.90),
        "max_error_ratio_nine_over_seven": max(ratios),
        "median_seven_port_nrmse_pct": statistics.median(e7),
        "median_nine_port_nrmse_pct": statistics.median(e9),
        "max_seven_port_nrmse_pct": max(e7),
        "max_nine_port_nrmse_pct": max(e9),
        "median_absolute_delta_pct_points": statistics.median(abs(delta) for delta in deltas),
        "max_absolute_delta_pct_points": max(abs(delta) for delta in deltas),
    }


def grouped(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in key_fields)].append(row)
    return groups


def build_source_output_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ("morphology_id", "basis_order", "source_name", "port_swc_id", "port_role")
    groups = grouped(rows, keys)
    result: list[dict[str, Any]] = []
    for key, subset in sorted(groups.items(), key=lambda item: item[0]):
        morphology_id, order, source, node, role = key
        result.append({
            "morphology_id": morphology_id,
            "basis_order": order,
            "source_name": source,
            "port_swc_id": node,
            "port_role": role,
            **summarize(subset),
            "workflow_run": subset[0]["workflow_run"],
        })
    expected = len(CASES) * len(EXPECTED_ORDERS) * len(EXPECTED_SOURCES) * EXPECTED_SHARED_PORTS
    require(len(result) == expected, f"unexpected aggregation row count: {len(result)} != {expected}")
    require(all(row["paired_observations"] == 18 for row in result),
            "each source/output group must contain nine scenarios × two pulse widths")
    return result


def render_csv(rows: list[dict[str, Any]]) -> str:
    from io import StringIO
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def fmt(value: float) -> str:
    return f"{float(value):.6g}"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines


def render_report(rows: list[dict[str, Any]], output_rows: list[dict[str, Any]]) -> str:
    overall = grouped(rows, ("morphology_id", "basis_order"))
    source_groups = grouped(rows, ("morphology_id", "basis_order", "source_name"))
    port_groups = grouped(rows, ("morphology_id", "basis_order", "port_role"))
    source_pulse_groups = grouped(rows, ("morphology_id", "basis_order", "source_name", "pulse_width_ms"))
    scenario_source_groups = grouped(rows, ("morphology_id", "basis_order", "parameter_scenario", "source_name"))
    lines = [
        "# PRIMA matched transient residual localization",
        "",
        "**Date:** 24 November 2026  ",
        "**Status:** reproducible diagnostics over archived, validated passive-RC holdouts.  ",
        "**Scope:** decomposition of existing paired results; not a new NEURON simulation or biological validation.",
        "",
        "## Research question",
        "",
        "For each morphology and basis order, where do the nine-port / seven-port shared-output error ratios arise: input source, output location, pulse width or passive parameter scenario?",
        "",
        "## Method and integrity checks",
        "",
        "The analyzer reads each holdout's matched_shared.csv. Each row is paired at identical morphology, order, parameter scenario, source, pulse width and shared SWC node ID. The script independently recomputes the stored error ratio and absolute NRMSE difference, rejects non-finite values and duplicate keys, and verifies 378 rows per order with nine scenarios × three sources × two pulse widths × seven shared outputs.",
        "",
        "The source/output table aggregates 18 paired observations per cell (nine scenarios × two pulse widths). Ratios are medians of paired nine-port NRMSE divided by seven-port NRMSE. NRMSE values are percentages; delta is in percentage points.",
        "",
        "## Overall paired results by morphology and order",
        "",
    ]
    table = []
    for (morphology_id, order), subset in sorted(overall.items()):
        s = summarize(subset)
        table.append([
            morphology_id, order, s["paired_observations"],
            f'{s["nine_port_worse_pairs"]}/{s["nine_port_better_pairs"]}/{s["ties_within_1e_15_pct_points"]}',
            fmt(s["median_error_ratio_nine_over_seven"]),
            fmt(s["p90_error_ratio_nine_over_seven"]),
            fmt(s["max_nine_port_nrmse_pct"]),
            fmt(s["max_absolute_delta_pct_points"]),
        ])
    lines += markdown_table(
        ["Holdout", "Order", "Pairs", "Worse / better / tie", "Median ratio", "P90 ratio", "Max 9-port NRMSE (%)", "Max |delta| (pp)"],
        table,
    )
    lines += [
        "",
        "## NMO_163775 — order 168 input-source decomposition",
        "",
        "The archived median 9/7 ratio is 14.501× overall. Each source group has 126 pairs (seven outputs × nine scenarios × two pulse widths).",
        "",
    ]
    source_table = []
    for (morphology_id, order, source), subset in sorted(source_groups.items()):
        if morphology_id == "NMO_163775" and order == 168:
            s = summarize(subset)
            source_table.append([
                source, s["paired_observations"],
                fmt(s["median_error_ratio_nine_over_seven"]),
                fmt(s["p90_error_ratio_nine_over_seven"]),
                fmt(s["median_seven_port_nrmse_pct"]),
                fmt(s["median_nine_port_nrmse_pct"]),
                fmt(s["max_nine_port_nrmse_pct"]),
            ])
    lines += markdown_table(
        ["Input source", "Pairs", "Median 9/7", "P90 9/7", "Median 7-port (%)", "Median 9-port (%)", "Max 9-port (%)"],
        source_table,
    )
    lines += [
        "",
        "## NMO_163775 — order 168 output-location decomposition",
        "",
        "Each output-role group has 54 pairs (three sources × nine scenarios × two pulse widths).",
        "",
    ]
    port_table = []
    for (morphology_id, order, role), subset in sorted(port_groups.items()):
        if morphology_id == "NMO_163775" and order == 168:
            s = summarize(subset)
            port_table.append([
                role, s["paired_observations"],
                fmt(s["median_error_ratio_nine_over_seven"]),
                fmt(s["p90_error_ratio_nine_over_seven"]),
                fmt(s["median_seven_port_nrmse_pct"]),
                fmt(s["median_nine_port_nrmse_pct"]),
                fmt(s["max_nine_port_nrmse_pct"]),
            ])
    port_table.sort(key=lambda row: float(row[2]), reverse=True)
    lines += markdown_table(
        ["Shared output", "Pairs", "Median 9/7", "P90 9/7", "Median 7-port (%)", "Median 9-port (%)", "Max 9-port (%)"],
        port_table,
    )
    lines += [
        "",
        "## NMO_163775 — source × output interaction",
        "",
        "These 21 groups each have 18 paired observations. They show whether a source/output combination is more sensitive than either marginal summary alone.",
        "",
    ]
    interaction_table = []
    for row in output_rows:
        if row["morphology_id"] == "NMO_163775" and row["basis_order"] == 168:
            interaction_table.append([
                row["source_name"], row["port_role"],
                fmt(row["median_error_ratio_nine_over_seven"]),
                fmt(row["max_error_ratio_nine_over_seven"]),
                fmt(row["median_seven_port_nrmse_pct"]),
                fmt(row["median_nine_port_nrmse_pct"]),
                fmt(row["max_nine_port_nrmse_pct"]),
            ])
    interaction_table.sort(key=lambda row: float(row[2]), reverse=True)
    lines += markdown_table(
        ["Input source", "Output", "Median 9/7", "Max 9/7", "Median 7-port (%)", "Median 9-port (%)", "Max 9-port (%)"],
        interaction_table,
    )
    lines += [
        "",
        "## Pulse-width sensitivity at NMO_163775, order 168",
        "",
        "Each source/pulse group has 63 pairs (nine scenarios × seven outputs).",
        "",
    ]
    pulse_table = []
    for (morphology_id, order, source, pulse), subset in sorted(source_pulse_groups.items()):
        if morphology_id == "NMO_163775" and order == 168:
            s = summarize(subset)
            pulse_table.append([
                source, f"{pulse:g} ms", s["paired_observations"],
                fmt(s["median_error_ratio_nine_over_seven"]),
                fmt(s["median_nine_port_nrmse_pct"]),
                fmt(s["max_nine_port_nrmse_pct"]),
            ])
    lines += markdown_table(
        ["Input source", "Pulse width", "Pairs", "Median 9/7", "Median 9-port (%)", "Max 9-port (%)"],
        pulse_table,
    )
    lines += [
        "",
        "## Parameter-scenario sensitivity at NMO_163775, order 168",
        "",
        "Each source/scenario group has 14 pairs (seven outputs × two pulse widths). This finite deterministic ±20% sweep is descriptive and does not establish a causal parameter effect.",
        "",
    ]
    scenario_table = []
    for (morphology_id, order, scenario, source), subset in scenario_source_groups.items():
        if morphology_id == "NMO_163775" and order == 168:
            s = summarize(subset)
            scenario_table.append([
                scenario, source, s["paired_observations"],
                fmt(s["median_error_ratio_nine_over_seven"]),
                fmt(s["median_seven_port_nrmse_pct"]),
                fmt(s["median_nine_port_nrmse_pct"]),
                fmt(s["max_nine_port_nrmse_pct"]),
            ])
    scenario_table.sort(key=lambda row: float(row[3]), reverse=True)
    lines += markdown_table(
        ["Parameter scenario", "Input source", "Pairs", "Median 9/7", "Median 7-port (%)", "Median 9-port (%)", "Max 9-port (%)"],
        scenario_table,
    )
    peng = summarize(overall[("NMO_163775", 168)])
    lines += [
        "",
        "## Interpretation",
        "",
        "- The relative penalty is source-dependent: soma and basal-q75 stimulation show larger median ratios than apical-q75 stimulation in this particular passive-RC protocol.",
        "- It is also output-dependent: soma and basal output roles show larger ratios than apical q75/q90 outputs. The interaction table shows the strongest source/output combinations.",
        f"- The overall median seven-port NRMSE is {fmt(peng['median_seven_port_nrmse_pct'])}% and median nine-port NRMSE is {fmt(peng['median_nine_port_nrmse_pct'])}%; maximum nine-port shared-output NRMSE is {fmt(peng['max_nine_port_nrmse_pct'])}%. The absolute values remain very small, so the ratio is not evidence of a large absolute voltage error.",
        "- The two pulse-width groups have similar order-of-magnitude median ratios; the archived data do not support claiming one pulse width alone explains the residual.",
        "- Parameter-scenario summaries vary, but the sweep is finite and deterministic. It is not a probabilistic sensitivity analysis and does not prove causal parameter mechanisms.",
        "- These diagnostics localize where the numerical difference appears in the tested protocol; they do not explain why the projection basis produces it. A mechanism-level explanation requires a targeted basis/port ablation or controlled perturbation.",
        "",
        "## Research decision and next experiment",
        "",
        "1. Do not reject the nine-port order-168 Peng candidate solely from the 14.501× ratio. Define an application-level absolute-error tolerance first; the repository has not established one.",
        "2. Preserve absolute NRMSE and paired 9/7 ratios together. Flag comparisons whose seven-port denominator is close to the numerical floor rather than presenting the ratio alone.",
        "3. Run a four-layout q25 ablation on the same morphology and mesh: seven canonical ports, seven plus basal-q25, seven plus apical-q25, and seven plus both q25. Match orders, shifts, scenarios, sources, pulses, dt and full-Hines shared outputs.",
        "4. Keep full Hines canonical and leave production defaults unchanged.",
        "",
        "## Source evidence",
        "",
    ]
    for spec in CASES:
        lines.append(
            f"- **{spec['id']}**: [paired shared-output CSV](../results/{spec['prefix']}_matched_shared.csv), "
            f"[validated workflow]({spec['workflow_run']})."
        )
    lines += [
        "",
        "## Limitations",
        "",
        "- Four single-cell morphology holdouts are not a representative biological population.",
        "- All comparisons are passive linear-RC transient comparisons against full Hines, not active-neuron or biological validation.",
        "- Ratios can be inflated by very small seven-port denominators; no universal application tolerance is assumed.",
        "- This decomposition is observational within a fixed deterministic experiment matrix; it does not prove a causal mechanism.",
        "- Mesh caps differ (0.125 µm vs 0.5 µm), so absolute cross-morphology errors are not pooled.",
        "",
        "No production solver code or defaults are changed. No new NEURON simulation is run by this analysis.",
        "",
    ]
    return "\n".join(lines)


def expected_outputs(root: Path = ROOT) -> dict[Path, str]:
    rows = load_all_rows(root)
    output_rows = build_source_output_rows(rows)
    return {
        root / "amsn-core" / "results" / OUTPUT.name: render_csv(output_rows),
        root / "amsn-core" / "research" / REPORT.name: render_report(rows, output_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the diagnostics report and CSV")
    mode.add_argument("--check", action="store_true", help="check generated outputs")
    args = parser.parse_args()
    outputs = expected_outputs(ROOT)
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"WROTE {path.relative_to(ROOT)}")
        return 0
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if stale:
        raise SystemExit("Diagnostics are missing or stale: " + ", ".join(stale))
    print(f"OK: {len(outputs)} outputs match all four validated paired datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
