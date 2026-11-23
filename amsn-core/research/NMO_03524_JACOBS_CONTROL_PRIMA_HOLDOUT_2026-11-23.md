# Independent PRIMA shift/order validation on NMO_03524 Jacobs control morphology

**Date:** 23 November 2026  
**Morphology:** NeuroMorpho NMO_03524 / Jacobs / 1-5-3  
**Status:** source and workflow added; numerical replay pending GitHub Actions

## Why this holdout matters

The existing NMO_162186 holdout is a human epilepsy surgical specimen with incomplete axon. This experiment adds a distinct published **Control-condition** human cortical pyramidal morphology from the Jacobs archive. Its source article used Golgi reconstructions; the cortical region is occipital Brodmann area 18.

The record is not treated as a pristine complete neuron: NeuroMorpho labels dendrites moderate and axon incomplete. It is a single-cell control-condition morphology, not a population sample.

## Source and preflight

- NeuroMorpho ID NMO_03524; cell 1-5-3.
- 23-year-old male; human neocortex, occipital, BA18.
- Control, in vitro, Golgi, 120 µm slice.
- Soma, basal and apical dendrites plus incomplete axon.
- Source URL and metadata page are listed in the provenance file.
- The CI downloads the standardized SWC, computes SHA-256 and byte size, checks exact 869-record topology and type counts (1:3, 2:42, 3:816, 4:8), validates parent references and three-point soma, imports it through NEURON 9.0.2 at a 0.125 µm segment cap, and confirms seven unique PRIMA ports and a finite passive response.

The computed immutable SHA-256 and Import3D/port map are archived in the preflight JSON.

## Numerical experiment

Reuses the validated seven-port PRIMA shift/order matrix:

- Orders: 56, 84 and 112.
- Shift distributions: narrow 3 kHz, extended 10 kHz, balanced 10 kHz.
- Nine deterministic passive parameter scenarios: nominal, Rm ±20%, Cm ±20%, Ra ±20%, all parameters −20%, all parameters +20%.
- AC frequencies: 0.1 Hz to 10 kHz (nine points).
- Source ports: soma, basal-q75, apical-q75.
- Transients: 2 ms and 10 ms square pulses; 10 pA; 2 ms onset; 20 ms total; 0.1 ms timestep.
- Reference: full Hines on the same exact morphology and parameter scenario.
- Coverage: 81 model rows, 729 frequency rows and 3,402 transient-port rows.

All candidates must achieve the requested order and pass Cholesky checks on their reduced conductance/capacitance matrices. The summarizer fails closed if any candidate or output row is absent or non-finite.

## Outputs

- Pinned source SWC: \`data/human/neuromorpho_jacobs/1-5-3.CNG.swc\`
- Provenance: \`data/human/neuromorpho_jacobs/NMO_03524_PROVENANCE.md\`
- Preflight: \`results/NMO_03524_JacobsControl_holdout/preflight.json\`
- Port mapping: \`results/NMO_03524_JacobsControl_holdout/port_mapping.csv\`
- Candidate model/frequency/transient tables and summary JSON/CSV under \`results/\`.

## Scientific limits

This is one control-condition human morphology with moderate dendritic completeness and incomplete axon. It broadens the external numerical holdout context; it does not establish population-level validity or active-neuron biology. No solver/default/runtime setting is changed.
