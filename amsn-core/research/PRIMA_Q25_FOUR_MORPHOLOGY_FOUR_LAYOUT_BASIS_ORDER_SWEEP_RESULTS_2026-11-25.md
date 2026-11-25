# PRIMA q25 four-morphology 7/8/8/9-port basis-order convergence — results

**Date:** 25 November 2026  
**Accepted workflow:** [45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400) — completed **success**  
**Result archive commit:** [09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a](https://github.com/Nolane-x/Nghien-cuu/commit/09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a)  
**Artifact:** [15031057886](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400/artifacts/15031057886) — 134,290,729 bytes  
**Artifact ZIP SHA-256:** `3eb04bf772ef93f90facac5cf4ea7b4f126f37bfbab12dd4acf81b377b79e65e`  
**Combined report:** `amsn-core/results/prima_q25_four_morphology_four_layout_basis_order_sweep_2026-11-25_report.json`

## 1. Executive result

The four-layout PRIMA q25 comparison has now been repeated at basis orders **112, 168 and 224** across four checksum-pinned passive morphologies. All three orders passed the declared computation and validation gates. The order-168 matrix is the already accepted strict-dispatch reference; orders 112 and 224 were recomputed in separate Python/NEURON subprocesses to avoid carrying native NEURON/HOC state across runs.

The main conclusion is not that one order solves every morphology. Instead:

- The very large combined-q25 transient-error ratios seen at order 168 in Tamas and Peng are strongly order-sensitive.
- At order 224, the combined nine-port transient ratio falls to approximately **1.00** for Tamas and **1.04** for Allen, while Jacobs falls slightly below the seven-port reference.
- Peng improves substantially relative to its order-168 result, but still has combined-nine-port transient ratios of **1.95× (20 ms)** and **3.74× (40 ms)**. Its discrete backward-Euler periodic-transfer ratios remain higher, although the absolute percentage-point errors are tiny.
- Therefore, fixed-order seed/basis competition is a plausible and important contributor, but order alone does not fully explain the Peng result. A targeted output-aware basis experiment is justified.

All ratios below are candidate error divided by seven-port error for the same morphology, scenario, source, pulse and shared output. Each morphology/window aggregate contains 378 matched pairs (nine passive scenarios × three source locations × two pulse widths × seven shared outputs). Ratios are always shown with absolute error changes because the seven-port residual can be extremely small.

## 2. Protocol and run provenance

The sweep holds the scientific protocol fixed:
- Four separate reconstructions: NMO_03524 Jacobs human Control; NMO_107159 Tamas human pyramidal Control comparison; NMO_162186 Allen L2/3 epilepsy-surgery specimen; NMO_163775 Peng mouse Control.
- Four retained-port layouts: seven, seven+basal-q25, seven+apical-q25, seven+both-q25.
- Nine passive parameter scenarios; inputs at soma, basal-q75 and apical-q75; 10-pA pulses of 2 and 10 ms beginning at 2 ms.
- Timestep 0.00625 ms; observation windows 20 and 40 ms; 0.5-µm NEURON segment cap.
- Six expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Pinned runtime: Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2; Haswell OpenBLAS one thread; active NumPy dispatch targets X86_V3 and baseline(X86_V2), with X86_V4/AVX512_ICL/AVX512_SPR disabled.

Order 168 was loaded from the strict accepted result matrix at run 45616046681. Orders 112 and 224 were newly calculated as isolated child processes. The run report records 144 unique basis hashes per order. Maximum basis orthogonality error across the models is **1.77636 × 10⁻¹⁵**.

## 3. Numerical acceptance

Each of the three orders passed the same expected-vs-read-back coverage:

| Output per order | Rows / points |
|---|---:|
| Master frequency grid | 3,201 |
| Frequency-summary matrix | 1,075,536 |
| Case metrics | 12,096 |
| Candidate-vs-seven comparisons | 9,072 |
| Source/layout/window summaries | 144 |
| Morphology/layout/window summaries | 24 |
| Finite-record DFT identity diagnostics | 1,728 |
| Posthoc interaction summaries | 336 |
| Posthoc morphology summaries | 168 |
| Posthoc source summaries | 1,008 |

| Basis order | Status | Max finite-DFT identity relative residual | Max orthogonality error | Calculation seconds |
|---:|---|---:|---:|---:|
| 112 | passed | 8.74381 × 10⁻¹² | 1.77636 × 10⁻¹⁵ | 1,856.98 |
| 168 | accepted reference | 8.78149 × 10⁻¹² | 1.77636 × 10⁻¹⁵ | 2,369.84 |
| 224 | passed | 8.75736 × 10⁻¹² | 1.77636 × 10⁻¹⁵ | 3,793.09 |

The maximum finite-DFT identity tolerance is 2 × 10⁻⁸. All four morphology checksum/preflight contracts passed at each freshly computed order. Both order-specific paired post-analysis reports are marked passed and match their input case/comparison CSV hashes.

The overall sweep used 5,652.50 seconds of wall time and peaked at 1,255,776 KiB RSS. The full run uploaded 32 files in artifact 15031057886. The 1,075,536-row frequency tables are retained in the artifact rather than committed as oversized Git blobs.

## 4. Combined nine-port transient error across basis order

The table reports median nine-port/seven-port perturbation-coordinate transient NRMSE ratio, followed by the median absolute error change in percentage points.

| Morphology | Order 112, 20/40 ms | Order 168, 20/40 ms | Order 224, 20/40 ms |
|---|---|---|---|
| Jacobs human Control | 4.108 / +5.09e-11; 3.642 / +5.02e-11 | 1.317 / +2.59e-12; 1.427 / +3.07e-12 | 0.944 / −3.01e-13; 0.894 / −8.40e-13 |
| Tamas human Control | 61.891 / +2.45e-6; 34.061 / +6.02e-6 | 25.268 / +3.31e-9; 49.840 / +1.31e-8 | 1.004 / +4.73e-13; 1.016 / +2.60e-12 |
| Allen L2/3 epilepsy specimen | 106.530 / +1.87e-7; 108.449 / +1.82e-7 | 1.434 / +8.02e-12; 1.349 / +6.44e-12 | 1.043 / +6.50e-13; 1.043 / +5.03e-13 |
| Peng mouse Control | 64.988 / +1.39e-5; 33.805 / +3.52e-5 | 106.945 / +1.39e-8; 66.254 / +5.75e-8 | 1.947 / +8.80e-12; 3.745 / +4.12e-11 |

### Interpretation

**Tamas and Allen:** The combined-q25 penalty seen at order 168 essentially collapses by order 224. Their median transient ratios are close to 1, and the absolute error changes are near the numerical residual scale. This supports the view that much of the apparent order-168 penalty was a fixed-order approximation-budget effect.

**Jacobs:** The ratio also approaches or falls below 1 at order 224. It does not support a universal rule that adding q25 ports worsens the seven shared outputs.

**Peng:** Order 224 reduces the large order-168 transient ratios dramatically, but does not bring the combined layout fully to the seven-port baseline. The remaining ratios (1.95 and 3.74) are paired with very small absolute changes (8.80e-12 and 4.12e-11 percentage points). The relative ratio is therefore a warning signal, not a stand-alone measure of practically large error.

## 5. The four layouts at order 224

Median perturbation-coordinate transient NRMSE ratios (candidate/seven) at order 224:

| Morphology | Window | Basal-only 8-port | Apical-only 8-port | Both q25 9-port |
|---|---:|---:|---:|---:|
| Jacobs | 20 ms | 1.047 | 1.590 | 0.944 |
| Jacobs | 40 ms | 1.164 | 1.785 | 0.894 |
| Tamas | 20 ms | 1.003 | 1.000 | 1.004 |
| Tamas | 40 ms | 1.001 | 0.999 | 1.016 |
| Allen | 20 ms | 1.018 | 1.018 | 1.043 |
| Allen | 40 ms | 1.018 | 1.036 | 1.043 |
| Peng | 20 ms | 1.315 | 0.976 | 1.947 |
| Peng | 40 ms | 1.320 | 1.112 | 3.745 |

This shows that the remaining order-224 Peng effect is mainly associated with the combined layout rather than a uniform penalty from every q25 addition. It is a strong reason to investigate the basis construction and the two-output interaction separately.

An important frequency/transient distinction remains: Peng's order-224 discrete-BE periodic-transfer ratios for the combined layout are about **21.87× (20 ms)** and **24.59× (40 ms)**, even though the finite-window perturbation-transient ratios are much smaller. Their absolute BE error increases are about 7.80e-11 and 8.56e-11 percentage points. Periodic-transfer error and finite-window transient error must therefore continue to be reported as distinct estimands; one cannot substitute for the other.

## 6. Multiplicative interaction across order

The post-analysis defines the descriptive multiplicative contrast

[
M=rac{E_{both}E_{seven}}{E_{basal}E_{apical}},
]

where E is the paired perturbation-coordinate transient error. Values above 1 mean the combined error is larger than the multiplicative no-interaction prediction on a log-error scale. The values below are medians across six source/pulse groups per morphology/window; they are not causal or biological interaction effects.

| Morphology | Order 112, 20/40 ms | Order 168, 20/40 ms | Order 224, 20/40 ms |
|---|---|---|---|
| Jacobs | 1.030 / 0.957 | 1.288 / 1.369 | 0.542 / 0.389 |
| Tamas | 1.820 / 2.333 | 7.712 / 9.296 | 1.005 / 1.029 |
| Allen | 2.689 / 2.753 | 0.343 / 0.394 | 0.969 / 0.952 |
| Peng | 1.759 / 2.699 | 10.950 / 12.458 | 2.022 / 3.283 |

The Tamas interaction contrast is close to neutral by order 224. The Allen and Jacobs contrasts are at or below 1. Peng remains clearly above 1 at order 224, which is consistent with the residual combined-layout penalty. This points toward a morphology-specific basis/port interaction that is not explained by the total order alone.

## 7. Seed-budget hypothesis and what remains unknown

The earlier independent initial-shift seed-budget audit counted independent starting columns before later Krylov growth. Tamas, Allen and Peng have initial ranks 42/48/48/54 for seven/basal-eight/apical-eight/combined-nine ports; Jacobs has 33/39/34/40. At order 112, the combined layout's initial block can consume nearly half the available state cap for the first three morphologies. At order 224, the same starting block consumes a smaller fraction.

This is consistent with fixed-order seed-budget competition, and the order sweep strengthens that explanation for Tamas and Allen. It does not prove that initial seed count is the only mechanism: later Krylov growth, conditioning, geometry, source weighting, output weighting and frequency/window weighting remain possible contributors. Peng's remaining interaction at order 224 is the clearest unresolved case.

## 8. Reproducibility and archival status

The canonical successful run is [45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400):
- All workflow steps passed, including calculation, exact CSV read-back, Git result commit and artifact upload.
- Result commit: `09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a`.
- Artifact 15031057886: 134,290,729 bytes; ZIP SHA-256 `3eb04bf772ef93f90facac5cf4ea7b4f126f37bfbab12dd4acf81b377b79e65e`.

A second overlapping run [45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005) independently recalculated orders 112 and 224. Its numerical sweep and artifact upload succeeded, but its duplicate Git archive step hit an add/add rebase conflict in report/time files because the successful run had already archived the same paths. The two run artifacts contain identical SHA-256 values for all numerical CSV matrices and summary CSVs; only the report/time metadata files differ. The second artifact's combined report/time files contain rebase conflict markers and are not used as the accepted report. The independent CSV agreement is useful reproducibility evidence, but the clean successful run 45616046400 remains the canonical artifact/report source.

## 9. Scientific limits and next experiment

The four inputs are individual morphology reconstructions, not a biological population. Allen NMO_162186 is an epilepsy-surgery specimen, not a healthy control. Peng NMO_163775 source metadata says No Diameter. This remains a passive linear-RC numerical reduction study; it does not validate active channels, action potentials, synapses, plasticity, calcium signalling or biological computation.

The next targeted experiment should focus on Peng:
1. Compare the seven-port primal basis against sparse q25 output-dual seed enrichment while keeping the input selector B fixed at the original seven ports.
2. Keep order fixed initially (224 is the stronger reference for current convergence), and predeclare low/mid/high output-dual shifts.
3. Require exact D0 parity with the existing multishift PRIMA basis, unchanged seven-port input map, congruent G/C projection, positive-definite reduced G/C, orthogonality, full-Hines DFT identity and all seven shared-output metrics.
4. Only if the small pilot improves q25 readouts without materially degrading the seven shared outputs should the method expand across all four morphologies and nine parameter scenarios.

The research-only prototype and its five focused tests are in `experimental_prima_output_aware_basis.py` and `test_prima_q25_output_aware_dual_seed_basis.py`. Its focused CI run [45633147052](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45633147052) passed. The prototype is not yet a validated improvement and is not used by the production solver.

Full Hines remains canonical. No production solver, retained-port default or PRIMA order default has changed.
