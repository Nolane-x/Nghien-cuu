# Research log — Cross-morphology PRIMA q25 basis conditioning audit

**Date:** 24 November 2026  
**Branch:** research/prima-cross-morphology-q25-conditioning-audit-2026-11-24  
**Status at creation:** implementation prepared; no audit metrics claimed.

## Motivation

The Peng mouse q25 ablation found a large dual-q25 order-168 penalty (14.525× median shared-output NRMSE ratio), while the independent Tamas human pyramidal replication found an approximately neutral result (1.001×). Both samples showed stronger degradation at order 112. This suggests morphology-by-order sensitivity, but no mechanism has been established.

## Audit design

For both morphologies, all four q25 layouts, both basis orders and all nine passive parameter scenarios:
- rebuild the PRIMA multi-shift basis using the original production function without changing its implementation;
- quantify (V^T V-I), the eigenvalues and condition number of the basis Gram matrix;
- quantify eigenvalue ranges and condition numbers for projected conductance and capacitance matrices;
- quantify the generalized passive RC decay-rate range from the symmetric whitened pair (C_r^{-1/2}G_rC_r^{-1/2});
- measure each retained port's basis-row leverage;
- reproduce and count the independent initial seed columns accepted from each of the six expansion shifts using the existing shifted-Hines solve and orthogonalization primitives.

The seed count is explicitly only the initial seeding contribution, not the later round-robin Krylov growth.

## Expected exact coverage

- 144 reduced-model structural metric rows.
- 1,152 per-port leverage rows.
- 864 initial shift-seed rows.
- 8 morphology/layout/order groups in the summary (2 × 4 × 2).

## Files created

- `amsn-core/research/audit_prima_q25_basis_conditioning.py`
- `amsn-core/tests/test_prima_q25_cross_morphology_conditioning.py`
- `.github/workflows/amsn-prima-q25-cross-morphology-conditioning-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-CROSS-MORPHOLOGY-CONDITIONING.md`
- This research log.

## Interpretation limits

The audit is descriptive and structural. Orthogonality and positive definiteness do not guarantee transient approximation quality; matrix condition numbers and initial seed counts do not prove causality. Keep mouse and human morphologies separate. No active conductances, biological validity, solver-default promotion or production-code changes are part of this task.
