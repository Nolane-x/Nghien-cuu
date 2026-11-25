# Handoff — PRIMA q25 four-morphology 7/8/8/9-port study and seed budget

**Date:** 25 November 2026  
**Active branch:** \`research/prima-q25-cross-morphology-boundary-replication-2026-11-25\`  
**Repository:** [Nolane-x/Nghien-cuu](https://github.com/Nolane-x/Nghien-cuu)

## Completed in this checkpoint

### Four-morphology four-layout boundary study

The earlier accepted 7/8/8/9-port experiment uses four individual passive morphology reconstructions and the same seven shared output sites, adding basal-q25, apical-q25 or both. The accepted result tables, protocol and scientific caveats are in:

- \`amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_PROTOCOL_2026-11-25.md\`
- \`amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_RESULTS_2026-11-25.md\`
- full frequency matrix / source SWC and runtime evidence: [artifact 15010408589](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45585262246/artifacts/15010408589)

Coverage is 1,075,536 frequency rows, 12,096 case metrics, 9,072 matched comparisons, 144 source/layout/window summaries, 24 morphology/layout/window summaries and 1,728 finite-DFT identities. Maximum finite-identity relative error was 8.78149e-12 against a 2e-8 tolerance. The initial result run's later Git commit failure was the oversized frequency CSV exceeding GitHub's 100-MB file limit; the full matrix remained in the artifact, and the archival workflow was subsequently corrected to keep only compact tables in Git.

### Initial multishift seed-budget audit — now accepted

The independent full-dispatch seed-budget diagnostic passed completely:

- [Actions run 45612672472](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472)
- [artifact 15021770119](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472/artifacts/15021770119)
- result commit: \`f06e277165d6cd8929c152c2ddb2b6e537e4ccb1\`
- raw rows: 864; morphology × scenario × layout groups: 144; morphology × layout summaries: 16
- runtime: 31.62 s; all eight regression tests, runtime/SIMD check, four SWC/preflight checks and commit/upload steps passed.

Key result: independent initial seed ranks after cross-shift orthogonalization:

| Morphology | 7-port | Basal-only 8-port | Apical-only 8-port | Both 9-port |
|---|---:|---:|---:|---:|
| Jacobs | 33 | 39 | 34 | 40 |
| Tamas | 42 | 48 | 48 | 54 |
| Allen | 42 | 48 | 48 | 54 |
| Peng | 42 | 48 | 48 | 54 |

For Jacobs, the apical-q25 addition contributes only one extra independent initial column across six shifts, whereas the basal addition contributes six. For Tamas, Allen and Peng, each q25 port contributes six. This is a measured initial subspace-budget difference and a plausible contributor to fixed-order error changes, not proof of a sole cause: later Krylov growth, complete basis construction and response-error convergence are not measured by this diagnostic.

Detailed results and method:

- \`amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_PROTOCOL_2026-11-25.md\`
- \`amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_RESULTS_2026-11-25.md\`
- \`amsn-core/research/audit_prima_q25_four_morphology_initial_shift_seed_budget.py\`
- \`amsn-core/tests/test_prima_q25_four_morphology_initial_shift_seed_budget.py\`

The strict environment in this audit used Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2, threadpoolctl 3.6.0, Haswell OpenBLAS with one thread, and \`NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR\`. Unfiltered NumPy dispatch inspection found only \`X86_V3\` and \`baseline(X86_V2)\` active.

## Current unfinished work

### Strict order-168 primary response matrix

The accepted selected-kernel strict matrix is [run 45608561071](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071), completed success with 12,096 case rows, 9,072 matched comparisons, 1,728 finite-DFT identity rows and maximum identity relative error \(8.78149\times10^{-12}\) against \(2\times10^{-8}\). Result commit is \`1ccac2315a3580505474dbbd188dfc89ef884543\`; artifact 15021668387.

A fresh full-functions-dispatch primary replay is [run 45613803039](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039). It passed runtime install, the unfiltered NumPy dispatch check, four-layout/finite-window tests and all four q25 morphology preflights; its long 7/8/8/9-port calculation remains in progress. Its coverage/identity gate, report commit and artifact upload have not yet executed. Use 456085 as the currently accepted primary matrix; only replace it with 456138 if that fresh run passes every gate.

### Downstream convergence

The earlier in-process sweep failed with native exit code 139 after passing runtime, reference gate, tests and q25 preflights. The failure occurred when the driver imported the full NEURON runner module and called its main function in the same interpreter. The driver is now changed to launch each order in a fresh child process; the runner accepts order and result-stem overrides from the child environment.

Latest isolated-process sweep: [run 45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005). It passed runtime/dispatch verification, source checksum, basis-order regression tests, all morphology preflights and the strict order-168 reference gate; its 112/224 sweep step is in progress. It must still pass both fresh matrices, exact coverage/identity, paired posthoc checks and combined summary validation before being accepted. The previous in-process [run 45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400) is still running under the old concurrency group; do not treat it as the current implementation.

### q25 output observer

The observer has two separate acceptance layers: exact primary/observer NumPy dispatch equality, and reproduction of all 144 primary basis/G/C/input hashes. The primary dispatch is now assigned and verified before comparison; q25 retained/observer-only role mapping is now computed before checking the output projection. Regression tests cover both cases.

The most recent instrumented run is [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599). It passed runtime, all-function dispatch, source checksum, observer regression tests and the primary report gate. Its numerical analysis is still running. Flushed \`OBSERVER_STAGE\` markers identify morphology import, Hines replays, PRIMA basis build and reduced simulation so the next failed native stage can be pinpointed if exit 139 recurs.

An additional observer run [45616562335](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616562335) is running an earlier fixed-code revision under the previous concurrency group; the latest instrumented run 45616908599 is the one to inspect for stage evidence. Earlier failures are retained in Actions history: 45615543451/45616181315 had Python variable-order errors; 45616497506 passed Python gates but ended with native exit 139. These failures are not accepted results.

### GitHub Actions trigger note

The primary result archive was committed by a workflow using \`GITHUB_TOKEN\`, so that bot push did not automatically fan out to downstream \`push\` workflows. Separate connector-authored workflow commits were used to trigger the basis and observer jobs. Keep this distinction in the research log; do not infer that a downstream job ran merely because the primary artifact was committed.

## Scientific constraints

- Four morphology reconstructions are individual specimens, not population samples.
- Allen NMO_162186 is an epilepsy surgery specimen, not a healthy control.
- Peng NMO_163775 metadata reports No Diameter; do not describe its source diameters as measured biological diameters.
- All q25 reduction studies here are passive linear-RC numerical experiments. No active channels, synapses, plasticity, action-potential fidelity or biological validity are established.
- Ratios must be read with absolute error deltas because very small baseline residuals can inflate ratios.
- Full Hines remains the canonical reference; no production PRIMA order, solver behavior, retained-port default or runtime default has been changed.

## Next concrete sequence

1. Finish and validate run 45613803039. Require exact coverage and finite-record DFT identity before accepting its order-168 matrices.
2. Confirm the report records all-function active NumPy dispatch targets and the exact Haswell/thread/package environment.
3. Run the paired post-analysis on the newly committed matrix.
4. Let the basis-order workflow compute fresh order 112 and 224, reusing only the accepted strict order-168 metrics/comparisons.
5. Run the fixed-vs-enriched q25 output observer only after all 144 primary basis/G/C/input hashes and dispatch targets match.
6. Compare absolute errors, paired ratios, seed-budget occupancy, basis hashes, orthogonality and finite-DFT residuals. Keep each morphology separate; no production changes without broader validation.
