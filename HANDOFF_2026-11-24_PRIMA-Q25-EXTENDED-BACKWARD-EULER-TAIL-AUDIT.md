# Handoff — Cross-morphology PRIMA q25 extended backward-Euler tail audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-extended-backward-euler-tail-audit-2026-11-24  
**Parent:** pulse-weighted transfer bridge / PR #27

## Research question

The continuous-time pulse-weighted AC bridge still showed large dual-q25/seven spectral ratios on Tamas, while the archived 20-ms time-domain NRMSE ratio remained near one. This audit re-runs the exact implicit backward-Euler method at dt=0.1 ms and measures cumulative NRMSE over 20, 40, 100 and 200-ms observation windows. It tests whether a late passive tail outside the original 20-ms window explains the gap.

## Scope

- Both checksum-pinned morphologies (Peng mouse NMO_163775 and Tamas human pyramidal NMO_107159).
- Seven-port and dual-q25 nine-port at basis order 168.
- Nine passive parameter scenarios, three current sources and seven exact shared output SWC nodes.
- 10-pA rectangular inputs, 2-ms onset, pulse widths 2/10 ms.
- Same 0.1-ms backward-Euler recurrence, extended to 200 ms.
- Report cumulative 20, 40, 100 and 200-ms errors for every source/output/scenario/pulse pair.

The full cable matrix is assembled from the exact passive tree G/C and factorized sparsely; reduced BE operators are precomputed from the exact reduced G/C matrices. A 20-ms parity guard requires the extended implementation to reproduce the archived transient NRMSE values closely before later windows are accepted.

## Expected exact coverage

- 6,048 per-layout cumulative transient rows.
- 3,024 paired dual-q25/seven comparisons.
- 756 20-ms archived parity rows.
- 672 per-output summaries.
- 336 per-output comparison summaries.
- 48 by-source summaries.
- 16 whole-window summaries.
- 32 layout/window summaries.

## Scientific constraints

This uses the exact BE update rule and sample timing, but the full Hines reference is solved via a sparse factorization of the same full cable matrix and must pass archived 20-ms parity. Only two individual passive linear-RC morphologies are compared. Full Hines remains canonical and no production code/defaults change.
