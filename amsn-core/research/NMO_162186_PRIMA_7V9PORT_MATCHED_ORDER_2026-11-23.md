# Matched 7-port / 9-port PRIMA validation on NMO_162186

**Date:** 23 November 2026  
**Morphology:** NMO_162186 / 770307286_transformed (Allen Cell Types)  
**SWC SHA-256:** \`a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc\`  
**Status:** validated — full matched 7-port/9-port holdout replay passed

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


## Validated numerical results — GitHub Actions run 45184621520

**Status:** passed on 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520  
**Artifact:** \`nmo162186-prima-7v9port-matched-order\`, ID \`14824270534\`  
**Artifact ZIP SHA-256:** \`56c2fc8a7aa8fbb4a5d1b58efa92a757d60c550b6b24eee71e21065a462806fe\`  
**Runtime:** Python 3.12.16, NEURON 9.0.2, NumPy 2.5.5

All setup, complete AMSN regression, source SWC SHA-256, Import3D/area/port preflight and matched-port unit-test steps passed. The replay ran for 422.61 s wall time, 518.23 s user CPU, with peak process RSS 187,160 KiB. All 36 models achieved their requested basis order and passed Cholesky passivity checks.

The runner completed every expected output:
- 36 model × port-count × order × parameter-scenario rows
- 324 frequency-matrix rows
- 1,728 per-port transient rows
- 756 matched pairs on the seven shared output nodes (378 per order)
- 216 q25-only observations (108 per order)
- 378 full-Hines shared-node consistency checks

### Matched shared outputs

| Basis order | 9-port worse | 9-port better | Ties | Median 9/7 transient-error ratio | Maximum 9/7 ratio |
|---:|---:|---:|---:|---:|---:|
| 112 | 377/378 | 1/378 | 0 | **8.1620×** | 395.2606× |
| 168 | 187/378 | 190/378 | 1 | **0.99999985×** | 1.00144× |

At order 112, adding the two q25 outputs is not a free improvement: the nine-port model is worse on 377 of 378 shared-output comparisons. The median transient error ratio is 8.16×. The absolute worst nine-port per-port transient NRMSE is still only 1.0655e−5%, but relative degradation is systematic and measurable.

At order 168, the same seven shared outputs are at numerical parity: the median ratio is 0.99999985× and the maximum ratio is 1.00144×. Improvements and regressions are balanced (190 versus 187), with one tie.

### Added q25 outputs

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 8.3418e−8% | 3.6711e−6% |
| 168 | 108 | 8.6262e−9% | **8.6226e−8%** |

The two added outputs are represented accurately at both orders against full Hines. However, only order 168 preserves near-parity on the original shared outputs. This reproduces the order-dependent conclusion from PR #6 on an independent morphology.

### High-frequency AC and numeric storage

| Port count | Order | Median Z residual at 10 kHz | Median Y residual at 10 kHz | Median numeric storage |
|---:|---:|---:|---:|---:|
| 7 | 112 | 4.6124e−6% | 9.5816e−6% | 6.4104 MB |
| 9 | 112 | 1.0498e−4% | 2.5063e−4% | 6.4104 MB |
| 7 | 168 | 2.7305e−10% | 7.2223e−10% | 9.7592 MB |
| 9 | 168 | 3.3864e−8% | 9.8754e−8% | 9.7592 MB |

Numeric storage here is the measured basis plus reduced G/C arrays, not whole-process RSS. At a matched order it is identical between the two port layouts in this implementation. The workflow's overall peak process RSS was 187,160 KiB; it is a single run and is not a controlled per-candidate memory benchmark.

The 378 shared-node full-Hines checks were exact: maximum absolute trace difference and relative L2 difference were both 0 for every matched reference. This establishes that the 7-port/9-port comparison did not change the underlying reference traces at shared nodes.

### Updated conditional recommendation

- **Seven outputs only:** keep 7-port order112 extended10kHz as the smaller high-frequency research candidate. The matched holdout also shows 7-port order168 has still lower AC residuals, at greater numeric storage.
- **Need basal-q25 and apical-q25:** choose 9-port order168 among the configurations tested. It preserves shared-output parity and has maximum q25 transient NRMSE below 1e−7%.
- **Do not choose 9-port order112** solely to obtain q25. It fits the q25 outputs well, but degrades the seven shared transient outputs systematically relative to 7-port order112.
- **Order84** remains the lower-memory alternative from the separate nine-port resource audit, but it was not part of this NMO_162186 matched-order run.
- Full Hines remains canonical; no production default or runtime path is changed.

### Scientific limits

NMO_162186 is one epilepsy surgical specimen with incomplete axon. This is a second protocol dimension on one external morphology, not a second morphology and not population-level validation. Results remain passive linear-RC numerical comparisons. They do not validate active channels, nonlinear synapses, plasticity or biological function.
