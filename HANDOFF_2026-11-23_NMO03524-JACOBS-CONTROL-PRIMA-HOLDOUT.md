# Handoff — NMO_03524 Jacobs control PRIMA holdout

**Date:** 23 November 2026  
**Branch:** research/prima-jacobs-control-independent-holdout-2026-11-23  
**Base:** PR #13 branch, matched NMO_162186 7-port/9-port holdout

## Read first

1. amsn-core/data/human/neuromorpho_jacobs/NMO_03524_PROVENANCE.md
2. amsn-core/research/NMO_03524_JACOBS_CONTROL_PRIMA_HOLDOUT_2026-11-23.md
3. amsn-core/research/HUMAN_PASSIVE_PRIMA_ACCURACY_MEMORY_HOLDOUT_SYNTHESIS_2026-11-23.md
4. PR #13 and workflow 45184621520 for the matched NMO_162186 7-port/9-port result

## Validated source

- NeuroMorpho NMO_03524 / Jacobs / cell 1-5-3.
- Human, age 23, male; Control metadata; occipital neocortex, BA18; in vitro Golgi.
- Dendrites moderate; axon incomplete. One cell, not a population.
- 869 SWC records, one root, no missing parents; type counts 3 soma / 42 axon / 816 basal dendrite / 8 apical dendrite.
- Source bytes: 31,199; SHA-256: 6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748.
- Import3D/NEURON 9.0.2 preflight: 862 electrical compartments, 68 sections, 35,248 segments at max 0.125 µm, seven unique ports.
- One terminal SWC probe (node 751 at x=1.0) uses a nearest-endpoint-segment readout; no interpolation extrapolation is performed.

## Validated workflow

- Run 45196546471 passed 146/146 repository tests and the full morphology preflight.
- All nine PRIMA shift/order candidates reached their requested rank and passed Cholesky passivity checks.
- Exact coverage: 81 model rows, 729 frequency rows, 3,402 transient-port rows.
- Artifact #14827204708; ZIP SHA-256 21f3298613f7660908388ddebc4a0d9e3df88123b513d22b60fdc6edece19ed6.

## Decision for this morphology

- Order112 + extended10kHz is the high-frequency precision candidate: median 10 kHz Z/Y 3.60e−10% / 1.81e−10%; numeric storage 0.928 MB.
- Order84 + extended10kHz is the balanced candidate: median Z/Y 5.58e−7% / 2.88e−7%; storage 0.660 MB (~29% below order112).
- Order56 + narrow3kHz is the low-footprint choice: 0.416 MB, but median 10 kHz Z/Y residuals are 0.00857% / 0.00546%.
- Extended10kHz is the best high-frequency shift strategy for each of the tested orders on this holdout.

These are passive linear-RC numerical comparisons against full Hines, not active-neuron validation. Full Hines remains canonical and no production default changes.

## Next work

1. Run a matched 7-port/9-port order112/order168 test on NMO_03524. Until then do not claim the q25 conclusion transfers to the control morphology.
2. Add another independent morphology, ideally with a more complete axon.
3. Run controlled fixed-machine timing if runtime ranking becomes important.
4. Continue active/nonlinear model validation as a distinct research track.
