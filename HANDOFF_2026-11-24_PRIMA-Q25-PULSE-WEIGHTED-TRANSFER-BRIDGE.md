# Handoff — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Parent:** Krylov-prefix transfer audit / PR #24

## Research question

The completed AC transfer audit found dual-q25 transfer residuals above seven-port on both morphologies, but the time-domain order-168 pulse NRMSE penalty was 14.525× on Peng and only 1.001× on Tamas. This follow-up weights the dense complex transfer residual by the actual 2-ms and 10-ms rectangular pulse spectra and joins each result to the archived pulse NRMSE pair.

## Design

- Two checksum-pinned morphologies.
- Seven-port baseline and dual-q25 nine-port candidate only.
- Basis order 168.
- Nine passive parameter scenarios.
- Three current sources and seven shared output nodes.
- Dense 0–5,000 Hz grid, 5-Hz spacing (1,001 frequencies).
- Rectangular pulse spectrum `|I(f)|² = (I0·T·sinc(fT))²`, with 10 pA amplitude, 2-ms onset and pulse widths 2/10 ms.
- Four frequency bands: 0–100, 100–500, 500–2,000, 2,000–5,000 Hz.
- Full Hines complex response computed with a vectorized tree solve; reduced response uses the PRIMA reduced G/C matrices.
- Compare pulse-weighted spectral error with the exact archived time-domain transient NRMSE row for the same morphology/scenario/source/output/pulse width.

The weighted AC metric is a continuous-time Parseval proxy. It is not asserted to exactly reproduce the finite-step backward-Euler transient solver.

## Expected coverage

- 3,024 per-layout weighted source/output/pulse rows.
- 12,096 frequency-band energy rows.
- 1,512 paired dual-q25 vs seven spectral/transient rows.
- 336 output summaries.
- 84 paired output summary groups.
- 48 by-source/layout summaries.
- 192 aggregated band summaries.

## Scientific limits

A large spectral ratio can arise from a very small seven-port error denominator. Preserve absolute weighted errors beside ratios. The pulse-weighted spectrum proxy and finite-window backward-Euler NRMSE are not identical measures. Only two individual passive linear-RC reconstructions are compared; no biological or population claim. Full Hines remains canonical and no production code/defaults change.
