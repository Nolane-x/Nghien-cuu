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

## Verified Import3D soma-attachment fix — final results (commit f63b3ce)

**Status:** resolved for the tested Import3D soma convention on both Segev morphologies; 4/4 multi-morphology jobs passed. Core CI also passed 4/4 jobs, including 81 tests on Python 3.12 and 81 on Python 3.13.

### Root cause and narrow correction

At NMO_68175, SWC node 5851 is a direct soma child of type axon and immediately branches into two children. The old detector only collapsed first neurite roots that continued as a long unbranched same-type stem, so it missed 5851. The NEURON importer did not retain the soma-centre-to-node-5851 edge as cable geometry. That edge has SWC frustum area 676.4765820 µm² and length 12.06765097 µm; this matched the pre-fix NEURON-versus-AMSN area residual (676.4772535 µm²) and axonal path-length difference (~12.06766 µm).

The final rule collapses (a) established long unbranched soma stems and (b) first neurite points that are themselves branch junctions (two or more children). A one-point terminal neurite is retained. The first attempt that collapsed every direct soma child was rejected by Core CI because it removed a synthetic terminal edge; this negative result is preserved in the source tests and handoff.

### Four-job rerun — NEURON 9.0.2

Each job ran the full AMSN test suite and compared 3 sources × 5 probes × 8 frequencies = 120 rows. Passive parameters remained fixed at Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.

| Morphology | NEURON max segment | NEURON segments | AMSN compartments | NEURON−AMSN area difference | Input complex median / p95 / max | Transfer complex median / p95 / max | Transfer magnitude max | Transfer phase max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NMO_68174 / cell1125 | 0.25 µm | 83,518 | 12,399 | −0.00000112% | 0.017741 / 0.037584 / 0.069900% | 0.005078 / 0.148567 / 0.364677% | 0.252771% | 0.150799° |
| NMO_68174 / cell1125 | 0.125 µm | 166,856 | 12,399 | −0.00000112% | 0.001938 / 0.040144 / 0.050504% | 0.001555 / 0.049609 / 0.130503% | 0.073582% | 0.062811° |
| NMO_68175 / cell1204 | 0.25 µm | 78,339 | 13,747 | −0.00000080% | 0.030424 / 0.065690 / 0.065898% | 0.010371 / 0.200269 / 0.393877% | 0.300621% | 0.146032° |
| NMO_68175 / cell1204 | 0.125 µm | 156,471 | 13,747 | −0.00000080% | 0.005663 / 0.035136 / 0.037737% | 0.002297 / 0.073511 / 0.169384% | 0.095953% | 0.085278° |

Area agreement is now better than 0.0000012% on both cells. For NMO_68175 at 0.125 µm, input complex maximum error fell from 5.68778% pre-fix to 0.03774% (~151× smaller); transfer complex maximum fell from 5.70172% to 0.16938% (~33.7× smaller). At 0.25 µm, the corresponding maxima fell from 5.68794% to 0.06590% input and from 5.92099% to 0.39388% transfer. These results validate the importer/conversion fix for the tested cells/configuration, not biological parameters.

### CI and raw artifacts

- Four-morphology matrix [run 44887065310](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310), 4/4 jobs successful.
- [NMO_68174, 0.25 µm artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699778704)
- [NMO_68175, 0.25 µm artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699833538)
- [NMO_68174, 0.125 µm artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699989410)
- [NMO_68175, 0.125 µm artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14700104294)
- Core CI [run 44887065325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065325), 4/4 jobs successful: 81/81 tests on Python 3.12 and 81/81 on Python 3.13; NEURON passive, temporal/spatial convergence, transient pulse/step, AMPA-like conductance, Exp2Syn event timing, matched single-compartment checks passed.
- [Python 3.12 NEURON raw validation artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065325/artifacts/14700805022); [Python 3.13 artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065325/artifacts/14700313358).
## Fine-mesh follow-up — 0.0625 µm (run 44887397930)

Both morphology jobs passed the full 81-test AMSN suite and NEURON 9.0.2 AC audit (120 measurements per cell). Segment counts doubled from the 0.125 µm reference, while membrane areas and normalized soma/attachment geometry remained unchanged to numerical precision.

| Morphology | NEURON segments | Area difference | Input complex median / p95 / max | Transfer complex median / p95 / max | Transfer magnitude max | Transfer phase max |
|---|---:|---:|---:|---:|---:|---:|
| NMO_68174 / cell1125 | 333,452 | −0.00000112% | 0.005932 / 0.036530 / 0.047282% | 0.001221 / 0.052982 / 0.133856% | 0.073723% | 0.064037° |
| NMO_68175 / cell1204 | 312,745 | −0.00000080% | 0.013756 / 0.031304 / 0.038863% | 0.003012 / 0.059594 / 0.099423% | 0.089533% | 0.030780° |

Mesh refinement is not monotone for every summary statistic. NMO_68174's transfer median improves from 0.001555% to 0.001221%, but p95 and max rise slightly (0.049609→0.052982%; 0.130503→0.133856%). NMO_68175's p95 and max improve (0.073511→0.059594%; 0.169384→0.099423%), while its median rises (0.002297→0.003012%). The worst pair and source/probe segment-centre offsets can change as the mesh changes. Therefore no universal 'finer is always better for every percentile' claim is justified.

Raw artifacts: [NMO_68174 0.0625 µm, artifact 14700676187](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14700676187); [NMO_68175 0.0625 µm, artifact 14700169600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14700169600).

The combined results (0.25/0.125/0.0625 µm) are in `amsn-core/results/human_segev_import3d_attachment_fix_summary_2026-11-21.csv`; the per-frequency fine-mesh table is in `amsn-core/results/human_segev_import3d_attachment_fix_0p0625_frequency_2026-11-21.csv`.

Interpretation: the missing soma/axon attachment was the dominant NMO_68175 discrepancy and is now fixed. The remaining ~0.1% transfer-complex tail is small, morphology-/site-dependent and high-frequency weighted; the mesh results do not yet prove a continuum limit or experimental biological accuracy.

## Residual localization from the raw source–probe CSVs

The raw artifacts were extracted and inspected, rather than relying only on workflow summaries. The [pair-residual localization note](SEGEV_FINE_MESH_RESIDUAL_LOCALIZATION_2026-11-21.md) records the worst pair at 3 kHz for both meshes, source/probe centre offsets, absolute impedance, and descriptive rank correlations. Error is consistently more associated with log-frequency (Spearman 0.747–0.833) than with either centre offset alone; the latter varies by cell and by source/probe. The 0.0625 µm worst pair changes for NMO_68175 but not NMO_68174. These are repeated-measure descriptive statistics and do not prove a causal effect. The next planned experiment is a matched-support source/probe placement audit, not blind further mesh refinement.


## Controlled DC source-placement audit generalized to Segev morphologies

The same-mesh source-placement experiment is now parameterized by morphology path/label, base mesh, source-alignment tolerance and NEURON nseg cap through environment variables. This lets it compare legacy-centre and SWC-aligned source placements on the two Segev cells without changing passive parameters or probes. It is a DC steady-state control; it does not replace the AC audit. A dedicated two-morphology workflow is added next.


## Source-placement control: bounded NEURON nseg strategy

The first Segev source-placement workflow passed all 81 tests but could not construct two distinct source centres with the old exact-preservation odd-multiple refinement under NEURON's per-section nseg cap of 32,767. The YAML path and matrix expressions have been fixed; this is a separate algorithmic limit.

The source-placement helper now searches odd nseg values up to the configured cap, maps the old legacy source coordinate to the nearest centre on the final mesh, and separately maps the exact SWC arc to a distinct centre. Both modes still share the same final section nseg, morphology, cable and probe discretization. The legacy coordinate remap is recorded explicitly rather than assumed to be zero. It rejects cases that cannot meet the alignment tolerance or produce distinct centres under the cap. This bounded redesign is pending CI and a successful Segev source-placement rerun.


## Placement-control edge case: source already aligned

On NMO_68174, one source section (dend[26]) has its original nearest segment centre only 1.535e-7 µm from the SWC target. Under the 0.002 µm tolerance it is already aligned. The control now records this explicitly and uses the same segment in both modes; it does not invent a different clamp location merely to force a difference. Other sources still require distinct legacy/aligned centres on one shared mesh. This refinement is pending CI.
