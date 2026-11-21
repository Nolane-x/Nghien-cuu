# Preliminary multi-morphology passive AC validation — 2026-11-21

**Status:** four-job matrix passed; NMO_68174 is mesh-sensitive and improves; NMO_68175 has a persistent discrepancy requiring geometry/import investigation. This is not yet a validated two-cell cross-simulator result.

## Protocol

- AMSN morphology inputs: NeuroMorpho NMO_68174 (cell 1125) and NMO_68175 (cell 1204), direct standardized CNG SWC files.
- Reference: NEURON 9.0.2 / Import3D.
- Same fixed passive parameters as the current AMSN baseline: Ri=0.7 Ω·m, Rm=1 Ω·m², Cm=0.01 F/m², Eleak=-65 mV.
- Three source locations × five probes × eight frequencies (0.1–3,000 Hz) = 120 source/probe/frequency rows per morphology/mesh.
- Mesh caps: 0.25 and 0.125 µm.
- Workflow: [44885009077](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077), all 4/4 matrix jobs passed, including full test suite.

## Preliminary result

| Morphology | NEURON mesh cap | Rows | Maximum transfer complex error |
|---|---:|---:|---:|
| NMO_68174 / cell 1125 | 0.25 µm | 120 | ~0.365% |
| NMO_68174 / cell 1125 | 0.125 µm | 120 | ~0.131% |
| NMO_68175 / cell 1204 | 0.25 µm | 120 | ~5.7% |
| NMO_68175 / cell 1204 | 0.125 µm | 120 | ~5.7% |

NMO_68174 shows the expected improvement as the NEURON mesh is refined.

NMO_68175 does not show a comparable improvement. Its input-complex discrepancy is already approximately 0.94% at 0.1 Hz, while its transfer-complex maximum reaches approximately 5.7% at 3 kHz. This is evidence of a persistent difference in the discretized geometry/import/compartment mapping, not evidence that the shared passive constants should be changed. The result must not be hidden by averaging across the two cells.

## Raw artifacts

- [NMO_68174, 0.25 µm — artifact 14699064700](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077/artifacts/14699064700)
- [NMO_68174, 0.125 µm — artifact 14699099470](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077/artifacts/14699099470)
- [NMO_68175, 0.25 µm — artifact 14699582231](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077/artifacts/14699582231)
- [NMO_68175, 0.125 µm — artifact 14699582225](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077/artifacts/14699582225)

## Required diagnostic steps

1. Compare total membrane area from AMSN's (\sum A_i\) and NEURON's `sum(seg.area())` for each morphology and mesh.
2. Compare normalized soma root, soma three-point nodes, wire-attachment IDs and the number/length of collapsed wires.
3. Compare NEURON section count and segment count with AMSN compartments and branch/junction counts.
4. Inspect source/probe SWC node IDs, branch identity and nearest-segment-centre offsets, especially for the NMO_68175 axon/soma junction.
5. Re-run at both mesh caps after fixing only a demonstrated import/mapping defect; do not change the biological passive parameters.
6. Only call the result converged after area, DC input and AC transfer residuals have a clear numerical explanation.

## Limits

These are two individual human temporal L2–3 morphologies with moderately complete dendrites and incomplete axons. No active-channel/synapse fitting or experimental trace validation was performed. Numerical agreement between two simulators is not biological validation.


## Import3D geometry diagnostics added (pending rerun)

The audit now emits:
- total SWC tapered-frustum area and path length by neurite type;
- total NEURON segment area by Import3D section type;
- NEURON section signatures (count, nseg, n3d points, area and length) by type;
- normalized spherical soma radius/area and each collapsed soma wire attachment's Import3D section identity, first-point flag and local point count;
- source/probe SWC IDs, selected Import3D section/x and nearest segment-centre offset.

This is intended to isolate why NMO_68175 has a low-frequency discrepancy that is nearly mesh invariant. No cause is assigned until the new logs and area ledgers are compared.
