# Research log — Cross-morphology PRIMA q25 pulse-weighted transfer bridge

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-weighted-transfer-bridge-2026-11-24  
**Draft PR:** [#27](https://github.com/Nolane-x/Nghien-cuu/pull/27)  
**Successful workflow:** [45343771112](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112)  
**Result commit:** `b82b80739144ded41de5862cddff05bbdbf824a1`  
**Artifact SHA-256:** `7be0cc4c7f5e5b9d90464f1bbc1e75a29eec3e3ae72221e057c17c9698e1577b`

## Motivation

The Krylov-prefix transfer audit showed a final dual-q25 AC transfer residual above seven-port for both Peng and Tamas. Yet the matched order-168 time-domain pulse NRMSE ratio was 14.525× on Peng and 1.001× on Tamas. This bridge weights the AC residual by the continuous rectangular-pulse spectrum and joins the result to the exact transient observation for identical scenario/source/output/pulse.

## Method and validation

For two checksum-pinned morphologies, seven-port and dual-q25 models at order 168, nine passive parameter scenarios, three sources and seven common output nodes:
1. Compute full-Hines and reduced PRIMA transfer functions on a dense 0–5,000 Hz grid at 5-Hz spacing (1,001 points).
2. Weight squared transfer error by `|I(f)|² = (I0·T·sinc(fT))²` for 10-pA rectangular pulses of 2-ms and 10-ms width.
3. Integrate error/reference energy using Parseval weighting.
4. Partition weighted error into four bands.
5. Join every dual-q25 output row to its archived time-domain transient NRMSE pair.

The 2-ms onset changes pulse-spectrum phase but not power weighting. This spectral integral is not an exact reproduction of finite-step backward-Euler or a finite observation window.

Workflow 45343771112: **success**, 7 tests passed, both morphology hashes, both transient inputs, both preflights, full compute, result commit and artifact upload all succeeded.

Exact rows: 1,512 model-weighted; 6,048 band energy; 756 spectral/transient bridge; 168 by-output; 84 comparison; 12 by-source; 96 band summary.

Runtime: 100.40 s wall, 177.13 s user CPU, 259,632 KB peak RSS. Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

Artifact [prima-q25-pulse-weighted-transfer-bridge](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112/artifacts/14896928557), SHA-256 `7be0cc4c7f5e5b9d90464f1bbc1e75a29eec3e3ae72221e057c17c9698e1577b`.

## Findings — spectral weighting does not reconcile transient behavior

Median across 21 source/output pairs per morphology/pulse:

| Morphology | Pulse | Median weighted spectral ratio | Median transient NRMSE ratio | Spectral worse | Transient worse |
|---|---:|---:|---:|---:|---:|
| Peng | 2 ms | 33.21× | 18.91× | 189/189 | 176/189 |
| Peng | 10 ms | 30.12× | 14.72× | 189/189 | 175/189 |
| Tamas | 2 ms | 35.93× | 1.0008× | 189/189 | 109/189 |
| Tamas | 10 ms | 28.59× | 1.0005× | 189/189 | 105/189 |

For Tamas, the spectral ratio remains 29–36× while transient NRMSE remains near one. The continuous-time pulse-weighted metric therefore fails to close the AC/transient discrepancy.

### Source dependence

| Morphology | Source | Pulse | Weighted spectral ratio | Transient ratio |
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

### Frequency-band error concentration

Median share of weighted spectral error energy across three input sources:

| Morphology | Pulse | 0–100 Hz | 100–500 Hz | Above 500 Hz |
|---|---:|---:|---:|---:|
| Peng | 2 ms | 90.18% | 9.82% | <0.001% |
| Peng | 10 ms | 99.35% | 0.65% | <0.001% |
| Tamas | 2 ms | 96.20% | 3.80% | <0.001% |
| Tamas | 10 ms | 99.81% | 0.19% | <0.001% |

Thus the weighted error is overwhelmingly low-frequency, especially for 10 ms, but the discrepancy remains.

## Interpretation

This is a negative result with useful value. The continuous-time Parseval metric weighted by the rectangular pulse spectrum does not reproduce the finite-duration, finite-step backward-Euler transient NRMSE contrast. In particular, it cannot explain why Tamas spectral ratios remain high while Tamas time-domain transient ratios remain near one.

The next experiment should use the exact discrete backward-Euler recurrence with dt=0.1 ms and the same pulse inputs, but extend observation windows to 20, 40, 100 and 200 ms. That will test whether the discrepancy grows in the late passive tail beyond the existing 20-ms measurement window.

## Files and hashes

Result stem: `prima_q25_pulse_weighted_transfer_bridge_2026-11-24`.

- `model_weighted.csv`: 1,512 rows.
- `band_energy.csv`: 6,048 rows.
- `by_output_summary.csv`: 168 rows.
- `transient_bridge.csv`: 756 rows.
- `comparison_summary.csv`: 84 rows.
- `by_source_summary.csv`: 12 rows.
- `band_summary.csv`: 96 rows.
- `report.json`, `.time.txt`.

Git blob SHA-1:
- report JSON: `7b92f5da67728de46d3055b7543c3d69f36bb2f5`
- model weighted: `a8036fff243581a1ee01ad51b39c2efd6fe8b1f5`
- band energy: `37e028aae7c7d33888b48ffae2bd389b27edd3f6`
- by-output summary: `a34758b5f2c5f7b96fd14866df9fa7b4867c142b`
- transient bridge: `d56b16b780ea77469e02a9b239fde9d47e978d71`
- comparison summary: `1bba30e5a2404b2646a1c5bad6af612135efcdc8`
- by-source summary: `4547455942d6914993c80f08301d251b1168764c`
- band summary: `fe9bda7b93025626f920d122c45a862be8ceab83`
- time: `c021b70635236bc9439c0908a9495c691a9f78b3`

## Limits

Two individual passive linear-RC morphology reconstructions, not biological or population evidence. Absolute weighted errors remain tiny; ratio denominators can be extremely small. Full Hines remains canonical. No production code/defaults changed.
