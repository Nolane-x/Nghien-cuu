# Handoff — PRIMA q25 pulse-spectrum-weighted transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-spectrum-weighted-transfer-audit-2026-11-24  
**Parent:** transfer-frequency localization / PR #25  
**Successful workflow:** [45381680741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741)  
**Result commit:** `6274a6dd4106d421aeda48ab4bbb7c5d76da5e60`  
**Artifact:** [prima-q25-pulse-spectrum-weighted-transfer](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741/artifacts/14914850862), SHA-256 `a572b412e7c2515862097585ae38c744243803ed70deece1b970bfd01bf36cfc`

## Research question

The frequency-localization audit shows that AC and finite-window transient error do not track one another identically, especially for the Tamas morphology at order 168. This experiment computes a pulse-spectrum-weighted complex transfer error for ideal 2 ms and 10 ms current pulses and compares it pairwise with the archived transient NRMSE.

## Design

Two checksum-pinned morphologies; seven-port baseline and dual-q25 nine-port; order 168; nine passive scenarios; three sources; seven shared outputs.

The transfer grid contains 98 nonuniform frequencies:
- DC, 0.1 and 1 Hz;
- 10–500 Hz in 10-Hz increments;
- 600–5,000 Hz in 100-Hz increments.

For pulse width (T), the spectral power weighting is (|\mathrm{sinc}(fT)|^2). The weighted complex transfer residual is integrated with the trapezoidal rule and paired with the exact saved 20-ms transient row for the same scenario, source, pulse and shared SWC output.

The transient join deliberately keeps only the seven SWC outputs shared by the seven-port and nine-port layouts. The two q25-only output rows in the nine-port transient file are excluded from the paired comparison.

## Verified execution and exact coverage

Workflow 45381680741 completed successfully:
- 6/6 focused tests passed.
- Both SWC SHA-256 checks and both morphology preflights passed.
- The 98-point transfer grid was evaluated and all outputs were committed.
- The artifact was uploaded successfully.

| Dataset | Expected | Read-back |
|---|---:|---:|
| AC frequency rows | 74,088 | 74,088 |
| Pulse-weighted shared-output rows | 1,512 | 1,512 |
| Weighted output summaries | 168 | 168 |
| Weighted source summaries | 24 | 24 |
| Paired spectral/transient rows | 756 | 756 |
| Paired source/pulse summaries | 12 | 12 |
| Pulse-spectrum samples | 196 | 196 |
| Matched transient input rows (7 shared outputs only) | 1,512 | 1,512 |

Runtime: 92.23 s wall, 109.95 s user CPU, 228,764 KB maximum RSS. Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## Main finding

The pulse-weighted continuous-time transfer metric remains much larger than the transient NRMSE ratio on Tamas, so pulse-spectrum weighting alone does not reconcile the AC/transient gap.

Median candidate/seven weighted-transfer ratio and median transient NRMSE ratio by source:

| Morphology | Source | Pulse | Weighted-transfer ratio | Transient ratio |
|---|---|---:|---:|---:|
| Peng mouse | Soma | 2 ms | 41.01× | 58.84× |
| Peng mouse | Soma | 10 ms | 34.05× | 60.23× |
| Peng mouse | Basal-q75 | 2 ms | 39.59× | 33.20× |
| Peng mouse | Basal-q75 | 10 ms | 33.55× | 29.66× |
| Peng mouse | Apical-q75 | 2 ms | 29.87× | 1.431× |
| Peng mouse | Apical-q75 | 10 ms | 25.75× | 1.366× |
| Tamas human pyramidal | Soma | 2 ms | 41.29× | 1.032× |
| Tamas human pyramidal | Soma | 10 ms | 30.13× | 1.031× |
| Tamas human pyramidal | Basal-q75 | 2 ms | 33.13× | 1.0007× |
| Tamas human pyramidal | Basal-q75 | 10 ms | 26.74× | 1.0007× |
| Tamas human pyramidal | Apical-q75 | 2 ms | 28.34× | 0.9995× |
| Tamas human pyramidal | Apical-q75 | 10 ms | 24.34× | 0.9993× |

The paired source-level log-ratio correlations are weak (Pearson and Spearman mostly near zero). The ratios are relative to very small seven-port denominators; they must be read alongside absolute errors, which are retained in the detailed output tables.

## Interpretation limits

This is a band-limited continuous-time spectral proxy, not an exact reproduction of the 0.1-ms finite-step backward-Euler solver or its 20-ms observation window. It omits finite-window leakage and discrete-time recurrence effects. It does not establish active-neuron, biological or population-level validity.

The result is a negative finding: rectangular-pulse spectral weighting, on its own, is not a sufficient predictor of finite-window transient NRMSE. Full Hines remains canonical; no production defaults changed.
