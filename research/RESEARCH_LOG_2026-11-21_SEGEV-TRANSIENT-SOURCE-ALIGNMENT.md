# Research log — Segev transient source-placement alignment — 2026-11-21

## Question

Does splitting the same 10 pA current pulse between adjacent NEURON segment centres using SWC arc interpolation weights better represent AMSN's exact SWC-node stimulus than a single nearest-centre IClamp?

## Motivation

The 12-job time/space matrix passed and showed:
- pairwise temporal differences halve at each dt halving, consistent with backward Euler;
- cross-simulator residuals barely change with dt;
- spatial effects are morphology-dependent, with NMO_68175 worsening at the 0.0625 µm mesh;
- source-centre offsets remain nonzero and vary with mesh.

The current transient baseline injects NEURON current at the nearest segment centre. This next experiment isolates that source placement choice.

## Method

New script: amsn-core/examples/human_segev_transient_source_alignment_audit.py.  
New workflow: .github/workflows/amsn-segev-transient-source-alignment.yml.

Compare nearest-segment-centre IClamp with two weighted IClamps at the adjacent segment centres. The weights are exactly the geometric interpolation weights already used for SWC-arc probe readout, and the sum of the amplitudes must remain 10 pA at every pulse sample.

## Verification

Pending. The four morphology/mesh jobs must all pass before results are reported.

## Limits

Weighted two-centre source placement is a discrete diagnostic approximation; it is not a claim of exact continuous point-current injection or biological validity.
