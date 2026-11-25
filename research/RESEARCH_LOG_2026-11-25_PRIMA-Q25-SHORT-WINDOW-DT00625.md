# Research log — PRIMA q25 short-window dt=0.00625 ms audit

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-dt00625-2026-11-25\`  
**Parent checkpoint:** PR #32, q25 four-step timestep refinement

## Motivation

The previous four-timestep sweep established that 100–200-ms nine/seven ratios are nearly invariant across dt=0.1 to 0.0125 ms, but short-window ratios still vary (notably Peng at 20 ms and Tamas at 40 ms). The next study therefore restricts the simulation to 20 and 40 ms and adds dt=0.00625 ms.

## Method and scope

Two checksum-pinned passive morphology reconstructions; nine parameter scenarios; seven-port and dual-q25 nine-port PRIMA order 168; fixed continuous-time projection bases; three sources; seven shared outputs; 2/10-ms rectangular current pulses. Grid: 0.1/0.05/0.025/0.0125/0.00625 ms. Full Hines at the finest step is the temporal reference. All coarse traces are sampled at matching end-of-step times.

## Expected output

15,120 layout metrics; 7,560 paired comparisons; 120 source summaries; 20 morphology × dt × window summaries; 6,048 full-Hines temporal rows; 16 convergence summaries.

## Execution record

Workflow [45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117) passed in both attempts. Each passed **20/20 tests**, both SWC checksum/preflight gates, the full short-window matrix, six exact CSV read-backs, result commit and artifact upload.

- Result commit `455b304a9f79c118196c6669c61fb4206a24375b`.
- Artifacts: [14994563122 (attempt 1)](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994563122), [14994278136 (attempt 2)](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994278136).
- Same-commit repeatability: 36/36 basis/model digests, 360/360 trace digests and all six numerical CSVs are byte-identical. Only runtime wall-time metadata differs.
- Both attempts used single-thread BLAS/OpenMP environment and `PYTHONHASHSEED=0`; active threadpool introspection was unavailable because `threadpoolctl` was not installed.

## Limits and next step

The 0.00625-ms trace is a finer reference, not exact continuous time. This is a targeted passive numerical comparison on two morphologies only. After CI, compare successive 20/40-ms nine/seven ratios and full-Hines discrepancy ratios; determine whether remaining variation is integration error or the finite-window boundary component. No production defaults are changed.


## Final short-window result — 25 November 2026

Median dual-q25 nine-port / seven-port perturbation-coordinate transient NRMSE ratios, by timestep order 0.1/0.05/0.025/0.0125/0.00625 ms:

| Morphology | 20 ms | 40 ms |
|---|---|---|
| Tamas | 24.47 / 26.80 / 27.19 / 26.39 / 24.64× | 55.21 / 57.13 / 54.88 / 49.79 / 49.14× |
| Peng | 138.26 / 128.38 / 123.56 / 119.50 / 114.77× | 70.09 / 67.67 / 64.52 / 65.31 / 65.06× |

Absolute nine-port NRMSE at dt 0.00625 ms remains tiny: about 4.22e-9% and 1.23e-8% for Tamas 20/40 ms, and 1.28e-8% and 6.40e-8% for Peng 20/40 ms. Thus ratios compare a small residual against an even smaller seven-port residual and should not be interpreted as large absolute waveform deviations.

Full-Hines median NRMSE against dt 0.00625 ms, by coarse dt 0.1/0.05/0.025/0.0125:
- Tamas 20 ms: 0.732 / 0.346 / 0.150 / 0.0503%.
- Tamas 40 ms: 0.678 / 0.322 / 0.141 / 0.0472%.
- Peng 20 ms: 0.734 / 0.345 / 0.149 / 0.0498%.
- Peng 40 ms: 0.657 / 0.309 / 0.133 / 0.0449%.

### Repeatability verified

The initial unpinned same-commit rerun changed the reduced metrics even though Hines reference traces matched. With BLAS/OpenMP thread variables pinned to one and `PYTHONHASHSEED=0`, both attempts of run 45552298117 reproduced **all 36 basis/model hashes, all 360 full/reduced trace hashes and all six numerical CSVs byte-for-byte**. Only wall-time metadata differs (162.52 vs 164.51 s). This confirms repeatability within the tested GitHub Actions environment, not across arbitrary hardware or BLAS libraries.

The runtime threadpool inspector was unavailable (`threadpoolctl` missing), but Actions logs confirmed the environment variables in both attempts. Keep the single-thread settings and digest diagnostics in follow-up numerical workflows.

### Interpretation

The remaining 20–40-ms q25 ratios still vary with dt even though the computations are now reproducible. Peng 20 ms declines steadily as dt is reduced; Tamas 40 ms also falls, while Tamas 20 ms is non-monotonic and Peng 40 ms is comparatively flat below 0.025 ms. The next scientific step should isolate periodic-transfer and terminal-boundary contributions at short windows rather than run another generic all-window sweep. No production defaults were changed.
