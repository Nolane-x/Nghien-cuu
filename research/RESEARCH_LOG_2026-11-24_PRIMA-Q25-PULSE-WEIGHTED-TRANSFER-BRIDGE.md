# Research log — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Draft PR:** [#27](https://github.com/Nolane-x/Nghien-cuu/pull/27)  
**Current workflow:** [45343771112](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112)

## Motivation

The Krylov-prefix transfer audit showed a final dual-q25 AC transfer residual above seven-port for both Peng and Tamas. Yet the matched order-168 time-domain pulse NRMSE ratio was 14.525× on Peng and 1.001× on Tamas. This bridge evaluates the complex transfer error after weighting it by the frequency spectrum of the actual rectangular current pulses and joins each result to the transient observation for the identical scenario/source/output/pulse.

## Method

For two checksum-pinned morphologies, seven-port and dual-q25 models at order 168, nine passive parameter scenarios, three sources and seven common output nodes:
1. Compute full-Hines and reduced PRIMA transfer functions on a dense 0–5,000 Hz grid with 5-Hz spacing (1,001 points).
2. Weight squared transfer error by `|I(f)|² = (I0·T·sinc(fT))²` for 10-pA rectangular pulses of 2-ms and 10-ms width.
3. Integrate error and reference energy using Parseval weighting to obtain a pulse-weighted relative L2 proxy.
4. Partition weighted error into 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz bands.
5. Join every dual-q25 output row to its archived time-domain transient NRMSE pair.

The 2-ms onset changes the pulse-spectrum phase but not its power weight. The spectral integral is not an exact reproduction of the finite-step backward-Euler solver or its finite observation window.

## Expected exact coverage

- 1,512 model/output/pulse rows.
- 6,048 band-energy rows.
- 756 dual-q25 vs seven comparison rows.
- 168 by-output summaries.
- 84 comparison summaries.
- 12 by-source summaries.
- 96 pooled band summaries.

## Validation state

Workflow 45343771112 has passed 7 focused tests, both morphology checksums, both transient-input file checks and both Import3D preflights. Dense calculation, output commit and artifact upload remain pending at the current update. No numeric pulse-weighted result is claimed yet.

## Files

- `amsn-core/research/analyze_prima_q25_pulse_weighted_transfer_bridge.py`
- `amsn-core/tests/test_prima_q25_pulse_weighted_transfer_bridge.py`
- `.github/workflows/amsn-prima-q25-pulse-weighted-transfer-bridge.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-PULSE-WEIGHTED-TRANSFER-BRIDGE.md`
- This research log.

## Scientific constraints

The spectral metric is a continuous-time Parseval-weighted proxy, not an exact finite-step transient reconstruction. Ratios may be large with a tiny seven-port denominator. Two passive linear-RC morphology reconstructions are not biological or population evidence. Full Hines remains canonical; no production defaults change.
