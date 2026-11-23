# Matched 7-port / 9-port PRIMA validation on NMO_03524 Jacobs Control morphology

**Date:** 23 November 2026  
**Morphology:** NeuroMorpho NMO_03524 / Jacobs / 1-5-3 (human Control metadata, occipital BA18)  
**SWC SHA-256:** `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`  
**Status:** validated — matched 7-port/9-port replay and result archival passed

## Research question

PR #13 showed that nine-port order112 systematically degrades the seven shared outputs on the NMO_162186 epilepsy holdout, while order168 restores near-parity and represents the two q25 outputs accurately. PR #14 added a second human morphology in a Control metadata context. This experiment tests whether the same order-dependent port-count conclusion transfers to NMO_03524.

The result is morphology-dependent: unlike NMO_162186, the nine-port expansion on NMO_03524 is already at near-parity with seven ports at order112.

## Pinned morphology and exact port identities

- Source: NMO_03524 / Jacobs / 1-5-3; human, Control metadata, age 23, male, occipital BA18, in vitro Golgi.
- 869 SWC records, 862 electrical compartments; source SHA-256 pinned above.
- Existing seven-port nodes: soma 1; basal q50 367, basal q75 583, basal q90 751; apical q50 866, apical q75 867, apical q90 868.
- Added q25 nodes: **basal q25 = 272; apical q25 = 864**. They were derived with the original path-distance quantile helper and are distinct from the seven canonical nodes.
- Shared current-injection nodes: soma 1, basal-q75 583, apical-q75 867.

The runner fails closed if the seven shared node IDs, the two q25-only IDs, source IDs, or expected port count change.

## Matched experiment

- Port counts: 7 and 9, with the same seven shared nodes.
- Basis orders: 112 and 168.
- Shift set: identical extended10kHz `0, 100, 1,000, 3,000, 6,000, 10,000 Hz`.
- Passive parameter scenarios: nine deterministic nominal / ±20% Rm/Cm/Ra / all-parameter cases.
- AC frequencies: 0.1 Hz to 10 kHz (nine points).
- Current sources: soma, basal-q75, apical-q75.
- Transients: 2 ms and 10 ms square pulses; 10 pA; onset 2 ms; total 20 ms; dt 0.1 ms.
- Reference: full Hines with the same morphology and parameter scenario.
- Shared output comparisons pair by exact SWC node ID. Basal-q25 and apical-q25 are reported separately.

## Validated workflow and coverage

[GitHub Actions run 45198027785](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785) completed successfully. Source checksum, complete AMSN regression, metadata/Import3D preflight, matched-port replay, exact coverage, result commit and artifact upload all passed.

- 36 model rows; all requested orders achieved; all reduced G/C matrices passed Cholesky checks.
- 324 frequency-matrix rows.
- 1,728 per-port transient rows.
- 756 shared-output pairs (378 per order).
- 216 q25-only observations (108 per order).
- 378 shared-Hines consistency checks.
- The 378 shared Hines traces were exactly identical: maximum absolute difference 0 V and relative L2 difference 0 for every pair.

Artifact: [nmo03524-jacobs-control-prima-7v9port-matched-order #14829710906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785/artifacts/14829710906)  
Artifact ZIP SHA-256: `eda28de9a4ce1fdf4742f88486671207d034bb12fb358e88280bb6601df72e06`

Runtime: Python 3.12.16, NEURON 9.0.2, NumPy 2.5.5. End-to-end time was 42.67 s wall / 89.88 s user CPU, peak RSS 98,100 KiB.

## Matched shared-output results

| Basis order | 9-port worse | 9-port better | Tie | Median 9/7 transient-error ratio | Maximum 9/7 ratio |
|---:|---:|---:|---:|---:|---:|
| 112 | 204/378 | 173/378 | 1 | **1.00000465×** | 1.00614× |
| 168 | 189/378 | 189/378 | 0 | **0.99999991×** | 1.00721× |

At order112 the median ratio is effectively 1.0, and the maximum observed ratio is only 1.00614. This is fundamentally different from NMO_162186, where the order112 median 9/7 ratio was 8.162× and 377/378 shared pairs regressed.

At order168 the two layouts are also at numerical parity on NMO_03524.

## Added q25 outputs

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 3.7497e−9% | 3.0585e−8% |
| 168 | 108 | 3.7498e−9% | 3.0586e−8% |

Both q25 outputs are represented with extremely small error at either basis order on this morphology.

## High-frequency AC and numeric storage

| Port count | Order | Median Z residual at 10 kHz | Median Y residual at 10 kHz | Median transient NRMSE | Numeric storage |
|---:|---:|---:|---:|---:|---:|
| 7 | 112 | 3.3897e−10% | 1.3226e−10% | 3.2708e−9% | 0.9280 MB |
| 9 | 112 | 5.3735e−9% | 5.4331e−9% | 3.5258e−9% | 0.9280 MB |
| 7 | 168 | 8.5030e−14% | 2.1992e−13% | 3.2706e−9% | 1.5355 MB |
| 9 | 168 | 8.8387e−14% | 3.0740e−13% | 3.5257e−9% | 1.5355 MB |

Numeric storage is the basis plus reduced G/C arrays, not whole-process RSS. At the same order it is identical for seven and nine ports in this implementation.

## Interpretation: port-count cost depends on morphology

The NMO_162186 and NMO_03524 results must now be interpreted together:

- On **NMO_162186** (epilepsy surgical specimen), nine-port order112 caused a major shared-output regression (median ratio 8.162×); order168 was needed to restore parity.
- On **NMO_03524** (Jacobs Control-condition morphology), nine-port order112 was already at parity (median ratio 1.00000465×, max 1.00614×), and q25 errors were below 3.1e−8%.

Thus **do not hard-code a universal rule that nine ports always require order168**. The incremental cost of retaining q25 outputs depends on morphology, port placement and the induced reduced basis. The same 9-port order112 design is a poor trade-off on NMO_162186 but a numerically acceptable candidate on NMO_03524 under this passive protocol.

For NMO_03524, order112 is sufficient for the tested nine-port passive outputs. This does not replace the conservative order168 option on NMO_162186, nor does it establish a population-wide design rule.

## Scientific limits

This is one Control-condition cell; dendrites are moderate and the axon incomplete. It is not a population sample. The result is passive linear-RC validation against full Hines only, not active-neuron or biological validation. Full Hines remains canonical and no production default changes.

## Outputs

The report JSON and CSVs under `amsn-core/results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_*` preserve the model curves, frequency matrices, transient outputs, exact shared-node pairs, q25-only errors, Hines consistency checks and per-candidate summaries.
