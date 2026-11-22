import pytest

from prima_resource_benchmark_validator import (
    EXPECTED_PER_MODEL_METRIC_COUNTS,
    parse_prima_order_list,
    validate_prima_resource_sweep,
)


def synthetic_rows(orders=(56, 112)):
    rows = []
    models = ["four_shift_order56_control"] + [f"six_shift_order{order}" for order in orders]
    model_orders = {"four_shift_order56_control": 56}
    model_orders.update({f"six_shift_order{order}": order for order in orders})
    for model_id in models:
        for metric, count in EXPECTED_PER_MODEL_METRIC_COUNTS.items():
            for index in range(count):
                rows.append({
                    "model_id": model_id,
                    "metric": metric,
                    "prima_order": str(model_orders[model_id]),
                    "record_index": str(index),
                })
    return rows


def test_parse_csv_order_list_with_whitespace():
    assert parse_prima_order_list("56, 112") == (56, 112)
    assert parse_prima_order_list("56,84,168") == (56, 84, 168)


@pytest.mark.parametrize(
    "raw",
    ["", "  ", "56,", ",112", "56,,112", "56,abc", "56,56", "112,168", "56,112,84", "56,0"],
)
def test_parse_order_list_rejects_malformed_or_unsupported_lists(raw):
    with pytest.raises(ValueError):
        parse_prima_order_list(raw)


def test_validator_accepts_csv_matrix_and_selects_last_candidate():
    result = validate_prima_resource_sweep(synthetic_rows(), parse_prima_order_list("56,112"))
    assert result["candidate_order"] == 112
    assert result["candidate_model_id"] == "six_shift_order112"
    assert len(result["candidate_rows"]) == 10
    assert result["counts"] == {
        "frequency_response": 30,
        "transient_port": 162,
        "transient_all_ports": 18,
    }


def test_validator_accepts_three_requested_orders():
    rows = synthetic_rows((56, 84, 168))
    result = validate_prima_resource_sweep(rows, parse_prima_order_list("56,84,168"))
    assert result["candidate_order"] == 168
    assert result["candidate_model_id"] == "six_shift_order168"
    assert result["counts"] == {
        "frequency_response": 40,
        "transient_port": 216,
        "transient_all_ports": 24,
    }


def test_validator_rejects_wrong_model_identity():
    rows = synthetic_rows()
    rows[0]["model_id"] = "six_shift_order56,112"
    with pytest.raises(ValueError, match="model identity coverage mismatch"):
        validate_prima_resource_sweep(rows, (56, 112))


def test_validator_rejects_incomplete_metric_coverage():
    rows = synthetic_rows()
    rows.pop()
    with pytest.raises(ValueError, match="coverage mismatch"):
        validate_prima_resource_sweep(rows, (56, 112))


def test_validator_rejects_wrong_realized_rank():
    rows = synthetic_rows()
    for row in rows:
        if row["model_id"] == "six_shift_order112" and row["metric"] == "frequency_response":
            row["prima_order"] = "84"
    with pytest.raises(ValueError, match="did not produce exact rank"):
        validate_prima_resource_sweep(rows, (56, 112))
