# Handoff — PRIMA q25 short-window periodic-transfer / terminal-boundary decomposition

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-boundary-decomposition-2026-11-25\`  
**Parent:** PR #33, reproducible q25 short-window dt=0.00625-ms audit

## Question

For the 20/40-ms finite records, how much of the seven/nine-port error is due to periodic discrete transfer, how much to the terminal state, and how strongly do the two components cancel?

## Method

- Reuse exact PR30 finite-record identity under the dt=0.00625-ms sample-end convention.
- Compute \(E_\mathrm{periodic}=(H_{9,\mathrm{BE}}-H_{7,\mathrm{BE}})U\).
- Compute \(E_\mathrm{boundary}=-(Q_9-Q_7)\), with each \(Q\) formed from the terminal state \(x[N-1]\).
- Verify \(E_\mathrm{finite}=E_\mathrm{periodic}+E_\mathrm{boundary}\) against the actual DFT of the reduced-minus-full perturbation trace.
- Report each component norm divided by the finite-error norm and the normalized cross-term; values above 100% are possible under cancellation.
- Keep order-168 PRIMA bases fixed for each morphology/scenario/layout; use the reproducible single-thread BLAS environment from PR33.

## Expected coverage

268,884 frequency summaries; 3,024 metric rows; 1,512 paired comparisons; 24 source summaries; 4 morphology/window summaries; 432 finite-record identity rows.

## Execution status

Implementation and 16 focused tests are authored. Full computation is pending GitHub Actions; no numerical result is accepted before all checks and CSV read-backs pass.

## Limits

Only two passive morphology instances. The 0.00625-ms full-Hines trace is a finer numerical reference, not exact continuum truth. No production solver/default is changed.
