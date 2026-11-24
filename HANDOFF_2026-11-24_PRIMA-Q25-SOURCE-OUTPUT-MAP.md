# Handoff — Cross-morphology PRIMA q25 source/output residual map

**Date:** 24 November 2026  
**Branch:** research/prima-q25-source-output-cross-morphology-map-2026-11-24  
**Parent:** Krylov growth audit branch / PR #22  
**Successful workflow:** [45335931927](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927)  
**Result commit:** `53432caa24358ce32e7a008bd21144aa0f682f0b`  
**Detailed report:** [PRIMA_Q25_SOURCE_OUTPUT_CROSS_MORPHOLOGY_MAP_2026-11-24.md](amsn-core/research/PRIMA_Q25_SOURCE_OUTPUT_CROSS_MORPHOLOGY_MAP_2026-11-24.md)

## Research question

Where do the dual-q25 shared-output transient residual changes occur when measured against the seven-port baseline, and does the source/output pattern differ between the Peng mouse and Tamas human pyramidal reconstructions?

## Verified data and coverage

This is deterministic post-processing of the already validated matched transient CSVs; no solver rerun. Both morphology inputs contain exactly 2,268 matched rows (4,536 total). The aggregation produces 252 source/output/layout/order groups, 36 source/layout/order groups and the 50 highest output-group median ratios.

The five aggregation tests passed. The corrected workflow also verified both input files, ran the full mapping, committed four generated files and uploaded the artifact.

Artifact: [prima-q25-source-output-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45335931927/artifacts/14893173225), SHA-256 `8dfc9451c7b7a6feb69d8ac9920b4cc6d6e0eda1bef098a2fce6decabbb76fee`.

## Main result — dual-q25, basis order 168

Each source summary aggregates all seven shared output ports and 126 matched pairs (nine passive scenarios × two pulse widths × seven outputs). The ratio shown is the median of the seven output-group median error ratios.

| Morphology | Input source | Median output-group ratio | Worse / better pairs | Median baseline NRMSE (%) | Median dual-q25 NRMSE (%) |
|---|---|---:|---:|---:|---:|
| Peng mouse | Soma | 92.509× | 126 / 0 | 6.400e-10 | 3.454e-8 |
| Peng mouse | Basal-q75 | 69.370× | 126 / 0 | 5.284e-10 | 9.179e-9 |
| Peng mouse | Apical-q75 | 1.847× | 99 / 27 | 2.372e-9 | 6.985e-9 |
| Tamas human pyramidal | Soma | 1.022× | 87 / 39 | 2.019e-8 | 2.446e-8 |
| Tamas human pyramidal | Basal-q75 | 1.0005× | 68 / 58 | 3.563e-8 | 3.574e-8 |
| Tamas human pyramidal | Apical-q75 | 0.9988× | 59 / 67 | 4.850e-8 | 4.840e-8 |

The Peng penalty is strongly input-source dependent: soma and basal-q75 stimulation make all 126 shared-output comparisons worse at order 168; apical-q75 stimulation is much less affected. On the Tamas sample, source-level results remain close to baseline for all three source sites.

Ratios are relative to a very small seven-port error and must be read beside the absolute NRMSE. For example, the largest absolute dual-q25 NRMSE at order 168 is 6.066e-7% on Peng and 5.456e-7% on Tamas. These remain small absolute numerical errors.

## Shared output identities pinned

Peng: soma 1; basal-q75 144; apical-q75 3926; apical-q90 3948; apical-q50 4104; basal-q50 4180; basal-q90 40.

Tamas: soma 1; basal-q75 6363; apical-q75 4735; basal-q50 5564; basal-q90 7023; apical-q50 4301; apical-q90 4623.

## Interpretation limits

This localizes the numerical residual pattern by input and output, but does not explain its mechanism. Two individual passive linear-RC morphology reconstructions are not species or cell-class populations. The error ratio denominator is the seven-port NRMSE and can be extremely small. No biological claim, active-neuron validation or production default change follows from this map. Full Hines remains canonical.
