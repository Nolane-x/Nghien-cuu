# Exact backward-Euler discrete-time transfer for PRIMA q25

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-discrete-transfer-2026-11-24\`  
**Parent checkpoint:** PR #29, finite-window discrete-time error spectrum  
**Execution:** pending GitHub Actions

## Research question

Does the exact discrete-time transfer function of the backward-Euler recurrence change the q25 seven-port/nine-port comparison relative to the prior continuous-time AC transfer proxy, and can its finite-record output DFT be reconstructed exactly when the terminal-state correction is included?

## Exact model

For passive cable matrices \(G,C\), port injection \(B\), output selector \(L\), step \(\Delta t\), and current sample \(u[n]\) held constant during \([n\Delta t,(n+1)\Delta t)\):

\[
(G+C/\Delta t)x[n]-(C/\Delta t)x[n-1]=Bu[n].
\]

The discrete transfer from current samples to the end-of-step voltage samples is

\[
H_{BE}(e^{j\Omega})=
L\left(G+\frac{1-e^{-j\Omega}}{\Delta t}C\right)^{-1}B,
\qquad \Omega=2\pi f\Delta t.
\]

Thus backward-Euler evaluates the continuous resolvent at the complex frequency

\[
s_{BE}(f)=\frac{1-e^{-j2\pi f\Delta t}}{\Delta t},
\]

not at \(j2\pi f\). In components, \(\Re(s_{BE})=(1-\cos\Omega)/\Delta t\) is a positive numerical-damping term and \(\Im(s_{BE})=\sin\Omega/\Delta t\) is the warped angular frequency. For \(\Delta t=0.1\) ms:

| Frequency | Re(s_BE) (s⁻¹) | Im(s_BE) (s⁻¹) | Continuous ω (s⁻¹) | Imaginary-frequency compression |
|---:|---:|---:|---:|---:|
| 100 Hz | 19.73 | 627.91 | 628.32 | 0.066% |
| 500 Hz | 489.43 | 3,090.17 | 3,141.59 | 1.637% |
| 1,000 Hz | 1,909.83 | 5,877.85 | 6,283.19 | 6.451% |
| 2,000 Hz | 6,909.83 | 9,510.57 | 12,566.37 | 24.317% |
| 5,000 Hz (Nyquist) | 20,000.00 | 0.00 | 31,415.93 | 100% |

The BE transfer therefore differs materially from the continuous AC transfer near the upper part of this sampled band even before model reduction is considered. This is a mathematically expected discretization effect, not evidence of a morphology-specific defect. For the finite record beginning at rest, the terminal state cannot be discarded:

\[
\left(G+\frac{1-e^{-j\Omega}}{\Delta t}C\right)X
=BU-\frac{C}{\Delta t}x[N-1].
\]

This audit explicitly evaluates the boundary term and compares its reconstruction with the actual output DFT. The discrete transfer-only term \(H_{BE}U\) is a periodic/circular-record component; it is not silently equated with a zero-state finite pulse trace.

## Scope

- Checksum-pinned NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Canonical seven-port versus dual-q25 nine-port, PRIMA basis order 168.
- All nine passive parameter scenarios; three sources; seven exact shared output SWC nodes.
- 10-pA pulses, 2-ms onset, widths 2 and 10 ms.
- Backward-Euler timestep 0.1 ms; observation windows 20, 40, 100 and 200 ms.
- Frequency grid 0–5 kHz, 5-Hz master spacing; shorter-window DFT grids are exact subsets.
- Continuous AC comparator uses the same sampled pulse passed through the exact zero-order-hold Fourier factor.

## Validation design

1. Verify both SWC hashes and both morphology preflights.
2. Test the BE frequency map, exact ZOH pulse spectrum, finite-window boundary identity and metric invariants.
3. Construct full-Hines and reduced-model continuous and discrete responses on the same frequency grid.
4. Replay the exact backward-Euler pulse protocol and record each window's terminal state.
5. Reconstruct every finite output DFT from \(H_{BE}U\) plus its terminal correction.
6. Save per-frequency summaries, case-level metrics, paired seven/nine comparisons, source/window summaries and identity checks.
7. Read back all CSV row counts and preserve the workflow artifact.

**Execution status:** run [45416403878](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45416403878) first exposed the ill-conditioned inter-model-residual normalization (5.05389). The next run [45417410370](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45417410370) completed the full computation and wrote all 864 identity diagnostics, but the better-scaled output-waveform residual still reached 2.737742435e-8 against the 2e-8 gate. This maximum came from the full-Hines replay on Tamas; reduced-PRIMA identity residuals stayed below 1.14e-13. Peng full-Hines residuals stayed below 6.39e-10. The trace comparison indicates a likely numerical-coordinate issue: the canonical transient evolves absolute voltages and subtracts E_leak, whereas the linear transfer is defined on V-E_leak. A second full-Hines replay in perturbation coordinates has now been added for the identity check, while the canonical absolute-voltage trace remains the transient-NRMSE reference. Run [45417470042](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45417470042) was concurrently validating the eight-test suite on the earlier absolute-coordinate code; the new perturbation-coordinate replay is queued in run [45419651741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45419651741). The 864-row diagnostic artifact from run 45417410370 is preserved (artifact 14932942667, SHA-256 4cf890875ee023588491f59a9cd482a6cba8c951be422aecb4db182bc24567d7). No new transfer or boundary conclusion is accepted until the perturbation-coordinate replay passes and its coordinate delta is reviewed.

Run 45417470042 then repeated the same maximum (2.737742435e-8 vs 2e-8) after the new scale-normalization test passed; the workflow ran the eight-test suite and uploaded artifact 14934170131 (ZIP SHA-256 a1f6b09189c9c703c336cab1d61d10feeea196802265470a2f407d82191e67ea). It used the prior absolute-voltage replay, so it is not a validation of the perturbation-coordinate change.

Expected coverage:
- 84,084 frequency-summary rows;
- 6,048 case/output/pulse/window metric rows;
- 3,024 paired nine/seven comparisons;
- 48 source/pulse/window summaries;
- 864 finite-record identity summaries.

## Interpretation limits

The continuous AC comparator is evaluated at finite-record DFT bins and weighted by the sample-and-hold input spectrum; it is not the exact sampled response of the continuous-time differential equation. The exact finite-record identity includes the terminal-state correction. Two individual passive linear-RC morphology reconstructions are not a population, and this is not active-neuron or biological validation. Relative ratios must be interpreted with absolute weighted norms and the measured transient NRMSE. Full Hines remains canonical; production defaults are unchanged.
