# Research log — PRIMA q25 backward-Euler timestep refinement

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-timestep-refinement-2026-11-24\`  
**Parent checkpoint:** PR #30 exact discrete-transfer audit

## Question

Does the stable seven/nine-port transient error ratio change with backward-Euler timestep, and how much time-discretization error remains in the full-Hines reference?

## Sources examined

- \`AGENTS.md\`, root \`HANDOFF.md\`, research dossier and latest q25 handoffs.
- PR #30 exact backward-Euler transfer report and committed eight-row morphology/window summary.
- Exact Hines backward-Euler kernel, reduced factorized recurrence, morphology preflight and layout construction from the validated q25 audits.

## Implementation

Added a full-Hines / seven-port / dual-q25 nine-port timestep-refinement replay for 0.1/0.05/0.025 ms. It holds the order-168 continuous-time projection basis fixed across \(\Delta t\), and computes the transient residual in perturbation coordinates. The absolute-voltage full-Hines trace is retained to quantify coordinate cancellation. Full-Hines coarse traces are compared with the finest 0.025-ms Hines reference at common sample-end times.

## Execution record

Pending GitHub Actions. The workflow pins Python 3.12, NEURON 9.0.2 and SciPy 1.16.3; it verifies both SWC hashes, both morphology preflights, focused tests, full-matrix computation and exact CSV read-back. No result is claimed before completion.

## Expected output

- Per-layout transient metrics and paired seven/nine-port comparisons for every morphology/scenario/source/output/pulse/window/timestep.
- Six-source/pulse groups and morphology/window summaries.
- Full-Hines temporal-convergence output for both coarse timesteps against 0.025 ms.
- Runtime, versions and provenance in report JSON.

## Limits and next step

The 0.025-ms run is a numerical reference, not an analytic solution. Only two passive morphologies. After CI, inspect timestep sensitivity separately for absolute model error and nine/seven ratio; do not change production defaults based on this limited study.
