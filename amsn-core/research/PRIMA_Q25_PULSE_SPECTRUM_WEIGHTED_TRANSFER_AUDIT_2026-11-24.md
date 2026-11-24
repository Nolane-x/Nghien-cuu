# PRIMA q25 pulse-spectrum-weighted transfer audit

**Date:** 24 November 2026  
**Workflow:** [45381680741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741) — success  
**Result commit:** `6274a6dd4106d421aeda48ab4bbb7c5d76da5e60`  
**Artifact:** [prima-q25-pulse-spectrum-weighted-transfer](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45381680741/artifacts/14914850862)  
**Artifact SHA-256:** `a572b412e7c2515862097585ae38c744243803ed70deece1b970bfd01bf36cfc`

## 1. Aim

The preceding transfer-stage analysis showed dual-q25 AC transfer error above seven-port on both Peng and Tamas, while the finite 20-ms transient NRMSE was 14.525× on Peng but 1.001× on Tamas. This audit applies the spectra of 2-ms and 10-ms rectangular current pulses to the complex transfer residuals, then joins the weighted output errors to the exact archived transient observations.

## 2. Method

- Morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Layouts: canonical seven-port and dual-q25 nine-port.
- Basis order: 168.
- Nine passive parameter scenarios, three input sources and seven shared output nodes.
- Pulse: 10 pA rectangular current, 2-ms and 10-ms widths, 2-ms onset.
- Frequency grid: 98 nonuniform points from DC to 5,000 Hz; Nyquist for dt=0.1 ms.
- Weight: (|I(f)|^2) proportional to (|\mathrm{sinc}(fT)|^2).
- Integral: trapezoidal over the sampled frequency grid.

The transfer error metric is a weighted relative L2 norm:
[
100\sqrt{\frac{\int_0^{5\mathrm{kHz}}|H_9(f)-H_{\mathrm{Hines}}(f)|^2|\mathrm{sinc}(fT)|^2 df}{\int_0^{5\mathrm{kHz}}|H_{\mathrm{Hines}}(f)|^2|\mathrm{sinc}(fT)|^2 df}}
]
This is not the finite-window backward-Euler NRMSE. The two metrics are compared empirically rather than treated as interchangeable.

Only the seven shared output SWC node IDs are paired. The two q25-only output rows from the nine-port transient CSV are excluded explicitly.

## 3. Validation and exact coverage

The workflow passed 6 focused tests, both SWC SHA-256 checks, both Import3D preflights, the transfer computation, result commit and artifact upload.

| Dataset | Expected | Verified |
|---|---:|---:|
| AC frequency rows | 74,088 | 74,088 |
| Pulse-weighted shared-output rows | 1,512 | 1,512 |
| Weighted output summaries | 168 | 168 |
| Weighted source summaries | 24 | 24 |
| Paired spectral/transient rows | 756 | 756 |
| Paired source/pulse summaries | 12 | 12 |
| Pulse-spectrum samples | 196 | 196 |
| Shared transient input rows | 1,512 | 1,512 |

Runtime: 92.23 s wall, 109.95 s user CPU, 228,764 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## 4. Main result — pulse weighting does not reconcile AC and transient errors

Median candidate/seven ratios by source:

| Morphology | Source | Pulse | Weighted-transfer ratio | Transient NRMSE ratio |
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

On Tamas, weighted spectral ratios remain roughly 24–41×, even though time-domain transient ratios stay very close to one. The Peng soma/basal transient degradation is reflected in the weighted spectral metric, but the apical source's time-domain penalty is far smaller than the corresponding spectral ratio. Pearson/Spearman log-ratio correlations are generally weak, so the frequency-integrated proxy does not predict the finite-window transient metric reliably.

## 5. Absolute-error and interpretation caveat

The denominator is the seven-port weighted transfer error, which is often extremely small. Therefore, ratios of 20–40× must not be interpreted as large absolute voltage or transfer failures. The detailed output CSV retains the absolute weighted error values, unweighted transfer errors and exact transient pair values for independent inspection.

This is a useful negative finding: continuous-time rectangular-pulse spectral weighting, using the sampled band-limited frequency grid, does not explain the AC/transient discrepancy on the Tamas morphology. The likely missing pieces are the exact discrete-time backward-Euler recurrence and finite observation-window behavior, which are the subject of the separate extended-tail experiment.

## 6. Scientific limitations

This is passive linear-RC numerical validation only. The two morphologies are individual reconstructions, not species/cell-class populations. The ideal rectangular pulse spectrum and 5-kHz band limit are approximations, not a full model of finite-step finite-window integration. No biological validation is claimed. Full Hines remains canonical; production code and defaults are unchanged.

## 7. Reproducible outputs

Result stem: `prima_q25_pulse_spectrum_weighted_transfer_2026-11-24`.

- `frequency.csv`: 74,088 sampled source/output frequency responses.
- `pulse_spectrum_samples.csv`: 196 pulse-spectrum samples.
- `weighted_output.csv`: 1,512 weighted output records.
- `weighted_output_summary.csv`: 168 summaries.
- `weighted_source_summary.csv`: 24 summaries.
- `vs_seven_time_domain_pairs.csv`: 756 exact paired rows.
- `vs_seven_source_summary.csv`: 12 source/pulse summaries.
- `report.json` and `.time.txt`.

Verified Git blob SHA-1:
- report JSON: `9eb757fef99984e96bb0b75e8c987a2dc4fddb59`
- frequency CSV: `a8967c7d9092d8fd9961e81af0db02903b0f6bab`
- pulse-spectrum samples: `6c6ba38fa9ca79f206ff7ea2e3324072ea124f35`
- vs-seven source summary: `683a3367e19847b16140cabeb4e511345e965865`
- vs-seven time-domain pairs: `6f65003eb5a9d02d93844a8b4e3a6e7a5ea5ee3d`
- weighted output summary: `d907c65209119b2e592733beffa008e402aa5dc2`
- weighted source summary: `61c09f7f785bcac164b0ecff56cf7b2dc8c7874a`
- timing file: `385a5186f53a3d712435eda4ba05eac9c39d94fa`
