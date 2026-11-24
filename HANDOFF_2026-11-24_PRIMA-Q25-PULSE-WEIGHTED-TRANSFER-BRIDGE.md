# Handoff — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Parent:** Krylov-prefix transfer audit / PR #24  
**Draft PR:** [#27](https://github.com/Nolane-x/Nghien-cuu/pull/27)  
**Successful workflow:** [45343771112](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112)  
**Result commit:** `b82b80739144ded41de5862cddff05bbdbf824a1`  
**Artifact:** [prima-q25-pulse-weighted-transfer-bridge](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112/artifacts/14896928557), SHA-256 `7be0cc4c7f5e5b9d90464f1bbc1e75a29eec3e3ae72221e057c17c9698e1577b`

## Research question

At order 168, dual-q25 AC transfer residuals are above seven-port on both Peng and Tamas, but the time-domain pulse penalty is 14.525× on Peng and only 1.001× on Tamas. This follow-up weights dense transfer residuals by the spectra of the 2-ms and 10-ms rectangular inputs and joins each result to the exact archived transient NRMSE pair.

## Design and verified coverage

- Two checksum-pinned morphologies: Peng mouse NMO_163775 and Tamas human pyramidal NMO_107159.
- Seven-port baseline versus dual-q25 nine-port; basis order 168.
- Nine passive parameter scenarios, three sources and seven shared SWC output nodes.
- Dense 0–5,000 Hz grid, 5-Hz spacing (1,001 points).
- Rectangular 10-pA pulse spectrum, 2-ms and 10-ms widths, 2-ms onset.
- Four bands: 0–100, 100–500, 500–2,000, 2,000–5,000 Hz.
- Every dual-q25 result joined by exact scenario/source/pulse/SWC output identity to the prior time-domain transient row.

Successful workflow 45343771112 passed 7/7 tests, both SWC hashes, both transient-file checks, both preflights, computation, exact coverage, result commit and artifact upload.

| Dataset | Expected | Verified |
|---|---:|---:|
| Weighted source/output/pulse rows | 1,512 | 1,512 |
| Band-energy rows | 6,048 | 6,048 |
| Paired spectral/transient rows | 756 | 756 |
| By-output summaries | 168 | 168 |
| Comparison summaries | 84 | 84 |
| By-source summaries | 12 | 12 |
| Pooled band summaries | 96 | 96 |

Runtime: 100.40 s wall, 177.13 s user CPU, 259,632 KB maximum RSS. Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## Finding 1 — pulse weighting does not reconcile the AC/transient gap

Median across the 21 source/output pairs (three sources × seven outputs) per morphology and pulse width:

| Morphology | Pulse | Median pulse-weighted spectral ratio | Median transient NRMSE ratio | Spectral worse pairs | Transient worse pairs |
|---|---:|---:|---:|---:|---:|
| Peng mouse | 2 ms | 33.21× | 18.91× | 189/189 | 176/189 |
| Peng mouse | 10 ms | 30.12× | 14.72× | 189/189 | 175/189 |
| Tamas human pyramidal | 2 ms | 35.93× | 1.0008× | 189/189 | 109/189 |
| Tamas human pyramidal | 10 ms | 28.59× | 1.0005× | 189/189 | 105/189 |

So weighting by the continuous rectangular-pulse spectrum reduces the spectral ratio moderately for 10 ms but does not explain why Tamas transient NRMSE remains effectively at parity.

## Finding 2 — input-source dependence persists

Median ratios across the seven output ports and nine parameter scenarios for each source/pulse:

| Morphology | Source | Pulse | Weighted spectral ratio | Transient NRMSE ratio |
|---|---|---:|---:|---:|
| Peng | Soma | 2 ms | 40.99× | 58.84× |
| Peng | Soma | 10 ms | 33.77× | 60.23× |
| Peng | Basal-q75 | 2 ms | 38.24× | 33.20× |
| Peng | Basal-q75 | 10 ms | 33.13× | 29.66× |
| Peng | Apical-q75 | 2 ms | 31.23× | 1.431× |
| Peng | Apical-q75 | 10 ms | 28.41× | 1.366× |
| Tamas | Soma | 2 ms | 41.83× | 1.032× |
| Tamas | Soma | 10 ms | 30.65× | 1.031× |
| Tamas | Basal-q75 | 2 ms | 33.65× | 1.0007× |
| Tamas | Basal-q75 | 10 ms | 27.75× | 1.0007× |
| Tamas | Apical-q75 | 2 ms | 28.65× | 0.9995× |
| Tamas | Apical-q75 | 10 ms | 24.44× | 0.9993× |

The Peng soma/basal transient degradation is reflected in the spectral metric. The Tamas spectral metric remains elevated for all sources, but transient NRMSE is almost unchanged outside soma, where it is still only about 3% above baseline.

## Finding 3 — weighted residual energy is concentrated below 100 Hz

Median share of dual-q25 pulse-weighted error energy across the three source locations:

| Morphology | Pulse | 0–100 Hz | 100–500 Hz | Above 500 Hz |
|---|---:|---:|---:|---:|
| Peng | 2 ms | 90.18% | 9.82% | <0.001% |
| Peng | 10 ms | 99.35% | 0.65% | <0.001% |
| Tamas | 2 ms | 96.20% | 3.80% | <0.001% |
| Tamas | 10 ms | 99.81% | 0.19% | <0.001% |

The low-frequency error share is dominant, especially for the 10-ms pulse. Yet this low-frequency weighting does not make the Tamas spectral ratio agree with the time-domain result.

## Interpretation and next experiment

This is a useful negative result: a continuous-time Parseval-weighted transfer metric, even with the rectangular input spectrum, is not a sufficient proxy for the finite 20-ms backward-Euler NRMSE used in the pulse experiment.

The next diagnostic should re-run the exact discrete backward-Euler scheme at dt=0.1 ms with longer observation windows (20, 40, 100 and 200 ms). This will test whether the AC residual gap appears primarily in the late passive tail beyond the original 20-ms window. It should preserve the same 10-pA input, 2-ms onset, 2/10-ms pulse widths, nine scenarios, three sources, seven common outputs and both morphologies.

## Scientific constraints

The pulse-weighted result is a continuous-time Parseval proxy, not an exact reproduction of finite-step backward-Euler transients. Ratios can be large when the seven-port denominator is extremely small; absolute errors remain beside ratios. Two individual passive linear-RC reconstructions are not biological/population evidence. Full Hines remains canonical; production code and defaults are unchanged.
