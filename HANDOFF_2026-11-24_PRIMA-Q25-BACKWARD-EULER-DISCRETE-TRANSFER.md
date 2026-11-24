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



## Validated update — 24 November 2026

The perturbation-coordinate implementation passed the exact finite-record DFT identity and the full-morphology workflow:

- Workflow [45419651741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45419651741): identity max \(1.43235\times10^{-11}\), below \(2\times10^{-8}\), 864 identity rows; result commit \`709385e\`.
- Workflow [45420670698](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45420670698): **9 focused tests passed**; both morphology SHA-256 checks and preflights passed; complete computation, identity gate, result commit and artifact upload passed. Result commit \`1d6f64a83ccc7d1310a19baa50b2bc9b738dd7f5\`; artifact 14934013973, digest \`4233f555deadac71f7109a8928c0a0a015f6f5bd77d54a2d48e0db0907a25e50\`.

### Main corrected finding

The seven/nine transient comparison must use the perturbation-coordinate full-Hines replay for these tiny residuals. Tamas' legacy absolute-voltage metric suggested near parity (1.001–1.029×), but its absolute-vs-perturbation discrepancy reached \(2.6494\times10^{-6}\%\). The stable metric instead gives median nine/seven ratios of 24.55×, 55.28×, 31.94× and 31.64× at 20/40/100/200 ms. Peng's corresponding stable ratios are 138.34×, 69.78×, 33.67× and 33.43×. The exact table and aggregation method are in the research report.

Absolute nine-port perturbation-coordinate NRMSE remains extremely small (about \(10^{-9}\%\) to \(10^{-8}\%\)). These are relative numerical error ratios, not a biological-performance claim.

At 20–40 ms, the terminal-state boundary component can exceed the finite-error norm because it cancels the periodic transfer-error component; by 100–200 ms its norm falls to about 2.2–2.4% and then about 0.005%. Thus the finite-pulse transient cannot be inferred from \(H_{BE}U\) alone.

The code now adds an eight-row morphology × window CSV and embeds the same summary in report.json. The table also records the terminal-boundary component norm and the count of perturbation-coordinate transient pairs worse than seven-port. Workflow 45422624509 passed 10/10 tests and all six CSV read-backs.

## Next concrete step

Next: use the validated perturbation-coordinate formulation to run a backward-Euler timestep-refinement audit (0.1/0.05/0.025 ms) on these same two morphologies, preserving full Hines as reference. Keep PR #30 draft and do not merge without explicit authorization.

