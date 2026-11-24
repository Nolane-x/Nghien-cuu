# Peng q25 four-layout PRIMA ablation — NMO_163775

**Date:** 24 November 2026  
**Workflow:** [GitHub Actions run 45326802613](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326802613) — success  
**Result archive commit:** `f459e82`  
**Artifact:** [Download workflow artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326802613/artifacts/14890033935)  
**Artifact SHA-256:** `5af588bac76b6d6accbd5fcc4e520873d60ac46873592cbdfa18ca9771c1b50d`

## 1. Aim

This controlled ablation asks whether the nine-port error trade-off seen on the Peng Control holdout is associated with the basal-q25 probe, the apical-q25 probe, or their joint addition to the canonical seven ports.

Four layouts were compared:
- `seven`: canonical seven.
- `eight_basal_q25`: seven plus basal-q25.
- `eight_apical_q25`: seven plus apical-q25.
- `nine_both_q25`: seven plus both q25 probes.

The same SWC, mesh cap, model scenarios, shift set, basis orders, source sites, pulses and numerical settings were kept fixed.

## 2. Experimental conditions

- Morphology: NMO_163775 Peng mouse Control SWC.
- NEURON segment cap: 0.5 µm.
- NEURON: 9.0.2.
- Python: 3.12.16; NumPy: 2.5.5.
- Six expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Basis orders: 112 and 168.
- Nine passive parameter scenarios and nine AC frequencies.
- Three source locations: soma, basal-q75 and apical-q75.
- Pulse widths: 2 and 10 ms; amplitude 10 pA; onset 2 ms; total duration 20 ms; dt 0.1 ms.
- Full-Hines replay is the reference for every layout.
- Shared outputs are paired by exact SWC node ID, not by array order.

## 3. Coverage and independent validation

| Dataset | Expected rows | Verified rows |
|---|---:|---:|
| Model configurations | 72 | 72 |
| Frequency matrices | 648 | 648 |
| Transient port observations | 3,456 | 3,456 |
| Shared outputs paired against seven-port | 2,268 | 2,268 |
| q25-only output observations | 432 | 432 |
| Shared-Hines consistency comparisons | 1,134 | 1,134 |

All 1,134 shared-Hines rows are exact matches: maximum absolute voltage difference = 0 V and relative L2 difference = 0%. All six dedicated regression tests, the existing Peng/PRIMA regression tests, pinned SWC checksum verification, Import3D preflight, simulation and artifact preservation steps passed in the corrected workflow.

Runtime: 317.18 seconds wall time, 479.95 seconds user CPU, 160,180 KB maximum RSS.

## 4. Shared-output error versus the seven-port baseline

NRMSE values below are percentages, not fractions. Each candidate layout has 378 matched shared-output pairs at each basis order.

| Layout | Basis order | Median transient NRMSE (%) | Maximum transient NRMSE (%) | Median candidate / seven error ratio | Worse pairs | Better pairs |
|---|---:|---:|---:|---:|---:|---:|
| seven | 112 | 1.4110e-7 | 5.2214e-6 | 1.000× | — | — |
| eight_basal_q25 | 112 | 9.2036e-7 | 3.3756e-5 | 5.715× | 378 | 0 |
| eight_apical_q25 | 112 | 9.3577e-7 | 3.6860e-5 | 6.495× | 378 | 0 |
| nine_both_q25 | 112 | 1.2506e-5 | 2.1588e-4 | 78.051× | 378 | 0 |
| seven | 168 | 5.9330e-10 | 1.2901e-8 | 1.000× | — | — |
| eight_basal_q25 | 168 | 1.1013e-9 | 1.3003e-8 | 1.036× | 302 | 76 |
| eight_apical_q25 | 168 | 9.0521e-10 | 1.9421e-8 | 1.046× | 303 | 75 |
| nine_both_q25 | 168 | 1.1632e-8 | 6.0657e-7 | 14.525× | 351 | 27 |

The dual-q25 configuration is substantially worse than either isolated q25 configuration under this matched shared-output metric. At order 168, the isolated additions produce median ratios close to one, whereas the dual addition has a 14.525× median ratio. At order 112, all three enriched layouts are worse on all 378 pairs.

The ratios are relative to the seven-port baseline, whose absolute errors are already tiny. The worst absolute transient NRMSE at order 168 is 6.0657e-7%, so a 14.525× ratio must not be described as a large absolute voltage error.

## 5. Accuracy of the added q25 outputs

| Layout | Basis order | q25 observations | Median q25 NRMSE (%) | Maximum q25 NRMSE (%) |
|---|---:|---:|---:|---:|
| eight_basal_q25 | 112 | 54 | 1.6424e-6 | 2.2580e-5 |
| eight_basal_q25 | 168 | 54 | 1.8403e-9 | 1.2233e-8 |
| eight_apical_q25 | 112 | 54 | 6.9245e-7 | 7.0486e-6 |
| eight_apical_q25 | 168 | 54 | 4.5868e-10 | 4.3324e-9 |
| nine_both_q25 | 112 | 108 | 1.8480e-5 | 2.1588e-4 |
| nine_both_q25 | 168 | 108 | 1.5567e-8 | 4.2824e-7 |

At order 168, apical-q25-only has a lower median and maximum q25-output error than basal-q25-only. The dual-q25 layout has larger q25-output errors than either isolated layout. Together with the shared-output comparison, this is evidence of a non-additive interaction in the numerical reduced construction under the tested conditions. It does not reveal the causal mechanism.

## 6. Interpretation

The evidence supports three narrow conclusions for this one experiment:

1. Adding basal-q25 or apical-q25 alone has a modest relative shared-output penalty at order 168, with very small absolute NRMSE.
2. Adding both q25 probes together has a substantially larger relative penalty than either single-probe layout.
3. The effect is basis-order-sensitive: at order 112 every q25-enriched candidate loses all 378 matched comparisons, while the single-probe order-168 results are much closer to the seven-port baseline.

This does **not** establish that nine ports are generally inferior, that one q25 port is biologically more important, or that the joint effect has a known mechanism. The correct next step is to inspect basis conditioning and shift sensitivity for the dual-q25 case and repeat the controlled ablation on another morphology. Do not change production defaults based on this single holdout.

## 7. Scientific limitations

NMO_163775 is one mouse Control-condition morphology, not a population sample. NeuroMorpho metadata lists “No Diameter”; standardized SWC radii must not be presented as measured biological diameters. This is a passive linear-RC numerical experiment only. It does not validate active conductances, synapses, plasticity, excitability, or biological fidelity.

Full Hines remains canonical. The 0.5 µm mesh stratum is kept explicit and should not be pooled with absolute-error results from other mesh caps.

## 8. Reproducible files

The generated results are archived under `amsn-core/results/` with the common stem:

`NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24`

Files: `models.csv`, `frequency.csv`, `transient.csv`, `matched_shared_vs_seven.csv`, `matched_summary.csv`, `q25.csv`, `q25_summary.csv`, `hines_shared.csv`, `summary.csv`, `report.json`, and `.time.txt`.

Verified blob SHA-1 values:
- report JSON: `41414c7155759de42ca90cb086d6797a571fde26`
- summary CSV: `2694c62b80423377125c461a9944139a353c6916`
- models CSV: `b26d8d1ddc50434bfbe7794c31c48197ee4621dc`
- frequency CSV: `d3e5ff141ed51f3d10fbe6364ac04475dac18874`
- transient CSV: `b9998a2283a7898823ee57e5070b8e63039344f3`
- matched shared-vs-seven CSV: `79e0b9dc0db54dcc9061482e2fe0a235db79cebe`
- matched summary CSV: `f52c4d96447d5bf3df9e26987a50469532278d9b`
- q25 CSV: `14d16b56c0c269143988e7b710218f3f75aa032d`
- q25 summary CSV: `c2169744fe3c0994d6a0155078c606b8e18eec9d`
- shared-Hines CSV: `71578175e589634655cc4f2698c91a5afe54066c`
- timing file: `29619c3996f6fd00c6c6ce4d15c5f70cfba2afdd`
