# Handoff — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Parent:** Krylov-prefix transfer audit / PR #24  
**Draft PR:** [#27](https://github.com/Nolane-x/Nghien-cuu/pull/27)  
**Current workflow:** [45343771112](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112) — full numeric step in progress at handoff update

## Research question

At order 168, dual-q25 AC transfer residuals are above seven-port on both Peng and Tamas, but the time-domain pulse penalty is 14.525× on Peng and only 1.001× on Tamas. This follow-up weights dense transfer residuals by the spectra of the exact 2-ms and 10-ms rectangular inputs and joins each weighted value to the archived transient NRMSE pair.

## Design

- NMO_163775 Peng mouse and NMO_107159 Tamas human pyramidal, with pinned source hashes.
- Seven-port baseline and dual-q25 nine-port only; basis order 168.
- All nine passive parameter scenarios, three sources and seven shared outputs.
- Dense 0–5,000 Hz grid at 5-Hz spacing (1,001 frequencies).
- Rectangular 10-pA pulse spectrum for widths 2 ms and 10 ms; onset 2 ms.
- Four weighted frequency bands: 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz.
- Full Hines complex response compared with PRIMA reduced response.
- Every dual-q25 weighted source/output/scenario/pulse result is joined to its exact time-domain transient row.

The pulse-weighted error is a continuous-time Parseval proxy, not an exact recreation of finite-step backward-Euler transients.

## Exact expected coverage

- 1,512 weighted source/output/pulse rows.
- 6,048 band-energy rows.
- 756 dual-q25 vs seven spectral/transient bridge rows.
- 168 by-output summaries.
- 84 paired output comparison summaries.
- 12 by-source summaries.
- 96 pooled band summaries.

## Validation state

The latest run 45343771112 has passed:
- 7/7 focused tests.
- Both SWC SHA-256 checks.
- Both archived transient input-file checks.
- Both Import3D preflights.

The dense pulse-weighted numerical calculation is the remaining workflow step. No numeric finding is claimed until it completes and the output CSVs/JSON are read back.

## Scientific limits

Large ratios may come from an extremely small seven-port denominator, so absolute weighted errors stay beside ratios. Pulse-weighted continuous-time transfer error is not identical to the finite-step backward-Euler NRMSE. Only two individual passive linear-RC morphology reconstructions are compared; no biological or population conclusion follows. Full Hines remains canonical; production code and defaults are unchanged.
