# Handoff — PRIMA nine-port high-order basis results

**Updated:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Merged PR:** https://github.com/Nolane-x/Nghien-cuu/pull/4  
**Merge commit:** `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`

## Start here

1. `AGENTS.md` — scientific integrity and project constraints.
2. `HANDOFF.md` — main project handoff.
3. `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md` — complete validated results.
4. `research/RESEARCH_LOG_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md` — research log and next work.
5. `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md` — prior seven-versus-nine port result.

## Status and evidence

PR #4 is merged. The merged code makes the optional extended PRIMA order sweep configurable through `AMSN_PRIMA_EXTENDED_ORDERS`; existing defaults remain 28/56/84. New workflow `.github/workflows/amsn-human-prima-nine-port-high-order.yml` explicitly tests 28/56/84/112/168.

Latest-head evidence:
- High-order matrix [44979673244]: 6/6 jobs success, 420 rows per config, 2,520 rows total.
- Core CI [44979673250]: 4/4 jobs success on Python 3.12 and 3.13.
- Nine-port audit [44979673251]: 6/6 jobs success.
- Seven-port Schur control [44979673239]: 6/6 jobs success.

## Main conclusion

Both six-shift orders 112 and 168 beat the nine-port and seven-port order-84 baselines on apical-q90 in all 36 matched cases per comparison. Both have zero regressions across 252 comparisons of the seven shared outputs. Order 168 is the transient-accuracy leader; order 112 is a lower-rank compromise. Higher orders slightly increase worst-case frequency response error versus native NEURON compared with order 84, while retaining more than 98% state reduction. No CPU-time or peak-memory benchmark has been completed.

Do not change production defaults. Keep full Hines canonical and default sweep 28/56/84. Keep 112/168 opt-in until resource profiling and held-out morphologies pass.

## Durable files added

- `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md`
- `amsn-core/research/analyze_human_prima_nine_port_high_order_artifacts.py`
- `amsn-core/results/human_passive_prima_nine_port_high_order_model_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_high_order_config_candidate_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_high_order_apical_q90_pair_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_high_order_shared_port_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_high_order_shared_port_by_probe_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_high_order_artifact_manifest_2026-11-22.csv`
- `research/RESEARCH_LOG_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md`

## Next experiment

1. Add CPU wall-time and peak RSS collection around basis construction, projection, all frequency solves and transient solves.
2. Compare orders 84/112/168 across repeated cold/warm runs; record median, p95, peak memory and rank.
3. Validate on held-out morphologies not used in the current three-dataset matrix.
4. Check parameter perturbations (Rm, Cm, Ra) without tuning to native NEURON; preserve Hines as exact passive reference and report native simulator discrepancy separately.
5. Keep active mechanisms and nonlinear biology as separate future model classes, never inferred from these passive RC tests.
