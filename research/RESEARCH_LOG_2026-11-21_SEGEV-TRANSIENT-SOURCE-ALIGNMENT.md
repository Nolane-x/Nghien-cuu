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


## Verified results — source-placement alignment

Workflow [44910070325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325) passed 4/4 morphology/mesh jobs; Core CI [44910070326](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326) passed 4/4.

Every configuration produced 18,030 trace rows and 60 summaries. Maximum total IClamp current-conservation error was 1.735e-18 nA.

NMO_68175 weighted source placement improved all non-unchanged pairs on interpolated probes at both meshes (10 improved, 0 worsened, 5 unchanged). Maximum interpolated NRMSE fell to 0.000192% at both mesh caps, versus 0.000791% at 0.125 µm and 0.002633% at 0.0625 µm under nearest-centre injection.

NMO_68174 was mixed at 0.125 µm (5 improved, 5 worsened, 5 unchanged for each probe readout). At 0.0625 µm, weighted source placement worsened all 10 non-unchanged interpolated probe pairs, and improved only 2/15 nearest-centre pairs.

Thus weighted two-centre injection is an optional diagnostic, not a universal default.

See [HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](../research/HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md).
