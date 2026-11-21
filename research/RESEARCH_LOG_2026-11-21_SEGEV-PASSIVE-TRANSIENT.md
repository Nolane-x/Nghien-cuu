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


## Verified results — native passive transient comparison

Workflow [44907890895](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895) passed 2/2 cells; Core CI [44907890934](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934) passed 4/4 jobs.

NMO_68174: 9,015 trace rows, 30 summary rows; maximum nearest-centre/interpolated waveform NRMSE 0.001641% / 0.000357%; maximum peak-amplitude error 0.002166% / 0.000393%; maximum absolute waveform error 5.147e-6 / 1.531e-6 mV.

NMO_68175: 9,015 trace rows, 30 summary rows; maximum NRMSE 0.002370% / 0.000791%; maximum peak error 0.003375% / 0.001106%; maximum absolute waveform error 4.424e-6 / 1.459e-6 mV.

All peak-time differences were zero at the 0.05 ms sampling grid. The current pulse was confirmed as 0.01 nA for 200 intervals in NEURON, matching the AMSN 10 pA left-edge input. Source-centre and probe-centre offsets were preserved in the summary CSVs.

See [HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md](../research/HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md). Next: factorial dt/mesh convergence.
