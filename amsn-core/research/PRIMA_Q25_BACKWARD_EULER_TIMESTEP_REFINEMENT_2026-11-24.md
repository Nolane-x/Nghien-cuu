# PRIMA q25 backward-Euler timestep refinement

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-timestep-refinement-2026-11-24\`  
**Parent:** PR #30, exact backward-Euler discrete-transfer audit  
**Execution:** pending GitHub Actions

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

**Execution status:** pending. No numerical conclusion is claimed until the workflow completes and its outputs are read back.

## Interpretation limits

The 0.025-ms Hines trace is a finer numerical reference, not an exact continuous-time solution. The PRIMA basis/order are held fixed across timesteps so this isolates temporal discretization sensitivity, not basis optimality. Large relative ratios must be read alongside absolute error norms and NRMSE. Only two passive morphology instances are included; no active-neuron or biological validation is claimed. No production solver/default is changed.
