# Handoff — Cross-morphology PRIMA q25 Krylov growth audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-growth-cross-morphology-2026-11-24  
**Parent:** basis-conditioning audit / PR #21

## Research question

The completed basis-conditioning audit found machine-precision orthogonality and full acceptance of every initial shifted input-port block, but did not explain why the Peng mouse dual-q25 layout has a large order-168 transient penalty while the Tamas human pyramidal layout does not. This follow-up records the later round-robin block-Krylov growth, per-shift residual ratios and accepted/rejected vectors.

## Design

Both pinned morphologies; four q25 layouts; basis orders 112/168; nine passive parameter scenarios; six positive-real expansion shifts. The audit mirrors the existing twice-reorthogonalized modified Gram-Schmidt and the existing Hines shifted solves. It compares every instrumented final basis against the unmodified production builder and fails if the maximum absolute difference exceeds 1e-14.

The output separates initial seed blocks from later round-robin iterations and records per-candidate norms, residual norms, residual ratios, acceptance decisions and global basis size.

## Expected exact coverage

- 144 model-level basis-growth summaries.
- 864 initial shift-block summaries.
- Variable numbers of later-round shift summaries and candidate events, each included in the generated report.

## Scientific constraints

This is a diagnostic of numerical basis construction on two individual passive linear-RC morphologies. The instrumented basis must match production basis; no production code changes. Krylov growth metrics alone do not prove the cause of transient error differences. Full Hines remains canonical.
