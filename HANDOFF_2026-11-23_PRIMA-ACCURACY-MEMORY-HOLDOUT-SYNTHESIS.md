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
- Treat 7-port order112 extended10kHz as the current high-frequency passive research candidate; extended10kHz is supported on both the NMO_162186 epilepsy and NMO_03524 Control holdouts.
- Treat port count/order as morphology-dependent: NMO_162186 required order168 to restore nine-port shared-output parity, while NMO_03524 was already at parity at order112 with both q25 outputs accurate.
- Treat 7-port order84 extended10kHz as a good accuracy/storage compromise on the NMO_03524 Control holdout; order84 remains the lower-memory region in the separate resource matrix.
- Do not change production defaults.

## Main evidence

- PR #7 / workflow 45002816664: 243 models, 2,187 AC rows, 10,206 transient-port rows; all nine candidates remain Pareto non-dominated.
- PR #8 / workflow 45012282648: one external NMO_162186 holdout; all 81 models pass. Source is an epilepsy surgical specimen with incomplete axon.
- PR #6 / workflow 44987393352: at equal order56/112, nine ports regress all 252 shared-output comparisons; at order168 shared outputs are effectively equivalent and q25 outputs are accurate.
- PR #4 / workflow 44979673244: nine-port order112/168 improve q90 transients across all 36 matched scenarios versus order84 references.
- PR #5 / workflow 44989658844: 37/37 jobs pass; median peak RSS order84/112/168 = 267.90/276.15/301.73 MB. Wall/CPU medians are confounded by heterogeneous GitHub runner hardware.

## Matched holdout result now completed

PR #13 / run 45184621520 passed the matched 7-port/9-port order112/168 comparison on NMO_162186. At order112, 9-port was worse on 377/378 shared pairs (median error ratio 8.162×). At order168, it was at parity (median ratio 0.99999985×; 190 better / 187 worse / 1 tie). q25 maximum NRMSE was 3.6711e−6% at order112 and 8.6226e−8% at order168; all 378 shared Hines checks were exact.

## Next work

1. Add a third independent morphology with a more complete axon and distinct source study; repeat the matched 7-port/9-port order112/168 test.
2. Re-benchmark runtime on fixed hardware before claiming a time-performance winner.
3. Keep active-channel and nonlinear-synapse validation as separate research stages.

## Scope

This report changes no solver, default order, port set, Hines reference or production behavior. It synthesizes passive linear-RC experiments only.


See PR #13 and its run 45184621520 for the completed matched-port holdout results and artifact 14824270534.


PR #14 / run 45196546471 passed 146/146 tests and the full NMO_03524 seven-port shift/order matrix. Order112 extended10kHz is the precision candidate; order84 extended10kHz is the accuracy/storage compromise. The 9-port q25 conclusion is not tested on this morphology.


## Second matched port-count morphology now complete

PR #15 / run 45198630080 passed the matched NMO_03524 Control-condition comparison. At order112, nine-port was worse on 204 shared pairs, better on 173 and tied on one; median ratio 1.00000465×. At order168, 189 pairs were better and 189 worse; median ratio 0.99999991×. q25 maximum NRMSE was 3.0585e−8% at order112 and 3.0586e−8% at order168. All 378 common Hines references were exact.

Together with PR #13 on NMO_162186, this shows morphology-dependent incremental port cost, not a universal nine-port order168 rule. See the synthesis report's cross-morphology table and PR #15 artifact #14829912332.
