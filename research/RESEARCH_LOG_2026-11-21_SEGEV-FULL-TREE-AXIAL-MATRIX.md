# Research log — Segev full-tree axial conductance matrix — 2026-11-21

## Question

Does the complete effective axial conductance matrix agree between AMSN and NEURON 9.0.2 for the two human Segev L2/3 morphologies after both trees are reduced to identical electrical SWC vertices?

## Motivation

The Segev full-tree geometry/topology audit passed for both cells:
- active SWC-edge coverage was 100%;
- branchpoint counts were exact (102/102 and 90/90);
- segment ri() and parent/child half-resistance checks were near floating-point precision;
- ordinary section endpoints had zero geometric gap.

This only establishes local edge and topology consistency. The next check must compare the assembled axial graph operator.

## Method

Use the human_full_tree_axial_matrix_audit.py script, now parameterized by morphology path, label and NEURON segment cap. For each cell:
- Import the SWC with NEURON 9.0.2.
- Convert the unresampled SWC to AMSN's exact node-centred CableTree.
- Map every active SWC edge to one Import3D pt3d interval.
- Reduce NEURON's segment ri() chain and endpoint half-caps to a single equivalent resistance/conductance for each AMSN edge.
- Apply both sparse tree Laplacians to 32 deterministic random voltage vectors (seed 20261121; 10 mV standard deviation).
- Check current conservation and constant-voltage nullspace.

The endpoint orientation correction is carried forward from the full-tree topology audit: if the final endpoint lies at the section's own orientation attachment, the parent-side half-resistance is represented by the last segment ri().

## Verification

Pending workflow amsn-segev-full-tree-axial-matrix-audit.yml. Do not claim matrix agreement until both cells pass and raw artifacts are inspected.

## Limits

Axial-only comparison. No leak, capacitance, synaptic or active conductance terms. Numerical agreement between two representations built from the same SWC is not biological validation.


## Verified results — Segev full-tree axial conductance matrix

Segev matrix workflow [44903533060](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060) passed both cells; original single-morphology matrix regression [44903453372](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453372) passed.

NMO_68174:
- Electrical graph 12,399 vertices / 12,398 edges; 214 NEURON sections / 41,864 segments.
- Edge conductance absolute median/p95/p99/max 0.0001641/0.0017516/0.0044951/0.0932558%.
- NEURON ri-network vs direct pt3d maximum 1.984e-11%.
- 32-vector axial-operator relative L2 mean/p95/max 0.0042137/0.0076496/0.0106860%.
- Max total-current conservation residual 4.606e-21 A; constant voltage nullspace 0 A.

NMO_68175:
- Electrical graph 13,747 vertices / 13,746 edges; 189 NEURON sections / 39,245 segments.
- Edge conductance absolute median/p95/p99/max 0.0001800/0.0019193/0.0051603/0.0359234%.
- NEURON ri-network vs direct pt3d maximum 1.550e-11%.
- 32-vector axial-operator relative L2 mean/p95/max 0.0020482/0.0030657/0.0032929%.
- Max total-current conservation residual 9.503e-21 A; constant voltage nullspace 0 A.

The full report is at [HUMAN_SEGEV_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md](../research/HUMAN_SEGEV_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md). This tests the axial-only graph; leak and capacitance are not included.
