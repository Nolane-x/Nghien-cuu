# PRIMA q25 Krylov-prefix source-to-output transfer audit

**Date:** 24 November 2026  
**Workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089) — success  
**Result commit:** `83ccc27d21d87e1a50a2ad48414958fe62a4c63e`  
**Artifact:** [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14894466250)  
**Artifact SHA-256:** `6f11321129aa05bc6208e67723fd211f7d4723c85138ea80e879eb25c7313026`

## 1. Question and method

Does the morphology-dependent Krylov novelty observed previously change the actual source-to-output AC transfer responses as the basis grows?

For NMO_163775 Peng mouse and NMO_107159 Tamas human pyramidal Control, this audit uses four layouts (7, basal-only 8, apical-only 8 and dual-q25 9), orders 112/168, nine passive scenarios, six shifts, nine AC frequencies (0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz), three current sources and seven exact shared SWC output nodes.

At each prefix (seed and after each completed round-robin Krylov round), it projects passive G/C, computes reduced complex transfer responses and compares them with full Hines for the exact same morphology, scenario, layout, source and frequency. The final instrumented basis is compared with the unmodified production builder, and final projected matrices are checked against production.

## 2. Validation

| Dataset | Expected | Verified |
|---|---:|---:|
| Prefix snapshots | 504 | 504 |
| Per-scenario source/output summaries | 10,584 | 10,584 |
| Frequency/source/output rows | 95,256 | 95,256 |
| Scenario-aggregated output summaries | 1,176 | 1,176 |
| Source summaries | 168 | 168 |

Five focused tests passed. Both pinned SWC hashes and Import3D preflights passed. The final instrumented basis differed from production by exactly 0.0 maximum absolute entry error across all models; max orthogonality error was 2.22e-15. Final reduced G/C matrices also passed production parity guards.

Runtime: 220.51 seconds wall, 308.03 seconds user CPU, 300,248 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## 3. Transfer error falls strongly with each Krylov prefix

For dual-q25 at basis order 168, the median across the three sources of the median complex transfer L2 error over seven shared outputs is:

| Prefix | Peng mouse | Tamas human pyramidal |
|---|---:|---:|
| Seed (54 basis vectors) | 7.788e-2% | 1.848e-2% |
| After round 1 (108) | 4.427e-5% | 6.521e-6% |
| After round 2 (162) | 7.466e-8% | 1.065e-8% |
| After round 3 / final order 168 | 2.140e-8% | 2.638e-9% |

Every Krylov round substantially improves the median transfer approximation on both morphologies.

## 4. Final dual-q25 AC transfer error versus seven-port, order 168

The ratio below is the median of seven paired output-node ratios, each ratio comparing the output-specific median transfer L2 error for dual-q25 with the corresponding seven-port error. All seven output groups are worse for dual-q25 in every source/morphology row below.

| Morphology | Source | Median dual-q25 / seven transfer-error ratio | Output groups worse |
|---|---|---:|---:|
| Peng mouse | Soma | 53.32× | 7/7 |
| Peng mouse | Basal-q75 | 52.01× | 7/7 |
| Peng mouse | Apical-q75 | 43.07× | 7/7 |
| Tamas human pyramidal | Soma | 23.06× | 7/7 |
| Tamas human pyramidal | Basal-q75 | 8.60× | 7/7 |
| Tamas human pyramidal | Apical-q75 | 6.70× | 7/7 |

Corresponding source-level median dual-q25 transfer L2 error values remain very small:

| Morphology | Soma | Basal-q75 | Apical-q75 |
|---|---:|---:|---:|
| Peng | 7.281e-8% | 2.140e-8% | 8.792e-9% |
| Tamas | 7.902e-9% | 2.638e-9% | 2.298e-9% |

These are relative errors in a unit-current AC transfer calculation; large ratios partly reflect the very small seven-port denominator.

## 5. Eight-port comparison at final order 168

Median source-level complex transfer L2 error (%) across the seven shared outputs:

| Morphology | Source | Seven | Basal-q25 8 | Apical-q25 8 | Dual-q25 9 |
|---|---|---:|---:|---:|---:|
| Peng | Soma | 1.366e-9 | 1.757e-9 | 3.795e-9 | 7.281e-8 |
| Peng | Basal-q75 | 4.115e-10 | 5.628e-10 | 1.120e-9 | 2.140e-8 |
| Peng | Apical-q75 | 2.041e-10 | 2.647e-10 | 5.005e-10 | 8.792e-9 |
| Tamas | Soma | 3.427e-10 | 5.387e-10 | 5.195e-10 | 7.902e-9 |
| Tamas | Basal-q75 | 3.069e-10 | 4.455e-10 | 4.238e-10 | 2.638e-9 |
| Tamas | Apical-q75 | 3.431e-10 | 3.873e-10 | 3.858e-10 | 2.298e-9 |

Dual-q25 has the largest AC transfer residual in every source/morphology comparison shown. The absolute relative-L2 transfer errors remain extremely small.

## 6. Order-112 comparison

At the final order-112 prefix, dual-q25/seven transfer ratios are elevated on both morphologies:

| Morphology | Soma | Basal-q75 | Apical-q75 |
|---|---:|---:|---:|
| Peng | 40.21× | 40.21× | 37.75× |
| Tamas | 39.79× | 40.19× | 35.33× |

This is consistent with the earlier order-112 time-domain transient degradation on both samples.

## 7. Why AC and transient results must remain separate

The earlier order-168 matched pulse experiment found a dual-q25 median shared-output transient NRMSE ratio of 14.525× on Peng but only 1.001× on Tamas. The current AC transfer audit finds dual-q25 transfer error above seven-port on both morphologies (more strongly on Peng).

These are not the same measurement. AC transfer error is a complex L2 comparison across nine discrete frequencies; transient NRMSE is computed on time-domain pulse traces. Frequency errors can be weighted and combined differently by the pulse waveform and observation window. The Tamas difference is a signal to study frequency weighting, not grounds to dismiss either result.

## 8. Interpretation and next step

The audit establishes that:
1. Transfer residuals fall by several orders of magnitude as Krylov vectors are added.
2. The final dual-q25 AC transfer error remains above seven-port at all seven shared outputs for all three source sites on both morphologies.
3. The relative penalty is larger on Peng, but absolute relative transfer errors remain very small.
4. The AC result and time-domain pulse result differ most clearly on Tamas at order 168.

Next, inspect frequency-by-frequency residuals and determine which AC bands dominate the transfer L2 score; compare those bands with the pulse spectrum and exact pulse timing. This may clarify why the Tamas AC residual penalty does not appear in its pulse NRMSE. This is not yet a causal or biological conclusion.

## 9. Scientific limits

This is passive linear-RC numerical transfer validation on two individual morphologies, not active-neuron or biological validation and not a population study. Full Hines remains canonical. No production code or solver defaults were changed.

## 10. Reproducible outputs

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
