# Research log — PRIMA q25 pulse-spectrum-weighted transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-spectrum-weighted-transfer-audit-2026-11-24  
**Successful workflow:** [45381680741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741)  
**Result archive commit:** `6274a6dd4106d421aeda48ab4bbb7c5d76da5e60`

## Motivation

The preceding transfer-stage audit found AC transfer residuals improving strongly as the basis grows, but dual-q25 remained above seven-port at every shared output on both morphologies. The order-168 finite-window transient result was much closer for Tamas than the AC metric suggested. This analysis weights complex transfer residuals by the ideal rectangular input-pulse spectrum and compares them against exact archived 20-ms transient NRMSE.

## Method

- Keep only canonical seven-port and dual-q25 nine-port layouts at basis order 168.
- Use nine passive parameter scenarios, three sources and seven exact shared output SWC node IDs.
- Evaluate full-Hines and reduced PRIMA transfer responses on 98 nonuniform frequencies from DC to 5 kHz.
- For 2 ms and 10 ms ideal rectangular current pulses, weight squared complex transfer residual by (|\mathrm{sinc}(fT)|^2) and integrate with the trapezoidal rule.
- Join each weighted output with the saved transient NRMSE for the exact morphology, scenario, source, output node and pulse width.
- Correlate weighted-transfer and transient candidate/seven log ratios.

The transient loader now explicitly pins the seven shared output IDs per morphology and filters out the two q25-only rows in the nine-port CSV. This makes both the paired data matrix and exact coverage contract consistent.

## Execution and read-back

- Workflow [45381680741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741): **success**.
- Tests: 6 passed.
- Both SWC checksums and both Import3D preflights passed.
- Runtime: 92.23 s wall, 109.95 s user CPU, 228,764 KB maximum RSS.
- Result commit: `6274a6dd4106d421aeda48ab4bbb7c5d76da5e60`.
- Artifact: [prima-q25-pulse-spectrum-weighted-transfer](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741/artifacts/14914850862), SHA-256 `a572b412e7c2515862097585ae38c744243803ed70deece1b970bfd01bf36cfc`.

| Dataset | Expected | Verified |
|---|---:|---:|
| Frequency rows | 74,088 | 74,088 |
| Weighted shared-output rows | 1,512 | 1,512 |
| Weighted output summaries | 168 | 168 |
| Weighted source summaries | 24 | 24 |
| Spectral/transient paired rows | 756 | 756 |
| Source/pulse paired summaries | 12 | 12 |
| Pulse-spectrum samples | 196 | 196 |
| Shared transient input rows | 1,512 | 1,512 |

## Source-level comparison

Median candidate/seven ratios by input source:

| Morphology | Source | Pulse | Weighted spectral ratio | Transient ratio |
|---|---|---:|---:|---:|
| Peng | Soma | 2 ms | 41.01× | 58.84× |
| Peng | Soma | 10 ms | 34.05× | 60.23× |
| Peng | Basal-q75 | 2 ms | 39.59× | 33.20× |
| Peng | Basal-q75 | 10 ms | 33.55× | 29.66× |
| Peng | Apical-q75 | 2 ms | 29.87× | 1.431× |
| Peng | Apical-q75 | 10 ms | 25.75× | 1.366× |
| Tamas | Soma | 2 ms | 41.29× | 1.032× |
| Tamas | Soma | 10 ms | 30.13× | 1.031× |
| Tamas | Basal-q75 | 2 ms | 33.13× | 1.0007× |
| Tamas | Basal-q75 | 10 ms | 26.74× | 1.0007× |
| Tamas | Apical-q75 | 2 ms | 28.34× | 0.9995× |
| Tamas | Apical-q75 | 10 ms | 24.34× | 0.9993× |

For Tamas, the weighted spectral ratio stays around 24–41× while transient ratios remain essentially one (or about 1.03 for soma). For Peng, the soma and basal transient penalties are reflected in both metrics, but the apical source has a much smaller transient penalty than its spectral ratio suggests.

Paired log-ratio correlations by source/pulse are weak overall. The continuous-time spectral weighted error is therefore not a sufficient predictor of the discrete finite-window transient NRMSE.

## Interpretation limits

The frequency grid is band-limited to 5 kHz (Nyquist for dt=0.1 ms), and the ideal rectangular pulse spectrum uses (|\mathrm{sinc}(fT)|^2). This does not model the exact finite-step backward-Euler recurrence or finite observation window. Ratios can be large because the seven-port denominator is very small; absolute errors are preserved in the CSVs. The analysis is passive linear-RC only, based on two individual reconstructions, not biology or populations. Full Hines remains canonical; no production defaults changed.
