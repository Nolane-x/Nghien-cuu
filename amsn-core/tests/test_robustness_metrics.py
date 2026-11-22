import numpy as np
import pytest

from amsn.robustness_metrics import (
    columnwise_relative_l2_percent,
    relative_l2_percent,
)


def test_relative_l2_percent_matches_known_error():
    assert relative_l2_percent([1.0, 2.0], [1.0, 3.0]) == pytest.approx(
        100.0 / np.sqrt(5.0)
    )


def test_relative_l2_percent_supports_complex_frequency_response():
    assert relative_l2_percent([1 + 1j], [1 + 2j]) == pytest.approx(100.0 / np.sqrt(2.0))


def test_relative_l2_percent_uses_floor_for_zero_reference():
    assert relative_l2_percent([0.0, 0.0], [1e-32, 0.0]) == pytest.approx(1.0)


def test_columnwise_relative_l2_percent_returns_each_port_error():
    reference = np.array([[1.0, 0.0], [1.0, 0.0]])
    approximation = np.array([[1.0, 1e-31], [2.0, 0.0]])
    result = columnwise_relative_l2_percent(reference, approximation)
    np.testing.assert_allclose(result, [100.0 / np.sqrt(2.0), 10.0])


@pytest.mark.parametrize(
    "reference,approximation",
    [
        ([1.0], [1.0, 2.0]),
        ([], []),
        ([float("nan")], [0.0]),
        ([1.0], [float("inf")]),
    ],
)
def test_relative_l2_percent_rejects_invalid_arrays(reference, approximation):
    with pytest.raises(ValueError):
        relative_l2_percent(reference, approximation)


@pytest.mark.parametrize("floor", [0.0, -1.0, float("nan"), float("inf")])
def test_relative_l2_percent_rejects_invalid_floor(floor):
    with pytest.raises(ValueError):
        relative_l2_percent([1.0], [1.0], floor=floor)
