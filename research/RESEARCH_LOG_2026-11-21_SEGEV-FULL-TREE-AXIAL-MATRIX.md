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
