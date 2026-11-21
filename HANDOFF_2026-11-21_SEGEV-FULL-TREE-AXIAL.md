# Handoff — Segev full-tree axial geometry and topology audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** whole-tree SWC/NEURON Import3D edge mapping, segment ri(), branchpoints and section connections  
**Status:** implementation committed; two-morphology CI pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md.
3. HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md.
4. The original single-morphology report: amsn-core/research/HUMAN_FULL_TREE_AXIAL_NETWORK_AUDIT_2026-11-21.md.

## Why this audit

The AC probe-coordinate mesh sweep is now complete. At 0.0625 µm, the exact-SWC cross-simulator maximum transfer-complex errors remain approximately 0.1340% for NMO_68174 and 0.0995% for NMO_68175. Complex interpolation is not a universally better readout. The next controlled variable is the electrical geometry/topology representation itself.

The existing whole-tree audit was written for NMO_290988 and already checks:
- every electrically retained SWC edge against an adjacent NEURON Import3D pt3d interval;
- every NEURON segment ri() against the corresponding pt3d half/full interval;
- section connections, branchpoint child counts and soma wire-attachment conventions.

This extension makes the audit morphology-configurable and runs the exact same checks on both Segev L2/3 cells. It also makes branchpoint child-count preservation and non-soma section endpoint coincidence CI-failing invariants rather than report-only metrics.

## Experimental design

- Morphologies: NMO_68174 / cell1125 and NMO_68175 / cell1204.
- NEURON reference: pinned 9.0.2.
- NEURON max segment length: 0.5 µm, matching the original full-tree axial network reference audit.
- Axial resistivity: 0.7 Ω·m (70 Ω·cm).
- Full SWC active edge mapping, every segment ri() row, every branchpoint and every section connection are checked.
- Preserve original CNG files and all soma normalization semantics; do not change source morphology or passive constants.

## Validation gates

For each morphology:
1. Complete AMSN test suite passes.
2. Every active SWC edge maps to exactly one adjacent Import3D pt3d interval; zero unmapped edges.
3. No non-root NEURON segment reports infinite ri().
4. NEURON internal, child-start and parent-end ri() reproduce their respective pt3d axial integral within 1e-6% relative.
5. Every SWC non-soma branchpoint has the exact NEURON child-section count.
6. Every non-soma section-connection endpoint gap is at most 0.001 µm.
7. Raw edge, ri, branchpoint and section-connection CSVs are uploaded.

Soma-centre wire attachments are reported separately. A zero-resistance import link is a representation convention and must not be interpreted as proof that biological soma-stem resistance is zero.

## Interpretation guardrails

- This is a whole-tree geometry/topology and NEURON self-consistency audit, not a voltage waveform comparison.
- A successful SWC-to-Import3D geometry match is not independent biological validation; both representations originate from the same SWC.
- Do not tune Ri/Rm/Cm/Eleak.
- Do not assume the eight or nine soma wire attachments have biologically zero resistance.
- Any mapping or topology failure must be preserved with raw CSV/log and investigated before proceeding.

## Next step

After both Segev jobs pass, compare the full-tree results with the 0.0625 µm AC residual localization. If edge-level geometry and topology pass, implement a separate whole-tree axial conductance matrix comparison for the Segev cells, then a full-tree passive voltage-operator comparison including leak and capacitance.
