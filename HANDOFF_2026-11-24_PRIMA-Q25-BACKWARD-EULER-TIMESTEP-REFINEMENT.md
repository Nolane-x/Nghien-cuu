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

Workflow [45426480184](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184) passed **15/15 focused tests**, both morphology checksum/preflight gates, the full matrix, all six CSV read-backs, result commit and artifact upload.

- Result commit: \`8161b30e7a9ac3f62dcfb8754e08850a703f5ad3\`.
- Artifact: [14934844995](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184/artifacts/14934844995), SHA-256 \`e8aeb6359f987a52040d38d28586185339654331c2d819334743cb1ee947e127\`.
- Coverage: 18,144 metrics; 9,072 paired 7/9 comparisons; 144 source summaries; 24 morphology/window summaries; 6,048 Hines temporal rows; 16 Hines temporal summaries.
- Stable nine/seven ratios: Tamas 20/40/100/200 ms = 24.44/55.24/31.87/31.64× at 0.1 ms, 26.59/57.04/31.73/31.59× at 0.05 ms, 27.05/54.85/31.72/31.59× at 0.025 ms. Peng = 138.24/70.09/33.67/33.43×, 130.11/67.68/33.62/33.42×, 123.68/63.89/33.64/33.46× respectively.
- At 100–200 ms these ratios change by less than about 0.5% from 0.1 to 0.025 ms; at 20–40 ms there is appreciable timestep dependence.
- Full-Hines coarse-vs-0.025-ms median NRMSE is about 0.52–0.59% at 0.1 ms and 0.176–0.197% at 0.05 ms. Halving dt reduces the discrepancy about 2.9–3.0×, consistent with a first-order BE trend.
- Absolute nine-port NRMSE remains roughly \(10^{-9}\%\)–\(10^{-8}\%\); time-discretization error is much larger in this benchmark.


## Scientific limits

The 0.025-ms run is a finer numerical reference, not an analytic continuous-time solution. Only two individual passive linear-RC morphologies are tested. No production solver/default is changed; full Hines remains canonical.


## Next concrete step

Extend the Hines temporal reference one more level to 0.0125 ms. Compare 0.05/0.025/0.0125-ms traces at common sample-end times to test whether the observed ~first-order BE trend persists, and recompute 7/9-port ratios at 0.0125 ms. Keep the same basis/order, pulse convention and perturbation-coordinate metric. Do not change production defaults.
