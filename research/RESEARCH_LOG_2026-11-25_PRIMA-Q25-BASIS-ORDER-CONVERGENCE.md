# Research log — PRIMA q25 basis-order convergence 112/168/224

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Canonical workflow:** [45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400)  
**Result commit:** `09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a`  
**Artifact:** [15031057886](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400/artifacts/15031057886)

## 1. Research question

Does the strong morphology-dependent q25 penalty observed in the fixed-order 168 four-layout experiment persist when the state cap is reduced to 112 or increased to 224, while keeping the same input-source, passive-parameter, timestep, window, morphology, and full-Hines comparison protocol?

## 2. Work performed

- Reused the strict accepted order-168 matrix as the reference.
- Computed order 112 and order 224 in separate Python/NEURON child processes to isolate native NEURON/HOC state.
- Recomputed all four layouts for each of four checksum-pinned morphologies.
- Ran paired post-analysis separately for each order using the exact per-order case-metric and comparison hashes.
- Verified exact expected-vs-read-back CSV counts, finite-record DFT identities, basis orthogonality, source checksums and morphology preflight contracts.
- Archived the accepted result set to Git and uploaded the complete runner/results artifact.
- Compared the successful artifact with a second overlapping run's artifact. All numerical and summary CSVs matched bit-for-bit; only report/timing metadata differed.

## 3. Fixed protocol

Four morphology strata: NMO_03524 Jacobs human Control; NMO_107159 Tamas human pyramidal Control comparison; NMO_162186 Allen L2/3 epilepsy-surgery specimen; NMO_163775 Peng mouse Control (metadata says No Diameter).

Four layouts: seven, seven+basal-q25, seven+apical-q25, seven+both-q25. The numerical protocol retains six expansion shifts (0/100/1,000/3,000/6,000/10,000 Hz), nine passive scenarios, three current sources, 10-pA 2/10-ms pulses at 2-ms onset, dt 0.00625 ms, 20/40-ms windows, 0.5-µm NEURON segment cap, 3,201 master frequencies from 0 to 80 kHz at 25-Hz spacing.

Pinned environment: Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2, Haswell OpenBLAS one thread, active NumPy targets X86_V3 and baseline(X86_V2); X86_V4, AVX512_ICL and AVX512_SPR disabled.

## 4. Acceptance evidence

Canonical run 45616046400 completed success, including the long calculation, exact CSV readback, Git archival commit and artifact upload. Result commit 09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a; artifact 15031057886, 134,290,729 bytes, ZIP SHA-256:

`3eb04bf772ef93f90facac5cf4ea7b4f126f37bfbab12dd4acf81b377b79e65e`.

For each order, expected and read-back counts were:
- 3,201 master frequencies
- 1,075,536 frequency-summary rows
- 12,096 case metrics
- 9,072 matched comparisons
- 144 source/layout/window summaries
- 24 morphology/layout/window summaries
- 1,728 finite-DFT identity diagnostics
- 336 interaction, 168 morphology and 1,008 source posthoc summaries

Maximum finite-DFT identity relative residuals: 8.74381e-12 (order112), 8.78149e-12 (order168), and 8.75736e-12 (order224), all below the 2e-8 tolerance. Maximum basis orthogonality error was 1.77636e-15; each order had 144 distinct basis hashes. All four morphology checksum/preflight contracts passed.

Runtime by order: 112 = 1,856.98s; 168 reference = 2,369.84s; 224 = 3,793.09s. Whole sweep wall time 5,652.50s; peak RSS 1,255,776 KiB.

## 5. Main results

Median combined-nine-port/seven-port perturbation-coordinate transient NRMSE ratios, with median absolute error changes in percentage points:

| Morphology | Order | 20 ms | 40 ms |
|---|---:|---:|---:|
| Jacobs | 112 | 4.108 / +5.09e-11 | 3.642 / +5.02e-11 |
| Jacobs | 168 | 1.317 / +2.59e-12 | 1.427 / +3.07e-12 |
| Jacobs | 224 | 0.944 / −3.01e-13 | 0.894 / −8.40e-13 |
| Tamas | 112 | 61.891 / +2.45e-6 | 34.061 / +6.02e-6 |
| Tamas | 168 | 25.268 / +3.31e-9 | 49.840 / +1.31e-8 |
| Tamas | 224 | 1.004 / +4.73e-13 | 1.016 / +2.60e-12 |
| Allen | 112 | 106.530 / +1.87e-7 | 108.449 / +1.82e-7 |
| Allen | 168 | 1.434 / +8.02e-12 | 1.349 / +6.44e-12 |
| Allen | 224 | 1.043 / +6.50e-13 | 1.043 / +5.03e-13 |
| Peng | 112 | 64.988 / +1.39e-5 | 33.805 / +3.52e-5 |
| Peng | 168 | 106.945 / +1.39e-8 | 66.254 / +5.75e-8 |
| Peng | 224 | 1.947 / +8.80e-12 | 3.745 / +4.12e-11 |

This establishes order sensitivity: the Tamas and Allen combined-q25 penalty is nearly eliminated by order224, and Jacobs approaches/slightly improves on the seven-port reference. Peng improves greatly over order168 but retains a relative ratio above 1; its absolute error changes remain extremely small. Its order224 discrete-BE ratios remain larger (about 21.87/24.59), with very small absolute percentage-point changes, reinforcing the need to keep periodic-transfer and finite-window transient metrics separate.

The multiplicative paired interaction diagnostic (M=E_{both}E_{seven}/(E_{basal}E_{apical})) also changes with order. Median M for Peng is 1.76/2.70 at order112, 10.95/12.46 at order168 and 2.02/3.28 at order224. Tamas moves from 1.82/2.33 to 7.71/9.30 and then ~1.005/1.029. Jacobs and Allen are at/below 1 for order224. This is descriptive reduced-model interaction, not causal or biological interaction.

## 6. Reproducibility and duplicate-run reconciliation

A second overlapping workflow [45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005) independently recomputed orders 112 and 224 and uploaded artifact 15031521434. Its numerical calculation and artifact upload succeeded. Its duplicate Git archive step failed during rebase with add/add conflicts in four report/time paths because the canonical successful run 45616046400 had already committed those same files. The duplicate artifact's report/time files contain conflict markers and are not treated as accepted report files.

A local SHA-256 comparison of the two downloaded artifacts found that **25 of the 27 files under results/** were identical. All per-order case metrics, frequency summaries, comparisons, DFT identity CSVs, posthoc CSVs, and summary CSVs were bit-identical. Only the combined report JSON and timing text differed. The clean successful run 45616046400 is the canonical source.

## 7. Scientific interpretation and limits

The results strongly support a fixed-order basis-budget effect for Tamas and Allen, but do not prove that initial seed count is the only mechanism. Later Krylov growth, conditioning, morphology geometry, source weighting, output weighting and time/frequency-window weighting can still contribute. Peng is the important unresolved stratum at order224.

These are four individual passive reconstructions, not a biological population. Allen is an epilepsy-surgery specimen; Peng metadata says No Diameter. The study does not establish active-channel, action-potential, synaptic, plasticity, calcium-signalling or biological validity. Full Hines remains canonical and no production solver/default changed.

## 8. Files and next action

- Detailed results: `amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_BASIS_ORDER_SWEEP_RESULTS_2026-11-25.md`.
- Run-specific manifest: `amsn-core/results/prima_q25_four_morphology_four_layout_basis_order_sweep_2026-11-25_manifest.json`.
- Combined report and all per-order reports/CSVs are stored under `amsn-core/results/`.
- Next: a small output-aware dual-seed pilot, initially focused on Peng, keeping the seven-port input selector fixed and adding sparse q25 dual resolvent vectors only to the state basis. D0 must be bitwise-equivalent to production multishift PRIMA and pass passivity, identity, and shared-output checks before the four-morphology sweep is authorized.
