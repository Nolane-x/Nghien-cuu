# Handoff — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Parent:** source/output map branch / PR #23

## Research question

The Krylov-growth audit found identical accepted-vector counts on Peng and Tamas, but different per-shift candidate residual ratios. This experiment tests whether those differences affect the seven shared source-to-output transfer functions as the basis grows from seed to each round-robin Krylov prefix.

## Design

Two pinned morphologies, four layouts, orders 112/168, nine passive parameter scenarios, six expansion shifts, nine AC frequencies, three input sources and seven shared output nodes. At each prefix snapshot (seed, after round 1, etc.), project passive G/C, solve the reduced complex transfer system and compare its source-to-output responses against full-Hines references for the exact same morphology, scenario and layout.

The instrumented final basis is required to match the unmodified production PRIMA basis within 1e-14. Projected G/C matrices at the final snapshot are independently checked against production model matrices.

## Expected coverage

- 504 Krylov-prefix snapshots.
- 10,584 per-model source/output transfer summaries.
- 95,256 individual frequency/source/output rows.
- 1,176 output summaries aggregated across nine passive scenarios.
- 168 source summaries aggregated across seven shared outputs.

## Scientific limits

This is passive linear-RC transfer validation only. It measures numerical transfer functions, not active-neuron or biological behavior. Two individual morphology reconstructions are not populations. Full Hines remains canonical; production code/defaults are unchanged.
