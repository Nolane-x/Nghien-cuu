# Research log — 2026-11-21 — full-tree axial conductance matrix comparison

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** 88747f0c45cb75405a1a2b612161fe93470ffa94  
**Dedicated workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672  
**Artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672/artifacts/14694905509  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853668  
**Report:** amsn-core/research/HUMAN_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md

## Research question and hypothesis

After expressing AMSN and NEURON on the same 8,893 electrical SWC vertices, do their complete axial-only graph Laplacians agree?

Hypothesis: if the two cable models represent the same tapered SWC edge geometry, then after eliminating NEURON's fine segment-centre nodes along each original SWC edge, the resulting edge conductances and axial Laplacian should closely match AMSN.

This is axial-only. It excludes leak, capacitance, active channels, synapses and time integration; it is not a full passive voltage or biological validation.

## Sources examined

- Repository instructions, latest full-tree handoff and prior axial network report.
- NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc; CC BY 4.0.
- NEURON 9.0.2 source: https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/treeset.cpp.
- NEURON geometry reference: https://www.neuronsimulator.org/en/latest/progref/modelspec/programmatic/topology/geometry.html.

## Work completed

1. Added amsn-core/examples/human_full_tree_axial_matrix_audit.py.
2. Added .github/workflows/amsn-full-tree-axial-matrix-audit.yml.
3. Built the exact unresampled AMSN CableTree: 8,893 nodes and 8,892 edges, using the existing electrical soma mapping.
4. For every edge, matched one Import3D pt3d interval, summed actual NEURON centre-to-centre ri() values and section half-resistances, and integrated partial pt3d endpoint caps.
5. Built identical sparse edge-list Laplacian operators for both simulators and applied them to 32 deterministic voltage vectors.
6. Added the three-node sign/conservation self-check, constant-potential nullspace check and hard total-current conservation assertion.
7. Preserved the first failed self-check attempt in Actions history; corrected its expected vector and reran successfully.

## Environment and command

Successful dedicated workflow 44872853672:
- Ubuntu 26.04.1, CPython 3.12.16, NumPy 2.5.5, NEURON 9.0.2.
- 125 NEURON sections / 25,233 segments; maximum segment length 0.5 µm.
- Axial resistivity 0.7 Ω·m.
- 32 voltage probes, seed 20261121, 10 mV standard deviation and −65 mV mean.
- Install: python -m pip install -e ".[test]"
- Install reference: python -m pip install --only-binary=neuron "neuron==9.0.2"
- Run: python examples/human_full_tree_axial_matrix_audit.py
- Workflow: 1/1 job successful; artifact 14694905509.

## Results

- Graph: 8,893 nodes / 8,892 edges.
- Edge conductance absolute difference: median 0.000163823%, p95 0.0020371056%, p99 0.0036173229%, maximum 0.0152884011%.
- Signed mean conductance difference: −1.3603464e−6%; signed median −1.6526393e−6%.
- NEURON reductions used 16,332 centre-to-centre ri pairs, 117 child-start half-resistances, 118 parent-end half-resistances and 17,523 direct partial pt3d caps.
- Maximum NEURON ri-network vs direct pt3d factor difference: 1.6642525e−11%.
- Across 32 probes: mean relative operator L2 error 3.5309972e−6; p95 5.9840343e−6; maximum 6.6745196e−6 (0.00035310%, 0.00059840%, 0.00066745%).
- Maximum absolute node-current difference 2.3401741e−11 A.
- Maximum total-current conservation residual 2.3955151e−21 A; constant-potential nullspace residual 0 A.
- All 32 probes passed the 1e−18 A conservation gate.

## Interpretation and limitations

This locally reproduced result shows close agreement of the two axial-only graph operators on the same electrical SWC vertices. The individual edge maximum is concentrated on one very short apical edge; it does not dominate the full-tree operator norm for the tested vectors.

The result does not show equivalent membrane-coupled voltage dynamics. Leak, capacitance and active/synaptic currents are excluded. It is not biological validation. No Ri/Rm/Cm or synaptic parameters were tuned.

## Failed attempt retained

The first run 44872686688 stopped at a three-node self-check because the expected current vector was wrong; the computed vector was the correct sum of edge currents. The expected vector was corrected before successful run 44872853672.

## Comprehensive Core CI completion

Workflow 44872853668 completed successfully on the same code commit: all 4/4 jobs succeeded. Unit/numerical tests passed 65 on Python 3.12 and 65 on Python 3.13. Both test jobs compiled all Python modules and ran examples; both NEURON 9.0.2 cross-validation jobs completed all steps.

## Files created

- .github/workflows/amsn-full-tree-axial-matrix-audit.yml
- amsn-core/examples/human_full_tree_axial_matrix_audit.py
- amsn-core/results/human_full_tree_axial_matrix_summary_2026-11-21.csv
- amsn-core/research/HUMAN_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md
- research/RESEARCH_LOG_2026-11-21_FULL-TREE-AXIAL-MATRIX.md
- HANDOFF_2026-11-21_FULL-TREE-AXIAL-MATRIX.md
- README.md checkpoint/index update

## Next experiment

Run a matched full-tree passive voltage impact comparison using the same morphology, passive parameters and source/probe mapping. Separate any residual into axial-network vs membrane-area/leak mapping terms. In parallel, acquire and provenance-check the official Eyal et al. 2018 / ModelDB 238347 archive before claiming a source-matched model reproduction. Do not use the incomplete third-party mirror as if it were the official archive.
