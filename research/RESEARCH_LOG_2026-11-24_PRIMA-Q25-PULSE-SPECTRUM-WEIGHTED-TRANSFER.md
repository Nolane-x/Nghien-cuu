# Research log — PRIMA q25 pulse-spectrum-weighted transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-spectrum-weighted-transfer-audit-2026-11-24  
**Status at creation:** implementation prepared; no weighted result claimed.

## Motivation

The previous transfer-stage audit found a substantial order-168 AC transfer penalty for dual-q25 on both morphologies, while the earlier time-domain pulse NRMSE was near baseline for Tamas. This analysis weights complex transfer residuals by the measured input-pulse spectrum and compares them with the exact archived transient errors.

## Method

- Keep only the canonical seven-port and dual-q25 nine-port layouts, basis order168 and nine passive parameter scenarios.
- Calculate full-Hines source-to-shared-output transfer responses and reduced PRIMA responses from DC to 5 kHz.
- Use a dense nonuniform band grid: 10 Hz spacing up to500Hz, then100Hz spacing to5000Hz, plus 0.1 and1Hz samples.
- For the 2ms and10ms ideal rectangular current pulses, weight squared complex transfer residual by (|sinc(fT)|^2) and integrate with the trapezoidal rule.
- Join weighted transfer rows to existing per-port transient NRMSE by morphology, scenario, source, output and pulse width.
- Compare candidate/seven ratios and compute Pearson/Spearman correlations in log-ratio space by morphology, source and pulse width.

The onset phase has unit magnitude and cancels in an energy ratio. The 5kHz maximum is Nyquist for dt=0.1ms. This does not model finite observation-window leakage or discrete-time solver effects exactly.

## Expected coverage

- 74,088 frequency rows.
- 1,512 pulse-weighted output rows.
- 168 weighted-output summaries;24 weighted-source summaries.
- 756 dual-q25-vs-seven/time-domain paired rows.
- 12 source/pulse summaries.
- 196 spectrum sample rows (98 frequencies ×2 pulse widths).

## Files created

- `amsn-core/research/analyze_prima_q25_pulse_weighted_transfer.py`
- `amsn-core/tests/test_prima_q25_pulse_weighted_transfer.py`
- `.github/workflows/amsn-prima-q25-pulse-spectrum-weighted-transfer.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-PULSE-SPECTRUM-WEIGHTED-TRANSFER.md`
- This research log.

## Interpretation limits

The spectral weighted metric is a band-limited surrogate for pulse response energy. It is not equal by definition to the finite 20ms transient NRMSE. Keep those metrics separate and assess their empirical correlation. No biological or population-level conclusions; full Hines remains canonical and production defaults unchanged.
