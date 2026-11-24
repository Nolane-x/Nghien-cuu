# PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Parent checkpoint:** PR #28 extended backward-Euler tail audit

## Question

Which discrete-frequency bands contribute to the actual finite-window transient error of the dual-q25 nine-port PRIMA model relative to the canonical seven-port model, and does that vary by morphology, input location, pulse width or observation window?

## Method

The earlier pulse-weighted bridge integrated continuous-time AC transfer residuals against a continuous rectangular-pulse spectrum. That was a proxy, not an exact reproduction of the finite-step backward-Euler recurrence. This audit instead takes the **actual simulated output error trace** (reduced output minus full-Hines output) and applies a real DFT separately to each finite observation window.

One-sided FFT weights follow Parseval: DC and Nyquist have weight one; interior positive-frequency bins have weight two. Four non-overlapping bands cover 0–5 kHz. Each band's absolute error energy, RMS error, contribution to total NRMSE and share of total error energy are reported. Their sum must reproduce the time-domain squared error within a relative tolerance of \(5\\times10^{-12}\). The 20-ms replay must also reproduce archived transient rows within the existing \(5\\times10^{-8}\) NRMSE percentage-point absolute tolerance.

## Fixed protocol

- Two checksum-pinned morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Seven-port baseline and dual-q25 nine-port layout; PRIMA basis order 168.
- All nine passive parameter scenarios; three sources; seven exact shared output SWC nodes.
- 10-pA pulses, 2-ms onset, pulse widths 2 and 10 ms.
- Backward-Euler timestep 0.1 ms; observation windows 20, 40, 100 and 200 ms.
- Frequency bands: 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz.

## Execution status

Pending GitHub Actions. No numerical conclusion is claimed until the workflow completes and outputs are read back.

Expected coverage:
- 6,048 trace rows;
- 24,192 trace-by-band energy rows;
- 12,096 paired nine/seven band comparisons;
- 384 layout/source/pulse/window/band summaries;
- 192 comparison summaries;
- 1,512 archived 20-ms parity rows.

## Interpretation limits

This is a spectral decomposition of finite-window **output-error traces**, not a transfer-function reconstruction. DFT resolution changes with observation window (50, 25, 10 and 5 Hz). Large ratios may reflect very small seven-port error denominators; absolute band NRMSE and energy shares must be considered alongside ratios.

Only two individual passive linear-RC morphologies are included. This is not population-level, active-neuron or biological validation. Full Hines remains canonical; no production solver defaults are changed.
