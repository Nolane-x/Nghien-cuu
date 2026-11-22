# Handoff — human passive PRIMA high-order resource benchmark

**Date:** 2026-11-22 (Asia/Bangkok)  
**Branch:** research/prima-high-order-resource-benchmark  
**PR:** https://github.com/Nolane-x/Nghien-cuu/pull/5  
**Validated Actions run:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44989658844

## Completed repair

The original benchmark failed only at model-identity validation after the simulation, measurement and artifact creation had succeeded. The cause was treating the comma-separated environment string 56,84 as one model order and trying to find a model literally named six_shift_order56,84.

Commit e643782 fixed the parser and separated the candidate order from the extended order list. It added a reusable validator, 12 unit tests and a preflight job that must succeed before the 36-measurement matrix can run.

## Validated result

The complete run passed **37/37 jobs**: 1 preflight plus all 36 resource measurements. Each measurement:
- exited with code 0;
- had 210 sweep rows (30 frequency, 162 transient-port and 18 all-port);
- had exact model identity, requested/achieved rank and port/scenario coverage;
- recorded wall time, user/system CPU and peak RSS.

The 36 artifact ZIPs were downloaded and their local SHA-256 hashes matched GitHub's published artifact digests. Full raw data, order summaries, per-morphology/mesh summaries, memory deltas and artifact manifest are committed under amsn-core/results/; the complete interpretation is in amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md.

## Resource decision

Peak RSS rose in all 12 matched pairs when increasing order:
- 112 vs 84: median +6.24 MB;
- 168 vs 84: median +23.48 MB;
- 168 vs 112: median +18.32 MB.

Order 84 is the lowest-resource candidate for future quality-versus-memory testing. Order 168 remains the more capable nine-port passive research candidate after the equal-order 7-vs-9 validation, but requires more peak memory. Wall/CPU medians are noisy because seven different CPU models were assigned by GitHub; don't claim a definitive speed ranking from them.

Keep Hines canonical and all production defaults unchanged. The study is passive RC only; do not extrapolate to active electrophysiology or cognition.
