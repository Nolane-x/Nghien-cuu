# PRIMA q25 short-window refinement at dt = 0.00625 ms

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-dt00625-2026-11-25\`  
**Parent:** PR #32, four-step convergence through 0.0125 ms  
**Execution:** passed — [workflow 45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117), attempts 1 and 2

## Research question

The 0.1/0.05/0.025/0.0125-ms sweep showed stable 100–200-ms nine/seven ratios but material variation at 20–40 ms. This targeted audit asks whether the short-window relative reduction-error ratios stabilize when dt is reduced to 0.00625 ms.

## Scope

- Same checksum-pinned NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Seven-port and dual-q25 nine-port PRIMA layouts, order 168, fixed continuous-time projection basis per morphology/scenario/layout.
- Nine passive parameter scenarios, three current sources, seven shared SWC outputs, two pulse widths.
- Observation windows restricted to 20 and 40 ms.
- Timestep grid 0.1/0.05/0.025/0.0125/0.00625 ms.
- Full Hines perturbation-coordinate trace at 0.00625 ms is the finer reference; coarser traces are aligned at common end-of-step times.

## Expected coverage

- 15,120 layout-level metrics.
- 7,560 paired seven/nine-port comparisons.
- 120 source × pulse × window summaries.
- 20 morphology × timestep × window summaries.
- 6,048 full-Hines temporal-convergence rows.
- 16 temporal-convergence summary rows.

## Validation

The workflow checks both SWC hashes and morphology preflights, runs focused tests for timestep alignment and pulse charge, executes the complete matrix, and requires exact row-count read-back from all six CSV files.

**Execution status:** passed in both attempts of workflow [45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117). Each attempt passed **20/20 tests**, both SWC SHA-256 checks, both morphology preflights, the full computation, six exact CSV read-backs, result commit and artifact upload.

- Result commit: `455b304a9f79c118196c6669c61fb4206a24375b`.
- Attempt 1 artifact: [14994563122](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994563122), ZIP SHA-256 `ccb011d55ed4bd12527157be6f4af473d4a13e339ff5e01ca689bc62085e455e`.
- Attempt 2 artifact: [14994278136](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994278136), ZIP SHA-256 `c66dd098f47af338559a2a0b5d59f78b69ea2bf7464c786eba5c4fc196ba1b8e`.
- Runtime: 162.52 s and 164.51 s respectively; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.

## Results

### Median dual-q25 nine-port / seven-port transient NRMSE ratio

Each cell is the median over six source × pulse groups; each group first aggregates nine parameter scenarios × seven shared outputs. Ratios compare relative reduction errors and are not pooled-energy ratios.

| Morphology | Window | dt 0.1 ms | dt 0.05 ms | dt 0.025 ms | dt 0.0125 ms | dt 0.00625 ms |
|---|---:|---:|---:|---:|---:|---:|
| Tamas human pyramidal | 20 ms | 24.47× | 26.80× | 27.19× | 26.39× | **24.64×** |
| Tamas human pyramidal | 40 ms | 55.21× | 57.13× | 54.88× | 49.79× | **49.14×** |
| Peng mouse | 20 ms | 138.26× | 128.38× | 123.56× | 119.50× | **114.77×** |
| Peng mouse | 40 ms | 70.09× | 67.67× | 64.52× | 65.31× | **65.06×** |

The short-window ratios are reproducible under the pinned single-thread numerical environment, but they are **not fully timestep-invariant**. Peng 20 ms decreases monotonically from 138.26× to 114.77×. Tamas 40 ms changes from about 57× to 49×, with most of the drop between 0.025 and 0.0125 ms. Peng 40 ms is flatter below 0.025 ms (64.52–65.31×). Tamas 20 ms is non-monotonic, peaking near 0.025 ms and returning to 24.64× at 0.00625 ms.

The absolute nine-port perturbation-coordinate NRMSE at 0.00625 ms remains very small: approximately 4.22e-9% (Tamas, 20 ms), 1.23e-8% (Tamas, 40 ms), 1.28e-8% (Peng, 20 ms), and 6.40e-8% (Peng, 40 ms). Large relative ratios coexist with small absolute waveform residuals.

### Full-Hines temporal convergence against dt = 0.00625 ms

Each summary row covers 378 parameter-scenario × protocol × output traces. Median NRMSE percentages against the 0.00625-ms Hines trace:

| Morphology | Coarse dt | 20 ms median | 40 ms median | Maximum across both windows |
|---|---:|---:|---:|---:|
| Tamas | 0.1 ms | 0.732% | 0.678% | 1.828% |
| Tamas | 0.05 ms | 0.346% | 0.322% | 0.873% |
| Tamas | 0.025 ms | 0.150% | 0.141% | 0.406% |
| Tamas | 0.0125 ms | 0.0503% | 0.0472% | 0.147% |
| Peng | 0.1 ms | 0.734% | 0.657% | 2.698% |
| Peng | 0.05 ms | 0.345% | 0.309% | 1.312% |
| Peng | 0.025 ms | 0.149% | 0.133% | 0.582% |
| Peng | 0.0125 ms | 0.0498% | 0.0449% | 0.200% |

The coarse-vs-fine error decreases consistently as dt is reduced, supporting first-order backward-Euler convergence. The 0.00625-ms waveform remains a finer numerical reference, not an exact continuous-time solution.

### Reproducibility verification

The two attempts of the **same commit** `586175367fb5d71d16b3244dcf059e6fa6f4793e`, with identical single-thread environment settings, were compared directly from their artifacts:

- **36/36** basis/model digests matched: basis, reduced G, reduced C, input matrix and retained-port index vector.
- **360/360** full/reduced trace digests matched.
- All six numerical CSVs were byte-identical between attempts. Their SHA-256 digests are:

| Output | SHA-256 |
|---|---|
| `..._metrics.csv` | `0748ccec72e475b766141a84ad9692c3e48ff2cb37e2657e6bafbb4aeddcea5a` |
| `..._seven_nine_comparisons.csv` | `c7f28a2200e3e7dab6c8d3b1735e834c8ecbc9068ac7734973f6f7a7b4892bd2` |
| `..._source_window_summary.csv` | `93ce68fd812ed52c7cc6347354fd3340de9bcb7ed3f7f6a4ec17f66b53f374f6` |
| `..._morphology_window_summary.csv` | `55315b452df1722bdce1d4ef5be5f1bc6e6c2551a801bc33209452fb0e0bc664` |
| `..._hines_temporal_convergence.csv` | `2fbfe7fea87564f78c9a2748ca97e4d6d4d960cd43665dd8153ee1f2288d136f` |
| `..._hines_temporal_convergence_summary.csv` | `5aeae14d15bc9fe5d0c4b0561198b227164a0bd9bc14ce60920ff6635fe6c2a4` |

The report JSON differs only in measured runtime wall time (162.52 vs 164.51 s); coverage, validation, basis/trace diagnostics and scientific summaries are identical. The timing files also differ as expected. Both attempts recorded all BLAS/OpenMP thread-control variables as `1` and `PYTHONHASHSEED=0`. The optional `threadpoolctl` package was not installed, so no active threadpool count was queried; the environment variables themselves were confirmed in the Actions logs.

This establishes repeatability for two same-commit runs under the pinned GitHub Actions environment. It does not prove bitwise reproducibility on other hardware, BLAS implementations or environments.

