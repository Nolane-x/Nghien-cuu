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


## Matched 7-port/9-port numerical replay completed

Successful GitHub Actions run 45314100588 passed the full AMSN suite, Tamas metadata/source tests, source hash, Import3D preflight, matched numerical replay, exact coverage, results commit and artifact upload. Artifact #14884183988; ZIP SHA-256 b01bbce48bc62931c10b78f5a97a8e334f26bd0ea186ede6335a92484b8d3808.

Preflight: 7,222 electrical compartments, 127 NEURON sections, 24,737 segments, maximum segment0.49997753 µm under0.5 µm cap. Seven shared ports [1,6363,4735,5564,7023,4301,4623]; q25 basal6609, apical4404.

Exact coverage:36 models,324 AC rows,1,728 transient rows,756 shared pairs,216 q25 observations,378 shared-Hines checks. All 378 shared Hines references were exactly equal (0 V difference).

Order112: 9-port worse on all 378 pairs; median 9/7 error ratio42.718×; maximum nine-port shared NRMSE3.9507e−5%. Order168:214 worse/164 better; median ratio1.00102×; maximum nine-port shared NRMSE5.4559e−7%. q25 maximum NRMSE3.5323e−5% at order112 and2.3679e−7% at order168.

At 10kHz, nine-port median Z/Y residuals 1.7339e−5%/1.8783e−4% at order112 and2.8131e−9%/2.9439e−7% at order168. Numeric storage6.3625MB at order112 and9.6874MB at order168. Runtime322s wall,408.14s user,144,420KiB peak RSS.

This is a diameter-recorded human pyramidal comparison cell (not rosehip interneuron) with complete arbors per metadata. It uses a0.5 µm mesh, same as Peng NMO_163775; earlier human holdouts use0.125 µm. The fourth holdout supports morphology-dependent port cost and shows order168 near parity for this cell. No production defaults changed.
