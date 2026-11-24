# PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Implementation commit:** \`7456a0a3cb3b2fff9b97b84631c3380af537af24\`  
**Result commit:** \`5ee268a30506af0a823b7e9c53f1c1bbcd44c571\`  
**Workflow:** [45400459091 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091)  
**Artifact:** [prima-q25-discrete-time-error-spectrum](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091/artifacts/14922946868)  
**Artifact ZIP SHA-256:** \`c9c103aa46f688f817e01c6ad645cc9a75996104a2a9d5e3dcd61cfb68582845\`

## 1. Question

Which discrete-frequency bands contribute to the actual finite-window transient error of the dual-q25 nine-port PRIMA model relative to the canonical seven-port model, and does that vary by morphology, input location, pulse width or observation window?

## 2. Why this is a distinct test

The earlier pulse-weighted bridge integrated continuous-time AC transfer residuals against a continuous rectangular-pulse spectrum. It was explicitly a proxy, not an exact reproduction of the finite-step backward-Euler recurrence. The extended-tail audit then replayed the actual 0.1-ms recurrence to 200 ms.

This audit takes the **actual simulated output-error trace** (reduced output minus full-Hines output) and applies a real DFT separately to each finite observation window. It therefore decomposes the measured transient error itself rather than assuming the continuous-time AC proxy is equivalent to the sampled recurrence.

One-sided FFT weights follow Parseval: DC and Nyquist have weight one; interior positive-frequency bins have weight two. Four non-overlapping bands cover the complete 0–5 kHz one-sided spectrum. Per-band absolute error energy, RMS error, contribution to total NRMSE and energy share are retained.

## 3. Fixed protocol

- Morphologies: checksum-pinned NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Layouts: canonical seven-port and dual-q25 nine-port; PRIMA basis order 168.
- All nine existing passive parameter scenarios.
- Sources: soma, basal-q75 and apical-q75; seven exact shared output SWC nodes.
- Pulses: 10 pA, 2 ms onset, widths 2 and 10 ms.
- Backward-Euler timestep: 0.1 ms; observation windows: 20, 40, 100 and 200 ms.
- DFT bands: 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz.
- Frequency resolutions: 50, 25, 10 and 5 Hz at the four respective windows.

The band-energy share shown below is the median of the nine-port trace-level shares, first aggregated over the nine passive scenarios and seven outputs for each source/pulse group, then summarized across the six source × pulse groups. The nine/seven band ratio uses the same nested medians. It is not a ratio of pooled total energies.

## 4. CI validation and exact coverage

Workflow [45400459091](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091) completed successfully:

- 7 dedicated unit tests passed in 0.47 s.
- Both pinned SWC SHA-256 checks passed.
- Both morphology preflights passed.
- Full-Hines and reduced backward-Euler replay completed.
- Parseval, direct NRMSE and archived 20-ms parity gates passed.
- All CSV outputs were read back and their exact row counts matched.
- Numerical outputs were committed and the evidence artifact uploaded.

| Dataset | Expected | Read back |
|---|---:|---:|
| Trace/window records represented in band table | 6,048 | 6,048 |
| Trace-by-band energy rows | 24,192 | 24,192 |
| Paired nine/seven band comparisons | 12,096 | 12,096 |
| Layout/source/pulse/window/band summaries | 384 | 384 |
| Comparison summaries | 192 | 192 |
| Archived 20-ms parity rows | 1,512 | 1,512 |

Maximum Parseval relative error was **1.0416081604643047e-15**, against a limit of **5e-12**. Maximum absolute Parseval discrepancy was **1.8055593228630336e-35 V²·samples**.

The maximum archived 20-ms NRMSE absolute difference was **3.0818710679657265e-8 percentage points**, below the existing **5e-8 percentage-point** tolerance. The maximum relative delta was 21.2146%; this remains a diagnostic because some archived residual denominators are extremely small.

Runtime was **87.90 s wall time**. Environment: Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

## 5. Results

Each table cell is **median nine-port/seven-port band NRMSE ratio / median nine-port error-energy share**. Values are aggregated across the six source × pulse groups as specified above. Ratios must be read beside energy shares and absolute band NRMSE; a large ratio can result from an extremely small seven-port denominator.

### NMO_163775 — Peng mouse Control

| Window | 0–100 Hz | 100–500 Hz | 500–2,000 Hz | 2,000–5,000 Hz |
|---|---:|---:|---:|---:|
| 20 ms | 11.48× / 18.22% | 78.27× / 78.33% | 40.37× / 1.87% | 38.33× / 0.48% |
| 40 ms | 35.75× / 86.32% | 42.49× / 12.39% | 23.92× / 0.45% | 24.01× / 0.12% |
| 100 ms | 26.35× / 98.90% | 47.49× / 1.10% | 2.26× / <0.001% | 1.84× / <0.001% |
| 200 ms | 23.11× / 98.97% | 50.03× / 1.02% | 1.03× / <0.001% | 1.00× / <0.001% |

The dominant error-energy band changes with the observation window. At 20 ms, 100–500 Hz carries a median 78.33% of the nine-port error energy. By 40 ms, 0–100 Hz carries 86.32%; by 100–200 ms it carries approximately 98.9%. The 100–500 Hz band retains a large relative nine/seven ratio (about 47–50×) at 100–200 ms, but its share of nine-port error energy is only about 1%.

For absolute context, the median nine-port 0–100 Hz band NRMSE is approximately 6.96e-8% at 100 ms and 7.02e-8% at 200 ms across the same source/pulse aggregation. These are small absolute residuals; the large ratios are relative to an even smaller seven-port error.

### NMO_107159 — Tamas human pyramidal Control

| Window | 0–100 Hz | 100–500 Hz | 500–2,000 Hz | 2,000–5,000 Hz |
|---|---:|---:|---:|---:|
| 20 ms | 1.00× / 94.09% | 1.02× / 5.07% | 1.00× / 0.71% | 1.00× / 0.19% |
| 40 ms | 1.03× / 97.70% | 1.11× / 1.96% | 1.02× / 0.27% | 1.02× / 0.07% |
| 100 ms | 1.02× / 99.34% | 1.04× / 0.54% | 1.00× / 0.08% | 1.00× / 0.02% |
| 200 ms | 1.01× / 99.71% | 1.03× / 0.24% | 1.00× / 0.04% | 1.00× / 0.01% |

The Tamas nine-port error energy is already concentrated below 100 Hz at 20 ms and becomes even more concentrated there at longer windows. In that dominant band, the median nine/seven ratio remains near one (1.00–1.03×). The 100–500 Hz ratio rises to 1.11× at 40 ms, but that band contributes only 1.96% of the nine-port error energy at that window; higher bands carry still smaller shares.

## 6. Interpretation

1. **The actual sampled transient error is predominantly low-frequency over long windows.** At 100–200 ms, the 0–100 Hz band accounts for approximately 99% of median nine-port error energy in both tested morphologies.
2. **The Peng discrepancy is real in the paired transient metric but remains small in absolute magnitude.** Its nine/seven band ratios are large, with the 0–100 Hz band dominant after 40 ms; by 200 ms the higher-than-500-Hz bands contribute essentially no error energy.
3. **Tamas remains near seven-port parity in the dominant transient band.** Although the earlier continuous-time AC transfer audit found larger relative dual-q25 residuals, those ratios do not appear as a comparable increase in the actual finite-window 0–100 Hz transient error.
4. **This does not yet identify the mechanism behind the AC/transient discrepancy.** The DFT is an exact decomposition of finite output-error samples; it is not a discrete-time transfer-function comparison and cannot show which component of the continuous-time AC proxy fails to predict the sampled response.

A useful next experiment is to derive and compare the exact discrete-time transfer response of the backward-Euler recurrence (including its sample/hold convention) for full-Hines and reduced models. This will directly bridge the discrete-time spectral result and the continuous-time AC calculations without modifying production defaults.

## 7. Scientific limits

Only two individual passive linear-RC morphology reconstructions are included. They are not a species or cell-class population. This does not validate active conductances, synapses, plasticity, excitability or biological fidelity. Shared-output comparisons use only the seven exact common SWC nodes. Large relative ratios must be interpreted alongside absolute NRMSE and band energy. Full Hines remains canonical; no production solver code or defaults were changed.

## 8. Reproducible outputs

Result stem: \`prima_q25_discrete_time_error_spectrum_2026-11-24\`.

- \`band_energy.csv\`: 24,192 trace-by-band energy rows.
- \`band_comparisons.csv\`: 12,096 paired band comparisons.
- \`layout_band_summary.csv\`: 384 layout/source/pulse/window/band summaries.
- \`comparison_band_summary.csv\`: 192 nine/seven summaries.
- \`20ms_parity.csv\`: 1,512 archived parity rows.
- \`report.json\`: method, scope, validation and exact-coverage metadata.

All files are committed under \`amsn-core/results/\`. The downloadable artifact also contains timing and both morphology preflight records.



## Correction note — Tamas q25 transient metric (24 November 2026)

The transient NRMSE values in this report are preserved as originally measured, but their interpretation for the Tamas human pyramidal morphology is superseded by the subsequent exact backward-Euler transfer audit in [PRIMA_Q25_BACKWARD_EULER_DISCRETE_TRANSFER_2026-11-24.md](PRIMA_Q25_BACKWARD_EULER_DISCRETE_TRANSFER_2026-11-24.md), workflow [45420670698](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45420670698).

The earlier Tamas nine/seven transient ratio of approximately 1.00–1.03× came from the canonical full-Hines absolute-voltage replay, which evolves voltages near the leak reversal and then subtracts that offset to obtain a tiny perturbation. The follow-up audit found that the absolute-vs-perturbation Hines trace discrepancy can exceed the PRIMA approximation residual in this tiny-error regime. A second, algebraically equivalent full-Hines replay initialized at zero perturbation and using zero leak source reproduces the linear transfer identity to a maximum relative DFT residual of \(1.43\times10^{-11}\). In that stable coordinate system, Tamas dual-q25 nine/seven transient ratios are about 24.5×, 56.2×, 32.2× and 32.1× at 20/40/100/200 ms.

Therefore, do **not** use the earlier near-unity Tamas ratio as evidence that seven-port and nine-port PRIMA are at parity. The original CSV and numbers remain in the repository for historical reproducibility; the newer perturbation-coordinate analysis provides the corrected interpretation. Absolute errors remain extremely small, and the result is still limited to two individual passive morphologies, not biological validation.

