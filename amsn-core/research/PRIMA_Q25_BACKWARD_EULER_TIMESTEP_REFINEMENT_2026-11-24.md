# PRIMA q25 backward-Euler timestep refinement

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-timestep-refinement-2026-11-24\`  
**Parent:** PR #30, exact backward-Euler discrete-transfer audit  
**Execution:** passed — [GitHub Actions run 45426480184](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184)

## Research question

Do the seven-port versus dual-q25 nine-port transient error ratios remain stable when the backward-Euler timestep is refined from 0.1 to 0.025 ms, and how large is the temporal integration error of the full-Hines reference over the same grid?

## Scope

- Checksum-pinned NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Canonical seven-port and dual-q25 nine-port layouts; PRIMA order 168, fixed projection basis across timestep values.
- Nine existing passive parameter scenarios, three sources, seven exact shared output SWC nodes, two pulse widths and 20/40/100/200-ms windows.
- Backward-Euler timesteps: 0.1, 0.05 and 0.025 ms.
- Full Hines is the reference at each timestep; the 0.025-ms full-Hines perturbation waveform is the temporal-convergence reference for the 0.1- and 0.05-ms runs.

## Numerical method

The primary comparison is measured in perturbation coordinates \(y=V-E_{\mathrm{leak}}\): the full-Hines replay starts at zero perturbation with zero leak source, while the absolute-voltage replay is retained as a floating-point diagnostic. Each reduced model uses the same fixed order-168 PRIMA projection basis and is re-factorized for each \(\Delta t\).

The pulse sampling convention is unchanged: current is applied at samples whose interval begins at or after the 2-ms onset and strictly before the pulse end. Both widths (2 and 10 ms) are exact multiples of all three timesteps. The 0.025-ms Hines trace is aligned to coarse sample-end times using stride 4 or 2 before measuring temporal refinement.

## Expected output coverage

- 18,144 layout-level transient metrics.
- 9,072 paired nine/seven comparison rows.
- 144 source × pulse × window summaries.
- 24 morphology × timestep × window summaries.
- 6,048 full-Hines temporal-convergence rows.
- 16 full-Hines temporal-convergence summary rows.

## Validation

The workflow verifies both SWC SHA-256 hashes, both morphology preflights, focused tests, finite outputs and exact CSV row-count read-back. Results and runtime metadata are committed only after the full calculation succeeds.

**Execution status:** completed and validated. Workflow [45426480184](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184) passed **15/15 focused tests**, both source checksums and both morphology preflights, the complete numerical replay, exact row-count read-back, result commit and artifact upload.

- Read-back: 18,144 metric rows; 9,072 paired seven/nine rows; 144 source summaries; 24 morphology/window summaries; 6,048 full-Hines temporal-comparison rows; 16 temporal-convergence summary rows.
- Result commit: \`8161b30e7a9ac3f62dcfb8754e08850a703f5ad3\`.
- Artifact: [14934844995](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45426480184/artifacts/14934844995), ZIP SHA-256 \`e8aeb6359f987a52040d38d28586185339654331c2d819334743cb1ee947e127\`.
- Runtime: 213.66 s; Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.

## Results

### Median dual-q25 nine-port / seven-port transient error ratio

Ratios are medians over the six source × pulse groups; within each group, the median is taken over nine parameter scenarios × seven shared outputs. They are relative error ratios, not ratios of pooled energies.

| Morphology | Window | dt = 0.1 ms | dt = 0.05 ms | dt = 0.025 ms |
|---|---:|---:|---:|---:|
| Tamas human pyramidal | 20 ms | 24.44× | 26.59× | 27.05× |
| Tamas human pyramidal | 40 ms | 55.24× | 57.04× | 54.85× |
| Tamas human pyramidal | 100 ms | 31.87× | 31.73× | 31.72× |
| Tamas human pyramidal | 200 ms | 31.64× | 31.59× | 31.59× |
| Peng mouse | 20 ms | 138.24× | 130.11× | 123.68× |
| Peng mouse | 40 ms | 70.09× | 67.68× | 63.89× |
| Peng mouse | 100 ms | 33.67× | 33.62× | 33.64× |
| Peng mouse | 200 ms | 33.43× | 33.42× | 33.46× |

The long-window ratios are very stable across the tested timesteps: changes from 0.1 to 0.025 ms are within about 0.5% at 100–200 ms for both morphologies. At 20 ms, the ratio changes by about +10.7% for Tamas and −10.5% for Peng; at 40 ms, Peng changes by about −8.9% while Tamas changes by less than 1%. Therefore the relative q25 penalty is fairly timestep-insensitive at 100–200 ms, but the short-window ratios are not yet fully converged at 0.025 ms.

The absolute nine-port perturbation-coordinate NRMSE remains tiny: across all timestep/window combinations, about \(2.85\times10^{-9}\%\) to \(1.83\times10^{-8}\%\) for Tamas and \(8.55\times10^{-9}\%\) to \(8.22\times10^{-8}\%\) for Peng. The large relative ratios arise because the seven-port denominator is even smaller; they do not mean large absolute waveform error.

### Full-Hines temporal convergence against dt = 0.025 ms

Each summary covers 378 paired scenario × protocol × output traces. Values are NRMSE percentages for the 0.1- or 0.05-ms full-Hines trace versus the 0.025-ms full-Hines trace sampled at matching end-of-step times.

| Morphology | Coarse dt | Median across windows | p90 across windows | Maximum |
|---|---:|---:|---:|---:|
| Tamas human pyramidal | 0.1 ms | 0.54–0.58% | about 0.94–0.95% | 1.453% |
| Tamas human pyramidal | 0.05 ms | 0.183–0.197% | about 0.319–0.320% | 0.495% |
| Peng mouse | 0.1 ms | 0.524–0.586% | about 1.012–1.014% | 2.141% |
| Peng mouse | 0.05 ms | 0.176–0.197% | about 0.356–0.357% | 0.744% |

Halving the step from 0.1 to 0.05 ms reduces the coarse-vs-fine median discrepancy by about 2.9–3.0×, consistent with the expected first-order backward-Euler trend over this range. This is supportive evidence, not a formal asymptotic-order proof, because the finest 0.025-ms solution is a numerical reference rather than an exact continuous-time solution.

The temporal discrepancy of full Hines (roughly 0.18–0.59% median against the 0.025-ms trace) is many orders of magnitude larger than the PRIMA reduction NRMSE (roughly \(10^{-9}\%\)–\(10^{-8}\%\)). In this benchmark, timestep discretization dominates the absolute error budget; the seven/nine-port ratios are still useful for comparing reduction error at a fixed timestep, but they should not be mistaken for total simulation error.

### Validation provenance

- 15 focused tests passed in 0.51 s.
- Both SWC SHA-256 checks and NEURON preflights passed.
- Exact CSV read-back counts matched all six declared outputs.
- Maximum absolute-vs-perturbation-coordinate full-Hines trace delta across the matrix: \(7.63\times10^{-8}\%\).
- The analysis used the same order-168 continuous-time PRIMA basis across timestep values and re-factorized the reduced backward-Euler matrices separately for each timestep.

## Interpretation limits

The 0.025-ms Hines trace is a finer numerical reference, not an exact continuous-time solution. The PRIMA basis/order are held fixed across timesteps so this isolates temporal discretization sensitivity, not basis optimality. Large relative ratios must be read alongside absolute error norms and NRMSE. Only two passive morphology instances are included; no active-neuron or biological validation is claimed. No production solver/default is changed.
