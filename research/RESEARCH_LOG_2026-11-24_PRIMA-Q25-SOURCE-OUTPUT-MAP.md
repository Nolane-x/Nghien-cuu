# Research log — Cross-morphology PRIMA q25 source/output residual map

**Date:** 24 November 2026  
**Branch:** research/prima-q25-source-output-cross-morphology-map-2026-11-24  
**Status at creation:** deterministic aggregation prepared; no new CI result claimed.

## Motivation

The prior q25 experiments show a large dual-q25 order-168 penalty on Peng but near-baseline behavior on Tamas. This analysis localizes that contrast by input-source location and shared output port, instead of collapsing all 378 pairs into one median.

## Method

Use the already archived and validated `matched_shared_vs_seven.csv` from each morphology. Validate exact row counts, required columns, finite positive ratios, unique row identities and the full factorial matrix. Summarize by morphology × candidate layout × order × input source × shared output port. A source summary collapses the seven outputs but retains the input-source identity.

Each per-output group must contain 18 matched values (9 parameter scenarios × 2 pulse widths). Each per-source group must contain 126 pairs (7 shared outputs × 18 values).

## Expected coverage

- 2,268 rows per morphology; 4,536 total.
- 252 per-output groups.
- 36 per-source groups.
- Top 50 worst per-output group medians.

## Files created

- `amsn-core/research/analyze_prima_q25_cross_morphology_source_output.py`
- `amsn-core/tests/test_prima_q25_cross_morphology_source_output.py`
- `.github/workflows/amsn-prima-q25-source-output-map.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-SOURCE-OUTPUT-MAP.md`
- This research log.

## Interpretation limits

The ratio is relative to the seven-port error and may amplify a tiny denominator. Always show absolute NRMSE beside ratios. This is a two-morphology passive-RC numerical comparison; it does not identify a causal mechanism or establish biology.
