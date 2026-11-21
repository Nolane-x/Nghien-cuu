# Segev full-tree axial conductance matrix — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 0c17ffe9ddd214397850854c63aa65d40877a536](https://github.com/Nolane-x/Nghien-cuu/commit/0c17ffe9ddd214397850854c63aa65d40877a536)  
**Segev matrix workflow:** [44903533060 — successful, 2/2 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060)  
**Original-morphology matrix regression:** [44903453372 — successful](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453372)  
**Core CI:** [44903453433 — running at report creation](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453433)  
**Summary CSV:** [human_segev_full_tree_axial_matrix_summary_2026-11-21.csv](../results/human_segev_full_tree_axial_matrix_summary_2026-11-21.csv)

## 1. Research question

After matching all individual SWC/Import3D axial edges and topology, do the *assembled whole-tree axial conductance matrices* of AMSN and NEURON agree when both are reduced to exactly the same electrical SWC vertices?

This is stronger than an edge-by-edge morphology audit. It checks the global graph operator produced after section boundaries, segment half-resistances, endpoint caps and soma/wire normalization have all been assembled.

## 2. Method

The existing full-tree axial matrix audit was parameterized for morphology path, morphology label and NEURON mesh cap. Two independent NEURON 9.0.2 jobs ran:

| Cell | Electrical vertices | Axial edges | NEURON sections | NEURON segments |
|---|---:|---:|---:|---:|
| NMO_68174 / cell1125 | 12,399 | 12,398 | 214 | 41,864 |
| NMO_68175 / cell1204 | 13,747 | 13,746 | 189 | 39,245 |

The matrix reduction uses:
- AMSN's unresampled production CableTree and the same electrical-node map used by the simulator.
- Every active SWC edge matched to the corresponding NEURON Import3D pt3d interval.
- Actual NEURON segment ri() centre-to-centre resistances, child-/parent-end half-resistances, and direct partial pt3d taper caps.
- Fixed axial resistivity Ri=0.7 Ω·m and maximum NEURON segment length 0.5 µm.
- 32 deterministic random voltage vectors per morphology, seed 20261121 and 10 mV standard deviation.

For each test vector, both sparse tree Laplacians produce a node-current vector. The comparison is the relative L2 difference between those current vectors. This is a deterministic sampled-vector audit, **not** a computation of the formal induced matrix/operator norm.

The script also checks total-current conservation and the constant-potential nullspace. No dense N×N matrix is formed.

## 3. Edge-wise axial conductance results

| Absolute relative conductance difference | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Median | 0.0001641% | 0.0001800% |
| P95 | 0.0017516% | 0.0019193% |
| P99 | 0.0044951% | 0.0051603% |
| Maximum | 0.0932558% | 0.0359234% |

The maxima are localized to very short apical edges already identified by the full-tree morphology audit:
- NMO_68174: SWC edge 10674→10675, apical, approximately 0.10198 µm.
- NMO_68175: SWC edge 7273→7274, apical, approximately 0.20199 µm.

The global median and tail remain small. A short edge can have a larger relative difference while contributing only a small part of the full operator; this is why the operator-vector comparison is reported separately.

The internal reduction of NEURON's actual ri() chain against its direct pt3d taper integral is exceptionally tight:
- NMO_68174 maximum: 1.984e-11%.
- NMO_68175 maximum: 1.550e-11%.

## 4. Whole-tree axial operator comparison

| Relative L2 current-vector difference over 32 probes | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Mean | 0.0042137% | 0.0020482% |
| P95 | 0.0076496% | 0.0030657% |
| Maximum | 0.0106860% | 0.0032929% |

Additional invariants:

| Invariant | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Maximum absolute node-current difference | 9.845e-10 A | 3.587e-10 A |
| Maximum total-current conservation residual | 4.606e-21 A | 9.503e-21 A |
| Constant-voltage axial nullspace maximum | 0 A | 0 A |

Both matrices conserve total current to around 1e-20 A and annihilate constant voltage exactly in the exported calculation. The sampled whole-operator relative L2 error is below 0.011% for all tested vectors and both cells.

## 5. Interpretation

For these two partial human L2/3 morphologies, the whole-tree axial conductance operator is numerically very close between AMSN and NEURON after both are reduced to the same electrical SWC graph.

This result strengthens the earlier local evidence:
- all active SWC edges map to Import3D;
- branchpoints and section connections are reconciled;
- NEURON segment ri() values reproduce local pt3d integrals;
- the reduced edge conductances agree closely;
- the assembled axial Laplacians produce nearly identical node-current responses over the 32 deterministic test vectors.

It does **not** establish biological accuracy. Both simulators are using the same SWC and the same fixed axial resistivity. It also does not yet compare membrane leak, capacitance, active channels or synapses. The random-vector tests sample the operator but do not prove a formal global spectral-norm bound.

## 6. Reproducibility artifacts

Segev full-tree matrix workflow [44903533060](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060), 2/2 jobs passed:

- NMO_68174 / cell1125: [artifact 14706049920](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060/artifacts/14706049920).
- NMO_68175 / cell1204: [artifact 14706334624](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060/artifacts/14706334624).

The original NMO_290988 full-tree axial conductance matrix regression passed [44903453372](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453372). The complete Core CI for the matrix-script parameterization was running at the time this report was committed; see [44903453433](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453433).

Each raw artifact contains the per-edge conductance matrix CSV, 32 operator-probe rows and the job log. Summary data: [CSV](../results/human_segev_full_tree_axial_matrix_summary_2026-11-21.csv).

## 7. Next step

Extend the comparison from axial-only conductance to the **full passive membrane operator** by adding matched leak and capacitance contributions on a common electrical node/control-volume support. This requires first deriving and validating a consistent mapping of membrane area and capacitance from NEURON segments to AMSN compartments. Keep the axial baseline locked; do not change Ri/Rm/Cm/Eleak to force agreement.
