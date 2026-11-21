# AMSN full-tree axial conductance matrix comparison

**Date:** 2026-11-21 (UTC+7)  
**Code commit:** 88747f0c45cb75405a1a2b612161fe93470ffa94  
**Dedicated workflow:** [44872853672 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672)  
**Comprehensive Core CI:** [44872853668 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853668)  
**Raw artifact:** [14694905509](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672/artifacts/14694905509)  
**Script:** amsn-core/examples/human_full_tree_axial_matrix_audit.py

## 1. Question and scope

After the full-tree geometry/topology audit, this experiment asks whether the complete AMSN and NEURON axial conductance operators agree after both are expressed on the same original electrical SWC vertices.

This compares the **axial-only graph Laplacian**. It excludes membrane leak, capacitance, active channels, synapses and voltage integration. It is not a full membrane-coupled system comparison.

## 2. Morphology and common electrical graph

- NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc.
- 8,903 source SWC nodes, 58 non-soma branchpoints and 8 dendritic stems.
- The existing CNG soma normalization collapses 10 soma-outline / wire-attachment edges into the electrical soma node.
- Common graph: **8,893 electrical nodes and 8,892 active axial edges**.
- Partial human temporal-cortex L2–3 reconstruction: soma and basal/apical dendrites, no axon; moderate dendritic completeness; metadata records mesiotemporal sclerosis. Not a population sample or complete healthy neuron.
- CC BY 4.0 attribution remains in the data README.

## 3. Method

### AMSN axial matrix

The full unresampled morphology is converted with SWCMorphology.to_cable_tree(). The tree supplies one axial conductance per retained electrical edge. For edge \(e=(i,j)\),

\[
R^A_{ij}=1/g^A_{ij}, \qquad G^A_{ij}=R^A_{ij}/R_i,
\]

with \(R_i=0.7\;\Omega\,m\).

### NEURON reduction to the same SWC vertices

NEURON 9.0.2 imports the same morphology with maximum segment length 0.5 µm (125 sections, 25,233 segments). Each active SWC edge maps to one adjacent Import3D pt3d interval.

The fine segment chain within each source edge is reduced to a series resistance using:
- actual segment.ri() values between adjacent segment centres;
- actual child-section-start half-resistance where the edge begins at a child connection;
- actual parent-section-end half-resistance where available;
- direct pt3d taper integration for partial endpoint caps that do not coincide with a public ri() location.

Branchpoint/SWC vertices remain shared nodes. Fine nodes inside an original SWC edge are eliminated only for this axial-only series network. This does not eliminate membrane shunts or capacitance.

### Whole-tree operator

For a voltage vector \(v\), each axial graph Laplacian applies

\[
(Lv)_i=\sum_{j\sim i}g_{ij}(v_i-v_j).
\]

The operators are applied directly from sparse edge lists; no dense 8,893 × 8,893 matrix is allocated. Thirty-two deterministic vectors use seed 20261121, mean −65 mV and standard deviation 10 mV. These are numerical probes, not physiological stimuli.

The relative operator error is

\[
\epsilon_L=\frac{\|L_Av-L_Nv\|_2}{\|L_Nv\|_2}.
\]

The audit also checks global axial-current conservation and the constant-voltage nullspace.

## 4. Environment

| Item | Value |
|---|---|
| Runner | Ubuntu 26.04.1 |
| Python | CPython 3.12.16 |
| NumPy | 2.5.5 |
| NEURON | 9.0.2 |
| NEURON sections / segments | 125 / 25,233 |
| NEURON maximum segment length | 0.5 µm |
| Common electrical graph | 8,893 nodes / 8,892 edges |
| Axial resistivity | 0.7 Ω·m |
| Matrix probes | 32; seed 20261121; 10 mV standard deviation |

Run from amsn-core/:

\`\`\`bash
python -m pip install -e ".[test]"
python -m pip install --only-binary=neuron "neuron==9.0.2"
python examples/human_full_tree_axial_matrix_audit.py
\`\`\`

## 5. Edge-wise conductance results

All 8,892 edges were compared.

| Statistic | Absolute relative difference |
|---|---:|
| Median | 0.000163823% |
| 95th percentile | 0.002037106% |
| 99th percentile | 0.003617323% |
| Maximum | 0.015288401% |

The signed mean conductance difference is −1.36035×10⁻⁶%, and the signed median is −1.65264×10⁻⁶%. No meaningful systematic conductance bias is visible at the reported precision.

The maximum is the very short apical edge SWC 5560→5842, approximately 0.156525 µm long. Its discrepancy is consistent with finite pt3d geometry precision becoming more visible on very short edges; this is plausible, not proven causal attribution.

### NEURON series-reduction consistency

| Contribution used across all source edges | Count |
|---|---:|
| Actual segment-centre ri() pairs | 16,332 |
| Actual child-section-start half-resistances | 117 |
| Actual parent-section-end half-resistances | 118 |
| Direct partial pt3d caps | 17,523 |

Maximum difference between the NEURON network reconstructed from actual ri() values plus partial caps and the direct pt3d integral: **1.66425×10⁻¹¹%**.

## 6. Whole-tree Laplacian results

| Operator metric | Result |
|---|---:|
| Mean relative L2 error | 3.530997×10⁻⁶ |
| 95th percentile relative L2 error | 5.984034×10⁻⁶ |
| Maximum relative L2 error | 6.674520×10⁻⁶ |
| Maximum absolute node-current difference | 2.34017×10⁻¹¹ A |
| Maximum total-current conservation residual | 2.39552×10⁻²¹ A |
| Constant-voltage nullspace residual | 0 A |

The mean / p95 / maximum relative operator errors are approximately **0.00035310% / 0.00059840% / 0.00066745%**.

All 32 probes passed the explicit total-current conservation gate of 10⁻¹⁸ A. A constant potential vector is annihilated exactly by both operators.

## 7. Interpretation

**Locally reproduced result:** for this source morphology, Import3D mapping, fixed NEURON segmentation and \(R_i=0.7\;\Omega\,m\), the full AMSN axial-only Laplacian agrees closely with the NEURON axial-only graph after both are expressed on the same 8,893 electrical vertices.

The operator-level error is smaller than the maximum individual edge error because the short-edge discrepancy is local and does not dominate the full-tree norm for these test vectors.

This is a numerical comparison of the axial-only operator. It does not imply identical passive voltage responses once membrane leak/capacitance are included, and it does not prove transient or biological equivalence.

## 8. Failed attempt preserved

The first workflow attempt [44872686688](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872686688) stopped at the three-node Laplacian unit test because its expected current vector was incorrect. The implementation returned the correct sum of edge currents. The expected vector was fixed, the self-test passed and the dedicated workflow then succeeded. No numerical or biological parameter was changed in response.

## 9. Limitations

- One partial morphology, one NEURON version and one fixed segment cap.
- Axial resistances only; leak, capacitance, active conductances, synaptic conductances and time integration are excluded.
- The 32 voltage vectors are numerical probes, not physiological stimuli or a statistical population.
- Branchpoint and soma geometry remain 1-D cable approximations. The eight soma-centre wire attachments are an import-policy assumption, not proof of zero physical stem resistance.
- No experimental membrane voltage data were fitted and no biological acceptance tolerance was established.
- This does not validate NMDA/Ca²⁺, active dendritic spikes, plasticity, metabolism or glial coupling.

## 10. Reproducibility

- Code: amsn-core/examples/human_full_tree_axial_matrix_audit.py.
- Workflow: .github/workflows/amsn-full-tree-axial-matrix-audit.yml.
- Code commit: 88747f0c45cb75405a1a2b612161fe93470ffa94.
- Dedicated workflow: [44872853672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672), 1/1 success.
- Artifact: [14694905509](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672/artifacts/14694905509).
- Artifact CSVs: human_full_tree_axial_matrix_edges_2026-11-21.csv (8,892 edges) and human_full_tree_axial_matrix_probes_2026-11-21.csv (32 probes).
- Compact committed summary: amsn-core/results/human_full_tree_axial_matrix_summary_2026-11-21.csv.

Comprehensive Core CI also completed successfully for the same code commit: [44872853668](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853668), 4/4 jobs; 65 tests passed on Python 3.12 and 65 on Python 3.13, with both NEURON cross-validation jobs successful.
