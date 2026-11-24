# Tamas human pyramidal q25 four-layout PRIMA replication — NMO_107159

**Date:** 24 November 2026  
**Workflow:** [GitHub Actions run 45330512800](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800) — success  
**Result archive commit:** `83e3fd8de612404fe821365a87489ce591355705`  
**Artifact:** [Download workflow artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800/artifacts/14892657539)  
**Artifact SHA-256:** `defc9964f3a2bca8670d6f7fb4552c2202d6afb04c0b8172a4d2cd7958e245ad`

## 1. Aim

This independent replication tests whether the large order-168 dual-q25 shared-output error ratio observed on the Peng mouse morphology generalizes to a human pyramidal morphology.

Four layouts were compared:
- `seven`: canonical seven.
- `eight_basal_q25`: seven plus basal-q25.
- `eight_apical_q25`: seven plus apical-q25.
- `nine_both_q25`: seven plus both q25 probes.

## 2. Source and experimental conditions

- Morphology: NMO_107159 Tamas human pyramidal Control comparison cell.
- One female human reconstruction; age not reported; not a rosehip interneuron.
- SWC: 7,228 records; SHA-256 `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`.
- Canonical shared SWC node IDs: `[1, 5564, 6363, 7023, 4301, 4735, 4623]`.
- Added probes: basal-q25 = 6609; apical-q25 = 4404.
- NEURON segment cap: 0.5 µm; NEURON 9.0.2.
- Python 3.12.16; NumPy 2.5.5.
- Six expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Basis orders: 112 and 168.
- Nine passive parameter scenarios; nine AC frequencies.
- Sources: soma, basal-q75, apical-q75.
- Pulse widths: 2 and 10 ms; amplitude 10 pA; onset 2 ms; duration 20 ms; dt 0.1 ms.
- Full Hines is the reference for every layout; shared outputs are matched by exact SWC node ID.

## 3. Coverage and validation

| Dataset | Expected rows | Verified rows |
|---|---:|---:|
| Model configurations | 72 | 72 |
| Frequency matrices | 648 | 648 |
| Transient port observations | 3,456 | 3,456 |
| Shared outputs matched against seven-port | 2,268 | 2,268 |
| q25-only output observations | 432 | 432 |
| Shared-Hines consistency comparisons | 1,134 | 1,134 |

All 1,134 shared-Hines rows are exact matches: maximum absolute voltage difference = 0 V and relative L2 difference = 0%. All 25 regression tests, source checksum validation, Import3D preflight, simulation, result commit and artifact upload passed in the corrected workflow.

Runtime: 792.91 seconds wall time, 975.98 seconds user CPU, 143,324 KB maximum RSS.

The first workflow attempt `45330465196` passed through simulation but failed at the result-commit shell step. The line-continuation issue was corrected; the complete corrected run `45330512800` passed. Only the corrected run is used for numeric claims.

## 4. Shared-output error versus the seven-port baseline

Each candidate has 378 matched shared-output pairs per basis order. NRMSE values are percentages; ratios are candidate error divided by the seven-port error.

| Layout | Order | Median error ratio | Worse / better / tie pairs | Median candidate NRMSE (%) | Maximum candidate NRMSE (%) |
|---|---:|---:|---:|---:|---:|
| eight_basal_q25 | 112 | 2.924× | 361 / 17 / 0 | 1.4701e-7 | 4.2189e-6 |
| eight_apical_q25 | 112 | 3.745× | 366 / 12 / 0 | 1.8528e-7 | 5.9813e-6 |
| nine_both_q25 | 112 | 42.723× | 378 / 0 / 0 | 1.9646e-6 | 3.9507e-5 |
| eight_basal_q25 | 168 | 1.000026× | 216 / 161 / 1 | 2.8336e-8 | 5.4511e-7 |
| eight_apical_q25 | 168 | 1.000023× | 213 / 165 / 0 | 2.8336e-8 | 5.4511e-7 |
| nine_both_q25 | 168 | 1.001032× | 214 / 164 / 0 | 2.8579e-8 | 5.4559e-7 |

At order 168, all three candidate layouts are effectively at the seven-port baseline: the dual-q25 median error ratio is 1.001×. Its maximum absolute transient NRMSE is 5.4559e-7%, so both relative and absolute measures remain very small.

At order 112, the same layouts degrade, with the dual-q25 layout showing a 42.723× median ratio and worse error on all 378 shared-output pairs. Its maximum absolute transient NRMSE is 3.9507e-5%.

## 5. Added q25 outputs themselves

| Layout | Order | Observations | Median q25 NRMSE (%) | Maximum q25 NRMSE (%) |
|---|---:|---:|---:|---:|
| basal-q25 only | 112 | 54 | 3.0440e-7 | 3.4571e-6 |
| apical-q25 only | 112 | 54 | 1.7058e-7 | 4.0189e-6 |
| dual-q25 | 112 | 108 | 3.0201e-6 | 3.5323e-5 |
| basal-q25 only | 168 | 54 | 3.0470e-8 | 2.3729e-7 |
| apical-q25 only | 168 | 54 | 2.1518e-8 | 1.7479e-7 |
| dual-q25 | 168 | 108 | 2.4895e-8 | 2.3680e-7 |

At order 168, the dual-q25 output median lies between the separate basal and apical medians; the dual layout does not reproduce the marked q25-output degradation seen in the Peng run.

## 6. Cross-morphology synthesis

| Morphology | Species / cell class | Dual-q25 median shared-output ratio at order 168 |
|---|---|---:|
| NMO_163775 Peng Control | Mouse | 14.525× |
| NMO_107159 Tamas Control | Human pyramidal comparison cell | 1.001× |

The large dual-q25 penalty at order 168 is therefore not universal across the two tested morphologies. Order-112 degradation appears in both. The current evidence suggests a morphology-by-basis-order interaction rather than a simple port-count rule.

This does not establish the mechanism. Basis conditioning, shift coverage and the morphology-dependent geometry are candidate explanations that require targeted tests. Two holdouts are not a population and do not justify a production port-default change.

## 7. Scientific limitations

This is one human morphology and passive linear-RC numerical validation only. NeuroMorpho lists Diameter, 3D and Angles for the reconstruction, but passive membrane parameters remain model assumptions. The experiment does not validate active channels, nonlinear synapses, plasticity, excitability or biological fidelity. Keep this human result separate from the mouse mesh stratum even though both use a 0.5 µm cap.

Full Hines remains canonical. No production solver defaults or behavior were changed.

## 8. Reproducible files

All outputs share the stem:

`NMO_107159_TamasHumanPyramidalControl_prima_q25_four_layout_replication_2026-11-24`

CSV files: `models.csv`, `frequency.csv`, `transient.csv`, `matched_shared_vs_seven.csv`, `matched_summary.csv`, `q25.csv`, `q25_summary.csv`, `hines_shared.csv`, and `summary.csv`; plus `report.json` and `.time.txt`.

Verified Git blob SHA-1 values:
- report JSON: `ca0086d15c497b949f32cb65bb7a24baa2c7dc48`
- summary CSV: `57a1c26723524013af7cb52ef49467b04edff119`
- models CSV: `aa3be0f649882320e3c032239297e15dd805048e`
- frequency CSV: `340e99b85b081b77436387420118e9f47a66a99d`
- transient CSV: `af42fe3df08a31428e232f74504642fe38636872`
- matched shared-vs-seven CSV: `038026f842d16c9b3899e31fb75129f7faa4abc3`
- matched summary CSV: `3221e949f7df0599b00512c8c2ed11901662f965`
- q25 CSV: `29faddf44732b4f68cb29be769062a758d931ed0`
- q25 summary CSV: `795da14ba198c251c0f0d8bd6e473e2f9d64c382`
- shared-Hines CSV: `bb21cb82c79128c0893b4a1e3ef1bf425a58d1b8`
