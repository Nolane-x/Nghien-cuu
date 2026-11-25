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
