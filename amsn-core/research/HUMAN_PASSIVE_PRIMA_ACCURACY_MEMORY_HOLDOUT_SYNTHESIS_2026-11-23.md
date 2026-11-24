# PRIMA accuracy–memory–holdout synthesis

**Date:** 23 November 2026  
**Repository:** `Nolane-x/Nghien-cuu`  
**Scope:** passive linear-RC neuron reduction only  
**Status:** evidence synthesis across validated PRs #4–#16; no production default changed

## Executive conclusion

There is no single PRIMA configuration that is best for every port set, output location, frequency band, transient protocol and resource budget. The current evidence supports three *conditional* choices:

1. **Seven-port, order 112, extended 10 kHz shifts** is the strongest high-frequency passive candidate in the seven-output shift/order sweep. It retains very low transient error and is supported by four independent morphology holdouts across different source contexts, including two complete-axon holdouts run at the same 0.5 µm reference mesh; one has explicit Diameter/3D metadata.
2. **Nine-port order must be selected per morphology** when basal-q25 and apical-q25 outputs are required. NMO_162186 needed order168 to restore shared-output parity; NMO_03524 was already at parity at order112; NMO_163775 showed high relative 9/7 ratios at both orders but very small absolute errors; NMO_107159 showed a 42.72× order112 median ratio and near parity at order168.
3. **Seven-port order84 with extended10kHz shifts** is a useful accuracy/storage compromise on NMO_03524; order56 remains the lowest-footprint option on that morphology. The separate process-RSS benchmark still shows increasing peak RSS with order, but its absolute values come from a different nine-port audit.

**Full Hines remains the canonical reference.** Existing production order defaults remain unchanged. Matched 7-port/9-port tests on NMO_162186, NMO_03524, NMO_163775 and NMO_107159 show that the incremental numerical cost of adding q25 ports is morphology-dependent; there is no universal order threshold for nine-port models.

## Evidence map

| Evidence axis | Source experiment | Validated coverage | Main result |
|---|---|---|---|
| Shift/order and protocol robustness | PR #7, run 45002816664 | 3 morphologies × 9 candidates × 9 passive-parameter scenarios; 243 models, 2,187 AC rows, 10,206 transient-port rows | All candidates pass passivity checks; order112 extended10kHz leads high-frequency accuracy |
| Independent morphology holdout | PR #8, run 45012282648 | NMO_162186; 81 model rows, 729 AC rows, 3,402 transient-port rows | Order112 extended10kHz maintains very low high-frequency residuals on one held-out morphology |
| Equal-order port-count test | PR #6, run 44987393352 | 3 morphologies × 2 mesh caps × 7/9 ports × orders 56/112/168; 3,072 sweep rows | Port count and order must be selected together; nine-port order168 restores shared-output parity and resolves q25 |
| Matched port-count × independent holdout | PR #13, run 45184621520 | NMO_162186; 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations | Confirms order-dependent result: nine-port order112 regresses shared outputs; order168 restores parity |
| Independent Control-condition morphology holdout | PR #14, run 45196546471 | NMO_03524 Jacobs; 81 models, 729 AC rows, 3,402 transient rows | Independently supports extended10kHz shift family; order84 extended10kHz is strong accuracy/storage compromise |
| Matched 7/9-port Control holdout | PR #15, run 45198630080 | NMO_03524; 36 models, 756 shared pairs, 216 q25 observations, 378 Hines checks | Nine-port order112 and168 both preserve shared-output parity on this morphology; q25 errors <3.1e−8% |
| Matched 7/9-port complete-axon holdout | PR #16, run 45311916600 | NMO_163775 Peng mouse Control; 36 models, 756 shared pairs, 216 q25 observations, 378 exact Hines checks | High relative ratios but absolute nine-port shared NRMSE <2.0e−4%; No Diameter metadata |
| Matched 7/9-port measured-diameter human pyramidal holdout | PR #17, run 45314100588 | NMO_107159 Tamas human Control; 36 models, 756 shared pairs, 216 q25 observations, 378 exact Hines checks | Order112 median ratio42.72×; order168 near parity1.001×; complete arbors, Diameter/3D/Angles metadata |
| Nine-port high-order capacity | merged PR #4, run 44979673244 | 3 morphologies × 2 mesh caps; orders 28/56/84/112/168; 2,520 rows | Higher capacity sharply reduces apical-q90 transient error |
| Runtime and peak RSS | PR #5, run 44989658844 | 36 measurements: 3 morphologies × 2 mesh caps × orders 84/112/168 × 2 repetitions; 37/37 jobs pass | Peak RSS increases consistently with order; timing is confounded by heterogeneous GitHub CPUs |

The experiments are related but not interchangeable. In particular, the PR #7 seven-output shift/order matrix, PR #6 equal-order port comparison, PR #5 nine-port resource audit and PR #8 held-out morphology matrix use different port/candidate sets. Their results are combined here as complementary evidence, not as though every metric came from one factorial experiment.

## 1. Seven-port shift/order: best high-frequency passive candidate

PR #7 evaluated three positive-real shift distributions:

- `narrow_3khz`: 0, 100, 1,000 and 3,000 Hz
- `extended_10khz`: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz
- `balanced_10khz`: 0, 10, 100, 1,000, 3,000 and 10,000 Hz

Each was tested at orders 56, 84 and 112 on three morphology fixtures, with nine deterministic passive-parameter scenarios per morphology. All 243 reduced models achieved the requested rank and passed Cholesky positive-definiteness checks. All nine candidates remained non-dominated across 19 objectives; no weighted score was used to manufacture one universal winner.

### Order 112 comparison

| Metric | Narrow 3 kHz | Extended 10 kHz |
|---|---:|---:|
| Median impedance residual at 10 kHz | 0.0001951% | **0.000004681%** |
| Median admittance residual at 10 kHz | 0.0006225% | **0.00001390%** |
| Median transient per-port NRMSE | 7.208e−8% | 7.307e−8% |
| P90 transient per-port NRMSE | 5.131e−7% | 5.175e−7% |
| Worst transient per-port NRMSE | 3.44984e−6% | 3.44983e−6% |
| Median numeric storage | 10.79 MB | 10.79 MB |

At order 112, extending the shift band lowers the median 10 kHz impedance/admittance residual by approximately **41.7× / 44.8×** versus the narrow set. Median transient NRMSE is only about 1.38% higher; the worst transient error is effectively unchanged. This makes `order112_extended_10khz` a strong high-frequency passive research candidate.

The same shift does not behave as well at every order. At order 56, extended shifts materially increase transient error. At order 84, the extended set improves high-frequency residuals but raises transient error relative to narrow shifts. Shift strategy and basis order must be selected together.

## 2. Independent morphology holdout

PR #8 tested nine candidates (orders 56/84/112 × the three shift strategies) on NMO_162186 / Allen Cell Types `770307286_transformed`, a human L2–3 specimen from right middle temporal gyrus.

The source is a **single epilepsy surgical specimen**. NeuroMorpho marks dendrites complete and axon incomplete. It is an external dendritic morphology holdout, not a healthy control, a complete axon-to-dendrite neuron, or a representative population.

The source SWC was checksum-pinned (SHA-256 `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`). The holdout workflow passed 2/2 jobs; all 81 models achieved their requested orders and passed reduced G/C Cholesky checks.

### Holdout results at order 112

| Metric | Narrow 3 kHz | Extended 10 kHz |
|---|---:|---:|
| Median Z residual at 10 kHz | 0.000139586% | **0.00000463044%** |
| Maximum Z residual at 10 kHz | 0.000428595% | **0.00000692168%** |
| Median Y residual at 10 kHz | 0.000310408% | **0.00000947438%** |
| Maximum Y residual at 10 kHz | 0.000672920% | **0.0000150405%** |
| Median transient per-port NRMSE | 8.723e−9% | 8.727e−9% |
| Maximum transient per-port NRMSE | 1.45426e−7% | 1.45425e−7% |
| Median numeric storage | 6.72 MB | 6.72 MB |

On this epilepsy holdout, order112 extended reduces median high-frequency Z/Y residual by **30.15× / 38.39×** compared with order112 narrow while preserving essentially the same transient metrics. This is positive external-morphology evidence, but it is one epilepsy specimen and does not establish population-level generalization. A second, distinct Jacobs Control-condition morphology is summarized in Section 8.

## 3. Seven ports versus nine ports: order is inseparable from port count

PR #6 compared seven-port and nine-port reductions at equal achieved orders 56, 112 and 168 on three morphologies and two mesh caps. The nine-port variant adds basal-q25 and apical-q25 observations.

### Shared outputs

| Equal basis order | Matched shared-output pairs | Nine-port regressions | Median nine/seven error ratio |
|---:|---:|---:|---:|
| 56 | 252 | 252/252 | 131.329× |
| 112 | 252 | 252/252 | 3.326× |
| 168 | 252 | 148/252 tiny relative regressions; 104 improvements | 1.00000062× |

At order 112, the nine-port error ratios are affected by very small seven-port denominators. The absolute maximum single-output NRMSE is still only 0.00003447% for nine ports versus 0.00000345% for seven ports. At order 168, the two models are effectively indistinguishable on the seven shared outputs.

This conclusion is now independently reproduced on NMO_162186 by PR #13 (run 45184621520), with a matched 7-port/9-port comparison at orders 112 and 168 using the same six extended10kHz shifts and nine passive-parameter scenarios. At order112 the nine-port model was worse on 377/378 shared-output pairs (median 9/7 transient-error ratio 8.162×). At order168 it was effectively at parity: 190 pairs improved, 187 regressed and one tied; median ratio 0.99999985×. The maximum ratio at order168 was 1.00144×.

### Additional q25 outputs

| Order | q25 observations | Median NRMSE | Maximum NRMSE |
|---:|---:|---:|---:|
| 56 | 72 | 0.00972849% | 0.14042521% |
| 112 | 72 | 2.19864e−7% | 0.0000123083% |
| 168 | 72 | 9.78181e−8% | **0.00000097486%** |

Order 168 is the first tested equal-order point at which the nine-port expansion preserves near-parity on shared outputs while representing the two additional q25 outputs accurately. Against the seven-port order-84 reference, nine-port order112 and order168 improve all 36 matched apical-q90 cases; however, this comparison is not the same as comparing seven and nine ports at equal order.

On the independent NMO_162186 holdout (PR #13), the nine-port q25 outputs also remained accurate: order112 median/maximum NRMSE 8.3418e−8% / 3.6711e−6%; order168 8.6262e−9% / 8.6226e−8%. The 378 shared Hines-reference checks on this holdout were exact (zero voltage difference), confirming that the shared reference traces are identical between port layouts.

**Decision:** choose the port count and order using a matched morphology-specific test. NMO_162186 showed that nine-port order112 degrades shared outputs and order168 restores parity; NMO_03524 showed that nine-port order112 is already at parity and both q25 outputs are accurate. Do not impose a universal order168 threshold from one morphology.

## 4. Runtime and peak memory

PR #5 measured the full nine-port passive audit process at orders 84, 112 and 168. The 36-job matrix passed 37/37 jobs and validated all artifact hashes.

| Candidate order | Median wall time | Median user CPU | Median peak RSS |
|---:|---:|---:|---:|
| 84 | 101.61 s | 122.00 s | **267.90 MB** |
| 112 | 129.11 s | 273.78 s | 276.15 MB |
| 168 | 124.83 s | 266.60 s | 301.73 MB |

All 12 matched peak-RSS comparisons were positive at each order increase:

| Comparison | Median paired RSS increase | Positive pairs |
|---|---:|---:|
| 112 vs 84 | +6.24 MB | 12/12 |
| 168 vs 84 | +23.48 MB | 12/12 |
| 168 vs 112 | +18.32 MB | 12/12 |

The memory trend is consistent within this experiment. Timing is **not** a controlled ranking: jobs ran across seven AMD EPYC/Intel Xeon CPU models, and the measured command includes model setup, full reference calculations and the complete sweep, not only the reduced solver kernel. Do not conclude that order168 is faster than order112 from these medians.

This is a separate nine-port resource experiment. Its RSS measurements should be used as order-level guidance, not presented as a direct memory measurement of the seven-port `order112_extended_10khz` candidate.

## 5. Conditional design recommendation

| Use case | Research candidate | Evidence-based reason | Limitation |
|---|---|---|---|
| High-frequency accuracy on the seven retained outputs | **7-port, order112, extended10kHz** | Best 3–10 kHz residuals in PR #7; extended10kHz also leads on both NMO_162186 and NMO_03524 | Passive RC only; holdout morphologies are individual specimens |
| Lower-memory passive compromise | **7-port, order84, extended10kHz** | On NMO_03524, median 10 kHz Z/Y residuals 5.58e−7% / 2.88e−7% at 0.660 MB numeric storage | Validated on the smaller Jacobs Control morphology; re-evaluate on additional morphologies |
| Lowest footprint | **Order56** (choose shift set by frequency/transient needs) | 0.416 MB numeric storage on NMO_03524; narrow3kHz preserves very small transient errors | Accept higher high-frequency AC residuals |
| Need basal-q25 and apical-q25 outputs | **9-port, morphology-tested order112 or168; select by absolute tolerance** | NMO_162186 needed order168; NMO_03524 was near parity at both; NMO_163775 has high relative ratios but small absolute errors; NMO_107159 returned to parity at order168 | No universal threshold; four individual morphologies with different reconstruction metadata |
| Canonical reference | **Full Hines** | Remains the unreduced reference against which all passive candidates are measured | More states and resource cost; not being replaced |

This table is a research selection guide, not a production-default change. All passive models remain candidates for specific protocols and output sets.

## 6. Unresolved validation gates

1. **Harmonize reference resolution across all four morphologies.** NMO_162186 and NMO_03524 were evaluated at 0.125 µm; NMO_163775 and NMO_107159 used 0.5 µm. Run a mesh-convergence subset at common caps (for example 0.125 and 0.5 µm where tractable) before comparing absolute errors across all four.
2. **Expand population coverage.** Four independent reconstructions are now represented, but each is still a single cell. Add a fifth morphology from another source study/region and preferably another cell class, while preserving explicit geometry and source metadata.
3. **Control performance timing.** Re-run order84/112/168 and the exact seven-port order112-extended candidate on fixed hardware or a controlled self-hosted runner with repeated isolated kernel timings. Hosted runner CPU heterogeneity prevents a clean wall-time ranking.
4. **Test active/nonlinear biology separately.** These results validate passive linear-RC reduction only. They do not validate action potentials, active dendritic ion channels, nonlinear synapses, calcium, plasticity, metabolism or cognition.
5. **Retain uncertainty and negative results.** The ±20% Rm/Cm/Ra scenarios are deterministic stress tests, not fitted biological distributions. A hierarchical or subject-level uncertainty treatment is needed when biological measurements are introduced.

## Source experiments and audit links

- [PR #4 — nine-port high-order capacity](https://github.com/Nolane-x/Nghien-cuu/pull/4); [workflow 44979673244](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244); [validated report on main](https://github.com/Nolane-x/Nghien-cuu/blob/main/amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md).
- [PR #5 — resource benchmark](https://github.com/Nolane-x/Nghien-cuu/pull/5); [workflow 44989658844](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44989658844); [resource report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-high-order-resource-benchmark/amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md).
- [PR #6 — equal-order seven-vs-nine-port](https://github.com/Nolane-x/Nghien-cuu/pull/6); [workflow 44987393352](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44987393352); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-equal-order-seven-vs-nine-ports-2026-11-22/amsn-core/research/HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_PORT_COUNT_2026-11-22.md).
- [PR #7 — shift/order Pareto](https://github.com/Nolane-x/Nghien-cuu/pull/7); [workflow 45002816664](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45002816664); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-basis-transfer-protocol-robustness-2026-11-22/amsn-core/research/HUMAN_PRIMA_SHIFT_ORDER_PARETO_2026-11-22.md).
- [PR #8 — held-out morphology](https://github.com/Nolane-x/Nghien-cuu/pull/8); [workflow 45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/allen-human-morphology-heldout-preflight-2026-11-22/amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md).
- [PR #13 — NMO_162186 matched 7/9 ports](https://github.com/Nolane-x/Nghien-cuu/pull/13); [workflow 45184621520](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520).
- [PR #14 — NMO_03524 Control shift/order holdout](https://github.com/Nolane-x/Nghien-cuu/pull/14); [workflow 45196546471](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471).
- [PR #15 — NMO_03524 matched 7/9 ports](https://github.com/Nolane-x/Nghien-cuu/pull/15); [workflow 45198630080](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198630080).

## Final guardrails

- Full Hines remains canonical.
- No production order default, port count, or runtime behavior is changed in this synthesis.
- A lower Hines-relative residual is not the same as lower discrepancy to native NEURON; both comparisons must remain separate.
- Resource results are specific to the complete audit process and mixed GitHub runner hardware.
- Passive linear-RC validation must not be described as active-neuron or biological validation.


## 7. Matched port-count validation on the independent NMO_162186 holdout

PR #13 / GitHub Actions run 45184621520 completed the previously missing cross-check. The same NMO_162186 morphology (7,287 SWC records; 7,278 electrical compartments), seven canonical output nodes, passive parameter scenarios, square-pulse protocol and six extended10kHz shifts were used for both port layouts. The nine-port layout added only basal-q25 and apical-q25.

The replay passed all validation steps and archived 36 model rows, 324 AC rows, 1,728 transient-port rows, 756 shared-output pairs, 216 q25-only observations and 378 exact Hines consistency checks. All 36 reduced matrices passed Cholesky checks.

| Matched holdout metric | Order112 | Order168 |
|---|---:|---:|
| Shared pairs | 378 | 378 |
| Nine-port worse / better / tie | 377 / 1 / 0 | 187 / 190 / 1 |
| Median 9/7 transient-error ratio | **8.1620×** | **0.99999985×** |
| Maximum 9/7 ratio | 395.2606× | 1.00144× |
| Maximum 9-port shared transient NRMSE | 1.0655e−5% | 1.4543e−7% |
| q25 median NRMSE | 8.3418e−8% | 8.6262e−9% |
| q25 maximum NRMSE | 3.6711e−6% | **8.6226e−8%** |

The result confirms that adding the two q25 outputs at order112 systematically degrades the seven shared outputs, even though q25 itself is represented accurately. At order168, shared-output parity is recovered while q25 remains accurate. All 378 paired full-Hines traces on the shared nodes were exactly equal, with maximum absolute voltage difference 0 V.

For high-frequency AC at 10 kHz on this holdout, median Z/Y residuals were 4.6124e−6% / 9.5816e−6% (7-port order112), 1.0498e−4% / 2.5063e−4% (9-port order112), 2.7305e−10% / 7.2223e−10% (7-port order168), and 3.3864e−8% / 9.8754e−8% (9-port order168).

The model-array numeric storage (basis plus reduced G/C matrices) was 6.4104 MB at order112 and 9.7592 MB at order168 for both port counts in this implementation. This is not whole-process RSS. The entire run took 422.61 s wall time, used 518.23 s CPU and peaked at 187,160 KiB RSS; this one end-to-end measurement is not a per-candidate resource benchmark.

**Updated decision:** use 7-port order112 extended10kHz when the original seven outputs are sufficient and high-frequency accuracy is the objective. When q25 outputs are required, run the matched 7/9-port comparison on the target morphology: NMO_162186 needed order168 for parity, whereas NMO_03524 was already at parity at order112. Order84 extended10kHz remains a good accuracy/storage compromise on NMO_03524, and order84 is also the lower-memory region in the separate resource benchmark. Full Hines remains canonical; no production default is changed.

Source: [PR #13](https://github.com/Nolane-x/Nghien-cuu/pull/13), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520), [artifact #14824270534](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520/artifacts/14824270534).


## 8. Second independent morphology: NMO_03524 Jacobs Control context

PR #14 / workflow 45196546471 adds a distinct Control-condition human pyramidal morphology from the Jacobs archive (NeuroMorpho NMO_03524 / 1-5-3), a 23-year-old male occipital BA18 reconstruction. NeuroMorpho metadata describes dendrites as moderate and the axon incomplete. This is one cell, not a population sample.

The pinned SWC (31,199 bytes; SHA-256 `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`) contains 869 records, 862 AMSN electrical compartments, 68 NEURON sections and 35,248 NEURON segments at a maximum 0.125 µm segment length. Seven PRIMA ports were identified. A terminal basal-q90 probe at x=1.0 uses a logged nearest-endpoint-segment readout rather than extrapolating past the segment-centre interval.

The CI passed 146/146 repository tests and the full morphology preflight. It evaluated all nine seven-port candidates (orders 56/84/112 × three shift distributions) across nine passive parameter scenarios, yielding 81 model rows, 729 AC rows and 3,402 transient rows. Every candidate achieved its requested order and passed Cholesky checks.

### High-frequency candidate summary on NMO_03524

| Candidate | Median Z at 10 kHz | Median Y at 10 kHz | Median transient NRMSE | Numeric storage |
|---|---:|---:|---:|---:|
| Order56 narrow3kHz | 0.0085692% | 0.0054551% | 3.5394e−9% | 0.4161 MB |
| Order56 extended10kHz | 0.0011971% | 0.00024464% | 9.0554e−9% | 0.4161 MB |
| Order84 extended10kHz | 5.5775e−7% | 2.8753e−7% | 3.2709e−9% | 0.6601 MB |
| Order112 extended10kHz | **3.6005e−10%** | **1.8143e−10%** | 3.2708e−9% | 0.9280 MB |

Order112 extended10kHz is the highest-precision candidate. Order84 extended10kHz is a strong accuracy/storage compromise, using about 29% less numeric storage than order112 while keeping 10 kHz residuals extremely small. Order56 is the lowest-footprint option, but its shift choice materially affects high-frequency AC accuracy. On this Control morphology, extended10kHz gives the best high-frequency residuals at each tested order.

This provides independent support for the extended10kHz shift family in a distinct human morphology and Control metadata context. The two morphology datasets differ in size and reconstruction context and must not be pooled as one factorial experiment.

**Port-count follow-up:** PR #15 has now run the matched seven-port/nine-port order112/order168 comparison on NMO_03524. It found near-parity already at order112 and q25 maximum NRMSE below 3.1e−8% at both orders; see Section 9.

Source: [PR #14](https://github.com/Nolane-x/Nghien-cuu/pull/14), [validated CI run](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471), [artifact #14827204708](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471/artifacts/14827204708).


## 9. Second matched port-count morphology: NMO_03524 Jacobs Control

PR #15 / [workflow 45198630080](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198630080) completed the second matched port-count holdout. It used the NMO_03524 Jacobs Control morphology (869 SWC records; SHA-256 `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`), seven shared SWC nodes, and two q25-only nodes: basal 272 and apical 864.

The run passed the full AMSN regression suite, source checksum, Import3D preflight, matched replay, idempotent result archive and artifact upload. It produced 36 model rows, 324 AC rows, 1,728 transient-port rows, 756 shared pairs, 216 q25-only observations and 378 shared-Hines checks. All models achieved the requested order and passed Cholesky checks; all 378 common Hines reference traces were exactly equal.

Artifact #14829912332; ZIP SHA-256 `cba24b3c36c24b125339feefbb3a10d0f105adf9cda2c80030a5577e80350b03`.

### Shared-output parity

| Basis order | 9-port worse / better / tie | Median 9/7 transient-error ratio | Maximum ratio |
|---:|---:|---:|---:|
| 112 | 204 / 173 / 1 | **1.00000465×** | 1.00614× |
| 168 | 189 / 189 / 0 | **0.99999991×** | 1.00721× |

On NMO_03524, nine-port order112 is already at near-parity on the seven shared outputs. At order168 the layouts are also at parity.

### q25 accuracy

| Basis order | q25 observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 3.7497e−9% | 3.0585e−8% |
| 168 | 108 | 3.7498e−9% | 3.0586e−8% |

The two q25 output probes are accurate at both tested orders.

### Cross-morphology comparison

| Morphology | Experimental context | Order112 median 9/7 error ratio | Order168 median 9/7 error ratio | Practical finding |
|---|---|---:|---:|---|
| NMO_162186 | Epilepsy surgical specimen; axon incomplete | **8.162×** | 0.99999985× | Order168 needed to restore shared-output parity when adding q25 ports |
| NMO_03524 | Jacobs Control-condition Golgi cell; dendrites moderate, axon incomplete | **1.00000465×** | 0.99999991× | Order112 already preserves parity while adding q25 outputs |

The incremental cost of adding q25 ports is therefore **morphology-dependent**. On NMO_162186, nine-port order112 caused a strong regression; on NMO_03524, order112 was effectively at parity. A new morphology should receive a matched seven-port/nine-port order comparison before fixing its order. The two tested morphologies are individual cells with incomplete axons or other structural limits; they do not support a population-wide rule.

Source: [PR #15](https://github.com/Nolane-x/Nghien-cuu/pull/15), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198630080), [artifact #14829912332](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198630080/artifacts/14829912332).


## 10. Third matched port-count morphology: NMO_163775 Peng complete-axon record

PR #16 / [successful workflow run 45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600) adds the third independent matched 7-port/9-port morphology. The specimen is NeuroMorpho NMO_163775 from the Peng archive: mouse, Cux2-CreERT2;Ai166, 56 days, Control condition, somatosensory neocortex layer 2–3, pyramidal IT projection. NeuroMorpho marks dendrites and axon complete. **Its morphological attributes are No Diameter**; standardized SWC radii are not documented measured biological diameters.

The repository source contains 4,209 records (3 soma, 3,602 axon, 306 basal, 298 apical), with one root, all nodes connected and no duplicate IDs/missing parents. SHA-256: \`94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f\`.

### Preflight and exact port identities

Import3D/AMSN preflight passed with 4,200 electrical compartments, 251 NEURON sections and 82,587 NEURON segments. Maximum observed segment length was 0.49999436 µm under a 0.5 µm cap. Seven shared SWC IDs:
\`1, 40, 144, 3926, 3948, 4104, 4180\`.

The nine-port layout adds only:
- basal-q25: SWC node 224
- apical-q25: SWC node 4096

The 7/9-port matched experiment generated 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations and 378 shared-Hines checks. All 36 models achieved their requested order and passed Cholesky checks. The 378 common Hines reference traces were exactly equal: 0 V difference and 0% relative L2 error.

### Shared-output parity and absolute errors

| Basis order | 9-port worse / better / tie | Median 9/7 transient-error ratio | Maximum ratio | Maximum absolute 9-port shared NRMSE |
|---:|---:|---:|---:|---:|
| 112 | 378 / 0 / 0 | **78.051×** | 6,739.21× | 0.0001933% |
| 168 | 347 / 31 / 0 | **14.501×** | 300.22× | 6.0657e−7% |

The 9/7 ratios are very large, but the seven-port baseline itself has extremely small error. For this reason, the ratio must not be interpreted alone: the maximum absolute nine-port shared-output NRMSE is still below 2.0e−4% at order112 and 6.1e−7% at order168. No application tolerance was assumed.

### q25-only accuracy

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 1.8480e−5% | 2.1588e−4% |
| 168 | 108 | 1.5567e−8% | 4.2824e−7% |

Both added q25 outputs are numerically close to their full-Hines references, especially at order168.

### High-frequency residuals and storage

At 10 kHz, nine-port median Z/Y residuals are 3.2464e−5% / 4.8096e−5% at order112, and 6.8670e−9% / 4.8906e−8% at order168. Numeric basis+G/C storage is 3.7803 MB at order112 and 5.8140 MB at order168, identical for seven and nine ports at the same order.

Runtime on the hosted runner: 187.50 s wall, 273.21 s user CPU, peak RSS 160,272 KiB (Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2). This is a single hosted-run measurement, not a controlled performance benchmark.

### Updated cross-morphology conclusion

| Morphology | Context / structural caveat | Order112 median 9/7 ratio | Order168 median 9/7 ratio | Interpretation |
|---|---|---:|---:|---|
| NMO_162186 | Human epilepsy specimen; axon incomplete | 8.162× | 0.99999985× | Order168 restored shared-output parity |
| NMO_03524 | Human Jacobs Control; dendrites moderate, axon incomplete | 1.00000465× | 0.99999991× | Already at parity at order112 |
| NMO_163775 | Mouse Peng Control; arbors complete by metadata; No Diameter | 78.051× | 14.501× | Relative 9-port penalty persists, although absolute errors remain small |

The third holdout strengthens the conclusion that q25 port cost is **morphology-dependent**, not a universal order rule. The choice between seven and nine ports should use both absolute error against a stated application tolerance and the relative change on matched shared outputs. On NMO_163775, the 9/7 ratio is high, but the absolute nine-port errors are still small in this passive protocol.

The Peng experiment uses a 0.5 µm NEURON mesh cap, while both human matched holdouts used 0.125 µm. Do not pool absolute error or timing values across these runs as if mesh and radius metadata were identical. NeuroMorpho explicitly lists No Diameter for NMO_163775, so its standardized SWC radii must not be treated as biological diameter measurements. This is one mouse specimen and passive linear-RC numerical validation only.

Sources: [PR #16](https://github.com/Nolane-x/Nghien-cuu/pull/16), [validated run 45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600), [artifact #14883752560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600/artifacts/14883752560).


## 11. Fourth matched port-count morphology: NMO_107159 Tamas human pyramidal comparison cell

PR #17 / [successful workflow run 45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588) adds the fourth independent matched 7-port/9-port morphology. The record is NeuroMorpho NMO_107159 from the Tamas archive: human female, frontal neocortex, layers 1 and 2–3, principal pyramidal cell, Control condition, in vitro biocytin, 70 µm slice. NeuroMorpho marks Dendrites & Axon Complete and Diameter, 3D, Angles. Age is not reported.

The source article is the human cortical rosehip-cell study, but this specific cell (\`Fig5c_141009_2og_B\`) is the **pyramidal comparison cell in Fig. 5C**, not a rosehip interneuron. The published article DOI is 10.1038/s41593-018-0205-2 (PMID 30150662).

Pinned standardized SWC SHA-256:
\`6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023\`.

The source contains 7,228 records (soma3, axon4,030, basal1,767, apical1,428), one three-point soma root, all nodes connected, no duplicate IDs or missing parents.

### Preflight and port identities

Import3D/AMSN preflight passed with 7,222 electrical compartments, 127 NEURON sections and 24,737 NEURON segments. Maximum observed segment length was 0.49997753 µm under the 0.5 µm cap.

Seven shared SWC nodes:
\`1, 6363, 4735, 5564, 7023, 4301, 4623\`.

Two q25-only probes:
- Basal q25: node 6609
- Apical q25: node 4404

### Exact replay coverage and Hines consistency

Run 45314100588 passed all tests, source checksum, Import3D, matched replay, result archive and artifact upload. Artifact [#14884183988](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588/artifacts/14884183988), ZIP SHA-256 \`b01bbce48bc62931c10b78f5a97a8e334f26bd0ea186ede6335a92484b8d3808\`.

Coverage: 36 models, 324 AC rows, 1,728 transient-port rows, 756 matched shared-output pairs, 216 q25 observations and 378 shared-Hines checks. All 36 models achieved requested order and passed Cholesky checks. All 378 common Hines traces were exactly equal: 0 V maximum absolute difference and 0% relative L2 difference.

### Shared-output comparison

| Basis order | 9-port worse / better / tie | Median 9/7 error ratio | Maximum ratio | Maximum absolute 9-port shared NRMSE |
|---:|---:|---:|---:|---:|
| 112 | 378 / 0 / 0 | **42.718×** | 140.029× | 3.9507e−5% |
| 168 | 214 / 164 / 0 | **1.00102×** | 4.373× | 5.4559e−7% |

At order112, the nine-port layout is worse on all 378 shared pairs, relative to a very accurate seven-port baseline. At order168, the layouts are near parity: 214 pairs worse and 164 better, with median ratio 1.00102×. The maximum absolute nine-port shared-output NRMSE is 3.95e−5% at order112 and 5.46e−7% at order168.

### q25-only accuracy

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 3.0201e−6% | 3.5323e−5% |
| 168 | 108 | 2.4896e−8% | 2.3679e−7% |

The two added q25 outputs are accurately represented at either order; order168 reduces the maximum q25 error by about 149×.

### High-frequency residuals, storage and runtime

At 10 kHz, nine-port median Z/Y residuals are 1.7339e−5% / 1.8783e−4% at order112, and 2.8131e−9% / 2.9439e−7% at order168. Numeric basis+G/C storage is 6.3625 MB at order112 and 9.6874 MB at order168, equal across port counts at the same order.

Runtime: 322.00 s wall, 408.14 s user CPU, 144,420 KiB peak RSS (Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2). This is a single hosted-run measurement, not a controlled benchmark.

### Updated conclusion across four morphologies

| Morphology | Context / structural caveat | Order112 median 9/7 ratio | Order168 median 9/7 ratio | Interpretation |
|---|---|---:|---:|---|
| NMO_162186 | Human epilepsy surgical specimen; axon incomplete | 8.162× | 0.99999985× | Order168 restored shared-output parity |
| NMO_03524 | Human Jacobs Control; dendrites moderate, axon incomplete | 1.00000465× | 0.99999991× | Near parity at both orders |
| NMO_163775 | Mouse Peng Control; arbors complete by metadata; No Diameter | 78.051× | 14.501× | Relative 9-port penalty persists; absolute errors are still very small |
| NMO_107159 | Human Tamas Control pyramidal comparison; complete arbors and Diameter/3D/Angles | **42.718×** | **1.00102×** | Order168 restores near parity; q25 max error 2.37e−7% |

This fourth holdout is especially useful because it combines complete arbors with explicit diameter metadata. It again supports morphology-dependent port-count cost: order112 incurs a relative penalty, while order168 returns the shared outputs to near parity. The absolute nine-port shared-output error is small at both orders, so application decisions should use a predeclared absolute tolerance alongside the relative 9/7 ratio.

The Tamas and Peng runs use the same 0.5 µm mesh cap, so their two complete-axon holdouts share the same reference discretization. The first two human holdouts used 0.125 µm; their absolute errors and runtimes must not be directly pooled with the 0.5 µm pair without mesh harmonization.

Sources: [PR #17](https://github.com/Nolane-x/Nghien-cuu/pull/17), [successful workflow 45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588), [artifact #14884183988](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588/artifacts/14884183988).
