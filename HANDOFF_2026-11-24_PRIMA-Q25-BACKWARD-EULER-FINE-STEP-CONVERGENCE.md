# Handoff — PRIMA q25 backward-Euler fine-step convergence

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-fine-step-convergence-2026-11-24\`  
**Parent:** PR #31, timestep refinement through 0.025 ms

## Question

Does the observed first-order full-Hines backward-Euler trend persist when refining the reference to 0.0125 ms, and do the short-window q25 nine/seven error ratios stabilize?

## Method

- Use dt 0.1 / 0.05 / 0.025 / 0.0125 ms.
- Same two checksum-pinned morphologies, nine passive scenarios, seven/nine-port layouts, order 168, three sources, seven outputs, two pulse widths and four windows.
- Keep the continuous-time PRIMA projection basis fixed across timesteps; refactorize reduced BE matrices separately for each dt.
- Use full-Hines perturbation-coordinate traces as the primary reference; retain canonical absolute-voltage Hines only as a round-off diagnostic.
- Compare dt 0.1 / 0.05 / 0.025 ms to the dt 0.0125-ms Hines trace at identical end-of-step times.

## Expected coverage

24,192 metrics; 12,096 paired seven/nine rows; 192 source summaries; 32 morphology/window summaries; 9,072 Hines temporal-comparison rows; 24 Hines temporal summaries.

## Execution status

Implementation and updated tests are authored. The full matrix is pending Actions; no numerical result is accepted until all test/preflight/computation/read-back/commit/artifact steps pass.

## Scientific limits

The 0.0125-ms run is a finer numerical reference, not an exact continuous-time solution. Only two passive linear-RC morphologies. No production solver/default is changed; full Hines remains canonical.
