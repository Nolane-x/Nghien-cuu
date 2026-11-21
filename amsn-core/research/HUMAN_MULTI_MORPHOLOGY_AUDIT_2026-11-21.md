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

## Root cause found — missing immediately branching axon attachment

Latest geometry run [44886628293](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44886628293) shows NMO_68175's NEURON total area is 83,861.8731579 µm² while AMSN is 84,538.3504114 µm², a difference of 676.4772535 µm² (−0.8002016%). The SWC edge from soma root 1 to axon node 5851 has a frustum area of 676.4765820 µm² and length 12.06765097 µm. NEURON's imported axon path is 676.4514768 µm versus 688.5191355 µm from SWC, again omitting that exact first edge to within 8e−6 µm.

Node 5851 is a direct root child and immediately branches (two children). The previous detector only marked first neurite nodes with more than one unbranched same-type edge, so it missed this axon attachment. The normalizer now treats every direct non-soma child of a verified three-point soma as an attachment, preserving the later SWC edges. The physical passive constants are unchanged. The next four-job matrix rerun must confirm area agreement and lower low-frequency impedance errors.

## Negative regression preserved

The first broad attachment rule made a synthetic one-point terminal neurite disappear; Core CI caught this. The detector is now narrower: it preserves the existing long unbranched stem rule and additionally treats a first neurite point that is itself an immediate branch junction as a soma attachment. A lone terminal child is retained as membrane. The Segev test continues to require NMO_68175 node 5851 (two children) to collapse.
