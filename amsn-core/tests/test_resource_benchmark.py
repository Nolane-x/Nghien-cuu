import pytest

from amsn.resource_benchmark import parse_prima_orders, validate_resource_sweep_rows


def _rows(orders=(56, 84), ports=9):
    models = [("four_shift_order56_control", 56)] + [
        (f"six_shift_order{order}", order) for order in orders
    ]
    rows = []
    for model_id, order in models:
        for index in range(10):
            rows.append({
                "model_id": model_id,
                "metric": "frequency_response",
                "prima_order": str(order),
                "requested_order": str(order),
                "frequency_hz": str(10 ** (index / 2)),
                "full_compartment_order": "12399",
                "state_count_reduction_pct": "99.5",
            })
        for scenario in range(6):
            for port in range(ports):
                rows.append({
                    "model_id": model_id,
                    "metric": "transient_port",
                    "scenario_id": f"scenario-{scenario}",
                    "port_swc_id": f"node-{port}",
                })
            rows.append({
                "model_id": model_id,
                "metric": "transient_all_ports",
                "scenario_id": f"scenario-{scenario}",
            })
    return rows


def test_parse_prima_orders_accepts_comma_separated_values():
    assert parse_prima_orders("56, 84,112") == (56, 84, 112)


@pytest.mark.parametrize(
    "value", ["", "0", "56,not-an-order", "56,56", "56,,84", "56,"]
)
def test_parse_prima_orders_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_prima_orders(value)


def test_validate_resource_sweep_accepts_exact_model_and_port_coverage():
    result = validate_resource_sweep_rows(
        _rows(), extended_orders=(56, 84), candidate_order=84, expected_ports=9
    )
    assert result["total_rows"] == 210
    assert result["frequency_rows"] == 30
    assert result["transient_port_rows"] == 162
    assert result["transient_all_ports_rows"] == 18
    assert result["actual_order"] == 84
    assert result["full_compartment_order"] == 12399


def test_validate_resource_sweep_rejects_wrong_model_identity():
    rows = _rows()
    rows[0] = {**rows[0], "model_id": "unexpected_model"}
    with pytest.raises(ValueError, match="model identity coverage mismatch"):
        validate_resource_sweep_rows(
            rows, extended_orders=(56, 84), candidate_order=84, expected_ports=9
        )


def test_validate_resource_sweep_rejects_requested_order_without_matching_rank():
    rows = _rows()
    rows[140]["prima_order"] = "56"
    with pytest.raises(ValueError, match="rank mismatch"):
        validate_resource_sweep_rows(
            rows, extended_orders=(56, 84), candidate_order=84, expected_ports=9
        )


def test_validate_resource_sweep_rejects_incomplete_port_matrix():
    rows = _rows()
    rows.pop()
    with pytest.raises(ValueError, match="metric coverage mismatch"):
        validate_resource_sweep_rows(
            rows, extended_orders=(56, 84), candidate_order=84, expected_ports=9
        )


def test_validate_resource_sweep_rejects_port_count_skew_between_scenarios():
    rows = _rows()
    candidate_rows = [
        row for row in rows
        if row.get("model_id") == "six_shift_order84" and row.get("metric") == "transient_port"
    ]
    candidate_rows[0]["port_swc_id"] = "duplicate-node"
    candidate_rows[1]["port_swc_id"] = "duplicate-node"
    with pytest.raises(ValueError, match="duplicate or missing scenario/port records|per-scenario port count"):
        validate_resource_sweep_rows(
            rows, extended_orders=(56, 84), candidate_order=84, expected_ports=9
        )
