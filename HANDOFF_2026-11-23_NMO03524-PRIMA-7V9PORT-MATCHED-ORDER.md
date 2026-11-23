# Handoff — NMO_03524 Jacobs Control matched 7-port / 9-port PRIMA

**Date:** 23 November 2026  
**Branch:** `research/prima-jacobs-control-matched-seven-nine-port-2026-11-23`  
**Base:** PR #14 head

## Read first

1. `amsn-core/data/human/neuromorpho_jacobs/NMO_03524_PROVENANCE.md`
2. `amsn-core/research/NMO_03524_JACOBS_CONTROL_PRIMA_HOLDOUT_2026-11-23.md`
3. `amsn-core/research/NMO_162186_PRIMA_7V9PORT_MATCHED_ORDER_2026-11-23.md`
4. PR #12 synthesis branch and PR #14

## Pinned identities

- SWC: NMO_03524 / Jacobs / 1-5-3; 869 records; SHA-256 `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`.
- Seven shared ports: [1, 367, 583, 751, 866, 867, 868].
- q25-only ports: basal node 272; apical node 864.
- Source injection nodes: soma 1; basal-q75 583; apical-q75 867.

## Validated run

- GitHub Actions run 45198027785 passed all steps, including full AMSN regression, source checksum/preflight, matched replay, result commit and artifact upload.
- Artifact #14829710906; ZIP SHA-256 `eda28de9a4ce1fdf4742f88486671207d034bb12fb358e88280bb6601df72e06`.
- Coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations, 378 exact Hines checks.
- All 36 reduced G/C matrices passed Cholesky checks; all requested orders were achieved.

## Key finding

Unlike NMO_162186, the Jacobs Control morphology does **not** show a meaningful order112 penalty for nine ports:
- Order112: 204 worse / 173 better / 1 tie; median 9/7 error ratio 1.00000465×; maximum 1.00614×.
- Order168: 189 worse / 189 better; median 0.99999991×; maximum 1.00721×.
- q25 max NRMSE: 3.0585e−8% at order112; 3.0586e−8% at order168.
- 378 common Hines references were exactly equal.

This indicates morphology-dependent incremental port cost. NMO_162186 required order168 to recover nine-port parity; NMO_03524 did not. Do not apply a universal order168 requirement without a morphology-specific check.

## Scientific boundary

Single human Control-condition morphology with moderate dendrites and incomplete axon. Passive linear-RC only. No production defaults or solver behavior change. Full Hines remains canonical.
