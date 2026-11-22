# Handoff — validated nine-port PRIMA result and next basis-capacity experiment

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Merged PR:** https://github.com/Nolane-x/Nghien-cuu/pull/3  
**Merge commit:** `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`

## Start here

1. `AGENTS.md` — preservation and scientific-integrity rules.
2. `HANDOFF.md` — long-range AMSN objective and latest checkpoints.
3. `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md` — complete result and decision.
4. `research/RESEARCH_LOG_2026-11-22_PRIMA-NINE-PORT-RESULTS.md` — experiment record, validation and next step.
5. `amsn-core/research/HUMAN_PASSIVE_PRIMA_ORDER_TRANSIENT_SWEEP_2026-11-22.md` — seven-port comparison baseline.

## Completed work

PR #3 implemented deterministic morphology quantile probes and an isolated nine-port Schur/PRIMA workflow. The canonical seven-port mapping path remained unchanged. The merged implementation is validated by:
- Nine-port workflow [44976224651]: 6/6 morphology × mesh jobs passed, all six artifacts uploaded.
- Core CI [44976224745]: 4/4 jobs passed on Python 3.12 and 3.13, including NEURON cross-validation.
- Seven-port control [44976224560]: 6/6 jobs passed.
- All 14 workflows recorded on the final PR head completed successfully.

The six nine-port configurations each generated 280 rows (40 frequency + 240 transient); 1,680 rows total.

## Main result

Matched q90 comparison: 36 pairs per model, six configurations × six pulse/source scenarios. Every model worsened on apical-q90 in 36/36 pairs after going from seven to nine ports:
- Four-shift order 56: median 11.515×, max 22.350×.
- Six-shift order 28: median 2.118×, max 3.394×.
- Six-shift order 56: median 127.706×, max 613.199×.
- Six-shift order 84: median 7.814×, max 28.749×.

This is a validated negative result for the proposition that simply adding q25 retained ports improves the difficult q90 transient. Do not promote nine ports as the default. Keep seven-port baseline and full Hines canonical. Six-shift order 84 remains only the best nine-port option among those tested; it still does not beat the paired seven-port apical-q90 error.

## Files added in this checkpoint

- `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md`
- `amsn-core/results/human_passive_prima_nine_port_model_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_config_model_summary_2026-11-22.csv` — 24 morphology × mesh × model rows
- `amsn-core/results/human_passive_prima_nine_vs_seven_port_q90_summary_2026-11-22.csv`
- `amsn-core/results/human_passive_prima_nine_port_artifact_manifest_2026-11-22.csv`
- `research/RESEARCH_LOG_2026-11-22_PRIMA-NINE-PORT-RESULTS.md`

Raw 9-port and 7-port data remain available in the linked Actions artifacts in the report. The report includes artifact IDs and run IDs.

## Next experiment

Investigate basis-capacity allocation under a fixed source/probe protocol:
1. Retain the seven-port control and nine-port enriched port set.
2. Test six-shift order 112 and order 168.
3. Add a block-Krylov or source/probe-weighted basis candidate without altering model parameters.
4. Preserve same morphology/mesh/frequency/transient matrix and all per-port outputs.
5. Require apical-q90 improvement with no unacceptable regression at soma, basal q50/q75/q90 or apical q50/q75; compare against full Hines and native NEURON.
6. Report actual retained rank/state reduction and all failed cases. Keep passive RC claims separate from biological claims.
