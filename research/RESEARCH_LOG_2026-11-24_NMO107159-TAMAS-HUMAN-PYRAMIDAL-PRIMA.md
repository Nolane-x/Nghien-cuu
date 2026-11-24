# Research log — fourth PRIMA morphology: NMO_107159

**Date:** 24 November 2026  
**PR:** #17  
**Source:** NeuroMorpho NMO_107159, Tamas archive

Selected a human frontal neocortical pyramidal comparison cell with diameter metadata, Dendrites & Axon Complete, Diameter/3D/Angles, Control, in vitro biocytin, 70 µm slice, DOI 10.1038/s41593-018-0205-2 / PMID30150662. The source study is about rosehip cells, but this cell is the pyramidal comparison shown in Figure 5C, not a rosehip interneuron. Age is not reported.

Pinned standardized SWC at `amsn-core/data/human/neuromorpho_tamas/NMO_107159_Fig5c_141009_2og_B.CNG.swc`; SHA-256 6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023. It has 7,228 records: soma3, axon4,030, basal1,767, apical1,428; a single root; all nodes connected; no duplicate IDs/missing parents; valid three-point soma.

Seven candidate shared SWC ports: [1,5564,6363,7023,4301,4735,4623]. q25 probes: basal6609, apical4404. Import3D preflight pins the seven; q25 IDs are emitted by preflight and independently required to match replay.

The matched 7/9-port order112/order168 matrix mirrors the prior holdouts and uses 0.5 µm segment cap, same as Peng NMO_163775. Earlier human runs used0.125 µm, so absolute cross-morphology errors require mesh harmonization.

Workflow 45314100588 passed full regression, source/metadata tests, SHA-256 and Import3D preflight. Numerical replay pending when this log was written. No production defaults or canonical Hines behavior changed.

Official NeuroMorpho morphometry (API `/api/morphometry/id/107159`): total length 12,320.7 µm; mean diameter 0.285193 µm; 61 bifurcations; 126 branches; 4 stems; max path distance 1,662.83 µm; max Euclidean distance 1,420.16 µm; width 777.889 µm, height 1,595.1 µm, depth 91.47 µm; surface 9,693.02 µm²; volume 1,624.96 µm³. These are repository morphometry measurements/derived descriptors; passive membrane and axial parameters remain separate model assumptions.
