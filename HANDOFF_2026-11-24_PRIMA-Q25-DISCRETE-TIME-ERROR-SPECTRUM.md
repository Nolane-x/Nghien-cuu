# Handoff — PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Parent:** PR #28, extended backward-Euler tail audit  
**Implementation commit:** \`7456a0a3cb3b2fff9b97b84631c3380af537af24\`  
**Result commit:** \`5ee268a30506af0a823b7e9c53f1c1bbcd44c571\`  
**Successful workflow:** [45400459091](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091)  
**Artifact:** [prima-q25-discrete-time-error-spectrum](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091/artifacts/14922946868)

## Research question

Decompose the actual 0.1-ms backward-Euler output-error traces into finite-window DFT bands to identify which frequency bands contribute to the transient error across the Peng and Tamas morphologies, source sites, pulse widths and 20/40/100/200-ms windows.

## Method

- Reuse the exact full-Hines and reduced backward-Euler simulation functions from the validated tail audit.
- Preserve both checksum-pinned morphologies, seven-/nine-port layouts, order 168, all nine passive scenarios, three sources, both pulse widths and seven exact shared output SWC nodes.
- Apply a real FFT to each actual finite-window output-error trace.
- Use one-sided Parseval weights: DC and Nyquist weight one; interior positive bins weight two.
- Partition all frequency bins into 0–100, 100–500, 500–2,000 and 2,000–5,000 Hz.
- Require band energy to reproduce time-domain squared error within relative tolerance 5e-12.
- Recheck all 1,512 archived 20-ms parity rows against the existing 5e-8 percentage-point absolute tolerance.
- Do not change production solver code or defaults.

## Validation

Workflow 45400459091 succeeded. Seven focused tests passed in 0.47 s; both SWC checksums and both preflights passed. Exact read-back counts: 6,048 traces, 24,192 band-energy rows, 12,096 band comparisons, 384 layout summaries, 192 comparison summaries and 1,512 archived parity rows. Maximum Parseval relative error: 1.0416081604643047e-15. Maximum archived 20-ms absolute delta: 3.0818710679657265e-8 percentage points (gate: 5e-8).

## Main findings

- Peng: the main nine-port error-energy band moves from 100–500 Hz at 20 ms (median 78.33% share) to 0–100 Hz by 40 ms (86.32%) and 100–200 ms (about 98.9%). The median nine/seven ratio in the 0–100 Hz band is 11.48×, 35.75×, 26.35× and 23.11× at 20/40/100/200 ms. Absolute band NRMSE remains very small.
- Tamas: 0–100 Hz carries 94.09–99.71% of nine-port error energy from 20 to 200 ms; its median nine/seven ratio in that band stays 1.00–1.03×. Higher bands account for little error energy.
- This exact finite-window DFT clarifies where the sampled transient error lies but does not fully explain why the earlier continuous-time AC transfer proxy showed larger relative residuals on Tamas.

See \`amsn-core/research/PRIMA_Q25_DISCRETE_TIME_ERROR_SPECTRUM_2026-11-24.md\` for full tables and caveats.

## Next research step

Derive the discrete-time transfer response of the actual backward-Euler recurrence, including its sample/hold convention, then compare full-Hines and reduced discrete-time responses against the finite-window DFT findings and the existing continuous-time AC proxy. Preserve the full-Hines reference and leave production defaults unchanged until a broader morphology validation supports a change.

## Limits

Only two individual passive linear-RC morphologies have been tested. This is not population or biological validation. Do not interpret relative ratios without absolute error and energy shares.
