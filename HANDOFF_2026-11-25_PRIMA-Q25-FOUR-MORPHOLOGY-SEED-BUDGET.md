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

The fresh full-dispatch strict run is [45613803039](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039). At the latest checkpoint:

- pinned runtime installation and full NumPy dispatch preflight passed;
- source download/checksum passed;
- four-layout/finite-window regression tests passed;
- all four q25 morphology preflights passed;
- the long 7/8/8/9-port calculation is running;
- coverage/finite-DFT identity, result commit and artifact upload have not yet run.

The older [run 45608561071](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071) passed its preflight/tests but remains stuck in the long calculation in the former concurrency group. Do not treat it as complete. The workflow concurrency group was changed so run 45613803039 can execute independently; the older pending [run 45610056257](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45610056257) is still queued in the former group.

### Downstream convergence and output observer

The basis-order workflow [45610065386](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45610065386) and observer workflow [45610073270](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45610073270) passed their own tests/runtime gates but correctly deferred numerical analysis because the committed order-168 report still refers to an older dispatch environment. Once the strict primary report and compact matrices are committed, the push trigger should launch the 112/168/224 sweep and observer workflow. Both must consume the new strict primary report; do not mix old two-feature/Haswell-intermediate matrices with the accepted no-AVX512 full-dispatch reference.

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
