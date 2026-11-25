# PRIMA q25 four-morphology initial multishift seed-budget audit — protocol

**Date:** 25 November 2026  
**Branch:** `research/prima-q25-cross-morphology-boundary-replication-2026-11-25`  
**Implementation:** `research/audit_prima_q25_four_morphology_initial_shift_seed_budget.py`  
**Tests:** `tests/test_prima_q25_four_morphology_initial_shift_seed_budget.py`  
**Workflow:** `.github/workflows/amsn-prima-q25-initial-seed-budget.yml`

## 1. Question

The four-layout q25 ablation changes the retained-port selector at a fixed PRIMA order. The implementation seeds a multishift rational-Krylov basis from shifted inverse blocks before growing the remaining basis in round-robin order. This audit measures the **independent columns actually added by those initial shift blocks**, after orthogonalization against columns seeded by earlier shifts.

It answers a narrow implementation question: how much of the requested state order is occupied before later Krylov growth begins, and how does that depend on morphology and the basal/apical q25 additions?

It does not rerun the full transient response matrix, compute a final 112/168/224 reduced basis, or claim that seed-budget competition is the sole cause of response-error changes.

## 2. Matched design

The diagnostic uses the same four pinned holdouts, q25 node identities, source SWC checksums and 0.5-µm NEURON segment cap as the four-layout boundary ablation.

| Morphology | NeuroMorpho ID | Shared seven SWC IDs | Basal-q25 | Apical-q25 |
|---|---|---|---:|---:|
| Peng mouse Control | NMO_163775 | 1, 144, 3926, 4180, 40, 4104, 3948 | 224 | 4096 |
| Tamas human pyramidal Control | NMO_107159 | 1, 6363, 4735, 5564, 7023, 4301, 4623 | 6609 | 4404 |
| Jacobs human Control | NMO_03524 | 1, 367, 583, 751, 866, 867, 868 | 272 | 864 |
| Allen L2/3 epilepsy surgical specimen | NMO_162186 | 1, 515, 2261, 2304, 4180, 4262, 6608 | 2713 | 4488 |

The four layouts are exactly:

- `seven`: the canonical seven shared ports;
- `eight_basal_q25`: the same seven plus basal-q25;
- `eight_apical_q25`: the same seven plus apical-q25;
- `nine_both_q25`: the same seven plus both q25 ports.

For every morphology and each of the nine passive parameter scenarios, the audit constructs each layout and processes these six expansion shifts in fixed order:

\[
0,\ 100,\ 1000,\ 3000,\ 6000,\ 10000\ \text{Hz}.
\]

The requested state orders are 112, 168 and 224. The initial shifted solves are rank-counted up to the maximum requested order, 224. At every shift, the script uses the same Hines shifted passive solve and twice-reorthogonalized block routine used by the conditioning audit:

- `_solve_shifted_passive_real(tree, shift_per_s, selector)`;
- `_orthogonalize_block(start, basis_columns, relative_tolerance, max_order)`.

For each shift it records new independent columns, cumulative columns and remaining budget. The model-level output derives the remaining states and occupied fraction at all three requested orders.

## 3. Coverage and pinned numerical runtime

| Output | Expected | Observed |
|---|---:|---:|
| Raw shift rows | 864 | 864 |
| Morphology × scenario × layout groups | 144 | 144 |
| Morphology × layout summaries | 16 | 16 |
| Morphologies | 4 | 4 |
| Parameter scenarios per morphology | 9 | 9 |
| Expansion shifts per group | 6 | 6 |

All four SWC checksums and source/preflight manifests were revalidated. The audit completed in 31.62 seconds.

Pinned runtime:

- Python 3.12.16
- NumPy 2.5.5
- SciPy 1.16.3
- NEURON 9.0.2
- threadpoolctl 3.6.0
- `OPENBLAS_CORETYPE=Haswell`, one OpenBLAS thread
- `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR`
- all functions/signatures returned by unfiltered `numpy.lib.introspect.opt_func_info()` were checked; active targets were `X86_V3` and `baseline(X86_V2)`, with no active X86_V4/AVX-512 dispatch.

The report stores full runtime diagnostics and the exact active dispatch target list.

## 4. Interpretation rules

1. “Initial seed columns” means independent columns surviving orthogonalization across the six initial shifted inverse blocks. It is **not** the nominal raw block-column count and not the final basis size.
2. Remaining budget is requested order minus cumulative initial independent seed rank. Later round-robin Krylov growth, rank loss and the final basis construction are not included.
3. Compare morphologies separately. These are four individual reconstructions, not a population sample.
4. The observed seed-budget difference is a plausible contributor to fixed-order approximation changes, but this audit is not a causal intervention. The full order-convergence sweep and matched output-observer comparison remain necessary to determine how the error differences evolve with order.
5. This is passive linear-RC numerical analysis only. It does not assess active channels, action potentials, nonlinear synapses, plasticity or biological validity.
6. No production PRIMA order, retained-port layout, solver default or production behavior is changed.

## 5. Reproducibility

The workflow is independently executable with `workflow_dispatch` and also runs on relevant pushes to the research branch. It performs the full runtime/SIMD gate, downloads and checksum-verifies the Allen SWC, checks all four pinned preflight manifests, runs regression tests, computes the tables, commits compact results and uploads a 90-day artifact.

The machine-readable report and CSVs are committed under `amsn-core/results/prima_q25_four_morphology_initial_shift_seed_budget_2026-11-25_*`.
