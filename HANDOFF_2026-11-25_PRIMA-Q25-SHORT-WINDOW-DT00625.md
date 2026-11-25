# Handoff — PRIMA q25 short-window refinement at 0.00625 ms

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-dt00625-2026-11-25\`  
**Parent:** PR #32, fine-step convergence through 0.0125 ms

## Question

Do the 20/40-ms q25 nine/seven transient ratios stabilize when dt is reduced to 0.00625 ms?

## Method

- Same two pinned morphologies, nine parameter scenarios, two layouts, three input sources, seven shared output nodes and two pulse widths.
- Restrict windows to 20 and 40 ms; use dt 0.1/0.05/0.025/0.0125/0.00625 ms.
- Keep the continuous-time order-168 PRIMA basis fixed; refactorize reduced BE systems per timestep.
- Use full-Hines perturbation coordinates as the primary reference; compare coarse full-Hines traces against dt 0.00625 at matching sample-end times.
- Preserve canonical absolute-voltage Hines as a round-off diagnostic.

## Expected coverage

15,120 metrics; 7,560 paired seven/nine comparisons; 120 source summaries; 20 morphology/window summaries; 6,048 Hines temporal rows; 16 Hines temporal summaries.

## Execution status

Implementation and focused tests are authored. Full computation is pending Actions; no numerical conclusion is accepted before tests, checksums, preflights, full calculation, CSV read-backs, commit and artifact upload pass.

## Limits

Only two passive morphology instances. The finest timestep is a numerical reference, not exact continuum truth. No production solver/default is changed.
