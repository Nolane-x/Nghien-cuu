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

Workflow [45428685906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906) passed **15/15 focused tests**, both morphology checksums and preflights, the full matrix, six exact CSV read-backs, result commit and artifact upload.

- Result commit: \`d79ca743cbb662bf4536b28c527bfa5234058c15\`.
- Artifact: [14937828066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906/artifacts/14937828066), SHA-256 \`9fae812ff71e2a6a0c8920495d7e990830a0f116843fadfbd20e84fa924e498f\`.
- Coverage: 24,192 metrics; 12,096 paired 7/9 comparisons; 192 source summaries; 32 morphology-window summaries; 9,072 Hines temporal comparisons; 24 Hines temporal summaries.
- Runtime: 388.44 s; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.
- Long-window 9/7 ratio is stable from dt 0.1 to 0.0125 ms: Tamas ~31.84–32.05× at 100–200 ms; Peng ~33.45–33.62×. At 20–40 ms it still varies, especially Peng (138.24→118.81× at 20 ms; 70.09→64.98× at 40 ms).
- Full-Hines error against dt 0.0125 is about 0.63–0.68% median at dt 0.1, 0.265–0.296% at dt 0.05, and 0.089–0.100% at dt 0.025. Adjacent discrepancy ratios 2.30–2.32 and 2.94–2.96 closely match first-order BE geometry (2.33 and 3).

## Scientific limits

The 0.0125-ms run is a finer numerical reference, not an exact continuous-time solution. Only two passive linear-RC morphologies. No production solver/default is changed; full Hines remains canonical.


## Next research step

Do not spend another sweep merely shrinking all timesteps uniformly. The long-window ratio is already stable. The highest-value next step is a targeted short-window study: retain dt 0.0125 ms, add 0.00625 ms for 20/40-ms windows only, and decompose the finite-window error into the periodic transfer and terminal-state boundary terms. Preserve the same perturbation-coordinate metric and seven/nine layouts. This should determine whether the remaining 20–40-ms variation is time-discretization error or cancellation between transient and boundary contributions.

