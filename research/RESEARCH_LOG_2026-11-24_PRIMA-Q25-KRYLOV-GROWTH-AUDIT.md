# Research log — Cross-morphology PRIMA q25 Krylov growth audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-growth-cross-morphology-2026-11-24  
**Successful workflow:** [45335399160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160)  
**Result archive commit:** `29f3daa5ca4b2698f183422236b8aec94dc106d4`

## Motivation

The earlier conditioning audit found machine-precision basis orthogonality and full acceptance of every initial shift input-port block, yet did not explain why the dual-q25 order-168 transient penalty differs between Peng mouse and Tamas human pyramidal morphologies. This audit traced the later round-robin block-Krylov growth.

## Implementation and validation

The instrumented builder mirrors the current private twice-reorthogonalized modified Gram-Schmidt routine and its projection ordering. For every one of 144 models it rebuilt the unmodified production PRIMA basis and compared the full basis arrays.

- Workflow [45335399160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160): success.
- Focused tests: 5 passed.
- Both SWC SHA-256 checks and both Import3D preflights passed.
- 144 model summaries, 864 seed-block rows, 20,160 candidate-event rows, 3,024 shift-round rows.
- Total rejected candidates: 0; vectors left unprocessed after hitting the requested order are recorded separately.
- Maximum absolute difference from production basis: **0.0** over all 144 models.
- Maximum orthogonality entry error: 1.78e-15.
- Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.
- Runtime: 305.93 s wall, 358.66 s user CPU, 200,468 KB maximum RSS.
- Result commit: `29f3daa5ca4b2698f183422236b8aec94dc106d4`.
- Artifact: [prima-q25-krylov-growth-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160/artifacts/14893173336), SHA-256 `438651dc40409fbe5bfc2685b17e7fb075a78d3bf0cfd2b3045bbb45ed29c682`.

## Exact accepted-vector schedule

At order 168 the accepted counts are identical for both morphologies:
- Seven ports: 42 seed columns, then 7 from each of six shifts in each of three Krylov rounds (126 later columns).
- Either eight-port layout: 48 seed columns, then 8 from each shift in two full rounds (96), then 24 more from the first three shifts in round 3.
- Dual-q25 nine-port: 54 seed columns, then 9 from each shift in rounds 1 and 2 (108), then 6 more from the 0-Hz shift in round 3.

At order 112 the schedule is likewise identical across the two samples:
- Seven ports: 42 seed + 42 in round 1 + 28 from four shifts in round 2.
- Either eight-port layout: 48 seed + 48 in round 1 + 16 from two shifts in round 2.
- Dual-q25 nine-port: 54 seed + 54 in round 1 + 4 from the 0-Hz shift in round 2.

Thus vector counts alone do not explain the morphology-specific transient behavior.

## Residual ratio profiles — dual-q25 order 168

Each entry below is the median across nine passive scenarios of the smallest accepted (|r|_2/|v|_2) ratio in the candidate block for that shift and round.

| Shift | Peng round 1 | Tamas round 1 | Peng round 2 | Tamas round 2 |
|---:|---:|---:|---:|---:|
| 0 Hz | 4.19e-8 | 2.84e-5 | 2.16e-8 | 6.09e-8 |
| 100 Hz | 4.13e-8 | 2.11e-5 | 5.95e-8 | 9.83e-8 |
| 1,000 Hz | 2.24e-8 | 1.65e-5 | 1.02e-6 | 1.98e-6 |
| 3,000 Hz | 4.51e-8 | 1.89e-5 | 2.44e-6 | 4.36e-6 |
| 6,000 Hz | 2.63e-7 | 3.42e-5 | 4.92e-6 | 1.37e-5 |
| 10,000 Hz | 1.91e-5 | 8.90e-5 | 2.38e-5 | 6.81e-5 |

At round 3, only the 0-Hz shift contributes the final six vectors for each morphology. Its median minimum accepted residual ratio is 9.53e-5 for Peng and 2.61e-7 for Tamas. Median accepted residual ratios for that block are 3.82e-3 and 2.68e-6 respectively.

The most conspicuous difference is the weakest candidate directions during round 1: Peng has much smaller residual/original ratios, particularly from 0–6 kHz, although all are above the (10^{-12}) acceptance threshold and are accepted. The final 0-Hz completion block reverses the pattern, with much larger novelty ratios on Peng. The resulting subspace composition differs even though the count schedule is the same.

## Interpretation

This establishes a morphology-dependent pattern in per-shift Krylov candidate novelty and block completion. It does **not** establish that this pattern causes the shared-output transient errors. Residual/original ratio measures how much of a candidate remains after projection against the current basis; it does not directly measure transfer-function importance or output error.

The data rule out a simple explanation based on different accepted-vector counts or lost initial shift blocks. The next useful step is to connect these per-candidate directions to source-to-output transfer residuals, for example by projecting each accepted block onto the exact shared output rows and examining frequency-specific transfer residual reduction after each round.

## Files

- `amsn-core/research/audit_prima_q25_krylov_growth.py`
- `amsn-core/tests/test_prima_q25_krylov_growth.py`
- `.github/workflows/amsn-prima-q25-krylov-growth-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-KRYLOV-GROWTH-AUDIT.md`
- Detailed report: `amsn-core/research/PRIMA_Q25_KRYLOV_GROWTH_AUDIT_2026-11-24.md`
- Result stem: `prima_q25_krylov_growth_cross_morphology_2026-11-24`, with `models.csv`, `candidate_events.csv`, `shift_rounds.csv`, `report.json` and `.time.txt`.

## Verified result blob SHA-1

- report JSON: `13705a1297e56f4c46caa481c175abd01af753f3`
- models CSV: `e411135f41fb2954c8b80f4d279de87a95a3c30b`
- candidate events CSV: `0087fbb0674c1672c0da7a42ea3235c82e931957`
- shift rounds CSV: `c40fa2bda8127cb85ce76ee5c0f51a20cdb70177`
- timing file: `526096a645c2b1ce2283834c6b7761c6d0810b46`

## Limits

Two individual passive linear-RC morphologies only. No active channels, synapses, plasticity or biological validation. Full Hines remains canonical. No production code/defaults are changed.
