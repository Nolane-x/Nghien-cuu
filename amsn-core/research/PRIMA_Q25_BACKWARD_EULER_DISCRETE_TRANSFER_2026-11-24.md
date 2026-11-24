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

not at \(j2\pi f\). The real part of \(s_{BE}\) introduces numerical damping and the imaginary part warps frequency. For the finite record beginning at rest, the terminal state cannot be discarded:

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

**Execution status:** pending. No numerical conclusion is claimed until CI completes and its committed outputs are read back.

Expected coverage:
- 84,084 frequency-summary rows;
- 6,048 case/output/pulse/window metric rows;
- 3,024 paired nine/seven comparisons;
- 48 source/pulse/window summaries;
- 864 finite-record identity summaries.

## Interpretation limits

The continuous AC comparator is evaluated at finite-record DFT bins and weighted by the sample-and-hold input spectrum; it is not the exact sampled response of the continuous-time differential equation. The exact finite-record identity includes the terminal-state correction. Two individual passive linear-RC morphology reconstructions are not a population, and this is not active-neuron or biological validation. Relative ratios must be interpreted with absolute weighted norms and the measured transient NRMSE. Full Hines remains canonical; production defaults are unchanged.
