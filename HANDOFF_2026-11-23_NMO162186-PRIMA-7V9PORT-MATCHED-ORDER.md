# Handoff — matched 7-port / 9-port PRIMA holdout replay

**Date:** 23 November 2026  
**Branch:** \`research/prima-holdout-seven-nine-port-matched-order-2026-11-23\`  
**Base:** PR #8 head \`7655389b9d95dc85a54f81185a037ab026e32300\`

## Read first

1. \`amsn-core/data/human/allen_cell_types/NMO_162186_PROVENANCE.md\`
2. \`amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md\`
3. \`amsn-core/research/HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_PORT_COUNT_2026-11-22.md\`
4. \`amsn-core/research/HUMAN_PASSIVE_PRIMA_ACCURACY_MEMORY_HOLDOUT_SYNTHESIS_2026-11-23.md\`

## Purpose

PR #6 compared seven and nine ports across three morphologies. PR #8 tested nine shift/order candidates on NMO_162186 using seven ports. This branch crosses the two dimensions on the same independent morphology.

## Implementation

- Repeats strict NMO_162186 SWC SHA-256 and 7,287-record validation.
- Re-runs the original Import3D/area/port preflight at 0.125 µm mesh cap.
- Builds seven canonical ports and adds only basal-q25/apical-q25 to make the nine-port set.
- Uses identical orders 112/168, identical extended10kHz shifts and identical nine passive parameter scenarios.
- Reproduces the same Hines pulse sources and compares shared outputs by exact SWC ID.
- Archives q25-only errors separately and checks the seven-port and nine-port full-Hines references on shared nodes.


## Validated result — run 45184621520

- CI: passed; workflow link https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520
- Artifact: ID 14824270534; ZIP SHA-256 \`56c2fc8a7aa8fbb4a5d1b58efa92a757d60c550b6b24eee71e21065a462806fe\`
- Coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared-output pairs, 216 q25-only observations, 378 exact Hines checks.
- Order112: 9-port worse in 377/378 shared comparisons; median nine/seven transient error ratio 8.162×.
- Order168: shared outputs effectively equal; median ratio 0.99999985× (190 better, 187 worse, 1 tie).
- q25 maximum NRMSE: 3.6711e−6% at order112 and 8.6226e−8% at order168.
- Shared Hines traces: exact equality, maximum absolute difference 0 V.
- Whole experiment: 422.61 s wall, 518.23 s user CPU, 187,160 KiB peak RSS.

## Final interpretation

The independent holdout reproduces the original order-dependent port-count conclusion. Do not use nine-port order112 as a default just to gain two q25 outputs. If q25 is required, nine-port order168 is the supported research candidate among tested configurations. If only the original seven outputs are needed, keep seven-port order112 as the lower-storage high-frequency candidate. Full Hines remains canonical. No production promotion.

## Scientific boundaries

The morphology is a single epilepsy surgical specimen with incomplete axon. It is not a population or healthy-control holdout. Results are passive linear-RC numerical comparisons only. No candidate is promoted and no production default changes.
