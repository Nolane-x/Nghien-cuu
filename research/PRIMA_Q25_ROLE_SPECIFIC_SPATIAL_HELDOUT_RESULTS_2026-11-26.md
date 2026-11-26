# PRIMA q25 role-specific seeds — held-out spatial generalization results

**Date:** 26 November 2026  
**Status:** accepted numerical result; generated from case-level archive  
**Basis order:** 224  
**Source numerical workflow:** [run 45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271)  

## Executive summary

This study compares D0 with basal-only, apical-only and joint 10-kHz q25 output-dual seeds at four dendritic observation sites that were not used to construct the dual seeds. The canonical seven input ports remain unchanged. Results below are recomputed from paired case-level NRMSE values, not from ratios of aggregate medians.

A pooled median error ratio below 1 is not sufficient evidence of spatial generalization by itself. Interpret the four held-out labels and four morphology strata separately, and read absolute percentage-point deltas alongside ratios when D0 is near the numerical floor.

Across all four unseeded spatial locations and both windows, each candidate schedule has 1,728 paired cases. Only 3/12 held-out-label-by-schedule combinations have a pooled median candidate/D0 ratio below 1. This is a mixed pattern, not consistent evidence of broad spatial transfer; the morphology-stratified and scenario-stratified results below remain decisive.

## Spatial generalization verdict (descriptive, not a significance test)

| Schedule | Held-out pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- |
| BASAL_10K | 1,728 | 0.9789 | 1.914e-08 | 1.692e-08 | -4.4300e-13 | 879/849 |
| APICAL_10K | 1,728 | 1.181 | 1.914e-08 | 2.087e-08 | +5.8267e-12 | 742/986 |
| BOTH_10K | 1,728 | 1.265 | 1.914e-08 | 2.285e-08 | +2.7403e-11 | 700/1028 |

The q25 seed targets are summarized separately. Strong q25-only gains alongside mixed unseeded-location results indicate target-local basis specialization rather than demonstrated broad spatial generalization.

| Schedule | q25 pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- |
| BASAL_10K | 864 | 0.4407 | 1.491e-08 | 5.933e-11 | -9.9415e-10 | 618/246 |
| APICAL_10K | 864 | 0.604 | 1.491e-08 | 7.508e-11 | -2.0115e-09 | 561/303 |
| BOTH_10K | 864 | 0.004211 | 1.491e-08 | 2.053e-11 | -1.4867e-08 | 790/74 |

## Held-out spatial aggregate by morphology

| Morphology | Schedule | Pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NMO_03524 | BASAL_10K | 432 | 1.215 | 1.268e-11 | 1.57e-11 | +3.4772e-12 | 153/279 |
| NMO_03524 | APICAL_10K | 432 | 1.242 | 1.268e-11 | 1.528e-11 | +2.4845e-12 | 165/267 |
| NMO_03524 | BOTH_10K | 432 | 0.9261 | 1.268e-11 | 1.197e-11 | -8.9057e-13 | 234/198 |
| NMO_107159 | BASAL_10K | 432 | 1.045 | 3.705e-08 | 4.445e-08 | +6.1989e-10 | 205/227 |
| NMO_107159 | APICAL_10K | 432 | 1.259 | 3.705e-08 | 4.393e-08 | +4.0134e-09 | 180/252 |
| NMO_107159 | BOTH_10K | 432 | 1.519 | 3.705e-08 | 6.193e-08 | +1.2358e-08 | 118/314 |
| NMO_162186 | BASAL_10K | 432 | 1.08 | 8.993e-09 | 1.137e-08 | +2.9605e-11 | 196/236 |
| NMO_162186 | APICAL_10K | 432 | 1.333 | 8.993e-09 | 1.177e-08 | +1.4966e-10 | 160/272 |
| NMO_162186 | BOTH_10K | 432 | 1.614 | 8.993e-09 | 1.284e-08 | +4.7131e-10 | 136/296 |
| NMO_163775 | BASAL_10K | 432 | 0.4748 | 2.333e-07 | 1.213e-07 | -6.4286e-08 | 325/107 |
| NMO_163775 | APICAL_10K | 432 | 0.9065 | 2.333e-07 | 1.771e-07 | -5.9222e-09 | 237/195 |
| NMO_163775 | BOTH_10K | 432 | 1.015 | 2.333e-07 | 2.146e-07 | +8.1358e-10 | 212/220 |

This morphology aggregate pools only the four declared held-out locations and both windows within each reconstruction; each row contains 432 paired cases. It is descriptive and is not a population estimate.

## Held-out location summary across both windows

| Held-out output | Schedule | Pairs | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| basal_q10 | BASAL_10K | 432 | 0.8561 | 2.789e-08 | 1.745e-08 | -1.9354e-11 | 236/196 |
| basal_q95 | BASAL_10K | 432 | 1.092 | 2.839e-08 | 4.167e-08 | +5.8422e-12 | 197/235 |
| apical_q10 | BASAL_10K | 432 | 1.029 | 1.042e-08 | 1.188e-08 | +7.3497e-13 | 210/222 |
| apical_q95 | BASAL_10K | 432 | 0.9224 | 1.014e-08 | 1.11e-08 | -2.4993e-12 | 236/196 |
| basal_q10 | APICAL_10K | 432 | 1.117 | 2.789e-08 | 2.816e-08 | +1.5835e-11 | 180/252 |
| basal_q95 | APICAL_10K | 432 | 1.231 | 2.839e-08 | 3.412e-08 | +1.5065e-11 | 174/258 |
| apical_q10 | APICAL_10K | 432 | 1.093 | 1.042e-08 | 1.384e-08 | +1.2950e-12 | 209/223 |
| apical_q95 | APICAL_10K | 432 | 1.235 | 1.014e-08 | 1.288e-08 | +5.2171e-12 | 179/253 |
| basal_q10 | BOTH_10K | 432 | 0.9467 | 2.789e-08 | 2.143e-08 | -1.9951e-12 | 225/207 |
| basal_q95 | BOTH_10K | 432 | 1.577 | 2.839e-08 | 5.518e-08 | +3.0909e-09 | 137/295 |
| apical_q10 | BOTH_10K | 432 | 1.265 | 1.042e-08 | 1.48e-08 | +2.2945e-11 | 165/267 |
| apical_q95 | BOTH_10K | 432 | 1.295 | 1.014e-08 | 1.808e-08 | +1.3943e-11 | 173/259 |

All comparisons are paired at the morphology, passive scenario, window, input source and pulse-width level. Counts are descriptive; no inferential p-value or population-level claim is made. Several D0 medians are extremely small, so ratios can be unstable and absolute NRMSE and percentage-point deltas must be read together.

## Fixed protocol

- Morphologies: 4 individual reconstructions; NMO_163775, NMO_107159, NMO_03524, NMO_162186.
- Passive parameter scenarios: 9.
- Basis order: 224; seven fixed input ports; 13 observed outputs.
- Primal input shifts (Hz): 0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0.
- Sources: soma, basal_q75, apical_q75; pulse widths: 2.0, 10.0 ms.
- Timestep: 0.00625 ms; windows: 20.0, 40.0 ms.
- q25 dual-seed schedules: D0_none, BASAL_10K, APICAL_10K, BOTH_10K.

## Exact coverage and numerical gates

| Evidence | Expected | Verified |
| --- | --- | --- |
| Morphology/scenario workers | 36 | 36 |
| Case metrics | 22,464 | 22464 |
| Worker summaries | 3,744 | 3744 |
| Morphology/window summaries | 416 | 416 |
| Scenario/window summaries | 936 | 936 |
| Pooled/window summaries | 104 | 104 |
| Finite-record DFT identities | 144 | 144 |
| Basis metadata rows | 144 | 144 |
| Unique case keys | 22,464 | 22464 |

- D0 exact production parity: True.
- All reduced G/C matrices Cholesky-positive: True.
- All models reached order 224: True.
- Seven input ports unchanged: True.
- Maximum basis orthogonality error: 1.9984e-15.
- All DFT identities passed: True; maximum full-Hines residual 3.1661e-12; maximum reduced residual 3.5918e-13; tolerance 2.0e-08.
- Runtime: 1667.5 s wall; 36 isolated workers.

## Pooled q25 and spatial held-out readouts

| Output | Window ms | Schedule | Cases | Median ratio | P90 ratio | Worst ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basal_q10 | 20 | D0_none | 216 | 1 | 1 | 1 | 2.523e-08 | 2.523e-08 | +0.0000e+00 | 0/0 |
| basal_q10 | 20 | BASAL_10K | 216 | 0.8024 | 2.361 | 11.06 | 2.523e-08 | 1.516e-08 | -6.2713e-11 | 124/92 |
| basal_q10 | 20 | APICAL_10K | 216 | 1.105 | 2.859 | 11.91 | 2.523e-08 | 2.175e-08 | +7.6606e-12 | 95/121 |
| basal_q10 | 20 | BOTH_10K | 216 | 0.9553 | 3.17 | 8.547 | 2.523e-08 | 1.753e-08 | -1.4165e-12 | 112/104 |
| basal_q10 | 40 | D0_none | 216 | 1 | 1 | 1 | 3.239e-08 | 3.239e-08 | +0.0000e+00 | 0/0 |
| basal_q10 | 40 | BASAL_10K | 216 | 0.8911 | 2.373 | 6.888 | 3.239e-08 | 2.089e-08 | -5.5503e-12 | 112/104 |
| basal_q10 | 40 | APICAL_10K | 216 | 1.17 | 2.555 | 8.507 | 3.239e-08 | 3.792e-08 | +2.5414e-11 | 85/131 |
| basal_q10 | 40 | BOTH_10K | 216 | 0.9416 | 3.116 | 8.424 | 3.239e-08 | 3.188e-08 | -3.1914e-12 | 113/103 |
| basal_q95 | 20 | D0_none | 216 | 1 | 1 | 1 | 2.603e-08 | 2.603e-08 | +0.0000e+00 | 0/0 |
| basal_q95 | 20 | BASAL_10K | 216 | 1.14 | 3.362 | 11.38 | 2.603e-08 | 3.36e-08 | +1.1593e-11 | 93/123 |
| basal_q95 | 20 | APICAL_10K | 216 | 1.175 | 3.567 | 8.626 | 2.603e-08 | 3.046e-08 | +1.0423e-11 | 90/126 |
| basal_q95 | 20 | BOTH_10K | 216 | 1.571 | 6.021 | 13.53 | 2.603e-08 | 4.342e-08 | +3.3703e-09 | 66/150 |
| basal_q95 | 40 | D0_none | 216 | 1 | 1 | 1 | 3.615e-08 | 3.615e-08 | +0.0000e+00 | 0/0 |
| basal_q95 | 40 | BASAL_10K | 216 | 1.038 | 3.546 | 11.38 | 3.615e-08 | 4.579e-08 | +1.8090e-12 | 104/112 |
| basal_q95 | 40 | APICAL_10K | 216 | 1.291 | 3.768 | 8.829 | 3.615e-08 | 5.156e-08 | +1.8652e-11 | 84/132 |
| basal_q95 | 40 | BOTH_10K | 216 | 1.604 | 5.456 | 15.25 | 3.615e-08 | 7.855e-08 | +1.8270e-09 | 71/145 |
| apical_q10 | 20 | D0_none | 216 | 1 | 1 | 1 | 8.401e-09 | 8.401e-09 | +0.0000e+00 | 0/0 |
| apical_q10 | 20 | BASAL_10K | 216 | 0.9698 | 2.819 | 13.91 | 8.401e-09 | 1.081e-08 | -9.5636e-13 | 111/105 |
| apical_q10 | 20 | APICAL_10K | 216 | 0.9759 | 2.864 | 10.17 | 8.401e-09 | 9.155e-09 | -1.3191e-13 | 109/107 |
| apical_q10 | 20 | BOTH_10K | 216 | 1.192 | 3.878 | 11.48 | 8.401e-09 | 1.143e-08 | +1.1884e-11 | 88/128 |
| apical_q10 | 40 | D0_none | 216 | 1 | 1 | 1 | 1.305e-08 | 1.305e-08 | +0.0000e+00 | 0/0 |
| apical_q10 | 40 | BASAL_10K | 216 | 1.064 | 3.233 | 13.91 | 1.305e-08 | 1.353e-08 | +3.7253e-12 | 99/117 |
| apical_q10 | 40 | APICAL_10K | 216 | 1.182 | 3.189 | 7.681 | 1.305e-08 | 1.895e-08 | +2.9816e-12 | 100/116 |
| apical_q10 | 40 | BOTH_10K | 216 | 1.33 | 4.487 | 11.48 | 1.305e-08 | 1.837e-08 | +1.1134e-10 | 77/139 |
| apical_q95 | 20 | D0_none | 216 | 1 | 1 | 1 | 1.023e-08 | 1.023e-08 | +0.0000e+00 | 0/0 |
| apical_q95 | 20 | BASAL_10K | 216 | 0.8772 | 2.549 | 13.74 | 1.023e-08 | 1.091e-08 | -3.1310e-12 | 124/92 |
| apical_q95 | 20 | APICAL_10K | 216 | 1.208 | 3.048 | 11.23 | 1.023e-08 | 1.104e-08 | +4.8704e-12 | 90/126 |
| apical_q95 | 20 | BOTH_10K | 216 | 1.279 | 4.834 | 9.574 | 1.023e-08 | 1.789e-08 | +8.8099e-12 | 89/127 |
| apical_q95 | 40 | D0_none | 216 | 1 | 1 | 1 | 1.009e-08 | 1.009e-08 | +0.0000e+00 | 0/0 |
| apical_q95 | 40 | BASAL_10K | 216 | 0.9639 | 2.796 | 10.35 | 1.009e-08 | 1.225e-08 | -5.5664e-13 | 112/104 |
| apical_q95 | 40 | APICAL_10K | 216 | 1.321 | 3.243 | 11.22 | 1.009e-08 | 1.388e-08 | +6.2744e-12 | 89/127 |
| apical_q95 | 40 | BOTH_10K | 216 | 1.304 | 4.759 | 20.33 | 1.009e-08 | 1.828e-08 | +2.1288e-11 | 84/132 |
| basal_q25 | 20 | D0_none | 216 | 1 | 1 | 1 | 2.142e-08 | 2.142e-08 | +0.0000e+00 | 0/0 |
| basal_q25 | 20 | BASAL_10K | 216 | 0.002518 | 0.8055 | 7.796 | 2.142e-08 | 1.752e-11 | -2.1231e-08 | 202/14 |
| basal_q25 | 20 | APICAL_10K | 216 | 1.032 | 2.804 | 18.09 | 2.142e-08 | 1.607e-08 | +1.3253e-12 | 105/111 |
| basal_q25 | 20 | BOTH_10K | 216 | 0.00257 | 0.6611 | 9.695 | 2.142e-08 | 1.812e-11 | -2.1233e-08 | 205/11 |
| basal_q25 | 40 | D0_none | 216 | 1 | 1 | 1 | 3.32e-08 | 3.32e-08 | +0.0000e+00 | 0/0 |
| basal_q25 | 40 | BASAL_10K | 216 | 0.001906 | 0.8414 | 8.901 | 3.32e-08 | 2.067e-11 | -3.3181e-08 | 199/17 |
| basal_q25 | 40 | APICAL_10K | 216 | 1.158 | 2.8 | 10.5 | 3.32e-08 | 3.182e-08 | +9.2655e-12 | 91/125 |
| basal_q25 | 40 | BOTH_10K | 216 | 0.001865 | 0.6212 | 8.598 | 3.32e-08 | 2.035e-11 | -3.3169e-08 | 205/11 |
| apical_q25 | 20 | D0_none | 216 | 1 | 1 | 1 | 8.853e-09 | 8.853e-09 | +0.0000e+00 | 0/0 |
| apical_q25 | 20 | BASAL_10K | 216 | 0.9517 | 3.818 | 13.71 | 8.853e-09 | 1.011e-08 | -9.9285e-13 | 114/102 |
| apical_q25 | 20 | APICAL_10K | 216 | 0.005453 | 1.382 | 10.26 | 8.853e-09 | 1.802e-11 | -8.6790e-09 | 183/33 |
| apical_q25 | 20 | BOTH_10K | 216 | 0.006284 | 1.075 | 8.66 | 8.853e-09 | 2.108e-11 | -8.6813e-09 | 191/25 |
| apical_q25 | 40 | D0_none | 216 | 1 | 1 | 1 | 1.156e-08 | 1.156e-08 | +0.0000e+00 | 0/0 |
| apical_q25 | 40 | BASAL_10K | 216 | 1.034 | 4.131 | 13.97 | 1.156e-08 | 1.26e-08 | +9.5075e-13 | 103/113 |
| apical_q25 | 40 | APICAL_10K | 216 | 0.005769 | 1.415 | 5.246 | 1.156e-08 | 2.164e-11 | -1.1554e-08 | 182/34 |
| apical_q25 | 40 | BOTH_10K | 216 | 0.006842 | 1.127 | 6.875 | 1.156e-08 | 2.597e-11 | -1.1557e-08 | 189/27 |

The ratio for each case is candidate NRMSE divided by the D0 NRMSE for the same morphology, scenario, source, pulse width, window and output. Δ is candidate minus D0 in NRMSE percentage points. Negative Δ is better. Both median absolute NRMSE values are shown so very small D0 denominators cannot be hidden by a large relative ratio.

## Output-role aggregate

| Window ms | Schedule | Output role | Cases | Median ratio | P90 ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | BASAL_10K | heldout_spatial_output | 864 | 0.9681 | 2.803 | 1.526e-08 | 1.446e-08 | -1.0786e-12 | 452/412 |
| 20 | BASAL_10K | q25_output | 432 | 0.4351 | 2.593 | 1.365e-08 | 5.291e-11 | -1.1061e-09 | 316/116 |
| 20 | BASAL_10K | shared_output | 1512 | 1.009 | 2.387 | 1.328e-11 | 1.55e-11 | +3.0697e-13 | 685/827 |
| 20 | APICAL_10K | heldout_spatial_output | 864 | 1.118 | 3.109 | 1.526e-08 | 1.733e-08 | +4.3782e-12 | 384/480 |
| 20 | APICAL_10K | q25_output | 432 | 0.5863 | 1.906 | 1.365e-08 | 7.241e-11 | -2.5649e-09 | 288/144 |
| 20 | APICAL_10K | shared_output | 1512 | 1.009 | 2.493 | 1.328e-11 | 1.535e-11 | +4.5086e-13 | 676/836 |
| 20 | BOTH_10K | heldout_spatial_output | 864 | 1.239 | 4.522 | 1.526e-08 | 1.957e-08 | +2.0880e-11 | 355/509 |
| 20 | BOTH_10K | q25_output | 432 | 0.004321 | 0.9136 | 1.365e-08 | 1.927e-11 | -1.3628e-08 | 396/36 |
| 20 | BOTH_10K | shared_output | 1512 | 1.008 | 2.111 | 1.328e-11 | 1.496e-11 | +3.9818e-13 | 669/843 |
| 40 | BASAL_10K | heldout_spatial_output | 864 | 1.009 | 3.134 | 2.214e-08 | 1.911e-08 | +2.3351e-13 | 427/437 |
| 40 | BASAL_10K | q25_output | 432 | 0.4608 | 2.674 | 1.688e-08 | 6.293e-11 | -5.9603e-10 | 302/130 |
| 40 | BASAL_10K | shared_output | 1512 | 1.013 | 2.363 | 1.513e-11 | 1.77e-11 | +6.6894e-13 | 632/880 |
| 40 | APICAL_10K | heldout_spatial_output | 864 | 1.243 | 3.266 | 2.214e-08 | 2.468e-08 | +8.6696e-12 | 358/506 |
| 40 | APICAL_10K | q25_output | 432 | 0.6671 | 2.075 | 1.688e-08 | 7.797e-11 | -4.9054e-10 | 273/159 |
| 40 | APICAL_10K | shared_output | 1512 | 1.006 | 2.331 | 1.513e-11 | 1.927e-11 | +4.1530e-13 | 671/841 |
| 40 | BOTH_10K | heldout_spatial_output | 864 | 1.297 | 4.573 | 2.214e-08 | 3.087e-08 | +3.0043e-11 | 345/519 |
| 40 | BOTH_10K | q25_output | 432 | 0.003906 | 0.8999 | 1.688e-08 | 2.242e-11 | -1.6716e-08 | 394/38 |
| 40 | BOTH_10K | shared_output | 1512 | 1.011 | 1.996 | 1.513e-11 | 1.752e-11 | +6.2134e-13 | 641/871 |

## Held-out results by morphology

| Morphology | Held-out output | Window ms | Schedule | Median ratio | P90 ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NMO_03524 | basal_q10 | 20 | BASAL_10K | 1.337 | 4.636 | 1.66e-11 | 2.081e-11 | +8.4227e-12 | 17/37 |
| NMO_03524 | basal_q10 | 20 | APICAL_10K | 1.542 | 4.228 | 1.66e-11 | 2.362e-11 | +5.7120e-12 | 18/36 |
| NMO_03524 | basal_q10 | 20 | BOTH_10K | 0.9277 | 3.234 | 1.66e-11 | 1.933e-11 | -1.0129e-12 | 30/24 |
| NMO_03524 | basal_q10 | 40 | BASAL_10K | 1.357 | 4.611 | 1.939e-11 | 2.592e-11 | +8.9881e-12 | 12/42 |
| NMO_03524 | basal_q10 | 40 | APICAL_10K | 1.533 | 3.847 | 1.939e-11 | 2.704e-11 | +7.3480e-12 | 17/37 |
| NMO_03524 | basal_q10 | 40 | BOTH_10K | 0.928 | 3.125 | 1.939e-11 | 2.102e-11 | -1.2398e-12 | 29/25 |
| NMO_03524 | basal_q95 | 20 | BASAL_10K | 1.191 | 4.168 | 2.007e-11 | 2.615e-11 | +5.2160e-12 | 18/36 |
| NMO_03524 | basal_q95 | 20 | APICAL_10K | 1.03 | 2.107 | 2.007e-11 | 2.67e-11 | +1.0541e-12 | 25/29 |
| NMO_03524 | basal_q95 | 20 | BOTH_10K | 0.8712 | 3.75 | 2.007e-11 | 2.399e-11 | -1.7445e-12 | 31/23 |
| NMO_03524 | basal_q95 | 40 | BASAL_10K | 1.242 | 4.365 | 2.127e-11 | 3.247e-11 | +6.5594e-12 | 16/38 |
| NMO_03524 | basal_q95 | 40 | APICAL_10K | 1.132 | 2.285 | 2.127e-11 | 2.741e-11 | +3.1532e-12 | 24/30 |
| NMO_03524 | basal_q95 | 40 | BOTH_10K | 0.8262 | 3.734 | 2.127e-11 | 2.714e-11 | -3.0754e-12 | 32/22 |
| NMO_03524 | apical_q10 | 20 | BASAL_10K | 1.079 | 6.023 | 8.862e-12 | 1.002e-11 | +7.3900e-13 | 24/30 |
| NMO_03524 | apical_q10 | 20 | APICAL_10K | 1.207 | 3.053 | 8.862e-12 | 1.01e-11 | +2.0036e-12 | 21/33 |
| NMO_03524 | apical_q10 | 20 | BOTH_10K | 0.9779 | 3.751 | 8.862e-12 | 8.455e-12 | -2.4741e-13 | 29/25 |
| NMO_03524 | apical_q10 | 40 | BASAL_10K | 1.158 | 4.404 | 1.153e-11 | 1.288e-11 | +1.5475e-12 | 21/33 |
| NMO_03524 | apical_q10 | 40 | APICAL_10K | 1.3 | 3.075 | 1.153e-11 | 1.201e-11 | +2.0687e-12 | 20/34 |
| NMO_03524 | apical_q10 | 40 | BOTH_10K | 1.001 | 3.027 | 1.153e-11 | 1.02e-11 | +4.5297e-14 | 27/27 |
| NMO_03524 | apical_q95 | 20 | BASAL_10K | 1.078 | 6.116 | 8.696e-12 | 9.693e-12 | +7.2962e-13 | 24/30 |
| NMO_03524 | apical_q95 | 20 | APICAL_10K | 1.208 | 3.071 | 8.696e-12 | 9.869e-12 | +1.9607e-12 | 20/34 |
| NMO_03524 | apical_q95 | 20 | BOTH_10K | 0.9788 | 3.781 | 8.696e-12 | 8.179e-12 | -2.3665e-13 | 29/25 |
| NMO_03524 | apical_q95 | 40 | BASAL_10K | 1.162 | 4.438 | 1.119e-11 | 1.288e-11 | +1.5049e-12 | 21/33 |
| NMO_03524 | apical_q95 | 40 | APICAL_10K | 1.3 | 3.092 | 1.119e-11 | 1.152e-11 | +2.0805e-12 | 20/34 |
| NMO_03524 | apical_q95 | 40 | BOTH_10K | 1.002 | 3.039 | 1.119e-11 | 1.012e-11 | +6.0090e-14 | 27/27 |
| NMO_107159 | basal_q10 | 20 | BASAL_10K | 0.6056 | 2.065 | 5.597e-08 | 4.561e-08 | -1.2438e-08 | 36/18 |
| NMO_107159 | basal_q10 | 20 | APICAL_10K | 0.864 | 3.172 | 5.597e-08 | 7.252e-08 | -5.0574e-09 | 30/24 |
| NMO_107159 | basal_q10 | 20 | BOTH_10K | 0.8484 | 1.689 | 5.597e-08 | 5.294e-08 | -7.9011e-09 | 32/22 |
| NMO_107159 | basal_q10 | 40 | BASAL_10K | 0.8561 | 1.895 | 1.022e-07 | 9.751e-08 | -1.3778e-08 | 30/24 |
| NMO_107159 | basal_q10 | 40 | APICAL_10K | 1.312 | 3.37 | 1.022e-07 | 1.364e-07 | +2.1934e-08 | 25/29 |
| NMO_107159 | basal_q10 | 40 | BOTH_10K | 0.6873 | 2.734 | 1.022e-07 | 9.685e-08 | -1.7943e-08 | 32/22 |
| NMO_107159 | basal_q95 | 20 | BASAL_10K | 1.35 | 4.653 | 4.087e-08 | 6.236e-08 | +1.5110e-08 | 18/36 |
| NMO_107159 | basal_q95 | 20 | APICAL_10K | 1.151 | 3.977 | 4.087e-08 | 4.173e-08 | +3.5515e-09 | 22/32 |
| NMO_107159 | basal_q95 | 20 | BOTH_10K | 1.571 | 4.567 | 4.087e-08 | 8.248e-08 | +2.5896e-08 | 4/50 |
| NMO_107159 | basal_q95 | 40 | BASAL_10K | 1.287 | 3.565 | 6.238e-08 | 1.019e-07 | +6.7768e-09 | 21/33 |
| NMO_107159 | basal_q95 | 40 | APICAL_10K | 1.303 | 4.199 | 6.238e-08 | 8.898e-08 | +1.8323e-08 | 22/32 |
| NMO_107159 | basal_q95 | 40 | BOTH_10K | 1.854 | 5.742 | 6.238e-08 | 1.339e-07 | +3.8601e-08 | 6/48 |
| NMO_107159 | apical_q10 | 20 | BASAL_10K | 1.071 | 2.598 | 2.261e-08 | 2.1e-08 | +1.7220e-09 | 24/30 |
| NMO_107159 | apical_q10 | 20 | APICAL_10K | 1.231 | 2.429 | 2.261e-08 | 2.504e-08 | +3.1693e-09 | 22/32 |
| NMO_107159 | apical_q10 | 20 | BOTH_10K | 1.363 | 3.954 | 2.261e-08 | 2.735e-08 | +4.9419e-09 | 14/40 |
| NMO_107159 | apical_q10 | 40 | BASAL_10K | 1.099 | 3.272 | 2.843e-08 | 3.215e-08 | +4.1465e-09 | 19/35 |
| NMO_107159 | apical_q10 | 40 | APICAL_10K | 1.58 | 3.193 | 2.843e-08 | 3.578e-08 | +1.0315e-08 | 18/36 |
| NMO_107159 | apical_q10 | 40 | BOTH_10K | 1.979 | 5.52 | 2.843e-08 | 5.502e-08 | +1.8815e-08 | 12/42 |
| NMO_107159 | apical_q95 | 20 | BASAL_10K | 0.882 | 2.074 | 1.364e-08 | 1.313e-08 | -6.0953e-10 | 34/20 |
| NMO_107159 | apical_q95 | 20 | APICAL_10K | 1.237 | 2.658 | 1.364e-08 | 1.75e-08 | +2.7647e-09 | 22/32 |
| NMO_107159 | apical_q95 | 20 | BOTH_10K | 2.084 | 6.786 | 1.364e-08 | 3.588e-08 | +1.0449e-08 | 12/42 |
| NMO_107159 | apical_q95 | 40 | BASAL_10K | 1.192 | 2.402 | 1.839e-08 | 2.242e-08 | +4.9833e-10 | 23/31 |
| NMO_107159 | apical_q95 | 40 | APICAL_10K | 1.472 | 3.062 | 1.839e-08 | 3.038e-08 | +3.4186e-09 | 19/35 |
| NMO_107159 | apical_q95 | 40 | BOTH_10K | 2.473 | 6.439 | 1.839e-08 | 6.541e-08 | +1.9871e-08 | 6/48 |
| NMO_162186 | basal_q10 | 20 | BASAL_10K | 1.116 | 1.846 | 1.001e-08 | 1.23e-08 | +2.8283e-11 | 22/32 |
| NMO_162186 | basal_q10 | 20 | APICAL_10K | 1.544 | 2.366 | 1.001e-08 | 1.383e-08 | +4.6554e-10 | 12/42 |
| NMO_162186 | basal_q10 | 20 | BOTH_10K | 1.389 | 6.383 | 1.001e-08 | 1.277e-08 | +4.1287e-10 | 16/38 |
| NMO_162186 | basal_q10 | 40 | BASAL_10K | 1.103 | 1.843 | 9.511e-09 | 1.135e-08 | +2.6753e-11 | 22/32 |
| NMO_162186 | basal_q10 | 40 | APICAL_10K | 1.544 | 2.353 | 9.511e-09 | 1.377e-08 | +4.5803e-10 | 12/42 |
| NMO_162186 | basal_q10 | 40 | BOTH_10K | 1.389 | 5.803 | 9.511e-09 | 1.25e-08 | +3.8668e-10 | 16/38 |
| NMO_162186 | basal_q95 | 20 | BASAL_10K | 0.8555 | 2.354 | 1.104e-08 | 1.693e-08 | -5.1664e-11 | 32/22 |
| NMO_162186 | basal_q95 | 20 | APICAL_10K | 1.186 | 4.03 | 1.104e-08 | 1.752e-08 | +8.4673e-11 | 24/30 |
| NMO_162186 | basal_q95 | 20 | BOTH_10K | 1.862 | 6.168 | 1.104e-08 | 2.362e-08 | +5.9444e-10 | 16/38 |
| NMO_162186 | basal_q95 | 40 | BASAL_10K | 0.8555 | 2.354 | 1.056e-08 | 1.574e-08 | -5.1405e-11 | 32/22 |
| NMO_162186 | basal_q95 | 40 | APICAL_10K | 1.184 | 4.03 | 1.056e-08 | 1.562e-08 | +8.3589e-11 | 24/30 |
| NMO_162186 | basal_q95 | 40 | BOTH_10K | 1.862 | 6.168 | 1.056e-08 | 2.253e-08 | +5.9074e-10 | 16/38 |
| NMO_162186 | apical_q10 | 20 | BASAL_10K | 1.305 | 2.894 | 8.288e-09 | 1.286e-08 | +1.9925e-10 | 20/34 |
| NMO_162186 | apical_q10 | 20 | APICAL_10K | 1.345 | 3.353 | 8.288e-09 | 1.103e-08 | +1.3087e-10 | 22/32 |
| NMO_162186 | apical_q10 | 20 | BOTH_10K | 1.976 | 4.482 | 8.288e-09 | 1.061e-08 | +1.3388e-09 | 10/44 |
| NMO_162186 | apical_q10 | 40 | BASAL_10K | 1.305 | 2.894 | 7.986e-09 | 1.188e-08 | +1.9782e-10 | 20/34 |
| NMO_162186 | apical_q10 | 40 | APICAL_10K | 1.344 | 3.347 | 7.986e-09 | 8.486e-09 | +1.2213e-10 | 22/32 |
| NMO_162186 | apical_q10 | 40 | BOTH_10K | 1.976 | 4.481 | 7.986e-09 | 9.959e-09 | +1.2764e-09 | 10/44 |
| NMO_162186 | apical_q95 | 20 | BASAL_10K | 1.081 | 2.742 | 9.359e-09 | 1.059e-08 | +3.7190e-11 | 24/30 |
| NMO_162186 | apical_q95 | 20 | APICAL_10K | 1.329 | 3.213 | 9.359e-09 | 1.001e-08 | +1.0098e-10 | 22/32 |
| NMO_162186 | apical_q95 | 20 | BOTH_10K | 1.304 | 3.728 | 9.359e-09 | 1.207e-08 | +1.0549e-10 | 26/28 |
| NMO_162186 | apical_q95 | 40 | BASAL_10K | 1.081 | 2.742 | 7.601e-09 | 1.01e-08 | +3.5075e-11 | 24/30 |
| NMO_162186 | apical_q95 | 40 | APICAL_10K | 1.322 | 3.213 | 7.601e-09 | 9.047e-09 | +8.5735e-11 | 22/32 |
| NMO_162186 | apical_q95 | 40 | BOTH_10K | 1.304 | 3.728 | 7.601e-09 | 1.072e-08 | +9.1568e-11 | 26/28 |
| NMO_163775 | basal_q10 | 20 | BASAL_10K | 0.3399 | 0.977 | 6.27e-08 | 2.956e-08 | -2.9614e-08 | 49/5 |
| NMO_163775 | basal_q10 | 20 | APICAL_10K | 0.844 | 1.451 | 6.27e-08 | 4.726e-08 | -8.8268e-09 | 35/19 |
| NMO_163775 | basal_q10 | 20 | BOTH_10K | 0.5792 | 1.415 | 6.27e-08 | 4.223e-08 | -1.5630e-08 | 34/20 |
| NMO_163775 | basal_q10 | 40 | BASAL_10K | 0.3756 | 0.9734 | 1.25e-07 | 5.254e-08 | -6.3488e-08 | 48/6 |
| NMO_163775 | basal_q10 | 40 | APICAL_10K | 0.7397 | 1.706 | 1.25e-07 | 8.444e-08 | -1.8350e-08 | 31/23 |
| NMO_163775 | basal_q10 | 40 | BOTH_10K | 0.5485 | 1.516 | 1.25e-07 | 7.419e-08 | -3.1518e-08 | 36/18 |
| NMO_163775 | basal_q95 | 20 | BASAL_10K | 1.053 | 2.886 | 2.029e-07 | 1.738e-07 | +3.1185e-09 | 25/29 |
| NMO_163775 | basal_q95 | 20 | APICAL_10K | 1.336 | 3.381 | 2.029e-07 | 2.328e-07 | +4.8943e-08 | 19/35 |
| NMO_163775 | basal_q95 | 20 | BOTH_10K | 1.837 | 6.702 | 2.029e-07 | 2.567e-07 | +8.7425e-08 | 15/39 |
| NMO_163775 | basal_q95 | 40 | BASAL_10K | 0.7671 | 2.92 | 4.695e-07 | 3.167e-07 | -1.2300e-07 | 35/19 |
| NMO_163775 | basal_q95 | 40 | APICAL_10K | 1.553 | 3.361 | 4.695e-07 | 7.837e-07 | +2.2292e-07 | 14/40 |
| NMO_163775 | basal_q95 | 40 | BOTH_10K | 1.617 | 5.703 | 4.695e-07 | 7.052e-07 | +1.5246e-07 | 17/37 |
| NMO_163775 | apical_q10 | 20 | BASAL_10K | 0.7045 | 1.117 | 1.109e-07 | 5.923e-08 | -2.4790e-08 | 43/11 |
| NMO_163775 | apical_q10 | 20 | APICAL_10K | 0.6149 | 2.567 | 1.109e-07 | 4.111e-08 | -3.9843e-08 | 44/10 |
| NMO_163775 | apical_q10 | 20 | BOTH_10K | 0.7974 | 1.497 | 1.109e-07 | 9.794e-08 | -3.2766e-09 | 35/19 |
| NMO_163775 | apical_q10 | 40 | BASAL_10K | 0.6319 | 1.671 | 1.893e-07 | 1.234e-07 | -4.0504e-08 | 39/15 |
| NMO_163775 | apical_q10 | 40 | APICAL_10K | 0.5742 | 2.847 | 1.893e-07 | 9.499e-08 | -4.3004e-08 | 40/14 |
| NMO_163775 | apical_q10 | 40 | BOTH_10K | 0.8899 | 2.087 | 1.893e-07 | 1.737e-07 | -3.1996e-09 | 28/26 |
| NMO_163775 | apical_q95 | 20 | BASAL_10K | 0.4825 | 1.694 | 1.27e-06 | 5.415e-07 | -3.5223e-07 | 42/12 |
| NMO_163775 | apical_q95 | 20 | APICAL_10K | 1.007 | 3.139 | 1.27e-06 | 2.266e-06 | +5.2527e-09 | 26/28 |
| NMO_163775 | apical_q95 | 20 | BOTH_10K | 1.225 | 5.966 | 1.27e-06 | 2.515e-06 | +7.6910e-08 | 22/32 |
| NMO_163775 | apical_q95 | 40 | BASAL_10K | 0.3966 | 1.528 | 1.929e-06 | 7.872e-07 | -9.6110e-07 | 44/10 |
| NMO_163775 | apical_q95 | 40 | APICAL_10K | 0.9237 | 3.475 | 1.929e-06 | 2.066e-06 | -6.1100e-08 | 28/26 |
| NMO_163775 | apical_q95 | 40 | BOTH_10K | 1.102 | 5.477 | 1.929e-06 | 3.702e-06 | +7.4149e-08 | 25/29 |

## Held-out results by passive parameter scenario

| Scenario | Held-out output | Window ms | Schedule | Cases | Median ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median Δ NRMSE (pp) | Better/Worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nominal | basal_q10 | 20 | BASAL_10K | 24 | 1.038 | 2.973e-08 | 2.12e-08 | +1.1105e-11 | 11/13 |
| nominal | basal_q10 | 20 | APICAL_10K | 24 | 1.597 | 2.973e-08 | 3.883e-08 | +2.8114e-09 | 2/22 |
| nominal | basal_q10 | 20 | BOTH_10K | 24 | 1.18 | 2.973e-08 | 2.555e-08 | +1.9588e-11 | 10/14 |
| nominal | basal_q10 | 40 | BASAL_10K | 24 | 1.245 | 5.491e-08 | 3.654e-08 | +2.1571e-11 | 10/14 |
| nominal | basal_q10 | 40 | APICAL_10K | 24 | 1.791 | 5.491e-08 | 1.09e-07 | +3.1164e-08 | 0/24 |
| nominal | basal_q10 | 40 | BOTH_10K | 24 | 1.312 | 5.491e-08 | 4.075e-08 | +2.5108e-11 | 10/14 |
| nominal | basal_q95 | 20 | BASAL_10K | 24 | 1.076 | 2.153e-08 | 1.982e-08 | +1.3722e-11 | 11/13 |
| nominal | basal_q95 | 20 | APICAL_10K | 24 | 0.8911 | 2.153e-08 | 2.229e-08 | -3.7635e-11 | 14/10 |
| nominal | basal_q95 | 20 | BOTH_10K | 24 | 1.266 | 2.153e-08 | 2.941e-08 | +2.0339e-11 | 10/14 |
| nominal | basal_q95 | 40 | BASAL_10K | 24 | 0.8669 | 4.212e-08 | 2.94e-08 | -9.0853e-09 | 13/11 |
| nominal | basal_q95 | 40 | APICAL_10K | 24 | 0.761 | 4.212e-08 | 2.373e-08 | -1.0093e-08 | 19/5 |
| nominal | basal_q95 | 40 | BOTH_10K | 24 | 1.443 | 4.212e-08 | 6.494e-08 | +2.4440e-11 | 10/14 |
| nominal | apical_q10 | 20 | BASAL_10K | 24 | 0.7426 | 1.556e-08 | 9.999e-09 | -1.5776e-09 | 14/10 |
| nominal | apical_q10 | 20 | APICAL_10K | 24 | 0.8006 | 1.556e-08 | 7.063e-09 | -1.2717e-09 | 15/9 |
| nominal | apical_q10 | 20 | BOTH_10K | 24 | 1.486 | 1.556e-08 | 1.27e-08 | +1.7589e-11 | 8/16 |
| nominal | apical_q10 | 40 | BASAL_10K | 24 | 0.8159 | 2.21e-08 | 1.239e-08 | -1.3052e-09 | 14/10 |
| nominal | apical_q10 | 40 | APICAL_10K | 24 | 0.7757 | 2.21e-08 | 1.039e-08 | -1.2949e-09 | 15/9 |
| nominal | apical_q10 | 40 | BOTH_10K | 24 | 1.806 | 2.21e-08 | 2.168e-08 | +2.0259e-10 | 5/19 |
| nominal | apical_q95 | 20 | BASAL_10K | 24 | 0.8365 | 1.385e-08 | 9.025e-09 | -8.3332e-10 | 14/10 |
| nominal | apical_q95 | 20 | APICAL_10K | 24 | 1.165 | 1.385e-08 | 1.847e-08 | +2.7967e-12 | 10/14 |
| nominal | apical_q95 | 20 | BOTH_10K | 24 | 1.289 | 1.385e-08 | 1.091e-08 | -8.8616e-12 | 12/12 |
| nominal | apical_q95 | 40 | BASAL_10K | 24 | 0.8755 | 1.547e-08 | 1.358e-08 | -7.9217e-10 | 14/10 |
| nominal | apical_q95 | 40 | APICAL_10K | 24 | 0.9206 | 1.547e-08 | 1.62e-08 | -2.2669e-10 | 13/11 |
| nominal | apical_q95 | 40 | BOTH_10K | 24 | 1.569 | 1.547e-08 | 1.033e-08 | +1.4367e-11 | 11/13 |
| Rm_minus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.8508 | 2.138e-08 | 1.337e-08 | -8.0239e-10 | 13/11 |
| Rm_minus20 | basal_q10 | 20 | APICAL_10K | 24 | 0.6615 | 2.138e-08 | 1.552e-08 | -4.7924e-09 | 17/7 |
| Rm_minus20 | basal_q10 | 20 | BOTH_10K | 24 | 1.108 | 2.138e-08 | 1.328e-08 | +1.4124e-10 | 9/15 |
| Rm_minus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.9767 | 2.425e-08 | 1.797e-08 | -9.2755e-13 | 12/12 |
| Rm_minus20 | basal_q10 | 40 | APICAL_10K | 24 | 0.6347 | 2.425e-08 | 1.95e-08 | -6.3705e-09 | 17/7 |
| Rm_minus20 | basal_q10 | 40 | BOTH_10K | 24 | 1.098 | 2.425e-08 | 2.002e-08 | +2.1097e-11 | 11/13 |
| Rm_minus20 | basal_q95 | 20 | BASAL_10K | 24 | 0.9449 | 2.319e-08 | 2.001e-08 | -8.4741e-13 | 13/11 |
| Rm_minus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.154 | 2.319e-08 | 3.068e-08 | +2.1354e-09 | 10/14 |
| Rm_minus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.464 | 2.319e-08 | 3.701e-08 | +3.3703e-09 | 5/19 |
| Rm_minus20 | basal_q95 | 40 | BASAL_10K | 24 | 0.8841 | 2.651e-08 | 2.261e-08 | -3.1260e-12 | 13/11 |
| Rm_minus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.464 | 2.651e-08 | 3.764e-08 | +1.5931e-08 | 8/16 |
| Rm_minus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.482 | 2.651e-08 | 4.414e-08 | +1.2593e-08 | 4/20 |
| Rm_minus20 | apical_q10 | 20 | BASAL_10K | 24 | 0.5722 | 1.037e-08 | 7.597e-09 | -2.0703e-09 | 22/2 |
| Rm_minus20 | apical_q10 | 20 | APICAL_10K | 24 | 0.5412 | 1.037e-08 | 8.79e-09 | -7.2954e-12 | 16/8 |
| Rm_minus20 | apical_q10 | 20 | BOTH_10K | 24 | 0.783 | 1.037e-08 | 1.217e-08 | -4.3598e-10 | 18/6 |
| Rm_minus20 | apical_q10 | 40 | BASAL_10K | 24 | 0.5595 | 1.376e-08 | 8.811e-09 | -1.9103e-09 | 21/3 |
| Rm_minus20 | apical_q10 | 40 | APICAL_10K | 24 | 0.473 | 1.376e-08 | 1.233e-08 | -8.4981e-12 | 14/10 |
| Rm_minus20 | apical_q10 | 40 | BOTH_10K | 24 | 0.7656 | 1.376e-08 | 1.723e-08 | -1.0362e-11 | 17/7 |
| Rm_minus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.7998 | 4.271e-09 | 7.389e-09 | -2.0752e-12 | 14/10 |
| Rm_minus20 | apical_q95 | 20 | APICAL_10K | 24 | 0.967 | 4.271e-09 | 4.793e-09 | +3.5895e-11 | 12/12 |
| Rm_minus20 | apical_q95 | 20 | BOTH_10K | 24 | 1.087 | 4.271e-09 | 8.758e-09 | +9.1499e-10 | 11/13 |
| Rm_minus20 | apical_q95 | 40 | BASAL_10K | 24 | 0.7471 | 4.621e-09 | 7.682e-09 | -3.4706e-12 | 14/10 |
| Rm_minus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.432 | 4.621e-09 | 8.092e-09 | +1.8401e-10 | 11/13 |
| Rm_minus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.046 | 4.621e-09 | 1.017e-08 | +1.3151e-09 | 11/13 |
| Rm_plus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.5589 | 3.619e-08 | 1.546e-08 | -1.3773e-08 | 16/8 |
| Rm_plus20 | basal_q10 | 20 | APICAL_10K | 24 | 0.8223 | 3.619e-08 | 2.046e-08 | -6.0754e-10 | 18/6 |
| Rm_plus20 | basal_q10 | 20 | BOTH_10K | 24 | 0.8926 | 3.619e-08 | 1.601e-08 | -2.4434e-09 | 17/7 |
| Rm_plus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.5398 | 5.345e-08 | 3.11e-08 | -2.4979e-08 | 16/8 |
| Rm_plus20 | basal_q10 | 40 | APICAL_10K | 24 | 0.8218 | 5.345e-08 | 7.601e-08 | -8.6994e-12 | 15/9 |
| Rm_plus20 | basal_q10 | 40 | BOTH_10K | 24 | 0.5417 | 5.345e-08 | 2.154e-08 | -4.0485e-08 | 17/7 |
| Rm_plus20 | basal_q95 | 20 | BASAL_10K | 24 | 2.158 | 2.575e-08 | 4.017e-08 | +1.4319e-08 | 6/18 |
| Rm_plus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.741 | 2.575e-08 | 3.201e-08 | +6.3079e-09 | 4/20 |
| Rm_plus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.714 | 2.575e-08 | 5.275e-08 | +1.8055e-08 | 7/17 |
| Rm_plus20 | basal_q95 | 40 | BASAL_10K | 24 | 1.983 | 7.154e-08 | 1.255e-07 | +4.6991e-08 | 5/19 |
| Rm_plus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.591 | 7.154e-08 | 8.088e-08 | +1.7087e-08 | 4/20 |
| Rm_plus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.21 | 7.154e-08 | 1.622e-07 | +4.5351e-11 | 11/13 |
| Rm_plus20 | apical_q10 | 20 | BASAL_10K | 24 | 1.437 | 1.115e-08 | 1.323e-08 | +3.4586e-12 | 10/14 |
| Rm_plus20 | apical_q10 | 20 | APICAL_10K | 24 | 0.8342 | 1.115e-08 | 1.224e-08 | -2.2171e-12 | 14/10 |
| Rm_plus20 | apical_q10 | 20 | BOTH_10K | 24 | 1.1 | 1.115e-08 | 8.431e-09 | +1.9790e-12 | 11/13 |
| Rm_plus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.876 | 2.218e-08 | 2.964e-08 | +7.8589e-12 | 8/16 |
| Rm_plus20 | apical_q10 | 40 | APICAL_10K | 24 | 0.9406 | 2.218e-08 | 2.422e-08 | -2.1351e-12 | 14/10 |
| Rm_plus20 | apical_q10 | 40 | BOTH_10K | 24 | 1.284 | 2.218e-08 | 2.048e-08 | +1.9475e-12 | 11/13 |
| Rm_plus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.8712 | 1.001e-08 | 1.216e-08 | -1.4501e-10 | 14/10 |
| Rm_plus20 | apical_q95 | 20 | APICAL_10K | 24 | 0.9923 | 1.001e-08 | 1.212e-08 | +3.0412e-15 | 12/12 |
| Rm_plus20 | apical_q95 | 20 | BOTH_10K | 24 | 1.519 | 1.001e-08 | 3.541e-08 | +1.9340e-12 | 11/13 |
| Rm_plus20 | apical_q95 | 40 | BASAL_10K | 24 | 1.155 | 1.543e-08 | 2.293e-08 | +5.1588e-12 | 8/16 |
| Rm_plus20 | apical_q95 | 40 | APICAL_10K | 24 | 0.9969 | 1.543e-08 | 2.341e-08 | +4.4137e-13 | 12/12 |
| Rm_plus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.496 | 1.543e-08 | 5.618e-08 | +1.9100e-12 | 11/13 |
| Cm_minus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.7631 | 1.62e-08 | 1.033e-08 | -1.9433e-10 | 18/6 |
| Cm_minus20 | basal_q10 | 20 | APICAL_10K | 24 | 1.808 | 1.62e-08 | 3.067e-08 | +7.4396e-10 | 5/19 |
| Cm_minus20 | basal_q10 | 20 | BOTH_10K | 24 | 1.238 | 1.62e-08 | 1.506e-08 | +1.4179e-10 | 8/16 |
| Cm_minus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.7473 | 1.934e-08 | 1.395e-08 | -1.3253e-11 | 15/9 |
| Cm_minus20 | basal_q10 | 40 | APICAL_10K | 24 | 1.802 | 1.934e-08 | 4.513e-08 | +1.6745e-09 | 3/21 |
| Cm_minus20 | basal_q10 | 40 | BOTH_10K | 24 | 1.345 | 1.934e-08 | 3.535e-08 | +5.6469e-09 | 6/18 |
| Cm_minus20 | basal_q95 | 20 | BASAL_10K | 24 | 1.171 | 1.188e-08 | 1.432e-08 | +7.5503e-10 | 8/16 |
| Cm_minus20 | basal_q95 | 20 | APICAL_10K | 24 | 0.8046 | 1.188e-08 | 9.928e-09 | -1.0916e-09 | 16/8 |
| Cm_minus20 | basal_q95 | 20 | BOTH_10K | 24 | 2.414 | 1.188e-08 | 3.502e-08 | +1.8662e-08 | 5/19 |
| Cm_minus20 | basal_q95 | 40 | BASAL_10K | 24 | 1.363 | 1.254e-08 | 2.566e-08 | +3.4975e-09 | 8/16 |
| Cm_minus20 | basal_q95 | 40 | APICAL_10K | 24 | 0.8712 | 1.254e-08 | 1.371e-08 | -5.9518e-11 | 15/9 |
| Cm_minus20 | basal_q95 | 40 | BOTH_10K | 24 | 2.873 | 1.254e-08 | 4.842e-08 | +3.7410e-08 | 4/20 |
| Cm_minus20 | apical_q10 | 20 | BASAL_10K | 24 | 0.8731 | 8.303e-09 | 5.967e-09 | -3.7041e-12 | 15/9 |
| Cm_minus20 | apical_q10 | 20 | APICAL_10K | 24 | 0.9679 | 8.303e-09 | 7.872e-09 | -1.6109e-12 | 12/12 |
| Cm_minus20 | apical_q10 | 20 | BOTH_10K | 24 | 1.275 | 8.303e-09 | 9.542e-09 | +6.0740e-11 | 8/16 |
| Cm_minus20 | apical_q10 | 40 | BASAL_10K | 24 | 0.9543 | 8.381e-09 | 1.271e-08 | -2.2537e-12 | 13/11 |
| Cm_minus20 | apical_q10 | 40 | APICAL_10K | 24 | 1.021 | 8.381e-09 | 1.115e-08 | +3.0641e-13 | 11/13 |
| Cm_minus20 | apical_q10 | 40 | BOTH_10K | 24 | 1.442 | 8.381e-09 | 1.709e-08 | +5.9463e-11 | 7/17 |
| Cm_minus20 | apical_q95 | 20 | BASAL_10K | 24 | 1.003 | 7.015e-09 | 7.466e-09 | -5.1734e-13 | 12/12 |
| Cm_minus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.611 | 7.015e-09 | 9.786e-09 | +1.9540e-09 | 6/18 |
| Cm_minus20 | apical_q95 | 20 | BOTH_10K | 24 | 1.751 | 7.015e-09 | 1.761e-08 | +2.1639e-09 | 8/16 |
| Cm_minus20 | apical_q95 | 40 | BASAL_10K | 24 | 1.295 | 7.472e-09 | 1.201e-08 | +2.9527e-10 | 10/14 |
| Cm_minus20 | apical_q95 | 40 | APICAL_10K | 24 | 2.01 | 7.472e-09 | 1.41e-08 | +1.8257e-09 | 6/18 |
| Cm_minus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.903 | 7.472e-09 | 2.493e-08 | +2.0165e-09 | 7/17 |
| Cm_plus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.5456 | 2.891e-08 | 2.073e-08 | -5.2527e-11 | 16/8 |
| Cm_plus20 | basal_q10 | 20 | APICAL_10K | 24 | 0.9203 | 2.891e-08 | 3.438e-08 | -1.0132e-11 | 14/10 |
| Cm_plus20 | basal_q10 | 20 | BOTH_10K | 24 | 1.099 | 2.891e-08 | 4.415e-08 | +6.8828e-11 | 12/12 |
| Cm_plus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.7664 | 6.177e-08 | 5.011e-08 | -1.4891e-11 | 14/10 |
| Cm_plus20 | basal_q10 | 40 | APICAL_10K | 24 | 0.9686 | 6.177e-08 | 6.103e-08 | -2.6300e-12 | 13/11 |
| Cm_plus20 | basal_q10 | 40 | BOTH_10K | 24 | 1.915 | 6.177e-08 | 8.448e-08 | +6.2951e-11 | 11/13 |
| Cm_plus20 | basal_q95 | 20 | BASAL_10K | 24 | 1.208 | 4.151e-08 | 4.721e-08 | +7.5444e-09 | 11/13 |
| Cm_plus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.202 | 4.151e-08 | 4.727e-08 | +8.8785e-12 | 9/15 |
| Cm_plus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.148 | 4.151e-08 | 8.218e-08 | +1.1373e-09 | 7/17 |
| Cm_plus20 | basal_q95 | 40 | BASAL_10K | 24 | 0.7702 | 1.28e-07 | 9.512e-08 | -4.6646e-09 | 20/4 |
| Cm_plus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.267 | 1.28e-07 | 1.005e-07 | +1.2258e-11 | 9/15 |
| Cm_plus20 | basal_q95 | 40 | BOTH_10K | 24 | 0.9928 | 1.28e-07 | 1.217e-07 | -6.3674e-14 | 12/12 |
| Cm_plus20 | apical_q10 | 20 | BASAL_10K | 24 | 1.073 | 1.765e-08 | 2.611e-08 | +1.1628e-12 | 9/15 |
| Cm_plus20 | apical_q10 | 20 | APICAL_10K | 24 | 1.357 | 1.765e-08 | 1.589e-08 | +6.9566e-12 | 8/16 |
| Cm_plus20 | apical_q10 | 20 | BOTH_10K | 24 | 0.708 | 1.765e-08 | 7.762e-09 | -3.6169e-10 | 17/7 |
| Cm_plus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.12 | 1.927e-08 | 4.122e-08 | +4.7204e-09 | 5/19 |
| Cm_plus20 | apical_q10 | 40 | APICAL_10K | 24 | 1.392 | 1.927e-08 | 3.749e-08 | +1.1304e-11 | 8/16 |
| Cm_plus20 | apical_q10 | 40 | BOTH_10K | 24 | 1.074 | 1.927e-08 | 2.08e-08 | +1.3382e-12 | 10/14 |
| Cm_plus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.6021 | 1.995e-08 | 1.351e-08 | -4.4924e-09 | 14/10 |
| Cm_plus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.176 | 1.995e-08 | 1.94e-08 | +1.9607e-12 | 10/14 |
| Cm_plus20 | apical_q95 | 20 | BOTH_10K | 24 | 0.9694 | 1.995e-08 | 2.549e-08 | -1.3383e-12 | 14/10 |
| Cm_plus20 | apical_q95 | 40 | BASAL_10K | 24 | 0.5683 | 2.617e-08 | 1.217e-08 | -3.7225e-09 | 14/10 |
| Cm_plus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.332 | 2.617e-08 | 1.763e-08 | +1.1032e-11 | 8/16 |
| Cm_plus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.072 | 2.617e-08 | 3.743e-08 | +1.3078e-12 | 10/14 |
| Ra_minus20 | basal_q10 | 20 | BASAL_10K | 24 | 1.838 | 1.383e-08 | 2.379e-08 | +9.3105e-11 | 6/18 |
| Ra_minus20 | basal_q10 | 20 | APICAL_10K | 24 | 1.117 | 1.383e-08 | 2.174e-08 | +1.0356e-11 | 9/15 |
| Ra_minus20 | basal_q10 | 20 | BOTH_10K | 24 | 1.246 | 1.383e-08 | 1.744e-08 | +2.0057e-11 | 8/16 |
| Ra_minus20 | basal_q10 | 40 | BASAL_10K | 24 | 1.871 | 2.758e-08 | 3.707e-08 | +9.0481e-11 | 6/18 |
| Ra_minus20 | basal_q10 | 40 | APICAL_10K | 24 | 1.48 | 2.758e-08 | 5.04e-08 | +1.5835e-11 | 8/16 |
| Ra_minus20 | basal_q10 | 40 | BOTH_10K | 24 | 1.246 | 2.758e-08 | 4.266e-08 | +1.9226e-11 | 9/15 |
| Ra_minus20 | basal_q95 | 20 | BASAL_10K | 24 | 1.022 | 2.528e-08 | 4.584e-08 | -1.0211e-11 | 12/12 |
| Ra_minus20 | basal_q95 | 20 | APICAL_10K | 24 | 0.8354 | 2.528e-08 | 3.302e-08 | -9.1447e-11 | 14/10 |
| Ra_minus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.545 | 2.528e-08 | 3.422e-08 | +2.1611e-10 | 8/16 |
| Ra_minus20 | basal_q95 | 40 | BASAL_10K | 24 | 1.022 | 3.481e-08 | 5.667e-08 | -7.8280e-12 | 12/12 |
| Ra_minus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.084 | 3.481e-08 | 6.976e-08 | +1.2310e-11 | 10/14 |
| Ra_minus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.862 | 3.481e-08 | 7.968e-08 | +2.1280e-10 | 9/15 |
| Ra_minus20 | apical_q10 | 20 | BASAL_10K | 24 | 1.424 | 5.888e-09 | 1.162e-08 | +1.3320e-10 | 5/19 |
| Ra_minus20 | apical_q10 | 20 | APICAL_10K | 24 | 1.006 | 5.888e-09 | 6.709e-09 | -2.6948e-11 | 12/12 |
| Ra_minus20 | apical_q10 | 20 | BOTH_10K | 24 | 1.571 | 5.888e-09 | 1.861e-08 | +2.5260e-11 | 6/18 |
| Ra_minus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.413 | 1.22e-08 | 1.678e-08 | +1.1040e-11 | 8/16 |
| Ra_minus20 | apical_q10 | 40 | APICAL_10K | 24 | 0.952 | 1.22e-08 | 1.268e-08 | -2.4281e-11 | 12/12 |
| Ra_minus20 | apical_q10 | 40 | BOTH_10K | 24 | 1.493 | 1.22e-08 | 3.426e-08 | +2.2237e-11 | 7/17 |
| Ra_minus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.6443 | 2.032e-08 | 1.372e-08 | -2.5771e-09 | 16/8 |
| Ra_minus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.181 | 2.032e-08 | 1.352e-08 | +2.8616e-12 | 11/13 |
| Ra_minus20 | apical_q95 | 20 | BOTH_10K | 24 | 2.071 | 2.032e-08 | 1.747e-08 | +4.8144e-10 | 4/20 |
| Ra_minus20 | apical_q95 | 40 | BASAL_10K | 24 | 0.6039 | 2.758e-08 | 1.354e-08 | -1.4102e-10 | 13/11 |
| Ra_minus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.266 | 2.758e-08 | 1.289e-08 | +4.5398e-12 | 11/13 |
| Ra_minus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.777 | 2.758e-08 | 1.663e-08 | +1.5851e-09 | 5/19 |
| Ra_plus20 | basal_q10 | 20 | BASAL_10K | 24 | 1.174 | 2.14e-08 | 1.549e-08 | +9.1495e-12 | 10/14 |
| Ra_plus20 | basal_q10 | 20 | APICAL_10K | 24 | 1.111 | 2.14e-08 | 1.046e-08 | +9.6017e-11 | 8/16 |
| Ra_plus20 | basal_q10 | 20 | BOTH_10K | 24 | 0.9227 | 2.14e-08 | 2.381e-08 | +1.2623e-10 | 12/12 |
| Ra_plus20 | basal_q10 | 40 | BASAL_10K | 24 | 1.311 | 4.157e-08 | 2.846e-08 | +1.5169e-11 | 9/15 |
| Ra_plus20 | basal_q10 | 40 | APICAL_10K | 24 | 1.112 | 4.157e-08 | 4.108e-08 | +9.2790e-11 | 8/16 |
| Ra_plus20 | basal_q10 | 40 | BOTH_10K | 24 | 0.854 | 4.157e-08 | 5.396e-08 | -5.2770e-12 | 13/11 |
| Ra_plus20 | basal_q95 | 20 | BASAL_10K | 24 | 0.9517 | 4.441e-08 | 5.823e-08 | -2.5182e-11 | 13/11 |
| Ra_plus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.429 | 4.441e-08 | 4.402e-08 | +1.0069e-10 | 8/16 |
| Ra_plus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.362 | 4.441e-08 | 8.52e-08 | +8.1367e-09 | 10/14 |
| Ra_plus20 | basal_q95 | 40 | BASAL_10K | 24 | 0.8838 | 8.183e-08 | 8.368e-08 | -5.8344e-11 | 14/10 |
| Ra_plus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.432 | 8.183e-08 | 6.223e-08 | +9.9244e-11 | 8/16 |
| Ra_plus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.332 | 8.183e-08 | 1.533e-07 | +2.8917e-08 | 8/16 |
| Ra_plus20 | apical_q10 | 20 | BASAL_10K | 24 | 0.9192 | 6.21e-09 | 7.712e-09 | -1.1653e-12 | 14/10 |
| Ra_plus20 | apical_q10 | 20 | APICAL_10K | 24 | 1.222 | 6.21e-09 | 6.77e-09 | +3.1817e-12 | 10/14 |
| Ra_plus20 | apical_q10 | 20 | BOTH_10K | 24 | 1.49 | 6.21e-09 | 1.077e-08 | +3.3181e-09 | 5/19 |
| Ra_plus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.054 | 7.193e-09 | 1.329e-08 | +1.2110e-09 | 10/14 |
| Ra_plus20 | apical_q10 | 40 | APICAL_10K | 24 | 1.426 | 7.193e-09 | 1.94e-08 | +8.0830e-10 | 4/20 |
| Ra_plus20 | apical_q10 | 40 | BOTH_10K | 24 | 2.147 | 7.193e-09 | 1.709e-08 | +8.4026e-09 | 5/19 |
| Ra_plus20 | apical_q95 | 20 | BASAL_10K | 24 | 1.35 | 1.266e-08 | 1.886e-08 | +3.7842e-09 | 10/14 |
| Ra_plus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.305 | 1.266e-08 | 1.46e-08 | +3.0524e-12 | 10/14 |
| Ra_plus20 | apical_q95 | 20 | BOTH_10K | 24 | 1.117 | 1.266e-08 | 1.741e-08 | +1.7224e-10 | 11/13 |
| Ra_plus20 | apical_q95 | 40 | BASAL_10K | 24 | 0.9663 | 2.479e-08 | 2.803e-08 | -5.4883e-13 | 13/11 |
| Ra_plus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.45 | 2.479e-08 | 2.717e-08 | +6.8824e-12 | 9/15 |
| Ra_plus20 | apical_q95 | 40 | BOTH_10K | 24 | 1.372 | 2.479e-08 | 1.642e-08 | +1.6482e-10 | 10/14 |
| all_minus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.8072 | 1.906e-08 | 5.929e-09 | -2.7981e-09 | 17/7 |
| all_minus20 | basal_q10 | 20 | APICAL_10K | 24 | 1.895 | 1.906e-08 | 1.672e-08 | +2.2152e-10 | 8/16 |
| all_minus20 | basal_q10 | 20 | BOTH_10K | 24 | 0.5234 | 1.906e-08 | 1.009e-08 | -1.4410e-09 | 18/6 |
| all_minus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.7448 | 2.387e-08 | 7.692e-09 | -5.8895e-09 | 15/9 |
| all_minus20 | basal_q10 | 40 | APICAL_10K | 24 | 1.881 | 2.387e-08 | 1.584e-08 | +2.1974e-10 | 8/16 |
| all_minus20 | basal_q10 | 40 | BOTH_10K | 24 | 0.4803 | 2.387e-08 | 1.163e-08 | -3.8125e-09 | 18/6 |
| all_minus20 | basal_q95 | 20 | BASAL_10K | 24 | 1.027 | 2.219e-08 | 3.086e-08 | +3.7248e-13 | 11/13 |
| all_minus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.699 | 2.219e-08 | 3.581e-08 | +5.4358e-09 | 8/16 |
| all_minus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.477 | 2.219e-08 | 2.733e-08 | +1.8886e-09 | 8/16 |
| all_minus20 | basal_q95 | 40 | BASAL_10K | 24 | 1.049 | 2.699e-08 | 3.885e-08 | +7.2957e-13 | 11/13 |
| all_minus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.826 | 2.699e-08 | 5.369e-08 | +1.3999e-08 | 8/16 |
| all_minus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.566 | 2.699e-08 | 2.97e-08 | +3.6448e-09 | 7/17 |
| all_minus20 | apical_q10 | 20 | BASAL_10K | 24 | 0.9871 | 8.363e-09 | 8.618e-09 | -1.5409e-13 | 12/12 |
| all_minus20 | apical_q10 | 20 | APICAL_10K | 24 | 1.068 | 8.363e-09 | 1.557e-08 | +4.6933e-11 | 12/12 |
| all_minus20 | apical_q10 | 20 | BOTH_10K | 24 | 0.9471 | 8.363e-09 | 7.215e-09 | +1.0425e-11 | 12/12 |
| all_minus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.054 | 8.238e-09 | 8.898e-09 | +7.2075e-13 | 11/13 |
| all_minus20 | apical_q10 | 40 | APICAL_10K | 24 | 1.074 | 8.238e-09 | 1.776e-08 | +4.5641e-11 | 12/12 |
| all_minus20 | apical_q10 | 40 | BOTH_10K | 24 | 0.9714 | 8.238e-09 | 8.354e-09 | +9.8736e-12 | 12/12 |
| all_minus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.8835 | 6.97e-09 | 7.602e-09 | -2.0526e-10 | 16/8 |
| all_minus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.281 | 6.97e-09 | 9.454e-09 | +2.6286e-09 | 10/14 |
| all_minus20 | apical_q95 | 20 | BOTH_10K | 24 | 2.126 | 6.97e-09 | 1.82e-08 | +9.2034e-09 | 6/18 |
| all_minus20 | apical_q95 | 40 | BASAL_10K | 24 | 0.8556 | 7.275e-09 | 7.525e-09 | -2.0180e-10 | 15/9 |
| all_minus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.405 | 7.275e-09 | 1.035e-08 | +2.8092e-09 | 10/14 |
| all_minus20 | apical_q95 | 40 | BOTH_10K | 24 | 2.393 | 7.275e-09 | 2.06e-08 | +1.1460e-08 | 6/18 |
| all_plus20 | basal_q10 | 20 | BASAL_10K | 24 | 0.5859 | 5.127e-08 | 2.654e-08 | -2.3940e-08 | 17/7 |
| all_plus20 | basal_q10 | 20 | APICAL_10K | 24 | 0.8427 | 5.127e-08 | 2.803e-08 | -4.3576e-09 | 14/10 |
| all_plus20 | basal_q10 | 20 | BOTH_10K | 24 | 0.6141 | 5.127e-08 | 2.039e-08 | -1.2985e-08 | 18/6 |
| all_plus20 | basal_q10 | 40 | BASAL_10K | 24 | 0.7268 | 1.893e-07 | 7.364e-08 | -4.7018e-08 | 15/9 |
| all_plus20 | basal_q10 | 40 | APICAL_10K | 24 | 0.7555 | 1.893e-07 | 5.107e-08 | -3.6891e-08 | 13/11 |
| all_plus20 | basal_q10 | 40 | BOTH_10K | 24 | 0.638 | 1.893e-07 | 7.292e-08 | -5.2103e-08 | 18/6 |
| all_plus20 | basal_q95 | 20 | BASAL_10K | 24 | 1.182 | 2.708e-08 | 5.904e-08 | +4.3317e-11 | 8/16 |
| all_plus20 | basal_q95 | 20 | APICAL_10K | 24 | 1.186 | 2.708e-08 | 6.732e-08 | +1.1711e-08 | 7/17 |
| all_plus20 | basal_q95 | 20 | BOTH_10K | 24 | 1.768 | 2.708e-08 | 1.058e-07 | +7.4306e-08 | 6/18 |
| all_plus20 | basal_q95 | 40 | BASAL_10K | 24 | 1.263 | 3.698e-08 | 1.537e-07 | +1.7778e-11 | 8/16 |
| all_plus20 | basal_q95 | 40 | APICAL_10K | 24 | 1.484 | 3.698e-08 | 1.295e-07 | +7.7098e-08 | 3/21 |
| all_plus20 | basal_q95 | 40 | BOTH_10K | 24 | 1.962 | 3.698e-08 | 3.94e-07 | +3.2967e-07 | 6/18 |
| all_plus20 | apical_q10 | 20 | BASAL_10K | 24 | 1.6 | 1.781e-08 | 1.22e-08 | +5.0637e-12 | 10/14 |
| all_plus20 | apical_q10 | 20 | APICAL_10K | 24 | 1.533 | 1.781e-08 | 1.585e-08 | +4.7476e-12 | 10/14 |
| all_plus20 | apical_q10 | 20 | BOTH_10K | 24 | 1.392 | 1.781e-08 | 2.116e-08 | +5.1805e-09 | 3/21 |
| all_plus20 | apical_q10 | 40 | BASAL_10K | 24 | 1.833 | 3.229e-08 | 2.974e-08 | +1.2136e-11 | 9/15 |
| all_plus20 | apical_q10 | 40 | APICAL_10K | 24 | 1.811 | 3.229e-08 | 3.346e-08 | +1.1468e-11 | 10/14 |
| all_plus20 | apical_q10 | 40 | BOTH_10K | 24 | 1.572 | 3.229e-08 | 7.439e-08 | +3.3781e-08 | 3/21 |
| all_plus20 | apical_q95 | 20 | BASAL_10K | 24 | 0.9224 | 1.396e-08 | 1.758e-08 | -3.0268e-10 | 14/10 |
| all_plus20 | apical_q95 | 20 | APICAL_10K | 24 | 1.208 | 1.396e-08 | 1.67e-08 | +5.6106e-12 | 9/15 |
| all_plus20 | apical_q95 | 20 | BOTH_10K | 24 | 1.008 | 1.396e-08 | 1.861e-08 | +1.3243e-13 | 12/12 |
| all_plus20 | apical_q95 | 40 | BASAL_10K | 24 | 1.156 | 2.037e-08 | 1.62e-08 | +8.1196e-12 | 11/13 |
| all_plus20 | apical_q95 | 40 | APICAL_10K | 24 | 1.208 | 2.037e-08 | 2.069e-08 | +1.3138e-11 | 9/15 |
| all_plus20 | apical_q95 | 40 | BOTH_10K | 24 | 0.9537 | 2.037e-08 | 1.595e-08 | -5.9981e-13 | 13/11 |

Each scenario cell contains 24 matched records (four morphology strata × three sources × two pulse widths). Scenario-specific improvement is checked alongside the four morphology-specific tables above.

## Exact spatial node map

### NMO_03524

- SWC SHA-256: `6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`.
- Seven shared node IDs: 1, 583, 867, 367, 751, 866, 868.
- q25 node IDs: basal 272; apical 864.

| Output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 631 | 112 | basal | 0.10 |
| basal_q95 | 702 | 801 | basal | 0.95 |
| apical_q10 | 863 | 7 | apical | 0.10 |
| apical_q95 | 869 | 70 | apical | 0.95 |

### NMO_107159

- SWC SHA-256: `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`.
- Seven shared node IDs: 1, 6363, 4735, 5564, 7023, 4301, 4623.
- q25 node IDs: basal 6609; apical 4404.

| Output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 6739 | 351 | basal | 0.10 |
| basal_q95 | 7206 | 5039 | basal | 0.95 |
| apical_q10 | 4355 | 922 | apical | 0.10 |
| apical_q95 | 4820 | 6230 | apical | 0.95 |

### NMO_162186

- SWC SHA-256: `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`.
- Seven shared node IDs: 1, 2304, 4262, 2261, 515, 6608, 4180.
- q25 node IDs: basal 2713; apical 4488.

| Output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 67 | 543 | basal | 0.10 |
| basal_q95 | 2167 | 4992 | basal | 0.95 |
| apical_q10 | 7171 | 1836 | apical | 0.10 |
| apical_q95 | 4769 | 7159 | apical | 0.95 |

### NMO_163775

- SWC SHA-256: `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`.
- Seven shared node IDs: 1, 144, 3926, 4180, 40, 4104, 3948.
- q25 node IDs: basal 224; apical 4096.

| Output | SWC node ID | Tree index | Branch | Path quantile |
| --- | --- | --- | --- | --- |
| basal_q10 | 7 | 21 | basal | 0.10 |
| basal_q95 | 94 | 261 | basal | 0.95 |
| apical_q10 | 3967 | 245 | apical | 0.10 |
| apical_q95 | 4042 | 1291 | apical | 0.95 |

## Scientific limits

- Four reconstructions are four individual morphology strata, not a biological population.
- This is passive linear-RC numerical reduction only: no active channels, action potentials, synapses, plasticity, calcium signalling or metabolism are simulated.
- Spatial holdouts are unseeded observation sites within existing SWC reconstructions, not independent biological specimens.
- Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 has no-diameter metadata.
- Full Hines remains the canonical reference. No production solver, default port layout or basis-order default is changed.

## Archived sources

- Case metrics: `prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout_order224_2026-11-26_case_metrics.csv`.
- Basis/node metadata: `prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout_order224_2026-11-26_basis_metadata.json`.
- Numerical report: `prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout_order224_2026-11-26_report.json`.
- Integrity manifest: `prima_q25_four_morphology_role_specific_q25_seed_spatial_holdout_order224_2026-11-26_manifest.json`.
