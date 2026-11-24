# PRIMA q25 source/output cross-morphology residual map

**Date:** 24 November 2026  
**Workflow:** [45335931927](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927) — success  
**Result commit:** `53432caa24358ce32e7a008bd21144aa0f682f0b`  
**Artifact:** [prima-q25-source-output-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927/artifacts/14893173225)  
**Artifact SHA-256:** `8dfc9451c7b7a6feb69d8ac9920b4cc6d6e0eda1bef098a2fce6decabbb76fee`

## 1. Aim

The Peng mouse four-layout q25 ablation showed a large dual-q25 shared-output error ratio at basis order 168, while the independent Tamas human pyramidal replication was close to seven-port baseline. This post-processing analysis localizes the difference by the location where current is injected and the shared output node being measured.

No solver rerun occurs here. Inputs are the already validated matched shared-output CSVs from the two four-layout experiments.

## 2. Exact coverage and method

| Dataset | Expected | Verified |
|---|---:|---:|
| Peng matched shared-output pairs | 2,268 | 2,268 |
| Tamas matched shared-output pairs | 2,268 | 2,268 |
| Total matched pairs | 4,536 | 4,536 |
| Output-port groups | 252 | 252 |
| Input-source groups | 36 | 36 |
| Highest output-group median ratios retained | 50 | 50 |

Five aggregation tests passed. The script verifies finite positive ratios, non-negative NRMSE, unique row identities, exact shared node/role maps and candidate port counts.

Each output group has 18 matched values (nine passive parameter scenarios × two pulse widths). Each source group aggregates seven shared output ports, totalling 126 values.

## 3. Dual-q25 results at basis order 168

The median ratio is the median across the seven output-port group medians for that source. The worse/better counts aggregate all 126 pairs in the source group.

| Morphology | Input source | Median output-group ratio | 90th percentile | Worse / better pairs | Median baseline NRMSE (%) | Median dual-q25 NRMSE (%) |
|---|---|---:|---:|---:|---:|---:|
| Peng mouse | Soma | 92.509× | 104.723× | 126 / 0 | 6.400e-10 | 3.454e-8 |
| Peng mouse | Basal-q75 | 69.370× | 80.364× | 126 / 0 | 5.284e-10 | 9.179e-9 |
| Peng mouse | Apical-q75 | 1.847× | 2.832× | 99 / 27 | 2.372e-9 | 6.985e-9 |
| Tamas human pyramidal | Soma | 1.022× | 1.110× | 87 / 39 | 2.019e-8 | 2.446e-8 |
| Tamas human pyramidal | Basal-q75 | 1.0005× | 1.006× | 68 / 58 | 3.563e-8 | 3.574e-8 |
| Tamas human pyramidal | Apical-q75 | 0.9988× | 1.0004× | 59 / 67 | 4.850e-8 | 4.840e-8 |

The strongest Peng penalty is under soma stimulation, closely followed by basal-q75 stimulation. In both source conditions, every shared-output pair is worse than the seven-port baseline. Apical-q75 stimulation is substantially less affected. On Tamas, all three source-level median ratios are near one; apical-q75 stimulation produces slightly more improved than worsened pairs.

## 4. Absolute error context

The relative ratios are large partly because the seven-port denominator is already extremely small. Absolute NRMSE remains small:

- Peng, dual-q25 order168, largest transient NRMSE across the full layout: 6.066e-7%.
- Tamas, dual-q25 order168: 5.456e-7%.

The source map therefore shows where relative degradation appears, not a large absolute voltage failure.

## 5. Shared output node identities

Peng shared outputs:

| SWC node | Output role |
|---:|---|
| 1 | soma |
| 144 | basal-q75 |
| 3926 | apical-q75 |
| 3948 | apical-q90 |
| 4104 | apical-q50 |
| 4180 | basal-q50 |
| 40 | basal-q90 |

Tamas shared outputs:

| SWC node | Output role |
|---:|---|
| 1 | soma |
| 6363 | basal-q75 |
| 4735 | apical-q75 |
| 5564 | basal-q50 |
| 7023 | basal-q90 |
| 4301 | apical-q50 |
| 4623 | apical-q90 |

These identities are pinned against the archived seven-port node mappings; pairing uses exact SWC node IDs rather than array position.

## 6. Interpretation

The source/output map localizes the Peng dual-q25 order-168 anomaly to soma and basal-q75 injection in this one mouse reconstruction. The independent Tamas human pyramidal morphology remains near baseline under all three input source locations. Together with the earlier conditioning audit, the results support a morphology-by-input-location interaction in the tested passive numerical settings.

This still does not prove the underlying mechanism. Basis orthogonality is preserved and initial shift blocks accept all port directions; later Krylov-growth diagnostics remain separate. Neither sample is a population and the result does not imply active-neuron or biological behavior.

## 7. Scientific limits

Both analyses are passive linear-RC numerical comparisons against the seven-port reduced-model baseline, with full Hines remaining the canonical reference in the underlying experiments. Error ratios can magnify a small baseline. No active conductances, synaptic dynamics, plasticity or biological validity are established. No production solver defaults were changed.

## 8. Reproducible files

Result stem: `prima_q25_source_output_cross_morphology_2026-11-24`

- `by_output.csv`: 252 source/output/layout/order groups.
- `by_source.csv`: 36 source/layout/order summaries.
- `worst_output_groups.csv`: top 50 group medians.
- `report.json`: exact coverage and dual-q25 order-168 source summary.

Verified Git blob SHA-1:
- report JSON: `47dc215420c77a57987ca6ff6a583ec3c583a008`
- by-source CSV: `a9218de8c349fea5c15f21e988583836c9dac618`
- by-output CSV: `fd23236ea06e0d52702793438f8a79b130512908`
- worst-output CSV: `3f0d5bc15eb9feb7384893ff173b9dcd14f3b69e`
