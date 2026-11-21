# Segev transient source-placement alignment — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 555cb0d22e4cb25c513d50af24e1effaf8c6c2d9](https://github.com/Nolane-x/Nghien-cuu/commit/555cb0d22e4cb25c513d50af24e1effaf8c6c2d9)  
**Source-placement workflow:** [44910070325 — success, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325)  
**Core CI:** [44910070326 — success, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326)  
**Summary CSV:** [human_segev_transient_source_alignment_summary_2026-11-21.csv](../results/human_segev_transient_source_alignment_summary_2026-11-21.csv)

## 1. Research question

The preceding transient convergence matrix showed that the cross-simulator error is nearly invariant to dt, while the effect of spatial refinement is morphology-dependent. The NEURON point current was placed at the nearest segment centre, whereas AMSN injects at the exact SWC electrical node.

This experiment compares two NEURON source-placement rules while preserving the same total 10 pA pulse:

1. Nearest-centre baseline: one IClamp at the nearest segment centre.
2. Weighted two-centre split: two IClamps at the bracketing segment centres, with current weights (1-w) and w taken from the exact SWC arc interpolation weight.

The AMSN source is unchanged and remains at the exact SWC electrical node.

## 2. Protocol and validation

The four-job matrix covers:
- NMO_68174 / cell1125 and NMO_68175 / cell1204.
- NEURON mesh caps 0.125 and 0.0625 µm.
- Fixed dt=0.05 ms, duration 30 ms, pulse +10 pA from 2 to 12 ms.
- NEURON 9.0.2; same passive Ri/Rm/Cm/Eleak as the prior transient tests.

Each configuration produced:
- 3 sources × 5 probes × 2 source placements × 2 probe readouts = 60 summary rows.
- 3 sources × 5 probes × 2 source placements × 601 time samples = 18,030 trace rows.

All four jobs passed the full 81-test AMSN suite, generated the expected rows and uploaded trace/summary/log artifacts. The total clamp current was checked at every time sample. Maximum conservation error was 1.735e-18 nA; the other three configurations were exact at exported precision. The maximum time-grid mismatch was 6.36e-13 ms.

## 3. Comparison results

NRMSE values below are percentages of peak NEURON voltage deflection. Counts compare the 15 source/probe pairs for the weighted source placement against the nearest-centre baseline; five unchanged pairs are typically cases where the source mapping resolves to the same segment (not five additional independent improvements).

| Cell | Mesh µm | Probe readout | Nearest source max NRMSE | Weighted split max NRMSE | Improved / worsened / unchanged |
|---|---:|---|---:|---:|---:|
| NMO_68174 | 0.125 | Nearest centre | 0.001641% | 0.001641% | 5 / 5 / 5 |
| NMO_68174 | 0.125 | SWC-arc interpolation | 0.000357% | 0.000265% | 5 / 5 / 5 |
| NMO_68174 | 0.0625 | Nearest centre | 0.001286% | 0.001161% | 2 / 8 / 5 |
| NMO_68174 | 0.0625 | SWC-arc interpolation | 0.000190% | 0.000265% | 0 / 10 / 5 |
| NMO_68175 | 0.125 | Nearest centre | 0.002370% | 0.001558% | 10 / 0 / 5 |
| NMO_68175 | 0.125 | SWC-arc interpolation | 0.000791% | 0.000192% | 10 / 0 / 5 |
| NMO_68175 | 0.0625 | Nearest centre | 0.002581% | 0.001655% | 8 / 2 / 5 |
| NMO_68175 | 0.0625 | SWC-arc interpolation | 0.002633% | 0.000192% | 10 / 0 / 5 |

### Main finding

The weighted split is highly beneficial for NMO_68175:
- At 0.125 µm it reduces the maximum NRMSE from 0.002370% to 0.001558% for nearest-centre probes and from 0.000791% to 0.000192% for SWC-arc interpolated probes.
- At 0.0625 µm it reduces the maximum from 0.002581% to 0.001655% for nearest-centre probes and from 0.002633% to 0.000192% for interpolated probes.

For NMO_68174, the benefit depends on mesh:
- At 0.125 µm, the maximum interpolated-probe NRMSE decreases from 0.000357% to 0.000265%, but per-pair outcomes are mixed for both readout modes.
- At 0.0625 µm, nearest-centre maximum improves modestly (0.001286% to 0.001161%), but the interpolated readout becomes worse: maximum NRMSE rises from 0.000190% to 0.000265%, with 10 worsened and zero improved pairs among the 15 comparisons.

Therefore the weighted two-centre source is not a universal improvement. Its benefit depends on morphology, mesh and probe readout. In particular, cell1204 benefits strongly, whereas cell1125 at the finer mesh shows the opposite result for interpolated probes.

## 4. Interpretation and decision

**Do not replace nearest-centre IClamp as the universal source-placement default.** Preserve weighted two-centre placement as an optional diagnostic/source-alignment mode.

This experiment supports three conclusions:
- Nonzero source-centre offsets can materially contribute to transient mismatch, especially in NMO_68175.
- Splitting current by interpolation weights can reduce that source-placement component for some geometries.
- A weighted current distribution is itself a discrete approximation; it is not automatically the exact physical point-source solution. A lower NRMSE is evidence about numerical mapping sensitivity, not biological validity.

The current sum was preserved at every time sample; this result is not explained by injecting extra or missing charge. No passive parameters were modified.

## 5. Reproducibility

Source-placement workflow [44910070325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325) passed all four jobs; Core CI [44910070326](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326) passed all four jobs.

| Morphology | Mesh µm | Artifact |
|---|---:|---:|
| NMO_68174 / cell1125 | 0.125 | [14709128221](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325/artifacts/14709128221) |
| NMO_68174 / cell1125 | 0.0625 | [14708479710](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325/artifacts/14708479710) |
| NMO_68175 / cell1204 | 0.125 | [14709089986](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325/artifacts/14709089986) |
| NMO_68175 / cell1204 | 0.0625 | [14709249249](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325/artifacts/14709249249) |

Each artifact includes 18,030 raw time-series rows, 60 summaries and the job log. The corrected summary includes both full probe-readout mode names; the earlier diagnostic run with truncated probe labels is not used in this report.

## 6. Next step

The next high-value test is to compare direct NEURON AC transfer impedance under the same two source-placement definitions:
- nearest segment centre as the existing baseline;
- two adjacent segment current sources with the same interpolation weights.

Keep the total injected current/forcing normalized and compare complex transfer impedance at the same five exact SWC probes and eight frequencies. This will test whether the source-placement benefit observed in transients also appears in the frequency domain. Do not tune Ri/Rm/Cm/Eleak.
