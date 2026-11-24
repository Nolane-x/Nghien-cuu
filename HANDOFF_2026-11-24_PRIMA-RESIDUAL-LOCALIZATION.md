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
