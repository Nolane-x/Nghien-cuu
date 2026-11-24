# Research log — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Status at creation:** implementation prepared; no pulse-weighted results claimed.

## Motivation

The q25 prefix transfer audit found that final dual-q25 AC transfer residuals are higher than seven-port on both Peng and Tamas. However, the matched time-domain pulse experiment at order 168 showed 14.525× degradation on Peng and 1.001× on Tamas. This bridge tests how the AC residual is weighted by the actual rectangular pulse spectra.

## Method

At order 168, for seven-port and dual-q25, all nine passive parameter scenarios, three input sources and seven shared outputs:
1. Compute full-Hines and PRIMA transfer functions on a 0–5,000 Hz grid at 5-Hz spacing (1,001 points).
2. Weight the complex transfer difference by `|I(f)|²` for 10-pA rectangular pulses of 2 ms and 10 ms width. Onset is 2 ms; onset affects phase, not the spectral power weight.
3. Integrate error and reference energy using Parseval weighting; report pulse-weighted relative L2 error.
4. Partition the weighted error energy into four frequency bands (0–100, 100–500, 500–2,000, 2,000–5,000 Hz).
5. Join each dual-q25 output/source/scenario/pulse row to the archived time-domain transient NRMSE pair.
6. Summarize weighted spectral ratios and time-domain transient ratios separately.

The vectorized full-Hines frequency solve is unit-tested against the production single-frequency CableTree solver on a small cable fixture.

## Expected coverage

- 3,024 weighted model/output rows.
- 12,096 band-energy rows.
- 1,512 dual-q25 vs seven comparison rows joined to transient NRMSE.
- 336 by-output summaries.
- 84 output comparison summaries.
- 48 source/layout summaries.
- 192 pooled band summaries.

## Files created

- `amsn-core/research/analyze_prima_q25_pulse_weighted_transfer_bridge.py`
- `amsn-core/tests/test_prima_q25_pulse_weighted_transfer_bridge.py`
- `.github/workflows/amsn-prima-q25-pulse-weighted-transfer-bridge.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-PULSE-WEIGHTED-TRANSFER-BRIDGE.md`
- This research log.

## Interpretation limits

This integrates continuous-time frequency responses against rectangular-pulse spectral power. It is a Parseval-weighted proxy, not an exact reproduction of finite-step backward-Euler time traces or finite observation-window truncation. Ratio denominators may be very small. The result is numerical and passive linear-RC only.
