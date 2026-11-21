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

## Verified results — workflow 44901688035

Both NMO_68174 and NMO_68175 NEURON 9.0.2 jobs passed, with 120 rows each (3 sources × 5 probes × 8 frequencies). Raw artifact IDs:
- NMO_68174: 14706460979.
- NMO_68175: 14706590616.

Core CI [44901673896](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901673896) passed.

### Probe-coordinate measurements

Exact-SWC and nearest-segment-centre Impedance.transfer() results were identical at exported precision for all rows. Complex-linear interpolation of the adjacent segment-centre impedances changed transfer impedance by up to:
- NMO_68174: basal q50 0.001654%, basal q90 0.018746%, apical q50 0.024816%, apical q90 0.057785%; soma 0%.
- NMO_68175: basal q50 0.011556%, basal q90 0.001704%, apical q50 0.095872%, apical q90 0.040445%; soma 0%.

The effect is strongest at 3 kHz. The interpolation is diagnostic only.

### Cross-simulator residual join

The exact-SWC probe audit was joined one-to-one to the original 0.125 µm cross-simulator CSVs using the five identity columns. NEURON's exact transfer complex was compared with complex-linear interpolation, both against the same AMSN transfer complex.

NMO_68174:
- Exact-SWC median/p95/max cross-simulator transfer-complex error: 0.001555/0.049634/0.130599%.
- Interpolated median/p95/max: 0.000670/0.046984/0.132786%.
- 26 pairs improved, 70 worsened, 24 unchanged. The median and p95 decrease, but maximum error rises slightly.

NMO_68175:
- Exact-SWC median/p95/max: 0.002297/0.073495/0.169222%.
- Interpolated median/p95/max: 0.001105/0.059094/0.125637%.
- 64 pairs improved, 32 worsened, 24 unchanged. The worst basal-q75 → apical-q50 pair at 3 kHz decreases from 0.169222% to 0.077077%.

Conclusion: complex interpolation materially changes the cross-simulator residual, particularly for cell1204 apical probes, but its effect is morphology-/site-dependent and it is not uniformly superior. No default readout change is justified until the same audit is repeated at 0.25/0.125/0.0625 µm and the effect is assessed for convergence.

Next: [HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md](../HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md).
