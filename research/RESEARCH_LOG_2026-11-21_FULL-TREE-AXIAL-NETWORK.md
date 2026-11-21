# Research log — 2026-11-21 — full-tree axial network audit

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** e65a347ef1c51bb44ecbc1deca35c8a4d5712a90  
**Dedicated workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854  
**Artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082  
**Report:** amsn-core/research/HUMAN_FULL_TREE_AXIAL_NETWORK_AUDIT_2026-11-21.md

## Research question

Does the whole NEURON-imported morphology preserve every active SWC axial edge and branchpoint connection, and do NEURON's segment ri() values reproduce its own pt3d axial geometry integrals?

## Hypothesis

Every active SWC edge should map to one unambiguous adjacent NEURON pt3d interval; actual NEURON segment and section half-resistances should agree with independently integrated pt3d geometry; branchpoint child counts and section connections should match the source topology. Soma wire attachments must be explicitly identified rather than silently treated as ordinary edges.

## Sources examined

- Repository instructions: AGENTS.md; HANDOFF_2026-11-21_AMPA-AXIAL-RESISTANCE.md; HANDOFF.md; AMSN_RESEARCH_DOSSIER.md.
- Morphology: NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc and its provenance JSON; CC BY 4.0.
- NEURON 9.0.2 implementation: https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/treeset.cpp (nrn_area_ri, diam_from_list and ri()).
- NEURON geometry documentation: https://www.neuronsimulator.org/en/latest/progref/modelspec/programmatic/topology/geometry.html (pt3d taper representation and float storage precision).

## Code and workflow work completed

1. Added amsn-core/examples/human_full_tree_axial_network_audit.py and the dedicated GitHub Actions workflow.
2. Mapped each active SWC edge through Import3D's point2sec/id2pt mapping to one adjacent NEURON pt3d pair. The mapping rejects unmatched active edges.
3. Audited all NEURON segment ri() values, child-section start half intervals and ordinary parent endpoint half intervals.
4. Counted NEURON child sections at all SWC branchpoints.
5. Separated eight soma-centre wire attachments from ordinary section endpoints. A first audit iteration exposed a classification bug (the three-point CNG soma is not identified by the simple one-point pt3d flag after define_shape); the classification was corrected using the explicit soma[0](0.5) + child orientation 0 convention and the workflow reran successfully.
6. Stored all four raw CSV outputs in the successful workflow artifact.

## Exact run environment and commands

Successful dedicated workflow run 44871993854:
- Ubuntu 26.04.1.
- CPython 3.12.16.
- NumPy 2.5.5.
- NEURON 9.0.2.
- 125 NEURON sections, 25,233 segments, max segment length 0.5 um.
- Ri = 0.7 ohm*m (NEURON Ra = 70 ohm*cm).
- Install: python -m pip install -e ".[test]"
- Reference simulator: python -m pip install --only-binary=neuron "neuron==9.0.2"
- Run: python examples/human_full_tree_axial_network_audit.py
- Dedicated workflow conclusion: success, 1/1 job.
- Artifact ID: 14693349082.

## Results

- SWC: 8,903 nodes, 58 non-soma branchpoints, 8 dendritic stems.
- Active SWC cable edges after ten soma-outline/wire edges are collapsed under the documented import policy: 8,892.
- Active edge mapping: 8,892/8,892 (100%); zero unmapped.
- Maximum SWC-to-NEURON pt3d axial geometry-factor difference: 0.0152884011%.
- Median: 0.0001638230%; p95: 0.0020347563%; p99: 0.0036172499%.
- Basal dendrite edge max: 0.0022279856%; apical edge max: 0.0152884011%.
- Largest difference occurs on a 0.156525 um apical edge; its pt3d endpoint coordinate and diameter offsets are tiny, consistent with NEURON pt3d float32 rounding becoming more visible on a very short edge. The causal attribution is plausible but not proven.
- Actual NEURON ri rows: 25,233, all checked and finite.
- Internal segment-centre ri: 25,108; max error against pt3d integral 2.2788054e-11%.
- Child-section start half ri: 124; max error 7.3003891e-14%.
- Parent endpoint half ri: 116; max error 1.1385008e-11%.
- Branchpoints: 58/58 have exactly the expected NEURON child section count.
- Section connections: 124 total; 116 ordinary endpoint connections have zero endpoint gap; eight soma wire attachments connect to soma[0](0.5), with 7.631–10.537 um offsets to child pt3d origins. They are an explicit import-policy assumption, not proof of zero biological stem resistance.
- Maximum SWC branchpoint to mapped pt3d point gap: 2.93485e-5 um.
- No solver or biological parameters were changed.

## Interpretation and limits

Locally reproduced result: all active SWC edges and all branchpoints were accounted for in this Import3D representation. NEURON's own ri() values agree with pt3d axial integrals at near machine precision for all checked segment and section half-intervals.

The small SWC-vs-pt3d edge difference is concentrated on very short edges and is consistent with NEURON's float32 pt3d coordinates/diameters; it is not evidence of a large solver error. The eight soma wire attachment links are an explicit geometry/topology policy that still needs to be checked against the original CNG and Eyal soma representations.

This audit is not equality of the full AMSN/NEURON voltage solve, not a 3-D branch-junction mesh, and not biological validation. One partial morphology with no axon was used.

## Files created

- amsn-core/examples/human_full_tree_axial_network_audit.py
- .github/workflows/amsn-full-tree-axial-network-audit.yml
- amsn-core/research/HUMAN_FULL_TREE_AXIAL_NETWORK_AUDIT_2026-11-21.md
- amsn-core/results/human_full_tree_axial_summary_2026-11-21.csv
- HANDOFF_2026-11-21_FULL-TREE-AXIAL-NETWORK.md
- research/RESEARCH_LOG_2026-11-21_FULL-TREE-AXIAL-NETWORK.md
- README.md checkpoint update

## Next experiment

1. Independently compare the entire AMSN axial edge/conductance matrix against the NEURON connection network, with separate treatment for the eight soma-wire attachment links and for branchpoint parent junctions.
2. Run a matched passive DC/steady-state multi-source comparison using unchanged membrane parameters and a node mapping that preserves the soma/branch semantics. Record source/probe transfer resistance and map any residual to the corresponding edge/connection class.
3. Reproduce the original Eyal et al. 2018 / ModelDB 238347 source archive using its own morphologies and mechanisms. The ModelDB GitHub mirror only documents a separate 133MB EyalEtAl2018.zip download; verify archive contents and license before importing or redistributing.


## Comprehensive Core CI completion

Workflow [44871993797](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993797) completed successfully on code commit `e65a347ef1c51bb44ecbc1deca35c8a4d5712a90`: all 4/4 jobs succeeded. The unit/numerical test matrix passed 65 tests on Python 3.12 and 65 on Python 3.13. Both test jobs compiled all Python modules and ran examples; both NEURON 9.0.2 cross-validation jobs completed passive, temporal/spatial, transient, AMPA, Exp2Syn timing and matched single-compartment checks.
