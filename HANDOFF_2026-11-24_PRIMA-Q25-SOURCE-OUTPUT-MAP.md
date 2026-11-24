# Handoff — Cross-morphology PRIMA q25 source/output residual map

**Date:** 24 November 2026  
**Branch:** research/prima-q25-source-output-cross-morphology-map-2026-11-24  
**Parent:** Krylov growth audit branch / PR #22

## Research question

Where do the dual-q25 shared-output transient residual changes occur when measured against the seven-port baseline, and does the source/output pattern differ between the Peng mouse and Tamas human pyramidal reconstructions?

## Data and design

This deterministic post-processing audit consumes the already validated matched shared-output CSVs from both four-layout q25 experiments. It groups each matched pair by morphology, candidate layout, basis order, input source and shared output node/role. Each output-port group contains nine passive scenarios × two pulse widths = 18 pairs; each source summary aggregates seven outputs = 126 pairs.

Expected coverage:
- 2,268 matched rows per morphology (4,536 total).
- 252 source/layout/order/output groups.
- 36 source/layout/order summary groups.
- Worst 50 output-group medians retained separately.

## Scientific constraints

Ratios divide candidate NRMSE by the seven-port NRMSE and can be large when the denominator is already extremely small. Keep absolute NRMSE beside ratios. The result localizes numerical residual patterns only; two individual passive morphologies do not establish a population, biological effect or causal mechanism. Full Hines remains canonical.
