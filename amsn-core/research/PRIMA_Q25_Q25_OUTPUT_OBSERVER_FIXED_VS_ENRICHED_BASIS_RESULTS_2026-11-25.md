# PRIMA q25 output-observer fixed-vs-enriched basis — recovered numerical results

**Date:** 25 November 2026  
**Original calculation:** [GitHub Actions run 45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599), overall conclusion **failure only at Git archival**  
**Numerical analysis step:** completed successfully; machine-readable report status `passed`  
**Recovered artifact:** [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308)  
**Artifact ZIP:** 1,441,656 bytes; SHA-256 `2391661263ef1c959d550e8a336c8fed89e1f1dfcc626ddab16b3db60bed8aa3`  
**Corrected archival replay:** [run 45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575), still running at the time this recovery report was written.

## 1. Why this result is recoverable

The original workflow's job-step record shows that:
- runtime, pinned dispatch, source checksum, regression tests and accepted order-168 primary-reference gates passed;
- the full fixed-vs-enriched q25 output-observer analysis completed successfully;
- the only failed step was `Commit verified observer-only matrices and summaries`;
- the following artifact-preservation step completed successfully and uploaded artifact 15027601308.

The artifact ZIP was downloaded and its SHA-256 independently recomputed; it exactly matches GitHub's artifact metadata. It contains eight files: the JSON report, 144-row basis-hash table, 3,456-row case matrix, 2,592 paired comparisons, 3,456 finite-DFT identity rows, morphology/source summaries and runtime record.

The report states that all **144/144** independently reconstructed PRIMA basis/G/C/input hashes matched the accepted primary matrix. The primary case-metric SHA-256 recorded in the observer report is `dff980e065b2f497f8aea930b3fd5a16e1db680e80ff84c1d79968430b020c13`, matching the archived primary four-layout matrix manifest.

## 2. Numerical acceptance

| Gate | Recovered result |
|---|---:|
| Observer report status | passed |
| Morphology strata | 4 |
| Port layouts | 4 |
| Q25 output roles | 2 |
| Basis/model hashes matching primary | 144 / 144 |
| Observer case rows | 3,456 |
| Candidate-vs-seven comparisons | 2,592 |
| Source summaries | 2,016 |
| Morphology summaries | 336 |
| Finite-DFT identity rows | 3,456 |
| Maximum finite-DFT identity relative residual | 5.386622461553216e-12 |
| Declared tolerance | 2e-8 |
| Runtime | 2,513.23 s |
| Peak RSS | 368,548 KiB |

The runtime was Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3 and NEURON 9.0.2; Haswell OpenBLAS was constrained to one thread and the active NumPy dispatch list was `X86_V3` plus `baseline(X86_V2)`.

## 3. What the observer experiment actually isolates

For every retained-port layout, both q25 output voltages are measured from their rows in the **full-compartment PRIMA basis**. When a q25 node is not in the retained-port set, it remains an observation-only output and is not added to the input selector (B).

This creates three distinct comparisons for each q25 output:
1. **Retained singly:** the q25 node is the additional retained port in its matching 8-port layout.
2. **Observer-only under the opposite single-port layout:** the other q25 location is retained, while this output remains observation-only.
3. **Both retained:** both q25 nodes are retained in the 9-port layout.

Ratios below are medians across 54 matched cases per morphology, role and window (nine passive scenarios × three input-source locations × two pulse widths). They compare each candidate basis against the seven-port basis for the **same q25 output**. The metric is perturbation-coordinate transient NRMSE. A ratio below 1 means a lower reduced-model error than the seven-port observer-only baseline; above 1 means a higher error.

| Morphology | Q25 output | Window | Retained singly | Observer-only in opposite layout | Both retained |
|---|---|---:|---:|---:|---:|
| Jacobs human Control | Basal | 20 ms | 0.0252 | 1.341 | 0.0232 |
| Jacobs human Control | Basal | 40 ms | 0.0314 | 1.371 | 0.0307 |
| Jacobs human Control | Apical | 20 ms | 1.370 | 0.885 | 1.307 |
| Jacobs human Control | Apical | 40 ms | 1.388 | 1.010 | 1.404 |
| Tamas human Control | Basal | 20 ms | 0.000233 | 3.078 | 0.00551 |
| Tamas human Control | Basal | 40 ms | 0.000398 | 2.712 | 0.00742 |
| Tamas human Control | Apical | 20 ms | 0.000504 | 3.587 | 0.00948 |
| Tamas human Control | Apical | 40 ms | 0.000904 | 3.243 | 0.0173 |
| Allen L2/3 epilepsy specimen | Basal | 20 ms | 0.000423 | 3.599 | 0.000819 |
| Allen L2/3 epilepsy specimen | Basal | 40 ms | 0.000495 | 3.599 | 0.000970 |
| Allen L2/3 epilepsy specimen | Apical | 20 ms | 0.001122 | 4.146 | 0.001230 |
| Allen L2/3 epilepsy specimen | Apical | 40 ms | 0.001184 | 4.146 | 0.001545 |
| Peng mouse Control | Basal | 20 ms | 0.0000236 | 2.121 | 0.000951 |
| Peng mouse Control | Basal | 40 ms | 0.0000502 | 1.814 | 0.001346 |
| Peng mouse Control | Apical | 20 ms | 0.0000672 | 0.621 | 0.001513 |
| Peng mouse Control | Apical | 40 ms | 0.000146 | 0.625 | 0.003053 |

## 4. Main findings

### 4.1 Retaining a q25 port can strongly improve its own readout

For Tamas, Allen and Peng, retaining the q25 output as an input/retained port in its corresponding 8-port basis reduces its own perturbation-transient error dramatically relative to measuring it only from the seven-port basis. Median ratios are approximately (2.3	imes10^{-4}) to (1.2	imes10^{-3}) for these strata. Jacobs basal-q25 also improves substantially (about 0.025–0.031), while Jacobs apical-q25 is near its already-small seven-port residual and does not improve (about 1.37–1.39).

This is a numerical output-approximation result, not proof that a biological neuron requires that particular recording site.

### 4.2 An unretained q25 output can be harmed by retaining the other q25

The observer-only output frequently becomes less accurate when the other q25 location is added to the retained-port set. In Tamas the median ratios are about 2.7–3.6; in Allen about 3.6–4.1. Peng basal-q25 also worsens under the apical-only layout (about 1.8–2.1), whereas Peng apical-q25 improves under the basal-only layout (about 0.62). Jacobs remains close to neutral apart from the more sensitive basal output.

Thus, the benefit is not merely “more ports always improves more outputs.” Adding one port changes the approximation subspace used to reconstruct other outputs.

### 4.3 Retaining both q25 nodes can trade accuracy between the two q25 outputs

The combined nine-port basis still beats the seven-port observer-only baseline for both q25 outputs in Tamas, Allen and Peng. However, it is worse than the corresponding single-q25 basis for the output already retained singly:
- Tamas: combined-vs-single error ratios are roughly 19–24× for each q25 output.
- Peng: roughly 21–40×, depending on q25 role and window.
- Allen: roughly 1.1–2.0×.
- Jacobs: little change for basal; apical remains near baseline.

This is consistent with finite-order basis-budget competition: at order 168, including a second q25 input port changes the basis and redistributes approximation capacity. It is not yet proof that initial seed budget alone causes the effect; basis-order convergence is still required.

### 4.4 Ratios require absolute-error context

A q25 observer residual under the seven-port basis can be very small. Large ratios and tiny ratios can therefore be misleading without the absolute error deltas. The original artifact retains per-case baseline/candidate errors, p90 ratios and all source/pulse strata. The perturbation-coordinate transient metric is the numerically stable transient comparison here; canonical absolute-voltage results are retained separately.

## 5. Limits

The study uses four individual passive morphology reconstructions, not four population samples. Allen NMO_162186 is an epilepsy-surgery specimen, not a healthy control. Peng NMO_163775 metadata says No Diameter. The results apply to the declared passive linear-RC PRIMA approximation, not active ion channels, action potentials, synapses, plasticity, calcium signalling or biological physiology.

No production solver or default changed. Full Hines remains canonical. The artifact is accepted as **numerical analysis evidence**, but the corrected workflow run 45625185575 must still pass its Git archival step before the raw observer files can be marked as committed to the branch.

## 6. Recovered artifact contents

Artifact [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308):
- `prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25_report.json`
- `..._basis_hashes.csv`
- `..._case_metrics.csv`
- `..._layout_vs_seven_comparisons.csv`
- `..._source_summary.csv`
- `..._morphology_summary.csv`
- `..._finite_dft_identity.csv`
- `....time.txt`

The complete original ZIP remains preserved in Actions artifact storage; its exact ZIP digest and all extracted file SHA-256 values are recorded in the companion recovery manifest.
