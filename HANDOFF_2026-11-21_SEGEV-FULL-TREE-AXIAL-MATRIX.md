# Handoff — Segev full-tree axial conductance matrix

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** reduce NEURON 9.0.2's full Import3D axial network onto the same electrical SWC vertices as AMSN and compare the sparse axial Laplacians  
**Status:** implementation committed; Segev matrix workflow pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL.md.
3. amsn-core/research/HUMAN_SEGEV_FULL_TREE_AXIAL_AUDIT_2026-11-21.md.
4. The original single-cell matrix audit reference: amsn-core/examples/human_full_tree_axial_matrix_audit.py and amsn-core/research/HUMAN_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md.

## Research question

Do the near-identical local SWC/Import3D axial geometry integrals also produce a matching global axial conductance operator after NEURON's section graph, segment ri() values, endpoint caps and soma normalization are reduced to AMSN's electrical SWC vertices?

A local edge audit is necessary but not sufficient: the full sparse Laplacian also depends on whether each reduced edge is attached to the correct electrical vertex and whether half-resistances at section boundaries are counted exactly once.

## Implementation

- The original axial matrix audit is now morphology-configurable through AMSN_MORPHOLOGY_PATH, AMSN_MORPHOLOGY_LABEL and AMSN_NEURON_MAX_SEGMENT_UM.
- It reuses the corrected full-tree network audit for SWC-to-Import3D mapping.
- It constructs the full unresampled AMSN CableTree using its production soma/wire electrical-node mapping.
- It reduces each Import3D SWC edge by summing actual NEURON segment ri() centre-to-centre values and direct pt3d partial caps.
- It compares every edge conductance and applies both tree Laplacians to 32 deterministic random voltage vectors with seed 20261121. No dense N×N matrix is materialized.
- It checks total-current conservation and the constant-voltage axial nullspace.
- The parent endpoint cap distinguishes ordinary far-end readout from the section's own orientation attachment. If the endpoint is the parent section's own orientation, use the actual last segment ri() half-edge rather than h.ri(1) through the shared parent topology.

## Matrix

Two Segev cells:
- NMO_68174 / cell1125: 12,410 SWC records.
- NMO_68175 / cell1204: 13,758 SWC records.

NEURON 9.0.2, axial resistivity 0.7 Ω·m, maximum segment length 0.5 µm. Each job runs the full 81-test AMSN suite.

## Validation gate

For each cell:
1. Every active SWC edge maps to exactly one Import3D edge; no unmapped/duplicate electrical edges.
2. AMSN and NEURON reduced graphs have identical electrical vertices and edge topology.
3. NEURON ri-network reduction agrees with direct pt3d taper integral within 1e-7%.
4. All edge conductances are compared.
5. Thirty-two deterministic voltage vectors are applied to both sparse axial Laplacians.
6. Both operators conserve total axial current and annihilate a constant potential.
7. Raw edge matrix CSV, operator probe CSV and job log are uploaded.

## Interpretation limits

This is an axial-only geometry/operator comparison. It does not include membrane leak, capacitance, synapses, active channels, or biological parameter fitting. Both models consume the same SWC; agreement is not independent biological validation. Soma wire attachments are an Import3D representation convention, not evidence that biological soma-stem resistance is zero.

## Next step

After both matrices pass, compare edge-wise conductance and whole-operator error against the 0.0625 µm AC residual localization. Then implement a full-tree passive voltage operator including leak and capacitance, with both simulators using the same electrical node set and explicit control-volume area support. Do not tune passive constants to absorb discretization effects.
