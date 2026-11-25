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

Workflow [45428685906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906) completed successfully. **15/15 tests passed**; both SWC hashes and NEURON preflights passed; full calculation, six CSV read-backs, result commit and artifact upload passed.

- Read-back: 24,192 metrics; 12,096 paired comparisons; 192 source summaries; 32 morphology × timestep × window summaries; 9,072 Hines coarse/fine rows; 24 Hines convergence summaries.
- Runtime: 388.44 s; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.
- Result commit \`d79ca743cbb662bf4536b28c527bfa5234058c15\`.
- Artifact [14937828066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906/artifacts/14937828066), SHA-256 \`9fae812ff71e2a6a0c8920495d7e990830a0f116843fadfbd20e84fa924e498f\`.
- Maximum absolute-vs-perturbation Hines trace delta: \(7.6328\times10^{-8}\%\).

## Limits and next step

The 0.0125-ms Hines waveform is a finer numerical reference, not an analytic continuous-time solution. Only two individual passive morphologies. After CI, inspect whether the 0.025-to-0.0125 discrepancy preserves the expected ratio and whether the 20/40-ms q25 ratios converge. No production defaults are changed.


## Validated four-step results

The median nine/seven perturbation-coordinate transient ratios (20/40/100/200-ms windows) are:

| Morphology | dt 0.1 ms | dt 0.05 ms | dt 0.025 ms | dt 0.0125 ms |
|---|---|---|---|---|
| Tamas | 24.44 / 55.24 / 31.87 / 31.64× | 26.59 / 57.04 / 31.73 / 31.59× | 27.05 / 54.85 / 31.72 / 31.59× | 26.55 / 49.91 / 32.05 / 31.84× |
| Peng | 138.24 / 70.09 / 33.67 / 33.43× | 130.11 / 67.68 / 33.62 / 33.42× | 123.68 / 63.89 / 33.64 / 33.46× | 118.81 / 64.98 / 33.62 / 33.45× |

At 100–200 ms, the ratio stays within about 0.6% for Tamas and 0.2% for Peng across the entire grid. The 20–40-ms ratio remains timestep-sensitive: Peng falls by about 14% at 20 ms and 7% at 40 ms from dt 0.1 to 0.0125; Tamas at 40 ms remains non-monotonic and changes from 54.85× to 49.91× between 0.025 and 0.0125 ms.

Full-Hines coarse-vs-0.0125-ms median NRMSE:
- Tamas: dt 0.1 = 0.632–0.682%; 0.05 = 0.275–0.296%; 0.025 = 0.094–0.100%.
- Peng: dt 0.1 = 0.613–0.685%; 0.05 = 0.265–0.296%; 0.025 = 0.089–0.099%.

Adjacent ratios are ~2.30–2.32 for 0.1 vs 0.05 and ~2.94–2.96 for 0.05 vs 0.025. With the fixed 0.0125-ms reference, first-order BE geometry predicts 2.33 and 3. This is strong evidence of first-order convergence over this range. The remaining 0.025-vs-0.0125 difference is still around 0.09–0.10% median, so the 0.0125-ms waveform is only a finer reference, not continuum truth.

The next work should focus on 20–40-ms windows with dt 0.00625 ms and explicit decomposition of periodic transfer and terminal-state boundary terms. Long-window ratios are already stable; full all-window refinement has diminishing value. No production solver/default was changed.
