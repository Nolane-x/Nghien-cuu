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

## Current status

Implementation and workflow are committed; the GitHub Actions run must pass before numerical conclusions are written. Expected coverage: 36 models, 324 frequency rows, 1,728 per-port transient rows, 756 shared-port pairs, 216 q25-only rows and 378 Hines reference checks.

## Scientific boundaries

The morphology is a single epilepsy surgical specimen with incomplete axon. It is not a population or healthy-control holdout. Results are passive linear-RC numerical comparisons only. No candidate is promoted and no production default changes.
