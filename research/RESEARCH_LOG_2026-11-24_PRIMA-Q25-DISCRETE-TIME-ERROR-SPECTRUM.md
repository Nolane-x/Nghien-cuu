# Research log — PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Parent checkpoint:** PR #28

## Question

Which frequency bands contain the error in actual finite-window backward-Euler output traces for seven-port and dual-q25 nine-port PRIMA models?

## Sources examined

- Repository instructions in \`AGENTS.md\`.
- PR #28 and its validated 200-ms extended backward-Euler tail report.
- The pulse-weighted continuous-time transfer bridge and its stated scientific limits.
- Peng four-layout ablation, Tamas four-layout replication, cross-morphology source/output map and Krylov-prefix transfer audit.
- Existing exact-Hines and reduced backward-Euler implementation.

## Rationale

The continuous-time pulse-weighted AC bridge did not reconcile Tamas's large AC residual ratio with near-unity finite-window transient NRMSE. Extending the transient to 200 ms did not resolve the discrepancy. A finite-window DFT of the actual transient error gives an exact Parseval decomposition of the already measured time-domain quantity, without treating a continuous-time transfer proxy as equivalent to the sampled recurrence.

## Work authored

- Added an analysis that reuses the existing exact Hines and reduced backward-Euler protocol for both pinned morphologies, both layouts, all passive scenarios, sources, pulses, outputs and windows.
- Added four non-overlapping frequency bands with exact one-sided real-FFT Parseval weighting.
- Added per-trace Parseval checks, direct NRMSE consistency checks, exact row-count checks and archived 20-ms parity validation.
- Added focused unit tests and a GitHub Actions workflow.
- No production model, solver or default was changed.

## Execution record

Pending GitHub Actions. Tests, preflights, numerical results, runtime and commit SHA are not claimed until the run completes.

## Expected outputs

\`prima_q25_discrete_time_error_spectrum_2026-11-24_band_energy.csv\`, \`_band_comparisons.csv\`, \`_layout_band_summary.csv\`, \`_comparison_band_summary.csv\`, \`_20ms_parity.csv\` and \`_report.json\`.

The script records exact expected row counts and reads each output CSV back before marking the run successful.

## Limitations and next step

This is an exact spectral decomposition of finite-window output-error samples, not a transfer-function solver or biological validation. DFT resolution depends on window length. After CI, inspect absolute errors and energy shares as well as ratios. If the AC/transient discrepancy remains, formulate a separate discrete-time transfer-response test.
