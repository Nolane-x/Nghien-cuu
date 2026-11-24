# Research log — PRIMA q25 backward-Euler fine-step convergence

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-fine-step-convergence-2026-11-24\`  
**Parent checkpoint:** PR #31 timestep refinement through 0.025 ms

## Question

Does backward-Euler full-Hines temporal convergence continue to behave approximately first-order down to 0.0125 ms, and do the short-window q25 seven/nine transient ratios stabilize?

## Sources examined

- PR #31 report, handoff, research log and committed timestep-refinement CSVs.
- Exact Hines backward-Euler kernel, reduced factorized recurrence, morphology preflights and four-layout construction.
- Parent study found full-Hines coarse-vs-0.025-ms median NRMSE around 0.52–0.59% at dt 0.1 ms and 0.176–0.197% at dt 0.05 ms, with a discrepancy ratio around 2.9–3.0.

## Implementation

Extended the timestep grid to 0.1/0.05/0.025/0.0125 ms. Kept order-168 PRIMA bases fixed for each morphology/scenario/layout; refactorized reduced backward-Euler matrices at each dt. The new finest full-Hines perturbation trace is used to compare all coarser Hines traces at identical sample-end times and to report seven/nine PRIMA errors at the finer step.

## Expected output

- 24,192 layout-level transient metrics.
- 12,096 paired seven/nine comparisons.
- 192 source × pulse × window summaries.
- 32 morphology × timestep × window summaries.
- 9,072 Hines temporal-convergence rows.
- 24 Hines temporal-convergence summaries.
- Runtime/version/provenance JSON and full CSV read-back.

## Execution record

Pending GitHub Actions. Both morphology hashes, preflights, focused tests and all exact output counts must pass. Do not infer the new fine-step result from the parent study.

## Limits and next step

The 0.0125-ms Hines waveform is a finer numerical reference, not an analytic continuous-time solution. Only two individual passive morphologies. After CI, inspect whether the 0.025-to-0.0125 discrepancy preserves the expected ratio and whether the 20/40-ms q25 ratios converge. No production defaults are changed.
