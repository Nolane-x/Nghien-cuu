# Research log — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Status at creation:** implementation prepared; no transfer error result claimed.

## Motivation

The preceding Krylov trace showed identical accepted-vector schedules for Peng and Tamas but substantial differences in post-orthogonalization candidate residual ratios. The next question is whether the novel directions added at each Krylov stage actually improve source-to-output transfer responses at the seven shared ports.

## Design

For both morphologies, four layouts, orders 112/168 and all nine passive scenarios:
1. Build the initial seed basis and preserve a snapshot after seed, then after each complete round-robin Krylov round.
2. Rebuild the full production PRIMA model and require final basis maximum absolute difference <=1e-14.
3. Project passive G and C at each prefix snapshot using the same conductance operator as production; compare final projected matrices against the production reduced matrices.
4. For each prefix, compute reduced complex transfer functions for soma, basal-q75 and apical-q75 sources at the nine AC frequencies.
5. Compare the seven shared SWC output nodes against full-Hines responses for the same scenario/layout/source/frequency.

Each output snapshot has nine frequency samples. Summary metrics preserve complex relative L2 error and per-frequency absolute/relative error.

## Expected exact coverage

- 504 snapshot rows.
- 10,584 per-model source/output rows.
- 95,256 frequency/source/output rows.
- 1,176 scenario-aggregated source/output rows.
- 168 scenario-aggregated source rows.

## Files created

- `amsn-core/research/analyze_prima_q25_krylov_transfer_stages.py`
- `amsn-core/tests/test_prima_q25_krylov_transfer_stages.py`
- `.github/workflows/amsn-prima-q25-krylov-transfer-stage-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-KRYLOV-TRANSFER-STAGE-AUDIT.md`
- This research log.

## Interpretation limits

Improvement or deterioration of a transfer residual across prefix snapshots localizes approximation behavior, but does not establish biological relevance or by itself explain transient response differences. Only two individual passive morphologies are tested. Full Hines remains canonical and production defaults remain unchanged.
