# Handoff — PRIMA four-morphology synthesis

**Date:** 24 November 2026  
**Branch:** research/prima-cross-morphology-synthesis-2026-11-24  
**Base:** research/prima-tamas-human-pyramidal-fourth-morphology-2026-11-24  
**Base commit at branch creation:** 307264784e351aca4d59d05613d94da66f67c16e

## Purpose

Consolidate the matched 7-port/9-port PRIMA holdouts for NMO_162186, NMO_03524, NMO_163775 and NMO_107159. Build a reproducible integrity gate that reads each archived JSON report and its matched-summary, q25-summary and Hines CSV files, checks exact coverage and cross-file agreement, and generates one cross-morphology report plus CSV.

This branch is stacked on PR #17 and does not change main or alter AMSN production code.

## Current evidence

The four single-morphology workflows are recorded as successful:

- NMO_162186: run 45184621520
- NMO_03524: run 45198027785
- NMO_163775: run 45311916600
- NMO_107159: run 45314100588

Each report contains 36 model configurations, 324 AC rows, 1,728 transient rows, 756 matched shared-output pairs, 216 q25-only observations and 378 shared-Hines checks. The raw Hines CSVs each contain 378 rows with exact zero absolute trace difference and zero relative L2 difference.

The current cross-morphology result is conditional: at order 112, NMO_03524 is near parity while the other three have larger relative nine-port penalties. At order 168, three of four holdouts are near parity; NMO_163775 remains at a 14.5x median relative ratio, although its maximum nine-port shared-output NRMSE is below 1e-6 percent. Do not use the ratio without the absolute error.

## Mesh and biological limits

NMO_162186 and NMO_03524 use a 0.125 µm NEURON segment cap. NMO_163775 and NMO_107159 use 0.5 µm. Absolute cross-morphology errors and runtime are therefore not pooled. NMO_163775 metadata says No Diameter; the stored SWC radii are not measured diameters. NMO_107159 is a pyramidal comparison cell, not a rosehip interneuron.

All comparisons are passive linear-RC numerical validation against full Hines. They do not establish active-channel, nonlinear-synapse, plasticity or biological validity. Full Hines remains canonical; no production defaults change.

## New files

- amsn-core/research/synthesize_prima_cross_morphology.py
- amsn-core/tests/test_prima_cross_morphology_synthesis.py
- .github/workflows/amsn-prima-cross-morphology-synthesis.yml
- Generated report: amsn-core/research/PRIMA_CROSS_MORPHOLOGY_SYNTHESIS_2026-11-24.md
- Generated table: amsn-core/results/prima_cross_morphology_synthesis_2026-11-24.csv

The workflow is expected to run focused standard-library tests, generate both outputs from the archived files, check reproducibility and commit the generated report/table. The result files are not claimed as generated until the workflow run succeeds.

## Next experiments

1. Harmonize mesh resolution across at least one holdout from each existing mesh stratum, ideally with paired 0.125 µm and 0.5 µm runs on the same morphology.
2. Localize NMO_163775 order-168 residuals by port, source, pulse width and passive parameter scenario; report absolute errors and baseline denominators.
3. Separately assess recent hierarchical-matrix/Cable-BEM work if extracellular field coupling or multicellular ephaptic effects become an AMSN requirement. It is not directly comparable to the present cable PRIMA benchmark.

## Session integrity

No new NEURON simulation was run in this synthesis step. Only archived workflow outputs are read. Record the synthesis workflow run ID, resulting commit SHA and generated file hashes after CI completes.


## Validated synthesis checkpoint — GitHub Actions run 45317943578

The synthesis workflow completed successfully on 24 November 2026.

- Focused regression tests: **7/7 passed** under CPython 3.12.16.
- The generator wrote the cross-morphology Markdown report and CSV from the archived four-morphology reports/CSVs.
- The deterministic `--check` pass confirmed both generated files match the source datasets.
- The workflow committed the generated files in commit `fde2876cc6b2c808c306e93629de2a18510178ca`.
- Run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45317943578
- Generated report blob SHA: `916dfc523faa5e356dfc5626a6278634eb60b789`.
- Generated CSV blob SHA: `0e605ed5849f59f996007e68f68f06d60727189`.

The resulting synthesis covers 144 model configurations, 1,296 AC matrices, 6,912 transient rows, 3,024 shared-output pairs, 864 q25 observations and 1,512 exact shared-Hines checks. This consolidates previously successful single-morphology runs; it does not constitute a new NEURON simulation or biological validation.
