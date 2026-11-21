# FCI Eyal-labelled human L2/3 derivative — source and parameter audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Source:** https://github.com/ido4848/fci  
**Pinned commit:** `75ad8b4d81a7f51bf888b30650c543592340db06`  
**Status:** FCI inspected read-only; two independently sourced NeuroMorpho SWCs obtained and validated; no FCI code copied.

## Core finding

FCI has two configurations under `human/eyal` for human temporal L2/3 cells 1125 and 1204. They are FCI-specific reduced derivatives, not proof that this is the original complete Eyal et al. 2018 ModelDB implementation.

Provenance layers:
- FCI folder label is `eyal`.
- FCI `models.csv` morphology citation field names Mohan et al. 2015, DOI 10.1093/cercor/bhv188.
- Exact standardized SWC filenames resolve through NeuroMorpho.org to Segev records NMO_68174 and NMO_68175.
- NeuroMorpho metadata links DOI 10.7554/eLife.16553 (Eyal et al. 2016).
- Eyal et al. 2018 ModelDB 238347 is a separate six-cell model archive; its official 133 MB ZIP has not been downloaded or verified.

## FCI licensing and scope

The pinned FCI root tree has no LICENSE file. AMPA/NMDA and GABAAB MOD headers include a Blue Brain Project 2015 CC BY-NC-SA 4.0 notice; Na/Kv MOD files have no equally clear file-specific licensing notice. Do not infer code licensing from paper licensing. No FCI Python, HOC, MOD or ASC file has been copied into AMSN.

The shared `passive_dends_simple_soma_model.hoc` is reduced:
- Dendrites are passive.
- Na/Kv mechanisms are inserted in soma and a synthetic axon only.
- Axon is two sections, 45 µm total, 1 µm diameter, five segments per section; not a complete reconstructed axon/AIS.
- No explicit three-dimensional spine head/neck compartments in this HOC.
- Therefore it is not the full dendritic spine / NMDA-spike Eyal 2018 model.

## Two human morphology records

| Cell | FCI model folder | NeuroMorpho record | SWC rows | Type1 soma | Type2 axon | Type3 basal | Type4 apical |
|---|---|---:|---:|---:|---:|---:|---:|
| 1125 | Human_L23_PC_0603_11_937 | NMO_68174 | 12,410 | 3 | 116 | 5,595 | 6,696 |
| 1204 | Human_L23_PC_1303_03_448 | NMO_68175 | 13,758 | 3 | 379 | 5,847 | 7,529 |

Both records: human temporal neocortex, Brodmann area 21, layer 2–3, pyramidal/principal neuron. Dendrite completeness moderate; axon completeness incomplete. Type-2 points are not a full axonal reconstruction.

Both standardized CNG SWCs are retained unchanged under `amsn-core/data/human/segev/`, downloaded through NeuroMorpho official direct endpoints rather than copied from FCI. Validation found one root, unique IDs, no missing parent references, no malformed seven-field rows and positive radii. Git blob SHA1 and exact URLs are in `amsn-core/research/references/FCI_EYAL_SOURCE_MANIFEST_2026-11-21.json`.

## FCI passive parameters — SI conversion

| Region | FCI value | SI |
|---|---:|---:|
| All | Ra = 150 Ω·cm | 1.5 Ω·m |
| Soma/axon | Cm = 1 µF/cm² | 0.01 F/m² |
| Soma/axon | gpas = 1/20000 S/cm² | 0.5 S/m²; Rm = 2 Ω·m² |
| Dendrite | Cm = 2 µF/cm² | 0.02 F/m² |
| Dendrite | gpas = 2/20000 S/cm² | 1 S/m²; Rm = 1 Ω·m² |
| All | Eleak = -70 mV | -70 mV |

AMSN current validated baseline is uniform Ri=0.7 Ω·m, Rm=1 Ω·m², Cm=0.01 F/m², Eleak=-65 mV. They differ: FCI Ri is ~2.14× higher; soma/axon Rm is 2×; dendritic Cm is 2×; reversal is 5 mV more negative. Do not merge the configurations or tune one to match the other outside a named reproduction experiment.

## Na/Kv scaling — FCI-specific, not direct human measurements

Unscaled HOC reference densities: soma Kv/Na 200/830 pS/µm²; synthetic axon Kv/Na 2,000/8,300 pS/µm². Per-cell Python config scales soma and axon separately using ratios based on a rat Hay L5b exemplar. Target human rho values are labelled “from me” in FCI files.

| Cell | Soma scale | Axon scale | Soma Kv | Soma Na | Synthetic axon Kv | Synthetic axon Na |
|---|---:|---:|---:|---:|---:|---:|
| 1125 | 2.232660 | 2.665052 | 446.532 | 1,853.108 | 5,330.104 | 22,119.930 |
| 1204 | 2.246350 | 2.613995 | 449.270 | 1,864.470 | 5,227.990 | 21,696.159 |

Densities are pS/µm². Na/Kv MOD comments state a 37°C reference, while the human synapse setup sets h.celsius=34°C. Mechanisms use Q10=2.3 and a 23°C reference variable. Reconcile temperature/calibration with the publication/protocol before any reuse.

## FCI synapse configuration

- AMPA: E=0 mV, rise 0.3 ms, decay 1.8 ms, g=0.00088 µS = 0.88 nS.
- NMDA: rise 5 ms, decay 43 ms, gamma=0.078 mV⁻¹, g=0.00131 µS = 1.31 nS; ratio NMDA/AMPA≈1.489.
- GABAA: E=-80 mV, rise 0.2 ms, decay 8 ms, g=0.0007 µS = 0.70 nS.
- GABAB ratio zero; h.celsius=34°C and Mg-dependent NMDA block.
- MOD event handlers update deterministic exponential states; stochastic input spike trains/weights are generated upstream. Do not claim stochastic vesicle release or STP is implemented in these NET_RECEIVE blocks.

These values describe FCI’s reduced configuration, not universal human synaptic constants.

## Safe AMSN integration plan

Use separate named models:
1. AMSN-NMO290988-passive-v1 — existing validated baseline.
2. AMSN-Segev1125-passive-v1 and AMSN-Segev1204-passive-v1 — morphology-only comparisons with explicitly fixed generic passive parameters.
3. FCI1125-reduced-reproduction-v1 / FCI1204-reduced-reproduction-v1 — only after mechanism licensing, units and temperature assumptions are resolved.
4. Eyal2018-original-v1 — only after original official archive/source is acquired and hashed.

## Limits

Two additional partial human L2/3 cells do not represent the human population. Their axons are incomplete. No active-channel fitting, synapse fitting or experimental trace fitting is performed by this audit. Passive cross-simulator agreement is numerical validation, not biological validation. FCI functional-complexity metrics are model/protocol measures, not evidence of intelligence or consciousness. Original Eyal 2018 ModelDB source remains not downloaded / not integrated.
