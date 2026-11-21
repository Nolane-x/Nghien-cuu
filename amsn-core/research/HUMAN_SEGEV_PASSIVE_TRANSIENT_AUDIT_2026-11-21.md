# Segev native passive transient cross-validation — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 8fc22706b48e5a703024eee37f869d7ba58b7980](https://github.com/Nolane-x/Nghien-cuu/commit/8fc22706b48e5a703024eee37f869d7ba58b7980)  
**Transient workflow:** [44907890895 — successful, 2/2 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895)  
**Core CI:** [44907890934 — successful, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934)  
**Summary CSV:** [human_segev_passive_transient_summary_2026-11-21.csv](../results/human_segev_passive_transient_summary_2026-11-21.csv)

## 1. Research question

Do the native NEURON 9.0.2 fine-segment passive model and AMSN's unresampled SWC node-centred CableTree produce the same time-domain voltage response when driven by the same current pulse?

This is intentionally different from the preceding matched-support passive admittance test. Here NEURON is solved directly on its native Import3D segment tree; AMSN is solved on its original SWC electrical nodes.

## 2. Protocol

Both cells were tested independently:
- NMO_68174 / cell1125: 12,410 SWC records, 12,399 AMSN electrical nodes, 166,856 NEURON segments.
- NMO_68175 / cell1204: 13,758 SWC records, 13,747 AMSN electrical nodes, 156,471 NEURON segments.

The reference configuration used NEURON 9.0.2 with 0.125 µm maximum segment length. The pulse was +10 pA from 2 to 12 ms, for a 30 ms simulation duration and a fixed dt of 0.05 ms (601 samples). Passive parameters were fixed at Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.

Both simulators used fully implicit backward Euler:
- AMSN: CableTree.step_passive.
- NEURON: h.secondorder=0, documented as fully implicit backward Euler by the NEURON programmatic simulation reference: https://www.neuronsimulator.org/en/latest/progref/simctrl/programmatic.html

The pulse was actually delivered to NEURON as 0.01 nA across 200 time intervals (0.05 ms each), matching the AMSN 10 pA input on the same interval convention. The exported time grids differed by at most 6.36e-13 ms.

Three source sites were exercised (soma, basal q75, apical q75), each with five probe sites (soma, basal q50/q90, apical q50/q90). Each morphology yielded exactly 9,015 trace rows and 30 summary rows. NEURON probe voltages were recorded both at the nearest segment centre and by linear interpolation between adjacent segment centres at the exact SWC arc coordinate.

## 3. Results

### Waveform agreement by morphology and probe readout

All values below are percentages except the final absolute voltage error column.

| Cell | NEURON probe readout | NRMSE median | NRMSE P95 | NRMSE max | Peak amplitude error max | AUC error max | Late-pulse mean error max | Max absolute waveform error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| NMO_68174 | Nearest centre | 0.0001710% | 0.0016017% | 0.0016407% | 0.0021657% | 0.0022356% | 0.0046824% | 5.147e-6 mV |
| NMO_68174 | Linear interpolation at SWC arc | 0.0001634% | 0.0003036% | 0.0003567% | 0.0003933% | 0.0004537% | 0.0009194% | 1.531e-6 mV |
| NMO_68175 | Nearest centre | 0.0007626% | 0.0020974% | 0.0023698% | 0.0033750% | 0.0032327% | 0.0065031% | 4.424e-6 mV |
| NMO_68175 | Linear interpolation at SWC arc | 0.0004698% | 0.0007788% | 0.0007907% | 0.0011065% | 0.0010303% | 0.0022304% | 1.459e-6 mV |

Peak-time differences were zero at the 0.05 ms sample resolution for all 60 source/probe/readout rows. This does not prove sub-time-step peak alignment.

### Source and probe mapping offsets

| Cell | Maximum source-to-nearest-centre offset | Maximum probe-to-nearest-centre offset |
|---|---:|---:|
| NMO_68174 | 0.003185 µm | 0.047808 µm |
| NMO_68175 | 0.044099 µm | 0.044767 µm |

All offsets stayed below half the 0.125 µm mesh cap (0.0625 µm). The nonzero source offset is important: the AMSN current is injected at the exact SWC electrical node, while NEURON's point current is applied at the nearest segment centre. This residual placement difference was measured and not concealed.

### Effect of probe interpolation

Linear interpolation improved the maximum and P95 NRMSE for both cells. For example:
- NMO_68174 maximum NRMSE decreased from 0.001641% to 0.000357%.
- NMO_68175 maximum NRMSE decreased from 0.002370% to 0.000791%.

The improvement is not uniform for every individual source/probe pair. Interpolation remains an alternative readout, not a universal physical ground truth. Preserve both nearest-centre and interpolated values in downstream comparisons.

The maximum absolute waveform differences are only a few millionths of a millivolt. Reporting those absolute differences alongside normalized metrics is important because distal transfer responses can be very small.

## 4. Interpretation

For the two tested Segev morphologies, native NEURON segment-level passive transients and AMSN's node-centred SWC transients are extremely close under the same passive constants and the same backward-Euler time grid:
- All 60 source/probe/readout summaries completed on matching sample times.
- Maximum waveform NRMSE was below 0.0024%.
- Maximum peak-amplitude error was below 0.0034%.
- Maximum absolute waveform difference was below 5.2e-6 mV.

This is a strong numerical consistency result for these two partial morphologies and this passive configuration. It does not constitute biological validation, does not validate active channels/synapses, and does not remove the known source-centre offset. The direct NEURON model remains a finite-segment discretization; AMSN remains a node-centred SWC discretization.

## 5. Reproducibility

Transient workflow [44907890895](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895) passed both cells:
- NMO_68174 / cell1125: [artifact 14708946634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895/artifacts/14708946634).
- NMO_68175 / cell1204: [artifact 14708836875](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895/artifacts/14708836875).

Core CI [44907890934](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934) passed 4/4 jobs: Python 3.12/3.13 tests and both NEURON cross-validation workflows.

The raw artifacts contain the complete 9,015-row voltage trace matrix, the 30-row summary table and the simulation log for each cell.

## 6. Next experiment: separate time-step and spatial convergence

The next run is a 12-job factorial matrix:
- two morphologies;
- NEURON maximum segment lengths of 0.125 and 0.0625 µm;
- backward-Euler dt values of 0.1, 0.05 and 0.025 ms.

This separates time-integration effects from mesh/source/probe placement effects. Source offsets and waveform errors must be compared across the full matrix; do not tune Ri/Rm/Cm/Eleak.

## Verified time/space convergence extension — 21/11/2026

The subsequent 12-job factorial audit [44908381318](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318) passed 12/12 and Core CI [44908381336](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336) passed 4/4. It extended the original dt=0.05 ms / mesh=0.125 µm transient comparison to dt=0.1/0.05/0.025 ms and mesh=0.125/0.0625 µm.

- The cross-simulator mismatch remains almost unchanged with dt at fixed mesh.
- Pairwise time-step refinement follows backward-Euler first-order behavior: halving dt nearly halves the waveform difference between successive time grids (ratios 1.985 and 1.984).
- Mesh refinement improves NMO_68174 but worsens NMO_68175, including a case where SWC-arc interpolation is worse than nearest-centre readout.
- Full report: [HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md](HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md).
