# PRIMA q25 short-window periodic-transfer / terminal-boundary decomposition

**Date:** 25 November 2026  
**Branch:** \`research/prima-q25-short-window-boundary-decomposition-2026-11-25\`  
**Parent:** PR #33, reproducible short-window timestep audit  
**Execution:** pending GitHub Actions

## Research question

At dt = 0.00625 ms, why can the finite-window 20/40-ms transient residual differ from the periodic backward-Euler transfer residual? The finite-record identity separates the seven/nine-port error into a periodic-transfer term and a terminal-state boundary correction. This audit measures both terms and their cross-term cancellation.

## Exact decomposition

For the declared sample-and-hold backward-Euler convention:

\[
E(\omega) =
\left(H_{9,\mathrm{BE}}-H_{7,\mathrm{BE}}\right)U(\omega)
-
\left(Q_9(\omega)-Q_7(\omega)\right),
\]

where \(Q(\omega)\) is the transfer of the terminal-state forcing \((C/\Delta t)x[N-1]\). The first term is the periodic-transfer component; the second is the finite-window terminal-boundary component.

The audit measures the norms of both terms relative to the actual finite-error norm, plus the cross-term:
\[
\|E\|^2 = \|E_{\mathrm{periodic}}\|^2+
\|E_{\mathrm{boundary}}\|^2+
2\operatorname{Re}\langle E_{\mathrm{periodic}},E_{\mathrm{boundary}}\rangle.
\]
The components can each exceed the finite-error norm when their cross-term is strongly negative. This is expected cancellation, not an energy-conservation claim.

## Scope

- Two checksum-pinned passive morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Seven-port and dual-q25 nine-port PRIMA layouts, order 168, same continuous-time projection basis per morphology/scenario/layout.
- Nine passive parameter scenarios, three current sources, seven shared output nodes, two rectangular current pulses (2/10 ms).
- Fixed timestep dt = 0.00625 ms; observation windows 20 and 40 ms only.
- Frequency grid 0–80 kHz in 25-Hz increments, matching the Nyquist and exact DFT bins for both windows.

## Expected output coverage

- 268,884 frequency-summary rows.
- 3,024 layout-level case-metric rows.
- 1,512 paired seven/nine-port rows.
- 24 source × pulse × window summaries.
- 4 morphology × window summaries.
- 432 finite-record identity rows.
- Six CSV datasets with exact read-back row-count gates, plus report JSON and runtime metadata.

## Execution status

Pending GitHub Actions. No decomposition result is accepted until focused tests, both morphology checksums/preflights, full calculation, all six CSV read-backs, finite-identity gate, result commit and artifact upload pass.

## Interpretation limits

The 0.00625-ms full-Hines solution is a finer numerical trace, not an exact continuous-time solution. The study is restricted to two individual passive linear-RC reconstructions; it is not population or biological validation. Full Hines remains canonical. No production solver/default is changed.
