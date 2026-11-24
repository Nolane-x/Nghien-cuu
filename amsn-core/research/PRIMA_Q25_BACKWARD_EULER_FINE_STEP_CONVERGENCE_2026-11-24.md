# PRIMA q25 backward-Euler fine-step convergence

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-fine-step-convergence-2026-11-24\`  
**Parent:** PR #31, timestep refinement through 0.025 ms  
**Execution:** pending GitHub Actions

## Research question

Does the approximately first-order full-Hines backward-Euler convergence observed between 0.1 and 0.05 ms persist when the reference is refined to 0.0125 ms, and do the short-window seven-port versus dual-q25 nine-port error ratios stabilize at this finer step?

## Scope

- Same two checksum-pinned passive morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Seven-port and dual-q25 nine-port layouts; PRIMA order 168, same continuous-time projection basis across all timesteps.
- Nine passive parameter scenarios, three current sources, seven shared outputs, two pulse widths, four windows.
- Timestep grid: 0.1, 0.05, 0.025 and 0.0125 ms.
- Full Hines at 0.0125 ms is the finer temporal reference; the three coarser traces are aligned to matching end-of-step sample times.

## Numerical method

All pulse edges and observation windows are exact multiples of the four timesteps. The stable primary error metric remains the full-Hines perturbation-coordinate comparison \(y=V-E_{\mathrm{leak}}\). The absolute-voltage replay is retained only as a round-off diagnostic. PRIMA basis/order are fixed; each reduced backward-Euler matrix is refactorized for its own timestep.

The finer reference allows two adjacent comparisons: 0.05 and 0.025 ms against 0.0125 ms, as well as 0.1 ms against 0.0125 ms. This tests whether the prior approximately 3:1 ratio between coarse/fine discrepancies continues at the next level.

## Expected output coverage

- 24,192 layout-level transient metrics.
- 12,096 paired seven/nine comparisons.
- 192 source × pulse × window summaries.
- 32 morphology × timestep × window summaries.
- 9,072 full-Hines temporal-convergence rows.
- 24 temporal-convergence summary rows.

## Validation

The workflow verifies both SWC SHA-256 hashes, both morphology preflights, focused tests, finite outputs and exact CSV read-back. Results are committed only after the full run succeeds.

**Execution status:** pending. No 0.0125-ms conclusion is claimed until tests, full computation, all six CSV read-backs, result commit and artifact upload pass.

## Interpretation limits

The 0.0125-ms Hines solution is a finer numerical reference, not an exact continuous-time solution. Four timesteps provide stronger evidence about the BE trend but do not alone establish an exact convergence order. Only two passive morphology instances are included; no active-neuron or biological validation is claimed. No production solver/default is changed.
