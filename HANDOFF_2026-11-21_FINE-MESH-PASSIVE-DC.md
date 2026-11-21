# Handoff — AMSN fine-mesh full-tree passive DC audit

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** 9a9890cf3411fcb07b06b235dd38f697de05b9b2  
**Dedicated workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889  
**Raw CSV artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889/artifacts/14694533497  
**Report:** amsn-core/research/HUMAN_FINE_MESH_PASSIVE_DC_AUDIT_2026-11-21.md  
**Research log:** research/RESEARCH_LOG_2026-11-21_FINE-MESH-PASSIVE-DC.md

## Start here

1. Read AGENTS.md, HANDOFF.md and this checkpoint.
2. Recheck the current main head and most recent CI before changing anything.
3. Read HANDOFF_2026-11-21_FULL-TREE-AXIAL-MATRIX.md for the preceding axial operator result.
4. Do not adjust passive parameters or source kinetics to improve cross-simulator agreement.

## What was added

- amsn-core/examples/human_fine_mesh_passive_dc_audit.py — 0.5 µm NEURON reference passive test, nearest-centre vs exact-SWC interpolation.
- .github/workflows/amsn-fine-mesh-passive-dc-audit.yml — NEURON 9.0.2 CI, raw output artifact.
- amsn-core/results/human_fine_mesh_passive_dc_2026-11-21.csv — 15 raw source–probe rows.
- amsn-core/research/HUMAN_FINE_MESH_PASSIVE_DC_AUDIT_2026-11-21.md — methods, comparison and limitations.

## Verified results

Dedicated workflow 44873368889 succeeded (1/1 job), using Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

- NEURON: 125 sections, 25,233 segments, 0.5 µm max segment length.
- AMSN: 8,893 full-tree compartments and 690 sectioned compartments.
- Total normalized area difference: −8.42632×10⁻⁷%.
- Source input-response differences vs full AMSN: soma 0.00006294%, basal q75 0.0432388%, apical q75 0.0679201%.
- Across 15 pairs, nearest-centre ratio errors: median 0.0461416%, p95 0.1018818%, max 0.1075660%.
- Interpolated-to-SWC ratio errors: median 0.0462721%, p95 0.0930256%, max 0.0930533%.
- Max steady residual between 200 and 250 ms: 8.99348×10⁻¹⁰ mV.
- Max nearest-centre offset at a probe: 0.242787 µm.

The same protocol at 5 µm NEURON resolution (prior Core CI 44872853668) had max transfer-ratio error 0.659658% and basal/apical source input differences around 0.41–0.42%. The 0.5 µm mesh reduces these numerical discrepancies, but this is not biological validation.

## Interpretation

Total normalized membrane area is effectively identical in this test. Probe interpolation improves the global max/p95 modestly, but does not help every source–probe pair.

The source clamp is still placed at the nearest NEURON segment centre, while AMSN injects at the exact electrical SWC node. The nearest-centre offsets at the dendritic sources are 0.07965 µm (basal q75) and 0.20686 µm (apical q75). This leaves a source-placement contribution which has not yet been isolated.

## Next work — ordered

1. Repeat the same passive DC protocol at 0.25 µm and 0.125 µm NEURON max segment lengths with identical Ri/Rm/Cm, dt and source/probe identities. Report convergence of input and transfer resistances.
2. Keep source placement and probe interpolation as independent factors; test a locally refined source section or a mechanism that positions current at the exact imported arc if supported.
3. After the passive baseline is stable, reproduce the official Eyal 2018 / ModelDB 238347 archive with verified provenance and mechanism licenses.
4. Only then progress to calibrated NMDA Mg²⁺ block, calcium microdomains and plasticity.

## Integrity

- This is passive cross-simulator numerical validation for one partial morphology.
- The comparison excludes biological parameter fit and experimental traces.
- Interpolation affects probe readout only; it does not move IClamp.
- The 8 soma-centre wire attachments remain an explicit morphology import policy; do not interpret them as zero physical resistance.
