"""Strict coverage checks for the high-order PRIMA resource benchmark."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

EXPECTED_PER_MODEL_METRIC_COUNTS = {
    "frequency_response": 10,
    "transient_port": 54,
    "transient_all_ports": 6,
}


def parse_prima_order_list(raw: str) -> tuple[int, ...]:
    """Parse the comma-separated PRIMA orders used by the benchmark matrix."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("PRIMA order list must be a non-empty comma-separated string")
    tokens = [token.strip() for token in raw.split(",")]
    if any(not token for token in tokens):
        raise ValueError(f"PRIMA order list contains an empty item: {raw!r}")
    try:
        orders = tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise ValueError(f"PRIMA order list contains a non-integer item: {raw!r}") from exc
    if any(order <= 0 for order in orders):
        raise ValueError(f"PRIMA orders must be positive: {orders!r}")
    if len(set(orders)) != len(orders):
        raise ValueError(f"PRIMA order list contains duplicates: {orders!r}")
    if orders[0] != 56:
        raise ValueError(f"PRIMA resource matrix must start with order 56, got {orders!r}")
    if tuple(sorted(orders)) != orders:
        raise ValueError(f"PRIMA order list must be strictly increasing: {orders!r}")
    if len(orders) < 2:
        raise ValueError("PRIMA resource matrix must include a control order and a candidate order")
    return orders


def validate_prima_resource_sweep(
    rows: Iterable[Mapping[str, str]], requested_orders: Iterable[int]
) -> dict[str, object]:
    """Validate exact model/metric coverage and the realized candidate rank.

    The sweep contains one four-shift order-56 control plus one six-shift model
    for every requested order. The final requested order is the resource
    candidate summarized in the per-job resource CSV.
    """
    orders = tuple(int(order) for order in requested_orders)
    if len(orders) < 2 or orders[0] != 56:
        raise ValueError(f"expected an order-56 control followed by candidate orders, got {orders!r}")
    if len(set(orders)) != len(orders) or tuple(sorted(orders)) != orders:
        raise ValueError(f"requested PRIMA orders must be unique and increasing: {orders!r}")
    materialized = list(rows)
    if not materialized:
        raise ValueError("resource sweep CSV is empty")

    expected_models = {"four_shift_order56_control"}
    expected_models.update(f"six_shift_order{order}" for order in orders)
    expected_total_counts = {
        metric: count * len(expected_models)
        for metric, count in EXPECTED_PER_MODEL_METRIC_COUNTS.items()
    }
    metric_counts = Counter(row.get("metric", "") for row in materialized)
    if dict(metric_counts) != expected_total_counts:
        raise ValueError(
            "coverage mismatch: "
            f"rows={len(materialized)} counts={dict(metric_counts)} "
            f"expected={expected_total_counts}"
        )

    observed_models = {row.get("model_id", "") for row in materialized}
    if observed_models != expected_models:
        raise ValueError(
            "model identity coverage mismatch: "
            f"observed={sorted(observed_models)} expected={sorted(expected_models)}"
        )

    for model_id in sorted(expected_models):
        model_counts = Counter(
            row.get("metric", "") for row in materialized if row.get("model_id") == model_id
        )
        if dict(model_counts) != EXPECTED_PER_MODEL_METRIC_COUNTS:
            raise ValueError(
                f"{model_id} metric coverage mismatch: "
                f"observed={dict(model_counts)} expected={EXPECTED_PER_MODEL_METRIC_COUNTS}"
            )

    for order in orders:
        model_id = f"six_shift_order{order}"
        frequency_rows = [
            row for row in materialized
            if row.get("metric") == "frequency_response" and row.get("model_id") == model_id
        ]
        try:
            ranks = {int(row["prima_order"]) for row in frequency_rows}
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{model_id} has a missing or invalid realized PRIMA order") from exc
        if ranks != {order}:
            raise ValueError(f"{model_id} requested order {order} did not produce exact rank: {ranks}")

    candidate_order = orders[-1]
    candidate_model_id = f"six_shift_order{candidate_order}"
    candidate_rows = [
        row for row in materialized
        if row.get("metric") == "frequency_response" and row.get("model_id") == candidate_model_id
    ]
    return {
        "counts": dict(metric_counts),
        "candidate_order": candidate_order,
        "candidate_model_id": candidate_model_id,
        "candidate_rows": candidate_rows,
        "candidate_ranks": {candidate_order},
        "model_ids": expected_models,
    }
