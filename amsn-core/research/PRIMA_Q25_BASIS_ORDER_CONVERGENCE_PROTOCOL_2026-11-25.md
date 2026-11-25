# PRIMA q25 four-layout basis-order convergence protocol

**Protocol date:** 25 November 2026  
**Primary reference:** order 168, four morphologies, four layouts  
**Additional orders:** 112 and 224  
**Driver:** run_prima_q25_four_layout_basis_order_convergence.py  
**Workflow:** ../../.github/workflows/amsn-prima-q25-basis-order-convergence.yml

## 1. Question

The four-layout experiment found morphology-dependent effects after adding basal-q25, apical-q25 or both probes at PRIMA basis order 168. This follow-up asks whether those paired error and interaction patterns persist when the approximation order is reduced to 112 or increased to 224.

This is a numerical convergence/sensitivity study. It is not a biological test and it does not alter the full-Hines reference or production defaults.

## 2. Order grid and source of each matrix

| Basis order | Source | Use |
|---:|---|---|
| 112 | Fresh run from the common four-layout runner | Lower-order sensitivity point |
| 168 | Previously completed and validated four-layout matrix | Reference point; raw case metrics and candidate comparisons are reused |
| 224 | Fresh run from the common four-layout runner | Higher-order sensitivity point |

Order 168 is not recomputed by the sweep driver. Its raw case-metric and candidate-comparison files must already be committed and its report must declare the exact 168 order and complete coverage. The driver refuses to start without those three reference files.

Order 280 is intentionally not part of the first pass. It is a further study only if order 224 does not show adequate stabilization or if the 112/168/224 trajectories remain non-monotonic.

## 3. Fixed protocol

All other settings are held constant across the three orders:

- Four individual morphologies: NMO_163775 Peng mouse Control; NMO_107159 Tamas human Control comparison pyramidal cell; NMO_03524 Jacobs human Control; NMO_162186 Allen human L2/3 epilepsy surgery specimen.
- Four layouts: seven shared ports; eight with basal-q25; eight with apical-q25; nine with both q25 probes.
- Same seven shared output SWC node IDs, same q25 node IDs, same source injection nodes and same 0.5-µm NEURON mesh cap as the [four-layout ablation protocol](PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_PROTOCOL_2026-11-25.md).
- Nine passive parameter scenarios; source locations soma, basal-q75 and apical-q75.
- 10-pA pulses of 2 ms and 10 ms, onset 2 ms; timestep 0.00625 ms; observation windows 20 ms and 40 ms.
- Same expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Same finite-record backward-Euler derivation, including the terminal-state correction and transfer/boundary cross-term.

The runner is the same numerical implementation used by the order-168 matrix. Only its basis-order parameter and output file stem vary.

## 4. Coverage contract

Every successful order must produce exactly:

| Output | Rows |
|---|---:|
| Four-layout case metrics | 12,096 |
| Matched candidate-vs-seven pairs | 9,072 |
| Paired source/layout/window summaries | 144 |
| Morphology/layout/window summaries | 24 |
| Finite-DFT identity diagnostics | 1,728 |
| Post-analysis source summaries | 1,008 |
| Post-analysis morphology summaries | 168 |
| Basal/apical interaction summaries | 336 |

The master grid remains 3,201 frequencies and the frequency matrix remains 1,075,536 rows per order. Each order must pass the same pinned morphology SWC checks, exact node-set assertions, finite-DFT identity tolerance (2 × 10⁻⁸), and CSV read-back checks as the primary experiment.

The post-analysis script independently revalidates all four layouts per paired case and recomputes the candidate/seven ratios from raw case metrics before creating the interaction tables.

## 5. Comparisons and outputs

The driver reuses order 168 and computes orders 112 and 224. For every order, it creates:
- the raw case metrics and candidate-vs-seven comparison matrix;
- morphology/layout/window and source/layout/window summaries;
- finite-DFT identity rows and machine-readable runner report;
- paired post-analysis source, morphology and interaction summaries.

It then creates combined source, morphology and interaction tables indexed by basis order, plus a manifest containing matrix checksums, basis orthogonality maxima, unique basis-hash counts, identity maxima, runtime and per-order pass/fail status.

The complete frequency matrix for each fresh order is retained in the Actions artifact. Individual frequency-summary CSVs are intentionally excluded from Git because each is about 190 MB and exceeds GitHub's per-file limit. The compact metrics, matched comparisons, identity rows and reports are committed.

## 6. Interpretation rules

1. Keep each morphology separate. The four reconstructions are not a representative population.
2. Compare both absolute error values/deltas and candidate/seven ratios. A very small seven-port residual can make a ratio large without a correspondingly large absolute error.
3. Keep discrete-BE periodic transfer, continuous-AC, canonical absolute-voltage transient and perturbation-coordinate transient metrics separate.
4. Do not call the multiplicative basal/apical contrast a causal or biological interaction. It is a descriptive paired numerical contrast on a log-error scale.
5. Do not claim convergence from one median alone. Inspect median, p90, worse-pair fraction, absolute-error change, identity residual, basis orthogonality and basis hashes together.
6. No layout should be promoted to a default solely from this passive linear-RC experiment. Full Hines remains the canonical reference.

## 7. Failure and partial-result handling

The sweep attempts order 112 and then 224. A per-order report is written only after that order's primary calculation and validation finish. The driver records a failed order explicitly and retains successful orders and their compact outputs. If either additional order fails, the combined manifest status is partial and the workflow is expected to report a failed overall sweep while still committing valid per-order outputs and uploading the available artifact for diagnosis.
