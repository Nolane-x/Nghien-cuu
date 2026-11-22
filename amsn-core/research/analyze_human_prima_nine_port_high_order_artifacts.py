#!/usr/bin/env python3
"""Validate and compare the six-config nine-port high-order PRIMA sweep.

Extract the six high-order, nine-port and seven-port GitHub Actions artifacts
into separate directories, then run this script. Python standard library only.
"""
from __future__ import annotations
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

SWEEP = "human_passive_prima_extended_order_transient_sweep_2026-11-22.csv"
HIGH_MODELS = (
    "four_shift_order56_control", "six_shift_order28", "six_shift_order56",
    "six_shift_order84", "six_shift_order112", "six_shift_order168",
)
BASE_MODELS = (
    "four_shift_order56_control", "six_shift_order28",
    "six_shift_order56", "six_shift_order84",
)
EXPECTED_HIGH = {"frequency_response": 60, "transient_port": 324, "transient_all_ports": 36}
EXPECTED_NINE = {"frequency_response": 40, "transient_port": 216, "transient_all_ports": 24}
EXPECTED_SEVEN = {"frequency_response": 40, "transient_port": 168, "transient_all_ports": 24}
SCENARIOS = (
    "soma_pulse2ms", "basal_q75_pulse2ms", "apical_q75_pulse2ms",
    "soma_pulse10ms", "basal_q75_pulse10ms", "apical_q75_pulse10ms",
)

def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def num(row, key):
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}: {row}")
    return value

def six_files(root: Path, pattern: str):
    files = sorted(root.glob("**/" + pattern))
    if len(files) != 6:
        raise ValueError(f"expected exactly six files matching {pattern} under {root}, found {len(files)}")
    return files

def metadata(rows):
    frequency_rows = [row for row in rows if row["metric"] == "frequency_response"]
    morphologies = {row["morphology_label"] for row in frequency_rows}
    meshes = {num(row, "neuron_max_segment_um") for row in frequency_rows}
    compartments = {int(row["full_compartment_order"]) for row in frequency_rows}
    if len(morphologies) != 1 or len(meshes) != 1 or len(compartments) != 1:
        raise ValueError("mixed morphology/mesh/compartment metadata in one artifact")
    return next(iter(morphologies)), next(iter(meshes)), next(iter(compartments))

def collect(root: Path, kind: str):
    if kind == "high":
        pattern = "*_highorder_9port_" + SWEEP
        expected = EXPECTED_HIGH
        models = set(HIGH_MODELS)
        expected_ports = {"soma", "basal_q25", "basal_q50", "basal_q75", "basal_q90",
                          "apical_q25", "apical_q50", "apical_q75", "apical_q90"}
    elif kind == "nine":
        pattern = "*_9port_" + SWEEP
        expected = EXPECTED_NINE
        models = set(BASE_MODELS)
        expected_ports = {"soma", "basal_q25", "basal_q50", "basal_q75", "basal_q90",
                          "apical_q25", "apical_q50", "apical_q75", "apical_q90"}
    else:
        pattern = "*" + SWEEP
        expected = EXPECTED_SEVEN
        models = set(BASE_MODELS)
        expected_ports = {"soma", "basal_q50", "basal_q75", "basal_q90",
                          "apical_q50", "apical_q75", "apical_q90"}

    output = {}
    for path in six_files(root, pattern):
        rows = read_csv(path)
        counts = defaultdict(int)
        for row in rows:
            counts[row["metric"]] += 1
        if dict(counts) != expected:
            raise ValueError(f"incorrect row coverage in {path}: {dict(counts)} != {expected}")
        morphology, mesh, compartments = metadata(rows)
        config = (morphology, mesh)
        if config in output:
            raise ValueError(f"duplicate morphology/mesh config {config}")
        frequency_rows = [row for row in rows if row["metric"] == "frequency_response"]
        port_rows = [row for row in rows if row["metric"] == "transient_port"]
        all_rows = [row for row in rows if row["metric"] == "transient_all_ports"]
        if {row["model_id"] for row in frequency_rows} != models:
            raise ValueError(f"wrong model set in {path}")
        model_data = {}
        expected_port_rows = 54 if kind in ("high", "nine") else 42
        for model in models:
            fr = [row for row in frequency_rows if row["model_id"] == model]
            ports = [row for row in port_rows if row["model_id"] == model]
            alls = [row for row in all_rows if row["model_id"] == model]
            if len(fr) != 10 or len(ports) != expected_port_rows or len(alls) != 6:
                raise ValueError(f"incomplete {config}/{model} frequency/transient coverage")
            ranks = {int(row["prima_order"]) for row in fr}
            if len(ranks) != 1:
                raise ValueError(f"actual basis rank varies by frequency: {config}/{model}/{ranks}")
            if {row["scenario_id"] for row in ports} != set(SCENARIOS):
                raise ValueError(f"wrong transient scenario set in {path}/{model}")
            by_port = defaultdict(list)
            for row in ports:
                roles = row["port_roles"].split(";")
                probe = next((part.split(":", 1)[1] for part in roles if part.startswith("probe:")), None)
                source = next((part.split(":", 1)[1] for part in roles if part.startswith("source:")), None)
                name = probe or source
                if name is None:
                    raise ValueError(f"port row has no source/probe role: {row}")
                by_port[name].append(row)
            if set(by_port) != expected_ports or any(len(values) != 6 for values in by_port.values()):
                raise ValueError(f"port/scenario coverage mismatch: {config}/{model}/{set(by_port)}")
            worst = max(ports, key=lambda row: num(row, "transient_port_nrmse_pct"))
            model_data[model] = {
                "actual_order": next(iter(ranks)),
                "state_reduction_pct": num(fr[0], "state_count_reduction_pct"),
                "max_Z_vs_NEURON_pct": max(num(row, "impedance_vs_neuron_pct") for row in fr),
                "max_Y_vs_NEURON_pct": max(num(row, "admittance_vs_neuron_pct") for row in fr),
                "max_Z_vs_Hines_pct": max(num(row, "impedance_vs_hines_pct") for row in fr),
                "max_Y_vs_Hines_pct": max(num(row, "admittance_vs_hines_pct") for row in fr),
                "max_all_port_NRMSE_pct": max(num(row, "transient_port_nrmse_pct") for row in alls),
                "max_single_port_NRMSE_pct": num(worst, "transient_port_nrmse_pct"),
                "worst_port": worst["port_roles"],
                "worst_scenario": worst["scenario_id"],
                "max_apical_q90_NRMSE_pct": max(num(row, "transient_port_nrmse_pct") for row in by_port["apical_q90"]),
                "ports": by_port,
            }
        output[config] = {"full_order": compartments, "models": model_data}
    if len(output) != 6:
        raise ValueError(f"expected six morphology/mesh configs, found {len(output)}")
    return output

def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--high-root", type=Path, required=True)
    parser.add_argument("--nine-root", type=Path, required=True)
    parser.add_argument("--seven-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    high = collect(args.high_root, "high")
    nine = collect(args.nine_root, "nine")
    seven = collect(args.seven_root, "seven")
    if set(high) != set(nine) or set(high) != set(seven):
        raise ValueError("morphology/mesh coverage differs across high/nine/seven-port runs")

    config_rows = []
    q90_pairs = []
    shared_pairs = []
    shared_probe_names = (
        "soma", "basal_q50", "basal_q75", "basal_q90",
        "apical_q50", "apical_q75", "apical_q90",
    )
    for config, data in sorted(high.items()):
        morphology, mesh = config
        for model, metrics in data["models"].items():
            config_rows.append({
                "morphology_label": morphology,
                "mesh_max_segment_um": mesh,
                "model_id": model,
                "full_compartment_order": data["full_order"],
                **{key: value for key, value in metrics.items() if key != "ports"},
            })
        for model in ("six_shift_order112", "six_shift_order168"):
            for scenario in SCENARIOS:
                def trace(dataset, model_id, port):
                    matches = [row for row in dataset[config]["models"][model_id]["ports"][port]
                               if row["scenario_id"] == scenario]
                    if len(matches) != 1:
                        raise ValueError(f"expected one matched trace: {config}/{model_id}/{port}/{scenario}")
                    return num(matches[0], "transient_port_nrmse_pct")
                new = trace(high, model, "apical_q90")
                nine84 = trace(nine, "six_shift_order84", "apical_q90")
                seven84 = trace(seven, "six_shift_order84", "apical_q90")
                if nine84 <= 0 or seven84 <= 0:
                    raise ValueError("zero reference transient norm; ratio undefined")
                q90_pairs.append({
                    "morphology_label": morphology,
                    "mesh_max_segment_um": mesh,
                    "model_id": model,
                    "scenario_id": scenario,
                    "new_q90_NRMSE_pct": new,
                    "nine_port_order84_q90_NRMSE_pct": nine84,
                    "seven_port_order84_q90_NRMSE_pct": seven84,
                    "ratio_vs_nine84": new / nine84,
                    "ratio_vs_seven84": new / seven84,
                })
            for port in shared_probe_names:
                for scenario in SCENARIOS:
                    new = trace(high, model, port)
                    reference = trace(seven, "six_shift_order84", port)
                    if reference <= 0:
                        raise ValueError("zero seven-port reference transient norm")
                    shared_pairs.append({
                        "morphology_label": morphology,
                        "mesh_max_segment_um": mesh,
                        "model_id": model,
                        "probe": port,
                        "scenario_id": scenario,
                        "high_order_NRMSE_pct": new,
                        "seven_port_order84_NRMSE_pct": reference,
                        "ratio_new_over_seven84": new / reference,
                    })

    q90_summary = []
    shared_summary = []
    shared_by_probe = []
    for model in ("six_shift_order112", "six_shift_order168"):
        subset = [row for row in q90_pairs if row["model_id"] == model]
        for key in ("ratio_vs_nine84", "ratio_vs_seven84"):
            ratios = [row[key] for row in subset]
            q90_summary.append({
                "model_id": model,
                "comparison": key,
                "pairs": len(ratios),
                "worse_pairs": sum(value > 1 for value in ratios),
                "median_ratio": median(ratios),
                "max_ratio": max(ratios),
            })
        subset = [row for row in shared_pairs if row["model_id"] == model]
        ratios = [row["ratio_new_over_seven84"] for row in subset]
        shared_summary.append({
            "model_id": model,
            "pairs": len(ratios),
            "worse_pairs_vs_seven84": sum(value > 1 for value in ratios),
            "median_ratio": median(ratios),
            "max_ratio": max(ratios),
        })
        for port in shared_probe_names:
            values = [row["ratio_new_over_seven84"] for row in subset if row["probe"] == port]
            shared_by_probe.append({
                "model_id": model,
                "probe": port,
                "matched_pairs": len(values),
                "worse_pairs_vs_seven84": sum(value > 1 for value in values),
                "median_ratio": median(values),
                "max_ratio": max(values),
            })

    aggregate = []
    for model in HIGH_MODELS:
        group = [row for row in config_rows if row["model_id"] == model]
        aggregate.append({
            "model_id": model,
            "actual_order_min": min(row["actual_order"] for row in group),
            "actual_order_max": max(row["actual_order"] for row in group),
            "state_reduction_min_pct": min(row["state_reduction_pct"] for row in group),
            "state_reduction_max_pct": max(row["state_reduction_pct"] for row in group),
            "max_Z_vs_NEURON_pct": max(row["max_Z_vs_NEURON_pct"] for row in group),
            "max_Y_vs_NEURON_pct": max(row["max_Y_vs_NEURON_pct"] for row in group),
            "max_Z_vs_Hines_pct": max(row["max_Z_vs_Hines_pct"] for row in group),
            "max_Y_vs_Hines_pct": max(row["max_Y_vs_Hines_pct"] for row in group),
            "max_all_port_NRMSE_pct": max(row["max_all_port_NRMSE_pct"] for row in group),
            "max_single_port_NRMSE_pct": max(row["max_single_port_NRMSE_pct"] for row in group),
            "max_apical_q90_NRMSE_pct": max(row["max_apical_q90_NRMSE_pct"] for row in group),
        })

    write_csv(args.out / "high_order_nine_port_model_summary.csv", aggregate)
    write_csv(args.out / "high_order_nine_port_config_model_summary.csv", config_rows)
    write_csv(args.out / "high_order_apical_q90_pairs.csv", q90_pairs)
    write_csv(args.out / "high_order_apical_q90_pair_summary.csv", q90_summary)
    write_csv(args.out / "high_order_shared_port_pairs.csv", shared_pairs)
    write_csv(args.out / "high_order_shared_port_summary.csv", shared_summary)
    write_csv(args.out / "high_order_shared_port_by_probe_summary.csv", shared_by_probe)
    print(
        f"configs={len(high)}; high_order_rows={sum(len(x['models']) * 420 for x in high.values())}; "
        f"q90_pairs={len(q90_pairs)}; shared_port_pairs={len(shared_pairs)}"
    )
    for row in q90_summary:
        print(row)
    for row in shared_summary:
        print(row)

if __name__ == "__main__":
    main()
