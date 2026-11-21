# Segev full-tree axial geometry and topology audit — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** [commit 3b9969971834046835cb9c5bfc4709f1e246ed4e](https://github.com/Nolane-x/Nghien-cuu/commit/3b9969971834046835cb9c5b9c5bfc4709f1e246ed4e)  
**Workflow:** [44903025679 — successful, 2/2 Segev jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025679)  
**Original-audit regression:** [44903025675 — successful](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025675)  
**Axial-matrix regression:** [44903025666 — successful](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025666)  
**Raw summary:** [human_segev_full_tree_axial_audit_summary_2026-11-21.csv](../results/human_segev_full_tree_axial_audit_summary_2026-11-21.csv)

## 1. Research question

Do the two Segev human L2/3 SWCs map completely onto NEURON 9.0.2 Import3D pt3d geometry, and does NEURON's segment/section topology preserve expected branchpoint and axial-resistance relationships?

This follows the AC probe mesh sweep, which bounded probe-readout sensitivity but did not remove every AMSN–NEURON residual. Before changing membrane parameters or the solver, the full morphology edge and section-connection representation needs to be checked.

## 2. Method

The existing single-morphology full-tree audit was parameterized to accept a morphology path, label and NEURON maximum segment length. It was run on:
- NMO_68174 / cell1125: 12,410 SWC records.
- NMO_68175 / cell1204: 13,758 SWC records.

NEURON was pinned to 9.0.2 with 0.5 µm maximum segment length and axial resistivity 0.7 Ω·m. The audit checks:
1. Each electrically retained SWC edge against an adjacent Import3D pt3d interval.
2. Every NEURON segment ri() against its corresponding within-section or child-section-start pt3d interval.
3. Every SWC branchpoint against NEURON child sections and same-section continuations.
4. Every section connection for endpoint geometry and parent-/child-side half-edge resistance.

The audit distinguishes NeuroMorpho three-point soma and zero-resistance Import3D wire attachments from ordinary section junctions. Those import conventions are reported separately.

## 3. Results

| Metric | NMO_68174 / cell1125 | NMO_68175 / cell1204 |
|---|---:|---:|
| SWC nodes | 12,410 | 13,758 |
| SWC branchpoints | 102 | 90 |
| Electrically retained SWC edges | 12,398 | 13,746 |
| Edges mapped to Import3D pt3d | 12,398 / 12,398 | 13,746 / 13,746 |
| Unmapped active edges | 0 | 0 |
| NEURON sections | 214 | 189 |
| NEURON segments at 0.5 µm cap | 41,864 | 39,245 |
| NEURON segment ri() records checked | 41,864 | 39,245 |
| Branchpoints with exact outgoing branch count | 102 / 102 | 90 / 90 |
| Ordinary section endpoint gap maximum | 0 µm | 0 µm |
| Soma wire attachment links | 9 | 9 |
| Maximum soma wire attachment offset | 15.8916 µm | 20.2236 µm |

### Axial geometry integral, SWC versus Import3D pt3d

| Absolute relative difference | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Median | 0.0001641% | 0.0001800% |
| P95 | 0.0017516% | 0.0019193% |
| P99 | 0.0044951% | 0.0051603% |
| Maximum | 0.0932558% | 0.0359234% |

Both morphologies have 100% active-edge mapping coverage. The largest NMO_68174 difference is on a short 0.10198 µm apical edge; the largest NMO_68175 difference is on a 0.20199 µm apical edge. Maximum node-to-pt3d mapping offsets are only 5.88e-5 µm and 5.87e-5 µm, respectively.

### NEURON ri() self-consistency

| Check | NMO_68174 | NMO_68175 |
|---|---:|---:|
| Internal segment ri() maximum error | 2.274e-11% | 4.552e-11% |
| Child-section start half-edge maximum error | 4.745e-14% | 5.793e-14% |
| Parent endpoint half-edge checks | 204 | 179 |
| Parent endpoint half-edge maximum error | 2.274e-11% | 5.718e-12% |
| Non-root infinite ri() records | 0 | 0 |

The NEURON segment ri() checks reproduce the pt3d integrals to near floating-point precision. Parent-side endpoint validation also passes after distinguishing an ordinary endpoint read from a section's own orientation attachment.

## 4. Topology correction discovered during the audit

The first strict branchpoint gate reported one apparent mismatch at NMO_68175 SWC node 5851: two SWC children but only one child section. Raw mappings show this is not a missing branch:
- SWC child 5852 continues inside NEURON section axon[0].
- SWC child 5944 starts NEURON section axon[1], connected at axon[0] x=0.
- The physical outgoing branch count is therefore one same-section continuation plus one child section: 2/2.

The branchpoint audit now counts both representations rather than assuming every SWC child must become a separate NEURON section.

A related endpoint issue appeared at that same orientation attachment. Calling h.ri(0) on axon[0] returned a value that did not represent the shared first-segment half-edge. The first segment's ri() is the correct half-edge and is independently validated by the segment-ri audit. The parent-endpoint check now uses segment.ri() when the parent connection coincides with the parent section's own orientation, while retaining h.ri(x) for ordinary opposite-endpoint connections. This reduced the apparent 97.66% error to 5.72e-12%.

The first failing run [44902771560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902771560) and raw artifacts [68175](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902771560/artifacts/14706024032) and [68174](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902771560/artifacts/14706383119) are preserved as negative diagnostics. No morphology file or passive parameter was changed to make the test pass.

## 5. Interpretation

The audit establishes that, for these two SWCs and this NEURON Import3D configuration:
- every electrically retained SWC edge maps to pt3d geometry;
- all SWC branchpoints are represented by the correct number of outgoing NEURON branches when same-section continuations are counted correctly;
- all NEURON segment ri() values and ordinary section-connection half-resistances reproduce their local pt3d integrals;
- ordinary non-soma section endpoints are geometrically coincident to the reported precision.

It does **not** independently validate the biological correctness of the morphologies: both AMSN and NEURON consume the same SWC. The audit is also not yet a full effective conductance-matrix or passive voltage-operator comparison for the Segev cells. Soma wire offsets up to 20.22 µm are Import3D conventions and must not be interpreted as anatomical zero-resistance stems.

## 6. Reproducibility artifacts

Final Segev workflow [44903025679](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025679), 2/2 jobs passed:
- NMO_68174 / cell1125: [artifact 14706363670](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025679/artifacts/14706363670).
- NMO_68175 / cell1204: [artifact 14706378618](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025679/artifacts/14706378618).

The original default-morphology full-tree audit passed after the shared script refactor [44903025675](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025675), and its axial-matrix regression passed [44903025666](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903025666).

Raw files per Segev cell include the full edge table, all segment ri() rows, branchpoint table and section-connection table. Summary metrics: [CSV](../results/human_segev_full_tree_axial_audit_summary_2026-11-21.csv).

## 7. Next step

Run the full-tree axial conductance-matrix and passive voltage-operator comparison on both Segev morphologies. That will test whether the near-identical local edge resistances also produce a matching global axial operator. After that, add leak and capacitance before any active-channel or synapse model expansion. Do not tune Ri/Rm/Cm/Eleak to absorb topology or readout errors.
