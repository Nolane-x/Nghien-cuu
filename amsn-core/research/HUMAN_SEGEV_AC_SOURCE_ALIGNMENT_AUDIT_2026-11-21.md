# Segev AC source-placement alignment — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 458ce327689b602faaeaca3f14fead835a7d4dd4](https://github.com/Nolane-x/Nghien-cuu/commit/458ce327689b602faaeaca3f14fead835a7d4dd4)  
**AC source-placement workflow:** [44910754764 — success, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764)  
**Core CI:** [44910754810 — success, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810)  
**Configuration summary:** [human_segev_ac_source_alignment_summary_2026-11-21.csv](../results/human_segev_ac_source_alignment_summary_2026-11-21.csv)  
**Baseline vs weighted comparison:** [human_segev_ac_source_alignment_comparison_2026-11-21.csv](../results/human_segev_ac_source_alignment_comparison_2026-11-21.csv)

## 1. Research question

The transient source-placement audit showed that a current split over adjacent NEURON segment centres improves NMO_68175 substantially but is morphology-/mesh-dependent for NMO_68174. This experiment checks whether the same source-placement sensitivity appears in passive AC transfer impedance.

## 2. Method and validation

For each morphology at NEURON mesh caps 0.125 and 0.0625 µm:
- Three source sites (soma, basal q75, apical q75).
- Five probe sites (soma, basal q50/q90, apical q50/q90).
- Eight frequencies (0.1–3,000 Hz).
- Three source modes:
  1. exact SWC arc;
  2. nearest segment centre;
  3. weighted adjacent centres, computed by complex linear superposition of the two bracketing source transfer responses using weights (1-w,w).
- Three probe modes: exact SWC arc, nearest centre and complex interpolation.

The weighted frequency-domain source is a mathematically valid linear superposition for this passive linear system and represents the same total AC input current because the weights sum to one. It is nevertheless a discrete two-location source approximation, not a claim that this is the unique physical continuum source.

Each job generated 1,080 raw rows and 135 grouped summary rows. The four jobs all passed the complete AMSN test suite; Core CI passed 4/4 jobs.

## 3. Weighted-source impact against nearest-centre source

The table compares NEURON's nearest-centre source baseline with the weighted adjacent-centre source, using identical probe modes and AMSN exact-SWC source references. Error metrics are the complex transfer-impedance relative error in percent, aggregated over all three sources, five probes and eight frequencies.

| Cell | Mesh µm | Probe readout | Baseline median / P95 / max | Weighted median / P95 / max |
|---|---:|---|---:|---:|
| NMO_68174 | 0.125 | Exact or nearest | 0.001555 / 0.049634 / 0.130599% | 0.001455 / 0.045051 / 0.129612% |
| NMO_68174 | 0.125 | Interpolated | 0.000670 / 0.046984 / 0.132786% | 0.000612 / 0.048510 / 0.133201% |
| NMO_68174 | 0.0625 | Exact or nearest | 0.001221 / 0.053004 / 0.133955% | 0.001351 / 0.055757 / 0.128277% |
| NMO_68174 | 0.0625 | Interpolated | 0.000253 / 0.033139 / 0.132166% | 0.000612 / 0.048607 / 0.133448% |
| NMO_68175 | 0.125 | Exact or nearest | 0.002297 / 0.073495 / 0.169222% | 0.001697 / 0.042116 / 0.068720% |
| NMO_68175 | 0.125 | Interpolated | 0.001105 / 0.059094 / 0.125637% | 0.000313 / 0.041721 / 0.071947% |
| NMO_68175 | 0.0625 | Exact or nearest | 0.003012 / 0.059626 / 0.099512% | 0.000821 / 0.037122 / 0.069568% |
| NMO_68175 | 0.0625 | Interpolated | 0.003131 / 0.066941 / 0.104835% | 0.000311 / 0.041875 / 0.072209% |

The exact-SWC and nearest-centre source modes produced identical NEURON results at exported precision for these source locations. The weighted source changes the response as described above.

### Main morphology-dependent result

**NMO_68175 / cell1204: strong benefit at both meshes.**
- At 0.125 µm, weighted-source maximum complex error falls from 0.169222% to 0.068720% for exact/nearest probes, and from 0.125637% to 0.071947% for interpolated probes.
- At 0.0625 µm, the maximum falls from 0.099512% to 0.069568% for exact/nearest probes, and from 0.104835% to 0.072209% for interpolated probes.
- Medians and P95 values also improve in all four comparisons.

**NMO_68174 / cell1125: mixed or negative result.**
- At 0.125 µm, exact/nearest probe statistics improve modestly. Interpolated-probe median improves, but P95 and maximum worsen slightly.
- At 0.0625 µm, exact/nearest probe median and P95 worsen (0.001221%→0.001351%; 0.053004%→0.055757%) although the maximum improves slightly. For interpolated probes, median/P95/max all worsen (0.000253%→0.000612%; 0.033139%→0.048607%; 0.132166%→0.133448%).

Therefore weighted source placement is not a universal improvement. It reproduces the strong NMO_68175 benefit found in the transient domain, while confirming the NMO_68174 mixed behaviour.

## 4. Interpretation and decision

Keep weighted adjacent-centre source placement as an **optional diagnostic/source-alignment mode**, not a universal default.

The matching transient and AC results on NMO_68175 strengthen the evidence that nonzero source-centre placement can contribute materially to the residual on this morphology. For NMO_68174, the source split is mesh-/probe-dependent and may move some responses away from AMSN. No passive parameter was changed. These results do not prove which discrete source is the exact physical continuum representation and do not constitute biological validation.

## 5. Reproducibility

Workflow [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed all four morphology/mesh jobs; Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4.

| Morphology | Mesh µm | Artifact |
|---|---:|---:|
| NMO_68174 / cell1125 | 0.125 | [14709363697](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764/artifacts/14709363697) |
| NMO_68174 / cell1125 | 0.0625 | [14709507642](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764/artifacts/14709507642) |
| NMO_68175 / cell1204 | 0.125 | [14710165980](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764/artifacts/14710165980) |
| NMO_68175 / cell1204 | 0.0625 | [14710006334](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764/artifacts/14710006334) |

Each artifact contains 1,080 raw rows and 135 grouped summary rows plus its job log.

## 6. Next step

Cross-domain testing now supports the same source-placement interpretation for NMO_68175 and the same caution for NMO_68174. Next, inspect the worst source/probe/frequency pairs in the raw AC CSV and identify whether the residual is concentrated around specific branch orders, short apical edges or source bracket widths. Retain source-mode alternatives and avoid tuning Ri/Rm/Cm/Eleak.
