# Handoff — PRIMA accuracy, memory and holdout synthesis

**Date:** 23 November 2026  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/prima-accuracy-memory-holdout-synthesis-2026-11-23`  
**Base:** main `b5dfd77816db8b34de689f2a456ccb9b52b79e4f`

## Read first

1. `AGENTS.md`
2. `HANDOFF.md`
3. `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md`
4. `amsn-core/research/HUMAN_PASSIVE_PRIMA_ACCURACY_MEMORY_HOLDOUT_SYNTHESIS_2026-11-23.md`

## Why this checkpoint exists

The passive PRIMA project had accumulated separate validated branches for shift/order accuracy, seven-vs-nine-port accuracy, high-order nine-port capacity, held-out morphology and resource benchmarking. Their conclusions were not yet joined into one conditional engineering decision.

This report synthesizes shift/order accuracy, equal-order port-count behavior, two independent morphology holdouts, high-order capacity and resource evidence while preserving the distinct configurations and comparison baselines.

## Validated conclusion

- Keep full Hines canonical.
- Treat 7-port order112 extended10kHz as the current high-frequency passive research candidate; extended10kHz is supported on both the NMO_162186 epilepsy and NMO_03524 Control holdouts.
- Treat port count/order as morphology-dependent and evaluate absolute error as well as ratios. NMO_162186 required order168 to restore nine-port parity; NMO_03524 was near parity at both orders; NMO_163775 had high relative ratios but small absolute errors; NMO_107159 showed 42.72× at order112 and near parity at order168 (1.001×). See PRs #13, #15, #16 and #17.
- Treat 7-port order84 extended10kHz as a good accuracy/storage compromise on the NMO_03524 Control holdout; order84 remains the lower-memory region in the separate resource matrix.
- Do not change production defaults.

## Main evidence

- PR #7 / workflow 45002816664: 243 models, 2,187 AC rows, 10,206 transient-port rows; all nine candidates remain Pareto non-dominated.
- PR #8 / workflow 45012282648: one external NMO_162186 holdout; all 81 models pass. Source is an epilepsy surgical specimen with incomplete axon.
- PR #6 / workflow 44987393352: at equal order56/112, nine ports regress all 252 shared-output comparisons; at order168 shared outputs are effectively equivalent and q25 outputs are accurate.
- PR #4 / workflow 44979673244: nine-port order112/168 improve q90 transients across all 36 matched scenarios versus order84 references.
- PR #5 / workflow 44989658844: 37/37 jobs pass; median peak RSS order84/112/168 = 267.90/276.15/301.73 MB. Wall/CPU medians are confounded by heterogeneous GitHub runner hardware.

## Matched holdout results now completed

PR #13 / run 45184621520 passed the matched 7-port/9-port comparison on NMO_162186. At order112, nine-port was worse on 377/378 shared pairs (median ratio 8.162×); at order168, it was at parity (0.99999985×). q25 maximum NRMSE was 3.6711e−6% at order112 and 8.6226e−8% at order168.

PR #15 / run 45198630080 passed the same matched design on NMO_03524. At order112, 9-port was near parity (204 worse / 173 better / 1 tie; median ratio 1.00000465×); at order168 it was also at parity (189/189; 0.99999991×). q25 maximum NRMSE was 3.0585e−8% and 3.0586e−8%, respectively. The incremental port-count cost is morphology-dependent; do not impose a universal order168 requirement.

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


PR #15 / workflow 45198630080 adds the second matched 7/9-port morphology. Its results support morphology-dependent incremental port cost: NMO_03524 achieved shared-output parity at order112, whereas NMO_162186 did not.


## Third matched morphology completed — NMO_163775 Peng

PR #16 / [run 45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600) passed. Artifact [#14883752560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600/artifacts/14883752560), ZIP SHA-256 \`9060b04e6e769a1e9b40700197361bf67a59b164965441849e8cd3effb716a58\`.

Coverage: 36 models, 324 AC, 1,728 transient, 756 shared pairs, 216 q25, 378 exact Hines comparisons. q25 SWC IDs basal 224, apical 4096. Hines references are exactly equal across layouts.

At order112, nine-port was worse on all 378 pairs; median 9/7 error ratio 78.051×, but maximum absolute nine-port shared NRMSE was 0.0001933%. At order168, 347 worse / 31 better; median ratio 14.501× and maximum absolute nine-port shared NRMSE 6.0657e−7%. q25 maximum NRMSE was 2.1588e−4% at order112 and 4.2824e−7% at order168.

Important: this Peng morphology uses 0.5 µm mesh and NeuroMorpho marks No Diameter, so it expands the structural-completeness context but does not provide diameter-grounded biology. The two earlier human holdouts used 0.125 µm; absolute cross-morphology error comparisons are not directly comparable. Full Hines remains canonical; no production defaults change.


## Fourth matched morphology now complete — NMO_107159 Tamas human pyramidal comparator

PR #17 / [run 45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588) passed. Artifact [#14884183988](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588/artifacts/14884183988), ZIP SHA-256 \`b01bbce48bc62931c10b78f5a97a8e334f26bd0ea186ede6335a92484b8d3808\`.

Coverage:36 models,324 AC,1,728 transient,756 shared pairs,216 q25 observations,378 exact Hines checks. All378 Hines traces were exactly equal. At order112, 9-port was worse on all378 pairs; median ratio42.718×, max absolute nine-port shared NRMSE3.9507e−5%. At order168,214 pairs worse/164 better, median ratio1.00102×, max absolute nine-port shared NRMSE5.4559e−7%. q25 max NRMSE3.5323e−5% at112 and2.3679e−7% at168.

NMO_107159 is a human female Control pyramidal comparison cell with Dendrites & Axon Complete and Diameter/3D/Angles metadata; it is not a rosehip interneuron. The run uses0.5 µm mesh, same as Peng NMO_163775; earlier human NMO_162186/NMO_03524 runs use0.125 µm. Absolute cross-morphology error comparisons need mesh harmonization.
