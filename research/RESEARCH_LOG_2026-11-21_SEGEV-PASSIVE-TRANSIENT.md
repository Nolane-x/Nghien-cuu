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

## Verified time/space transient convergence — 21/11/2026

Workflow [44908381318](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318) passed 12/12 jobs; Core CI [44908381336](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336) passed 4/4. The matrix covered two cells × mesh 0.125/0.0625 µm × dt 0.1/0.05/0.025 ms, producing 126,180 raw trace rows.

Temporal pairwise errors halve closely when dt halves:
- NMO_68174: maximum pairwise NRMSE 0.186066% for 0.1→0.05 ms, and 0.093728% for 0.05→0.025 ms (ratio 1.985).
- NMO_68175: 0.176664% and 0.089052% (ratio 1.984).

Cross-simulator mismatch remains nearly unchanged with dt at fixed mesh. Spatial refinement is not uniform:
- NMO_68174 improves at 0.0625 µm (nearest max NRMSE 0.001286%; interpolated 0.000190%).
- NMO_68175 worsens at 0.0625 µm (nearest 0.002580%; interpolated 0.002632%), and interpolation is no longer better than nearest-centre.

Direct NEURON mesh-to-mesh waveform changes have maximum pairwise NRMSE 0.000480% (cell1125) and 0.003862% (cell1204). AMSN traces are invariant across NEURON mesh settings.

See [HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md](../research/HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md) and the two configuration/pairwise CSVs under ../results.
