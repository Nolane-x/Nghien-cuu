# PRIMA q25 backward-Euler fine-step convergence

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-fine-step-convergence-2026-11-24\`  
**Parent:** PR #31, timestep refinement through 0.025 ms  
**Execution:** passed — [workflow 45428685906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906)

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

**Execution status:** complete and validated. Workflow [45428685906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906) passed 15/15 focused tests, both morphology SHA-256 checks and NEURON preflights, the full calculation, six exact CSV read-backs, result commit and artifact upload.

- Read-back: 24,192 layout metrics; 12,096 paired 7/9-port rows; 192 source-window summaries; 32 morphology × timestep × window summaries; 9,072 Hines temporal-comparison rows; 24 temporal summaries.
- Result commit: \`d79ca743cbb662bf4536b28c527bfa5234058c15\`.
- Artifact: [14937828066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906/artifacts/14937828066), ZIP SHA-256 \`9fae812ff71e2a6a0c8920495d7e990830a0f116843fadfbd20e84fa924e498f\`.
- Runtime: 388.44 s; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.

## Results

### Median dual-q25 nine-port / seven-port transient error ratio

Each ratio is the median over six source × pulse groups; each group takes the median across nine parameter scenarios × seven shared outputs. These are relative residual ratios, not ratios of pooled energy.

| Morphology | Window | dt 0.1 ms | dt 0.05 ms | dt 0.025 ms | dt 0.0125 ms |
|---|---:|---:|---:|---:|---:|
| Tamas human pyramidal | 20 ms | 24.44× | 26.59× | 27.05× | **26.55×** |
| Tamas human pyramidal | 40 ms | 55.24× | 57.04× | 54.85× | **49.91×** |
| Tamas human pyramidal | 100 ms | 31.87× | 31.73× | 31.72× | **32.05×** |
| Tamas human pyramidal | 200 ms | 31.64× | 31.59× | 31.59× | **31.84×** |
| Peng mouse | 20 ms | 138.24× | 130.11× | 123.68× | **118.81×** |
| Peng mouse | 40 ms | 70.09× | 67.68× | 63.89× | **64.98×** |
| Peng mouse | 100 ms | 33.67× | 33.62× | 33.64× | **33.62×** |
| Peng mouse | 200 ms | 33.43× | 33.42× | 33.46× | **33.45×** |

The long-window result is now particularly stable. From 0.1 to 0.0125 ms, the median nine/seven ratio changes by only about 0.6% for Tamas and less than 0.2% for Peng at 100–200 ms. This is strong evidence that the long-window relative reduction penalty is not an artifact of the tested timestep.

The short-window ratios remain more sensitive. Peng's ratios fall from 138.24× to 118.81× at 20 ms and from 70.09× to 64.98× at 40 ms across the full grid. Tamas is less monotonic: its 40-ms ratio moves from 55.24× to 57.04× to 54.85× to 49.91×. Thus, even at 0.0125 ms, the 20–40-ms ratio should not yet be treated as fully converged.

Despite the large relative ratios, the absolute nine-port perturbation-coordinate NRMSE at 0.0125 ms remains tiny: Tamas is about \(4.13\times10^{-9}\%\), \(1.21\times10^{-8}\%\), \(1.86\times10^{-8}\%\), and \(1.86\times10^{-8}\%\) at 20/40/100/200 ms; Peng is about \(1.25\times10^{-8}\%\), \(6.33\times10^{-8}\%\), \(8.40\times10^{-8}\%\), and \(8.40\times10^{-8}\%\).

### Full-Hines temporal convergence against dt = 0.0125 ms

Each row summarizes 378 scenario × protocol × output traces. Values are NRMSE percentages for the coarse full-Hines perturbation trace against the 0.0125-ms trace sampled at identical end-of-step times.

| Morphology | Coarse dt | Median across windows | Maximum |
|---|---:|---:|---:|
| Tamas | 0.1 ms | 0.632–0.682% | 1.702% |
| Tamas | 0.05 ms | 0.275–0.296% | 0.746% |
| Tamas | 0.025 ms | 0.094–0.100% | 0.267% |
| Peng | 0.1 ms | 0.613–0.685% | 2.511% |
| Peng | 0.05 ms | 0.265–0.296% | 1.122% |
| Peng | 0.025 ms | 0.089–0.099% | 0.387% |

The ratios between adjacent coarse-vs-fine discrepancies are consistent with first-order backward Euler. For the 0.1-to-0.05-ms pair, the discrepancy ratio is about 2.30–2.32; for 0.05-to-0.025 ms it is about 2.94–2.96. The ideal geometric ratios with the fixed 0.0125-ms reference are \(0.0875/0.0375=2.33\) and \(0.0375/0.0125=3\), respectively. The measured results are therefore strongly consistent with first-order convergence over this range.

The 0.025-ms Hines trace still differs from the 0.0125-ms trace by a median of about 0.089–0.100%. The 0.0125-ms reference is not an exact continuous-time solution, so this remains a refinement study rather than a proof of convergence to the continuum.

### Updated interpretation

The evidence now separates two conclusions:
1. For 100–200-ms windows, the seven/nine-port relative reduction-error ratio is effectively stable across dt 0.1 to 0.0125 ms for these two passive morphologies.
2. For 20–40-ms windows, timestep sensitivity remains material; a still-finer reference or a dedicated short-time boundary/transient analysis is needed.

Full-Hines temporal error remains much larger than PRIMA reduction NRMSE. The seven/nine ratio compares reduced-model error at a fixed timestep; it is not the total simulation error.

### Validation provenance

- 15 focused tests passed; both morphology hashes and NEURON preflights passed.
- All six output CSVs read back with their exact expected row counts.
- Maximum full-Hines absolute-vs-perturbation-coordinate trace delta across the matrix: \(7.6328\times10^{-8}\%\).
- Same order-168 continuous-time PRIMA projection basis used across timesteps; reduced BE systems refactorized per timestep.

## Interpretation limits

The 0.0125-ms Hines solution is a finer numerical reference, not an exact continuous-time solution. Four timesteps provide stronger evidence about the BE trend but do not alone establish an exact convergence order. Only two passive morphology instances are included; no active-neuron or biological validation is claimed. No production solver/default is changed.
