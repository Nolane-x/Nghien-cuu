# Human morphology source-placement replication — transient and AC results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Workflow:** [44914135217 — success, 6/6 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217)  
**Implementation commit:** [4cac5961789d690630b691aead067f08fb565a37](https://github.com/Nolane-x/Nghien-cuu/commit/4cac5961789d690630b691aead067f08fb565a37)  
**Machine-readable comparison:** [human_morphology_source_alignment_summary_2026-11-21.csv](../results/human_morphology_source_alignment_summary_2026-11-21.csv)

## 1. Purpose

The two-cell Segev experiment showed a large weighted-source benefit for NMO_68175 but mixed or negative outcomes for NMO_68174. This replication adds a third, distinct NeuroMorpho.Org neuron record and repeats both time-domain and frequency-domain source-placement comparisons.

The canonical reference remains AMSN current injection at the exact SWC electrical node. NEURON alternatives are:
- nearest segment-centre source;
- weighted two-centre source, distributing the same total current according to the interpolation bracket around the exact SWC arc.

Probe readouts are retained separately. No Ri/Rm/Cm/Eleak parameter is retuned.

## 2. Third morphology and limitations

NMO_290988 / 1094_Mohan_etal_2015 is a distinct NeuroMorpho.Org/DeKock record:
- 8,903 standardized CNG SWC records;
- soma and basal/apical dendrites, no axon;
- human adult middle temporal gyrus, Brodmann area 21, layer 2–3 pyramidal/principal reconstruction;
- dendritic completeness marked moderate;
- metadata records mesiotemporal sclerosis and does not report shrinkage correction.

It is not a healthy-control morphology. It is a distinct neuron record, but shares a broad cortical region and cell class with the Segev fixtures. Three reconstructions are still not a population sample.

## 3. Execution and integrity

Workflow [44914135217](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217) passed all six matrix jobs:
- 3 morphologies × 2 NEURON mesh caps (0.125 and 0.0625 µm);
- complete 81-test AMSN suite in each job;
- exact SWC record-count checks;
- Import3D mapping of 3 source sites and 5 probe sites (7 unique locations because soma is reused);
- transient and AC source-placement audits;
- raw artifact uploads.

Aggregate output:
- 108,180 transient trace rows and 360 transient summaries;
- 6,480 raw AC transfer rows and 810 grouped AC summaries;
- the total 10 pA transient current was conserved at every sample, with maximum numerical error 1.735e-18 nA.

For every configuration, the transient summary includes 60 rows (15 source/probe pairs × 2 source modes × 2 probe readouts); AC includes 1,080 raw rows and 135 grouped summaries.

## 4. Transient source-placement results

Each row below aggregates 15 source/probe pairs. NRMSE is the waveform RMSE normalized by the peak NEURON voltage deflection. P95 uses nearest-rank empirical quantile; with 15 pairs, P95 equals the maximum.

| Cell | Mesh µm | Probe readout | Nearest max | Weighted max | Improved / worse / same pairs |
|---|---:|---|---:|---:|---:|
| NMO_68174 | 0.125 | Nearest centre | 0.001641% | 0.001641% | 5 / 5 / 5 |
| NMO_68174 | 0.125 | SWC-arc interpolation | 0.000357% | 0.000265% | 5 / 5 / 5 |
| NMO_68174 | 0.0625 | Nearest centre | 0.001286% | 0.001161% | 2 / 8 / 5 |
| NMO_68174 | 0.0625 | SWC-arc interpolation | 0.000190% | 0.000265% | 0 / 10 / 5 |
| NMO_68175 | 0.125 | Nearest centre | 0.002370% | 0.001558% | 10 / 0 / 5 |
| NMO_68175 | 0.125 | SWC-arc interpolation | 0.000791% | 0.000192% | 10 / 0 / 5 |
| NMO_68175 | 0.0625 | Nearest centre | 0.002581% | 0.001655% | 8 / 2 / 5 |
| NMO_68175 | 0.0625 | SWC-arc interpolation | 0.002633% | 0.000192% | 10 / 0 / 5 |
| NMO_290988 | 0.125 | Nearest centre | 0.019396% | 0.001711% | 8 / 2 / 5 |
| NMO_290988 | 0.125 | SWC-arc interpolation | 0.020312% | 0.000392% | 10 / 0 / 5 |
| NMO_290988 | 0.0625 | Nearest centre | 0.001861% | 0.001111% | 7 / 3 / 5 |
| NMO_290988 | 0.0625 | SWC-arc interpolation | 0.001955% | 0.000365% | 10 / 0 / 5 |

The weighted source is strongly beneficial to NMO_290988 transients: maximum NRMSE falls by 91–98% at 0.125 µm and 40–81% at 0.0625 µm. The nearest-source baseline itself changes substantially across meshes for this cell, so mesh sensitivity must remain visible in any later model reduction.

Across all 180 transient source/probe comparisons, 85 improve, 35 worsen and 60 are unchanged. The same pairs can behave differently under nearest-centre and interpolated probe readouts; do not collapse these two measurements.

## 5. AC complex-transfer results

For each source/probe pair, the error is first maximized over eight frequencies; the table then reports the maximum across the 15 pairs. The underlying raw data preserve each individual frequency and complex transfer value.

| Cell | Mesh µm | Probe readout | Nearest max | Weighted max | Improved / worse / same pairs |
|---|---:|---|---:|---:|---:|
| NMO_68174 | 0.125 | Exact SWC | 0.130599% | 0.129612% | 5 / 5 / 5 |
| NMO_68174 | 0.125 | Complex interpolation | 0.132786% | 0.133201% | 5 / 5 / 5 |
| NMO_68174 | 0.0625 | Exact SWC | 0.133955% | 0.128277% | 2 / 8 / 5 |
| NMO_68174 | 0.0625 | Complex interpolation | 0.132166% | 0.133448% | 0 / 10 / 5 |
| NMO_68175 | 0.125 | Exact SWC | 0.169222% | 0.068720% | 7 / 3 / 5 |
| NMO_68175 | 0.125 | Complex interpolation | 0.125637% | 0.071947% | 6 / 4 / 5 |
| NMO_68175 | 0.0625 | Exact SWC | 0.099512% | 0.069568% | 9 / 1 / 5 |
| NMO_68175 | 0.0625 | Complex interpolation | 0.104835% | 0.072209% | 10 / 0 / 5 |
| NMO_290988 | 0.125 | Exact SWC | 0.273392% | 0.239773% | 7 / 3 / 5 |
| NMO_290988 | 0.125 | Complex interpolation | 0.254908% | 0.230398% | 10 / 0 / 5 |
| NMO_290988 | 0.0625 | Exact SWC | 0.230103% | 0.232801% | 5 / 5 / 5 |
| NMO_290988 | 0.0625 | Complex interpolation | 0.229296% | 0.231359% | 2 / 8 / 5 |

The third morphology is the decisive counterexample to a simple rule: weighted source produces large transient gains, modest AC gains at 0.125 µm, but slight AC degradation at 0.0625 µm. Time-domain improvement does not guarantee frequency-domain improvement, even on the same cell and mesh.

Across all 180 AC pair comparisons, 68 improve, 52 worsen and 60 remain unchanged. The weighted source is often helpful, but less consistently than in the transient experiment.

## 6. Geometry and current conservation

| Cell | Mesh µm | Maximum source offset | Maximum bracket width |
|---|---:|---:|---:|
| NMO_68174 | 0.125 | 0.003185 µm | 0.124970 µm |
| NMO_68174 | 0.0625 | 0.009962 µm | 0.062498 µm |
| NMO_68175 | 0.125 | 0.044099 µm | 0.124991 µm |
| NMO_68175 | 0.0625 | 0.027810 µm | 0.062490 µm |
| NMO_290988 | 0.125 | 0.060157 µm | 0.124943 µm |
| NMO_290988 | 0.0625 | 0.005167 µm | 0.062488 µm |

NMO_290988's largest source offset at 0.125 µm is close to half the mesh cap; at 0.0625 µm the offset becomes much smaller. Yet the AC result changes in the opposite direction from what a simple offset-threshold rule would predict. Three morphologies are not enough to derive a safe geometric switch.

## 7. Decision

1. Keep exact-SWC injection as the canonical comparison reference.
2. Keep weighted adjacent-centre injection as an optional diagnostic, not a global default.
3. Do not infer an automatic offset threshold from three reconstructed cells.
4. Keep transient and AC validations separate; passing one does not guarantee the other.
5. Do not tune Ri/Rm/Cm/Eleak to force the weighted method to win.
6. Treat all results as numerical model comparisons, not biological validation or population-level evidence.

The present evidence supports a source-placement sensitivity that interacts with morphology, mesh and probe coordinate. A source-aware reduction should preserve the alternatives and quantify their residuals rather than silently selecting one.

## 8. Reproducibility artifacts

All six jobs in [workflow 44914135217](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217) passed and uploaded the raw datasets.

| Morphology | Mesh µm | Artifact |
|---|---:|---:|
| NMO_68174 | 0.125 | [14710249518](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14710249518) |
| NMO_68174 | 0.0625 | [14710224649](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14710224649) |
| NMO_68175 | 0.125 | [14711185931](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14711185931) |
| NMO_68175 | 0.0625 | [14711400157](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14711400157) |
| NMO_290988 | 0.125 | [14710778602](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14710778602) |
| NMO_290988 | 0.0625 | [14711395235](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217/artifacts/14711395235) |

The linked summary CSV contains 24 configuration/domain/readout rows. Each raw workflow artifact retains the transient waveform matrix, the AC complex transfer table, both source modes, probe modes and logs.
