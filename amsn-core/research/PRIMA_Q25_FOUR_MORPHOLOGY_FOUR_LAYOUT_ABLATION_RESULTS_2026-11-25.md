# PRIMA q25 four-layout ablation — numerical results and interaction analysis

**Date:** 25 November 2026  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Protocol:** [four-layout ablation protocol](PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_PROTOCOL_2026-11-25.md)  
**Primary calculation run:** [45585262246](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246)  
**Validated result artifact:** [artifact 15010408589](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246/artifacts/15010408589)  
**Artifact size:** 67,067,789 bytes; SHA-256 3004c7686aae9e4c3f674396740f4ce191e72063b2a6552641c5c082a0f9766b  
**Archival rerun:** [45585843464](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585843464) — launched with the corrected Git commit filter; its numerical replay is separate from the already completed calculation recorded below.

## 1. Execution and acceptance

The first four-layout numerical computation completed successfully. The runner exited with status 0 after **2,546.82 seconds** (about 42.45 minutes). The independent coverage/identity gate also passed. The overall Actions run is marked failed only because its subsequent Git commit step attempted to push the 190.12-MB frequency-summary CSV, which exceeds GitHub's 100-MB per-file limit. The always-run artifact step then uploaded the complete matrix successfully.

The corrected workflow now deliberately excludes that one large CSV from Git commits while retaining it in the Actions artifact. The archival rerun is tracked separately above; do not confuse its eventual job conclusion with the already validated numerical run.

| Output | Expected | Read back |
|---|---:|---:|
| Master frequency grid | 3,201 points | 3,201 |
| Frequency summary | 1,075,536 rows | 1,075,536 |
| Case metrics | 12,096 rows | 12,096 |
| Matched candidate-vs-seven comparisons | 9,072 rows | 9,072 |
| Source/layout/window summaries | 144 rows | 144 |
| Morphology/layout/window summaries | 24 rows | 24 |
| Finite-DFT identity diagnostics | 1,728 rows | 1,728 |

The maximum finite-record DFT identity relative error was **8.78149 × 10⁻¹²**, against a tolerance of **2 × 10⁻⁸**. The maximum absolute identity residual was **4.80983 × 10⁻¹¹ V-samples**. The maximum full/reduced model identity error was **8.74381 × 10⁻¹²**. The frequency summary is 190.12 MB and is retained in the artifact rather than Git.

## 2. Matched experiment

The four layouts are:

- seven: canonical seven shared output ports.
- eight_basal_q25: the same seven plus basal-q25.
- eight_apical_q25: the same seven plus apical-q25.
- nine_both_q25: the same seven plus both q25 ports.

Each candidate is paired against the seven-port result at exactly the same morphology, passive parameter scenario, current-source site, shared output SWC node, pulse width and observation window. Each morphology/window comparison therefore contains **378 matched pairs** (9 scenarios × 3 sources × 2 pulses × 7 outputs).

The numerical protocol is unchanged: PRIMA order 168; nine passive scenarios; soma, basal-q75 and apical-q75 sources; 10-pA pulses of 2 and 10 ms beginning at 2 ms; timestep 0.00625 ms; windows 20 and 40 ms; 0.5-µm NEURON segment cap. The finite-record analysis includes the terminal-state boundary term. It does not equate the periodic transfer term alone with the complete finite response.

## 3. Discrete backward-Euler periodic-transfer error

Each cell below is **median candidate/seven error ratio (number of worse pairs / 378)**. A ratio above 1 means the candidate's periodic-transfer error is larger.

| Morphology | Window | Basal-only 8-port | Apical-only 8-port | Both 9-port |
|---|---:|---:|---:|---:|
| Jacobs Control | 20 ms | 1.000 (195) | 1.000 (185) | 1.001 (215) |
| Jacobs Control | 40 ms | 1.004 (253) | 1.002 (218) | 1.002 (218) |
| Tamas human Control comparison | 20 ms | 2.123 (372) | 1.999 (365) | 32.267 (378) |
| Tamas human Control comparison | 40 ms | 2.232 (375) | 1.983 (366) | 28.033 (378) |
| Allen L2/3 epilepsy specimen | 20 ms | 1.046 (286) | 1.200 (315) | 1.131 (290) |
| Allen L2/3 epilepsy specimen | 40 ms | 1.046 (281) | 1.218 (310) | 1.157 (302) |
| Peng mouse Control | 20 ms | 1.690 (348) | 2.160 (378) | 42.412 (378) |
| Peng mouse Control | 40 ms | 1.687 (378) | 1.972 (378) | 32.576 (378) |

The absolute median error increase for the combined nine-port layout was approximately:

| Morphology | Window | Median discrete-BE error increase |
|---|---:|---:|
| Jacobs | 20 ms | 1.165 × 10⁻¹⁴ percentage points |
| Jacobs | 40 ms | 1.556 × 10⁻¹⁴ percentage points |
| Tamas | 20 ms | 1.650 × 10⁻⁸ percentage points |
| Tamas | 40 ms | 1.829 × 10⁻⁸ percentage points |
| Allen | 20 ms | 3.278 × 10⁻¹² percentage points |
| Allen | 40 ms | 4.372 × 10⁻¹² percentage points |
| Peng | 20 ms | 6.368 × 10⁻⁸ percentage points |
| Peng | 40 ms | 6.866 × 10⁻⁸ percentage points |

The absolute increases are small in absolute percentage-point units, even where ratios are large. This distinction is important when the seven-port reference error is itself very small.

## 4. Numerically stable perturbation-coordinate transient error

This metric compares transient responses in y = V − E_leak coordinates and avoids subtracting two near-0.1-V values to recover small perturbations. Each cell is again **median candidate/seven ratio (worse pairs / 378)**. The last column is the median absolute increase in transient NRMSE, in percentage points.

| Morphology | Window | Basal-only 8-port | Apical-only 8-port | Both 9-port | Both: median absolute increase |
|---|---:|---:|---:|---:|---:|
| Jacobs Control | 20 ms | 0.975 (173) | 1.363 (263) | 1.317 (292) | 2.593 × 10⁻¹² |
| Jacobs Control | 40 ms | 1.035 (192) | 1.373 (265) | 1.427 (291) | 3.068 × 10⁻¹² |
| Tamas human Control comparison | 20 ms | 1.370 (338) | 1.213 (306) | 25.268 (372) | 3.313 × 10⁻⁹ |
| Tamas human Control comparison | 40 ms | 2.571 (371) | 2.323 (361) | 49.840 (378) | 1.315 × 10⁻⁸ |
| Allen L2/3 epilepsy specimen | 20 ms | 1.380 (297) | 1.618 (304) | 1.434 (305) | 8.022 × 10⁻¹² |
| Allen L2/3 epilepsy specimen | 40 ms | 1.289 (299) | 1.498 (296) | 1.349 (310) | 6.435 × 10⁻¹² |
| Peng mouse Control | 20 ms | 2.549 (360) | 3.452 (363) | 106.945 (373) | 1.386 × 10⁻⁸ |
| Peng mouse Control | 40 ms | 1.901 (371) | 2.454 (372) | 66.254 (378) | 5.747 × 10⁻⁸ |

The canonical absolute-voltage transient metric is retained in the raw case matrix. Its median candidate/seven ratios remain close to 1 for Jacobs, Tamas and Allen; Peng's combined layout is about 10.36 at 20 ms and 21.39 at 40 ms. The canonical and perturbation-coordinate metrics are algebraically equivalent but can differ numerically when the reduction residual is extremely small. The perturbation-coordinate metric is the more stable comparison for this residual scale; neither metric is silently substituted for the other.

## 5. Basal/apical interaction diagnostic

To check whether the combined change is predictable from the two one-port changes, each matched case is also evaluated with:

\[
M = \frac{E_{both}E_{seven}}{E_{basal}E_{apical}}
\]

Here E is one error metric for the same paired case. M > 1 means the combined error exceeds the multiplicative no-interaction prediction on a log-error scale; M < 1 means it is below that prediction. Values below are medians across the 378 matched cases. The final column is the share of cases in which M > 1.

| Morphology | Window | Discrete-BE median M | BE cases M>1 | Perturbation-transient median M | Transient cases M>1 |
|---|---:|---:|---:|---:|---:|
| Jacobs | 20 ms | 1.002 | 57.4% | 1.222 | 54.0% |
| Jacobs | 40 ms | 1.001 | 51.9% | 1.240 | 51.9% |
| Tamas | 20 ms | 6.815 | 99.7% | 8.847 | 95.2% |
| Tamas | 40 ms | 6.165 | 99.7% | 8.541 | 99.7% |
| Allen | 20 ms | 0.964 | 27.8% | 0.625 | 29.4% |
| Allen | 40 ms | 0.967 | 28.0% | 0.725 | 30.2% |
| Peng | 20 ms | 12.203 | 98.9% | 11.458 | 95.8% |
| Peng | 40 ms | 11.261 | 98.7% | 12.188 | 97.6% |

### Interpretation

1. **The large combined penalty in Tamas and Peng is not explained by either q25 probe alone.** The one-probe transient ratios are about 1.2–2.6, while the combined ratios range from about 25 to 107. The median multiplicative interaction diagnostic is roughly 8.5–12.2, and at least 95% of matched cases exceed the no-interaction prediction in these two morphologies.
2. **Allen behaves differently.** The combined transient ratio is only about 1.35–1.43, and the multiplicative contrast is below 1 in roughly 70% of pairs. This is a descriptive result for this one epilepsy-surgical reconstruction, not a general statement about human neurons.
3. **Jacobs remains comparatively close to neutral.** The periodic BE ratios stay around 1.0. The transient median ratios are slightly above 1 for the two-q25 layout, with an interaction contrast only modestly above 1.
4. The additive contrast E_both − E_basal − E_apical + E_seven is also retained in the post-analysis outputs. Its numerical magnitude is scale-dependent; the multiplicative contrast is useful here for comparing relative residual changes but must not be interpreted as a causal or biological interaction.
5. Continuous-AC, discrete-BE periodic-transfer, canonical transient and perturbation-coordinate transient results are different estimands. In particular, continuous-AC frequency ratios should not be used as a substitute for the finite-window transient result.

## 6. What this does and does not establish

This experiment shows that the effect of adding q25 output ports depends on morphology and that the two q25 changes can interact strongly in the reduced model. It does **not** show that one anatomical port layout is universally superior. Ratios must be read alongside absolute error changes, especially when the seven-port error is near the numerical floor.

The four inputs are individual reconstructions, not a population sample. Peng is a mouse Control cell whose source metadata says No Diameter; Jacobs has moderate dendritic integrity and an incomplete axon; Allen is an epilepsy surgical specimen and not a healthy control; Tamas is one human Control pyramidal comparison cell. The models are passive linear-RC reductions. This does not validate active channels, action potentials, synapses, plasticity or biological physiology. Full Hines remains the canonical reference and no production default is changed.

## 7. Reproducibility files and next steps

The complete 1,075,536-row frequency matrix, all raw metrics, comparison pairs, preflight files, runtime evidence and source SWC needed for the Allen holdout are preserved in [Actions artifact 15010408589](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246/artifacts/15010408589).

The repository now also contains the reusable paired post-analysis:
- research/summarize_prima_q25_four_layout_interactions.py
- tests/test_prima_q25_four_layout_posthoc.py
- .github/workflows/amsn-prima-q25-four-layout-posthoc.yml

Its eight unit tests pass and the script compiles under Python 3.12. The workflow is configured to execute and commit the post-analysis summaries once the primary case-metric and comparison CSVs are committed. The archival rerun excludes the oversized frequency CSV from Git but retains it in the artifact.
