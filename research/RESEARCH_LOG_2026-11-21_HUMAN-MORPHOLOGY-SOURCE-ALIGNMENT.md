# Research log — independent morphology source-alignment replication — 2026-11-21

## Question

Does the transient/AC source-placement result reproduce on a third, distinct human morphology record already used by the AMSN full-tree audits?

## Candidate

NMO_290988 / 1094_Mohan_etal_2015, NeuroMorpho.Org, DeKock archive. The standardized CNG SWC has 8,903 records, soma plus basal/apical dendrites, no axon, and moderate dendritic completeness. Its metadata records mesiotemporal sclerosis. Do not describe it as a healthy control.

The source file and CC BY 4.0 attribution are documented in amsn-core/data/human/README.md and 1094_Mohan_etal_2015.provenance.json.

## Method

New workflow: .github/workflows/amsn-human-morphology-source-alignment.yml.

Six matrix jobs: three morphology records × two NEURON mesh caps (0.125/0.0625 µm). Each job runs the full test suite, validates SWC record counts and Import3D source/probe mapping, then runs both transient and AC source-placement comparisons with all raw measurements preserved.

## Expected outputs

Per morphology/mesh:
- transient source placement: 18,030 traces, 60 summaries;
- AC source placement: 1,080 raw rows, 135 grouped summaries.

## Verification

Pending. Do not generalize a source-placement rule until all six jobs pass and the third-cell raw outputs have been inspected.

## Limits

The third record is a distinct neuron and archive, but the three samples are not a broad population study. NMO_290988 has no axon, moderate dendritic integrity and a recorded mesiotemporal sclerosis context.
