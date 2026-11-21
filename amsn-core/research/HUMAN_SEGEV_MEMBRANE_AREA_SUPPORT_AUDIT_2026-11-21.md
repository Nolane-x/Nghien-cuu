# Segev membrane area on matched control-volume support — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 7cefa688510f4f965afcdfc2c06f00312200e1de](https://github.com/Nolane-x/Nghien-cuu/commit/7cefa688510f4f965afcdfc2c06f00312200e1de)  
**Workflow:** [44904138720 — successful, 2/2 morphology jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720)  
**Summary CSV:** [human_segev_membrane_area_support_summary_2026-11-21.csv](../results/human_segev_membrane_area_support_summary_2026-11-21.csv)

## 1. Research question

Does NEURON's actual segment membrane area, when assigned to the same electrical SWC endpoint control volumes used by AMSN, reproduce AMSN's per-node membrane area distribution?

The earlier Segev checks established global total-area agreement below 1.2e-6%. That is necessary but not sufficient for a passive membrane operator: every electrical node carries a local leak conductance and capacitance, so the area must be assigned to the correct control volume, not merely conserved in aggregate.

## 2. Control-volume mapping method

AMSN's node-centred CableTree splits each tapered SWC frustum at its geometric midpoint and assigns the proximal half-surface area to the parent electrical node and the distal half to the child.

This audit reconstructs that exact support on NEURON Import3D:

1. Import the same CNG SWC into NEURON 9.0.2 at a 0.125 µm maximum segment length.
2. Read the actual NEURON segment.area() for every segment.
3. Map each active SWC edge to the matching Import3D pt3d interval.
4. Split the edge at its tapered-frustum midpoint.
5. Intersect each NEURON segment interval with the two half-edge regions.
6. Distribute each measured segment.area() in proportion to the pt3d geometric surface area of its overlap with each half-edge.
7. Accumulate the allocated area at the parent/child electrical SWC nodes and compare every node with AMSN CableTree.area_m2.

Soma-section area is assigned to the root soma control volume. Collapsed soma-wire connector edges do not contribute cable membrane area. Each non-soma section has per-segment and per-section closure checks to ensure that no measured NEURON segment area is omitted or counted twice.

This is a matched-support allocation of measured segment totals, using pt3d surface geometry to partition each segment. It is not a native NEURON node-centred membrane representation and should be read as a controlled mapping, not as an exact continuous membrane field.

## 3. Results

| Metric | NMO_68174 / cell1125 | NMO_68175 / cell1204 |
|---|---:|---:|
| NEURON sections | 214 | 189 |
| NEURON segments | 166,856 | 156,471 |
| Electrical control volumes | 12,399 | 13,747 |
| Active SWC edges | 12,398 | 13,746 |
| AMSN total membrane area | 89,374.560790 µm² | 83,861.873830 µm² |
| NEURON allocated membrane area | 89,374.559790 µm² | 83,861.873158 µm² |
| Total area difference | −0.000001119% | −0.000000801% |

### Per-node control-volume area difference

| Absolute relative difference | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Median | 0.00008137% | 0.00008884% |
| P95 | 0.00068466% | 0.00080180% |
| P99 | 0.00165961% | 0.00193923% |
| Maximum | 0.02558449% | 0.00907464% |

The largest node-support discrepancy is localized to a very small terminal control volume:
- NMO_68174: apical SWC node 9656, 0.193830 µm² in AMSN versus 0.193781 µm² mapped from NEURON (−0.025584%).
- NMO_68175: basal SWC node 2863, 0.344735 µm² in AMSN versus 0.344704 µm² from NEURON (−0.009075%).

### Per-edge half-control-volume area difference

| Absolute relative difference | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Median | 0.00016379% | 0.00017938% |
| P95 | 0.00174860% | 0.00191930% |
| P99 | 0.00449639% | 0.00515999% |
| Maximum | 0.09325774% | 0.03592530% |

The maximum half-edge differences occur on the same very short apical edges identified by the axial-geometry audit:
- NMO_68174 edge 10674→10675, 0.10198 µm, apic[75].
- NMO_68175 edge 7273→7274, 0.20199 µm, apic[15].

### Segment and section area closure

| Closure metric | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Maximum per-segment support closure error | 4.51e-14% | 4.24e-14% |
| Maximum per-section actual-area coverage error | 1.92e-14% | 2.23e-14% |

All 166,856 and 156,471 NEURON segment-area values, respectively, were allocated to the mapped SWC half-edge support. The total area allocated to control volumes equals the raw sum of NEURON segment.area() values; no section's segment area was dropped.

## 4. Interpretation

The result closes a key prerequisite for the passive membrane operator:

- NEURON and AMSN agree not only on total membrane area, but also on the distribution of area over the same electrical SWC nodes to within 0.026% at every tested node.
- The high-percentile node and edge-half errors are around 0.001–0.005%.
- The largest local errors are confined to short apical frusta, not a broad systematic area mismatch.
- The measured NEURON segment area is fully partitioned across the SWC support; the support-closure errors are near floating-point precision.

This substantially reduces the risk that a passive leak/capacitance comparison will be dominated by a gross mismatch in membrane-area support. It does not, by itself, validate passive parameters, channel kinetics, synapses or biological accuracy.

## 5. Reproducibility artifacts

Final workflow [44904138720](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720), 2/2 jobs passed:

- NMO_68174 / cell1125: [artifact 14707141454](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720/artifacts/14707141454).
- NMO_68175 / cell1204: [artifact 14707730197](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720/artifacts/14707730197).

Each artifact includes per-node control-volume area, per-edge half-area allocation, section-level closure metrics and the job log.

Summary data: [CSV](../results/human_segev_membrane_area_support_summary_2026-11-21.csv).

## 6. Next step

Build the matched-support passive admittance operator:
\[
Y(\omega)=L_{\mathrm{axial}}+\operatorname{diag}\left(\frac{A_i}{R_m}+j\omega C_m A_i\right),
\]
using the already-validated electrical graph and per-node area support. Compare leak and capacitance diagonals separately before comparing the combined complex operator. Keep the exact-SWC probe convention and all membrane parameters fixed. Do not interpret a sampled operator match as biological validation.
