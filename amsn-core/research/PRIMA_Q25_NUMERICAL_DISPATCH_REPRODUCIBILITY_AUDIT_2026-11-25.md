# PRIMA q25 numerical-dispatch reproducibility audit

**Date:** 25 November 2026  
**Primary run:** [45585262246](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246), artifact 15010408589  
**Independent rerun:** [45585843464](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585843464), artifact 15012912899  
**Scope:** order-168, four morphology, four-layout passive finite-window calculation.

## 1. Why this audit was opened

The two completed order-168 runs used the same source revision for the numerical runner and the same declared software versions (Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3 and NEURON 9.0.2). Both passed the morphology checks, complete CSV coverage and finite-record DFT identity gate.

They did not, however, reproduce the same numerical model. The runtime configuration embedded by NumPy reported a different CPU-feature set:

- Run 45585262246: X86_V3 was reported as found; X86_V4 and AVX512_ICL were not found.
- Run 45585843464: X86_V3, X86_V4 and AVX512_ICL were reported as found.

The two runs also differed materially in wall time (2,546.82 s versus 1,353.44 s), despite using one-thread environment settings. The CPU-feature distinction is a credible numerical-dispatch confounder: NumPy documents that its runtime-dispatched implementations depend on detected CPU features and that NPY_DISABLE_CPU_FEATURES restricts the features available to dispatch. OpenBLAS separately supports OPENBLAS_CORETYPE to override CPU-target auto-detection. References: [NumPy runtime SIMD dispatch](https://numpy.org/doc/stable/reference/simd/build-options.html#runtime-dispatch), [OpenBLAS runtime variables](https://www.openmathlib.org/OpenBLAS/docs/runtime_variables/).

This does not establish that CPU dispatch is the only cause of the observed changes. It does establish that the two runs did not share an identical recorded runtime-feature environment, so the second run cannot be represented as a bit-for-bit reproducibility check.

There is one further instrumentation limitation: the two original reports show `ModuleNotFoundError: No module named 'threadpoolctl'` under their OpenBLAS runtime diagnostics. Their NumPy build configuration identifies the bundled SciPy OpenBLAS build as dynamic-architecture SkylakeX, but this is build metadata, not the actual CPU kernel selected at runtime. Therefore, the first two runs' active OpenBLAS architecture is **unknown**. It would be too strong to attribute the basis differences exclusively to NumPy SIMD dispatch. The defensible conclusion is that both NumPy's detected SIMD feature set and the unrecorded OpenBLAS runtime architecture are unresolved numerical-dispatch variables in the original pair.

The corrected workflows now pin the Python/NumPy/SciPy/NEURON/threadpoolctl versions as well as the OpenBLAS core type and NumPy SIMD-disable environment, and verify the selected OpenBLAS architecture before launching the long run.

## 2. Direct comparison of the two raw case matrices

Both artifacts contain exactly 12,096 case-metric rows, and all paired case keys match. Comparing all cases by morphology, scenario, layout, source, output, pulse and window:

| Metric | Rows that changed | Median absolute difference | 99th-percentile absolute difference |
|---|---:|---:|---:|
| Continuous-AC weighted error (%) | 12,096 / 12,096 | 5.68 × 10⁻¹⁰ percentage points | 8.99 × 10⁻⁷ percentage points |
| Discrete-BE periodic error (%) | 12,096 / 12,096 | 3.20 × 10⁻¹² percentage points | 2.04 × 10⁻⁸ percentage points |
| Canonical transient NRMSE (%) | 12,096 / 12,096 | 9.56 × 10⁻¹² percentage points | 8.84 × 10⁻⁹ percentage points |
| Perturbation-coordinate transient NRMSE (%) | 12,096 / 12,096 | 1.10 × 10⁻¹¹ percentage points | 9.29 × 10⁻⁹ percentage points |

The maximum relative differences can be very large when the underlying residual is near zero; they should not be read without the absolute differences. More importantly, all 144 basis hashes differed between the runs, as did all 144 projected conductance, capacitance and input-matrix hashes. Only 72 of the 216 recorded full-Hines trace hashes were identical.

The DFT identities still passed in both runs: maximum relative error was 8.78149 × 10⁻¹² for run 45585262246 and 8.92962 × 10⁻¹² for run 45585843464, each below the 2 × 10⁻⁸ tolerance. Passing the identity gate validates the finite-record decomposition inside each run; it does not imply that two separately constructed PRIMA bases are identical.

## 3. Which scientific observations survived the run-to-run change?

The following table compares the median combined-nine-port / seven-port error ratio across 378 matched cases per morphology and window.

| Morphology | Window | Discrete-BE ratio, run 1 → run 2 | Perturbation-transient ratio, run 1 → run 2 |
|---|---:|---:|---:|
| Jacobs Control | 20 ms | 1.001 → 1.002 | 1.317 → 0.998 |
| Jacobs Control | 40 ms | 1.002 → 1.003 | 1.427 → 1.047 |
| Tamas human Control comparison | 20 ms | 32.267 → 32.627 | 25.268 → 26.331 |
| Tamas human Control comparison | 40 ms | 28.033 → 27.728 | 49.841 → 51.882 |
| Allen L2/3 epilepsy specimen | 20 ms | 1.131 → 1.351 | 1.434 → 1.696 |
| Allen L2/3 epilepsy specimen | 40 ms | 1.157 → 1.382 | 1.349 → 1.504 |
| Peng mouse Control | 20 ms | 42.412 → 38.781 | 106.945 → 124.504 |
| Peng mouse Control | 40 ms | 32.576 → 32.645 | 66.254 → 61.280 |

Interpretation:

1. **Tamas and Peng retain a very large combined-layout penalty in both runs.** This qualitative observation is robust to the observed CPU-feature change, although its precise magnitude is not bitwise reproducible yet.
2. **Jacobs is not stable enough for the earlier transient conclusion.** The first run suggested a 1.3–1.4× perturbation-coordinate penalty; the second was near neutral. The earlier point estimate must not be promoted as a stable morphology effect.
3. **Allen remains a moderate, source/model-dependent case, but the exact effect size moves materially.** It is one epilepsy-surgery reconstruction, not a healthy-control population.
4. The two runs do not justify a universal port-layout recommendation. Absolute errors, ratios and source/window strata must remain side by side.

## 4. Numerical-dispatch pin now added to the workflows

The four-layout primary workflow and basis-order workflow now request:

- OPENBLAS_CORETYPE=Haswell
- OPENBLAS_NUM_THREADS=1
- NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR
- The existing one-thread settings for OMP, MKL, BLIS, VECLIB and NumExpr
- threadpoolctl==3.6.0 for runtime verification.

Before an expensive calculation, the Actions job asserts that threadpoolctl sees the OpenBLAS architecture as Haswell. The finite-window runner repeats that check when it records runtime diagnostics and stores the NumPy CPU-feature map. The basis-order sweep also refuses to use an order-168 reference matrix unless its report records the same OpenBLAS core type and NumPy feature-disable contract.

This is a controlled numerical-dispatch environment, not a claim of universal bitwise reproducibility across every operating system, compiler or BLAS build. The newly pinned order-168 replay is the acceptance test. Only after it passes will the 112/168/224 convergence sweep be allowed to consume that reference.

## 5. Stricter AVX-512 exclusion and current rerun queue

The first successful Haswell order-168 replay is [run 45597945977](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45597945977). It passed all four morphology preflights, the 12,096-row case matrix, 9,072 matched comparisons, 1,728 finite-DFT identity rows and the 2 × 10⁻⁸ identity gate. It used Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3 and NEURON 9.0.2; both bundled OpenBLAS libraries reported Haswell with one thread. However, NumPy's hardware feature map still reported AVX512_SPR as found, although X86_V4 and AVX512_ICL were not found. It therefore establishes the Haswell OpenBLAS pin, but not the stricter no-AVX512 environment now required for the final reference.

The dispatch contract has been tightened to:

- OPENBLAS_CORETYPE=Haswell and OPENBLAS_NUM_THREADS=1;
- NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR;
- exact packages: Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2 and threadpoolctl 3.6.0;
- numpy.lib.introspect.opt_func_info checks that current implementations for the selected float64/complex128 kernels do not use X86_V4 or AVX512 paths.

The observer workflow's three-feature preflight passed on run 45603415289, but skipped its numerical analysis because the committed primary report was still the earlier two-feature result. The latest three-feature primary replay is queued as [run 45604285118](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45604285118), and its corresponding basis-order workflow is queued as [run 45604298291](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45604298291). An older main/basis run is still occupying the concurrency groups; its output is not to be mixed into the final three-feature sweep.

No result from run 45597945977 is discarded: it remains a valid Haswell/one-thread intermediate replay with complete internal DFT identity, but the 112/168/224 convergence study will only use the stricter three-feature order-168 reference.

## 6. Current interpretation hold

- The original two validated artifacts remain immutable and preserved.
- The first run's compact raw matrix and paired post-analysis remain in Git with SHA-256 values recorded in the archive manifest.
- A pinned Haswell order-168 replay has been launched; the run will commit the replacement matrix and updated runtime diagnostics only after the complete identity and coverage gate passes.
- The order sweep has been gated so it cannot silently mix the old, unpinned reference with new pinned order-112 or order-224 calculations.
- No PRIMA order, port layout, solver default or production behavior has been changed by this audit.

Until the pinned replay and convergence sweep finish, treat the Tamas/Peng large-error pattern as a robust preliminary numerical finding, the exact effect sizes as dispatch-sensitive, and the Jacobs/Allen transient conclusions as provisional.
