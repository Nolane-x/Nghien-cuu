# Research log — Segev Import3D soma attachment correction — 2026-11-21

## Research question
Why did NMO_68175 / cell1204 retain ~5.7% passive AC impedance mismatch across 0.25 and 0.125 µm NEURON meshes while NMO_68174 improved normally?

## Hypothesis and source evidence
Hypothesis: AMSN incorrectly retained a soma-centre-to-first-axon SWC edge that NEURON Import3D treats as a soma attachment rather than neurite cable.
Source data: direct NeuroMorpho CNG SWCs NMO_68174 and NMO_68175, unchanged and attributed CC BY 4.0. Both human temporal neocortex BA21 L2–3 pyramidal/principal morphologies; dendrites moderately complete, axons incomplete.

## Diagnostic result (run 44886628293)
- NMO_68175 NEURON area 83,861.8731579 µm²; AMSN area before fix 84,538.3504114 µm²; difference 676.4772535 µm².
- SWC root→axon node 5851 edge length 12.06765097 µm; frustum area 676.4765820 µm². Node 5851 has two children, i.e. immediate bifurcation.
- NEURON axon path 676.4514768 µm vs SWC path 688.5191355 µm, with difference matching first edge.
- This identified an importer normalization rule gap, not passive parameter miscalibration.

## Implementation and negative result
- First broad rule (collapse all first neurite children) failed Core CI because it removed a synthetic one-point terminal neurite. Preserve this negative result.
- Final rule: collapse established long unbranched stems AND first neurite nodes that are themselves immediate branch junctions (>=2 children); preserve lone terminal neurites.
- Added regression tests for NMO_68175 node 5851 and for the synthetic terminal-neurite negative case.
- No passive constants changed: Ri=0.7 Ω·m, Rm=1 Ω·m², Cm=0.01 F/m², Eleak=−65 mV.

## Verified tests and experiment
- Commit: f63b3ce89344207f504dcc47a869be59cc21f438.
- Multi-morphology NEURON 9.0.2 workflow 44887065310: 4/4 jobs success, 120 rows per cell/mesh.
- Core CI 44887065325: 4/4 jobs success; Python 3.12 81/81 and Python 3.13 81/81 tests; NEURON checks passed for passive cross-validation, temporal/spatial convergence, transient pulse/step, AMPA-like conductance, Exp2Syn event timing and matched single compartment.

## Results
- NMO_68175 area discrepancy reduced from 0.8002% to 0.00000080%.
- NMO_68175 at 0.125 µm: input complex error median/p95/max 0.005663/0.035136/0.037737%; transfer complex 0.002297/0.073511/0.169384%.
- NMO_68175 at 0.25 µm: input max 0.065898%; transfer max 0.393877%.
- NMO_68174 is unchanged and remains below 0.365% transfer-complex maximum at 0.25 µm and below 0.131% at 0.125 µm.
- Raw artifact IDs: 14699778704, 14699833538, 14699989410, 14700104294 (run 44887065310).

## Limitations and next experiment
- This validates numerical correspondence of the Import3D/Cable morphology conversion for two incomplete human L2/3 morphologies under generic passive parameters. It does not validate biological Ri/Rm/Cm, active channels, synapses or healthy human axons.
- Next: extend the Segev matrix with 0.0625 µm NEURON mesh to measure further spatial convergence and error floor on both cells; then introduce a separate named FCI-derived reduced active model only after license and mechanism assumptions are resolved.

## Commit
`f63b3ce89344207f504dcc47a869be59cc21f438`.
## Fine-mesh refinement at 0.0625 µm — run 44887397930

- Both NEURON 9.0.2 jobs passed 81/81 AMSN tests and 120 frequency-response rows.
- NMO_68174: 333,452 NEURON segments; area diff −1.11863e−6%; input complex median/p95/max 0.005932/0.036530/0.047282%; transfer complex 0.001221/0.052982/0.133856%; transfer magnitude max 0.073723%; phase max 0.064037°.
- NMO_68175: 312,745 NEURON segments; area diff −8.00770e−7%; input complex 0.013756/0.031304/0.038863%; transfer complex 0.003012/0.059594/0.099423%; transfer magnitude max 0.089533%; phase max 0.030780°.
- Error statistics are not monotone in every percentile: NMO_68174 p95/max rise slightly while median improves; NMO_68175 p95/max improve while median rises. Do not overstate mesh convergence.
- Raw artifacts: 14700676187 (NMO_68174) and 14700169600 (NMO_68175), run 44887397930.
- Dedicated workflow `.github/workflows/amsn-segev-fine-mesh-frequency-audit.yml` is committed at `ff83fd7acc36da874f0ebcca7290a7bc8c80bdf4`.

## Pair-level residual localization from raw CSV

Extracted four Actions artifacts (NMO_68174 and NMO_68175 at 0.125 and 0.0625 µm; 120 rows each). Worst 3 kHz pairs:
- NMO_68175 0.125: basal q75 SWC3253 → apical q50 SWC12177, complex 0.169384%, source/probe offsets 0.044099/0.043591 µm.
- NMO_68175 0.0625: apical q75 SWC7640 → apical q50 SWC12177, 0.099423%, offsets 0.027810/0.002554 µm.
- NMO_68174 0.125: basal q75 SWC1577 → apical q90 SWC10532, 0.130503%, offsets 0.001441/0.030656 µm.
- NMO_68174 0.0625: same pair, 0.133856%, offsets 0.009962/0.022117 µm.

Spearman error-versus-log-frequency across the 120 rows is 0.747–0.833. Source/probe offset associations vary by cell, so this is not a causal location result. The NMO_68174 0.0625 worst transfer path has a very small absolute NEURON magnitude (~2.410e−7 MΩ); relative error must be read with absolute transfer. A matched-support site-placement experiment is the next step.
