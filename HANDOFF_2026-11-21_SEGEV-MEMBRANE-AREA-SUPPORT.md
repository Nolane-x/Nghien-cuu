# Handoff — Segev membrane area on matched control-volume support

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** assign actual NEURON segment membrane area onto the same electrical SWC endpoint control volumes used by AMSN CableTree  
**Status:** implementation committed; workflow pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL.md.
3. HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md.
4. amsn-core/research/HUMAN_SEGEV_FULL_TREE_AXIAL_AUDIT_2026-11-21.md.
5. This handoff and research/RESEARCH_LOG_2026-11-21_SEGEV-MEMBRANE-AREA-SUPPORT.md.

## Research question

Does NEURON's actual segment membrane area, when partitioned onto the exact same electrical SWC node support as AMSN, reproduce AMSN's per-node membrane area distribution?

AMSN's node-centred CableTree does not assign a whole SWC frustum to one node. It splits each tapered frustum at its geometric midpoint and assigns the proximal half to the parent control volume and distal half to the child control volume. Summed total area equality is not sufficient: a membrane passive operator depends on the area attached to each electrical voltage unknown.

## Method

- Import each Segev morphology with NEURON 9.0.2 at 0.125 µm maximum segment length.
- Read actual segment.area() values.
- Match all electrically retained SWC edges to Import3D pt3d intervals using the full-tree mapping helper.
- Split each SWC edge at its tapered-frustum midpoint.
- For each segment, calculate the pt3d geometric surface area on its full interval and the overlap with each SWC half-edge.
- Allocate the measured segment.area() proportionally to the pt3d surface area in each overlap.
- Accumulate actual NEURON segment area onto the electrical parent/child SWC nodes.
- Compare every node's NEURON support area with AMSN CableTree.area_m2.
- Treat soma sections separately: their measured area is assigned to the root soma electrical control volume, while collapsed soma-wire edges contribute no cable membrane area.

The allocation is exact with respect to each measured segment total and the pt3d surface-area partition used for its subsegment overlap. The fractionally allocated support is still a numerical control-volume mapping; it is not a direct readout of a continuous membrane density field.

## Validation gates

- All active SWC edges map; no duplicated electrical edge.
- Every non-soma NEURON segment's measured area is fully covered by mapped SWC half-edge intervals.
- Per-segment area-support partition closure and per-section allocated segment area closure are both within 1e-6%.
- Every AMSN electrical node receives a NEURON area support value.
- Raw node, edge-half and section-coverage CSVs are uploaded.

## Interpretation rules

- Compare per-node and per-edge-half area errors, not just total area.
- Identify whether high residuals cluster at soma attachments, branchpoints, terminals or short edges.
- Do not change specific membrane resistance or capacitance to compensate for an area-support mismatch.
- This stage validates only area mapping. It is not a full passive operator comparison and not biological validation.

## Next step

If per-node area support is sufficiently close, build a matched-support passive admittance operator by adding leak and capacitance to the already-validated axial graph. If area differences remain localized, investigate the mapping and preserve both raw area distributions before proceeding.
