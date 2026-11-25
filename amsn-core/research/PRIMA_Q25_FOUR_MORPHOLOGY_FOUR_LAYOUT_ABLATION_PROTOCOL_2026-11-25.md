# PRIMA q25 four-layout boundary ablation — protocol and pinned identities

**Branch:** `research/prima-q25-cross-morphology-boundary-replication-2026-11-25`  
**Workflow:** `.github/workflows/amsn-prima-q25-four-layout-boundary-ablation.yml`  
**Runner:** `amsn-core/research/analyze_prima_q25_four_morphology_four_layout_boundary_ablation.py`

## Purpose

The previous four-morphology experiment compared only the canonical seven-port layout with a nine-port layout containing both q25 probes. That establishes whether the combined two-probe layout differs, but it cannot attribute the change to the basal or apical probe individually.

This ablation separates the two changes while preserving the same seven shared SWC nodes, source injection sites, passive scenarios, PRIMA order, timestep, input waveform, observation windows, and frequency mapping.

## Layout contract

| Layout ID | Ports | Added q25 probe(s) |
|---|---:|---|
| `seven` | 7 | None; canonical baseline |
| `eight_basal_q25` | 8 | Basal q25 only |
| `eight_apical_q25` | 8 | Apical q25 only |
| `nine_both_q25` | 9 | Basal q25 and apical q25 |

For every morphology the runner must enforce:

1. Exactly seven unique shared SWC node IDs.
2. Exactly two distinct q25 IDs, neither overlapping the shared seven.
3. The basal-only 8-port set equals the shared seven plus only basal-q25.
4. The apical-only 8-port set equals the shared seven plus only apical-q25.
5. The 9-port set equals the shared seven plus both q25 IDs.
6. All four layouts retain exactly the same soma, basal-q75 and apical-q75 source SWC node IDs.

The validator fails closed if a layout contains another node, a duplicate node, a swapped q25 role, or a changed source site.

## Pinned per-morphology node identities

The following IDs are exact SWC node IDs, not zero-based array indices.

| NeuroMorpho ID | Shared seven SWC IDs | Basal q25 | Apical q25 |
|---|---|---:|---:|
| NMO_163775 (Peng) | 1, 144, 3926, 4180, 40, 4104, 3948 | 224 | 4096 |
| NMO_107159 (Tamas) | 1, 6363, 4735, 5564, 7023, 4301, 4623 | 6609 | 4404 |
| NMO_03524 (Jacobs) | 1, 367, 583, 751, 866, 867, 868 | 272 | 864 |
| NMO_162186 (Allen L2/3) | 1, 515, 2261, 2304, 4180, 4262, 6608 | 2713 | 4488 |

The independent source SHA-256 and q25 preflight contract for every morphology are checked before this experiment starts. The two newer Jacobs/Allen q25 contracts were produced by their own preflight. Peng and Tamas use preflight records retained from previously validated runs; the runner still reloads the exact SWC bytes, recomputes the source mapping, and checks the pinned node identities.

## Fixed numerical protocol

- Morphologies: 4 independent reconstructions.
- Layouts: 4 (7 / 8 basal-only / 8 apical-only / 9 combined).
- PRIMA basis order: 168.
- Expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Passive parameter scenarios: nominal; Rm −20%; Rm +20%; Cm −20%; Cm +20%; Ra −20%; Ra +20%; all −20%; all +20%.
- Sources: soma, basal-q75 and apical-q75.
- Input: 10-pA square pulse, onset 2 ms, widths 2 ms and 10 ms.
- Timestep: 0.00625 ms.
- Observation windows: 20 ms and 40 ms.
- Master frequency grid: 0–80 kHz, 25-Hz spacing (3,201 points).
- Common NEURON maximum segment cap: 0.5 µm.
- DFT finite-window identity tolerance: 2 × 10⁻⁸ relative to the output DFT scale.

## Exact expected coverage

| Output | Expected rows |
|---|---:|
| Frequency summary (4 morphologies × 4 layouts × 3 sources × 7 shared outputs × 3,201 frequencies) | 1,075,536 |
| Case metrics (4 × 9 scenarios × 4 layouts × 3 sources × 2 pulse widths × 7 outputs × 2 windows) | 12,096 |
| Candidate-layout vs seven-port matched pairs (4 × 9 × 3 candidate layouts × 3 sources × 2 pulses × 7 outputs × 2 windows) | 9,072 |
| Source/layout/window summary (4 × 3 candidates × 3 sources × 2 pulses × 2 windows) | 144 |
| Morphology/layout/window summary (4 × 3 candidates × 2 windows) | 24 |
| Finite-DFT identity diagnostics (4 × 9 scenarios × 4 layouts × 3 sources × 2 pulses × 2 windows) | 1,728 |

The workflow reads every result CSV back and validates these exact counts. It separately enforces the maximum finite-window DFT identity error against the 2 × 10⁻⁸ tolerance.

## Interpretation plan

Compare each candidate to the seven-port baseline within the same morphology, scenario, source, pulse and window:

- **Basal effect:** `eight_basal_q25` versus `seven`.
- **Apical effect:** `eight_apical_q25` versus `seven`.
- **Combined effect:** `nine_both_q25` versus `seven`.
- **Interaction diagnostic:** compare the combined error/residual change with the two one-probe changes. Do not assume the two probe effects add linearly; their bases are independently generated reduced models.

The report must show continuous-AC, discrete backward-Euler periodic-transfer, canonical absolute-voltage transient, and perturbation-coordinate transient metrics separately. It must also retain the terminal-boundary component and periodic/boundary cross-term. Large relative ratios must be shown alongside absolute error measures because the seven-port denominator can be very small.

Do not pool the four morphologies as if they were exchangeable. Peng is a mouse Control record with NeuroMorpho's No Diameter attribute; Jacobs has moderate dendritic integrity and an incomplete axon; Allen is an epilepsy surgical specimen with incomplete axon; Tamas is a single human Control pyramidal comparison cell. None is a population sample. This remains a passive linear-RC reduction study, not active-neuron or biological validation.

## Artifact strategy

The master frequency summary has more than one million rows and is expected to exceed GitHub's 100-MB single-file limit. Therefore:

- The complete frequency summary, every other CSV, the JSON report, runtime file, SWC source required for reproduction, and pinned preflight records go into the GitHub Actions artifact.
- Smaller comparison, identity, summary and case-metric CSVs plus the JSON report are committed to the research branch.
- The workflow's final gate verifies the expected row counts before committing any numerical result.
