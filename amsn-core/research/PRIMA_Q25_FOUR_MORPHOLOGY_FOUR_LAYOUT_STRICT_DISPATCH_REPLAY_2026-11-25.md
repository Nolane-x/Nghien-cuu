# PRIMA q25 four-morphology 7/8/8/9-port strict-dispatch replay

**Date:** 25 November 2026  
**Workflow:** [45616046681](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681) — completed success  
**Result archive commit:** [2326ea077c3c6821ba427aef9b009b655e052cfe](https://github.com/Nolane-x/Nghien-cuu/commit/2326ea077c3c6821ba427aef9b009b655e052cfe)  
**Artifact:** [15027292605](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681/artifacts/15027292605), 70,254,593 bytes, SHA-256 `4171ef306c4e53a4f5ec0637883c33243d0f36294c80ff093753ec070ca0c8ab`  
**Machine-readable report:** `amsn-core/results/prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25_report.json`

## 1. Purpose and acceptance

This is a strict runtime/CPU-dispatch replay of the four-layout order-168 matrix. It is not a new biological experiment and it does not change the numerical model or production defaults. The previous matrix already existed; this run verifies that the complete calculation, result checks, archival commit and artifact upload succeed under the pinned runtime/dispatch controls.

The workflow finished with all steps successful:
- Python/NumPy/OpenBLAS runtime and active-dispatch verification.
- Four checksum-pinned morphology imports and q25-node preflight contracts.
- Focused four-layout and finite-window regression tests.
- Full four-morphology 7/8/8/9-port calculation.
- Exact expected-vs-read-back CSV row counts and finite-record identity gate.
- Compact result commit and full evidence artifact upload.

The numerical report status is `prima_q25_four_morphology_four_layout_boundary_ablation_passed`; the post-analysis report status is `passed`.

## 2. Fixed numerical protocol

- Four separate NeuroMorpho reconstructions: NMO_03524 Jacobs human Control; NMO_107159 Tamas human pyramidal Control comparison; NMO_162186 Allen L2/3 epilepsy-surgery specimen; NMO_163775 Peng mouse Control (source metadata says No Diameter).
- Four retained-port layouts: seven shared ports; seven plus basal-q25; seven plus apical-q25; seven plus both q25 ports.
- All comparisons preserve the same seven shared output node IDs within each morphology. The q25 node IDs and SWC SHA-256 checksums are recorded in the machine-readable report.
- PRIMA order 168; six expansion shifts; nine passive parameter scenarios; three current sources (soma, basal-q75, apical-q75); 10-pA rectangular pulses of 2 and 10 ms at 2-ms onset; timestep 0.00625 ms; observation windows 20 and 40 ms; 0.5-µm NEURON segment cap.
- Master frequency grid: 0–80 kHz at 25-Hz spacing (3,201 points).

## 3. Runtime and numerical acceptance

| Item | Verified value |
|---|---:|
| Python | 3.12.16 |
| NumPy | 2.5.5 |
| SciPy | 1.16.3 |
| NEURON | 9.0.2 |
| OpenBLAS | Haswell, one thread |
| Active NumPy dispatch targets | X86_V3; baseline(X86_V2) |
| Wall time | 2,510.29 s |
| Peak RSS | 1,233,904 KiB |
| Maximum finite-DFT identity relative residual | 8.781488969255743e-12 |
| Acceptance tolerance | 2e-8 |
| Maximum model identity relative residual | 8.743810650683813e-12 |
| Maximum finite identity absolute residual | 4.809833427024806e-11 V-samples |

Exact row counts were checked after re-reading each CSV:

| Output | Expected and read back |
|---|---:|
| Master frequency points | 3,201 |
| Frequency summary | 1,075,536 |
| Case metrics | 12,096 |
| Candidate-vs-seven comparisons | 9,072 |
| Source/layout/window summaries | 144 |
| Morphology/layout/window summaries | 24 |
| Finite-DFT identity diagnostics | 1,728 |

The 199,352,753-byte frequency-summary CSV is kept in the Actions artifact rather than committed as a Git blob. The artifact contains 23 files and the complete runner/source evidence.

## 4. Cross-run reproducibility check

The current report was compared with the archived report at repository commit `27c3e6668a34c4ea97de4cde5412602d896fb0dc`.

- All **144/144** basis-model records matched across runs for morphology, layout, parameter scenario, basis SHA-256, projected-conductance SHA-256, projected-capacitance SHA-256 and input SHA-256.
- Each run contains 144 distinct basis hashes.
- Five tracked numerical CSVs have identical Git blob SHA-1 values across the two revisions: case metrics, candidate-vs-seven comparisons, morphology/layout/window summary, source/layout/window summary and finite-DFT identity diagnostics.
- The report diff records changed runner CPU-feature availability and wall-clock metadata; it does not record a changed numerical basis or matrix in those comparisons.

This supports repeatability of the archived order-168 matrices across the two observed runner CPU-feature maps. It does not prove bitwise reproducibility on every CPU, BLAS implementation, operating system or future dependency version. The current run's strict preflight records the active NumPy dispatch targets and one-thread Haswell OpenBLAS configuration.

## 5. Four-layout response summary

The table gives median candidate/seven error ratios across the **378 matched cases per morphology/window** (9 parameter scenarios × 3 current sources × 2 pulse widths × 7 shared outputs). Each cell is **discrete backward-Euler periodic-transfer ratio / perturbation-coordinate transient NRMSE ratio**. A value greater than 1 means the candidate's error is larger than the seven-port reference. These are numerical approximation ratios, not biological error rates.

| Morphology | Window | Basal-only 8-port | Apical-only 8-port | Both q25 9-port |
|---|---:|---:|---:|---:|
| Jacobs human Control | 20 ms | 1.000 / 0.975 | 1.000 / 1.363 | 1.001 / 1.317 |
| Jacobs human Control | 40 ms | 1.004 / 1.035 | 1.002 / 1.373 | 1.002 / 1.427 |
| Tamas human Control | 20 ms | 2.123 / 1.370 | 1.999 / 1.213 | 32.267 / 25.268 |
| Tamas human Control | 40 ms | 2.232 / 2.571 | 1.983 / 2.323 | 28.033 / 49.840 |
| Allen L2/3 epilepsy specimen | 20 ms | 1.046 / 1.380 | 1.200 / 1.618 | 1.131 / 1.434 |
| Allen L2/3 epilepsy specimen | 40 ms | 1.046 / 1.289 | 1.218 / 1.498 | 1.157 / 1.349 |
| Peng mouse Control | 20 ms | 1.690 / 2.549 | 2.160 / 3.452 | 42.412 / 106.945 |
| Peng mouse Control | 40 ms | 1.687 / 1.901 | 1.972 / 2.454 | 32.576 / 66.254 |

The canonical absolute-voltage transient metric is also retained. It is close to 1 for Jacobs, Tamas and Allen; Peng's combined 9-port ratio is about 15.62 at 20 ms and 28.49 at 40 ms. The perturbation-coordinate metric is the numerically stable transient comparison at this small residual scale. Neither metric is silently substituted for the other.

### Interpretation supported by this matrix

1. **The combined two-q25 layout is strongly morphology-dependent.** The largest effect is in Tamas and Peng, where the two-port combination produces far larger errors than either single-q25 layout. Jacobs is close to the seven-port baseline; Allen is intermediate and the combined layout is not worse than each one-port layout by the same degree.
2. **The combined effect is non-additive in the reduction experiment.** The paired post-analysis defines the multiplicative contrast as (M=E_{both}E_{seven}/(E_{basal}E_{apical})), with a separate additive contrast (E_{both}-E_{basal}-E_{apical}+E_{seven}). It reports 336 interaction-summary rows, 168 morphology summaries and 1,008 source summaries covering 3,024 matched case keys. For Tamas and Peng, the combined-layout perturbation error is far above either single-port error; the detailed per-source/per-pulse contrasts are in the posthoc CSVs.
3. **The source location matters.** For Allen, basal-q75 stimulation gives a combined-layout perturbation ratio near 1.02–1.05, while apical-q75 and soma stimulation are several times higher. Tamas and Peng show large combined-layout ratios across all three source positions.
4. **A fixed-order basis-budget mechanism is plausible but not yet causal proof.** The retained-port input selector changes the multishift PRIMA starting block and its subsequent Krylov growth while all layouts share order 168. The results are consistent with competition for a fixed reduced-state budget, but geometry, frequency/window weighting and basis order remain possible contributors.

### Read ratios with absolute deltas

A very small seven-port residual can make candidate/seven ratios large. The post-analysis therefore retains absolute error deltas, p90 ratios and worse/better/tied pair counts. For the combined layout, median absolute perturbation-NRMSE changes (in percentage points) are approximately:
- Jacobs: (2.59	imes10^{-12}) (20 ms), (3.07	imes10^{-12}) (40 ms).
- Tamas: (3.31	imes10^{-9}) (20 ms), (1.31	imes10^{-8}) (40 ms).
- Allen: (8.02	imes10^{-12}) (20 ms), (6.44	imes10^{-12}) (40 ms).
- Peng: (1.39	imes10^{-8}) (20 ms), (5.75	imes10^{-8}) (40 ms).

## 6. Limits and decisions

These are four individual reconstructions, not four biological populations. Allen NMO_162186 is an epilepsy-surgery specimen, not a healthy control. Peng NMO_163775 metadata says No Diameter; its standardized radii must not be represented as measured biological diameters. This remains a passive linear-RC numerical reduction experiment. It does not validate active channels, action potentials, synapses, plasticity, calcium signaling or biological physiology.

Full Hines remains the canonical reference. This replay changes no production solver, retained-port default, PRIMA order default or biological parameter. Do not generalize a port layout as universally better from these four specimens.

## 7. Next discriminating work

- Finish the isolated 112/168/224 basis-order sweep. Determine whether the Tamas/Peng combined-q25 penalty shrinks as order increases, and retain basis rank, conditioning, orthogonality, hashes, both transient metrics and runtime/peak RSS.
- Finish the q25 output-observer study. Require exact primary/observer dispatch equality and all 144 primary basis/G/C/input hash matches before accepting observer-only results.
- Keep each morphology as a separate stratum. If the order effect persists, test source/probe weighting and frequency/window weighting rather than promoting a production default.
