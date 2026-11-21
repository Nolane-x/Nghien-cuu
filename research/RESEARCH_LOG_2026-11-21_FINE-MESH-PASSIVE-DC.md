# Research log — 2026-11-21 — fine-mesh full-tree passive DC audit

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Code commit:** 9a9890cf3411fcb07b06b235dd38f697de05b9b2  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889  
**Artifact:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889/artifacts/14694533497  
**Report:** amsn-core/research/HUMAN_FINE_MESH_PASSIVE_DC_AUDIT_2026-11-21.md

## Question

Does a finer NEURON reference mesh (0.5 µm instead of 5 µm) reduce the passive full-morphology AMSN/NEURON discrepancy, and how much of the remaining difference comes from reading the nearest segment centre rather than the exact SWC probe arc?

## Work completed

1. Added amsn-core/examples/human_fine_mesh_passive_dc_audit.py and its pinned NEURON 9.0.2 workflow.
2. Reused the established NMO_290988 Import3D/passive parameters and increased NEURON resolution to max segment length 0.5 µm (25,233 segments).
3. Compared 3 source sites × 5 probe sites; AMSN fine tree 8,893 nodes and sectioned tree 690 compartments.
4. Recorded NEURON voltage at nearest segment centre and linear interpolation to exact SWC arc; source clamp remained at nearest segment centre.
5. Compared total normalized membrane area and steady-state residual.
6. Saved raw 15-row CSV as workflow artifact and preserved a report.

## Exact environment and command

- Ubuntu 26.04.1, CPython 3.12.16, NumPy 2.5.5, NEURON 9.0.2.
- NEURON: 125 sections / 25,233 segments, max segment length 0.5 µm.
- Ri=0.7 Ω·m, Rm=1 Ω·m², Cm=0.01 F/m², Eleak=−65 mV, IClamp=10 pA.
- dt=0.025 ms; run 200 ms; final readout 250 ms.
- Install: python -m pip install -e ".[test]"
- Install: python -m pip install --only-binary=neuron "neuron==9.0.2"
- Run: python examples/human_fine_mesh_passive_dc_audit.py
- Workflow 44873368889: success, 1/1 job. Artifact 14694533497.

## Results

- NEURON total membrane area 23,338.438806144 µm²; AMSN normalized area 23,338.439002801 µm²; difference −8.42632×10⁻⁷%.
- Source input-response differences: soma 0.00006294%; basal q75 0.0432388%; apical q75 0.0679201%.
- Across 15 source–probe pairs, NEURON nearest-centre transfer-ratio error median/p95/max: 0.0461416% / 0.1018818% / 0.1075660%.
- Interpolating probe voltage to exact SWC arc: median/p95/max 0.0462721% / 0.0930256% / 0.0930533%.
- By source, maximum interpolated error: soma 0.0001647%; basal q75 0.0463064%; apical q75 0.0930533%.
- Existing sectioned AMSN mesh vs full AMSN tree max ratio difference: 0.0492173%.
- Maximum 200–250 ms steady residual: 8.99348×10⁻¹⁰ mV.
- Maximum nearest probe centre offset: 0.242787 µm; selected Import3D geometry offsets below 2.7×10⁻⁵ µm.

## Comparison against the earlier 5 µm reference

The earlier Core CI 44872853668 used max NEURON segment length 5 µm and the same passive parameters/sites. Its maximum full-AMSN ratio error was 0.659658%; basal and apical source input-resistance differences were 0.424589% and 0.408867%. At 0.5 µm these become:
- max nearest-centre ratio error 0.107566%;
- max interpolated ratio error 0.093053%;
- source input differences 0.043239% and 0.067920%.

This is consistent with spatial refinement reducing numerical mismatch; it does not prove biological truth or full convergence.

## Interpretation and limitations

The total normalized membrane area is not a plausible explanation for the residual in this test. Probe interpolation reduces the maximum transfer-ratio error by about 13.5% relative to nearest-centre readout, but does not improve every pair.

The source clamp itself remains at the nearest NEURON segment centre while AMSN current is applied at the exact SWC node. This source-position mismatch is a remaining candidate, especially for apical q75 (nearest centre offset 0.20686 µm). It has not yet been isolated from any remaining model difference.

No experimental trace was fitted; no passive parameters were changed; this is numerical cross-simulator evidence for one partial morphology only.

## Next experiment

Repeat at 0.25 µm and 0.125 µm NEURON max segment lengths with identical passive parameters, and separate source-placement effects from probe-readout interpolation. Do not tune Ri/Rm/Cm to force agreement.
