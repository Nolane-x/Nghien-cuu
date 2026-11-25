# PRIMA q25 short-window refinement at dt = 0.00625 ms

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-dt00625-2026-11-25\`  
**Parent:** PR #32, four-step convergence through 0.0125 ms  
**Execution:** pending GitHub Actions

## Research question

The 0.1/0.05/0.025/0.0125-ms sweep showed stable 100–200-ms nine/seven ratios but material variation at 20–40 ms. This targeted audit asks whether the short-window relative reduction-error ratios stabilize when dt is reduced to 0.00625 ms.

## Scope

- Same checksum-pinned NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Seven-port and dual-q25 nine-port PRIMA layouts, order 168, fixed continuous-time projection basis per morphology/scenario/layout.
- Nine passive parameter scenarios, three current sources, seven shared SWC outputs, two pulse widths.
- Observation windows restricted to 20 and 40 ms.
- Timestep grid 0.1/0.05/0.025/0.0125/0.00625 ms.
- Full Hines perturbation-coordinate trace at 0.00625 ms is the finer reference; coarser traces are aligned at common end-of-step times.

## Expected coverage

- 15,120 layout-level metrics.
- 7,560 paired seven/nine-port comparisons.
- 120 source × pulse × window summaries.
- 20 morphology × timestep × window summaries.
- 6,048 full-Hines temporal-convergence rows.
- 16 temporal-convergence summary rows.

## Validation

The workflow checks both SWC hashes and morphology preflights, runs focused tests for timestep alignment and pulse charge, executes the complete matrix, and requires exact row-count read-back from all six CSV files.

**Execution status:** pending. No 0.00625-ms conclusion is claimed before the complete workflow passes.

## Interpretation limits

The 0.00625-ms full-Hines trace is a finer numerical reference, not an exact continuous-time solution. Only two passive linear-RC morphologies are included. The PRIMA projection basis/order stay fixed to isolate temporal discretization sensitivity. Full Hines remains canonical; no production solver/default is changed.
