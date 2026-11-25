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

Pending GitHub Actions. Expected-count gates and sample-alignment tests are updated for the short-window-only matrix. No new results are accepted until full CI and read-back pass.

## Limits and next step

The 0.00625-ms trace is a finer reference, not exact continuous time. This is a targeted passive numerical comparison on two morphologies only. After CI, compare successive 20/40-ms nine/seven ratios and full-Hines discrepancy ratios; determine whether remaining variation is integration error or the finite-window boundary component. No production defaults are changed.

## Reproducibility investigation — same-commit rerun

The first complete run [45551126065 attempt 1] and its same-commit rerun (attempt 2) both passed all 18 tests, SWC checksum/preflight checks, full simulation, six CSV read-backs and artifact upload. However, their numerical outputs differed:

- Hines temporal-convergence CSV: identical SHA-256 across attempts.
- PRIMA metrics, paired comparisons, source summaries and morphology/window summaries: different SHA-256.
- Maximum absolute change in perturbation transient NRMSE: approximately \(1.6515\times10^{-10}\) percentage points; relative differences can be much larger because the residual itself is tiny.
- Maximum absolute-vs-perturbation Hines trace delta remained in the same \(10^{-8}\%\) range.

This localizes the source to the reduction/basis or reduced-solve path rather than the Hines temporal reference. The current hypothesis is floating-point reduction-order sensitivity; it remains unproven.

On 25 November, the PR #33 branch was updated to pin BLAS/OpenMP libraries to one thread, set \`PYTHONHASHSEED=0\`, record NumPy/BLAS/threadpool runtime details, and hash each basis, projected \(G_r/C_r\), input matrix, port index vector and full/reduced traces. The new workflow runs [45552270328](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552270328) and [45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117) must be followed by a same-final-commit rerun. Reproducibility is accepted only if diagnostic hashes and full CSV hashes are identical; otherwise isolate the earliest differing stage. Do not promote short-window ratios into scientific conclusions yet.

