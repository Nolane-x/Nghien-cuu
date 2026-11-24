# Research log — Peng four-layout q25 PRIMA ablation

**Date:** 24 November 2026  
**Topic:** isolate basal-q25 versus apical-q25 port enrichment  
**Branch:** research/prima-peng-q25-four-layout-ablation-2026-11-24

## Question and design

Question: on the NMO_163775 Peng Control morphology, which q25 probe contributes to the shared-output error trade-off observed when both q25 outputs are added?

Four matched layouts were replayed against independently generated full-Hines references:
1. canonical seven ports;
2. seven plus basal-q25;
3. seven plus apical-q25;
4. seven plus both q25 probes.

The same morphology, 0.5 µm mesh cap, six expansion shifts, basis orders 112/168, nine passive parameter scenarios, AC frequencies, source sites, pulse widths, pulse amplitude, onset, duration and dt were held fixed. Shared outputs were paired by exact SWC node ID.

## Execution record

- Corrected workflow: [45326802613](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326802613) — **success**.
- Earlier workflow: [45326775736](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326775736) — failed on the pre-fix code snapshot; superseded.
- Generated result commit: `f459e82`.
- Artifact: [nmo163775-peng-q25-four-layout-prima-ablation](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326802613/artifacts/14890033935), SHA-256 `5af588bac76b6d6accbd5fcc4e520873d60ac46873592cbdfa18ca9771c1b50d`.
- Runtime: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2; 317.18 s wall time, 160,180 KB maximum RSS.
- The corrected workflow passed the focused q25 regression suite, existing Peng source/PRIMA regression suite, pinned SWC SHA-256 verification, Import3D preflight, full simulation, result commit and artifact upload.

## Read-back coverage

The report JSON and all CSV files were fetched again from the branch. Exact expected and actual data rows agree:

| Dataset | Expected and actual rows |
|---|---:|
| Reduced models | 72 |
| AC frequency matrices | 648 |
| Per-port transient observations | 3,456 |
| Matched shared outputs vs seven-port | 2,268 |
| q25-only observations | 432 |
| Shared-Hines comparisons | 1,134 |

All 1,134 shared-Hines comparisons have exactly zero maximum absolute voltage difference and exactly zero relative L2 difference.

## Results

### Shared outputs versus the seven-port baseline

| Layout | Order | Median transient NRMSE (%) | Maximum transient NRMSE (%) | Median candidate / seven error ratio | Worse / better of 378 |
|---|---:|---:|---:|---:|---:|
| seven | 112 | 1.411e-7 | 5.221e-6 | baseline | — |
| eight_basal_q25 | 112 | 9.204e-7 | 3.376e-5 | 5.715× | 378 / 0 |
| eight_apical_q25 | 112 | 9.358e-7 | 3.686e-5 | 6.495× | 378 / 0 |
| nine_both_q25 | 112 | 1.251e-5 | 2.159e-4 | 78.051× | 378 / 0 |
| seven | 168 | 5.933e-10 | 1.290e-8 | baseline | — |
| eight_basal_q25 | 168 | 1.101e-9 | 1.300e-8 | 1.036× | 302 / 76 |
| eight_apical_q25 | 168 | 9.052e-10 | 1.942e-8 | 1.046× | 303 / 75 |
| nine_both_q25 | 168 | 1.163e-8 | 6.066e-7 | 14.525× | 351 / 27 |

At order 168, either q25 port alone produces only a small relative shift against the seven-port baseline. Adding both together produces a distinctly larger penalty in this matched experiment. The absolute error remains very small: maximum transient NRMSE at this order is 6.066e-7%.

At order 112, the same direction is stronger and all enriched layouts are worse on every paired shared-output observation. The results are therefore basis-order-sensitive.

### Added q25 outputs themselves

| Layout | Order | Observations | Median q25 NRMSE (%) | Maximum q25 NRMSE (%) |
|---|---:|---:|---:|---:|
| eight_basal_q25 | 112 | 54 | 1.642e-6 | 2.258e-5 |
| eight_basal_q25 | 168 | 54 | 1.840e-9 | 1.223e-8 |
| eight_apical_q25 | 112 | 54 | 6.925e-7 | 7.049e-6 |
| eight_apical_q25 | 168 | 54 | 4.587e-10 | 4.332e-9 |
| nine_both_q25 | 112 | 108 | 1.848e-5 | 2.159e-4 |
| nine_both_q25 | 168 | 108 | 1.557e-8 | 4.282e-7 |

The apical-only q25 output has lower error than the basal-only q25 output in this run. The dual-q25 output error is not a simple additive combination of the single-probe results. This indicates an interaction in the reduced numerical construction, but does not identify its mechanism.

## Interpretation and next research step

The ablation isolates the empirical layout effect for one passive mouse morphology; it does not establish a population-level rule or a biological conclusion. Large error ratios must be interpreted with absolute errors because the seven-port denominator is already extremely small. Full Hines remains canonical and production solver defaults remain unchanged.

The next useful experiment is not to promote a port count from this single morphology. First inspect basis construction / conditioning and shift sensitivity for the dual-q25 configuration, then repeat the same controlled ablation on another morphology before proposing any default change.

## Files created

- `amsn-core/examples/replay_nmo163775_four_layout_ablation.py`
- `amsn-core/tests/test_nmo163775_four_layout_ablation.py`
- `.github/workflows/amsn-prima-peng-q25-four-layout-ablation.yml`
- `HANDOFF_2026-11-24_PENG-Q25-FOUR-LAYOUT-ABLATION.md`
- This research log.
- Detailed report: `amsn-core/research/PRIMA_PENG_Q25_FOUR_LAYOUT_ABLATION_2026-11-24.md`
- Eleven result files under `amsn-core/results/NMO_163775_PengControl_prima_q25_four_layout_ablation_2026-11-24*`.

## Interpretation limits

One mouse morphology, passive linear-RC only, no biological validation. NeuroMorpho metadata says No Diameter. Keep full Hines canonical and production defaults unchanged.
