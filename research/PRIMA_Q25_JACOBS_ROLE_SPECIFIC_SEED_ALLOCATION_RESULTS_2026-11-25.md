# PRIMA q25 Jacobs role-specific output-dual seed allocation — results

**Date:** 25 November 2026 · **Status:** accepted research result  
**Workflow:** [45650388401](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401) — success  
**Result commit:** [bc0fa11dc136107d0cfee17ab14771f919dea81c](https://github.com/Nolane-x/Nghien-cuu/commit/bc0fa11dc136107d0cfee17ab14771f919dea81c)  
**Artifact:** [15041330718](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401/artifacts/15041330718), 254,430 bytes; ZIP SHA-256 \`a510ff14720304c498ff0c5cc474a974fb7dcf483449af0afad37c864a37161a\`

## Executive conclusion

The predeclared hypothesis that an apical-only dual seed would repair the Jacobs apical-q25 exception is **not supported**. APICAL-only 0/1k/10k schedules have scenario-median candidate/D0 ratios above one in both windows, improving the scenario median in only 2–3 of 9 scenarios. They also worsen the pooled median of all seven shared outputs in both windows.

Basal q25 responds differently. BASAL-only 0 Hz and 10 kHz improve the basal readout in most scenarios. BOTH_10K remains the best observed compromise: strong basal improvement, near-neutral apical q25, and the most favorable shared-output results. Do not change production defaults.

## Fixed protocol

\[
C\dot{x}+Gx=B_7u,\qquad y=L_9x,\qquad
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T.
\]

The original seven-port input selector \(B_7\) was held fixed. Output-dual columns were added only to the state basis; seven shared outputs and both q25 outputs were measured separately.

| Dimension | Fixed value |
|---|---|
| Morphology | Jacobs human control, NMO_03524; 869 SWC records |
| SWC SHA-256 | \`6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748\` |
| Source preflight | PASS |
| Scenarios | nominal; Rm ±20%; Cm ±20%; Ra ±20%; all ±20% (9 total) |
| Basis order / input ports / output rows | 224 / 7 / 9 |
| Primal input shifts | 0, 100, 1k, 3k, 6k, 10k Hz |
| Inputs | soma, basal-q75, apical-q75 |
| Pulses | 10 pA; onset 2 ms; widths 2 and 10 ms |
| dt / windows | 0.00625 ms / 20 and 40 ms |
| NEURON mesh cap | 0.5 µm |

Ten fixed schedules: D0_none; APICAL_0/1K/10K; BASAL_0/1K/10K; BOTH_1K/10K; BOTH_1K_10K.

## Verification

Workflow 45650388401 passed calculation, global verification, Git archival and artifact upload.

| Evidence | Expected = read back |
|---|---:|
| Scenario workers | 9 |
| Case metrics | 9,720 |
| Scenario summaries | 1,620 |
| Pooled summaries | 180 |
| Finite-record DFT identities | 45 |
| Basis/schedule metadata | 90 |
| Unique case keys | 9,720 |

D0 exactly matched production multishift PRIMA in all scenarios. Nominal D0 and BOTH_10K hashes and paired metrics matched the prior accepted sweep bit-for-bit. All models reached order224, retained seven input ports, and passed reduced G/C Cholesky checks.

- Max basis orthogonality error: \(1.77636\times10^{-15}\).
- 45/45 DFT identities passed tolerance \(2\times10^{-8}\).
- Max full-Hines identity relative residual: \(4.70924\times10^{-13}\).
- Max reduced identity relative residual: \(3.61286\times10^{-13}\).
- Runtime: Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2; one-thread Haswell OpenBLAS; active NumPy dispatch X86_V3 + baseline(X86_V2).
- Wall time 392.38 s; summed worker time 388.74 s.

## Apical q25

“Scenario median” = median of nine scenario-level median candidate/D0 ratios. “Pooled median” = median across 54 matched source/pulse cases. “Better” = cases with candidate NRMSE below D0.

| Schedule | Scenario median ratio (20/40 ms) | Pooled median ratio (20/40 ms) | Better cases (20/40 ms) |
|---|---:|---:|---:|
| APICAL_0 | 1.197 / 1.218 | 1.415 / 1.388 | 18 / 17 of 54 |
| APICAL_1K | 1.554 / 1.125 | 1.194 / 1.256 | 20 / 21 |
| APICAL_10K | 1.207 / 1.388 | 1.207 / 1.301 | 21 / 20 |
| BASAL_0 | 1.095 / 1.096 | 1.127 / 1.084 | 22 / 22 |
| BASAL_1K | 1.112 / 1.409 | 1.430 / 1.462 | 18 / 17 |
| BASAL_10K | 1.062 / 1.159 | 1.078 / 1.159 | 24 / 21 |
| BOTH_1K | 1.077 / 1.062 | 1.241 / 1.232 | 17 / 17 |
| BOTH_10K | 1.035 / 1.049 | 0.979 / 1.001 | 29 / 27 |
| BOTH_1K_10K | 1.260 / 1.373 | 1.364 / 1.483 | 8 / 8 |

No APICAL-only schedule improves the apical scenario median in more than three of nine scenarios. BOTH_10K is closest to neutral, not a robust apical improvement.

D0 apical q25 NRMSE is already at the numerical floor:

| Window | Median | P90 | Maximum |
|---|---:|---:|---:|
| 20 ms | \(8.8483\times10^{-12}\%\) | \(1.3140\times10^{-11}\%\) | \(1.7020\times10^{-11}\%\) |
| 40 ms | \(1.1511\times10^{-11}\%\) | \(1.5842\times10^{-11}\%\) | \(1.8376\times10^{-11}\%\) |

BOTH_10K's pooled median absolute apical error delta is only \(-2.40\times10^{-13}\) percentage points at 20 ms and \(+4.89\times10^{-14}\) at 40 ms. Ratios here are numerically fragile and do not support practical improvement claims.

## Basal q25

| Schedule | Scenario median ratio (20/40 ms) | Pooled median ratio (20/40 ms) | Better cases (20/40 ms) |
|---|---:|---:|---:|
| APICAL_0 | 1.202 / 1.224 | 1.220 / 1.324 | 20 / 18 of 54 |
| APICAL_1K | 1.195 / 1.298 | 1.222 / 1.266 | 20 / 20 |
| APICAL_10K | 1.234 / 1.226 | 1.215 / 1.220 | 19 / 19 |
| BASAL_0 | 0.555 / 0.647 | 0.466 / 0.613 | 41 / 41 |
| BASAL_1K | 0.747 / 0.767 | 0.563 / 0.612 | 36 / 37 |
| BASAL_10K | 0.676 / 0.606 | 0.621 / 0.644 | 40 / 38 |
| BOTH_1K | 0.785 / 0.808 | 0.455 / 0.528 | 40 / 37 |
| BOTH_10K | 0.540 / 0.525 | 0.449 / 0.464 | 43 / 43 |
| BOTH_1K_10K | 0.822 / 0.956 | 0.737 / 0.894 | 33 / 34 |

BASAL_0 and BASAL_10K are lower-cost basal-focused options. BOTH_10K gives the strongest pooled basal result: 43/54 better cases in both windows. Its pooled median absolute basal error delta is \(-8.06\times10^{-12}\) and \(-8.15\times10^{-12}\) percentage points (20/40 ms).

## Seven shared outputs

Each value is the median of the seven output-specific pooled candidate/D0 medians; counts show outputs whose individual median ratio is below one.

| Schedule | Median shared ratio (20/40 ms) | Improved shared outputs (20/40 ms) |
|---|---:|---:|
| APICAL_0 | 1.416 / 1.389 | 0 / 0 of 7 |
| APICAL_1K | 1.194 / 1.255 | 0 / 0 |
| APICAL_10K | 1.208 / 1.300 | 0 / 0 |
| BASAL_0 | 1.127 / 1.084 | 0 / 0 |
| BASAL_1K | 1.430 / 1.463 | 0 / 0 |
| BASAL_10K | 1.078 / 1.162 | 0 / 0 |
| BOTH_1K | 1.242 / 1.232 | 0 / 0 |
| BOTH_10K | 0.979 / 1.002 | 7 / 2 |
| BOTH_1K_10K | 1.363 / 1.486 | 0 / 0 |

APICAL-only schedules worsen all seven shared-output medians. BOTH_10K is the only schedule with all seven medians improved at 20 ms; it is near-neutral at 40 ms.

## Decision and limits

- Reject APICAL-only dual seeding as a fix for Jacobs apical q25.
- Keep BOTH_10K as the best current **research** compromise; retain BASAL_0 and BASAL_10K as basal-focused alternatives.
- Do not chase apical relative ratios until an absolute error target and numerical noise floor are specified.
- This is one human control reconstruction with nine passive parameter settings, not a biological population. The model is passive linear-RC only: active channels, action potentials, synapses, plasticity, calcium signalling and biological validity were not tested. Full Hines remains canonical; no production solver or default PRIMA order changed.

## Raw evidence

All accepted files are under \`amsn-core/results/\`, stem \`prima_q25_jacobs_role_specific_seed_allocation_order224_2026-11-25\`: case metrics, scenario summary, pooled summary, finite-DFT identity, basis metadata, report and manifest.
