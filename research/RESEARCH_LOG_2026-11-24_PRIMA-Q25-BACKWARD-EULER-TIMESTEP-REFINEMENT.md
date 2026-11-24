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

Workflow [45426480184](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184) completed successfully. All **15 focused tests passed** in 0.51 s. Both SWC checksums, both morphology preflights, the full matrix, exact CSV read-back, result commit and artifact upload passed.

- Read-back: 18,144 metrics; 9,072 paired comparisons; 144 source summaries; 24 morphology/window summaries; 6,048 Hines temporal-comparison rows; 16 temporal-convergence summaries.
- Runtime: 213.66 s; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.
- Result commit \`8161b30e7a9ac3f62dcfb8754e08850a703f5ad3\`.
- Artifact [14934844995](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184/artifacts/14934844995), SHA-256 \`e8aeb6359f987a52040d38d28586185339654331c2d819334743cb1ee947e127\`.
- Maximum full-Hines absolute-vs-perturbation coordinate delta: \(7.6328\times10^{-8}\%\).

## Expected output

- Per-layout transient metrics and paired seven/nine-port comparisons for every morphology/scenario/source/output/pulse/window/timestep.
- Six-source/pulse groups and morphology/window summaries.
- Full-Hines temporal-convergence output for both coarse timesteps against 0.025 ms.
- Runtime, versions and provenance in report JSON.



## Validated timestep trends

The morphology/window summary gives the following median nine/seven transient ratios, ordered by 20/40/100/200-ms windows:

| Morphology | 0.1 ms | 0.05 ms | 0.025 ms |
|---|---|---|---|
| Tamas | 24.44 / 55.24 / 31.87 / 31.64× | 26.59 / 57.04 / 31.73 / 31.59× | 27.05 / 54.85 / 31.72 / 31.59× |
| Peng | 138.24 / 70.09 / 33.67 / 33.43× | 130.11 / 67.68 / 33.62 / 33.42× | 123.68 / 63.89 / 33.64 / 33.46× |

Nine-port NRMSE remains very small: \(2.85e{-9}\%\)–\(1.83e{-8}\%\) for Tamas and \(8.55e{-9}\%\)–\(8.22e{-8}\%\) for Peng. At 100–200 ms the ratios change by less than about 0.5% from 0.1 to 0.025 ms; at 20–40 ms they vary more, particularly Peng. Thus long-window relative penalty is stable over this timestep range, while short-window ratios are not yet fully converged at 0.025 ms.

## Full-Hines integration convergence

Against the 0.025-ms Hines waveform, median NRMSE is about 0.52–0.59% at 0.1 ms and 0.176–0.197% at 0.05 ms. Maximum differences are 2.141% for Peng / 0.1 ms and 1.453% for Tamas / 0.1 ms; at 0.05 ms these maxima fall to 0.744% and 0.495%. Halving dt from 0.1 to 0.05 ms reduces the discrepancy by about 2.9–3.0×, consistent with a first-order backward-Euler trend over this range.

Consequently, full-Hines temporal error is many orders of magnitude greater than PRIMA reduction NRMSE for these settings. Timestep discretization dominates the absolute error budget; seven/nine ratios remain useful for comparing reduction error at a fixed timestep but are not total simulation error.

## CI fixture debugging

Earlier CI attempts exposed fixture-schema and fixture-coverage mistakes: the test fixture did not carry the new coordinate-delta field, then the summary fixture covered only one morphology/one dt/window rather than the declared 144 source/window groups. These were corrected without weakening production or analysis gates. The final workflow passed 15/15 tests before starting the full replay; failed iterations produced no accepted numerical result.

## Limits and next step

The 0.025-ms run is a numerical reference, not an analytic solution. Only two passive morphologies. Next, extend the reference to 0.0125 ms and compare 0.05/0.025/0.0125-ms Hines traces at common sample times; recompute q25 ratios at 0.0125 ms. Do not change production defaults based on this limited study.
