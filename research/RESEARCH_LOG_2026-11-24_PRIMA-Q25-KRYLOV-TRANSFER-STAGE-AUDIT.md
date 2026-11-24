# Research log — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Successful workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089)  
**Result commit:** `a0d6e8e2c9a8f203d53a0c0c04c2691f9cc8702f`

## Motivation

The prior Krylov audit showed identical vector-count schedules on Peng and Tamas but different candidate residual ratios. This audit measures whether those different basis prefixes yield a better or worse approximation to the source-to-output AC transfer functions at the seven shared output nodes.

## Implementation and validation

For each morphology, layout, order and passive scenario:
- preserve a basis snapshot after the complete seed stage and after every complete round-robin Krylov round;
- project passive (G) and (C) using the production conductance operator;
- solve reduced complex transfer responses for soma, basal-q75 and apical-q75 sources at nine frequencies;
- compare seven shared output nodes against full-Hines responses;
- compare the final instrumented basis against the unmodified production PRIMA builder, and final projected (G_r/C_r) against the production reduced matrices.

Workflow [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089) completed successfully. Five focused tests, both source hashes, both Import3D preflights, the 504-snapshot matrix and all parity guards passed.

Exact rows: 504 snapshots; 10,584 per-scenario source/output transfer summaries; 95,256 frequency/source/output rows; 1,176 scenario-aggregated output summaries; 168 source summaries. Maximum final-basis difference from production = 0.0; maximum basis orthogonality entry error = 1.78e-15.

Runtime: 220.51 s wall, 308.03 s user CPU, 300,248 KB maximum RSS. Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

Artifact [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14893398287), SHA-256 `a274bcd3ff1ce31bc2659bd6d3f12b0bd93b7d2853f8d6f62bdf82f7e0a1e9d`.

## Transfer convergence — dual-q25 order 168

Median across the three sources of the median complex transfer L2 error over seven shared outputs:

| Prefix | Peng (%) | Tamas (%) |
|---|---:|---:|
| Seed | 7.788e-2 | 1.848e-2 |
| Round 1 | 4.427e-5 | 6.521e-6 |
| Round 2 | 7.466e-8 | 1.065e-8 |
| Round 3 / final order 168 | 2.140e-8 | 2.638e-9 |

Every Krylov round strongly reduces the AC transfer residual on both morphologies. The final dual-q25 transfer error remains above the seven-port baseline at all seven shared outputs for all three source sites on both morphologies.

### Final dual-q25 versus seven-port, order 168

Median of the seven output-specific transfer error ratios:

| Morphology | Source | Median ratio | Worse output groups |
|---|---|---:|---:|
| Peng | Soma | 53.32× | 7/7 |
| Peng | Basal-q75 | 50.48× | 7/7 |
| Peng | Apical-q75 | 45.29× | 7/7 |
| Tamas | Soma | 23.15× | 7/7 |
| Tamas | Basal-q75 | 9.56× | 7/7 |
| Tamas | Apical-q75 | 6.16× | 7/7 |

Source-level absolute relative-L2 transfer error remains very small: Peng 8.79e-9% (apical-q75) to 7.28e-8% (soma); Tamas 2.30e-9% (apical-q75) to 7.90e-9% (soma).

## Order 112 and comparison with transient errors

At the final order-112 prefix the dual-q25/seven transfer ratios are also elevated on both morphologies:
- Peng: 40.21× soma, 40.21× basal-q75, 37.75× apical-q75.
- Tamas: 39.79× soma, 40.19× basal-q75, 35.33× apical-q75.

This is broadly aligned with the earlier order-112 transient degradation on both samples. At order 168, however, the transient matched-pulse ratio was 14.525× on Peng but 1.001× on Tamas, while this AC transfer analysis still finds dual-q25 transfer residuals above seven-port on both. These are different metrics and must not be conflated: the AC metric is a complex transfer L2 error over nine frequency samples; transient NRMSE is computed on time-domain pulse traces. Frequency-specific errors can integrate differently in the time domain.

## Interpretation

The prefix analysis shows the AC transfer approximation improving strongly as Krylov vectors are added. Yet the final dual-q25 AC transfer residual remains relatively larger than seven-port, particularly on Peng. The Tamas time-domain pulse result remains near baseline despite an elevated AC transfer-error ratio. This suggests that frequency weighting and source/output transfer structure may matter, but the current data do not prove a causal mechanism.

A follow-up should identify which frequency bands dominate the final AC residual and test whether those bands contribute materially to the pulse waveform under the tested input timing. Keep the full-Hines reference canonical and do not change production defaults.

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
