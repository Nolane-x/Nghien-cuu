# Handoff — PRIMA held-out morphology, port-count and order-capacity results

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**PR:** [#8 — draft/open](https://github.com/Nolane-x/Nghien-cuu/pull/8)  
**Checkpoint:** `5180f0bc72dbfad0a460b0870ca80fec772db0e3`

## Read first

1. [Validated PRIMA results](amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md).
2. [Research log](research/RESEARCH_LOG_2026-11-22_PRIMA-PORT-ORDER-HOLDOUT.md).
3. [20-artifact SHA-256 manifest](amsn-core/results/human_prima_verified_artifact_manifest_2026-11-22.csv).

## Current validated state

- NMO_162186 source + PRIMA [45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648): 2/2 pass; 7,287 SWC records; 81/729/3,402 model/frequency/transient rows; all 81 Cholesky checks passed.
- Equal-order 7-vs-9 [45012282737](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282737): 12/12 pass; 1,008 common-port transient pairs and 144 q90 pairs.
- Nine-port high-order [45012282650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282650): 6/6 pass; 2,520 rows.
- Core CI [45012282476](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282476): 4/4 pass.
- Nine-port enrichment [45012282496]: 6/6 pass. Parameter robustness [45012282485]: 3/3 pass.
- Runtime/RSS matrix [45012282723]: validator preflight passed; 23/30 resource jobs were still queued. Matrix not yet complete.

## Research decisions

- Keep full Hines as canonical; do not change production defaults.
- Keep seven ports as the canonical passive PRIMA reference. Equal-order 9-port expansion at orders56 and112 worsened all common outputs in this test. Order168 returned shared-port errors to numerical parity, not a systematic improvement.
- Order168 offers morphology-dependent benefit over112; the Mohan partial dendritic fixture improves markedly, the two Segev fixtures plateau. Await runtime/RSS cost before deciding whether that capacity is worth using.
- For NMO_162186, order112 extended-10k has much lower 10kHz Z/Y error than narrow shifts and nearly identical transient error. Order84 narrow is a lower-storage transient-oriented alternative.

## Scientific limits

NMO_162186 is a human L2–3 dendritic reconstruction from an epilepsy surgical specimen, with incomplete axon. It is not a healthy control or representative population sample. All results are passive linear-RC numerical comparisons; ±20% parameter cases are deterministic stress tests. No active-channel, nonlinear-synapse, calcium, plasticity, gene, metabolism or cognition validation is implied.

## Next steps

1. Complete the 30-job high-order runtime/peak-RSS matrix and inspect every artifact/hash.
2. Seek a second independent human morphology with explicitly verified provenance and completeness fields before claiming holdout generalization.
3. Keep all raw artifacts/manifests and run logs; no force-push or PR merge without explicit authorization.
