# Research log — PRIMA q25 short-window boundary decomposition

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-boundary-decomposition-2026-11-25\`  
**Parent checkpoint:** PR #33, repeatable q25 short-window timestep refinement

## Motivation

PR #33 established reproducible 20/40-ms seven/nine-port ratios through dt=0.00625 ms, but they remain timestep-sensitive. Earlier finite-window analysis showed that periodic transfer and terminal state can partially cancel. The next experiment therefore decomposes the actual finite-window reduced-model error instead of running another generic timestep sweep.

## Sources

- PR #30 exact backward-Euler discrete transfer and terminal-state finite-record identity.
- PR #33 repeatable dt=0.00625-ms short-window trace/reduction outputs and pinned BLAS environment.
- Canonical Hines BE factorization, reduced PRIMA BE recurrence, exact SWC and morphology-preflight sources.

## Method

At dt=0.00625 ms, evaluate the exact finite-record relation on the DFT bins of 20/40-ms windows:
\[
E=(H_9-H_7)U-(Q_9-Q_7).
\]
Calculate the periodic transfer component, terminal-boundary component, finite-error norm and cross-term. Verify the reconstructed finite error against the actual DFT difference. Use a 25-Hz master grid through Nyquist 80 kHz; 20-ms bins have 50-Hz spacing and 40-ms bins 25-Hz spacing.

The reduced transient uses the batched factorized LU recurrence throughout the record. BLAS/OpenMP and Python hash settings are pinned to the same single-thread environment proven repeatable by PR33.

## Expected output

268,884 frequency rows; 3,024 case metrics; 1,512 paired seven/nine comparisons; 24 source/pulse/window summaries; 4 morphology/window summaries; 432 identity rows; report JSON with basis/trace digests and runtime configuration.

## Execution record

Pending Actions. Six CSV read-back gates and the finite-record identity tolerance are mandatory. No new numerical conclusion is claimed before the workflow completes.

## Limits and next step

Component norms can exceed the finite-error norm because the cross-term can be strongly negative. Interpret the cancellation alongside the identity residual and absolute transient NRMSE. Only two passive morphologies are tested; no active-neuron or biological validation. Keep full Hines canonical and do not change production defaults.
