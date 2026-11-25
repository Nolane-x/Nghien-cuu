# PRIMA q25 four-morphology initial shift seed-budget — results

**Date:** 25 November 2026  
**Protocol:** [initial shift seed-budget audit](PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_PROTOCOL_2026-11-25.md)  
**Workflow run:** [45612672472 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472)  
**Result commit:** \`f06e277165d6cd8929c152c2ddb2b6e537e4ccb1\`  
**Artifact:** [15021770119 — 9,371 bytes](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472/artifacts/15021770119)

## 1. Execution and coverage

The independent diagnostic completed and committed successfully. Every CI step passed, including the strict numerical-runtime/SIMD gate, all four source/preflight checks, eight regression tests, the 864-row computation, result commit and artifact upload.

| Coverage item | Expected | Observed |
|---|---:|---:|
| Morphologies | 4 | 4 |
| Passive parameter scenarios per morphology | 9 | 9 |
| Port layouts | 4 | 4 |
| Expansion shifts per layout/scenario | 6 | 6 |
| Raw initial-shift rows | 864 | 864 |
| Morphology × scenario × layout groups | 144 | 144 |
| Morphology × layout summaries | 16 | 16 |

Wall time was **31.62 seconds**. The raw-seed CSV SHA-256 is \`4aa61b37b5923e4383114afc005e4793b8ed629450d82d801b2f732c352ccda4\`.

The run pinned Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2 and threadpoolctl 3.6.0. Both observed OpenBLAS pools reported Haswell and one thread. \`NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR\` was applied. Unfiltered \`numpy.lib.introspect.opt_func_info()\` reported only \`X86_V3\` and \`baseline(X86_V2)\` as active targets; there was no active X86_V4 or AVX-512 implementation.

## 2. Main result: actual independent initial seed rank

The total independent columns contributed by the six initial expansion shifts were constant across all nine passive scenarios within each morphology/layout pair.

| Morphology | 7-port baseline | Basal-only 8-port | Apical-only 8-port | Combined 9-port |
|---|---:|---:|---:|---:|
| Jacobs Control | 33 | 39 | 34 | 40 |
| Tamas human Control comparison | 42 | 48 | 48 | 54 |
| Allen L2/3 epilepsy specimen | 42 | 48 | 48 | 54 |
| Peng mouse Control | 42 | 48 | 48 | 54 |

This is the rank **after** each initial block is orthogonalized against all previously seeded blocks. It is therefore more informative than simply multiplying port count by six.

### Jacobs: shift-to-shift rank redundancy

For the nominal Jacobs scenario, the independent columns contributed at shifts 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz were:

| Layout | Independent columns per shift | Total |
|---|---|---:|
| seven | 7, 6, 5, 6, 5, 4 | 33 |
| basal-only | 8, 7, 6, 7, 6, 5 | 39 |
| apical-only | 8, 7, 4, 7, 4, 4 | 34 |
| both q25 | 9, 8, 5, 8, 5, 5 | 40 |

The additional apical-q25 selector therefore adds only **one** independent column across the six initial shifts relative to the seven-port baseline in this morphology. The basal-q25 addition adds six; including both adds seven, not twelve. This rank pattern is stable in total across all nine parameter scenarios, although individual per-shift allocations can vary slightly.

### Tamas, Allen and Peng: full nominal rank at each initial shift

For each of these three morphologies, every shift contributes the full retained-port count:

| Layout | Independent columns per shift | Total |
|---|---|---:|
| seven | 7, 7, 7, 7, 7, 7 | 42 |
| basal-only | 8, 8, 8, 8, 8, 8 | 48 |
| apical-only | 8, 8, 8, 8, 8, 8 | 48 |
| both q25 | 9, 9, 9, 9, 9, 9 | 54 |

Thus, for these three individual reconstructions, each q25 port adds six independent initial seed columns and the combined layout adds twelve relative to seven.

## 3. Remaining state budget

The table reports the median remaining requested states after the initial shifts. The values are constant across the nine scenarios for each morphology/layout pair.

| Morphology | Layout | Seed columns | Remaining at order 112 | Remaining at order 168 | Remaining at order 224 |
|---|---|---:|---:|---:|---:|
| Jacobs | seven | 33 | 79 | 135 | 191 |
| Jacobs | basal-only | 39 | 73 | 129 | 185 |
| Jacobs | apical-only | 34 | 78 | 134 | 190 |
| Jacobs | both q25 | 40 | 72 | 128 | 184 |
| Tamas | seven | 42 | 70 | 126 | 182 |
| Tamas | basal-only | 48 | 64 | 120 | 176 |
| Tamas | apical-only | 48 | 64 | 120 | 176 |
| Tamas | both q25 | 54 | 58 | 114 | 170 |
| Allen | seven | 42 | 70 | 126 | 182 |
| Allen | basal-only | 48 | 64 | 120 | 176 |
| Allen | apical-only | 48 | 64 | 120 | 176 |
| Allen | both q25 | 54 | 58 | 114 | 170 |
| Peng | seven | 42 | 70 | 126 | 182 |
| Peng | basal-only | 48 | 64 | 120 | 176 |
| Peng | apical-only | 48 | 64 | 120 | 176 |
| Peng | both q25 | 54 | 58 | 114 | 170 |

For the Tamas/Allen/Peng pattern, the initial shifts occupy 37.50% of order 112, 25.00% of order 168 and 18.75% of order 224 for the seven-port layout. The combined nine-port layout occupies 48.21%, 32.14% and 24.11%, respectively. The additional two q25 ports therefore consume a further 10.71, 7.14 and 5.36 percentage points of the initial order budget at orders 112, 168 and 224.

Jacobs is different: the initial seed rank is lower because shifted blocks have more inter-shift redundancy after orthogonalization. Its seven-port baseline occupies 29.46%, 19.64% and 14.73% of orders 112, 168 and 224; the combined layout occupies 35.71%, 23.81% and 17.86%.

## 4. What this supports — and what it does not

The audit establishes that adding q25 ports changes the initial independent Krylov seed budget, but **the size of that change is morphology-dependent**:

- Tamas, Allen and Peng: each additional q25 port contributes six more independent seed columns across the six shifts.
- Jacobs: basal-q25 contributes six, apical-q25 contributes one, and the combined layout contributes seven.

This is a concrete implementation-level pathway by which a fixed-order multishift reduction can allocate a different portion of its finite state budget to initial port-driven blocks. It makes seed-budget competition a plausible contributor to the non-monotonic error changes already seen in the fixed-order ablation.

### Important counterexample: equal seed ranks, different response errors

Allen, Tamas and Peng have **identical initial seed ranks for every layout** (42/48/48/54), yet the combined-nine-port perturbation-transient median ratios in the accepted earlier order-168 matrix differ substantially:

| Morphology | 20-ms combined/seven ratio | 40-ms combined/seven ratio |
|---|---:|---:|
| Tamas | 25.27× | 49.84× |
| Allen | 1.43× | 1.35× |
| Peng | 106.95× | 66.25× |

This is direct evidence that the scalar initial-seed count is not sufficient to predict response error. Allen and Tamas/Peng consume the same number of independent initial columns, but the resulting approximation errors are very different. The seed-budget effect can describe one part of fixed-order allocation; the morphology-specific directions of the added basis vectors, projected dynamics and source/output weighting must also matter. This is why the diagnostic must not be presented as a single-cause explanation.


It is not proof that this is the only cause. The diagnostic does not measure later Krylov growth, final basis overlap, approximation error or convergence. It also does not establish a biological interaction. The four inputs are individual passive reconstructions, not a population sample. The 112/168/224 response-error sweep and output-observer analysis are still needed before deciding whether the error penalty shrinks with order or persists after the initial seed-budget difference is accounted for.

No production solver setting or retained-port default is changed.

## 5. Machine-readable files

Committed under \`amsn-core/results/\`:

- \`prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25_raw.csv\` — all 864 per-shift rows;
- \`prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25_model_summary.csv\` — 144 morphology/scenario/layout groups;
- \`prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25_morphology_summary.csv\` — 16 morphology/layout aggregates;
- \`prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25_report.json\` — coverage, runtime, active SIMD targets, input checksums and limits.
