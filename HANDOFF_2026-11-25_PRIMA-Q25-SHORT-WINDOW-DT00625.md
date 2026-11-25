# Handoff — PRIMA q25 short-window refinement at 0.00625 ms

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-dt00625-2026-11-25\`  
**Parent:** PR #32, fine-step convergence through 0.0125 ms

## Question

Do the 20/40-ms q25 nine/seven transient ratios stabilize when dt is reduced to 0.00625 ms?

## Method

- Same two pinned morphologies, nine parameter scenarios, two layouts, three input sources, seven shared output nodes and two pulse widths.
- Restrict windows to 20 and 40 ms; use dt 0.1/0.05/0.025/0.0125/0.00625 ms.
- Keep the continuous-time order-168 PRIMA basis fixed; refactorize reduced BE systems per timestep.
- Use full-Hines perturbation coordinates as the primary reference; compare coarse full-Hines traces against dt 0.00625 at matching sample-end times.
- Preserve canonical absolute-voltage Hines as a round-off diagnostic.

## Expected coverage

15,120 metrics; 7,560 paired seven/nine comparisons; 120 source summaries; 20 morphology/window summaries; 6,048 Hines temporal rows; 16 Hines temporal summaries.

## Execution status

Both attempts of workflow [45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117) passed **20/20 focused tests**, both SWC checksum/preflight gates, the full calculation, six exact CSV read-backs, result commit and artifact upload.

- Result commit: `455b304a9f79c118196c6669c61fb4206a24375b`.
- Attempt 1 artifact: [14994563122](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994563122).
- Attempt 2 artifact: [14994278136](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117/artifacts/14994278136).
- Same-commit repeatability confirmed: 36/36 basis/model hashes, 360/360 trace hashes and all six numerical CSVs match byte-for-byte. Only runtime metadata differs (wall time 162.52 vs 164.51 s).


## Limits

Only two passive morphology instances. The finest timestep is a numerical reference, not exact continuum truth. No production solver/default is changed.


## Validated findings and current interpretation

Median nine/seven perturbation-coordinate transient ratios, ordered by dt 0.1/0.05/0.025/0.0125/0.00625 ms:

- Tamas 20 ms: **24.47 / 26.80 / 27.19 / 26.39 / 24.64×**.
- Tamas 40 ms: **55.21 / 57.13 / 54.88 / 49.79 / 49.14×**.
- Peng 20 ms: **138.26 / 128.38 / 123.56 / 119.50 / 114.77×**.
- Peng 40 ms: **70.09 / 67.67 / 64.52 / 65.31 / 65.06×**.

Absolute nine-port NRMSE at dt 0.00625 ms is about 4.22e-9%, 1.23e-8%, 1.28e-8%, and 6.40e-8% for Tamas 20/40 and Peng 20/40 respectively. These are relative reduction-error ratios with very small absolute residuals.

Full-Hines coarse-vs-0.00625-ms median NRMSE is about 0.68–0.73% at dt 0.1, 0.309–0.346% at 0.05, 0.133–0.150% at 0.025 and 0.0449–0.0503% at 0.0125. The 0.00625-ms Hines trace remains a finer reference, not a continuous-time exact solution.

## Reproducibility lesson

The original unpinned same-commit rerun differed in PRIMA residual CSVs even though Hines reference traces matched. Pinning BLAS/OpenMP and Python hash-seed environment resolved the observed issue in this Actions environment: the two thread-pinned attempts produced identical 36 basis/model digests, 360 trace digests and all six CSV hashes. The report JSON differs only in runtime wall time. The diagnostic could not query live threadpool counts because `threadpoolctl` was absent, but the job logs confirm each relevant thread-control environment variable was set to `1`.

Keep the branch single-thread settings and digest checks in future numerical workflows. This evidence supports repeatability on the GitHub Actions environment tested; it does not guarantee identical results across other BLAS vendors or hardware.

