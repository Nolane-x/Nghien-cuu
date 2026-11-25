# Research log — validated PRIMA q25 short-window boundary decomposition

**Date:** 25 November 2026  
**Branch:** `research/prima-q25-short-window-boundary-decomposition-2026-11-25`  
**Workflow:** [45555648742](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45555648742)  
**Result commit:** `c988e1b82407822d658046898c4c8a4d58ca8082`

## Research question

For a finite 20/40-ms record computed with the backward-Euler state update, how do the periodic discrete-transfer mismatch and the terminal-state boundary term combine to produce the observed seven-port versus dual-q25 nine-port residual?

## Hypothesis and falsification

Hypothesis: the transfer-only metric differs from the finite-window transient residual because the finite-record DFT includes a terminal-state correction. This explanation is falsified if the explicit periodic plus terminal decomposition fails to reconstruct the directly computed finite-error DFT within the predeclared tolerance.

## Sources and inputs

- Prior finite-record identity implementation and tests from the preceding q25 research branch.
- PR #33 fine-step q25 transient outputs and its pinned single-thread numerical environment.
- Checksum-pinned SWC and preflight outputs for NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- The current branch's exact backward-Euler and boundary-decomposition implementation.

## Work performed

- Implemented the periodic-transfer / terminal-boundary decomposition at dt=0.00625 ms.
- Preserved both canonical absolute-voltage and perturbation-coordinate transient metrics.
- Used order-168 seven-port and dual-q25 nine-port reductions.
- Evaluated nine passive parameter scenarios, three source locations, two pulse widths, seven shared outputs and two observation windows.
- Added 16 focused tests covering frequency mapping, finite-record identity, recurrence equivalence, input scaling, coordinate parity, summary aggregation, pulse charge, time-step convention, hashing, runtime settings and exact coverage.
- Added exact expected row-count checks and CSV read-back gates.
- Preserved basis, trace and runtime diagnostics.

## Commands and execution

GitHub Actions run [45555648742](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45555648742) executed on commit `67739459f4611e1c561dc48d47ef608a6abaef5f`:

- `python -m pytest -q tests/test_prima_q25_short_window_boundary_decomposition.py` → 16 passed, one warning, 0.88 s.
- `python examples/prepare_nmo163775_peng_control_holdout.py` → PASS.
- `python examples/prepare_nmo107159_tamas_holdout.py` → PASS.
- `/usr/bin/time ... python research/analyze_prima_q25_short_window_boundary_decomposition.py` → successful; 761.245 s wall time.
- Workflow artifact upload → successful, artifact ID 14996127618.

The result archival commit `c988e1b82407822d658046898c4c8a4d58ca8082` is one commit after the tested source. The Git compare shows that it adds only the seven generated result artifacts; no code or workflow files changed in that archival commit.

## Results

- 268,884 frequency summaries.
- 3,024 case metrics.
- 1,512 matched seven/nine comparisons.
- 24 source/window summaries.
- 4 morphology/window summaries.
- 432 finite-DFT identity rows.
- Six CSV read-backs exactly matched expected row counts.
- Both morphology checksums and preflights passed.
- Maximum finite-identity relative residual: 8.92040452890518e-12, under the 2e-8 limit.
- Maximum model identity relative residual: 8.743810650683813e-12.
- Maximum absolute finite-identity residual: 4.7998036999657625e-11 V·samples.

The periodic component, terminal-boundary component and cross-term vary markedly by morphology and window. Median component magnitudes relative to final finite-error norm reach 552.33% and 536.72% for Tamas 20 ms, and 611.56% and 609.57% for Peng 20 ms. The corresponding cross-terms are -6,051.93% and -7,316.36%. This is strong cancellation in the squared-norm identity, not a biological energy statement.

The canonical absolute-voltage and perturbation-coordinate transient metrics also produce materially different nine/seven ratios. Both must remain reported; neither may be silently selected to support a preferred conclusion.

## Reproducibility and caveats

Environment: Ubuntu 26.04.1, Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3 and NEURON 9.0.2. BLAS/OpenMP and PYTHONHASHSEED variables were pinned. The optional threadpoolctl package was absent, so the workflow did not independently query active BLAS pool counts.

The finest-step Hines trace is a numerical reference, not exact continuum truth. Only two individual passive morphology reconstructions were included. No active-neuron or biological validation is claimed; no production defaults were changed.

## Next action

Add q25-aware, checksum-pinned preflights for NMO_03524 Jacobs Control and NMO_162186 Allen L2/3, use a common 0.5-µm NEURON segment cap for the first replication, and rerun the same finite-record decomposition. Keep the epilepsy-condition and incomplete-axon morphology separate in interpretation. Do not claim population-level behavior from four cells.
