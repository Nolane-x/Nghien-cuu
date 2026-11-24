# PRIMA q25 Krylov-prefix source-to-output transfer audit

**Date:** 24 November 2026  
**Workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089) — success  
**Result commit:** `a0d6e8e2c9a8f203d53a0c0c04c2691f9cc8702f`  
**Artifact:** [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14893398287)  
**Artifact SHA-256:** `a274bcd3ff1ce31bc2659bd6d3f12b0bd93b7d2853f8d6f62bdf82f7e0a1e9d`

## 1. Question and method

Does the morphology-dependent Krylov novelty observed previously change the actual source-to-output AC transfer responses as the basis grows?

For NMO_163775 Peng mouse and NMO_107159 Tamas human pyramidal Control, this audit uses four layouts (7, basal-only 8, apical-only 8 and dual-q25 9), orders 112/168, nine passive scenarios, six shifts, nine AC frequencies, three current sources and seven exact shared SWC output nodes.

At each prefix (seed and after each completed round-robin Krylov round), it projects passive (G/C), computes reduced complex transfer responses and compares them with full Hines for the exact same morphology, scenario, layout, source and frequency. The final instrumented basis is compared with the unmodified production builder, and final projected matrices are checked against production.

## 2. Validation

| Dataset | Expected | Verified |
|---|---:|---:|
| Prefix snapshots | 504 | 504 |
| Per-scenario source/output summaries | 10,584 | 10,584 |
| Frequency/source/output rows | 95,256 | 95,256 |
| Scenario-aggregated output summaries | 1,176 | 1,176 |
| Source summaries | 168 | 168 |

Five focused tests passed. Both pinned SWC hashes and Import3D preflights passed. The final instrumented basis differed from production by exactly 0.0 maximum absolute entry error across all models; max orthogonality error was 1.78e-15. Final reduced (G_r/C_r) matrices also passed production parity guards.

Runtime: 220.51 seconds wall, 308.03 seconds user CPU, 300,248 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## 3. Transfer error falls strongly with each Krylov prefix

For dual-q25 at basis order 168, the median across the three sources of the median complex transfer L2 error over seven shared outputs is:

| Prefix | Peng mouse | Tamas human pyramidal |
|---|---:|---:|
| Seed | 7.788e-2% | 1.848e-2% |
| After round 1 | 4.427e-5% | 6.521e-6% |
| After round 2 | 7.466e-8% | 1.065e-8% |
| After round 3 / order 168 | 2.140e-8% | 2.638e-9% |

Every Krylov round substantially improves the transfer approximation on both morphologies.

## 4. Final dual-q25 AC transfer error versus seven-port, order 168

The ratio below is the median of seven paired output-node ratios, each ratio comparing the output-specific median transfer L2 error for dual-q25 with the corresponding seven-port error. All seven output groups are worse for the dual-q25 candidate in every source/morphology row below.

| Morphology | Source | Median dual-q25 / seven transfer-error ratio | Output groups worse |
|---|---|---:|---:|
| Peng mouse | Soma | 53.32× | 7/7 |
| Peng mouse | Basal-q75 | 50.48× | 7/7 |
| Peng mouse | Apical-q75 | 45.29× | 7/7 |
| Tamas human pyramidal | Soma | 23.15× | 7/7 |
| Tamas human pyramidal | Basal-q75 | 9.56× | 7/7 |
| Tamas human pyramidal | Apical-q75 | 6.16× | 7/7 |

The corresponding median source-level transfer L2 error values for dual-q25 remain very small:

| Morphology | Soma | Basal-q75 | Apical-q75 |
|---|---:|---:|---:|
| Peng | 7.281e-8% | 2.140e-8% | 8.792e-9% |
| Tamas | 7.902e-9% | 2.638e-9% | 2.298e-9% |

These are relative errors in a unit-current AC transfer calculation; large ratios partly reflect the very small seven-port denominator.

## 5. Order-112 comparison

At the final order-112 prefix, the dual-q25 transfer-error ratios are elevated on both morphologies:

| Morphology | Soma | Basal-q75 | Apical-q75 |
|---|---:|---:|---:|
| Peng | 40.21× | 40.21× | 37.75× |
| Tamas | 39.79× | 40.19× | 35.33× |

This is consistent with the earlier order-112 time-domain transient degradation on both samples.

## 6. Why AC and transient results must remain separate

The earlier order-168 matched pulse experiment found a dual-q25 median shared-output transient NRMSE ratio of 14.525× on Peng but only 1.001× on Tamas. The current AC transfer audit finds dual-q25 transfer error above seven-port on both morphologies (more strongly on Peng).

These are not contradictory measurements of the same quantity. AC transfer error is a complex L2 comparison across nine discrete frequencies; transient NRMSE evaluates the time-domain pulse traces. Frequency errors can be weighted and combined differently by the pulse waveform and time window. The Tamas difference is therefore a signal to study frequency weighting, not grounds to dismiss either result.

## 7. Interpretation and next step

The audit establishes that:
1. Transfer residuals fall by several orders of magnitude as Krylov vectors are added.
2. The final dual-q25 AC transfer error remains above seven-port at all seven shared outputs for all three source sites on both morphologies.
3. The relative penalty is larger on Peng, but the absolute relative transfer errors remain small.
4. The AC result and the time-domain pulse result diverge most clearly for Tamas at order168.

Next, inspect frequency-by-frequency residuals and determine which AC bands dominate the transfer L2 score; then compare those bands with the pulse spectrum and timing. This may clarify why the Tamas AC residual penalty does not appear in the pulse NRMSE. It is still not a causal or biological conclusion.

## 8. Scientific limits

This is passive linear-RC numerical transfer validation on two individual morphologies, not active-neuron or biological validation and not a population study. Full Hines remains canonical. No production code or solver defaults were changed.

## 9. Reproducible outputs

Result stem: `prima_q25_krylov_transfer_stages_cross_morphology_2026-11-24`.

- `snapshots.csv`: 504 rows.
- `by_output_model.csv`: 10,584 rows.
- `frequency.csv`: 95,256 rows.
- `by_output_summary.csv`: 1,176 rows.
- `by_source_summary.csv`: 168 rows.
- `report.json` and `.time.txt`.

Verified Git blob SHA-1:
- report JSON: `1c4ac637390d9d2fcecd0829f36f3ccee6b6fb05`
- snapshots: `b53142daaba630d3a7e3415e124c3d77f0f4bb3a`
- by-output-model: `988003ad94fe20157d6ceb0415de72d0466cf479`
- frequency: `e41a8ad72aec0b8865f66e7077a4a8074ee1c62f`
- by-output summary: `9f1042f9cd5efc4883cbb4505900c6c117fcf8e4`
- by-source summary: `735530023dd07dd344653891f2fad15cc0968041`
- timing: `84753b35e4d0c94a48401edb209b2306d4dc31c9`
