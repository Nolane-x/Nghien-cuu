# Research log — Cross-morphology PRIMA q25 Krylov growth audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-growth-cross-morphology-2026-11-24  
**Status at creation:** implementation prepared; no growth metrics claimed.

## Motivation

The q25 conditioning audit found:
- all basis Gram matrices orthonormal to floating-point precision;
- every initial shift accepted its full 7/8/9 input-port block;
- projected G/C condition numbers and q25 row leverage did not provide a simple explanation of the Peng-vs-Tamas order-168 transient difference.

The unresolved stage is later round-robin block-Krylov growth.

## Audit design

For both morphologies, four layouts, orders 112/168 and all nine passive parameter scenarios:
1. Trace every initial seed vector and every subsequent Krylov candidate, grouped by shift and iteration.
2. Record original norm, post-reorthogonalization residual norm, residual/original ratio, acceptance/rejection, global basis size and per-shift accepted counts.
3. Preserve the exact production twice-reorthogonalized modified Gram-Schmidt behavior, including its accepted-block projection ordering.
4. Rebuild the unmodified production PRIMA basis for every model and require the instrumented final basis to match to a maximum absolute difference of 1e-14.

This deliberately captures later round-robin growth, not just the initial seed block.

## Expected exact coverage

- 144 instrumented model summaries.
- 864 initial shift-block summaries.
- Variable later-round and candidate-event counts, reported explicitly and preserved in CSVs.
- All 144 final basis parity checks within 1e-14 of production.

## Files created

- `amsn-core/research/audit_prima_q25_krylov_growth.py`
- `amsn-core/tests/test_prima_q25_krylov_growth.py`
- `.github/workflows/amsn-prima-q25-krylov-growth-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-KRYLOV-GROWTH-AUDIT.md`
- This research log.

## Interpretation limits

A basis-growth trace may localize differences in candidate novelty and shift contributions, but does not establish that they cause the observed transfer or transient residual. Keep the two morphologies separate. No biological validation or production default change is in scope.
