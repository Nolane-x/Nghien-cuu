# Handoff — PRIMA apical/basal nine-port enrichment

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Base main commit:** 7cf8164b4d59deb62eef6b21b4703bb6456d392c  
**Work branch:** `research/prima-apical-port-enrichment-2026-11-22`

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

## Current status

Implementation has been added to the branch, but this checkpoint contains no claimed nine-port numerical result yet. The dedicated workflow runs six morphology × mesh jobs and stores artifacts with a `9port_` prefix. Inspect all six logs and raw CSVs before writing a result report.

## Decision

Promote the enriched port basis only if apical-q90 transient error improves consistently and the other ports retain acceptable accuracy. Keep the seven-port baseline and full Hines canonical until evidence supports a different optional preset.
