# PRIMA q25-versus-edge multilocation output-dual seed results

**Date:** 26 November 2026  
**Status:** accepted numerical archive; generated from paired case-level data  
**Basis order:** 224  
**Numerical workflow:** [run 45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978)  

## Executive summary

This experiment reverses the seed placement from the prior q25 study. It compares q25-target seeds with basal/apical edge seeds, while measuring the same 13 readouts in every schedule. The seven input ports, primal shifts, numerical integrator and full-Hines reference remain unchanged.

Every readout is measured in every schedule, but seed-target accuracy and unseeded transfer are reported separately. Q25_BOTH_10K seeds both q25 rows and tests edge transfer. BASAL_EDGES_10K and APICAL_EDGES_10K seed one branch's two edge rows and test q25 plus the opposite branch's edge rows. BOTH_EDGES_10K seeds all four edge rows and tests q25 transfer. No row used as a seed is counted as an unseeded transfer readout for that schedule.

## Seed strategy comparison

| Schedule | Seed labels | Requested sites | Accepted initial dual columns
median (min–max) | Seeded pairs | Seeded median ratio | Unseeded q25 pairs | q25 transfer median ratio | q25 transfer Δ (pp) | Unseeded edge pairs | edge transfer median ratio | edge transfer Δ (pp) | Shared median ratio | Shared median Δ (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q25_BOTH_10K | basal_q25, apical_q25 | 2 | 2 (2–2) | 864 | 0.004211 | 0 | — | — | 1,728 | 1.265 | +2.7403e-11 | 1.01 | +5.1452e-13 |
| BASAL_EDGES_10K | basal_q10, basal_q95 | 2 | 2 (2–2) | 864 | 0.003165 | 864 | 1.33 | +2.0502e-11 | 864 | 1.087 | +1.8588e-12 | 1.006 | +4.4147e-13 |
| APICAL_EDGES_10K | apical_q10, apical_q95 | 2 | 2 (2–2) | 864 | 0.008682 | 864 | 1.712 | +6.8412e-10 | 864 | 1.614 | +1.9283e-10 | 1.013 | +6.8435e-13 |
| BOTH_EDGES_10K | basal_q10, basal_q95, apical_q10, apical_q95 | 4 | 4 (4–4) | 1,728 | 0.007064 | 864 | 2.187 | +6.8666e-09 | 0 | — | — | 1.015 | +8.3224e-13 |

Requested seed sites are the predeclared coordinate count; accepted initial dual columns are the observed independent directions retained after reorthogonalization (median and min–max over 36 morphology/scenario cells). The primary resource-matched comparisons are Q25_BOTH_10K, BASAL_EDGES_10K and APICAL_EDGES_10K (two requested sites each). BOTH_EDGES_10K requests four sites and is a higher-budget coverage condition, not a location-only comparison. The q25/edge transfer columns exclude seed-target outputs for that schedule; a zero count is intentionally shown as no unseeded transfer readout.

Ratios compare candidate NRMSE with the exact paired D0 case. Negative percentage-point deltas indicate lower candidate error. Read both because D0 may be close to the numerical floor.

## Basis construction cost and conditioning

| Schedule | Requested seed sites | Accepted output-dual rank
median (min–max) | Basis build median (s) | Basis build P90 (s) | Max cond(G) | Max cond(C) | Max basis orthogonality error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D0_none | 0 | 0 (0–0) | 2.851 | 3.346 | 3.958e+06 | 333.2 | 1.5543e-15 |
| Q25_BOTH_10K | 2 | 2 (2–2) | 3.009 | 3.569 | 4.181e+06 | 337.5 | 1.7764e-15 |
| BASAL_EDGES_10K | 2 | 2 (2–2) | 3.013 | 3.56 | 4.142e+06 | 331.2 | 1.5543e-15 |
| APICAL_EDGES_10K | 2 | 2 (2–2) | 3.008 | 3.551 | 3.976e+06 | 335.6 | 1.4433e-15 |
| BOTH_EDGES_10K | 4 | 4 (4–4) | 2.909 | 3.443 | 3.515e+06 | 328.5 | 2.2204e-15 |

Build time and conditioning are summarized over the 36 morphology/scenario cells per schedule. Condition numbers are descriptive; the numerical acceptance gates still require positive-definite projected G/C and the stated orthogonality tolerance.

## Readout-specific seed-target and transfer results

| Output | Schedule | Readout status | Pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basal_q25 | Q25_BOTH_10K | Seed target | 432 | 0.002284 | 2.772e-08 | 1.929e-11 | -2.7522e-08 | 410/22 |
| basal_q25 | BASAL_EDGES_10K | Unseeded transfer | 432 | 1.45 | 2.772e-08 | 2.65e-08 | +5.7257e-11 | 161/271 |
| basal_q25 | APICAL_EDGES_10K | Unseeded transfer | 432 | 2.037 | 2.772e-08 | 3.758e-08 | +2.4888e-09 | 111/321 |
| basal_q25 | BOTH_EDGES_10K | Unseeded transfer | 432 | 2.414 | 2.772e-08 | 5.755e-08 | +1.1829e-08 | 83/349 |
| apical_q25 | Q25_BOTH_10K | Seed target | 432 | 0.006668 | 9.833e-09 | 2.363e-11 | -9.7265e-09 | 380/52 |
| apical_q25 | BASAL_EDGES_10K | Unseeded transfer | 432 | 1.273 | 9.833e-09 | 1.194e-08 | +1.0520e-11 | 170/262 |
| apical_q25 | APICAL_EDGES_10K | Unseeded transfer | 432 | 1.417 | 9.833e-09 | 1.606e-08 | +5.5205e-11 | 147/285 |
| apical_q25 | BOTH_EDGES_10K | Unseeded transfer | 432 | 1.987 | 9.833e-09 | 2.272e-08 | +3.7723e-09 | 112/320 |
| basal_q10 | Q25_BOTH_10K | Unseeded transfer | 432 | 0.9467 | 2.789e-08 | 2.143e-08 | -1.9951e-12 | 225/207 |
| basal_q10 | BASAL_EDGES_10K | Seed target | 432 | 0.002165 | 2.789e-08 | 1.907e-11 | -2.7804e-08 | 402/30 |
| basal_q10 | APICAL_EDGES_10K | Unseeded transfer | 432 | 1.546 | 2.789e-08 | 2.766e-08 | +3.2215e-11 | 168/264 |
| basal_q10 | BOTH_EDGES_10K | Seed target | 432 | 0.004487 | 2.789e-08 | 2.884e-11 | -2.7777e-08 | 405/27 |
| basal_q95 | Q25_BOTH_10K | Unseeded transfer | 432 | 1.577 | 2.839e-08 | 5.518e-08 | +3.0909e-09 | 137/295 |
| basal_q95 | BASAL_EDGES_10K | Seed target | 432 | 0.003483 | 2.839e-08 | 2.909e-11 | -2.8320e-08 | 405/27 |
| basal_q95 | APICAL_EDGES_10K | Unseeded transfer | 432 | 1.701 | 2.839e-08 | 4.804e-08 | +9.7928e-10 | 116/316 |
| basal_q95 | BOTH_EDGES_10K | Seed target | 432 | 0.005382 | 2.839e-08 | 3.846e-11 | -2.8258e-08 | 407/25 |
| apical_q10 | Q25_BOTH_10K | Unseeded transfer | 432 | 1.265 | 1.042e-08 | 1.48e-08 | +2.2945e-11 | 165/267 |
| apical_q10 | BASAL_EDGES_10K | Unseeded transfer | 432 | 1.181 | 1.042e-08 | 1.448e-08 | +4.2715e-12 | 191/241 |
| apical_q10 | APICAL_EDGES_10K | Seed target | 432 | 0.00711 | 1.042e-08 | 2.1e-11 | -1.0098e-08 | 367/65 |
| apical_q10 | BOTH_EDGES_10K | Seed target | 432 | 0.01216 | 1.042e-08 | 2.217e-11 | -9.8761e-09 | 382/50 |
| apical_q95 | Q25_BOTH_10K | Unseeded transfer | 432 | 1.295 | 1.014e-08 | 1.808e-08 | +1.3943e-11 | 173/259 |
| apical_q95 | BASAL_EDGES_10K | Unseeded transfer | 432 | 0.9709 | 1.014e-08 | 1.421e-08 | -9.4919e-13 | 222/210 |
| apical_q95 | APICAL_EDGES_10K | Seed target | 432 | 0.01103 | 1.014e-08 | 3.477e-11 | -1.0118e-08 | 367/65 |
| apical_q95 | BOTH_EDGES_10K | Seed target | 432 | 0.01188 | 1.014e-08 | 3.168e-11 | -1.0119e-08 | 382/50 |

## Results by morphology

| Morphology | Schedule | Readout family | Pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NMO_03524 | Q25_BOTH_10K | Seeded readouts | 216 | 0.7263 | 1.266e-11 | 9.645e-12 | -3.0137e-12 | 142/74 |
| NMO_03524 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — | — | — |
| NMO_03524 | Q25_BOTH_10K | Unseeded edge transfer | 432 | 0.9261 | 1.268e-11 | 1.197e-11 | -8.9057e-13 | 234/198 |
| NMO_03524 | Q25_BOTH_10K | Shared outputs | 756 | 0.9835 | 9.333e-12 | 9.148e-12 | -1.5656e-13 | 391/365 |
| NMO_03524 | BASAL_EDGES_10K | Seeded readouts | 216 | 0.3866 | 1.998e-11 | 9.961e-12 | -1.0232e-11 | 159/57 |
| NMO_03524 | BASAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.271 | 1.266e-11 | 1.589e-11 | +2.7333e-12 | 86/130 |
| NMO_03524 | BASAL_EDGES_10K | Unseeded edge transfer | 216 | 1.155 | 9.571e-12 | 9.78e-12 | +1.0374e-12 | 95/121 |
| NMO_03524 | BASAL_EDGES_10K | Shared outputs | 756 | 1.182 | 9.333e-12 | 9.724e-12 | +1.2507e-12 | 323/433 |
| NMO_03524 | APICAL_EDGES_10K | Seeded readouts | 216 | 1.173 | 9.571e-12 | 1.153e-11 | +1.2856e-12 | 86/130 |
| NMO_03524 | APICAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.15 | 1.266e-11 | 1.535e-11 | +1.5065e-12 | 91/125 |
| NMO_03524 | APICAL_EDGES_10K | Unseeded edge transfer | 216 | 1.532 | 1.998e-11 | 3.116e-11 | +6.0962e-12 | 69/147 |
| NMO_03524 | APICAL_EDGES_10K | Shared outputs | 756 | 1.164 | 9.333e-12 | 1.142e-11 | +1.3378e-12 | 295/461 |
| NMO_03524 | BOTH_EDGES_10K | Seeded readouts | 432 | 0.5111 | 1.268e-11 | 8.309e-12 | -6.4304e-12 | 280/152 |
| NMO_03524 | BOTH_EDGES_10K | Unseeded q25 transfer | 216 | 1.258 | 1.266e-11 | 1.499e-11 | +3.3429e-12 | 94/122 |
| NMO_03524 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — | — | — |
| NMO_03524 | BOTH_EDGES_10K | Shared outputs | 756 | 0.8896 | 9.333e-12 | 7.769e-12 | -9.6667e-13 | 398/358 |
| NMO_107159 | Q25_BOTH_10K | Seeded readouts | 216 | 0.003674 | 3.343e-08 | 1.368e-10 | -3.3224e-08 | 216/0 |
| NMO_107159 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — | — | — |
| NMO_107159 | Q25_BOTH_10K | Unseeded edge transfer | 432 | 1.519 | 3.705e-08 | 6.193e-08 | +1.2358e-08 | 118/314 |
| NMO_107159 | Q25_BOTH_10K | Shared outputs | 756 | 1.004 | 1.497e-10 | 1.514e-10 | +6.2961e-13 | 303/453 |
| NMO_107159 | BASAL_EDGES_10K | Seeded readouts | 216 | 0.002274 | 6.238e-08 | 1.651e-10 | -6.2273e-08 | 216/0 |
| NMO_107159 | BASAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.307 | 3.343e-08 | 4.028e-08 | +5.9869e-09 | 79/137 |
| NMO_107159 | BASAL_EDGES_10K | Unseeded edge transfer | 216 | 1.768 | 2.23e-08 | 4.076e-08 | +9.4145e-09 | 67/149 |
| NMO_107159 | BASAL_EDGES_10K | Shared outputs | 756 | 1.003 | 1.497e-10 | 1.514e-10 | +5.1638e-13 | 325/431 |
| NMO_107159 | APICAL_EDGES_10K | Seeded readouts | 216 | 0.006334 | 2.23e-08 | 1.105e-10 | -2.2196e-08 | 216/0 |
| NMO_107159 | APICAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.377 | 3.343e-08 | 4.539e-08 | +8.6401e-09 | 77/139 |
| NMO_107159 | APICAL_EDGES_10K | Unseeded edge transfer | 216 | 1.721 | 6.238e-08 | 1.199e-07 | +3.4584e-08 | 57/159 |
| NMO_107159 | APICAL_EDGES_10K | Shared outputs | 756 | 1.002 | 1.497e-10 | 1.496e-10 | +3.2785e-13 | 316/440 |
| NMO_107159 | BOTH_EDGES_10K | Seeded readouts | 432 | 0.003987 | 3.705e-08 | 1.54e-10 | -3.6862e-08 | 432/0 |
| NMO_107159 | BOTH_EDGES_10K | Unseeded q25 transfer | 216 | 1.832 | 3.343e-08 | 7.224e-08 | +2.8560e-08 | 38/178 |
| NMO_107159 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — | — | — |
| NMO_107159 | BOTH_EDGES_10K | Shared outputs | 756 | 1.003 | 1.497e-10 | 1.496e-10 | +4.6554e-13 | 318/438 |
| NMO_162186 | Q25_BOTH_10K | Seeded readouts | 216 | 0.00447 | 7.099e-09 | 2.517e-11 | -7.0737e-09 | 216/0 |
| NMO_162186 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — | — | — |
| NMO_162186 | Q25_BOTH_10K | Unseeded edge transfer | 432 | 1.614 | 8.993e-09 | 1.284e-08 | +4.7131e-10 | 136/296 |
| NMO_162186 | Q25_BOTH_10K | Shared outputs | 756 | 1.004 | 1.308e-11 | 1.31e-11 | +4.7976e-14 | 369/387 |
| NMO_162186 | BASAL_EDGES_10K | Seeded readouts | 216 | 0.003451 | 1.008e-08 | 2.769e-11 | -1.0042e-08 | 216/0 |
| NMO_162186 | BASAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.375 | 7.099e-09 | 9.321e-09 | +1.0485e-10 | 80/136 |
| NMO_162186 | BASAL_EDGES_10K | Unseeded edge transfer | 216 | 1.311 | 8.304e-09 | 1.002e-08 | +1.6375e-10 | 80/136 |
| NMO_162186 | BASAL_EDGES_10K | Shared outputs | 756 | 1.004 | 1.308e-11 | 1.298e-11 | +4.7696e-14 | 368/388 |
| NMO_162186 | APICAL_EDGES_10K | Seeded readouts | 216 | 0.01232 | 8.304e-09 | 5.298e-11 | -8.0469e-09 | 216/0 |
| NMO_162186 | APICAL_EDGES_10K | Unseeded q25 transfer | 216 | 2.272 | 7.099e-09 | 1.125e-08 | +1.5794e-09 | 36/180 |
| NMO_162186 | APICAL_EDGES_10K | Unseeded edge transfer | 216 | 2.301 | 1.008e-08 | 2.049e-08 | +9.5520e-10 | 52/164 |
| NMO_162186 | APICAL_EDGES_10K | Shared outputs | 756 | 1.018 | 1.308e-11 | 1.407e-11 | +2.5422e-13 | 337/419 |
| NMO_162186 | BOTH_EDGES_10K | Seeded readouts | 432 | 0.01597 | 8.993e-09 | 6.421e-11 | -8.9271e-09 | 432/0 |
| NMO_162186 | BOTH_EDGES_10K | Unseeded q25 transfer | 216 | 3.525 | 7.099e-09 | 2.066e-08 | +7.0114e-09 | 20/196 |
| NMO_162186 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — | — | — |
| NMO_162186 | BOTH_EDGES_10K | Shared outputs | 756 | 1.038 | 1.308e-11 | 1.349e-11 | +6.7406e-13 | 304/452 |
| NMO_163775 | Q25_BOTH_10K | Seeded readouts | 216 | 7.002e-05 | 2.383e-07 | 1.686e-11 | -2.3826e-07 | 216/0 |
| NMO_163775 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — | — | — |
| NMO_163775 | Q25_BOTH_10K | Unseeded edge transfer | 432 | 1.015 | 2.333e-07 | 2.146e-07 | +8.1358e-10 | 212/220 |
| NMO_163775 | Q25_BOTH_10K | Shared outputs | 756 | 1.331 | 1.222e-11 | 1.555e-11 | +3.6590e-12 | 247/509 |
| NMO_163775 | BASAL_EDGES_10K | Seeded readouts | 216 | 0.0001056 | 1.537e-07 | 1.897e-11 | -1.5371e-07 | 216/0 |
| NMO_163775 | BASAL_EDGES_10K | Unseeded q25 transfer | 216 | 1.397 | 2.383e-07 | 3.861e-07 | +5.6000e-08 | 86/130 |
| NMO_163775 | BASAL_EDGES_10K | Unseeded edge transfer | 216 | 0.5063 | 3.946e-07 | 2.131e-07 | -9.8149e-08 | 171/45 |
| NMO_163775 | BASAL_EDGES_10K | Shared outputs | 756 | 1.091 | 1.222e-11 | 1.512e-11 | +6.5903e-13 | 344/412 |
| NMO_163775 | APICAL_EDGES_10K | Seeded readouts | 216 | 3.987e-05 | 3.946e-07 | 2.062e-11 | -3.9455e-07 | 216/0 |
| NMO_163775 | APICAL_EDGES_10K | Unseeded q25 transfer | 216 | 2.564 | 2.383e-07 | 8.908e-07 | +4.3474e-07 | 54/162 |
| NMO_163775 | APICAL_EDGES_10K | Unseeded edge transfer | 216 | 1.035 | 1.537e-07 | 1.669e-07 | +2.5778e-09 | 106/110 |
| NMO_163775 | APICAL_EDGES_10K | Shared outputs | 756 | 1.274 | 1.222e-11 | 1.481e-11 | +2.5790e-12 | 292/464 |
| NMO_163775 | BOTH_EDGES_10K | Seeded readouts | 432 | 7.245e-05 | 2.333e-07 | 2.193e-11 | -2.3333e-07 | 432/0 |
| NMO_163775 | BOTH_EDGES_10K | Unseeded q25 transfer | 216 | 4.159 | 2.383e-07 | 1.168e-06 | +6.9695e-07 | 43/173 |
| NMO_163775 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — | — | — |
| NMO_163775 | BOTH_EDGES_10K | Shared outputs | 756 | 1.285 | 1.222e-11 | 1.865e-11 | +3.3591e-12 | 247/509 |

## Results by passive parameter scenario

| Scenario | Schedule | Readout family | Pairs | Median ratio | Median Δ (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- |
| nominal | Q25_BOTH_10K | Seeded readouts | 96 | 0.005986 | -1.9760e-08 | 76/20 |
| nominal | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| nominal | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.312 | +1.9041e-11 | 76/116 |
| nominal | BASAL_EDGES_10K | Seeded readouts | 96 | 0.003357 | -3.1942e-08 | 96/0 |
| nominal | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 0.8002 | -1.1595e-09 | 57/39 |
| nominal | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 0.9509 | -4.2511e-13 | 50/46 |
| nominal | APICAL_EDGES_10K | Seeded readouts | 96 | 0.01143 | -1.5333e-08 | 88/8 |
| nominal | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.54 | +4.7810e-11 | 36/60 |
| nominal | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.491 | +5.8261e-09 | 30/66 |
| nominal | BOTH_EDGES_10K | Seeded readouts | 192 | 0.007641 | -2.7068e-08 | 154/38 |
| nominal | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 2.101 | +1.1571e-08 | 4/92 |
| nominal | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Rm_minus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.002587 | -1.2291e-08 | 96/0 |
| Rm_minus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Rm_minus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.105 | +8.8302e-11 | 86/106 |
| Rm_minus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.002188 | -2.6198e-08 | 96/0 |
| Rm_minus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.569 | +1.1096e-09 | 25/71 |
| Rm_minus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 0.9239 | -1.3375e-12 | 50/46 |
| Rm_minus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.006654 | -5.2349e-09 | 72/24 |
| Rm_minus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.739 | +4.6370e-11 | 30/66 |
| Rm_minus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.289 | +1.8630e-11 | 38/58 |
| Rm_minus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.005773 | -1.5636e-08 | 192/0 |
| Rm_minus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 1.078 | +4.0223e-11 | 46/50 |
| Rm_minus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Rm_plus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.003367 | -1.8202e-08 | 88/8 |
| Rm_plus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Rm_plus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.044 | -1.1189e-13 | 96/96 |
| Rm_plus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.0013 | -3.7338e-08 | 87/9 |
| Rm_plus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.092 | +1.4312e-12 | 47/49 |
| Rm_plus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 1.424 | +2.8396e-12 | 39/57 |
| Rm_plus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.005874 | -1.4931e-08 | 80/16 |
| Rm_plus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.815 | +2.8334e-09 | 14/82 |
| Rm_plus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.186 | +4.9514e-12 | 43/53 |
| Rm_plus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.006699 | -2.4381e-08 | 155/37 |
| Rm_plus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 1.968 | +4.0531e-09 | 15/81 |
| Rm_plus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Cm_minus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.005433 | -8.2774e-09 | 79/17 |
| Cm_minus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Cm_minus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.549 | +4.9693e-10 | 53/139 |
| Cm_minus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.006484 | -1.5435e-08 | 96/0 |
| Cm_minus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.408 | +2.1579e-09 | 37/59 |
| Cm_minus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 0.7208 | -8.2194e-12 | 63/33 |
| Cm_minus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.00912 | -7.9680e-09 | 96/0 |
| Cm_minus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.896 | +5.0758e-10 | 36/60 |
| Cm_minus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.381 | +3.5152e-10 | 37/59 |
| Cm_minus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.008676 | -8.7248e-09 | 192/0 |
| Cm_minus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 3.441 | +1.1337e-08 | 21/75 |
| Cm_minus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Cm_plus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.001611 | -3.8660e-08 | 90/6 |
| Cm_plus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Cm_plus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.008 | +2.5779e-13 | 93/99 |
| Cm_plus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.001482 | -4.1411e-08 | 94/2 |
| Cm_plus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.468 | +1.1138e-11 | 40/56 |
| Cm_plus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 0.7619 | -2.9673e-12 | 57/39 |
| Cm_plus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.005819 | -1.7598e-08 | 88/8 |
| Cm_plus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.408 | +1.1191e-08 | 26/70 |
| Cm_plus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 2.017 | +9.3292e-10 | 16/80 |
| Cm_plus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.005418 | -3.3453e-08 | 187/5 |
| Cm_plus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 1.566 | +7.6635e-09 | 28/68 |
| Cm_plus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Ra_minus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.003279 | -1.7249e-08 | 82/14 |
| Ra_minus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Ra_minus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.53 | +8.2727e-11 | 56/136 |
| Ra_minus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.004291 | -2.3955e-08 | 80/16 |
| Ra_minus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.791 | +3.7357e-09 | 19/77 |
| Ra_minus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 1.273 | +2.9411e-12 | 47/49 |
| Ra_minus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.006579 | -1.1815e-08 | 72/24 |
| Ra_minus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 2.727 | +1.0179e-08 | 20/76 |
| Ra_minus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 2.536 | +1.2108e-10 | 29/67 |
| Ra_minus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.007747 | -1.9221e-08 | 152/40 |
| Ra_minus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 3.588 | +2.3549e-08 | 14/82 |
| Ra_minus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| Ra_plus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.009186 | -1.5145e-08 | 94/2 |
| Ra_plus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| Ra_plus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.241 | +1.3688e-09 | 74/118 |
| Ra_plus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.002259 | -4.1706e-08 | 96/0 |
| Ra_plus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 0.8309 | -5.6928e-12 | 53/43 |
| Ra_plus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 1.137 | +1.4566e-10 | 44/52 |
| Ra_plus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.01521 | -1.0709e-08 | 84/12 |
| Ra_plus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.702 | +1.0819e-09 | 31/65 |
| Ra_plus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.534 | +5.2217e-10 | 33/63 |
| Ra_plus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.006397 | -1.7349e-08 | 186/6 |
| Ra_plus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 2.382 | +1.9538e-08 | 15/81 |
| Ra_plus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| all_minus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.005643 | -8.7714e-09 | 96/0 |
| all_minus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| all_minus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.269 | +1.1154e-10 | 87/105 |
| all_minus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.003002 | -2.2344e-08 | 78/18 |
| all_minus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.186 | +3.8696e-12 | 41/55 |
| all_minus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 1.193 | +3.7778e-12 | 36/60 |
| all_minus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.01164 | -7.5646e-09 | 80/16 |
| all_minus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.079 | +1.6300e-12 | 44/52 |
| all_minus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.61 | +2.2692e-10 | 30/66 |
| all_minus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.006525 | -1.2872e-08 | 192/0 |
| all_minus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 1.737 | +2.5266e-09 | 36/60 |
| all_minus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |
| all_plus20 | Q25_BOTH_10K | Seeded readouts | 96 | 0.006539 | -1.4834e-08 | 89/7 |
| all_plus20 | Q25_BOTH_10K | Unseeded q25 transfer | 0 | — | — | — |
| all_plus20 | Q25_BOTH_10K | Unseeded edge transfer | 192 | 1.339 | +2.9051e-10 | 79/113 |
| all_plus20 | BASAL_EDGES_10K | Seeded readouts | 96 | 0.003502 | -4.4429e-08 | 84/12 |
| all_plus20 | BASAL_EDGES_10K | Unseeded q25 transfer | 96 | 1.667 | +5.5424e-09 | 12/84 |
| all_plus20 | BASAL_EDGES_10K | Unseeded edge transfer | 96 | 1.615 | +1.9013e-11 | 27/69 |
| all_plus20 | APICAL_EDGES_10K | Seeded readouts | 96 | 0.008776 | -2.0193e-08 | 74/22 |
| all_plus20 | APICAL_EDGES_10K | Unseeded q25 transfer | 96 | 2.082 | +6.6242e-09 | 21/75 |
| all_plus20 | APICAL_EDGES_10K | Unseeded edge transfer | 96 | 1.703 | +1.0921e-08 | 28/68 |
| all_plus20 | BOTH_EDGES_10K | Seeded readouts | 192 | 0.009709 | -2.9330e-08 | 166/26 |
| all_plus20 | BOTH_EDGES_10K | Unseeded q25 transfer | 96 | 3.524 | +6.9776e-09 | 16/80 |
| all_plus20 | BOTH_EDGES_10K | Unseeded edge transfer | 0 | — | — | — |

## Exact coverage and numerical gates

| Evidence | Expected | Verified |
| --- | --- | --- |
| Morphology/scenario workers | 36 | 36 |
| Case metrics | 28,080 | 28080 |
| Worker summaries | 4,680 | 4680 |
| Morphology/window summaries | 520 | 520 |
| Scenario/window summaries | 1,170 | 1170 |
| Pooled/window summaries | 130 | 130 |
| Finite-record DFT identities | 180 | 180 |
| Basis metadata rows | 180 | 180 |
| Unique case keys | 28,080 | 28080 |

- D0 exact production parity: True.
- All reduced G/C matrices Cholesky-positive: True.
- Every model reached order 224: True.
- Seven input ports unchanged: True.
- Maximum basis orthogonality error: 2.2204e-15.
- All DFT identities passed: True; max full-Hines residual 3.1661e-12; max reduced residual 3.6404e-13; tolerance 2.0e-08.
- Runtime: 3011.0 s wall; 36 isolated workers.

## Exact SWC node map

### NMO_03524 — NMO_03524_JacobsControl

- SWC SHA-256: `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`.
- Shared seven: 1, 583, 867, 367, 751, 866, 868.
- q25: basal 272; apical 864.

| Edge output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 631 | 112 | basal | 0.10 |
| basal_q95 | 702 | 801 | basal | 0.95 |
| apical_q10 | 863 | 7 | apical | 0.10 |
| apical_q95 | 869 | 70 | apical | 0.95 |

### NMO_107159 — NMO_107159_Tamas_human_pyramidal_Control

- SWC SHA-256: `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`.
- Shared seven: 1, 6363, 4735, 5564, 7023, 4301, 4623.
- q25: basal 6609; apical 4404.

| Edge output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 6739 | 351 | basal | 0.10 |
| basal_q95 | 7206 | 5039 | basal | 0.95 |
| apical_q10 | 4355 | 922 | apical | 0.10 |
| apical_q95 | 4820 | 6230 | apical | 0.95 |

### NMO_162186 — NMO_162186_AllenL23

- SWC SHA-256: `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`.
- Shared seven: 1, 2304, 4262, 2261, 515, 6608, 4180.
- q25: basal 2713; apical 4488.

| Edge output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 67 | 543 | basal | 0.10 |
| basal_q95 | 2167 | 4992 | basal | 0.95 |
| apical_q10 | 7171 | 1836 | apical | 0.10 |
| apical_q95 | 4769 | 7159 | apical | 0.95 |

### NMO_163775 — NMO_163775_Peng_mouse_Control

- SWC SHA-256: `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`.
- Shared seven: 1, 144, 3926, 4180, 40, 4104, 3948.
- q25: basal 224; apical 4096.

| Edge output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 7 | 21 | basal | 0.10 |
| basal_q95 | 94 | 261 | basal | 0.95 |
| apical_q10 | 3967 | 245 | apical | 0.10 |
| apical_q95 | 4042 | 1291 | apical | 0.95 |

## Scientific limits

- Four individual reconstructions are morphology strata, not a biological population.
- This is passive linear-RC model reduction only; active channels, spikes, synapses, plasticity, calcium signalling, metabolism and cognition are not modeled.
- q25/edge seed rows are measured in all schedules; only the rows not seeded by a given schedule are transfer readouts for that schedule.
- Relative ratios are secondary when D0 error is near the numerical floor; absolute percentage-point deltas must also be interpreted.
- Full Hines remains canonical. No production solver or default has changed.

## Archived sources

- Case metrics: `prima_q25_four_morphology_multilocation_output_dual_seed_order224_2026-11-26_case_metrics.csv`.
- Basis metadata: `prima_q25_four_morphology_multilocation_output_dual_seed_order224_2026-11-26_basis_metadata.json`.
- Numerical report: `prima_q25_four_morphology_multilocation_output_dual_seed_order224_2026-11-26_report.json`.
- Integrity manifest: `prima_q25_four_morphology_multilocation_output_dual_seed_order224_2026-11-26_manifest.json`.
