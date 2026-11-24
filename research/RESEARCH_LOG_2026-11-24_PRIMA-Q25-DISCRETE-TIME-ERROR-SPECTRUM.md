# Research log — PRIMA q25 finite-window discrete-time error spectrum

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-discrete-time-error-spectrum-2026-11-24\`  
**Implementation commit:** \`7456a0a3cb3b2fff9b97b84631c3380af537af24\`  
**Result commit:** \`5ee268a30506af0a823b7e9c53f1c1bbcd44c571\`  
**Workflow:** [45400459091 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091)  
**Artifact:** [run 45400459091 artifact 14922946868](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45400459091/artifacts/14922946868)

## Question

Which frequency bands contain the error in actual finite-window backward-Euler output traces for seven-port and dual-q25 nine-port PRIMA models?

## Sources examined

- Repository instructions in \`AGENTS.md\`.
- PR #28 and its validated 200-ms extended backward-Euler tail report.
- The pulse-weighted continuous-time transfer bridge and its stated scientific limitations.
- Peng four-layout ablation, Tamas four-layout replication, cross-morphology source/output map and Krylov-prefix transfer audit.
- Existing exact-Hines and reduced backward-Euler implementation.

## Rationale

The continuous-time pulse-weighted AC bridge did not reconcile Tamas's larger AC residual ratio with near-unity finite-window transient NRMSE. Extending the transient to 200 ms did not resolve this discrepancy. A finite-window DFT of the actual transient error provides an exact Parseval decomposition of the measured time-domain error, without assuming that a continuous-time transfer proxy is equivalent to the sampled recurrence.

## Implementation

Added \`analyze_prima_q25_discrete_time_error_spectrum.py\`, focused tests and a GitHub Actions workflow. The script reuses the exact Hines and reduced backward-Euler implementation from the extended-tail audit. It keeps both pinned morphologies, seven/nine layouts, order 168, nine passive scenarios, three sources, two pulse widths, seven shared outputs and four observation windows.

The DFT uses DC/Nyquist weight one and interior positive-bin weight two. Four bands partition the complete 0–5 kHz spectrum. The script records absolute band energy, RMS, band NRMSE and energy shares. It validates Parseval per trace, the direct time-domain NRMSE, archived 20-ms parity and CSV read-back counts. No production solver implementation or default was changed.

## CI execution and validation

Workflow 45400459091 succeeded on 24 November 2026:
- 7 dedicated unit tests passed in 0.47 s.
- Both pinned source SHA-256 checks passed.
- Both morphology preflights passed.
- The full finite-window DFT computation passed.
- Result commit and artifact upload passed.

Exact read-back coverage:
- 6,048 trace/window records.
- 24,192 band-energy rows.
- 12,096 paired nine/seven band comparisons.
- 384 layout/source/pulse/window/band summaries.
- 192 comparison summaries.
- 1,512 archived 20-ms parity rows.

Maximum Parseval relative error was 1.0416081604643047e-15 against 5e-12. Maximum absolute 20-ms archived NRMSE delta was 3.0818710679657265e-8 percentage points against 5e-8. The maximum relative parity delta was 21.2146%, retained as a diagnostic because tiny baseline residuals magnify relative differences.

Runtime: 87.90 s wall time. Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2. Artifact ZIP SHA-256: \`c9c103aa46f688f817e01c6ad645cc9a75996104a2a9d5e3dcd61cfb68582845\`.

## Results

The band table values are medians over six source × pulse groups; each source/pulse summary first aggregates nine passive scenarios and seven shared outputs. The value is median nine-port/seven-port band NRMSE ratio / median nine-port error-energy share.

### Peng mouse Control (NMO_163775)

| Window | 0–100 Hz | 100–500 Hz | 500–2,000 Hz | 2,000–5,000 Hz |
|---|---:|---:|---:|---:|
| 20 ms | 11.48× / 18.22% | 78.27× / 78.33% | 40.37× / 1.87% | 38.33× / 0.48% |
| 40 ms | 35.75× / 86.32% | 42.49× / 12.39% | 23.92× / 0.45% | 24.01× / 0.12% |
| 100 ms | 26.35× / 98.90% | 47.49× / 1.10% | 2.26× / <0.001% | 1.84× / <0.001% |
| 200 ms | 23.11× / 98.97% | 50.03× / 1.02% | 1.03× / <0.001% | 1.00× / <0.001% |

### Tamas human pyramidal Control (NMO_107159)

| Window | 0–100 Hz | 100–500 Hz | 500–2,000 Hz | 2,000–5,000 Hz |
|---|---:|---:|---:|---:|
| 20 ms | 1.00× / 94.09% | 1.02× / 5.07% | 1.00× / 0.71% | 1.00× / 0.19% |
| 40 ms | 1.03× / 97.70% | 1.11× / 1.96% | 1.02× / 0.27% | 1.02× / 0.07% |
| 100 ms | 1.02× / 99.34% | 1.04× / 0.54% | 1.00× / 0.08% | 1.00× / 0.02% |
| 200 ms | 1.01× / 99.71% | 1.03× / 0.24% | 1.00× / 0.04% | 1.00× / 0.01% |

## Interpretation

1. For Peng, the dominant nine-port error-energy band changes from 100–500 Hz at 20 ms to 0–100 Hz by 40 ms; at 100–200 ms approximately 99% of the energy is below 100 Hz. The nine/seven ratios are high, but the absolute residuals remain very small.
2. For Tamas, 0–100 Hz already accounts for 94.09% of energy at 20 ms and 99.71% at 200 ms, while the nine/seven ratio in that dominant band remains approximately one.
3. The higher-frequency AC transfer ratios from earlier work do not translate into comparably large error energy in the sampled transient traces. This narrows the discrepancy but does not identify its mechanism.
4. The DFT is a decomposition of sampled output-error traces, not a new transfer function. It cannot by itself establish why the continuous-time AC proxy differs.

## Next experiment

Derive the exact discrete-time transfer response of the actual backward-Euler recurrence, including sample/hold conventions, and compare full-Hines and reduced responses. This is the appropriate next bridge between continuous-time AC calculations and sampled transient behavior. Keep full Hines canonical and do not change production defaults based on the two-morphology passive study.

## Limits

Only two individual passive linear-RC morphology reconstructions are compared, not populations. No active-neuron, synaptic, plasticity or biological validation is claimed. Relative ratios can be large when the seven-port baseline is extremely small; absolute band NRMSE and energy shares remain necessary context.
