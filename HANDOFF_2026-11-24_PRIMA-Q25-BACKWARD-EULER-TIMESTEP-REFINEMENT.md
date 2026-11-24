# Handoff — PRIMA q25 backward-Euler timestep refinement

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-timestep-refinement-2026-11-24\`  
**Parent:** PR #30 exact discrete-transfer audit

## Question

Does the q25 nine/seven transient error penalty remain stable at backward-Euler timesteps 0.1/0.05/0.025 ms, and how rapidly does the full-Hines reference itself converge in time?

## Method

- Keep the same two checksum-pinned morphologies, nine passive scenarios, 7/9-port layouts, order 168, three sources, seven shared outputs, two pulse widths and four windows.
- Rebuild the reduced BE factorization for each timestep, keeping the same continuous-time PRIMA projection basis for a given morphology/scenario/layout.
- Use full-Hines perturbation-coordinate traces as the primary reference; retain absolute-voltage full Hines as a round-off diagnostic.
- Compare coarse full-Hines traces to the 0.025-ms trace sampled at identical end-of-step times.
- Record per-output metrics, paired nine/seven ratios, source summaries, morphology/window summaries and full-Hines temporal-convergence summaries.

## Execution status

Implementation and focused tests are authored. The full matrix is pending GitHub Actions. No new timestep-convergence result is accepted until the tests, preflights, calculation, exact row-count read-back, artifact upload and result commit all pass.

## Scientific limits

The 0.025-ms run is a finer numerical reference, not an analytic continuous-time solution. Only two individual passive linear-RC morphologies are tested. No production solver/default is changed; full Hines remains canonical.
