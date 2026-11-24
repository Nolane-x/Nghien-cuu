# Cross-morphology PRIMA q25 Krylov growth audit

**Date:** 24 November 2026  
**Workflow:** [GitHub Actions run 45335399160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160) — success  
**Result archive commit:** `29f3daa5ca4b2698f183422236b8aec94dc106d4`  
**Artifact:** [prima-q25-krylov-growth-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335399160/artifacts/14893173336)  
**Artifact SHA-256:** `438651dc40409fbe5bfc2685b17e7fb075a78d3bf0cfd2b3045bbb45ed29c682`

## 1. Aim

The preceding basis-conditioning audit found machine-precision orthogonality and full acceptance of each initial shift input-port block, but did not explain the order-168 dual-q25 transient difference between NMO_163775 Peng mouse and NMO_107159 Tamas human pyramidal morphologies.

This audit instruments the later round-robin block-Krylov growth to quantify, by shift and round, how much each candidate vector survives projection against the current basis.

## 2. Exact validation and coverage

The corrected workflow passed five focused tests, both SWC SHA-256 checks, both Import3D preflights, the full trace, production-basis parity checks, result commit and artifact upload.

| Dataset | Expected / verified rows |
|---|---:|
| Model summaries | 144 |
| Initial shift-block summaries | 864 |
| Candidate vector events | 20,160 |
| Shift-round summaries | 3,024 |
| Rejected candidate vectors | 0 |
| Instrumented-vs-production maximum absolute basis difference | 0.0 |

The maximum orthogonality entry error across traced bases is 1.78e-15.

Runtime was 305.93 seconds wall time, 358.66 seconds user CPU and 200,468 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

The instrumented modified Gram-Schmidt mirrors the current private production routine, including projection ordering. Its final basis is rebuilt independently using the unchanged production PRIMA function for each model; every element matches exactly in this run.

## 3. Accepted-vector counts

All four layouts follow the same accepted-vector schedule on both morphologies.

| Layout | Order | Seed columns | Later Krylov columns | Krylov rounds |
|---|---:|---:|---:|---:|
| seven | 112 | 42 | 70 | 2 |
| seven | 168 | 42 | 126 | 3 |
| eight_basal_q25 | 112 | 48 | 64 | 2 |
| eight_basal_q25 | 168 | 48 | 120 | 3 |
| eight_apical_q25 | 112 | 48 | 64 | 2 |
| eight_apical_q25 | 168 | 48 | 120 | 3 |
| nine_both_q25 | 112 | 54 | 58 | 2 |
| nine_both_q25 | 168 | 54 | 114 | 3 |

For dual-q25 order 168, both morphologies accept nine new vectors per shift in rounds 1 and 2. In round 3, only six more from the 0-Hz block are processed before the order cap reaches 168; the other five shift blocks remain unprocessed. No attempted candidate was rejected by the (10^{-12}) relative tolerance. The schedule therefore does not explain the morphology-dependent transient error by a difference in vector counts.

## 4. Per-shift candidate novelty — dual-q25 order 168

Residual ratio means post-orthogonalization residual norm divided by the candidate's original norm. The table reports the median across nine passive parameter scenarios of the *minimum accepted candidate residual ratio* within each shift/round block.

| Shift | Peng round 1 | Tamas round 1 | Peng round 2 | Tamas round 2 |
|---:|---:|---:|---:|---:|
| 0 Hz | 4.19e-8 | 2.84e-5 | 2.16e-8 | 6.09e-8 |
| 100 Hz | 4.13e-8 | 2.11e-5 | 5.95e-8 | 9.83e-8 |
| 1,000 Hz | 2.24e-8 | 1.65e-5 | 1.02e-6 | 1.98e-6 |
| 3,000 Hz | 4.51e-8 | 1.89e-5 | 2.44e-6 | 4.36e-6 |
| 6,000 Hz | 2.63e-7 | 3.42e-5 | 4.92e-6 | 1.37e-5 |
| 10,000 Hz | 1.91e-5 | 8.90e-5 | 2.38e-5 | 6.81e-5 |

During round 1, the weakest surviving Peng directions are much closer to the already-built subspace than the weakest Tamas directions, particularly at 0–6 kHz. All remain above the acceptance threshold and are retained. During round 2 the smallest residual ratios remain generally lower on Peng, although the gap narrows.

The final round is especially different: both morphologies accept six vectors from 0 Hz. The median minimum residual ratio is **9.53e-5** on Peng and **2.61e-7** on Tamas; the median of accepted residual ratios is **3.82e-3** versus **2.68e-6**. Thus the final six Peng vectors are much less represented by the current basis before acceptance than the final six Tamas vectors.

## 5. Interpretation

The Krylov audit localizes a morphology-dependent difference in candidate novelty and round-by-round subspace composition. The vector-count schedule, number of Krylov rounds and initial shift blocks are identical. The notable differences lie in the distribution of residual/original ratios for the accepted candidate vectors, particularly the weakest candidates during early rounds and the final 0-Hz completion block.

This is **not** a causal proof that those candidate directions produce the transient errors. A large residual ratio means a vector is less represented by the current basis; it does not show that the vector is important to any specific source-to-output transfer function. The measured pattern must be connected to transfer residual reduction at the shared outputs before a mechanism can be asserted.

The next targeted experiment should project each accepted Krylov block onto the seven shared output rows, and measure frequency-specific source-to-output transfer residual reduction after every shift/round. That would test whether the different candidate novelty is actually useful or harmful for the outputs that diverge in Peng and remain near baseline in Tamas.

## 6. Scientific constraints

This is a passive linear-RC numerical basis-construction audit on two individual morphology reconstructions, not a population or biological validation. The source morphologies remain separate. Full Hines remains canonical. No production solver code or defaults are changed.

## 7. Reproducible outputs

Result stem: `prima_q25_krylov_growth_cross_morphology_2026-11-24`.

- `models.csv`: 144 model summaries.
- `candidate_events.csv`: 20,160 candidate events.
- `shift_rounds.csv`: 3,024 shift/round summaries.
- `report.json`: status, exact coverage and source scope.
- `.time.txt`: runtime and resource usage.

Verified Git blob SHA-1:
- report JSON: `13705a1297e56f4c46caa481c175abd01af753f3`
- models CSV: `e411135f41fb2954c8b80f4d279de87a95a3c30b`
- candidate events CSV: `0087fbb0674c1672c0da7a42ea3235c82e931957`
- shift rounds CSV: `c40fa2bda8127cb85ce76ee5c0f51a20cdb70177`
- timing file: `526096a645c2b1ce2283834c6b7761c6d0810b46`
