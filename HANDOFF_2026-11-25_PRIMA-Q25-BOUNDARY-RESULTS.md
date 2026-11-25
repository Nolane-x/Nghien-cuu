# Handoff — PRIMA q25 finite-window decomposition results

**Date:** 25 November 2026  
**Completed branch:** `research/prima-q25-short-window-boundary-decomposition-2026-11-25`  
**Research PR:** [#34](https://github.com/Nolane-x/Nghien-cuu/pull/34)  
**Latest result commit before this checkpoint:** `c988e1b82407822d658046898c4c8a4d58ca8082`

## Current state

The q25 short-window periodic-transfer / terminal-boundary decomposition is complete for two pinned passive morphologies. The workflow [45555648742](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45555648742) succeeded; 16/16 focused tests passed; both morphology preflights and source checksums passed; all six numerical CSVs passed exact read-back coverage checks; 432 finite-record identities were checked.

The maximum finite-identity relative residual was (8.9204\times10^{-12}), versus the (2\times10^{-8}) acceptance tolerance. The complete validated result and scientific limits are recorded in:

- `amsn-core/research/PRIMA_Q25_SHORT_WINDOW_BOUNDARY_DECOMPOSITION_RESULTS_2026-11-25.md`
- `research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-BOUNDARY-RESULTS.md`

The earlier `HANDOFF_2026-11-25_PRIMA-Q25-SHORT-WINDOW-BOUNDARY-DECOMPOSITION.md` and initial research note are preserved as the pre-execution checkpoint; their “pending” status describes the state when they were authored, not the final state.

## Core finding

Periodic discrete-transfer error and finite-window terminal-boundary correction strongly cancel. Their individual norms exceed the final finite error in several conditions. The cancellation and transient metric ratios are morphology- and window-dependent. Both canonical absolute-voltage and perturbation-coordinate transient metrics must remain visible. No biological generalization or production-default change is justified.

## Repository/PR handling

- Do not push these research results directly to `main`; the current PR is stacked on the q25 dt=0.00625-ms research branch.
- PR #33 remains the parent branch/PR for the timestep refinement; PR #34 contains the boundary decomposition.
- Do not merge either PR as part of this handoff. Review the dependency chain and exact results first.
- Full Hines remains canonical; no production runtime defaults have changed.
- Keep prior failed/cancelled workflow attempts as history; the successful workflow is the accepted run for this study.

## Next concrete experiment

Replicate the finite-record decomposition on the independent NMO_03524 Jacobs Control and NMO_162186 Allen L2/3 holdouts. Their source files and earlier seven/nine-port studies already exist, but q25-specific node mapping and preflight must be freshly pinned for this experiment. Use a common 0.5-µm NEURON segment cap for the first comparison; preserve source condition and morphology limitations separately. The four-morphology matrix should target 537,768 frequency rows, 6,048 case metrics, 3,024 paired comparisons, 48 source/window summaries, 8 morphology/window summaries and 864 identity checks.

Before interpreting the next run, validate the q25 identities, exact source checksums, output-node mapping and common mesh cap. Do not infer population-level behavior from four individual reconstructions.
