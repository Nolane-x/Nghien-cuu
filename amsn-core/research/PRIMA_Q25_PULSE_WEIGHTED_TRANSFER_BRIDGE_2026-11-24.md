# PRIMA q25 pulse-weighted transfer / transient bridge

**Date:** 24 November 2026  
**Workflow:** [45343771112](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112) — success  
**Result commit:** `b82b80739144ded41de5862cddff05bbdbf824a1`  
**Artifact:** [prima-q25-pulse-weighted-transfer-bridge](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45343771112/artifacts/14896928557)  
**Artifact SHA-256:** `7be0cc4c7f5e5b9d90464f1bbc1e75a29eec3e3ae72221e057c17c9698e1577b`

## 1. Aim and method

The final order-168 dual-q25 AC transfer residual is above seven-port on both Peng and Tamas, while time-domain pulse NRMSE was 14.525× on Peng but 1.001× on Tamas. This experiment applies a rectangular-pulse Parseval weighting to dense complex transfer residuals, then joins those values to the exact archived transient observations.

The two pinned morphologies are:
- NMO_163775 Peng mouse Control, 4,209 SWC records.
- NMO_107159 Tamas human pyramidal Control comparison cell, 7,228 SWC records.

For seven-port and dual-q25 nine-port at order168, all nine passive scenarios, three current sources and seven shared SWC outputs:
- 10-pA rectangular pulse widths 2 ms and 10 ms, onset2ms.
- Dense frequency grid 0–5,000 Hz, 5-Hz spacing (1,001 points).
- Weight squared transfer error by `|I(f)|²=(I0·T·sinc(fT))²`.
- Integrate using the trapezoid rule and split energy into four bands.

This is a continuous-time spectral proxy. It is not an exact reproduction of the 0.1-ms finite-step backward-Euler simulator or its 20-ms observation window.

## 2. Validation and coverage

Workflow 45343771112 succeeded. Seven focused tests passed, both morphology checksums passed, both transient input CSV checks passed, both Import3D preflights passed, computation completed, results committed and artifact uploaded.

| Dataset | Expected | Verified |
|---|---:|---:|
| Weighted model/output/pulse rows | 1,512 | 1,512 |
| Frequency-band energy rows | 6,048 | 6,048 |
| Dual-q25 vs seven spectral/transient pairs | 756 | 756 |
| By-output summaries | 168 | 168 |
| Comparison summaries | 84 | 84 |
| By-source summaries | 12 | 12 |
| Band summaries | 96 | 96 |

Runtime: 100.40 s wall, 177.13 s user CPU, 259,632 KB maximum RSS. Python3.12.16, NumPy2.5.5, NEURON9.0.2.

## 3. Main finding — pulse weighting does not reconcile the AC/transient gap

Median across 21 source/output pairs (three sources × seven outputs) per morphology and pulse width:

| Morphology | Pulse width | Weighted spectral ratio | Transient NRMSE ratio | Spectral worse pairs | Transient worse pairs |
|---|---:|---:|---:|---:|---:|
| Peng mouse | 2 ms | 33.21× | 18.91× | 189/189 | 176/189 |
| Peng mouse | 10 ms | 30.12× | 14.72× | 189/189 | 175/189 |
| Tamas human pyramidal | 2 ms | 35.93× | 1.0008× | 189/189 | 109/189 |
| Tamas human pyramidal | 10 ms | 28.59× | 1.0005× | 189/189 | 105/189 |

For Tamas, pulse weighting lowers the median spectral ratio somewhat from the unweighted AC result, but it remains around 29–36× while time-domain transient NRMSE remains effectively at baseline. Therefore continuous-time pulse-weighted transfer error is still not a sufficient proxy for the measured finite-window transient metric.

## 4. Source-specific comparison

Median ratios across seven shared outputs and nine passive scenarios:

| Morphology | Input source | Pulse | Weighted spectral ratio | Transient ratio |
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

The Peng soma/basal transient degradation is reflected in the spectral bridge. Peng apical source has a much smaller transient penalty than its weighted spectral ratio would suggest. For Tamas all three transient source groups remain close to unity, particularly basal/apical inputs.

## 5. Where the weighted spectral error lies

Median share of dual-q25 pulse-weighted error energy across the three source sites:

| Morphology | Pulse | 0–100 Hz | 100–500 Hz | Above 500 Hz |
|---|---:|---:|---:|---:|
| Peng | 2 ms | 90.18% | 9.82% | <0.001% |
| Peng | 10 ms | 99.35% | 0.65% | <0.001% |
| Tamas | 2 ms | 96.20% | 3.80% | <0.001% |
| Tamas | 10 ms | 99.81% | 0.19% | <0.001% |

The spectral error energy is concentrated below 100 Hz; the 10-ms rectangular pulse pushes it further into the lowest band. Yet this stronger low-frequency weighting does not close the Tamas discrepancy.

## 6. Absolute error context

Median pulse-weighted relative-L2 error across all 189 model/output pairs:

| Morphology | Pulse | Seven-port (%) | Dual-q25 (%) |
|---|---:|---:|---:|
| Peng | 2 ms | 3.20e-9 | 8.63e-8 |
| Peng | 10 ms | 2.67e-9 | 5.41e-8 |
| Tamas | 2 ms | 7.44e-10 | 2.52e-8 |
| Tamas | 10 ms | 6.06e-10 | 1.65e-8 |

The relative ratios appear large partly because the seven-port denominator is extremely small. Absolute pulse-weighted transfer errors remain tiny.

## 7. Interpretation and next step

This is a useful negative finding: continuous-time transfer residuals weighted by the rectangular input spectrum do not reproduce the finite-step, finite-window backward-Euler NRMSE contrast. The low-frequency error share is dominant, but this alone does not predict the transient discrepancy.

The next diagnostic should re-run the **exact backward-Euler recurrence at dt=0.1 ms** while measuring cumulative NRMSE at 20, 40, 100 and 200 ms. If the Tamas nine-port penalty grows only in the late passive tail, the original 20-ms window could explain why it is hidden in the time-domain metric. If it remains near unity at every window, the discrepancy must be investigated in the discrete-time transfer/resolution treatment rather than assumed to be tail truncation.

## 8. Scientific limits

Passive linear-RC numerical validation only. Two individual morphologies, not populations. The weighted spectral bridge is a continuous-time Parseval proxy, not exact finite-window backward-Euler. Large ratios can come from a tiny seven-port denominator. Full Hines remains canonical; no production code or defaults changed.

## 9. Reproducible output files

Result stem: `prima_q25_pulse_weighted_transfer_bridge_2026-11-24`.

- `model_weighted.csv`: 1,512 rows.
- `band_energy.csv`: 6,048 rows.
- `by_output_summary.csv`: 168 rows.
- `transient_bridge.csv`: 756 rows.
- `comparison_summary.csv`: 84 rows.
- `by_source_summary.csv`: 12 rows.
- `band_summary.csv`: 96 rows.
- `report.json`, `.time.txt`.

Blob SHA-1:
- report JSON: `7b92f5da67728de46d3055b7543c3d69f36bb2f5`
- model weighted: `a8036fff243581a1ee01ad51b39c2efd6fe8b1f5`
- band energy: `37e028aae7c7d33888b48ffae2bd389b27edd3f6`
- by-output summary: `a34758b5f2c5f7b96fd14866df9fa7b4867c142b`
- transient bridge: `d56b16b780ea77469e02a9b239fde9d47e978d71`
- comparison summary: `1bba30e5a2404b2646a1c5bad6af612135efcdc8`
- by-source summary: `4547455942d6914993c80f08301d251b1168764c`
- band summary: `fe9bda7b93025626f920d122c45a862be8ceab83`
- timing: `c021b70635236bc9439c0908a9495c691a9f78b3`
