# Handoff — PRIMA apical/basal nine-port enrichment

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Base main commit:** 61c228ecf052d88b821b31455f407b4d3c3467ad  
**Work branch:** `research/prima-apical-port-enrichment-2026-11-22`  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/3  
**Current code head:** `f1dcc73579d1ed7a56b0dfb2d96f38721ea47531`

## Read first

1. `AGENTS.md`
2. `HANDOFF.md`
3. `HANDOFF_2026-11-22_PRIMA-ORDER-TRANSIENT-MATRIX.md`
4. `amsn-core/research/HUMAN_PASSIVE_PRIMA_ORDER_TRANSIENT_SWEEP_2026-11-22.md`
5. `research/RESEARCH_LOG_2026-11-22_PRIMA-APICAL-PORT-ENRICHMENT.md`

## Why this is next

The six-configuration, seven-port order/transient study identified the apical-q90 probe as the recurring worst transient output. The next experiment adds basal/apical q25 and q75 probes while preserving soma, q50 and q90 probes. This expands the retained unique port count from seven to nine.

## Required geometry and port roles

Nine unique SWC node IDs per morphology:
- soma
- basal q25/q50/q75/q90
- apical q25/q50/q75/q90

The basal-q75 and apical-q75 nodes are also the stimulation sources; the same node ID must not be duplicated in the electrical boundary set. The quantile helper fixes deterministic sort/tie behavior and tests known node IDs for each morphology.

## Model and input matrix

Four variants: four-shift order 56 control, six-shift order 28, order 56 and order 84. Ten frequency points through 10 kHz. Six 10 pA transients: soma/basal-q75/apical-q75 × 2/10 ms pulses.

Every configuration must emit 280 rows: 40 frequency-domain + 240 transient (nine ports plus aggregate). Six configurations yield 1,680 rows.

## Implementation and validation status — 2026-11-22

PR #3 is open: https://github.com/Nolane-x/Nghien-cuu/pull/3. The branch is synchronized with main (0 commits behind) and contains four changed paths: `amsn.ports`, the nine-port audit helper, the generalized Schur/PRIMA audit entry point, and morphology tests.

The canonical seven-port Import3D mapper remains unchanged. Nine-port enrichment is isolated in `human_prima_port_enrichment.py` and activated only in the dedicated workflow. The code verifies three sources, nine probe labels, nine unique SWC nodes, and nine unique electrical vertices after soma/wire normalization. Outputs use a `9port_` prefix.

Quantile node IDs have been independently recomputed using the repository's Python `round` semantics (ties-to-even); this corrects an initial expected-ID mismatch caused by using JavaScript's different half-rounding rule. Confirmed unique retained electrical ports:

- NMO_290988: `[1, 2070, 3355, 3784, 3814, 8831, 6897, 5920, 5164]`
- NMO_68174 cell1125: `[1, 5302, 3789, 1577, 2135, 7495, 11993, 9934, 10532]`
- NMO_68175 cell1204: `[1, 4716, 140, 3253, 2827, 12553, 12177, 7640, 7074]`

No nine-port numerical result is claimed yet. The dedicated workflow [44976224651](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651), Core CI [44976224745](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224745), and seven-port control [44976224560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224560) have been triggered on the preceding synchronized commit but were queued while many repository path-triggered workflows competed for runners. The current branch head is newer (`f1dcc735...`); its latest relevant Actions runs are also queued. Recheck the current head before relying on any result.

## Decision

Promote the enriched port basis only if apical-q90 transient error improves consistently and the other ports retain acceptable accuracy. Keep the seven-port baseline and full Hines canonical until evidence supports a different optional preset.
