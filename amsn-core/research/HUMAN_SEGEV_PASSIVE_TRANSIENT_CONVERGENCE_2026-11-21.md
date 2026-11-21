# Segev native passive transient — time/space convergence audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 3f959b7751a087a06a22f28a45f8490e991370f7](https://github.com/Nolane-x/Nghien-cuu/commit/3f959b7751a087a06a22f28a45f8490e991370f7)  
**Convergence workflow:** [44908381318 — success, 12/12 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318)  
**Core CI:** [44908381336 — success, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336)  
**Baseline transient workflow:** [44908381396 — success, 2/2 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381396)  
**Configuration summary:** [human_segev_passive_transient_convergence_summary_2026-11-21.csv](../results/human_segev_passive_transient_convergence_summary_2026-11-21.csv)  
**Pairwise convergence measurements:** [human_segev_passive_transient_pairwise_convergence_2026-11-21.csv](../results/human_segev_passive_transient_pairwise_convergence_2026-11-21.csv)

## 1. Purpose

The first native transient comparison showed very close agreement between NEURON's fine Import3D segment tree and AMSN's node-centred SWC CableTree at dt=0.05 ms and a 0.125 µm NEURON mesh cap. This follow-up changes spatial mesh and time step independently to answer two separate questions:

1. Is the discrepancy dominated by backward-Euler time discretization?
2. Does reducing the NEURON segment length consistently move the native NEURON waveform toward the AMSN SWC waveform?

## 2. Experimental design and validation

The factorial matrix contained:
- 2 morphologies: NMO_68174 / cell1125 and NMO_68175 / cell1204.
- 2 NEURON mesh caps: 0.125 and 0.0625 µm.
- 3 time steps: 0.1, 0.05 and 0.025 ms.
- Total: 12 independent GitHub Actions jobs.

Every job used NEURON 9.0.2 and the complete 81-test AMSN suite. The 10 pA pulse remained +10 pA from 2 to 12 ms; the run duration remained 30 ms. Both solvers used backward Euler. All pulse boundaries were checked to lie exactly on each configured time grid before simulation.

Each configuration generated 15 source/probe traces and two NEURON readout modes:
- nearest segment centre;
- linear interpolation between adjacent centres at the exact SWC arc coordinate.

Expected and observed outputs:
- dt=0.1 ms: 301 samples per trace, 4,515 trace rows, 30 summary rows.
- dt=0.05 ms: 601 samples per trace, 9,015 trace rows, 30 summary rows.
- dt=0.025 ms: 1,201 samples per trace, 18,015 trace rows, 30 summary rows.

Across the full matrix this is **126,180 time-series rows and 360 source/probe/readout summaries**. All 12 jobs passed; all trace and summary artifacts were uploaded. Core CI passed 4/4 jobs.

## 3. Cross-simulator waveform agreement by mesh and dt

All NRMSE values below are percentages of the peak NEURON voltage deflection. Each table cell is the maximum over all 15 source/probe pairs for that morphology, mesh and dt.

| Cell | Mesh (µm) | dt (ms) | Nearest-centre max NRMSE | Interpolated max NRMSE |
|---|---:|---:|---:|---:|
| NMO_68174 | 0.125 | 0.1 | 0.00164071% | 0.00035695% |
| NMO_68174 | 0.125 | 0.05 | 0.00164072% | 0.00035674% |
| NMO_68174 | 0.125 | 0.025 | 0.00164026% | 0.00035664% |
| NMO_68174 | 0.0625 | 0.1 | 0.00128612% | 0.00018974% |
| NMO_68174 | 0.0625 | 0.05 | 0.00128585% | 0.00018974% |
| NMO_68174 | 0.0625 | 0.025 | 0.00128561% | 0.00018978% |
| NMO_68175 | 0.125 | 0.1 | 0.00237166% | 0.00079069% |
| NMO_68175 | 0.125 | 0.05 | 0.00236980% | 0.00079069% |
| NMO_68175 | 0.125 | 0.025 | 0.00236946% | 0.00079071% |
| NMO_68175 | 0.0625 | 0.1 | 0.00258297% | 0.00263510% |
| NMO_68175 | 0.0625 | 0.05 | 0.00258116% | 0.00263321% |
| NMO_68175 | 0.0625 | 0.025 | 0.00258016% | 0.00263217% |

### What changes with dt?

At a fixed morphology and mesh, the cross-simulator NRMSE changes only slightly across dt=0.1, 0.05 and 0.025 ms:
- For NMO_68174, the maximum nearest-centre NRMSE changes by less than 0.04% relative across the three dt values at either mesh.
- For NMO_68175, it changes by less than 0.12% relative.
- The interpolated results are similarly stable.

This indicates that reducing dt does not materially change the difference between the two simulators in this experiment. It does not mean that the individual transient solution is time-step independent; that is assessed separately below.

### What changes with mesh?

The spatial result is morphology-dependent:
- NMO_68174 improves when the NEURON mesh is refined from 0.125 to 0.0625 µm. Maximum nearest-centre NRMSE decreases from 0.001641% to 0.001286% (about 21.6% lower); maximum interpolated NRMSE decreases from 0.0003567% to 0.0001897% (about 46.8% lower).
- NMO_68175 does not improve with the same refinement. Maximum nearest-centre NRMSE increases from 0.002369% to 0.002580% (about 8.9% higher), while the interpolated maximum rises from 0.0007907% to 0.002632% (about 3.33 times higher).

At the finer NMO_68175 mesh, the worst interpolated pair is apical q75 source → apical q50 probe. The worst pair at the coarser mesh is different (basal q75 source → soma). This is a localized, source/probe-dependent spatial effect, not a uniform global degradation.

## 4. Direct spatial mesh-to-mesh comparison

To distinguish changes in NEURON itself from changes in the AMSN–NEURON residual, the NEURON waveforms at 0.125 and 0.0625 µm were compared directly at identical dt values and common time samples. The AMSN waveform was also checked across these runs; it is exactly invariant to the NEURON mesh, as expected.

| Cell | NEURON readout | Median pairwise NRMSE | P95 | Maximum | Maximum absolute voltage difference |
|---|---|---:|---:|---:|---:|
| NMO_68174 | Nearest centre | 0.000163% | 0.000423% | 0.000480% | 5.83e-7 mV |
| NMO_68174 | Interpolated | 0.000133% | 0.000342% | 0.000343% | 1.225e-6 mV |
| NMO_68175 | Nearest centre | 0.001104% | 0.003246% | 0.003862% | 6.36e-6 mV |
| NMO_68175 | Interpolated | 0.001124% | 0.003021% | 0.003021% | 6.55e-6 mV |

The spatial change in the native NEURON solution is small in absolute terms, but it is larger for NMO_68175. The NMO_68175 interpolation readout is particularly sensitive on the apical q75 → basal q90 pair. These data explain why refinement does not have the same effect on both cells.

## 5. Direct temporal convergence

Waveforms at different dt values were compared only at common sample times, using the finer dt waveform as the reference. The normalized metric is the RMSE of the coarse-versus-fine voltage deflection, divided by the peak deflection of the finer-dt reference.

| Cell | dt comparison | Maximum pairwise NRMSE | Maximum absolute voltage difference |
|---|---|---:|---:|
| NMO_68174 | 0.1 → 0.05 ms | 0.186066% | 0.0007781 mV |
| NMO_68174 | 0.05 → 0.025 ms | 0.093728% | 0.0004114 mV |
| NMO_68175 | 0.1 → 0.05 ms | 0.176664% | 0.0004959 mV |
| NMO_68175 | 0.05 → 0.025 ms | 0.089052% | 0.0003258 mV |

Halving dt approximately halves the remaining pairwise temporal error:
- NMO_68174 ratio: 0.186066 / 0.093728 = 1.985.
- NMO_68175 ratio: 0.176664 / 0.089052 = 1.984.

This is consistent with first-order temporal convergence expected from backward Euler. It is not a formal proof of global temporal order, but the measured ratio is strong supporting evidence.

The important distinction is that this temporal error is largely common-mode between AMSN and NEURON: their separate waveforms change as dt is refined, but the cross-simulator NRMSE remains almost unchanged. Thus reducing dt below 0.05 ms provides little improvement to the relative AMSN–NEURON agreement in the current passive setup.

## 6. Source/probe offsets and absolute errors

Maximum nearest-segment-centre offsets:

| Cell | Mesh (µm) | Source offset max | Probe offset max |
|---|---:|---:|---:|
| NMO_68174 | 0.125 | 0.003185 µm | 0.047808 µm |
| NMO_68174 | 0.0625 | 0.009962 µm | 0.022117 µm |
| NMO_68175 | 0.125 | 0.044099 µm | 0.044767 µm |
| NMO_68175 | 0.0625 | 0.027810 µm | 0.029426 µm |

All offsets remain below half the respective mesh cap. The maximum cross-simulator absolute waveform errors over the 12 configurations are only a few millionths of a millivolt. Reporting absolute voltage error remains essential because distal transfer paths can be weak.

## 7. Decision and limitations

1. Keep dt=0.05 ms as the normal comparison setting. Use dt=0.025 ms when tighter time accuracy is needed; it does not materially improve the cross-simulator residual in this passive experiment.
2. Do not declare 0.0625 µm the universally better mesh. It improves NMO_68174 but worsens selected NMO_68175 paths.
3. Keep nearest-centre and SWC-arc interpolated probes side by side. At NMO_68175 / 0.0625 µm, interpolation is not better than nearest-centre.
4. Do not retune Ri/Rm/Cm/Eleak.
5. No biological validity is claimed. This is numerical validation of two partial morphologies from the same SWC source.

## 8. Reproducibility artifacts

The 12-job convergence workflow [44908381318](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318) passed 12/12 jobs. Each job ran the complete AMSN test suite and uploaded its trace, summary and log.

| Cell | Mesh (µm) | dt (ms) | Artifact |
|---|---:|---:|---:|
| NMO_68174 | 0.125 | 0.1 | [14708817805](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708817805) |
| NMO_68174 | 0.125 | 0.05 | [14708628323](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708628323) |
| NMO_68174 | 0.125 | 0.025 | [14708154832](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708154832) |
| NMO_68174 | 0.0625 | 0.1 | [14709052180](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14709052180) |
| NMO_68174 | 0.0625 | 0.05 | [14709221281](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14709221281) |
| NMO_68174 | 0.0625 | 0.025 | [14708672055](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708672055) |
| NMO_68175 | 0.125 | 0.1 | [14708188029](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708188029) |
| NMO_68175 | 0.125 | 0.05 | [14708249496](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708249496) |
| NMO_68175 | 0.125 | 0.025 | [14708208171](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708208171) |
| NMO_68175 | 0.0625 | 0.1 | [14708777829](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708777829) |
| NMO_68175 | 0.0625 | 0.05 | [14708364130](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14708364130) |
| NMO_68175 | 0.0625 | 0.025 | [14709156949](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318/artifacts/14709156949) |

Core CI [44908381336](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336) passed 4/4 jobs. The baseline two-cell transient workflow also passed [44908381396](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381396).

## 9. Next controlled experiment

The next unresolved variable is source placement on NEURON's native segment mesh. The current point current is applied at the nearest segment centre. Implement a diagnostic comparison:
- nearest-segment-centre IClamp (current baseline);
- split the same total 10 pA across the two bracketing segment centres using the exact SWC arc interpolation weights.

Keep total injected charge exactly constant and compare both against AMSN's exact SWC-node current. This isolates source-placement effects before considering a fine-tree Schur complement or active mechanisms.
