# Handoff — exact backward-Euler discrete-time transfer for PRIMA q25

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-discrete-transfer-2026-11-24\`  
**Parent:** PR #29, finite-window DFT audit  
**Execution:** pending GitHub Actions

## Question

Derive the exact discrete-time transfer of the backward-Euler state recurrence and test whether its comparison with the continuous-time AC proxy better explains the mismatch observed on Tamas. Verify the finite-record DFT identity including the terminal-state term.

## Method

At a 0.1-ms timestep, the backward-Euler map compresses the imaginary frequency by 6.45% at 1 kHz and 24.32% at 2 kHz; at Nyquist 5 kHz the mapped shift is purely real. Keep this numerical damping/frequency warping separate from PRIMA approximation error.

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

Run 45417410370 completed the computation and wrote 864 identity rows, but the output-scaled identity residual still reached 2.737742435e-8 versus the 2e-8 gate. The maximum is localized to full-Hines on Tamas; reduced-PRIMA identity stayed below 1.14e-13 and Peng full-Hines below 6.39e-10. A likely cause is the numerical difference between the canonical absolute-voltage replay (followed by subtracting E_leak) and the perturbation-coordinate linear transfer. The code now performs an additional full-Hines replay from zero perturbation with zero leak source for the DFT identity, retains the absolute-voltage replay for the historical transient NRMSE and records their difference explicitly. Eight focused tests were already authored; the old-coordinate eight-test run was in progress at the last check, and the new perturbation-coordinate full replay is queued. Diagnostic artifact 14932942667 from run 45417410370 is preserved. Do not accept transfer/boundary conclusions until the new identity check passes, the absolute-vs-perturbation delta is examined, and every CSV count reads back.

The eight-test validation on the previous absolute-coordinate implementation (run 45417470042) reproduced the same 2.737742435e-8 maximum and uploaded artifact 14934170131 (SHA-256 a1f6b09189c9c703c336cab1d61d10feeea196802265470a2f407d82191e67ea). It does not include the perturbation-coordinate fix. The next possible step is to inspect discrete/continuous ratio changes and quantify how much of the finite-record difference comes from the terminal state, then extend to additional morphology holdouts only if justified.

## Scientific limits

Only two individual passive linear-RC morphologies. No production solver code/defaults changed. Relative error ratios need absolute weighted norms. Full Hines remains canonical.
