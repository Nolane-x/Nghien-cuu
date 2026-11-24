# Handoff — NMO_107159 Tamas human pyramidal comparison cell

**Branch:** `research/prima-tamas-human-pyramidal-fourth-morphology-2026-11-24`  
**PR:** [#17](https://github.com/Nolane-x/Nghien-cuu/pull/17)

## Source lock

- NeuroMorpho ID NMO_107159; cell `Fig5c_141009_2og_B`; archive Tamas.
- Human female; age not reported.
- Frontal neocortex, layers 1 and 2–3; principal pyramidal cell.
- Control; in vitro; biocytin; Neurolucida; perpendicular slicing.
- Slice thickness70 µm; oil objective100×.
- Dendrites & Axon Complete; Diameter, 3D, Angles.
- DOI 10.1038/s41593-018-0205-2; PMID30150662.
- Correct source identity: pyramidal comparison cell shown in Fig.5C of the rosehip-cell paper, **not** a rosehip interneuron.

## Pinned SWC

`amsn-core/data/human/neuromorpho_tamas/NMO_107159_Fig5c_141009_2og_B.CNG.swc`

SHA-256: `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`.

7,228 records: soma3, axon4,030, basal1,767, apical1,428; one root; all nodes connected; no duplicate IDs or missing parents; three-point soma preserved.

## Port map

Seven shared SWC nodes:
`1, 5564, 6363, 7023, 4301, 4735, 4623`.

q25-only probes:
- Basal: 6609
- Apical: 4404

Preflight computes/stores q25 IDs and replay must reproduce them exactly.

## Experiment protocol

7/9 ports, orders112/168, six extended10kHz shifts, nine deterministic passive parameter scenarios, nine AC frequencies, three sources, two pulses and full-Hines shared-node comparisons.

Expected coverage: 36 model rows,324 AC rows,1,728 transient rows,756 shared pairs,216 q25 observations,378 Hines checks.

This branch uses a 0.5 µm NEURON mesh cap to align with Peng NMO_163775. The first two human fixtures used0.125 µm, so cross-morphology absolute errors are not directly comparable without mesh harmonization.

## Current validation state

Workflow run [45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588) has passed full suite, Tamas-specific tests, source checksum and Import3D preflight. The matched numerical replay remains in progress. Consult PR17 and the latest Actions run before claiming metrics.

Full Hines remains canonical. No production defaults change.

Official NeuroMorpho morphometry (API `/api/morphometry/id/107159`): total length 12,320.7 µm; mean diameter 0.285193 µm; 61 bifurcations; 126 branches; 4 stems; max path distance 1,662.83 µm; max Euclidean distance 1,420.16 µm; width 777.889 µm, height 1,595.1 µm, depth 91.47 µm; surface 9,693.02 µm²; volume 1,624.96 µm³. These are repository morphometry measurements/derived descriptors; passive membrane and axial parameters remain separate model assumptions.
