# Handoff — PRIMA residual localization

**Date:** 24 November 2026  
**Branch:** research/prima-residual-localization-2026-11-24  
**Base:** research/prima-cross-morphology-synthesis-2026-11-24  
**Base commit:** 2fdd6a29a9fa5600187076344defdf731b7bb400

## Purpose

Decompose the matched 7-port/9-port transient NRMSE ratios by stimulation source, shared output role, source/output pair, pulse width and passive parameter scenario. The immediate target is the NMO_163775 order-168 result, where the overall median 9/7 ratio is 14.501×.

This branch only analyzes already archived paired CSV data. It does not rerun NEURON or change the solver.

## Integrity rules

- Pair keys include basis order, parameter scenario, source, pulse width and exact shared SWC node ID.
- Recompute e9/e7 and e9-e7; reject inconsistent stored values, duplicates, non-finite metrics and zero denominators.
- Require 378 rows per order for each morphology: nine scenarios × three sources × two pulse widths × seven common output nodes.
- Report paired ratios together with seven-port and nine-port absolute NRMSE values.
- Treat group medians as descriptive; do not infer a causal mechanism from this deterministic factorial.

## Files

- amsn-core/research/analyze_prima_matched_residuals.py
- amsn-core/tests/test_prima_matched_residuals.py
- .github/workflows/amsn-prima-residual-localization.yml
- Generated Markdown: amsn-core/research/PRIMA_MATCHED_RESIDUAL_DIAGNOSTICS_2026-11-24.md
- Generated CSV: amsn-core/results/prima_matched_residual_diagnostics_2026-11-24.csv

The generated report and CSV are not considered validated until the branch workflow succeeds and the files are read back from GitHub.

## Next experiment

Run a four-layout ablation on the same morphology and mesh: seven canonical ports, seven plus basal-q25, seven plus apical-q25, and seven plus both q25. Keep basis order, shifts, passive scenarios, sources, pulse widths, dt and full-Hines shared output references matched. This distinguishes whether either added probe is sufficient to reproduce the observed trade-off. Do not promote an order or layout without an explicit absolute-error acceptance criterion.


## Validated checkpoint — workflow 45326438648

The residual-localization workflow completed successfully on 24 November 2026.

- Focused regression suite: 7/7 tests passed.
- Generator wrote the Markdown decomposition report and source/output summary CSV.
- Deterministic check confirmed both generated outputs match the four archived paired datasets.
- Workflow run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326438648
- Generated-output commit: 4f0408af2db59f83c5ed1041ce5f1c531a3a6220.
- Report blob SHA: d134dc69693b9f2e8eb2b453466330400bad6317.
- CSV blob SHA: 481ad73e9948b192e74097c0262be60308a50908.

The report localizes the NMO_163775 order-168 relative penalty by input source and output role. For example, the median paired ratio is 113.558× for soma stimulation → soma output and 1.00460× for apical-q75 stimulation → apical-q75 output. The overall maximum nine-port shared-output NRMSE is 6.06567e-7%. These are descriptive numerical diagnostics; they do not establish a causal mechanism or biological effect.

The analyzer consumes previously validated CSVs only. No new NEURON simulation was run, and no production solver code/defaults changed.
