# Research log — exact backward-Euler discrete-time transfer for PRIMA q25

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-discrete-transfer-2026-11-24\`  
**Parent checkpoint:** PR #29

## Question

Does the exact discrete-time transfer function of the backward-Euler recurrence change the q25 comparison relative to continuous-time AC, and can finite-record output DFTs be reconstructed with a terminal-state correction?

## Sources examined

- \`AGENTS.md\`, \`HANDOFF.md\` and \`research/AMSN_RESEARCH_DOSSIER.md\`.
- PR #29 handoff and validated finite-window DFT report.
- The prior q25 continuous-time transfer, Krylov-stage, extended-tail and transient-spectrum audits.
- Existing exact-order Hines and reduced backward-Euler implementations.

## Derivation

Starting with
\[
(G+C/\Delta t)x[n]-(C/\Delta t)x[n-1]=Bu[n],
\]
and the convention that \(u[n]\) is held during one time interval while \(x[n]\) is sampled at the interval end, the discrete transfer is
\[
H_{BE}(e^{j\Omega})=L(G+(1-e^{-j\Omega})C/\Delta t)^{-1}B.
\]
It is the continuous resolvent evaluated at \(s_{BE}=(1-e^{-j\Omega})/\Delta t\), not at \(j\Omega/\Delta t\). For a finite record initialized at rest, the DFT obeys
\[
(G+(1-e^{-j\Omega})C/\Delta t)X=BU-(C/\Delta t)x[N-1].
\]
The last term is retained as the terminal-state boundary correction.

## Implementation authored

- Added exact complex-shift Hines and reduced solves for both \(s=j\omega\) and \(s=s_{BE}\).
- Added sample-and-hold pulse-spectrum construction.
- Added full/reduced transient replays that retain terminal state at 20, 40, 100 and 200 ms.
- Added finite-record DFT reconstruction checks.
- Added focused unit tests, workflow, report, handoff and this log.
- No production solver or default was changed.

## Execution record

Pending CI. No tests, preflights or numerical results are claimed before the workflow completes. The workflow pins Python 3.12, NumPy (environment-resolved), NEURON 9.0.2 and SciPy 1.16.3, verifies both SWC hashes, runs both preflights and records raw CSV read-back counts.

## Expected outputs

- \`frequency_summary.csv\`
- \`case_metrics.csv\`
- \`nine_seven_comparisons.csv\`
- \`source_window_summary.csv\`
- \`finite_dft_identity.csv\`
- \`report.json\`

## Limits and next step

The continuous comparator is sampled at discrete DFT frequencies and weighted by the ZOH input spectrum; it is not the exact sampled response of the continuous-time ODE. Only two passive linear-RC morphologies are included. After CI, compare absolute weighted norms, ratios, transient NRMSE and boundary correction separately. Keep full Hines canonical.
