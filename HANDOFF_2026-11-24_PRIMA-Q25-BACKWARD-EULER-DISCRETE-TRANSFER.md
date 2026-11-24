# Handoff — exact backward-Euler discrete-time transfer for PRIMA q25

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-discrete-transfer-2026-11-24\`  
**Parent:** PR #29, finite-window DFT audit  
**Execution:** pending GitHub Actions

## Question

Derive the exact discrete-time transfer of the backward-Euler state recurrence and test whether its comparison with the continuous-time AC proxy better explains the mismatch observed on Tamas. Verify the finite-record DFT identity including the terminal-state term.

## Method

- Use \(s_{BE}=(1-e^{-j2\pi f\Delta t})/\Delta t\), giving \(H_{BE}=L(G+s_{BE}C)^{-1}B\).
- Keep \(u[n]\) held over \([n\Delta t,(n+1)\Delta t)\); \(x[n]\) is the state at the interval end.
- Use the exact zero-order-hold Fourier factor for the continuous-AC comparator.
- For each finite window, retain \(x[N-1]\) and verify
  \[
  X=(G+(1-e^{-j\Omega})C/\Delta t)^{-1}(BU-(C/\Delta t)x[N-1]).
  \]
- Compare both layouts against full Hines for the same source/output, then join continuous-AC, discrete-BE and actual finite-transient metrics.

## Expected outputs

- 84,084 frequency-summary rows.
- 6,048 case-level transfer/transient metrics.
- 3,024 paired nine/seven rows.
- 48 source/window summaries.
- 864 finite-record identity summaries.

## Status and next step

Implementation and tests are authored; numerical execution is pending. Do not claim a result until Actions passes, commits the CSVs and the report is read back. The next possible step is to inspect discrete/continuous ratio changes and quantify how much of the finite-record difference comes from the terminal state, then extend to additional morphology holdouts only if justified.

## Scientific limits

Only two individual passive linear-RC morphologies. No production solver code/defaults changed. Relative error ratios need absolute weighted norms. Full Hines remains canonical.
