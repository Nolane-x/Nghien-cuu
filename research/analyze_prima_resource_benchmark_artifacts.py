#!/usr/bin/env python3
"""Validate and summarize the 36 AMSN PRIMA benchmark ZIPs using Python's standard library."""
import argparse
import collections
import csv
import hashlib
import json
import re
import statistics
import zipfile
from pathlib import Path

METRICS = {"frequency_response": 30, "transient_port": 162, "transient_all_ports": 18}
TOTALS = {"frequency_response": 1080, "transient_port": 5832, "transient_all_ports": 648}


def csv_rows(data):
    return list(csv.DictReader(data.decode("utf-8-sig").splitlines()))


def median(rows, key):
    return statistics.median(float(row[key]) for row in rows)


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory containing downloaded artifact ZIPs")
    parser.add_argument("--manifest", type=Path, required=True, help="CSV with artifact_id, artifact_name, sha256_expected")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    expected = {}
    with args.manifest.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            name = row["artifact_name"]
            if name in expected:
                raise ValueError(f"duplicate artifact: {name}")
            expected[name] = (row["artifact_id"], row["sha256_expected"].removeprefix("sha256:"))
    if len(expected) != 36:
        raise ValueError(f"expected 36 manifest entries, got {len(expected)}")

    runs, digest_rows, errors = [], [], []
    totals, conditions = collections.Counter(), set()
    for name, (artifact_id, expected_hash) in sorted(expected.items()):
        archive = args.input_dir / f"{name}.zip"
        if not archive.is_file():
            errors.append(f"missing ZIP: {archive.name}")
            continue
        actual_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
        matched = actual_hash == expected_hash
        digest_rows.append({"artifact_id": artifact_id, "artifact_name": name, "sha256_expected": expected_hash,
                            "sha256_downloaded": actual_hash, "sha256_match": str(matched).lower(), "zip_bytes": archive.stat().st_size})
        if not matched:
            errors.append(f"SHA-256 mismatch: {name}")

        with zipfile.ZipFile(archive) as zipped:
            names = zipped.namelist()
            def read(suffix):
                match = next((item for item in names if item.endswith(suffix)), None)
                if match is None:
                    raise ValueError(f"{name}: missing {suffix}")
                return csv_rows(zipped.read(match))
            resource = read("resource_benchmark.csv")
            environment = read("benchmark_environment.csv")
            sweep_files = [item for item in names if item.startswith("results/") and item.endswith(".csv")]
            if len(sweep_files) != 1:
                raise ValueError(f"{name}: expected one result sweep CSV")
            sweep = csv_rows(zipped.read(sweep_files[0]))
        if len(resource) != 1 or len(environment) != 1:
            errors.append(f"{name}: expected one resource and one environment row")
            continue
        data = resource[0]
        match = re.search(r"order-(\d+)-rep-(\d+)", name)
        if not match:
            errors.append(f"{name}: cannot parse selected order and replicate")
            continue
        order, replicate = int(match.group(1)), int(match.group(2))
        if int(data["actual_order"]) != order or int(data["replicate"]) != replicate or int(data["exit_status"]) != 0:
            errors.append(f"{name}: wrong achieved order, replicate, or exit status")
        if int(data["candidate_order"].split(",")[-1]) != order:
            errors.append(f"{name}: requested order mismatch")
        metrics = collections.Counter(row.get("metric", "") for row in sweep)
        if len(sweep) != 210 or dict(metrics) != METRICS:
            errors.append(f"{name}: sweep metric coverage mismatch")
        model_ids = {row.get("model_id") for row in sweep}
        expected_models = {"four_shift_order56_control", "six_shift_order56", f"six_shift_order{order}"}
        if model_ids != expected_models:
            errors.append(f"{name}: model IDs do not match expected controls/candidate")
        achieved = {int(row["prima_order"]) for row in sweep if row.get("metric") == "frequency_response" and row.get("model_id") == f"six_shift_order{order}"}
        if achieved != {order}:
            errors.append(f"{name}: frequency rows do not confirm achieved order")
        morphology, mesh = data["morphology"], float(data["mesh_max_segment_um"])
        condition = (morphology, mesh, order, replicate)
        if condition in conditions:
            errors.append(f"duplicate matrix condition: {condition}")
        conditions.add(condition)
        totals.update(metrics)
        runs.append({"artifact_id": artifact_id, "artifact_name": name, "sha256_match": str(matched).lower(),
            "morphology": morphology, "mesh_max_segment_um": mesh, "requested_orders": data["candidate_order"],
            "candidate_order": order, "actual_order": int(data["actual_order"]), "replicate": replicate,
            "cpu_model": data["cpu_model"], "python_version": data["python_version"],
            "logical_cpu_count": int(data["logical_cpu_count"]), "full_compartment_order": int(data["full_compartment_order"]),
            "state_reduction_pct": float(data["state_reduction_pct"]), "elapsed_wall_seconds": float(data["elapsed_wall_seconds"]),
            "user_cpu_seconds": float(data["user_cpu_seconds"]), "system_cpu_seconds": float(data["system_cpu_seconds"]),
            "max_rss_kb": int(data["max_rss_kb"]), "max_rss_mib": float(data["max_rss_mb"]),
            "exit_status": int(data["exit_status"]), "frequency_rows": int(data["frequency_rows"]),
            "transient_port_rows": int(data["transient_port_rows"]), "transient_all_ports_rows": int(data["transient_all_ports_rows"]),
            "sweep_csv_rows": len(sweep)})

    if len(runs) != 36 or len(conditions) != 36:
        errors.append(f"incomplete matrix: {len(runs)} rows / {len(conditions)} unique conditions")
    if dict(totals) != TOTALS:
        errors.append(f"aggregate sweep counts mismatch: {dict(totals)}")
    if len(digest_rows) != 36 or sum(row["sha256_match"] == "true" for row in digest_rows) != 36:
        errors.append("not all 36 artifact hashes verified")

    by_order = []
    for order in (84, 112, 168):
        group = [row for row in runs if row["candidate_order"] == order]
        by_order.append({"candidate_order": order, "n_runs": len(group),
            "wall_median_seconds": median(group, "elapsed_wall_seconds"),
            "wall_min_seconds": min(row["elapsed_wall_seconds"] for row in group),
            "wall_max_seconds": max(row["elapsed_wall_seconds"] for row in group),
            "user_cpu_median_seconds": median(group, "user_cpu_seconds"),
            "user_cpu_min_seconds": min(row["user_cpu_seconds"] for row in group),
            "user_cpu_max_seconds": max(row["user_cpu_seconds"] for row in group),
            "peak_rss_median_mib": median(group, "max_rss_mib"),
            "peak_rss_min_mib": min(row["max_rss_mib"] for row in group),
            "peak_rss_max_mib": max(row["max_rss_mib"] for row in group),
            "state_reduction_median_pct": median(group, "state_reduction_pct"),
            "morphologies": ";".join(sorted({row["morphology"] for row in group})),
            "cpu_models": ";".join(sorted({row["cpu_model"] for row in group}))})

    def grouped_summary(keys):
        result = []
        for values in sorted({tuple(row[key] for key in keys) for row in runs}):
            group = [row for row in runs if tuple(row[key] for key in keys) == values]
            item = dict(zip(keys, values)); item["n_runs"] = len(group)
            for source, target in (("elapsed_wall_seconds", "wall_median_seconds"), ("user_cpu_seconds", "user_cpu_median_seconds"),
                                   ("max_rss_mib", "peak_rss_median_mib"), ("state_reduction_pct", "state_reduction_median_pct")):
                item[target] = median(group, source)
            result.append(item)
        return result

    by_mesh = grouped_summary(["mesh_max_segment_um", "candidate_order"])
    by_morphology = grouped_summary(["morphology", "mesh_max_segment_um", "candidate_order"])
    validation = {"workflow_run": "45016243390", "validated_artifacts": len(digest_rows),
        "sha256_matches": sum(row["sha256_match"] == "true" for row in digest_rows), "unique_conditions": len(conditions),
        "raw_sweep_rows": sum(totals.values()), "metric_rows": dict(totals), "errors": errors,
        "python_versions": dict(collections.Counter(row["python_version"] for row in runs)),
        "cpu_models": dict(collections.Counter(row["cpu_model"] for row in runs)),
        "by_order": by_order, "by_mesh": by_mesh, "by_morphology": by_morphology}
    write_csv(args.output_dir / "prima_resource_benchmark_36_runs_2026-11-22.csv", runs)
    write_csv(args.output_dir / "prima_resource_benchmark_by_order_2026-11-22.csv", by_order)
    write_csv(args.output_dir / "prima_resource_benchmark_by_mesh_2026-11-22.csv", by_mesh)
    write_csv(args.output_dir / "prima_resource_benchmark_by_morphology_2026-11-22.csv", by_morphology)
    write_csv(args.output_dir / "prima_resource_benchmark_artifact_manifest_2026-11-22.csv", digest_rows)
    (args.output_dir / "prima_resource_benchmark_validation_2026-11-22.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("validated_artifacts", "sha256_matches", "unique_conditions", "raw_sweep_rows", "metric_rows", "errors", "by_order")}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
