# Validated results — PRIMA q25 short-window boundary decomposition

**Date:** 25 November 2026  
**Branch:** `research/prima-q25-short-window-boundary-decomposition-2026-11-25`  
**Research PR:** [#34](https://github.com/Nolane-x/Nghien-cuu/pull/34)  
**Workflow:** [45555648742](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45555648742)  
**Result commit:** `c988e1b82407822d658046898c4c8a4d58ca8082`

## Executive result

The finite-record backward-Euler identity was reproduced on two checksum-pinned passive morphologies. The periodic-transfer contribution and the terminal-state boundary correction can each be several times larger than the final finite-window error because they strongly cancel. This explains why a periodic transfer metric alone does not determine the observed finite-window transient error.

The decomposition is numerically consistent with the directly computed finite-record DFT: the maximum normalized identity residual was (8.9204\times10^{-12}), below the predeclared (2\times10^{-8}) tolerance. This is an algebraic/numerical validation of the stated discrete model and sampling convention, not biological validation.

## Execution and validation

The successful GitHub Actions run executed the source at commit `67739459f4611e1c561dc48d47ef608a6abaef5f`. The workflow then committed the generated result archive as `c988e1b82407822d658046898c4c8a4d58ca8082`. A Git compare confirms that this one-commit difference contains only the seven generated result files; the code tested by Actions was not changed by the archival commit.

Executed commands:

- `python -m pytest -q tests/test_prima_q25_short_window_boundary_decomposition.py` — **16 passed**, one warning, 0.88 s.
- `python examples/prepare_nmo163775_peng_control_holdout.py` — preflight PASS.
- `python examples/prepare_nmo107159_tamas_holdout.py` — preflight PASS.
- `/usr/bin/time ... python research/analyze_prima_q25_short_window_boundary_decomposition.py` — completed successfully.

Validation evidence:

- Both pinned SWC source checksums matched their preflight records.
- Both morphology preflights passed.
- All 432 finite-record DFT identity rows were produced.
- Maximum model identity relative error: (8.7438\times10^{-12}).
- Maximum finite-error identity relative error: (8.9204\times10^{-12}), against tolerance (2\times10^{-8}).
- Maximum absolute finite-identity residual: (4.7998\times10^{-11}) V·samples.
- All six numerical CSVs passed exact row-count read-back:
  - 268,884 frequency summaries;
  - 3,024 case metrics;
  - 1,512 matched seven/nine-port comparisons;
  - 24 source/window summaries;
  - 4 morphology/window summaries;
  - 432 finite-DFT identity rows.
- Result artifact: [14996127618](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45555648742/artifacts/14996127618), ZIP SHA-256 `63d56c7cf9bba5ca70f78d0385638d78de3f55aec1a88bd56e102126e4eaf14d`.

Environment: Ubuntu 26.04.1, Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2. Wall time was 761.245 s. BLAS/OpenMP and Python hash-seed variables were set to single-thread/deterministic values. The optional `threadpoolctl` module was absent, so active threadpool counts were not independently introspected; the configured environment variables were present in the Actions log.

## Method

The timestep is 0.00625 ms, basis order is 168, and the layouts are the canonical seven-port model and the dual-q25 nine-port model. Each morphology is evaluated over nine deterministic passive parameter scenarios, three current injection sites (soma, basal-q75 and apical-q75), two 10-pA rectangular pulse widths (2 and 10 ms), seven shared output nodes and 20/40-ms observation windows.

For the declared sample-and-hold backward-Euler update,

[
(G + C/\Delta t)x[n] - (C/\Delta t)x[n-1] = Bu[n],
]

the finite-record DFT contains an explicit terminal-state term:

[
E(\omega) =
(H_{9,BE}-H_{7,BE})U(\omega)
-
(Q_9(\omega)-Q_7(\omega)).
]

The first contribution is the periodic discrete-transfer difference; the second is the terminal-boundary correction. The cross-term is retained because the two contributions may cancel strongly. Component percentages are normalized by the norm of the final finite-record error, so values above 100% are valid and should not be read as ordinary waveform-error percentages.

## Validated results

Median values over the six source × pulse groups:

| Morphology | Window | Periodic component / finite-error norm | Boundary component / finite-error norm | Cross-term / finite-error energy |
|---|---:|---:|---:|---:|
| NMO_107159 Tamas human pyramidal Control | 20 ms | 552.33% | 536.72% | -6,051.93% |
| NMO_107159 Tamas human pyramidal Control | 40 ms | 134.95% | 96.65% | -184.08% |
| NMO_163775 Peng mouse Control | 20 ms | 611.56% | 609.57% | -7,316.36% |
| NMO_163775 Peng mouse Control | 40 ms | 139.26% | 106.64% | -210.45% |

The component norms are much larger than the final error in the 20-ms cases, which is consistent with strong cancellation. The cross-term is the algebraic term required to close the squared-norm identity; it is not a biological energy measure.

### Metric sensitivity that must remain visible

The report deliberately preserves two transient coordinate conventions. Their median nine/seven ratios differ materially:

| Morphology | Window | Canonical absolute-voltage transient ratio | Perturbation-coordinate transient ratio |
|---|---:|---:|---:|
| Tamas human pyramidal | 20 ms | 0.9963× | 25.6917× |
| Tamas human pyramidal | 40 ms | 1.0001× | 49.9211× |
| Peng mouse | 20 ms | 17.4320× | 135.1351× |
| Peng mouse | 40 ms | 27.0457× | 59.8136× |

These ratios compare reduction residuals, not absolute biological error. The seven-port denominator can be extremely small. The coordinate sensitivity is itself an important diagnostic: future summaries must show the two metrics side by side and include absolute NRMSE, not choose whichever ratio appears most favorable.

The separate timestep-refinement experiment on the same two morphologies found the short-window perturbation-coordinate ratios at dt=0.00625 ms to be 24.64× / 49.14× for Tamas and 114.77× / 65.06× for Peng (20/40 ms). Full-Hines coarse-to-fine differences also fell with timestep refinement. The 0.00625-ms trace is a finer numerical reference, not exact continuum truth.

## Scientific interpretation

1. A periodic frequency-domain transfer calculation and a finite, zero-initial-state transient calculation are not interchangeable. The terminal-state correction is required by the finite-record identity.
2. A large relative nine/seven ratio can coexist with a tiny absolute residual because the seven-port baseline may be exceptionally accurate.
3. The cancellation magnitude and transient ratios differ by morphology and observation window. The result is not a universal q25 penalty or a universal preference for seven versus nine ports.
4. No production solver, default, or recommended production port layout is changed. Full Hines remains the canonical reference.

## Limits

- Only two individual passive linear-RC morphology reconstructions were included.
- These records do not represent cell populations.
- The model does not include active ion channels, nonlinear synapses, calcium signaling, plasticity, metabolism or glial coupling.
- The finite-DFT identity validates the declared discrete equations and implementation; it does not establish that the passive parameterization is biologically complete.
- The continuous-time AC comparator is a separate diagnostic, not the exact sampled response of the continuous differential equation.
- Runtime is from one hosted Actions runner and is not a controlled hardware benchmark.

## Next experiment: cross-morphology replication

Extend the same finite-record decomposition to two previously pinned, independently sourced human morphologies:

- NMO_03524 Jacobs Control, a single human pyramidal reconstruction with moderate dendritic integrity and incomplete axon.
- NMO_162186 Allen Cell Types L2/3, an epilepsy-condition specimen with incomplete axon.

Treat these as distinct holdouts/strata, not as a homogeneous healthy population. Before running the decomposition, create and validate q25-aware preflights for both; pin the source SHA-256, exact seven shared SWC node IDs and two q25-only IDs. Use a common 0.5-µm maximum NEURON segment cap for the first cross-morphology comparison, while recording the difference from earlier 0.125-µm studies. Keep the same basis order, timestep, source/pulse design, observation windows and finite-identity tolerance.

For a four-morphology run with the same design, expected coverage is 537,768 frequency rows, 6,048 case metrics, 3,024 paired comparisons, 48 source/window summaries, 8 morphology/window summaries and 864 finite-identity rows. Do not pool absolute residuals across different mesh caps or biological source conditions.

Acceptance gates: exact source/provenance validation; q25 node identities pinned by preflight; focused tests; finite-identity residual below (2\times10^{-8}); exact CSV read-back row counts; reproducibility hashes; and artifact upload. Only after this replication should the study consider a broader morphology-level conclusion.
