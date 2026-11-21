# NMO_290988 passive transient time/space convergence — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Workflow:** [44915125555 — success, 6/6 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555)  
**Implementation commit:** [69333b5314c3321e72e5fb6b8158cd6723aff5b3](https://github.com/Nolane-x/Nghien-cuu/commit/69333b5314c3321e72e5fb6b8158cd6723aff5b3)  
**Configuration summary:** [human_nmo290988_passive_transient_convergence_summary_2026-11-21.csv](../results/human_nmo290988_passive_transient_convergence_summary_2026-11-21.csv)  
**Pairwise comparisons:** [human_nmo290988_passive_transient_pairwise_convergence_2026-11-21.csv](../results/human_nmo290988_passive_transient_pairwise_convergence_2026-11-21.csv)

## 1. Question and protocol

The three-morphology source-placement audit showed a relatively large transient discrepancy for NMO_290988 at a 0.125 µm NEURON mesh and a much smaller discrepancy at 0.0625 µm. This follow-up independently varies NEURON mesh and backward-Euler time step to distinguish spatial from temporal error.

Morphology: NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015, 8,903 SWC records, soma plus basal/apical dendrites, no axon, moderate dendritic completeness. This is not a healthy-control morphology.

Matrix:
- NEURON maximum segment length: 0.125 and 0.0625 µm.
- Time step: 0.1, 0.05 and 0.025 ms.
- Pulse: +10 pA from 2 to 12 ms; duration 30 ms.
- Passive constants: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV.
- NEURON 9.0.2 and AMSN use fully implicit backward Euler.

The six-job workflow [44915125555](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555) passed 6/6. Every job passed the complete 81-test suite, checked the exact 8,903-record fixture, ran the transient comparison and uploaded raw traces and summaries.

Aggregate outputs: 63,090 transient trace rows and 180 source/probe/probe-readout summaries.

## 2. Cross-simulator mismatch by mesh and time step

NRMSE is the waveform RMSE normalized by the peak NEURON voltage deflection. The values below are maxima over the 15 source/probe pairs for each probe readout.

| Mesh µm | dt ms | Nearest-probe max NRMSE | Interpolated-probe max NRMSE | Peak amplitude error max |
|---:|---:|---:|---:|---:|
| 0.125 | 0.1 | 0.019358% | 0.020281% | 0.036718% |
| 0.125 | 0.05 | 0.019396% | 0.020312% | 0.036713% |
| 0.125 | 0.025 | 0.019416% | 0.020328% | 0.036711% |
| 0.0625 | 0.1 | 0.001858% | 0.001952% | 0.003362% |
| 0.0625 | 0.05 | 0.001861% | 0.001955% | 0.003362% |
| 0.0625 | 0.025 | 0.001863% | 0.001957% | 0.003361% |

At fixed mesh, changing dt from 0.1 to 0.025 ms barely changes the AMSN–NEURON maximum NRMSE:
- mesh 0.125 µm, interpolated: 0.020281% → 0.020328%;
- mesh 0.0625 µm, interpolated: 0.001952% → 0.001957%.

By contrast, refining NEURON from 0.125 to 0.0625 µm reduces maximum interpolated-probe NRMSE by approximately 90.4% at every dt. The nearest-probe maximum falls by a similar proportion. For this morphology and passive configuration, spatial discretization dominates the cross-simulator residual over the tested parameter range.

This is a two-level spatial comparison, not proof of asymptotic mesh convergence. A third, finer mesh would be needed to estimate spatial convergence order or show that 0.0625 µm is already in the asymptotic regime.

## 3. Direct temporal convergence

NEURON waveforms were compared at common time samples, using the finer grid as the reference. The reported NRMSE is the RMSE of voltage deflections divided by the peak deflection of the finer-grid trace. Each statistic aggregates 15 source/probe pairs.

| Mesh µm | dt comparison ms | Readout | Median pairwise NRMSE | P95 / maximum |
|---:|---:|---|---:|---:|
| 0.125 | 0.1 → 0.05 | Nearest centre | 0.177869% | 0.283786% |
| 0.125 | 0.05 → 0.025 | Nearest centre | 0.089754% | 0.145211% |
| 0.0625 | 0.1 → 0.05 | Nearest centre | 0.177875% | 0.283776% |
| 0.0625 | 0.05 → 0.025 | Nearest centre | 0.089757% | 0.145206% |

Interpolated-probe pairwise results are nearly identical. Halving dt approximately halves the maximum pairwise temporal error:
- 0.125 µm: 0.283786 / 0.145211 = 1.954.
- 0.0625 µm: 0.283776 / 0.145206 = 1.954.

Median ratios are approximately 1.982. This is consistent with first-order temporal convergence expected from backward Euler. It is supporting evidence for the tested responses, not a formal proof of global order.

The individual solutions do change with dt, but the cross-simulator mismatch remains nearly unchanged. Temporal refinement is behaving as expected; it is not the dominant source of AMSN–NEURON residual in this experiment.

## 4. Direct spatial mesh-to-mesh comparison

At identical dt, NEURON waveforms on the 0.125 and 0.0625 µm meshes were compared at common time samples.

| Probe readout | Median pairwise NRMSE | P95 / maximum | Maximum absolute voltage difference |
|---|---:|---:|---:|
| Nearest segment centre | ≈0.001882% | 0.01753–0.01758% | ≈0.001397 mV |
| Linear interpolation | ≈0.001868% | 0.01836–0.01840% | ≈0.001448 mV |

These mesh-to-mesh differences are almost invariant across dt. The largest spatially sensitive path is basal q75 source → basal q90 probe. This supports the finding that the larger residual at 0.125 µm is associated with local spatial discretization, not a mismatch in time grids.

## 5. Decision and limits

1. Use dt=0.05 ms as the normal comparison setting for this passive audit. dt=0.025 ms gives the expected temporal refinement but does not materially reduce cross-simulator mismatch.
2. Prefer the 0.0625 µm NEURON mesh for this morphology when numerical agreement is the priority. This is a validated improvement across both probe readouts, but not yet a universal optimal mesh.
3. Keep source-placement and probe-readout alternatives separate; do not conflate their effects with mesh convergence.
4. Do not retune Ri/Rm/Cm/Eleak.
5. This is numerical validation on one partial reconstruction, not biological validation.

## 6. Reproducibility artifacts

Workflow [44915125555](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555) passed all six jobs.

| Mesh µm | dt ms | Artifact |
|---:|---:|---:|
| 0.125 | 0.1 | [14711058996](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14711058996) |
| 0.125 | 0.05 | [14711715961](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14711715961) |
| 0.125 | 0.025 | [14710454924](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14710454924) |
| 0.0625 | 0.1 | [14711143786](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14711143786) |
| 0.0625 | 0.05 | [14711233125](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14711233125) |
| 0.0625 | 0.025 | [14711516756](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555/artifacts/14711516756) |

The configuration and pairwise CSVs preserve exact metrics. Each artifact contains the full 15 source/probe traces for AMSN, NEURON nearest-centre and interpolated readouts.
