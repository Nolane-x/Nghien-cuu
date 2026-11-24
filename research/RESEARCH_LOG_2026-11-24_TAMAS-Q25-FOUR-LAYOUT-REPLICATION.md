# Research log — Tamas human pyramidal q25 four-layout replication

**Date:** 24 November 2026  
**Branch:** research/prima-tamas-q25-four-layout-replication-2026-11-24  
**Successful workflow:** [45330512800](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800)  
**Result archive commit:** `83e3fd8de612404fe821365a87489ce591355705`

## Motivation and question

The NMO_163775 Peng mouse four-layout experiment found a large relative shared-output penalty for the dual-q25 layout at order 168 (14.525× median candidate/seven error ratio), while either q25 probe alone showed only a small relative shift. This independent replication tests whether that pattern generalizes to a human pyramidal reconstruction.

NMO_107159 is one female Tamas human pyramidal Control-condition comparison cell. It is not a rosehip interneuron and is not a population sample. Its SWC has 7,228 records and pinned SHA-256 `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`. Canonical ports: `[1, 5564, 6363, 7023, 4301, 4735, 4623]`; q25-only nodes: basal 6609 and apical 4404.

## Design

Four matched layouts: canonical seven; seven + basal-q25; seven + apical-q25; seven + both q25 probes. The same 0.5 µm mesh cap, six shifts, basis orders 112/168, nine passive parameter scenarios, nine AC frequencies, three sources, two pulse widths, pulse current, onset, duration and dt were used. Full-Hines reference traces were produced independently for each layout, then paired by exact shared SWC IDs.

## Execution and validation

- First run [45330465196](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330465196): tests, checksum, preflight and simulation passed; result-commit shell step failed due malformed line continuation.
- Corrected run [45330512800](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800): **success** across all steps, including commit and artifact upload.
- Test result: 25 passed.
- Runtime: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2; 792.91 s wall time, 143,324 KB maximum RSS.
- Result commit: `83e3fd8de612404fe821365a87489ce591355705`.
- Artifact: [nmo107159-tamas-q25-four-layout-prima-replication](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800/artifacts/14892657539), SHA-256 `defc9964f3a2bca8670d6f7fb4552c2202d6afb04c0b8172a4d2cd7958e245ad`.

The report JSON and all CSVs were read back from the branch. Expected and actual row counts match exactly: 72 models, 648 frequency matrices, 3,456 transient rows, 2,268 matched shared pairs, 432 q25-only output observations and 1,134 shared-Hines comparisons. All 1,134 Hines comparisons have exactly zero maximum absolute voltage difference and zero relative L2 difference.

## Results — shared outputs versus seven-port

Each candidate has 378 matched shared-output pairs per basis order. NRMSE values are percentages.

| Layout | Order | Median candidate/seven ratio | Worse / better / tie pairs | Median candidate NRMSE (%) | Maximum candidate NRMSE (%) |
|---|---:|---:|---:|---:|---:|
| eight_basal_q25 | 112 | 2.924× | 361 / 17 / 0 | 1.4701e-7 | 4.2189e-6 |
| eight_apical_q25 | 112 | 3.745× | 366 / 12 / 0 | 1.8528e-7 | 5.9813e-6 |
| nine_both_q25 | 112 | 42.723× | 378 / 0 / 0 | 1.9646e-6 | 3.9507e-5 |
| eight_basal_q25 | 168 | 1.000026× | 216 / 161 / 1 | 2.8336e-8 | 5.4511e-7 |
| eight_apical_q25 | 168 | 1.000023× | 213 / 165 / 0 | 2.8336e-8 | 5.4511e-7 |
| nine_both_q25 | 168 | 1.001032× | 214 / 164 / 0 | 2.8579e-8 | 5.4559e-7 |

The large dual-q25 penalty at order 168 in the Peng mouse experiment does not reproduce here. At order 168 the Tamas dual-q25 ratio is near unity and the absolute error remains very small. All three q25-enriched layouts show order-112 degradation, especially the dual-q25 layout.

## Results — q25-only output traces

| Layout | Order | Observations | Median q25 NRMSE (%) | Maximum q25 NRMSE (%) |
|---|---:|---:|---:|---:|
| basal-q25 only | 112 | 54 | 3.0440e-7 | 3.4571e-6 |
| apical-q25 only | 112 | 54 | 1.7058e-7 | 4.0189e-6 |
| dual-q25 | 112 | 108 | 3.0201e-6 | 3.5323e-5 |
| basal-q25 only | 168 | 54 | 3.0470e-8 | 2.3729e-7 |
| apical-q25 only | 168 | 54 | 2.1518e-8 | 1.7479e-7 |
| dual-q25 | 168 | 108 | 2.4895e-8 | 2.3680e-7 |

At order 168, dual-q25 q25-only error is between the individual basal and apical medians, rather than being markedly worse than both. This agrees with the near-unity shared-output result.

## Cross-morphology synthesis

The order-168 dual-q25 penalty is not universal across the two tested morphologies:
- Peng mouse NMO_163775: 14.525× median ratio at order 168.
- Tamas human pyramidal NMO_107159: 1.001× median ratio at order 168.

Order 112 degradation appears in both. Thus the current evidence suggests morphology-by-order interaction, not a simple monotonic port-count rule. This is a hypothesis about numerical basis sensitivity; it does not prove a mechanism.

## Files

- `amsn-core/examples/replay_nmo107159_four_layout_replication.py`
- `amsn-core/tests/test_nmo107159_four_layout_replication.py`
- `.github/workflows/amsn-prima-tamas-q25-four-layout-replication.yml`
- `HANDOFF_2026-11-24_TAMAS-Q25-FOUR-LAYOUT-REPLICATION.md`
- This research log.
- Detailed report: `amsn-core/research/PRIMA_TAMAS_Q25_FOUR_LAYOUT_REPLICATION_2026-11-24.md`
- Eleven result files under `amsn-core/results/NMO_107159_TamasHumanPyramidalControl_prima_q25_four_layout_replication_2026-11-24*`.

## Scientific limits

One human morphology, passive linear-RC only. NeuroMorpho lists Diameter, 3D and Angles; this is not active-channel, synaptic, plasticity or biological validation. Passive membrane parameters remain model assumptions. Keep this human morphology separate from the mouse mesh stratum. Full Hines stays canonical and no production solver defaults change.
