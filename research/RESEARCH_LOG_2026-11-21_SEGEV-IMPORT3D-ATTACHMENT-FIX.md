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