# Human passive PRIMA shift/order Pareto sweep — validated results

**Date:** 2026-11-22 (Asia/Bangkok)  
**Pull request:** [#7 — Study PRIMA basis reuse, shift-band and order trade-offs](https://github.com/Nolane-x/Nghien-cuu/pull/7)  
**GitHub Actions:** [Run 45002816664 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45002816664)

## Executive result

The three-morphology sweep completed with **3/3 GitHub Actions jobs successful**. Each job passed the complete AMSN test suite. The raw artifacts were downloaded and SHA-256 verified against GitHub's artifact metadata.

Validated coverage:
- **243 model records:** 3 morphologies × 9 candidates × 9 passive-parameter scenarios.
- **2,187 AC records:** 243 model/scenario combinations × 9 frequencies.
- **10,206 transient-port records:** 243 × 3 source locations × 2 pulse widths × 7 retained outputs.
- All 243 reduced models achieved their exact requested PRIMA order (56, 84 or 112).
- All 243 reduced conductance and capacitance matrices passed Cholesky positive-definiteness checks.
- Exact frequency and transient coverage passed; recorded errors and timings were finite and non-negative.

The result is a multi-objective trade-off, not one universal winner. The strongest high-frequency candidate is **order112_extended_10khz**. Compared with order 112 using only 3 kHz shifts, it lowers median 10 kHz impedance error by about **41.7×** and admittance error by about **44.8×**, while median transient per-port NRMSE is only about **1.4% higher** and worst transient error is effectively unchanged. This is a compelling high-fidelity passive research candidate, at a higher state/memory cost.

## Candidate design

The sweep crosses three achieved basis orders with three positive-real shift distributions:

| Strategy | Expansion shifts (Hz) |
|---|---|
| narrow_3khz | 0, 100, 1,000, 3,000 |
| extended_10khz | 0, 100, 1,000, 3,000, 6,000, 10,000 |
| balanced_10khz | 0, 10, 100, 1,000, 3,000, 10,000 |

Each shift set was tested at order 56, 84 and 112. The same nine passive-parameter scenarios were repeated for every candidate: nominal; Rm ±20%; Cm ±20%; Ra ±20%; all three parameters -20%; and all three +20%.

Three human morphology fixtures were used:
- NMO_68174 cell1125 — 12,399 electrical compartments.
- NMO_68175 cell1204 — 13,747 electrical compartments.
- NMO_290988 / 1094_Mohan_etal_2015 — 8,893 electrical compartments. This is a partial dendritic reconstruction without an axon; it is not a healthy-control morphology.

Frequency-domain impedance Z and admittance Y were compared against the matching full Hines cable tree at 0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz. Transient tests used 10 pA square-current pulses at soma, basal-q75 and apical-q75; pulse widths were 2 ms and 10 ms, onset 2 ms, total duration 20 ms and dt 0.1 ms. All seven retained outputs were recorded by SWC node ID.

## Candidate-level summary

All error fields are relative L2/NRMSE percentages. AC medians and maxima summarize the 81 morphology/parameter combinations for each candidate at the stated frequency. Transient median, P90 and maximum summarize 1,134 paired per-port traces per candidate.

| Order | Shift strategy | Median Z at 10 kHz | Median Y at 10 kHz | Median transient NRMSE | P90 transient | Worst transient |
|---:|---|---:|---:|---:|---:|---:|
| 56 | narrow 3 kHz | 0.28737% | 0.38757% | 0.00002688% | 0.0003611% | 0.008743% |
| 56 | extended 10 kHz | 0.08121% | 0.12141% | 0.00010970% | 0.0013347% | 0.026977% |
| 56 | balanced 10 kHz | 0.37645% | 0.53053% | 0.00006218% | 0.0005728% | 0.014052% |
| 84 | narrow 3 kHz | 0.006487% | 0.015528% | 0.00000009731% | 0.0000006588% | 0.00001155% |
| 84 | extended 10 kHz | 0.0002071% | 0.0003496% | 0.000002039% | 0.00003201% | 0.0010217% |
| 84 | balanced 10 kHz | 0.002411% | 0.005497% | 0.0000002012% | 0.000001572% | 0.00006720% |
| 112 | narrow 3 kHz | 0.0001951% | 0.0006225% | 0.00000007208% | 0.0000005131% | 0.000003450% |
| 112 | extended 10 kHz | **0.000004681%** | **0.00001390%** | 0.00000007307% | 0.0000005175% | **0.000003450%** |
| 112 | balanced 10 kHz | 0.0001940% | 0.0005859% | **0.00000007213%** | **0.0000005131%** | 0.000003450% |

### Order-dependent shift effects

**Order 56:** extending to 10 kHz improves median 10 kHz Z/Y residuals by 3.54× / 3.19× compared with narrow shifts, but raises median transient error by 4.08× and worst transient error by 3.09×. At this low order, the high-band gain costs a meaningful transient-accuracy loss.

**Order 84:** the extended set reduces median 10 kHz Z/Y residuals by 31.3× / 44.4× versus narrow 3 kHz, but raises median transient NRMSE by about 21× and worst transient error by about 88×. The balanced set is an intermediate compromise, but it is not best for every frequency or transient metric.

**Order 112:** the extended set obtains the lowest AC residuals across the tested 3/6/10 kHz points. Against the narrow set, median 10 kHz residuals fall by about 41.7× for Z and 44.8× for Y. Its transient median and P90 are only 1.38% and 0.86% higher, respectively; the worst transient error is essentially identical (3.4498314e-6% versus 3.4498365e-6%). This indicates that the extra basis capacity largely absorbs the high-frequency shift allocation without the substantial transient penalty seen at orders 56 and 84.

The balanced shift allocation did not become a general winner. It can improve parts of the low-/mid-frequency range for some orders, but at 10 kHz it is worse than the extended set and does not dominate the narrow set on transient error.

## Pareto frontier

The analysis minimizes 19 separate objectives: median and worst-case Z/Y residuals at 3, 6 and 10 kHz; transient median, P90 and maximum NRMSE; median basis-build time; median reduced-transient runtime; median numeric storage; and retained basis order.

**All 9 candidates remain non-dominated** under this full objective set. This is not a failed ranking: each candidate retains at least one advantage, such as lower state count/storage or better accuracy in a particular response domain. No weighted composite score was invented to hide those trade-offs.

Practical reading:
- **High-fidelity passive candidate:** order112_extended_10khz. It gives the strongest 3–10 kHz AC accuracy and almost matches order112_narrow_3khz transient error, at the largest storage footprint.
- **Transient-/resource-oriented candidate:** order84_narrow_3khz. It has low transient errors and lower numeric storage than order112, but its high-band residual is materially larger.
- **Smallest candidate:** order56_narrow_3khz. It has the lowest numeric storage, but the highest transient and high-frequency residuals of the narrow-shift family.

These are opt-in research candidates for different use cases, not production defaults.

## Computational cost and compression

Median candidate-specific costs across 27 morphology/parameter builds:

| Basis order | Median basis-build time | Median reduced numeric storage | Median reduced transient runtime |
|---:|---:|---:|---:|
| 56 | about 1.02 s | 5.35 MB | 0.0074 s |
| 84 | about 1.57 s | 8.05 MB | 0.0122 s |
| 112 | about 2.14 s | 10.79 MB | 0.0263 s |

Numeric storage is the measured dense basis plus reduced conductance/capacitance matrices; it does **not** include Python object overhead, sparse solver workspace or total process memory.

State reduction ranges across the three morphology fixtures:
- Order 56: 99.370–99.593%.
- Order 84: 99.055–99.389%.
- Order 112: 98.741–99.185%.

The complete job-level resource measurements include basis construction, full-reference calculations, frequency sweeps and all transient protocols. They are not isolated solver microbenchmarks:

| Morphology | Full sweep wall time | User CPU time | Peak process RSS |
|---|---:|---:|---:|
| NMO_290988_Mohan2015 | 265.24 s | 359.48 s | 221.89 MB |
| NMO_68174_cell1125 | 360.98 s | 768.41 s | 319.54 MB |
| NMO_68175_cell1204 | 397.01 s | 810.79 s | 321.88 MB |

Peak RSS is morphology/job-level, not per-candidate. User CPU can exceed wall time because it sums CPU time across threads. Runner hardware is not pinned, so these wall/CPU values are not a precise cross-host performance ranking.

## Scientific interpretation and next steps

1. **Order matters at least as much as shift distribution.** Moving from order 56 to 112 reduces transient errors by several orders of magnitude. At order112, the extended shift set buys large high-frequency gains with negligible transient degradation.
2. **The balanced shift hypothesis is not a universal win.** Some low-/mid-frequency points improve, but 10 kHz Z/Y is worse than the extended strategy at the same order.
3. **Keep Hines canonical and production defaults unchanged.** The order112_extended_10khz candidate is the strongest high-fidelity passive option in this tested matrix, but still needs a held-out morphology and later active/nonlinear validation before broader claims.
4. **Next:** add at least one held-out human morphology with traceable source/usage rights, then repeat the leading order84_narrow_3khz and order112_extended_10khz candidates. After that, test a broader passive-parameter grid and only then begin a separate active-channel study.

## Reproducibility and provenance

- Actions run: [45002816664](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45002816664), 3/3 success.
- Each artifact contains model, frequency and transient CSVs plus its process-resource profile and run log.
- Artifact IDs, byte sizes, SHA-256 digests and expiry timestamps are committed in the artifact manifest under amsn-core/results.
- GitHub listed the artifacts as retained until 2027-02-20 08:26:22 UTC at validation time.
- Reproduction/validation program: amsn-core/research/analyze_human_prima_shift_order_pareto.py.
- Summary tables under amsn-core/results are recomputed from exact model/scenario/frequency/source/pulse/SWC-node coverage, without fitting any parameters to NEURON.

## Scope limits

These remain passive linear RC reduction experiments. Cholesky positive-definiteness checks are not a substitute for response validation and do not prove all biological passivity properties. No active Na/K/Ca channels, action-potential propagation, nonlinear AMPA/NMDA/GABA synapses, plasticity, calcium signaling, gene expression, metabolism or cognition are represented. The three morphology fixtures do not constitute a representative human-neuron population; NMO_290988_Mohan2015 is a partial dendritic reconstruction without an axon. Parameter changes are deterministic stress cases, not biological confidence intervals.
