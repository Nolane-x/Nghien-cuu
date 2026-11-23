#!/usr/bin/env python3
"""Validate the Jacobs control PRIMA matrix and archive endpoint summaries."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[1]
RESULTS = ROOT / "results"
PREFLIGHT = ROOT / "results" / "NMO_03524_JacobsControl_holdout" / "preflight.json"
STEM = "NMO_03524_JacobsControl_human_prima_shift_order_pareto_2026-11-23"
EXPECTED = {"models": 81, "frequency": 729, "transient": 3402}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_values(rows: list[dict], key: str) -> list[float]:
    values = [float(row[key]) for row in rows]
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"non-finite values in {key}")
    return values


def main() -> None:
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if preflight.get("status") != "PASS":
        raise RuntimeError("Jacobs control SWC preflight did not pass")
    if preflight["source"]["neuromorpho_id"] != "NMO_03524":
        raise RuntimeError("unexpected morphology in preflight manifest")
    models = read_csv(RESULTS / f"{STEM}_models.csv")
    frequency = read_csv(RESULTS / f"{STEM}_frequency.csv")
    transient = read_csv(RESULTS / f"{STEM}_transient.csv")
    actual = {"models":len(models),"frequency":len(frequency),"transient":len(transient)}
    if actual != EXPECTED:
        raise RuntimeError(f"exact matrix coverage mismatch: {actual} != {EXPECTED}")
    candidate_ids = sorted({row["model_id"] for row in models})
    if len(candidate_ids) != 9:
        raise RuntimeError(f"expected nine distinct candidates, got {candidate_ids}")
    if {row["passivity_check"] for row in models} != {"cholesky_passed"}:
        raise RuntimeError("one or more candidate models failed passivity checks")
    if not all(int(row["basis_order_requested"]) == int(row["basis_order_actual"]) for row in models):
        raise RuntimeError("one or more candidates did not achieve requested basis order")

    summary = []
    for candidate in candidate_ids:
        mrows = [row for row in models if row["model_id"] == candidate]
        frows = [row for row in frequency if row["model_id"] == candidate]
        trows = [row for row in transient if row["model_id"] == candidate]
        freq10 = [row for row in frows if float(row["frequency_hz"]) == 10000.0]
        if len(mrows) != 9 or len(frows) != 81 or len(trows) != 378 or len(freq10) != 9:
            raise RuntimeError(
                f"incomplete candidate coverage for {candidate}: "
                f"models={len(mrows)}, frequency={len(frows)}, transient={len(trows)}, 10kHz={len(freq10)}"
            )
        summary.append({
            "model_id": candidate,
            "basis_order": int(mrows[0]["basis_order_actual"]),
            "shift_strategy": mrows[0]["shift_strategy"],
            "parameter_scenario_rows": len(mrows),
            "frequency_rows": len(frows),
            "transient_port_rows": len(trows),
            "median_z_error_10khz_pct": float(np.median(finite_values(freq10,"z_error_vs_hines_pct"))),
            "max_z_error_10khz_pct": max(finite_values(freq10,"z_error_vs_hines_pct")),
            "median_y_error_10khz_pct": float(np.median(finite_values(freq10,"y_error_vs_hines_pct"))),
            "max_y_error_10khz_pct": max(finite_values(freq10,"y_error_vs_hines_pct")),
            "median_transient_port_nrmse_pct": float(np.median(finite_values(trows,"port_nrmse_pct"))),
            "max_transient_port_nrmse_pct": max(finite_values(trows,"port_nrmse_pct")),
            "median_numeric_storage_mb": float(np.median(finite_values(mrows,"numeric_storage_bytes"))) / (1024.0*1024.0),
            "median_basis_build_seconds": float(np.median(finite_values(mrows,"basis_build_wall_seconds"))),
        })

    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / f"{STEM}_summary.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    result = {
        "status":"jacobs_control_prima_shift_order_replay_passed",
        "morphology":preflight["source"],
        "preflight": {
            "swc_records":preflight["swc"]["record_count"],
            "neurite_type_counts":preflight["swc"]["type_counts"],
            "electrical_compartments":preflight["amsn"]["electrical_compartment_count"],
            "unique_port_count":len(preflight["amsn"]["seven_unique_port_node_ids"]),
            "neuron_version":preflight["neuron"]["version"],
        },
        "protocol": {
            "orders":[56,84,112],
            "shift_sets":{
                "narrow_3khz":[0,100,1000,3000],
                "extended_10khz":[0,100,1000,3000,6000,10000],
                "balanced_10khz":[0,10,100,1000,3000,10000],
            },
            "parameter_scenarios":9,
            "frequencies_hz":[0.1,1,10,100,300,1000,3000,6000,10000],
            "source_ports":["soma","basal_q75","apical_q75"],
            "pulse_widths_ms":[2,10],
            "pulse_amplitude_pA":10,
            "pulse_onset_ms":2,
            "duration_ms":20,
            "dt_ms":0.1,
        },
        "exact_coverage":actual,
        "candidate_summary":summary,
        "scientific_limits":[
            "One human control morphology from the Jacobs archive; not a representative human population.",
            "NeuroMorpho describes dendrites as moderate and axon as incomplete.",
            "Passive linear-RC comparison against full Hines only; no active-channel or nonlinear-synapse validation.",
            "This is a seven-port shift/order sweep; it does not independently test the nine-port q25 decision on this control morphology.",
            "No production default, solver method or runtime behavior is promoted.",
        ],
    }
    (RESULTS / f"{STEM}_report.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "status":result["status"],
        "exact_coverage":actual,
        "source_sha256":preflight["source"]["source_sha256"],
        "source_bytes":preflight["source"]["source_bytes"],
        "candidate_summary":summary,
        "report":str(RESULTS/f"{STEM}_report.json"),
    },indent=2))


if __name__=="__main__":
    main()
