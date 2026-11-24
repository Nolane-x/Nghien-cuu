# Handoff — Cross-morphology PRIMA q25 Krylov growth audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-growth-cross-morphology-2026-11-24  
**Parent:** basis-conditioning audit / PR #21  
**Successful workflow:** [45335399160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160)  
**Result commit:** `29f3daa5ca4b2698f183422236b8aec94dc106d4`  
**Detailed report:** [PRIMA_Q25_KRYLOV_GROWTH_AUDIT_2026-11-24.md](amsn-core/research/PRIMA_Q25_KRYLOV_GROWTH_AUDIT_2026-11-24.md)

## Research question

The prior basis-conditioning audit found machine-precision orthogonality and full acceptance of every initial shifted input-port block, but did not explain the Peng-vs-Tamas order-168 dual-q25 transient difference. This audit records later round-robin Krylov candidate growth and residual ratios by shift and round.

## Verified execution and coverage

The corrected workflow passed all five focused tests, both pinned SWC checksum checks, both Import3D preflights, the full trace, exact production-basis parity, result commit and artifact upload.

Read-back coverage:
- 144 model-level summaries (2 morphologies × 4 layouts × 2 orders × 9 passive scenarios).
- 864 seed-block rows.
- 20,160 candidate-event rows.
- 3,024 shift-round rows (864 initial seed blocks + 2,160 Krylov round/shift rows).
- Zero attempted candidates rejected by the relative-tolerance test.
- All 144 instrumented final bases have **exact zero** maximum absolute difference from the production PRIMA basis.

Environment: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2. Runtime: 305.93 s wall, 358.66 s user CPU, 200,468 KB maximum RSS.

Artifact: [prima-q25-krylov-growth-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160/artifacts/14893173336), SHA-256 `438651dc40409fbe5bfc2685b17e7fb075a78d3bf0cfd2b3045bbb45ed29c682`.

## Main result — identical vector counts, different residual profiles

All four layouts have the same accepted vector counts on Peng and Tamas. For example at order 168:
- 7 ports: 42 seed + 126 later Krylov vectors = 168.
- Either 8-port layout: 48 seed + 120 later Krylov vectors = 168.
- Dual-q25 9 ports: 54 seed + 114 later Krylov vectors = 168.

For the dual-q25 order-168 models, both morphologies accept nine new vectors from every shift in rounds 1 and 2. In round 3, the order cap is reached after accepting six more vectors from the first shift (0 Hz); the remaining five shift blocks are unprocessed. This schedule is identical in the two morphologies.

The difference is in the size of the post-orthogonalization residuals, not in whether a vector is accepted. The table below gives, for each shift, the median across the nine passive scenarios of the *smallest accepted residual/original norm ratio* within that round's candidate block.

| Shift | Peng round 1 | Tamas round 1 | Peng round 2 | Tamas round 2 |
|---:|---:|---:|---:|---:|
| 0 Hz | 4.19e-8 | 2.84e-5 | 2.16e-8 | 6.09e-8 |
| 100 Hz | 4.13e-8 | 2.11e-5 | 5.95e-8 | 9.83e-8 |
| 1,000 Hz | 2.24e-8 | 1.65e-5 | 1.02e-6 | 1.98e-6 |
| 3,000 Hz | 4.51e-8 | 1.89e-5 | 2.44e-6 | 4.36e-6 |
| 6,000 Hz | 2.63e-7 | 3.42e-5 | 4.92e-6 | 1.37e-5 |
| 10,000 Hz | 1.91e-5 | 8.90e-5 | 2.38e-5 | 6.81e-5 |

For the final round-3 0-Hz block, both morphologies accept six vectors. The median of the per-scenario minimum accepted residual ratio is 9.53e-5 on Peng versus 2.61e-7 on Tamas; the median accepted residual ratio is 3.82e-3 versus 2.68e-6.

These differences reveal morphology-dependent Krylov subspace novelty despite identical vector-count schedules. They are **not** a causal explanation of the transient error difference: a larger residual ratio means a candidate is less represented by the current basis, not necessarily that it improves a particular transfer function or output.

## Scientific constraints

This is a numerical trace of passive linear-RC basis construction on two individual morphologies. The instrumented basis is checked against the unmodified production builder; no production code/defaults are changed. Keep the mouse and human samples separate. Krylov residual ratios do not establish biological validity or a unique mechanism for transient errors. Full Hines remains canonical.
