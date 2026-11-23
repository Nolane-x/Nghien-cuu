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

The q25 IDs were derived using the original path-distance/quantile definition and are required to remain distinct.

## Implementation

Reuses the validated NMO_162186 matched-port runner and changes only the pinned morphology identity, preflight schema and output paths. Same order112/order168, six extended10kHz shifts, nine passive scenarios, nine AC frequencies, three sources and two pulse widths. Shared outputs pair by exact SWC ID; q25 output errors are separately reported. Full-Hines references are checked for exact identity on all seven shared nodes.

## Status

Runner, tests, workflow, report and handoff are committed. CI replay is pending. Expected coverage: 36 models, 324 frequency rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations and 378 Hines consistency checks.

## Scientific boundaries

Single human Control-condition morphology with moderate dendrites and incomplete axon. Passive linear-RC only. No production defaults or solver behavior change.
