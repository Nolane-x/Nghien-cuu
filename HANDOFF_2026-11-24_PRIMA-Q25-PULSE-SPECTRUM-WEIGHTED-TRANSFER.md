# Handoff — PRIMA q25 pulse-spectrum-weighted transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-pulse-spectrum-weighted-transfer-audit-2026-11-24  
**Parent:** transfer-frequency localization / PR #25

## Research question

The frequency-localization audit shows that AC and transient errors do not track one another identically, especially for the Tamas morphology at order 168. This experiment computes a pulse-spectrum-weighted complex transfer error for the exact 2 ms and 10 ms current pulses and compares it pairwise with archived transient NRMSE.

## Design

Two pinned morphologies; seven-port and dual-q25 layouts; order 168; nine passive parameter scenarios; three source locations; seven shared outputs. Full-Hines and reduced PRIMA transfer responses are computed on a nonuniform grid from DC to 5 kHz, with 10 Hz spacing through 500 Hz and 100 Hz spacing above, plus very-low-frequency points. The band limit is Nyquist for dt=0.1 ms.

For a rectangular pulse width T, the spectral power weighting is (|sinc(fT)|^2). The weighted transfer error is the square root of the frequency integral of squared complex transfer residual times pulse spectral power, divided by the corresponding full-Hines transfer energy. The result is compared with the exact stored 2 ms/10 ms time-domain NRMSE rows for the same scenario, source and output.

This is a band-limited spectral proxy; it is not claimed to equal the finite 20 ms transient NRMSE.

## Expected exact coverage

- 74,088 frequency/source/output/layout/scenario rows.
- 1,512 pulse-weighted output rows.
- 168 output summaries and 24 source summaries.
- 756 paired dual-q25/seven weighted-transfer and transient rows.
- 12 source/pulse comparison summaries.
- Two pulse widths and 98 frequency samples.

## Scientific limits

Passive linear-RC only, two individual morphology reconstructions, no biological or population inference. The 5 kHz band limit and ideal rectangular-pulse spectrum are explicit approximations. Full Hines remains canonical; no production code/default changes.
