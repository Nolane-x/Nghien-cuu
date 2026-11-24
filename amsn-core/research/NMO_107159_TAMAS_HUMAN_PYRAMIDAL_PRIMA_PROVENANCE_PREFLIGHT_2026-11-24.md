# NMO_107159 Tamas human pyramidal comparison cell — provenance and preflight

**Date:** 24 November 2026  
**NeuroMorpho ID:** NMO_107159  
**PR:** [#17](https://github.com/Nolane-x/Nghien-cuu/pull/17)

## Purpose

Add a fourth independent morphology to the passive PRIMA matched 7-port/9-port × morphology validation. This record is a human frontal neocortical pyramidal comparison cell with dendrites and axon marked complete and explicit 3D diameter metadata. It provides a diameter-recorded comparison alongside the Peng complete-axon record whose metadata says No Diameter.

## NeuroMorpho provenance

- NeuroMorpho.Org ID: NMO_107159
- Cell: `Fig5c_141009_2og_B`
- Archive: Tamas
- Species: human
- Gender: female
- Age: not reported
- Region: neocortex, frontal, layer 1 and layer 2–3
- Cell class: principal cell, pyramidal
- Experimental condition: Control
- Protocol: in vitro
- Stain: biocytin
- Slicing direction: perpendicular to cortical layers
- Slice thickness: 70 µm
- Reconstruction software: Neurolucida
- Objective: oil, 100×
- Structural domain: Dendrites, Soma, Axon
- Physical integrity: Dendrites & Axon Complete
- Morphological attributes: Diameter, 3D, Angles
- Original format: Neurolucida.dat
- Published source DOI: 10.1038/s41593-018-0205-2
- PMID: 30150662

Official sources:
- [NeuroMorpho detail page](https://neuromorpho.org/neuron_info.jsp?neuron_name=Fig5c_141009_2og_B)
- [NeuroMorpho API record](https://neuromorpho.org/api/neuron/id/107159)
- [Morphometry](https://neuromorpho.org/api/morphometry/id/107159)
- [Standardized SWC](https://neuromorpho.org/dableFiles/tamas/CNG%20version/Fig5c_141009_2og_B.CNG.swc)
- [Published article](https://doi.org/10.1038/s41593-018-0205-2)
- [bioRxiv version](https://www.biorxiv.org/content/10.1101/216085v1.full-text)

### Correct cell identity in the source article

The source article is about a specialized human cortical GABAergic rosehip cell type. Its Figure 5C nevertheless explicitly shows a pyramidal comparison cell in connection with a rosehip cell. The NeuroMorpho cell name `Fig5c_141009_2og_B` and record class `principal cell, pyramidal` identify this reconstruction as the **pyramidal comparison cell**, not as a rosehip interneuron. Preserve this distinction in all reports and citations.


Official NeuroMorpho morphometry (API `/api/morphometry/id/107159`): total length 12,320.7 µm; mean diameter 0.285193 µm; 61 bifurcations; 126 branches; 4 stems; max path distance 1,662.83 µm; max Euclidean distance 1,420.16 µm; width 777.889 µm, height 1,595.1 µm, depth 91.47 µm; surface 9,693.02 µm²; volume 1,624.96 µm³. These are repository morphometry measurements/derived descriptors; passive membrane and axial parameters remain separate model assumptions.

## Pinned repository source

Repository path:
`amsn-core/data/human/neuromorpho_tamas/NMO_107159_Fig5c_141009_2og_B.CNG.swc`

SHA-256:
`6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`

The file contains the original standardized SWC's numeric seven-column records unchanged; upstream comments are replaced with a provenance/attribution header.

Independent topology scan:
- 7,228 SWC records
- Soma: 3
- Axon: 4,030
- Basal dendrite: 1,767
- Apical dendrite: 1,428
- One soma root
- All 7,228 nodes reachable from root
- No duplicate IDs
- No missing parent references
- Three-point soma convention preserved

## Path-distance quantiles and candidate ports

The quantile helper uses root-to-node Euclidean path distance and deterministic rank selection.

Seven canonical ports:
- Soma: 1
- Basal q50/q75/q90: 5564 / 6363 / 7023
- Apical q50/q75/q90: 4301 / 4735 / 4623

Two q25-only probes:
- Basal q25: 6609
- Apical q25: 4404

The preflight pins the canonical seven and recomputes q25 with the same helper used by the replay. Replay reads the two q25 IDs from `preflight.json` and fails closed if its own mapping differs.

## Matched 7-port / 9-port experiment

- Port counts: 7 and 9, preserving exactly the same seven shared SWC node identities.
- Basis orders: 112 and 168.
- Six extended10kHz expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Nine deterministic passive Rm/Cm/Ra scenarios.
- Nine AC frequencies: 0.1 Hz through 10 kHz.
- Three current sources: soma, basal-q75 and apical-q75.
- Two square-pulse widths: 2 ms and 10 ms; 10 pA; onset 2 ms; total duration 20 ms; dt 0.1 ms.
- Full-Hines references are computed for both layouts and checked at all seven common outputs.
- Same 0.5 µm NEURON segment cap as the Peng complete-axon holdout; the two earlier human holdouts used 0.125 µm.

Expected coverage: 36 models, 324 AC rows, 1,728 transient-port rows, 756 matched shared-output pairs, 216 q25 observations and 378 shared-Hines checks.

## Scientific limits

This is one human pyramidal reconstruction, not a representative population. The record has measured-diameter attributes (Diameter, 3D, Angles), but the passive membrane parameters, conductance assumptions and reference discretization still affect absolute numerical errors. The source article concerns rosehip cells; this specific reconstruction is a pyramidal comparison cell, not a rosehip interneuron.

The experiment is passive linear-RC reduction against full Hines only. It does not validate active channels, action potentials, nonlinear synapses, plasticity or biological physiology. Full Hines remains canonical; no production defaults change.

## Data attribution

NeuroMorpho.Org data are supplied under CC BY 4.0. Use requires attribution to:
1. The original article: DOI 10.1038/s41593-018-0205-2.
2. NeuroMorpho.Org (RRID:SCR_002145).
3. Tecuatl C, Ljungquist B, Ascoli GA (2024), “Accelerating the continuous community sharing of digital neuromorphology data,” FASEB Bioadv. 6(7):207–221, doi:10.1096/fba.2024-00048.

See [NeuroMorpho terms of use](https://neuromorpho.org/useterm.jsp).

## Validation checkpoint

The current GitHub Actions run [45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588) has passed the complete AMSN regression suite, the Tamas source/metadata guardrails, source SHA-256 verification and Import3D preflight. The matched numerical replay is still in progress. No numerical 7-port/9-port conclusion is claimed in this preflight report.
