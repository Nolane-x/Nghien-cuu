# PRIMA q25 four-morphology finite-window boundary decomposition — results

**Run date:** 25 November 2026  
**GitHub Actions:** [run 45571400424](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45571400424)  
**Results commit:** [14fd51e6ade9d9cae359c9077f55174e3d0347f7](https://github.com/Nolane-x/Nghien-cuu/commit/14fd51e6ade9d9cae359c9077f55174e3d0347f7)  
**Artifact:** `prima-q25-four-morphology-boundary-decomposition` (33,448,650 bytes; 90-day retention at upload)  
**Report JSON:** `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_report.json`

## 1. Acceptance

The four-morphology run completed successfully. Every workflow gate passed:

- Source SHA-256 and morphology record counts checked for all four SWCs.
- The seven shared output node IDs and two q25-only IDs were checked separately per morphology.
- Four-morphology numerical regression and q25 mapping tests passed.
- All four preflight contracts passed.
- Every expected CSV row count was read back and verified.
- The finite-window DFT identity stayed below its declared tolerance.
- Result CSVs and the JSON report were committed; the complete matrix and runtime evidence were uploaded as the GitHub Actions artifact.

Exact coverage:

| Output | Expected | Read back |
|---|---:|---:|
| Master frequency grid | 3,201 points | 3,201 |
| Frequency summary | 537,768 rows | 537,768 |
| Case metrics | 6,048 rows | 6,048 |
| Matched 9-port / 7-port comparisons | 3,024 rows | 3,024 |
| Source/window summaries | 48 rows | 48 |
| Morphology/window summaries | 8 rows | 8 |
| Finite-DFT identity diagnostics | 864 rows | 864 |

Maximum finite-identity relative error was **8.9204 × 10⁻¹²**, against a tolerance of **2 × 10⁻⁸**. The maximum absolute identity residual was **4.7998 × 10⁻¹¹ V-samples**. The largest full-Hines / reduced-model identity residual was similarly below tolerance. Across 72 reduced basis builds, all 72 basis hashes were distinct and maximum basis orthogonality error was **2.4425 × 10⁻¹⁵**.

## 2. Experimental design

The experiment compares two layouts with the same seven retained output nodes:

- **Seven-port:** the canonical seven shared SWC nodes.
- **Nine-port:** exactly those same seven nodes plus basal-q25 and apical-q25.

The nine-port model therefore adds only the two q25 probes; it does not replace or move the seven shared outputs. Each morphology has its own pinned IDs and source checksum.

All runs use PRIMA basis order **168**, the same six expansion shifts through 10 kHz, nine passive parameter scenarios, three current sources (soma, basal-q75 and apical-q75), two 10-pA pulse widths (2 and 10 ms), onset 2 ms, timestep **0.00625 ms**, and observation windows **20 and 40 ms**. The common NEURON segment cap is **0.5 µm**.

The finite-record analysis keeps the terminal-state term:

```
Y = H_BE U - L (G + (1-exp(-jΩ)) C/dt)^(-1) (C/dt) x[N-1]
```

It therefore distinguishes the periodic/circular transfer component from the terminal-boundary contribution in the actual finite record. It does not treat the transfer-only term as the complete finite-record response.

## 3. Morphology-level results

The following values are medians aggregated over the six source/pulse groups (three sources × two pulse widths) for each morphology/window. Ratios are **nine-port error divided by seven-port error**; values above 1 mean the nine-port metric is larger.

| Morphology | Window | Continuous AC ratio | Discrete BE ratio | Canonical transient ratio | Perturbation-coordinate transient ratio | Worse pairs / 63* |
|---|---:|---:|---:|---:|---:|---:|
| Jacobs human Control | 20 ms | 4.073 | 1.002 | 0.9999 | 0.9657 | 28 |
| Jacobs human Control | 40 ms | 4.094 | 1.004 | 0.9999 | 0.9819 | 28.5 |
| Tamas human Control | 20 ms | 13.263 | 32.169 | 0.9963 | 25.692 | 63 |
| Tamas human Control | 40 ms | 13.499 | 27.824 | 1.0001 | 49.921 | 63 |
| Allen human epilepsy specimen | 20 ms | 2.577 | 2.560 | 1.0002 | 4.502 | 54 |
| Allen human epilepsy specimen | 40 ms | 2.577 | 2.191 | 1.0001 | 3.409 | 54 |
| Peng mouse Control | 20 ms | 37.212 | 38.668 | 17.432 | 135.135 | 63 |
| Peng mouse Control | 40 ms | 31.153 | 32.866 | 27.046 | 59.814 | 63 |

* The final column is the median number of worse perturbation-coordinate transient pairs out of 63 matched scenario/output pairs, computed across the six source/pulse groups. A value of 28.5 is a median across groups, not half a pair in one experiment.

### What this supports

1. **The q25 effect is morphology-dependent.** Jacobs is approximately neutral or slightly better for the perturbation-coordinate transient metric. Allen shows a moderate increase. Tamas and Peng show much larger increases in that metric. A universal claim that adding q25 always helps or always harms is not supported.
2. **The frequency-domain and finite-transient conclusions are not interchangeable.** For example, Jacobs has a continuous-AC ratio around 4.1 while its discrete-BE and transient ratios are close to 1. This is exactly why the finite-window boundary correction is retained.
3. **The canonical and perturbation-coordinate transient metrics must both remain visible.** The canonical absolute-voltage replay first propagates voltages near the leak reversal and then subtracts the leak value. The perturbation replay starts directly at zero in y=V−E_leak coordinates and avoids subtracting two larger floating-point values to recover a small perturbation. The two full-Hines traces are algebraically equivalent, but their maximum relative numerical difference reached **9.61 × 10⁻⁷ %** for the Tamas specimen. That is small relative to the full response but can be material when the model-reduction residual itself is extremely small. The perturbation-coordinate metric is the more numerically stable dynamic comparison here; the canonical metric is retained for continuity with prior work.
4. **Ratios are not absolute biological errors.** A large nine/seven ratio can arise when the seven-port denominator is exceptionally small. The raw per-case metrics and the full 3,024-row matched comparison are retained rather than inferring absolute quality from the ratio alone.
5. **The periodic and terminal components interact.** The decomposition records their norms and cross-term separately. Summary values are marginal medians across groups, so the displayed medians should not be algebraically added to reconstruct one particular comparison.

## 4. Source strata and limits

| NeuroMorpho ID | Stratum | SWC SHA-256 | Important source limitation |
|---|---|---|---|
| [NMO_163775](https://neuromorpho.org/neuron_info.jsp?neuron_name=18453_5766_x31719_y6139-semi_r) | Mouse, Peng archive, Control; somatosensory neocortex L2–3 | `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f` | Dendrites and axon marked complete; NeuroMorpho metadata says **No Diameter**, so the standardized radii must not be described as measured biological diameters. |
| [NMO_107159](https://neuromorpho.org/neuron_info.jsp?neuron_name=Fig5c_141009_2og_B) | Human, Tamas archive, female pyramidal Control comparison cell | `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023` | Dendrites and axon marked complete; diameter metadata available. It is one reconstruction, not a population. |
| [NMO_03524](https://neuromorpho.org/neuron_info.jsp?neuron_name=1-5-3) | Human, Jacobs archive, pyramidal Control; occipital neocortex BA18 | `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748` | Dendritic integrity is moderate and axon is incomplete. |
| [NMO_162186](https://neuromorpho.org/neuron_info.jsp?neuron_name=770307286_transformed) | Human, Allen Cell Types L2–3; epilepsy surgical specimen | `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc` | Dendrites marked complete and axon incomplete. It is **not** a healthy-control specimen. |

These are four individual reconstructions, not four biological populations. The common 0.5-µm mesh cap aligns one discretization limit; it does not make their tissue conditions, species, sources, or reconstructions interchangeable. The study remains a passive linear-RC numerical reduction experiment. It does not validate active ion channels, action potentials, synapses, plasticity, calcium signaling, or biological physiology. Full Hines remains the canonical reference, and no production solver or default was changed.

## 5. Reproducibility and files

The report and machine-readable outputs are committed under:

- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_report.json`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_morphology_window_summary.csv`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_source_window_summary.csv`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_nine_seven_comparisons.csv`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_case_metrics.csv`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_finite_dft_identity.csv`
- `results/prima_q25_four_morphology_boundary_decomposition_2026-11-25_frequency_summary.csv`

The frequency-summary CSV is about 97.9 MB and the case-metrics CSV about 3.2 MB; retrieve the full matrix from the artifact linked in the Actions run rather than relying on the GitHub file preview.

## 6. Four-layout follow-up — completed

The requested decomposition of the combined q25 change is now complete. The 7 / 8-basal / 8-apical / 9-both experiment and its paired interaction analysis are documented in:

- [Four-morphology four-layout results](PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_RESULTS_2026-11-25.md)
- [Pinned four-layout protocol and node identities](PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_PROTOCOL_2026-11-25.md)
- [Primary Actions calculation and full artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246)

The completed matrix contains 12,096 case-metric rows, 9,072 matched candidate-vs-seven pairs, 1,728 finite-DFT identity diagnostics and 1,075,536 frequency-summary rows. The maximum finite-DFT identity relative error is 8.78149 × 10⁻¹², below the 2 × 10⁻⁸ tolerance. The full 190.12-MB frequency matrix is preserved in the Actions artifact because GitHub rejects individual Git blobs above 100 MB.

The most important descriptive result is morphology dependence: the combined q25 layout has a much larger transient-error ratio in Tamas and Peng than either one-probe layout alone, while Jacobs remains close to neutral and Allen is moderate. Paired multiplicative interaction diagnostics show strong non-additivity for Tamas and Peng. This is a numerical reduced-model observation, not a biological interaction claim. The [post-analysis module](summarize_prima_q25_four_layout_interactions.py) companion script is in the research directory and its eight focused regression tests pass.

## 7. Next discriminating experiment

Before recommending a port layout, test whether the observed q25 interaction is stable across PRIMA basis order. The present four-layout experiment fixes order 168; because the basis is regenerated for each retained-port set, a strong effect could be sensitive to approximation order as well as probe placement.

The next study is now implemented as a **basis-order convergence sweep** for all four layouts on the same four pinned morphologies, using the existing order-168 matrix plus fresh order-112 and order-224 runs. It retains the existing expansion shifts, sources, passive scenarios and finite-window decomposition. The [sweep driver](run_prima_q25_four_layout_basis_order_convergence.py), [tests](../tests/test_prima_q25_four_layout_basis_order_convergence.py) and [Actions workflow](../../../.github/workflows/amsn-prima-q25-basis-order-convergence.yml) are committed. A further order-280 run is reserved for the case where order 224 has not stabilized. Report:
- convergence of absolute discrete-BE and perturbation-coordinate transient errors against the full-Hines reference;
- whether basal-only, apical-only and combined interaction contrasts persist or collapse as order increases;
- basis rank, orthogonality, conditioning and unique subspace hashes by morphology/layout/order;
- periodic-transfer and terminal-boundary terms separately, including their cross-term;
- runtime and peak memory, so the highest useful order is selected empirically.

Keep the four morphologies as separate strata and preserve the current caveats about individual reconstructions and passive linear-RC scope.
