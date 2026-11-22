# Handoff — PRIMA high-order resource benchmark completed

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**PR:** [#8 — draft/open](https://github.com/Nolane-x/Nghien-cuu/pull/8)  
**Code head measured:** `e556625b9f0b1f31f9c822e603cf0ae220eefe0f`  
**Completed benchmark run:** [45016243390](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45016243390)

## Start here

1. `AGENTS.md` — research, preservation and scientific-integrity requirements.
2. `HANDOFF.md` — current project handoff; this file supersedes the earlier partial-resource status.
3. `amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md` — complete results and limitations.
4. `research/RESEARCH_LOG_2026-11-22_PRIMA-RESOURCE-BENCHMARK-FINAL.md` — exact session work and test evidence.
5. `amsn-core/results/human_prima_resource_benchmark_artifact_manifest_2026-11-22.csv` — all 36 artifact IDs and SHA-256 checks.

## Completed state

- Actions run 45016243390: **37/37 jobs successful** (one validator + 36 resource jobs).
- Artifact matrix: 3 morphologies × 2 mesh caps × 3 candidate orders (84/112/168) × 2 repeats = 36 unique jobs.
- All 36 ZIP artifacts downloaded; **36/36 SHA-256 digests match** the GitHub artifact API.
- All 36 resource records exit 0; exact selected order achieved; each sweep contains 210 rows.
- Total raw sweep coverage: 7,560 rows = 1,080 frequency + 5,832 per-port transient + 648 aggregate transient rows.
- Validator test log: 16 passed on Python 3.12.16.

## Resource summary

| Order | Median user CPU | Median peak RSS | Median state reduction |
|---:|---:|---:|---:|
| 84 | 141.45 s | 268.16 MiB | 99.3225% |
| 112 | 205.96 s | 277.29 MiB | 99.0967% |
| 168 | 278.31 s | 300.76 MiB | 98.6451% |

The whole audit process was measured; these are not isolated PRIMA-kernel measurements. Seven runner CPU models were observed, so wall-time medians are not used to rank speed. Finer mesh cap 0.0625 µm increased process RSS by roughly 40–50% over 0.125 µm in this matrix.

## Decisions and guardrails

- Do not change production defaults based on this benchmark.
- Full Hines remains the canonical passive reference.
- Order 84 is the lower-resource tested candidate; order 112 is intermediate; order 168 has the highest measured process resource footprint. Their accuracy trade-offs remain morphology/protocol dependent.
- Keep seven ports as the canonical retained-output set. Nine-port order168 remains an optional research candidate, not a universal replacement.
- All claims remain limited to passive linear RC. NMO_162186 is a single epilepsy-surgical dendritic holdout with incomplete axon, not a healthy control or population sample. NMO_290988 is partial dendritic morphology without axon.
- PR #8 remains **draft/open**. Do not merge or mark ready without user authorization.

## Next concrete work

1. Build a kernel-isolated profiler: separate shifted-Krylov basis assembly, orthogonalization, congruence projection, frequency solves and transient solves; run on declared fixed hardware with repeated trials.
2. Measure full Hines in a separate process to avoid mixing its memory and CPU use with reduced-order costs.
3. Repeat the focused profile on NMO_162186 and a second morphology with documented human-cell provenance and axon/dendrite completeness fields.
4. Keep all new results versioned and append-only; retain the old 12-artifact partial report as historical context.

**Latest research log:** `research/RESEARCH_LOG_2026-11-22_PRIMA-RESOURCE-BENCHMARK-FINAL.md`.
