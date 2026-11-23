# Matched 7-port / 9-port PRIMA validation on NMO_03524 Jacobs Control morphology

**Date:** 23 November 2026  
**Morphology:** NeuroMorpho NMO_03524 / Jacobs / 1-5-3 (human Control metadata, occipital BA18)  
**SWC SHA-256:** `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`  
**Status:** implementation and CI added; numerical replay pending

## Research question

PR #13 showed that nine-port order112 systematically degrades the seven shared outputs on the NMO_162186 epilepsy holdout, while order168 restores near-parity and represents the two q25 outputs accurately. PR #14 added a second human morphology in a Control metadata context but used seven ports only.

This experiment tests whether the same order-dependent port-count conclusion transfers to NMO_03524 using the exact same seven shared SWC nodes and two q25-only nodes in both layouts.

## Pinned morphology and exact port identities

- Source: NMO_03524 / Jacobs / 1-5-3; human, Control metadata, age 23, male, occipital BA18, in vitro Golgi.
- 869 SWC records, 862 electrical compartments; source SHA-256 pinned above.
- Existing seven-port nodes: soma 1; basal q50 367, basal q75 583, basal q90 751; apical q50 866, apical q75 867, apical q90 868.
- Added q25 nodes: **basal q25 = 272; apical q25 = 864**. These were derived using the exact path-distance quantile helper from the original research code and verified to be distinct from the seven canonical nodes.
- Both layouts share the same soma/basal-q75/apical-q75 current-injection nodes.

The runner fails closed if the seven shared node IDs, the two q25-only IDs, source IDs, or expected port count change.

## Matched experiment

- Port counts: 7 and 9, with the same seven shared nodes.
- Basis orders: 112 and 168.
- Shift set: identical extended10kHz `0, 100, 1,000, 3,000, 6,000, 10,000 Hz`.
- Passive parameter scenarios: the same nine deterministic nominal / ±20% Rm/Cm/Ra / all-parameter cases.
- AC frequencies: 0.1 Hz to 10 kHz (nine points).
- Current sources: soma, basal-q75, apical-q75.
- Transients: 2 ms and 10 ms square pulses; 10 pA; onset 2 ms; total 20 ms; dt 0.1 ms.
- Reference: full Hines with the same morphology and parameter scenario.
- Shared output comparisons pair by exact SWC node ID. Basal-q25 and apical-q25 are reported separately.

## Expected complete coverage

| Output | Rows |
|---|---:|
| Model × port-count × order × scenario | 36 |
| Frequency matrices | 324 |
| Per-port transient rows | 1,728 |
| Shared output pairs | 756 |
| q25-only observations | 216 |
| Full-Hines shared-node checks | 378 |

All reduced G/C matrices must pass Cholesky checks, each candidate must achieve the requested order, and all Hines shared-node reference traces must be exactly equal within the configured numerical tolerance.

## What this test can decide

1. Whether nine-port order112 again degrades the seven shared outputs on a Control-context morphology.
2. Whether nine-port order168 restores shared-output parity.
3. Whether the two q25 outputs remain accurate on NMO_03524.
4. Whether a port-count decision made on an epilepsy specimen also holds on a separate Jacobs Control-condition morphology.

## Scientific limits

This is one Control-condition cell; dendrites are moderate and the axon incomplete. It is not a population sample. The result is passive linear-RC validation against full Hines only, not active-neuron or biological validation. Full Hines remains canonical and no production default changes.
