"""Tests for the finite-window discrete-time PRIMA error spectrum audit."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

RESEARCH = Path(__file__).parents[1] / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import analyze_prima_q25_discrete_time_error_spectrum as audit


def test_expected_exact_coverage():
    assert audit.expected_counts() == {
        "trace_rows": 6048,
        "band_energy_rows": 24192,
        "band_comparison_rows": 12096,
        "layout_band_summary_rows": 384,
        "comparison_band_summary_rows": 192,
        "archived_20ms_parity_rows": 1512,
    }


@pytest.mark.parametrize("sample_count", [200, 400, 1000, 2000])
def test_parseval_decomposition_reproduces_time_energy(sample_count):
    dt_s = 1e-4
    t = np.arange(sample_count, dtype=float) * dt_s
    error = (0.7 * np.sin(2 * np.pi * 35 * t)
             + 0.2 * np.cos(2 * np.pi * 725 * t)
             + 0.05 * np.sin(2 * np.pi * 3200 * t))
    reference = 0.1 + 0.01 * np.cos(2 * np.pi * 8 * t)
    rows, diagnostics = audit.parseval_band_decomposition(error, reference, dt_s)
    expected = float(np.dot(error, error))
    observed = sum(float(x["band_error_energy_v2_samples"]) for x in rows)
    assert np.isclose(observed, expected, rtol=5e-12, atol=1e-30)
    assert diagnostics["parseval_relative_error"] <= audit.PARSEVAL_RELATIVE_TOLERANCE
    assert np.isclose(
        sum(float(x["band_nrmse_pct"]) ** 2 for x in rows),
        diagnostics["time_domain_nrmse_pct"] ** 2,
        rtol=5e-12,
        atol=1e-24,
    )
    assert sum(float(x["band_error_energy_share_pct"]) for x in rows) == pytest.approx(100.0)


def test_frequency_bands_partition_each_window():
    for window_ms in audit.WINDOWS_MS:
        n = int(round(window_ms / audit.DT_MS))
        frequencies = np.fft.rfftfreq(n, d=audit.DT_S)
        masks = [
            audit._band_mask(frequencies, low, high, include_upper=i == len(audit.BANDS_HZ) - 1)
            for i, (_, low, high) in enumerate(audit.BANDS_HZ)
        ]
        assert np.all(np.sum(np.stack(masks), axis=0) == 1)
        assert frequencies[0] == 0.0
        assert frequencies[-1] == pytest.approx(5000.0)
        assert frequencies[1] == pytest.approx(1000.0 / window_ms)


def test_zero_error_has_zero_energy_and_no_nan():
    rows, diagnostics = audit.parseval_band_decomposition(
        np.zeros(200), np.ones(200), audit.DT_S
    )
    assert diagnostics["time_domain_nrmse_pct"] == 0.0
    assert all(float(x["band_error_energy_share_pct"]) == 0.0 for x in rows)
    assert all(float(x["band_nrmse_pct"]) == 0.0 for x in rows)
