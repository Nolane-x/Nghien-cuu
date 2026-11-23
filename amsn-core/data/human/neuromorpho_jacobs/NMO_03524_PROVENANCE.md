# NMO_03524 — Jacobs human control morphology provenance

**NeuroMorpho.Org ID:** NMO_03524  
**Cell name:** 1-5-3  
**Archive:** Jacobs  
**Source URL:** https://neuromorpho.org/dableFiles/jacobs/CNG%20version/1-5-3.CNG.swc  
**Metadata:** https://neuromorpho.org/neuron_info.jsp?neuron_name=1-5-3

## Published metadata

- Species: human.
- Experimental condition: Control.
- Age/sex: 23-year-old male.
- Brain region: neocortex, occipital cortex, Brodmann area 18.
- Cell class: principal cell, pyramidal.
- Structural domains: soma, dendrites and axon.
- Physical integrity: dendrites moderate; axon incomplete.
- Experimental protocol: in vitro.
- Staining: Golgi.
- Slice thickness: 120 µm.
- Reconstruction: Neurolucida.
- Related source article: *Life-span dendritic and spine changes in areas 10 and 18 of human cortex: a quantitative Golgi study*.

## Pinned standardized SWC

- Source bytes: 31,199.
- SHA-256: 6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748.
- SWC records: 869; one soma root; no missing parent references.
- Type counts: soma 3, axon 42, basal dendrite 816, apical dendrite 8.
- Branch points: 30; total path length: 4,453.468 µm.

## Import3D preflight

- NEURON version: 9.0.2.
- Sections: 68; segments: 35,248.
- Maximum segment length: 0.12499949 µm (configured cap 0.125 µm).
- AMSN electrical compartments: 862.
- Seven PRIMA ports: soma; basal q50/q75/q90; apical q50/q75/q90.
- A 1 kHz passive response was finite.

The basal-q90 SWC point (node 751) is at normalized section x=1.0, beyond the last NEURON segment centre. The shared probe mapper records an explicit right-endpoint nearest-segment fallback (0.06250 µm centre offset) rather than extrapolating outside the segment-centre interval.

## Intended use

This is an independent control-condition human morphology holdout for passive linear-RC PRIMA shift/order validation. It is from a different archive and experimental context than the NMO_162186 epilepsy specimen. The source has a three-point soma, basal and apical dendrites, and a partial axon.

## Limitations

- One morphology is not a population sample.
- “Control” is the published archive metadata; this does not establish absence of every neurological condition beyond the study's stated classification.
- Dendrites are rated moderate and the axon incomplete.
- The experiment validates passive linear-RC numerical reduction only; it does not validate active ion channels, nonlinear synapses, action potentials, plasticity or biological function.
- The morphology is used as a numerical holdout, not to estimate or tune biological conductances.

NeuroMorpho.Org is the source repository; follow its data-use terms and cite the archive and associated study. No production model or default is changed by this research phase.
