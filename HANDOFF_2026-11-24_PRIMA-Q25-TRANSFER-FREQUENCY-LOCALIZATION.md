# Handoff — PRIMA q25 transfer frequency localization

**Date:** 24 November 2026  
**Branch:** research/prima-q25-transfer-frequency-localization-2026-11-24  
**Parent:** Krylov-prefix transfer audit / PR #24

## Research question

Which sampled AC frequencies account for the remaining source-to-output transfer residual after the final Krylov prefix, and how do the two rectangular pulse widths (2 ms and 10 ms) weight those sampled frequencies?

## Design

This deterministic post-processing consumes the verified 95,256-row AC transfer matrix from PR #24. It groups error by morphology, layout, basis order, Krylov stage, source, shared output and frequency, then compares candidates with seven-port at the same stage. It also records the normalized magnitude and power spectrum of the continuous-time rectangular pulse at the nine sampled frequencies. These are descriptive samples, not a continuous integral.

Expected:
- 10,584 output/frequency groups (nine passive scenarios aggregated).
- 1,512 source/frequency groups.
- 7,938 paired candidate-vs-seven output/frequency groups.
- 1,134 candidate-vs-seven source/frequency summaries.
- 18 pulse-spectrum samples.
