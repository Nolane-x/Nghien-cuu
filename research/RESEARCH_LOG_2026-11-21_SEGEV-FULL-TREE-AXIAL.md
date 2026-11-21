# Research log — Segev full-tree axial geometry and topology audit — 2026-11-21

## Question

Does the Import3D geometry and NEURON segment/section topology preserve all electrically retained SWC cable edges and the expected axial resistance relationships across both Segev human L2/3 morphologies?

## Motivation

The full-tree axial network audit previously covered NMO_290988 only. The current Segev AC work leaves residuals below ~0.14% after soma-attachment normalization and fine mesh refinement. Probe interpolation is not a universal fix. Before changing any physics parameters, the same edge/ri/topology checks should be repeated directly on the two Segev SWCs.

## Method

The existing whole-tree audit is parameterized by:
- AMSN_MORPHOLOGY_PATH
- AMSN_MORPHOLOGY_LABEL
- AMSN_NEURON_MAX_SEGMENT_UM

It runs NEURON 9.0.2 with 0.5 µm maximum segment length and fixed Ra=0.7 Ω·m. It records:
- each electrically retained SWC edge and matching adjacent Import3D pt3d taper;
- all NEURON segment ri() values and their own pt3d geometry integrals;
- all branchpoint-to-child-section mappings;
- all section endpoint positions and both side half-resistance contributions;
- soma wire attachments separately from ordinary endpoint connections.

New CI gates fail on unmapped active edges, unexpected infinite ri(), internal/child-start/parent-end ri() mismatch above 1e-6%, branchpoint child-count mismatch, or non-soma endpoint gap above 0.001 µm.

## Verification

Pending GitHub Actions. Do not claim the multi-morphology extension is validated until both jobs pass and their raw CSV artifacts are inspected.

## Limits

NEURON and AMSN both consume the same SWC source; matching their geometry does not independently validate the morphology biologically. A zero-resistance soma wire connection is an import convention, not an anatomical statement.


## Follow-up: global axial conductance matrix

The next stage after the local edge/topology audit is recorded in HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md and the research log RESEARCH_LOG_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md. The matrix workflow passed 2/2 Segev cells; the axial-only operator is closely matched on 32 deterministic random voltage vectors. It is not a passive membrane or biological validation.
