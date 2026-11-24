# Handoff — PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Parent:** PR #28, extended backward-Euler tail audit  
**Execution:** pending GitHub Actions

## Research question

Decompose the actual 0.1-ms backward-Euler output-error traces into finite-window DFT bands to determine which bands contribute to measured transient error across the Peng and Tamas morphologies, source sites, pulse widths and 20/40/100/200-ms windows.

## Method and safeguards

- Reuse the exact full-Hines and reduced backward-Euler simulation functions from the validated tail audit.
- Preserve both checksum-pinned morphologies, seven-/nine-port layouts, order 168, nine passive scenarios, three sources, both pulse widths and seven exact shared output SWC nodes.
- Apply a real FFT to each actual finite-window output-error trace.
- Use one-sided Parseval weights: DC and Nyquist weight one; interior bins weight two.
- Partition all bins into 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz.
- Require band energy to reproduce the time-domain squared error within relative tolerance 5e-12.
- Recheck all 1,512 archived 20-ms parity rows against the existing 5e-8 percentage-point absolute tolerance.
- Do not change production solver code or defaults.

## Expected coverage

6,048 output traces; 24,192 band-energy rows; 12,096 paired band comparisons; 384 layout band summaries; 192 comparison band summaries; 1,512 archived parity rows.

## Files

- \`amsn-core/research/analyze_prima_q25_discrete_time_error_spectrum.py\`
- \`amsn-core/tests/test_prima_q25_discrete_time_error_spectrum.py\`
- \`.github/workflows/amsn-prima-q25-discrete-time-error-spectrum.yml\`
- \`amsn-core/research/PRIMA_Q25_DISCRETE_TIME_ERROR_SPECTRUM_2026-11-24.md\`
- \`research/RESEARCH_LOG_2026-11-24_PRIMA-Q25-DISCRETE-TIME-ERROR-SPECTRUM.md\`

## Status and limits

Implementation and workflow are authored; numerical execution is pending. Do not claim tests or results until Actions confirms them. This remains passive linear-RC numerical work on two individual reconstructions, not population or biological validation.

## Next step

Read the workflow report and CSVs. Present band shares and absolute band NRMSE beside ratios. If the finite-window decomposition still differs from continuous-time AC transfer scoring, keep both findings explicit and design a separate discrete-time transfer-response test.
