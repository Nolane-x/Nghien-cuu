# Research log — Segev passive AC probe-coordinate sensitivity — 2026-11-21

## Question

Does NEURON 9.0.2 produce materially different passive transfer impedance when a probe is read at its exact SWC section arc, at the nearest segment centre, or through complex interpolation between the adjacent segment centres?

## Method

- Morphologies: NMO_68174 / cell1125 and NMO_68175 / cell1204, direct NeuroMorpho CNG SWCs already attributed CC BY 4.0.
- NEURON 9.0.2, original imported morphology with 0.125 µm maximum segment length.
- Three source references: soma, basal q75, apical q75. Source is fixed at exact SWC-derived section coordinate.
- Five probes: soma, basal q50, basal q90, apical q50, apical q90.
- Eight frequencies: 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.
- Probe modes: exact SWC arc, nearest segment centre, and complex-linear interpolation between adjacent segment-centre impedances.
- Interpolation is performed in the complex plane, preserving phase consistently.
- Parameters unchanged: Ri=0.7 Ω·m, Rm=1 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.
- Expected output: 120 rows per morphology.

## Motivation: preceding three-reference source audit

Workflow 44899442076 passed both morphology jobs and produced 160 raw rows:
- NMO_68174 apical q75 source, legacy-to-exact transfer-complex max 0.021954%; exact-to-refined-centre effect 0% at exported precision.
- NMO_68175 basal q75 source, legacy-to-exact transfer-complex max 0.228926%; exact-to-refined-centre effect 0% at exported precision.
- NMO_68174 basal source was pre-aligned; NMO_68175 apical source unresolved under the NEURON nseg cap. Those rows were not valid distinct-source contrasts.
- Core CI workflow 44899349672 passed.

## Artifacts

- Implementation: amsn-core/examples/human_segev_ac_probe_coordinate_audit.py.
- Workflow: .github/workflows/amsn-segev-ac-probe-coordinate.yml.
- Raw measurements: Actions artifacts from the probe-coordinate workflow.

## Verification

Pending. Do not claim numerical results until both jobs pass and the raw CSVs have been inspected.

## Limits and next work

The test quantifies a numerical readout choice in NEURON, not the biological accuracy of either simulator. Linear interpolation between segment-centre impedance values is a diagnostic approximation; it must not be adopted as ground truth without support-aware validation. Next compare probe readout sensitivity with the existing cross-simulator residuals and then examine branchpoints/section joins and the full-tree passive voltage operator.
