# PRIMA q25 initial multishift seed-budget audit protocol

**Date:** 25 November 2026  
**Script:** audit_prima_q25_four_morphology_initial_shift_seed_budget.py  
**Workflow:** ../../.github/workflows/amsn-prima-q25-initial-seed-budget.yml

## 1. Question

The fixed-order q25 ablation shows that adding basal-q25 and apical-q25 can change errors at the seven shared outputs. One implementation-level explanation is that each retained port contributes an initial shifted inverse block at each expansion shift. Adding ports can therefore increase the rank consumed before subsequent round-robin Krylov growth begins.

This audit measures that initial seed budget on the same four morphology reconstructions and exact 7/8/8/9-port layouts. It is a structural diagnostic, not a response-error experiment and not proof that seed-budget competition is the sole cause of the q25 error changes.

## 2. Exact protocol

For each of the four checked SWCs, each of the nine passive parameter scenarios, each retained-port layout, and each of the six declared expansion shifts:

1. Build the same cable tree and passive parameter variant used by the primary four-layout experiment.
2. Form the retained-port selector \(B\).
3. At each shift \(\sigma\), solve the same shifted passive system \((G+\sigma C)^{-1}B\) using the existing Hines real-shift solve.
4. Orthogonalize the shifted block against the already accumulated initial seed columns using the same two-pass orthogonalization and relative tolerance \(10^{-12}\).
5. Record the independent columns contributed by that shift, the cumulative initial seed rank, and the remaining number of states at orders 112, 168 and 224.

The six shift values remain 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz. The four layouts are “seven”, “eight_basal_q25”, “eight_apical_q25” and “nine_both_q25”.

The numerical runtime is pinned to Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2 and threadpoolctl 3.6.0. OpenBLAS is pinned to Haswell with one thread. NumPy's complete current SIMD dispatch inventory is collected in an isolated preflight and rejects any active X86_V4 or AVX-512 kernel. The verified target list is handed to the script through GITHUB_ENV; the script does not rerun NumPy introspection in the analysis process.

## 3. Coverage contract

| Output | Expected rows |
|---|---:|
| Four morphology × nine scenarios × four layouts × six shifts | 864 |
| Morphology/scenario/layout initial seed summaries | 144 |
| Morphology/layout summaries across nine scenarios | 16 |

Each model/layout group must have exactly six unique shifts, consistent cumulative rank, nonnegative remaining state budget, and no shift block rank greater than the retained port count. All 144 groups must fit inside each requested order.

## 4. Expected seed-budget interpretation

If all ports contribute linearly independent columns at each of the six shifts, the initial block sizes are:

| Layout | Ports | Initial seed columns | Remaining at order 112 | Remaining at order 168 | Remaining at order 224 |
|---|---:|---:|---:|---:|---:|
| seven | 7 | 42 | 70 | 126 | 182 |
| eight_basal_q25 | 8 | 48 | 64 | 120 | 176 |
| eight_apical_q25 | 8 | 48 | 64 | 120 | 176 |
| nine_both_q25 | 9 | 54 | 58 | 114 | 170 |

These are arithmetic expectations, not assumed observations. The audit records the actual independent rank after each shift. Rank loss or dependence can make the observed seed budget smaller. The later adaptive Krylov growth, frequency distribution, projected operator conditioning and finite-window response errors are not represented by the initial count.

## 5. Interpretation rules

- A difference of 6 or 12 initial seed columns between layouts confirms a real difference in the initial subspace budget for this implementation.
- A larger initial seed budget is not automatically worse: the added columns may also better represent the desired response directions.
- If error penalties shrink at order 224 while seed ranks remain 42/48/54, that is consistent with a fixed-order truncation-budget effect, but the convergence results must be inspected directly.
- If penalties persist at larger order, the retained-port geometry, shift placement, conditioning, and output/source directions require closer study.
- This diagnostic does not validate biological function and does not change solver defaults or production behavior. Four individual morphologies are not a population sample.
