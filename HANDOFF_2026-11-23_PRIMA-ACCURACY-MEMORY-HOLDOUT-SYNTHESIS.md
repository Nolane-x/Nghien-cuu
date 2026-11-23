# Handoff — PRIMA accuracy, memory and holdout synthesis

**Date:** 23 November 2026  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** \`research/prima-accuracy-memory-holdout-synthesis-2026-11-23\`  
**Base:** main \`b5dfd77816db8b34de689f2a456ccb9b52b79e4f\`

## Read first

1. \`AGENTS.md\`
2. \`HANDOFF.md\`
3. \`amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md\`
4. \`amsn-core/research/HUMAN_PASSIVE_PRIMA_ACCURACY_MEMORY_HOLDOUT_SYNTHESIS_2026-11-23.md\`

## Why this checkpoint exists

The passive PRIMA project had accumulated separate validated branches for shift/order accuracy, seven-vs-nine-port accuracy, high-order nine-port capacity, held-out morphology and resource benchmarking. Their conclusions were not yet joined into one conditional engineering decision.

This report synthesizes the five evidence tracks while explicitly preserving their different configurations and comparison baselines.

## Validated conclusion

- Keep full Hines canonical.
- Treat 7-port order112 extended10kHz as the current high-frequency passive research candidate, supported on three morphologies and one independent holdout.
- Treat 9-port order168 as an opt-in research candidate only when basal/apical q25 outputs are required.
- Treat order84 as the lower-memory candidate from the separate nine-port resource matrix.
- Do not change production defaults.

## Main evidence

- PR #7 / workflow 45002816664: 243 models, 2,187 AC rows, 10,206 transient-port rows; all nine candidates remain Pareto non-dominated.
- PR #8 / workflow 45012282648: one external NMO_162186 holdout; all 81 models pass. Source is an epilepsy surgical specimen with incomplete axon.
- PR #6 / workflow 44987393352: at equal order56/112, nine ports regress all 252 shared-output comparisons; at order168 shared outputs are effectively equivalent and q25 outputs are accurate.
- PR #4 / workflow 44979673244: nine-port order112/168 improve q90 transients across all 36 matched scenarios versus order84 references.
- PR #5 / workflow 44989658844: 37/37 jobs pass; median peak RSS order84/112/168 = 267.90/276.15/301.73 MB. Wall/CPU medians are confounded by heterogeneous GitHub runner hardware.

## Next work

1. Run a matched seven-port versus nine-port order112/order168 comparison on NMO_162186.
2. Add another independent morphology with clear source metadata and a different experimental context.
3. Re-benchmark runtime on fixed hardware before claiming a time-performance winner.
4. Keep active-channel and nonlinear-synapse validation as separate research stages.

## Scope

This report changes no solver, default order, port set, Hines reference or production behavior. It synthesizes passive linear-RC experiments only.
