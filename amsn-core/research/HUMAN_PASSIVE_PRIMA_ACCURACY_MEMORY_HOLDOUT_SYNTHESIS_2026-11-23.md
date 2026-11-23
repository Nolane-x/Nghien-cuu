# PRIMA accuracy–memory–holdout synthesis

**Date:** 23 November 2026  
**Repository:** \`Nolane-x/Nghien-cuu\`  
**Scope:** passive linear-RC neuron reduction only  
**Status:** evidence synthesis across validated PRs #4–#8; no production default changed

## Executive conclusion

There is no single PRIMA configuration that is best for every port set, output location, frequency band, transient protocol and resource budget. The current evidence supports three *conditional* choices:

1. **Seven-port, order 112, extended 10 kHz shifts** is the strongest high-frequency passive candidate in the seven-output shift/order sweep. It retains very low transient error and reproduced its advantage on one independent held-out morphology.
2. **Nine-port, order 168** is the defensible choice when basal-q25 and apical-q25 outputs are specifically required. It is the first tested equal-order point where the two additional outputs are accurate while the seven shared outputs remain effectively at parity with the seven-port model.
3. **Order 84** is the lower-memory point among the resource-benchmarked nine-port candidates. It remains a useful constrained alternative, but its accuracy depends on shift placement and the target outputs.

**Full Hines remains the canonical reference.** Existing production order defaults remain unchanged. Orders 112 and 168 remain opt-in research configurations.

## Evidence map

| Evidence axis | Source experiment | Validated coverage | Main result |
|---|---|---|---|
| Shift/order and protocol robustness | PR #7, run 45002816664 | 3 morphologies × 9 candidates × 9 passive-parameter scenarios; 243 models, 2,187 AC rows, 10,206 transient-port rows | All candidates pass passivity checks; order112 extended10kHz leads high-frequency accuracy |
| Independent morphology holdout | PR #8, run 45012282648 | NMO_162186; 81 model rows, 729 AC rows, 3,402 transient-port rows | Order112 extended10kHz maintains very low high-frequency residuals on one held-out morphology |
| Equal-order port-count test | PR #6, run 44987393352 | 3 morphologies × 2 mesh caps × 7/9 ports × orders 56/112/168; 3,072 sweep rows | Port count and order must be selected together; nine-port order168 restores shared-output parity and resolves q25 |
| Nine-port high-order capacity | merged PR #4, run 44979673244 | 3 morphologies × 2 mesh caps; orders 28/56/84/112/168; 2,520 rows | Higher capacity sharply reduces apical-q90 transient error |
| Runtime and peak RSS | PR #5, run 44989658844 | 36 measurements: 3 morphologies × 2 mesh caps × orders 84/112/168 × 2 repetitions; 37/37 jobs pass | Peak RSS increases consistently with order; timing is confounded by heterogeneous GitHub CPUs |

The experiments are related but not interchangeable. In particular, the PR #7 seven-output shift/order matrix, PR #6 equal-order port comparison, PR #5 nine-port resource audit and PR #8 held-out morphology matrix use different port/candidate sets. Their results are combined here as complementary evidence, not as though every metric came from one factorial experiment.

## 1. Seven-port shift/order: best high-frequency passive candidate

PR #7 evaluated three positive-real shift distributions:

- \`narrow_3khz\`: 0, 100, 1,000 and 3,000 Hz
- \`extended_10khz\`: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz
- \`balanced_10khz\`: 0, 10, 100, 1,000, 3,000 and 10,000 Hz

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

At order 112, extending the shift band lowers the median 10 kHz impedance/admittance residual by approximately **41.7× / 44.8×** versus the narrow set. Median transient NRMSE is only about 1.38% higher; the worst transient error is effectively unchanged. This makes \`order112_extended_10khz\` a strong high-frequency passive research candidate.

The same shift does not behave as well at every order. At order 56, extended shifts materially increase transient error. At order 84, the extended set improves high-frequency residuals but raises transient error relative to narrow shifts. Shift strategy and basis order must be selected together.

## 2. Independent morphology holdout

PR #8 tested nine candidates (orders 56/84/112 × the three shift strategies) on NMO_162186 / Allen Cell Types \`770307286_transformed\`, a human L2–3 specimen from right middle temporal gyrus.

The source is a **single epilepsy surgical specimen**. NeuroMorpho marks dendrites complete and axon incomplete. It is an external dendritic morphology holdout, not a healthy control, a complete axon-to-dendrite neuron, or a representative population.

The source SWC was checksum-pinned (SHA-256 \`a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc\`). The holdout workflow passed 2/2 jobs; all 81 models achieved their requested orders and passed reduced G/C Cholesky checks.

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

On this one holdout, order112 extended reduces median high-frequency Z/Y residual by **30.15× / 38.39×** compared with order112 narrow while preserving essentially the same transient metrics. This is positive external-morphology evidence, but it is still one morphology from one disease-affected specimen. It does not establish population-level generalization.

## 3. Seven ports versus nine ports: order is inseparable from port count

PR #6 compared seven-port and nine-port reductions at equal achieved orders 56, 112 and 168 on three morphologies and two mesh caps. The nine-port variant adds basal-q25 and apical-q25 observations.

### Shared outputs

| Equal basis order | Matched shared-output pairs | Nine-port regressions | Median nine/seven error ratio |
|---:|---:|---:|---:|
| 56 | 252 | 252/252 | 131.329× |
| 112 | 252 | 252/252 | 3.326× |
| 168 | 252 | 148/252 tiny relative regressions; 104 improvements | 1.00000062× |

At order 112, the nine-port error ratios are affected by very small seven-port denominators. The absolute maximum single-output NRMSE is still only 0.00003447% for nine ports versus 0.00000345% for seven ports. At order 168, the two models are effectively indistinguishable on the seven shared outputs.

### Additional q25 outputs

| Order | q25 observations | Median NRMSE | Maximum NRMSE |
|---:|---:|---:|---:|
| 56 | 72 | 0.00972849% | 0.14042521% |
| 112 | 72 | 2.19864e−7% | 0.0000123083% |
| 168 | 72 | 9.78181e−8% | **0.00000097486%** |

Order 168 is the first tested equal-order point at which the nine-port expansion preserves near-parity on shared outputs while representing the two additional q25 outputs accurately. Against the seven-port order-84 reference, nine-port order112 and order168 improve all 36 matched apical-q90 cases; however, this comparison is not the same as comparing seven and nine ports at equal order.

**Decision:** do not select nine ports at order 56 or 112 merely because more outputs are retained. Use nine-port order168 only when q25 outputs are required and the added memory/capacity is justified. Otherwise retain the seven-port reference.

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

This is a separate nine-port resource experiment. Its RSS measurements should be used as order-level guidance, not presented as a direct memory measurement of the seven-port \`order112_extended_10khz\` candidate.

## 5. Conditional design recommendation

| Use case | Research candidate | Evidence-based reason | Limitation |
|---|---|---|---|
| High-frequency accuracy on the seven retained outputs | **7-port, order112, extended10kHz** | Best 3–10 kHz residuals in PR #7; advantage reproduced on NMO_162186 | Only one external holdout; passive RC only |
| Lower-memory passive alternative | **Order84** (choose shift set for required frequency/transient domain) | Lowest median peak RSS in the separate order resource matrix | No one order84 shift strategy is best on every endpoint |
| Need basal-q25 and apical-q25 outputs | **9-port, order168** | Near-parity on shared outputs and q25 maximum NRMSE <1e−6% in equal-order test | Higher RSS and fewer retained full-state degrees than order84; holdout port-count replication still needed |
| Canonical reference | **Full Hines** | Remains the unreduced reference against which all passive candidates are measured | More states and resource cost; not being replaced |

This table is a research selection guide, not a production-default change. All passive models remain candidates for specific protocols and output sets.

## 6. Unresolved validation gates

1. **Cross the port-count and holdout dimensions.** The NMO_162186 holdout tested the nine shift/order candidates, while the equal-order 7-vs-9 matrix used three other morphologies. Run the seven-port and nine-port designs at matched orders on NMO_162186 before claiming the q25 port decision generalizes to that holdout.
2. **Add another independent morphology.** NMO_162186 is a single epilepsy specimen with incomplete axon. Add at least one independently sourced morphology with clear metadata and different experimental context; do not label a single morphology as a population.
3. **Control performance timing.** Re-run order84/112/168 and the exact seven-port order112-extended candidate on one fixed machine or a controlled self-hosted runner with repeated isolated kernel timings. GitHub hosted CPU heterogeneity prevents a clean wall-time ranking.
4. **Test active/nonlinear biology separately.** These results validate passive linear-RC reduction only. They do not validate action potentials, active dendritic ion channels, nonlinear synapses, calcium, plasticity, metabolism or cognition.
5. **Retain uncertainty and negative results.** The ±20% Rm/Cm/Ra scenarios are deterministic stress tests, not fitted biological distributions. A hierarchical or subject-level uncertainty treatment is not applicable to these numerical morphology fixtures but should be applied when biological measurements are introduced.

## Source experiments and audit links

- [PR #4 — nine-port high-order capacity](https://github.com/Nolane-x/Nghien-cuu/pull/4); [workflow 44979673244](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244); [validated report on main](https://github.com/Nolane-x/Nghien-cuu/blob/main/amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md).
- [PR #5 — resource benchmark](https://github.com/Nolane-x/Nghien-cuu/pull/5); [workflow 44989658844](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44989658844); [resource report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-high-order-resource-benchmark/amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md).
- [PR #6 — equal-order seven-vs-nine-port](https://github.com/Nolane-x/Nghien-cuu/pull/6); [workflow 44987393352](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44987393352); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-equal-order-seven-vs-nine-ports-2026-11-22/amsn-core/research/HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_PORT_COUNT_2026-11-22.md).
- [PR #7 — shift/order Pareto](https://github.com/Nolane-x/Nghien-cuu/pull/7); [workflow 45002816664](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45002816664); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-basis-transfer-protocol-robustness-2026-11-22/amsn-core/research/HUMAN_PRIMA_SHIFT_ORDER_PARETO_2026-11-22.md).
- [PR #8 — held-out morphology](https://github.com/Nolane-x/Nghien-cuu/pull/8); [workflow 45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648); [report](https://github.com/Nolane-x/Nghien-cuu/blob/research/allen-human-morphology-heldout-preflight-2026-11-22/amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md).

## Final guardrails

- Full Hines remains canonical.
- No production order default, port count, or runtime behavior is changed in this synthesis.
- A lower Hines-relative residual is not the same as lower discrepancy to native NEURON; both comparisons must remain separate.
- Resource results are specific to the complete audit process and mixed GitHub runner hardware.
- Passive linear-RC validation must not be described as active-neuron or biological validation.
