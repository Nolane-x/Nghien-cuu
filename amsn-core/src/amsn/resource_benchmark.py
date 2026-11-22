"""Validation helpers for reproducible PRIMA resource benchmark artifacts."""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import math

EXPECTED_FREQUENCY_ROWS_PER_MODEL = 10
EXPECTED_TRANSIENT_SCENARIOS = 6
CONTROL_MODEL_ID = "four_shift_order56_control"


def parse_prima_orders(value: str) -> tuple[int, ...]:
    """Parse a comma-separated list of unique positive PRIMA orders."""
    if not value.strip():
        raise ValueError("at least one PRIMA order is required")
    parts = value.split(",")
    if any(not part.strip() for part in parts):
        raise ValueError(f"empty item in PRIMA order list: {value!r}")
    try:
        orders = tuple(int(part.strip()) for part in parts)
    except ValueError as exc:
        raise ValueError(f"invalid PRIMA order list: {value!r}") from exc
    if any(order <= 0 for order in orders):
        raise ValueError("PRIMA orders must be positive integers")
    if len(set(orders)) != len(orders):
        raise ValueError(f"duplicate PRIMA orders are not allowed: {orders}")
    return orders


def validate_resource_sweep_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    extended_orders: Sequence[int],
    candidate_order: int,
    expected_ports: int = 9,
) -> dict[str, int | float | tuple[str, ...]]:
    """Validate exact model, metric, frequency, port and achieved-rank coverage."""
    orders = tuple(int(order) for order in extended_orders)
    if not orders or any(order <= 0 for order in orders):
        raise ValueError("extended_orders must contain positive integers")
    if len(set(orders)) != len(orders):
        raise ValueError(f"duplicate extended PRIMA orders are not allowed: {orders}")
    if candidate_order not in orders:
        raise ValueError(
            f"candidate order {candidate_order} is not in extended order list {orders}"
        )
    if expected_ports <= 0:
        raise ValueError("expected_ports must be positive")
    if not rows:
        raise ValueError("the PRIMA sweep CSV is empty")

    expected_models = {CONTROL_MODEL_ID} | {f"six_shift_order{order}" for order in orders}
    observed_models = {row.get("model_id", "") for row in rows}
    if observed_models != expected_models:
        raise ValueError(
            "model identity coverage mismatch: "
            f"observed={sorted(observed_models)}, expected={sorted(expected_models)}"
        )

    per_model_metrics = {
        "frequency_response": EXPECTED_FREQUENCY_ROWS_PER_MODEL,
        "transient_port": EXPECTED_TRANSIENT_SCENARIOS * expected_ports,
        "transient_all_ports": EXPECTED_TRANSIENT_SCENARIOS,
    }
    expected_ranks = {CONTROL_MODEL_ID: 56} | {
        f"six_shift_order{order}": order for order in orders
    }
    total_counts: Counter[str] = Counter()
    for model_id in sorted(expected_models):
        model_rows = [row for row in rows if row.get("model_id") == model_id]
        metric_counts = Counter(row.get("metric", "") for row in model_rows)
        if metric_counts != Counter(per_model_metrics):
            raise ValueError(
                f"metric coverage mismatch for {model_id}: "
                f"observed={dict(metric_counts)}, expected={per_model_metrics}"
            )
        total_counts.update(metric_counts)

        frequency_rows = [
            row for row in model_rows if row.get("metric") == "frequency_response"
        ]
        rank = expected_ranks[model_id]
        observed_actual_ranks = {int(row["prima_order"]) for row in frequency_rows}
        observed_requested_ranks = {int(row["requested_order"]) for row in frequency_rows}
        if observed_actual_ranks != {rank} or observed_requested_ranks != {rank}:
            raise ValueError(
                f"rank mismatch for {model_id}: actual={observed_actual_ranks}, "
                f"requested={observed_requested_ranks}, expected={rank}"
            )
        frequencies = {float(row["frequency_hz"]) for row in frequency_rows}
        if len(frequencies) != EXPECTED_FREQUENCY_ROWS_PER_MODEL:
            raise ValueError(
                f"frequency coverage mismatch for {model_id}: "
                f"found {len(frequencies)} unique frequencies"
            )

        transient_port_rows = [
            row for row in model_rows if row.get("metric") == "transient_port"
        ]
        scenario_ids = {row.get("scenario_id", "") for row in transient_port_rows}
        if len(scenario_ids) != EXPECTED_TRANSIENT_SCENARIOS or "" in scenario_ids:
            raise ValueError(
                f"transient scenario coverage mismatch for {model_id}: {scenario_ids}"
            )
        port_pairs = {
            (row.get("scenario_id", ""), row.get("port_swc_id", ""))
            for row in transient_port_rows
        }
        ports_per_scenario = Counter(
            row.get("scenario_id", "") for row in transient_port_rows
        )
        if any(count != expected_ports for count in ports_per_scenario.values()):
            raise ValueError(
                f"per-scenario port count mismatch for {model_id}: "
                f"{dict(ports_per_scenario)}; expected {expected_ports} each"
            )
        if len(port_pairs) != EXPECTED_TRANSIENT_SCENARIOS * expected_ports:
            raise ValueError(
                f"duplicate or missing scenario/port records for {model_id}: "
                f"{len(port_pairs)} unique pairs"
            )
        if any(not port_id for _, port_id in port_pairs):
            raise ValueError(f"empty SWC port ID in transient coverage for {model_id}")

        aggregate_scenarios = {
            row.get("scenario_id", "")
            for row in model_rows
            if row.get("metric") == "transient_all_ports"
        }
        if aggregate_scenarios != scenario_ids:
            raise ValueError(
                f"all-port aggregate scenarios do not match port traces for {model_id}"
            )

    candidate_id = f"six_shift_order{candidate_order}"
    candidate_rows = [
        row for row in rows
        if row.get("model_id") == candidate_id and row.get("metric") == "frequency_response"
    ]
    full_orders = {int(row["full_compartment_order"]) for row in candidate_rows}
    reductions = {float(row["state_count_reduction_pct"]) for row in candidate_rows}
    if len(full_orders) != 1 or len(reductions) != 1:
        raise ValueError("candidate metadata changes across frequency rows")
    reduction = next(iter(reductions))
    if not math.isfinite(reduction) or not 0.0 <= reduction <= 100.0:
        raise ValueError(f"invalid state reduction percentage: {reduction}")

    return {
        "models": tuple(sorted(expected_models)),
        "frequency_rows": total_counts["frequency_response"],
        "transient_port_rows": total_counts["transient_port"],
        "transient_all_ports_rows": total_counts["transient_all_ports"],
        "total_rows": len(rows),
        "actual_order": candidate_order,
        "full_compartment_order": next(iter(full_orders)),
        "state_count_reduction_pct": reduction,
    }
