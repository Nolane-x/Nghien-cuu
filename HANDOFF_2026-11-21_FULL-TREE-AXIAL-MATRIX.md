# Handoff — AMSN full-tree axial conductance matrix

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** 88747f0c45cb75405a1a2b612161fe93470ffa94  
**Dedicated workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672  
**Raw artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672/artifacts/14694905509  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853668  
**Report:** amsn-core/research/HUMAN_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md  
**Compact summary:** amsn-core/results/human_full_tree_axial_matrix_summary_2026-11-21.csv  
**Research log:** research/RESEARCH_LOG_2026-11-21_FULL-TREE-AXIAL-MATRIX.md

## Start here

1. Read AGENTS.md, HANDOFF.md and this checkpoint.
2. Recheck the live main head and newest CI; documentation commits may be newer than the validated code snapshot.
3. Read HANDOFF_2026-11-21_FULL-TREE-AXIAL-NETWORK.md for full-tree edge and branchpoint coverage.
4. Do not change production Ri/Rm/Cm or solver semantics to improve an unexplained residual.

## What was added

- amsn-core/examples/human_full_tree_axial_matrix_audit.py: edge-by-edge conductance comparison and matrix-vector operator test.
- .github/workflows/amsn-full-tree-axial-matrix-audit.yml: pinned NEURON 9.0.2 CI and raw artifact retention.
- amsn-core/results/human_full_tree_axial_matrix_summary_2026-11-21.csv: compact durable result table.
- Full edge-level CSV and 32 probe rows are stored in workflow artifact 14694905509.

## Verified results

Dedicated workflow 44872853672 succeeded (1/1 job) on Ubuntu 26.04.1, Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

- Same graph: 8,893 electrical nodes / 8,892 edges.
- NEURON: 125 sections / 25,233 segments, max segment length 0.5 µm.
- Per-edge conductance absolute difference: median 0.000163823%, p95 0.002037106%, p99 0.003617323%, maximum 0.015288401%.
- NEURON actual ri-network reduction vs direct pt3d integral maximum difference: 1.66425e−11%.
- 32 deterministic voltage probes (seed 20261121, 10 mV standard deviation): mean relative operator L2 error 3.530997e−6, p95 5.984034e−6, max 6.674520e−6. Percent equivalents: 0.00035310%, 0.00059840%, 0.00066745%.
- Maximum absolute node-current difference 2.34017e−11 A.
- Maximum total-current conservation residual 2.39552e−21 A; constant-potential nullspace residual 0 A.
- All 32 probes passed the explicit 1e−18 A conservation assertion.

This is an axial-only graph-operator comparison, not the membrane-coupled voltage system and not biological validation.

## Failed attempt retained

Workflow 44872686688 failed at the three-node self-check because its expected vector was wrong. The code was corrected and final dedicated run 44872853672 succeeded. Keep the failure in the evidence chain.

## CI

- Dedicated axial matrix workflow 44872853672: success, 1/1 job.
- Comprehensive Core CI 44872853668 for the same code commit: success, 4/4 jobs; 65 tests passed on Python 3.12 and 65 on Python 3.13; both NEURON cross-validation jobs completed all steps.

## Next work — strict order

1. **Passive voltage impact after matrix audit.** Compare the full 8,893-node AMSN morphology against NEURON with the exact same passive parameters and source/probe sites. Align SWC positions and distinguish segment-centre mapping from geometry error. Report input resistance, transfer resistance, voltage and residuals without refitting parameters.
2. **Published Eyal 2018 / ModelDB 238347 reproduction.** Obtain the official 133MB EyalEtAl2018.zip archive referenced in ModelDB's own readme. Record source SHA/version, file inventory, licenses, SWCs, mechanism provenance and original run instructions before copying or running.
3. A third-party Herrera et al. 2023 repository contains an EyalEtAl2018 folder, but it is not a verified copy of the official ModelDB archive. Its smoke-test script depends on undefined path/output globals and uses a lower-case .asc filename while the mirrored morphology filename is .ASC; its model folder readme points to BBP mechanisms. Treat it only as reconnaissance, not as a reproduction or vendorable source.
4. Only after the original source baseline is reproducible should the project deepen NMDA Mg²⁺ block, calcium microdomains, plasticity, gene/protein and metabolism.

## Integrity

- No solver, passive or synaptic parameters were changed in this matrix audit.
- The 32 voltage vectors are numerical probes, not biological stimuli.
- The NEURON fine-grid series reduction is exact for the axial-only resistor network; it does not reduce membrane shunts/capacitance or prove the full dynamic system equivalent.
- The NMO_290988 morphology is partial, has no axon and has the source metadata limitations documented in provenance.
