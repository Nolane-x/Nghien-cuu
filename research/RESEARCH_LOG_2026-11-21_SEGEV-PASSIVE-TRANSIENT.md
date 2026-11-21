# Research log — Segev native passive transient cross-validation — 2026-11-21

## Question

Do native NEURON 9.0.2 fine-segment passive transients agree with AMSN's unresampled SWC CableTree for identical step-current inputs and backward-Euler time stepping?

## Motivation

The Segev matched-support passive admittance operator passed with sampled relative L2 maxima of 0.0078381% (NMO_68174) and 0.0025449% (NMO_68175). That result compared a projected node-support operator, not the original native NEURON segment-level tree. A direct time-domain check is the next independent validation axis.

## Method

New script: amsn-core/examples/human_segev_passive_transient_audit.py.  
New workflow: .github/workflows/amsn-segev-passive-transient.yml.

Both simulators use a 10 pA rectangular pulse from 2 to 12 ms, total duration 30 ms and dt 0.05 ms. NEURON uses h.secondorder=0 (fully implicit backward Euler); AMSN uses CableTree.step_passive (backward Euler). NEURON imports the SWC at a 0.125 µm mesh cap.

Three source positions and five probe positions are shared by the prior AC experiments. Raw traces record the AMSN voltage, NEURON nearest-centre voltage and NEURON linearly interpolated voltage at the exact SWC arc readout.

Expected per cell: 9,015 trace rows and 30 summary rows.

## Verification

Pending. Inspect both raw trace CSVs, especially the source-centre offsets and absolute voltage magnitudes, before drawing a conclusion.

## Limits

This is native fine-tree NEURON versus node-centred AMSN transient comparison. It is distinct from the matched-support projected operator and is not biological validation.
