# Research log — PRIMA q25 transfer frequency localization

**Date:** 24 November 2026  
**Branch:** research/prima-q25-transfer-frequency-localization-2026-11-24  
**Status at creation:** deterministic post-processing prepared; no new frequency-localized result claimed.

## Motivation

The Krylov-prefix transfer audit showed AC transfer residuals improving strongly as the basis grows, but dual-q25 remained above seven-port at every shared output on both morphologies. The order-168 transient results were substantially closer for Tamas than the AC metric suggested. This analysis will localize residuals by frequency and annotate the sampled frequencies with the spectral magnitude of the two pulse widths.

## Method

Read the validated 95,256-row frequency CSV produced by PR #24; verify exact morphology, layout, stage, source, output-node/role, scenario and frequency identities. Aggregate the nine passive scenarios per source/output/frequency. Compare each candidate error with the seven-port error at the same morphology, stage, source, output and frequency. Aggregate over seven outputs for a source/frequency summary.

For rectangular pulses, record (|sinc(fT)|) and its square at the nine AC sample frequencies for (T=2) ms and (T=10) ms. Because the frequency grid is sparse/log-spaced, these values are explanatory samples only—not quadrature weights or a direct estimate of pulse error.

## Expected coverage

- 10,584 output/frequency groups.
- 1,512 source/frequency groups.
- 7,938 paired candidate-vs-seven output/frequency rows.
- 1,134 paired source/frequency summaries.
- 18 pulse-spectrum samples.
- Top 100 output/frequency residual groups.

## Files created

- `amsn-core/research/analyze_prima_q25_transfer_frequency_localization.py`
- `amsn-core/tests/test_prima_q25_transfer_frequency_localization.py`
- `.github/workflows/amsn-prima-q25-transfer-frequency-localization.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-TRANSFER-FREQUENCY-LOCALIZATION.md`
- This research log.

## Interpretation limits

AC transfer errors are not identical to time-domain pulse NRMSE. Pulse spectrum samples cannot be integrated over this sparse grid. Keep absolute transfer error alongside relative ratios. Passive linear-RC and two individual morphologies only; no biological or population inference and no production default changes.
