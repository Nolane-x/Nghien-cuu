# Matched 7-port / 9-port PRIMA validation on NMO_162186

**Date:** 23 November 2026  
**Morphology:** NMO_162186 / 770307286_transformed (Allen Cell Types)  
**SWC SHA-256:** \`a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc\`  
**Status:** implementation and CI added; numerical result pending the Actions replay

## Research question

PR #6 showed that at equal basis order the nine-port model can regress the seven shared outputs at orders 56 and 112, while order168 restores near-parity and resolves the added q25 outputs. PR #8 independently validated a seven-port shift/order sweep on NMO_162186, but did not cross the port-count dimension.

This experiment closes that gap by evaluating **both seven-port and nine-port reductions on the same held-out morphology**, at the same order, shifts, passive parameter scenario, source, pulse, and exact shared SWC output IDs.

## Matched design

- Morphology: NMO_162186, 7,287 SWC records, 7,278 AMSN electrical compartments.
- Provenance: epilepsy surgical specimen; dendrites complete, axon incomplete. This is one external morphology, not a healthy control or population sample.
- Port sets: canonical seven ports versus the same seven plus basal-q25 and apical-q25 (nine ports).
- Orders: 112 and 168.
- Shift distribution: identical six-shift extended10kHz set \`0, 100, 1,000, 3,000, 6,000, 10,000 Hz\`.
- Passive parameter scenarios: nominal, Rm ±20%, Cm ±20%, Ra ±20%, all three −20%, and all three +20% (nine scenarios).
- AC: 0.1 Hz to 10 kHz, nine frequencies; each port-count matrix compared with its own full Hines reference.
- Transients: soma/basal-q75/apical-q75 sources × 2/10 ms square pulses; 10 pA, 2 ms onset, 20 ms total, dt=0.1 ms.
- Shared output comparisons are paired by exact SWC node ID. The two q25 outputs are analyzed separately.

## Exact expected coverage

| Output | Rows |
|---|---:|
| Model × port-count × order × parameter-scenario | 36 |
| Frequency matrices | 324 |
| Per-port transient results | 1,728 |
| Seven shared outputs, paired 7-port vs 9-port | 756 |
| Two q25-only output results | 216 |
| Full-Hines shared-output consistency checks | 378 |

The runner fails closed if the two port layouts do not share the exact seven canonical SWC node IDs, if the q25-only roles are missing, if requested/achieved order differs, if C/G matrices fail Cholesky, or if any expected row is missing.

## What this test can decide

1. Whether the equal-order 7-vs-9-port behavior from PR #6 reproduces on NMO_162186.
2. Whether order168 continues to preserve near-parity on shared outputs on the holdout.
3. Whether the q25 output accuracy achieved on three earlier morphologies transfers to this independent morphology.
4. Whether order112 remains a viable lower-order nine-port compromise when evaluated on the same held-out specimen.

It does not validate active ion channels, nonlinear synapses, plasticity or biological completeness. The output is a passive linear-RC comparison against full Hines.

## Outputs

- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_report.json\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_models.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_frequency.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_transient.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_matched_shared.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_matched_summary.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_q25.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_q25_summary.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_hines_shared.csv\`
- \`NMO_162186_prima_7v9port_matched_order_2026-11-23_summary.csv\`

The workflow commits outputs to the branch and uploads a run artifact. Full Hines remains canonical; this experiment does not change production defaults.
