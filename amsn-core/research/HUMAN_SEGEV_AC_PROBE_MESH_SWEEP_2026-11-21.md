# Segev AC probe-coordinate mesh convergence — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** [352e7177550722d74a70deefe802e2f315c9477a](https://github.com/Nolane-x/Nghien-cuu/commit/352e7177550722d74a70deefe802e2f315c9477a)  
**Probe mesh workflow:** [44902130621 — successful, 6/6 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621)  
**Core CI:** [44902130609 — successful, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130609)  
**Raw summary:** [human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv](../results/human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv)

## 1. Question

Does the site-dependent effect of complex-linear interpolation between NEURON segment-centre impedances diminish as spatial resolution is refined, and does that interpolation improve the AMSN-versus-NEURON passive AC residual consistently?

## 2. Protocol and validation

Two NeuroMorpho human temporal L2/3 morphologies were tested independently:
- NMO_68174 / cell1125.
- NMO_68175 / cell1204.

The six-job matrix used NEURON 9.0.2 at maximum segment lengths of 0.25, 0.125 and 0.0625 µm for each cell. Each job ran the full 81-test AMSN suite, checked the morphology fixture and emitted 120 rows: three exact-SWC sources × five exact-SWC probes × eight frequencies (0.1–3,000 Hz). Passive parameters remained fixed at Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.

For every source/probe/frequency row, the audit compared:
1. NEURON transfer impedance at the exact SWC arc coordinate.
2. NEURON transfer impedance at the nearest segment centre.
3. Complex-linear interpolation of transfer impedance between the two adjacent segment centres.

Interpolation was applied to the complex quantity (real and imaginary parts), not separately to magnitude and phase.

The six mesh jobs passed, generated 720 rows total and uploaded individual CSV/log artifacts. The separate Core CI passed all four jobs: Python 3.12 tests, Python 3.13 tests, and both NEURON 9.0.2 cross-validation jobs.

## 3. Probe-readout sensitivity across meshes

In all 720 rows, exact-SWC and nearest-segment-centre readouts were identical at exported precision. The exact-vs-nearest complex delta therefore has median, p95 and maximum of zero in every cell/mesh combination.

Complex-linear interpolation changed the readout in a manner that depends on probe, cell, frequency and mesh:

| Cell | Mesh cap (µm) | Interpolation delta median | P95 | Maximum |
|---|---:|---:|---:|---:|
| NMO_68174 | 0.25 | 0.002970% | 0.132757% | 0.213915% |
| NMO_68174 | 0.125 | 0.000247% | 0.025229% | 0.057785% |
| NMO_68174 | 0.0625 | 0.000453% | 0.024298% | 0.041671% |
| NMO_68175 | 0.25 | 0.001827% | 0.123073% | 0.209515% |
| NMO_68175 | 0.125 | 0.000825% | 0.041143% | 0.095872% |
| NMO_68175 | 0.0625 | 0.000263% | 0.021311% | 0.042864% |

The maximum interpolation shift occurred at 3,000 Hz in all six cell/mesh runs. Maximum shift falls substantially from 0.25 to 0.0625 µm in both cells:
- NMO_68174: 0.213915% → 0.041671%.
- NMO_68175: 0.209515% → 0.042864%.

The median is not strictly monotone for NMO_68174: 0.000247% at 0.125 µm versus 0.000453% at 0.0625 µm. It is therefore more accurate to say that the high-percentile and maximum readout differences shrink strongly with refinement, not that every statistic decreases monotonically.

The strongest probes also change with cell and mesh. At 0.25 µm, the largest shift is basal q50 for NMO_68174 and apical q50 for NMO_68175. At 0.125 µm, the maximum shifts to apical q90 for NMO_68174 and apical q50 for NMO_68175. At 0.0625 µm, apical q90 is the largest for both.

## 4. Re-evaluation against the same AMSN outputs

Each probe CSV was joined one-to-one with the original AMSN/NEURON passive frequency-response CSV for the same morphology and mesh using source, source SWC ID, probe, probe SWC ID and frequency. Every join contained exactly 120 matched rows; no unmatched rows were found.

The following table compares the error between the same AMSN complex transfer impedance and two NEURON readouts: exact-SWC and complex interpolation.

| Cell | Mesh (µm) | Readout | Median error | P95 | Maximum |
|---|---:|---|---:|---:|---:|
| NMO_68174 | 0.25 | Exact SWC | 0.005078% | 0.148676% | 0.365601% |
| NMO_68174 | 0.25 | Interpolated | 0.001647% | 0.072337% | 0.184093% |
| NMO_68174 | 0.125 | Exact SWC | 0.001555% | 0.049634% | 0.130599% |
| NMO_68174 | 0.125 | Interpolated | 0.000670% | 0.046984% | 0.132786% |
| NMO_68174 | 0.0625 | Exact SWC | 0.001221% | 0.053004% | 0.133955% |
| NMO_68174 | 0.0625 | Interpolated | 0.000253% | 0.033139% | 0.132166% |
| NMO_68175 | 0.25 | Exact SWC | 0.010372% | 0.200565% | 0.395064% |
| NMO_68175 | 0.25 | Interpolated | 0.008078% | 0.113393% | 0.186395% |
| NMO_68175 | 0.125 | Exact SWC | 0.002297% | 0.073495% | 0.169222% |
| NMO_68175 | 0.125 | Interpolated | 0.001105% | 0.059094% | 0.125637% |
| NMO_68175 | 0.0625 | Exact SWC | 0.003012% | 0.059626% | 0.099512% |
| NMO_68175 | 0.0625 | Interpolated | 0.003131% | 0.066941% | 0.104835% |

Per-row comparison counts (interpolation error lower / higher / unchanged than exact-SWC) were:

| Cell | Mesh (µm) | Improved | Worsened | Unchanged |
|---|---:|---:|---:|---:|
| NMO_68174 | 0.25 | 73 | 23 | 24 |
| NMO_68174 | 0.125 | 26 | 70 | 24 |
| NMO_68174 | 0.0625 | 77 | 19 | 24 |
| NMO_68175 | 0.25 | 74 | 22 | 24 |
| NMO_68175 | 0.125 | 64 | 32 | 24 |
| NMO_68175 | 0.0625 | 42 | 54 | 24 |

### Key interpretation

Interpolation is clearly not a universally superior readout:
- At 0.25 µm, median, p95 and maximum cross-simulator errors improve for both cells.
- At 0.125 µm, NMO_68175 improves on all three aggregate statistics; NMO_68174's median and p95 improve slightly while its maximum worsens slightly.
- At 0.0625 µm, NMO_68174 improves on all three aggregate statistics. NMO_68175 worsens on all three: median 0.003012% → 0.003131%, p95 0.059626% → 0.066941%, maximum 0.099512% → 0.104835%.

Thus the difference between readout methods becomes smaller with finer meshes, but the change in cross-simulator residual does not converge to a uniform benefit. The sign and size of the effect remain cell-/probe-dependent. In particular, the NMO_68175 0.0625 µm result shows that interpolation can move away from the AMSN result even when the interpolation shift itself is smaller.

## 5. Decision

**Keep exact-SWC probe coordinates as the canonical cross-simulator baseline. Do not switch the production audit to complex interpolation.**

Complex-linear interpolation should remain a diagnostic column because:
- it reduces errors for many pairs and strongly reduces some large residuals;
- it worsens a material subset of pairs;
- it does not produce a consistent cross-morphology benefit at the finest mesh;
- interpolation is an alternative numerical readout, not an independently established continuum truth.

No Ri/Rm/Cm/Eleak values were changed. No biological accuracy claim is made. Relative complex errors should still be reviewed alongside absolute transfer magnitudes, especially on weak paths.

## 6. Reproducibility artifacts

Mesh sweep [44902130621](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621), 6/6 jobs passed:

| Cell | Mesh (µm) | Artifact |
|---|---:|---:|
| NMO_68174 | 0.25 | [14706705700](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14706705700) |
| NMO_68174 | 0.125 | [14706511545](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14706511545) |
| NMO_68174 | 0.0625 | [14706785100](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14706785100) |
| NMO_68175 | 0.25 | [14705604235](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14705604235) |
| NMO_68175 | 0.125 | [14705544460](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14705544460) |
| NMO_68175 | 0.0625 | [14706168324](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621/artifacts/14706168324) |

Core CI [44902130609](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130609) passed 4/4 jobs, including Python 3.12/3.13 tests and both NEURON 9.0.2 cross-validation jobs.

Summary data: [CSV](../results/human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv). Detailed raw CSVs include 120 rows each and the per-row mesh cap.

## 7. Next research step

The probe readout variable is now bounded across three mesh caps. The remaining residual should be investigated through matched-support geometry at branchpoints/section junctions and by reconciling how AMSN's SWC electrical nodes represent finite-volume control volumes versus NEURON's section/segment geometry. Do not attempt to remove the remaining residual by tuning passive membrane parameters.
