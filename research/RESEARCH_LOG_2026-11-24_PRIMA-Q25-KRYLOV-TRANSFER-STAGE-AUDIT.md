# Research log — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Successful workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089)  
**Result archive commit:** `83ccc27d21d87e1a50a2ad48414958fe62a4c63e`

## Motivation

The prior Krylov audit showed identical vector-count schedules on Peng and Tamas but different candidate residual ratios. This audit measures whether those different basis prefixes yield a better or worse approximation to the source-to-output AC transfer functions at the seven shared output nodes.

## Implementation and validation

For each morphology, layout, order and passive scenario:
- preserve a basis snapshot after the complete seed stage and after every complete round-robin Krylov round;
- project passive G and C using the production conductance operator;
- solve reduced complex transfer responses for soma, basal-q75 and apical-q75 sources at nine frequencies;
- compare seven shared output nodes against full-Hines responses;
- compare the final instrumented basis against the unmodified production PRIMA builder, and final projected G/C against the production reduced matrices.

Workflow [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089) completed successfully. Five focused tests, both source hashes, both Import3D preflights, the 504-snapshot matrix and all parity guards passed.

Exact rows: 504 snapshots; 10,584 per-scenario source/output transfer summaries; 95,256 frequency/source/output rows; 1,176 scenario-aggregated output summaries; 168 source summaries. Maximum final-basis difference from production = 0.0; maximum basis orthogonality entry error = 2.22e-15.

Runtime: 220.51 s wall, 308.03 s user CPU, 300,248 KB maximum RSS. Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

Artifact [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14894466250), SHA-256 `6f11321129aa05bc6208e67723fd211f7d4723c85138ea80e879eb25c7313026`.

## Transfer convergence — dual-q25 order 168

Median across the three source summaries of the median complex transfer L2 error over seven shared outputs:

| Prefix | Peng (%) | Tamas (%) |
|---|---:|---:|
| Seed (54) | 7.788e-2 | 1.848e-2 |
| Round 1 (108) | 4.427e-5 | 6.521e-6 |
| Round 2 (162) | 7.466e-8 | 1.065e-8 |
| Round 3 / final order 168 | 2.140e-8 | 2.638e-9 |

Every Krylov round substantially improves the median AC transfer approximation on both morphologies.

### Final dual-q25 versus seven-port, order 168

Median of seven paired output-specific transfer-error ratios:

| Morphology | Source | Median ratio | Worse output groups |
|---|---|---:|---:|
| Peng | Soma | 53.32× | 7/7 |
| Peng | Basal-q75 | 52.01× | 7/7 |
| Peng | Apical-q75 | 43.07× | 7/7 |
| Tamas | Soma | 23.06× | 7/7 |
| Tamas | Basal-q75 | 8.60× | 7/7 |
| Tamas | Apical-q75 | 6.70× | 7/7 |

Absolute relative-L2 transfer errors remain very small: Peng 8.79e-9% (apical-q75) to 7.28e-8% (soma); Tamas 2.30e-9% to 7.90e-9%.

### 8-port comparison at final order 168

Median source-level complex transfer L2 error (%) across the seven outputs:

| Morphology | Source | Seven | Basal-q25 8 | Apical-q25 8 | Dual-q25 9 |
|---|---|---:|---:|---:|---:|
| Peng | Soma | 1.366e-9 | 1.757e-9 | 3.795e-9 | 7.281e-8 |
| Peng | Basal-q75 | 4.115e-10 | 5.628e-10 | 1.120e-9 | 2.140e-8 |
| Peng | Apical-q75 | 2.041e-10 | 2.647e-10 | 5.005e-10 | 8.792e-9 |
| Tamas | Soma | 3.427e-10 | 5.387e-10 | 5.195e-10 | 7.902e-9 |
| Tamas | Basal-q75 | 3.069e-10 | 4.455e-10 | 4.238e-10 | 2.638e-9 |
| Tamas | Apical-q75 | 3.431e-10 | 3.873e-10 | 3.858e-10 | 2.298e-9 |

The dual-q25 configuration has the largest AC transfer residual in each source/morphology row, but all absolute relative-L2 errors remain tiny.

## Order 112 and comparison with transient errors

At final order 112, dual-q25/seven transfer ratios are elevated on both morphologies:
- Peng: 40.21× soma, 40.21× basal-q75, 37.75× apical-q75.
- Tamas: 39.79× soma, 40.19× basal-q75, 35.33× apical-q75.

At order 168, the earlier transient matched-pulse ratio was 14.525× on Peng but 1.001× on Tamas, while this AC transfer analysis still finds dual-q25 transfer residuals above seven-port on both. These are different metrics: complex AC transfer L2 error across nine discrete frequencies versus time-domain pulse NRMSE. The Tamas difference motivates a denser pulse-weighted frequency audit rather than an assumption that the measurements should match one-to-one.

## Interpretation and next step

The prefix analysis shows AC transfer error falling strongly as Krylov vectors are added. The final dual-q25 AC residual nevertheless remains above the seven-port baseline at all seven shared outputs for all source sites on both morphologies. Relative penalties are larger on Peng, while absolute transfer errors remain very small.

The next audit should measure a denser pulse-weighted frequency response for the exact 2-ms and 10-ms input protocols, then compare its integrated error with the time-domain pulse NRMSE. This is especially important for the Tamas order-168 mismatch.

## Files and blob hashes

Result stem: `prima_q25_krylov_transfer_stages_cross_morphology_2026-11-24`.

- `snapshots.csv`: 504 rows.
- `by_output_model.csv`: 10,584 rows.
- `frequency.csv`: 95,256 rows.
- `by_output_summary.csv`: 1,176 rows.
- `by_source_summary.csv`: 168 rows.
- `report.json`, `.time.txt`.

Git blob SHA-1:
- report JSON: `1c4ac637390d9d2fcecd0829f36f3ccee6b6fb05`
- snapshots: `b53142daaba630d3a7e3415e124c3d77f0f4bb3a`
- by-output-model: `988003ad94fe20157d6ceb0415de72d0466cf479`
- frequency: `e41a8ad72aec0b8865f66e7077a4a8074ee1c62f`
- by-output summary: `9f1042f9cd5efc4883cbb4505900c6c117fcf8e4`
- by-source summary: `735530023dd07dd344653891f2fad15cc0968041`
- timing: `84753b35e4d0c94a48401edb209b2306d4dc31c9`

## Limits

Two individual passive linear-RC morphology reconstructions, not biological or population evidence. AC transfer error ratios can amplify very small seven-port denominators. Full Hines remains canonical; no production code/defaults changed.
