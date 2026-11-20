# Handoff — AMSN passive cable cross-validated against NEURON 9.0.2

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Final code commit:** 56eaf350334a3f1795f4070edc5b96a1748fcc89  
**CI:** [44745099560 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44745099560)

## Read first
1. AGENTS.md
2. HANDOFF.md
3. HANDOFF_2026-11-20_HUMAN-SECTIONED-MESH.md
4. This handoff.
5. amsn-core/research/NEURON_PASSIVE_CROSS_VALIDATION_2026-11-20.md
6. amsn-core/results/neuron_passive_cross_validation_2026-11-20.csv
7. amsn-core/data/human/README.md and provenance JSON.

## Cell and data provenance
NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc: human temporal-cortex BA21 layer 2–3 pyramidal/principal cell; soma + dendrites, no axon; dendritic integrity moderate; metadata records mesiotemporal sclerosis; shrinkage not reported. It is not a complete or healthy-control neuron. Preserve CC BY 4.0 attribution in the data README.

## Critical Import3D normalization

The source morphology meets NEURON Import3D's special three-point soma conditions:
- first three SWC records are type 1;
- two soma outline points are direct leaf children of root;
- equal diameters;
- summed root-to-outline distances 17.120467 µm vs diameter 17.13 µm (within 1%).

NEURON replaces it with a spherical soma (area 921.859209332 µm²). Eight long soma-attached neurite roots are treated as zero-resistance wire attachments and their incoming edges are omitted from membrane/axial cable geometry.

AMSN now detects exactly this standardized pattern. SWCMorphology.detect_neuromorpho_three_point_soma() returns the normalization record; electrical_node_mapping() maps original soma-outline and wire-root SWC IDs to the single soma electrical vertex. to_cable_tree() and to_sectioned_cable_tree() apply it by default. Set normalize_neuromorpho_soma=False to inspect the unnormalized point cable. Raw morphology and IDs are never modified.

## Verified results

GitHub Actions run 44745099560:
- Python 3.12.16 — 46 passed in 1.55 s.
- Python 3.13.18 — 46 passed in 1.98 s.
- NEURON 9.0.2 Import3D validation passed in both jobs.

NEURON: 125 sections, 2,637 segments, odd nseg, max physical segment 5 µm. AMSN fine normalized tree 8,893 compartments. AMSN sectioned tree 690 compartments (92.24% fewer). Same generic passive defaults in both simulators: Ri=.7 Ω·m, Rm=1 Ω·m², Cm=.01 F/m², Eleak=-65 mV; 10 pA injection; 3 sources × 5 probes.

Area:
- NEURON: 23,338.438806144 µm²;
- AMSN normalized: 23,338.439002801 µm²;
- relative difference: −0.000000843%.

Maximum relative errors over the 15 pairs:

| Metric | Fine AMSN | Sectioned AMSN |
|---|---:|---:|
| Input resistance | 0.422794% | 0.463750% |
| Transfer resistance | 0.517393% | 0.560092% |
| Transfer ratio | 0.664039% | 0.685124% |

All 15 measurement rows match between Python versions. NEURON voltage changed by at most 1e-9 mV between 200 and 250 ms. Maximum SWC-point to NEURON segment-centre offset: 2.424330 µm; PT3D geometry mapping error itself <0.00003 µm.

## What this establishes—and what it does not

This is cross-simulator numerical validation of a passive linear 1-D cable on one partial human morphology. It supports the SWC geometry conversion, Import3D soma/wire convention and DC Hines solver. It is not an experimental fit or biologically complete neuron. No active channels, synapses, calcium, glia, gene expression, metabolism, plasticity or axon are validated.

## Next concrete work
1. Run NEURON timestep convergence: dt 0.0125 and 0.00625 ms, keeping the same geometry.
2. Run segment convergence: max segment 2.5 and 1.25 µm, record convergence for the same 15 pairs.
3. Compare transient passive step and synaptic-like current responses, not only DC.
4. Validate another license-cleared human L2–3 morphology and preserve cell-level clinical/completeness metadata.
5. Only then reproduce a published human L2–3 active model unchanged before fitting channel parameters.

Never call the model a complete or biologically calibrated human neuron from this result alone.
