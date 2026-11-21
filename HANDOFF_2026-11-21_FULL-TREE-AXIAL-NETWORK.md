# Handoff — AMSN full-tree axial network audit

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** e65a347ef1c51bb44ecbc1deca35c8a4d5712a90  
**Successful full-tree audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854  
**Artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082  
**Research report:** amsn-core/research/HUMAN_FULL_TREE_AXIAL_NETWORK_AUDIT_2026-11-21.md  
**Research log:** research/RESEARCH_LOG_2026-11-21_FULL-TREE-AXIAL-NETWORK.md

## Start here for the next session

1. Read AGENTS.md and HANDOFF.md for repository-wide goals and preservation rules.
2. Read this handoff and the full-tree audit report linked above.
3. Re-read HANDOFF_2026-11-21_AMPA-AXIAL-RESISTANCE.md for the preceding local support audit.
4. Verify the current main head and CI state before changing anything; never assume this checkpoint is still the tip.
5. Do not change Ri, membrane parameters or solver semantics merely to improve a residual.

## What is implemented

- Full-morphology edge mapper from SWC nodes to adjacent NEURON Import3D pt3d points.
- Whole-tree axial geometry-factor comparison.
- Whole-NEURON segment-centre ri() self-consistency check.
- Parent-endpoint and child-section-start half-resistance checks.
- Branchpoint child-section count comparison.
- Explicit soma wire-attachment classification.
- Four CSV outputs in the workflow artifact.

Files:
- `amsn-core/examples/human_full_tree_axial_network_audit.py`
- `.github/workflows/amsn-full-tree-axial-network-audit.yml`

## Verified results

The dedicated workflow [44871993854](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854) completed successfully on Ubuntu 26.04.1, CPython 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

- 125 NEURON sections; 25,233 segments, max segment length 0.5 um.
- 8,903 SWC nodes; 58 branchpoints.
- 8,892 active SWC edges mapped to 8,892/8,892 NEURON pt3d edge intervals; zero unmapped.
- Maximum SWC-to-pt3d axial factor difference 0.0152884%; median 0.000163823%; p99 0.00361725%.
- 25,233 NEURON ri() rows checked; 25,108 internal connections, 124 child-start half intervals, 116 parent-endpoint half intervals; all errors at or below approximately 2.28e-11% in the respective comparisons.
- 58/58 SWC branchpoints have the expected number of NEURON child sections.
- 124 section connections: 116 normal endpoint connections have zero endpoint gap; 8 soma wire attachments connect to soma[0](0.5) and have 7.631–10.537 um child pt3d-origin offsets.
- All eight soma wire links are intentionally separated from ordinary endpoint junctions in the report. They are a representation assumption, not an assertion of zero biological stem resistance.

This is geometry/topology/numerics evidence for one partial morphology and NEURON 9.0.2. It is not biological validation, not a complete 3-D branch-junction model and not yet an all-entry AMSN-vs-NEURON global voltage-solve equivalence proof.

## CI

- Dedicated audit: [44871993854](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854), success, 1/1 job.
- Comprehensive Core CI for code commit `e65a347ef1c51bb44ecbc1deca35c8a4d5712a90`: [44871993797](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993797), success (4/4 jobs); 65 tests passed on Python 3.12 and 65 on Python 3.13; both NEURON 9.0.2 cross-validation jobs completed all steps.

## Next work — ordered

1. **Full AMSN-to-NEURON axial matrix comparison.** Compare every effective AMSN cable edge against the corresponding NEURON parent-child resistance/conductance. Include ordinary junctions and an explicit, separate case for the eight soma wire attachments. Report every unmatched edge.
2. **Passive voltage impact.** Use the same passive parameters and matched source/probe locations to compare transfer/input resistance after the matrix audit. Do not refit any parameter.
3. **Original Eyal 2018 reproduction.** ModelDB 238347 is the right biological reference direction. Its GitHub mirror contains a readme and documents a separate 133MB `EyalEtAl2018.zip` archive. Inspect the archive's contents, source version, licenses, original SWCs and run scripts before importing or redistributing it. Keep Eyal's cell morphologies/mechanisms distinct from NMO_290988.
4. Only after that source-matched electrical baseline is reproducible should the project expand NMDA Mg²⁺ block, calcium, plasticity, gene/protein or metabolism.

## Data retention

The four raw CSVs are in workflow artifact [14693349082](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082). The audit script can recreate them at any time using the pinned environment. A compact full-tree summary CSV is committed separately for long-term quick inspection.
