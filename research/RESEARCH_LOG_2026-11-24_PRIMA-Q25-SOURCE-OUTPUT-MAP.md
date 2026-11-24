# Research log — Cross-morphology PRIMA q25 source/output residual map

**Date:** 24 November 2026  
**Branch:** research/prima-q25-source-output-cross-morphology-map-2026-11-24  
**Successful workflow:** [45335931927](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927)  
**Result commit:** `53432caa24358ce32e7a008bd21144aa0f682f0b`

## Motivation

The prior q25 experiments show a large dual-q25 order-168 penalty on Peng but near-baseline behavior on Tamas. This analysis localizes that contrast by input-source location and shared output port, instead of collapsing all 378 comparisons per candidate layout/order into one median.

## Method

The analysis uses the already archived `matched_shared_vs_seven.csv` from both morphologies. It validates:
- exact 2,268 matched rows per morphology (4,536 total);
- finite positive error ratios and non-negative NRMSE values;
- unique source/output/layout/order/scenario/pulse identities;
- exact pinned seven shared output node/role pairs for each morphology;
- expected candidate port counts (8/8/9).

It summarizes by morphology × candidate layout × basis order × input source × shared output port. Each output group contains 18 values (nine passive scenarios × two pulse widths). Each source group aggregates seven outputs, or 126 matched values.

## Execution and coverage

- Workflow [45335931927](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927): **success**.
- Tests: 5 passed.
- 4,536 matched input rows read.
- 252 output groups and 36 source groups generated.
- Top 50 worst output-group medians preserved.
- Result commit: `53432caa24358ce32e7a008bd21144aa0f682f0b`.
- Artifact: [prima-q25-source-output-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927/artifacts/14893173225), SHA-256 `8dfc9451c7b7a6feb69d8ac9920b4cc6d6e0eda1bef098a2fce6decabbb76fee`.

## Findings — dual-q25 at order 168

The source summary is the median across seven shared output-port group medians. Pair counts and worse/better signs aggregate all seven outputs × nine scenarios × two pulse widths.

| Morphology | Source | Median output-group ratio | Worse / better pairs | Median baseline NRMSE (%) | Median candidate NRMSE (%) |
|---|---|---:|---:|---:|---:|
| Peng | Soma | 92.509× | 126 / 0 | 6.400e-10 | 3.454e-8 |
| Peng | Basal-q75 | 69.370× | 126 / 0 | 5.284e-10 | 9.179e-9 |
| Peng | Apical-q75 | 1.847× | 99 / 27 | 2.372e-9 | 6.985e-9 |
| Tamas | Soma | 1.022× | 87 / 39 | 2.019e-8 | 2.446e-8 |
| Tamas | Basal-q75 | 1.0005× | 68 / 58 | 3.563e-8 | 3.574e-8 |
| Tamas | Apical-q75 | 0.9988× | 59 / 67 | 4.850e-8 | 4.840e-8 |

The Peng difference concentrates in soma and basal-q75 stimulation; in those two source conditions all 126 paired shared-output errors worsen. Apical-q75 is less affected. Tamas remains close to the seven-port baseline under all three sources; apical-q75 has slightly more better than worse pairs.

These relative ratios must not be mistaken for large absolute errors. Maximum dual-q25 transient NRMSE at order 168 is 6.066e-7% for Peng and 5.456e-7% for Tamas.

## Interpretation

The source/output map narrows the Peng anomaly to soma and basal-q75 input sources, rather than a uniform global deterioration across all three source sites. The Tamas human pyramidal morphology does not exhibit the same source-specific penalty. This supports a morphology-by-input-location interaction in the present passive numerical experiments, not a biological mechanism or population-level rule.

## Files

- `amsn-core/research/analyze_prima_q25_cross_morphology_source_output.py`
- `amsn-core/tests/test_prima_q25_cross_morphology_source_output.py`
- `.github/workflows/amsn-prima-q25-source-output-map.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-SOURCE-OUTPUT-MAP.md`
- Detailed report: `amsn-core/research/PRIMA_Q25_SOURCE_OUTPUT_CROSS_MORPHOLOGY_MAP_2026-11-24.md`
- Result CSVs: `by_output.csv`, `by_source.csv`, `worst_output_groups.csv`; JSON report, all under `amsn-core/results/prima_q25_source_output_cross_morphology_2026-11-24_*`.

## Limits

The ratio denominator is the seven-port NRMSE and may be extremely small. Keep absolute values visible. This is two individual passive linear-RC morphology reconstructions, not biological/population validation. Full Hines remains canonical; no production default changes.
