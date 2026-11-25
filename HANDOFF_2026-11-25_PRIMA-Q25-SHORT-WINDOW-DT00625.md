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

## Current blocker — repeated short-window metrics differ

The original workflow [45551126065](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45551126065) passed all 18 tests and the full calculation. A same-commit rerun also passed, but its Hines temporal CSV was byte-identical while the reduced-model metric and ratio CSVs changed. This means the CI pass alone is not enough to accept the PRIMA short-window ratios as reproducible.

The observed maximum absolute change in perturbation NRMSE was about \(1.65\times10^{-10}\) percentage points, a small absolute change but material relative to the very small residuals. Do not claim a converged 20/40-ms 9/7 ratio from the first artifact alone.

The latest commit pins BLAS-related thread counts to one and adds reproducibility metadata: basis, reduced \(G/C\), input and trace digests plus NumPy/BLAS/threadpool configuration. Workflow runs [45552270328](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552270328) and [45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117) validate the changes. Next: compare the saved basis hashes and trace hashes across a repeated run of the final commit. Accept the ratios only if repeated hashes and CSV outputs match; otherwise isolate the first differing stage and keep the results provisional.

