# Exact passive Schur port-matrix comparison — human morphologies

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Schur audit:** [workflow 44916411567 — 6/6 passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567)  
**Core CI:** [workflow 44916411432 — 4/4 passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432)  
**Implementation commit:** [3afd81736a752aea9296a417af14fc1bbee53e10](https://github.com/Nolane-x/Nghien-cuu/commit/3afd81736a752aea9296a417af14fc1bbee53e10)  
**Configuration summary:** [human_schur_port_matrix_summary_2026-11-21.csv](../results/human_schur_port_matrix_summary_2026-11-21.csv)  
**Frequency-resolved metrics:** [human_schur_port_matrix_frequency_summary_2026-11-21.csv](../results/human_schur_port_matrix_frequency_summary_2026-11-21.csv)

## 1. What was reduced

A new core API, \`amsn.schur_reduce_passive_admittance(tree, retained_indices, frequency_hz)\`, builds the complete passive complex nodal admittance operator and eliminates all non-retained electrical vertices. The returned dense matrix is the exact Schur complement on the selected ports for the discretized AMSN cable.

The audit preserved seven shared SWC ports:
- sources: soma, basal q75, apical q75;
- probes: soma, basal q50/q90, apical q50/q90;
- soma is shared, so there are seven unique vertices.

For each of eight frequencies (0.1, 1, 10, 30, 100, 300 and 1,000, 3,000 Hz):
1. AMSN produced the sparse-elimination Schur admittance matrix.
2. AMSN independently assembled the seven-port impedance matrix from seven unit-current Hines solves, then inverted it.
3. NEURON 9.0.2 produced the native Import3D seven-port complex transfer-impedance matrix at exact SWC section coordinates, then that matrix was inverted into port admittance.

The comparison therefore does not rely on the earlier matched-support membrane-area projection. Every non-port compartment inside each simulator is eliminated implicitly. The resulting port operator is frequency-dependent and dense.

## 2. Validation of the Schur implementation itself

All six morphology/mesh jobs passed the full 90-test AMSN suite and the Schur audit. The most important internal check is the agreement between:
- AMSN's explicit sparse Schur reduction; and
- the inverse of AMSN's independently constructed full-tree port impedance.

| Morphology | Mesh µm | Maximum Schur-vs-full AMSN relative error |
|---|---:|---:|
| NMO_68174 | 0.125 | 5.93e-11% |
| NMO_68174 | 0.0625 | 5.93e-11% |
| NMO_68175 | 0.125 | 6.72e-11% |
| NMO_68175 | 0.0625 | 6.71e-11% |
| NMO_290988 | 0.125 | 9.40e-11% |
| NMO_290988 | 0.0625 | 9.40e-11% |

This confirms that the new Schur operator reproduces the full AMSN port behavior to near floating-point precision for these six large-tree cases. It is a direct validation of the implementation, not an inference from cross-simulator agreement.

Reciprocity is also preserved:
- maximum AMSN port-impedance reciprocity error: 1.14e-13%;
- maximum NEURON port-impedance reciprocity error: 1.23e-12%.

The largest NEURON port-impedance condition number was 72.11, so the tested matrices were not close to singular under the audit's condition-number gate.

## 3. Cross-simulator seven-port matrix errors

Each job produced 392 raw matrix entries (8 frequencies × 7 × 7) and eight per-frequency summaries. Across all six jobs: 2,352 raw entries and 48 summaries.

The table reports the maximum across the eight frequencies of the Frobenius relative error of the full seven-port matrix. This is a matrix-level metric; it is not the maximum relative error of any one tiny matrix element.

| Morphology | Mesh µm | Port-admittance error max | Port-impedance error max | Worst frequency |
|---|---:|---:|---:|---:|
| NMO_68174 | 0.125 | 0.026180% | 0.089419% | 3,000 Hz |
| NMO_68174 | 0.0625 | 0.024059% | 0.044363% | 3,000 Hz |
| NMO_68175 | 0.125 | 0.021700% | 0.050049% | 3,000 Hz |
| NMO_68175 | 0.0625 | 0.021748% | 0.040735% | 3,000 Hz |
| NMO_290988 | 0.125 | 0.016746% | 0.061944% | 3,000 Hz |
| NMO_290988 | 0.0625 | 0.016666% | 0.062007% | 3,000 Hz |

All six cases show the largest matrix-level error at 3 kHz. At lower frequencies, the matrix errors are smaller. For example, at 0.1 Hz, port-admittance errors range from 0.00175% to 0.01340%; at 3 kHz they range from 0.01667% to 0.02618%.

### Diagonal and off-diagonal behavior

At 3 kHz, the separately normalized off-diagonal admittance submatrix errors range from 0.0430% to 0.0907%, while diagonal errors range from 0.0167% to 0.0262%. Thus the branch-to-branch transfer couplings are more sensitive than the port self-admittances in this comparison.

This is an important distinction from a scalar input-resistance check: a model may reproduce individual port self-admittances well while retaining somewhat larger differences in the coupling between distant ports.

Do not interpret elementwise relative errors where a reference coupling is almost zero. Such entries can show a very large percentage despite a negligible absolute difference. The report therefore prioritizes full-matrix Frobenius metrics and separately normalized diagonal/off-diagonal blocks; raw CSVs retain absolute errors for every entry.

## 4. Does mesh refinement help?

The effect differs by morphology and by whether admittance or impedance is inspected:

- **NMO_68174:** refining from 0.125 to 0.0625 µm reduces worst port-admittance error by about 8.1% and port-impedance error by about 50.4%.
- **NMO_68175:** port-admittance error is effectively unchanged (0.021700% to 0.021748%), while port-impedance error improves by about 18.6%.
- **NMO_290988:** port-admittance error improves slightly (0.016746% to 0.016666%), while port-impedance error is effectively unchanged/slightly higher (0.061944% to 0.062007%).

There is no universal monotonic mesh trend across these three morphologies. The inverse relationship between port admittance and port impedance also means their Frobenius errors need not move in exactly the same direction.

## 5. Interpretation and limits

The new Schur reduction is validated internally: it reproduces the full AMSN boundary behavior to approximately 1e-10% relative error. The remaining AMSN–NEURON difference is small at the level of the seven-port operators: all tested full-matrix relative errors remain below 0.09%.

The residual grows toward high frequency and is more pronounced in off-diagonal transfer couplings than in diagonal self-admittances. This suggests the remaining error is primarily in how the two discretizations represent spatial coupling along dendritic paths, rather than a failure of the Schur elimination itself.

This remains a passive numerical comparison between two discretized models. It does not establish biological validity, active-channel accuracy, synaptic physiology or population-level generalization. NMO_290988 is a partial dendritic reconstruction and must not be treated as a healthy-control morphology.

## 6. Reproducibility

All six jobs passed 90 tests each. Core CI [44916411432] also passed 90 tests on both Python 3.12 and 3.13, plus both NEURON cross-validation jobs. The six-job workflow [44916411567](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567) passed all jobs. Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed all four jobs, including Python 3.12/3.13 and both NEURON validation jobs.

| Morphology | Mesh µm | Artifact |
|---|---:|---:|
| NMO_68174 | 0.125 | [14711587402](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14711587402) |
| NMO_68174 | 0.0625 | [14712336148](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14712336148) |
| NMO_68175 | 0.125 | [14711776885](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14711776885) |
| NMO_68175 | 0.0625 | [14711552473](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14711552473) |
| NMO_290988 | 0.125 | [14711852797](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14711852797) |
| NMO_290988 | 0.0625 | [14712351124](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567/artifacts/14712351124) |

Each artifact retains all 392 complex matrix entries, eight frequency summaries and its execution log.


## 7. Port-resolved error localization at 3 kHz

The rerun also emits a port-localization table for every frequency. For each retained port it computes the relative Frobenius error of that matrix row, the off-diagonal part of that row, the diagonal self-admittance error and the maximum absolute row error. The 3 kHz worst-port rows are:

| Cell | Mesh µm | Highest-error retained port | Row error | Off-diagonal row error | Diagonal error |
|---|---:|---|---:|---:|---:|
| NMO_68174 | 0.125 | apical q50 probe | 0.1691% | 0.1646% | 0.1691% |
| NMO_68174 | 0.0625 | apical q50 probe | 0.0559% | 0.0703% | 0.0559% |
| NMO_68175 | 0.125 | basal q50 probe | 0.0699% | 0.0903% | 0.0676% |
| NMO_68175 | 0.0625 | apical q50 probe | 0.0543% | 0.0600% | 0.0543% |
| NMO_290988 | 0.125 | apical q90 probe | 0.0913% | 0.2716% | 0.0913% |
| NMO_290988 | 0.0625 | apical q90 probe | 0.0964% | 0.2614% | 0.0964% |

This identifies a stable apical q50 hotspot for NMO_68174, while the highest-error port shifts from basal q50 to apical q50 for NMO_68175 when the NEURON mesh is refined. NMO_290988 remains dominated by apical q90 at both meshes; for that row the off-diagonal coupling error is roughly 2.7 times the diagonal self-admittance error.

The 3 kHz localization table does not imply that all error is at the probe itself. Each row aggregates the error between one port and all seven other ports, including its couplings to the rest of the boundary. It is a row-level diagnostic, not a unique causal attribution to one physical branch.
