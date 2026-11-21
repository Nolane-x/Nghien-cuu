# AMSN fine-mesh full-tree passive DC cross-validation

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Code commit:** 9a9890cf3411fcb07b06b235dd38f697de05b9b2  
**Dedicated workflow:** [44873368889 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889)  
**Raw 15-row CSV artifact:** [passive DC output](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889/artifacts/14694533497)  
**Script:** amsn-core/examples/human_fine_mesh_passive_dc_audit.py

## 1. Question

The pre-existing whole-morphology passive DC validation used a 5 µm NEURON maximum segment length, while AMSN's full reference tree retained 8,893 electrical nodes. This experiment repeats the same passive comparison with a much finer 0.5 µm NEURON reference mesh and adds voltage interpolation at the exact SWC probe arc.

It separates:
- source placement: NEURON current clamp remains on the nearest segment centre, whereas AMSN injects at the exact SWC electrical node;
- probe readout: NEURON voltage at the nearest segment centre versus linear interpolation to the exact SWC arc;
- mesh model: full unresampled AMSN versus its existing 690-compartment electrotonic mesh.

Interpolation changes readout only. It does not move the NEURON IClamp or alter the cable model.

## 2. Common morphology and passive parameters

- NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc.
- 8,903 SWC records; the electrically normalized tree has 8,893 compartments.
- NEURON 9.0.2, 125 sections, 25,233 segments, maximum segment length 0.5 µm.
- AMSN full tree: 8,893 compartments; sectioned comparison mesh: 690 compartments.
- Axial resistivity \(R_i=0.7\;\Omega\,m\).
- Specific membrane resistance \(R_m=1.0\;\Omega\,m^2\).
- Specific capacitance \(C_m=0.01\;F/m^2\).
- Leak reversal −65 mV.
- One DC current clamp of 10 pA per source site.
- Fixed timestep 0.025 ms; transient run to 200 ms, final readout at 250 ms.

No parameters were fitted or changed. The source clamp remains active for 500 ms, so it is on throughout the 250 ms run.

## 3. Protocol and measurement sites

Source sites:
- Soma, SWC 1.
- Basal q75, SWC 3784.
- Apical q75, SWC 5920.

Probe sites:
- Soma, SWC 1.
- Basal q50, SWC 3355.
- Basal q90, SWC 3814.
- Apical q50, SWC 6897.
- Apical q90, SWC 5164.

Each source is compared against all five probes, yielding 15 source–probe pairs. For each probe, the script records NEURON's nearest segment-centre voltage and a linear interpolation between the adjacent segment centres at the exact SWC arc. AMSN fine and sectioned results are read at their protected SWC electrical nodes.

## 4. Membrane-area check

| Quantity | Area |
|---|---:|
| NEURON total segment area | 23,338.438806144 µm² |
| AMSN normalized electrical area | 23,338.439002801 µm² |
| Relative difference | −8.42632 × 10⁻⁷ % |

This confirms that the total normalized passive membrane area is not a meaningful source of the remaining sub-0.1% transfer-ratio residual in this experiment. It does not prove every local area assignment or soma-stem representation is physically correct.

## 5. Source input response

The relative difference below compares NEURON's source-segment deflection with the full AMSN electrical node at the exact SWC location.

| Source | NEURON source deflection | AMSN fine deflection | Relative difference |
|---|---:|---:|---:|
| Soma | 0.539311631 mV | 0.539311971 mV | 0.00006294% |
| Basal q75 | 4.595403320 mV | 4.597391175 mV | 0.0432388% |
| Apical q75 | 4.985497600 mV | 4.988886057 mV | 0.0679201% |

The two dendritic source clamps are placed at the nearest NEURON segment centres, not exactly at their source SWC arc. Their nearest-centre offsets are 0.07965 µm at basal q75 and 0.20686 µm at apical q75. This source-location discrepancy remains even when probe readout is interpolated.

## 6. Transfer-ratio comparison across 15 source–probe pairs

Relative errors are computed against the full AMSN electrical tree. The nearest and interpolated columns are both NEURON; interpolation is readout-only.

| Metric | NEURON nearest centre | NEURON interpolated to SWC arc |
|---|---:|---:|
| Median absolute relative error | 0.0461416% | 0.0462721% |
| 95th percentile | 0.1018818% | 0.0930256% |
| Maximum | 0.1075660% | 0.0930533% |

Interpolation reduces the maximum from 0.107566% to 0.093053% and the p95 from 0.101882% to 0.093026%, but does not improve every pair. For soma-source probes, it reduces the maximum error from 0.014638% to 0.000165%. For the basal and apical dendritic sources, a residual remains because the source current is applied at a nearest segment centre.

### Maximum error by source

| Source | NEURON nearest | NEURON interpolated |
|---|---:|---:|
| Soma | 0.0146377% | 0.0001647% |
| Basal q75 | 0.0607860% | 0.0463064% |
| Apical q75 | 0.1075660% | 0.0930533% |

The existing 690-compartment sectioned AMSN mesh has a maximum transfer-ratio difference of 0.0492173% against the full AMSN tree for these same pairs. That value is not a NEURON-vs-AMSN error; it measures the additional effect of AMSN's own sectioned discretization.

## 7. Comparison with the previous 5 µm reference

The previous comprehensive Core CI run [44872853668](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853668) included the same full-tree passive protocol with NEURON max segment length 5 µm. On that coarser mesh:
- maximum NEURON-vs-full-AMSN transfer-ratio error was 0.659658%;
- basal q75 and apical q75 source input-resistance differences were 0.424589% and 0.408867%.

With the 0.5 µm mesh:
- maximum nearest-centre transfer-ratio error is 0.107566% (about 6.1× lower);
- maximum interpolated-readout transfer-ratio error is 0.093053% (about 7.1× lower);
- basal and apical source input-response differences fall to 0.043239% and 0.067920%.

This is consistent with better spatial resolution reducing the numerical cross-simulator discrepancy. It is not proof that the result has converged to biological ground truth.

## 8. Steady-state and mapping checks

- Maximum change between 200 ms and 250 ms across all probe readouts: \(8.99348\times10^{-10}\) mV.
- Maximum nearest segment-centre probe offset: 0.242787 µm.
- Import3D geometric node-mapping offsets remain below 2.7×10⁻⁵ µm at the selected sites.
- All 15 source–probe rows were generated successfully.
- Total NEURON / AMSN normalized membrane area difference remains below 10⁻⁶ percent.

## 9. Interpretation and limitations

**Locally reproduced result:** with the 0.5 µm NEURON reference mesh and the unchanged passive parameters, the full AMSN tree and NEURON passive input/transfer responses agree within approximately 0.1% on the selected source–probe pairs after probe interpolation.

The remaining discrepancy is not attributable to total membrane area, which agrees to roughly \(8.4\times10^{-7}\%\). A remaining candidate is source placement: IClamp is located at the nearest NEURON segment centre while AMSN applies current at the exact SWC electrical node. The apical q75 source has the largest such offset (0.2069 µm). The current experiment narrows but does not fully isolate this source-placement contribution from any remaining implementation differences.

No experimental trace was fitted. The reconstruction is partial, has no axon, and carries the source metadata limitations recorded in provenance. This is numerical cross-simulator validation, not biological validation.

## 10. Reproducibility

- Code: amsn-core/examples/human_fine_mesh_passive_dc_audit.py.
- Workflow: .github/workflows/amsn-fine-mesh-passive-dc-audit.yml.
- Code commit: 9a9890cf3411fcb07b06b235dd38f697de05b9b2.
- Successful workflow: [44873368889](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889), 1/1 job.
- Artifact: [14694533497](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889/artifacts/14694533497).
- Raw output: amsn-core/results/human_fine_mesh_passive_dc_2026-11-21.csv.
- Comprehensive Core CI for the same code commit: [44873368723](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368723); at report creation its two unit-test jobs had passed (65 each), while both NEURON cross-validation jobs were still running.

## 11. Next experiment

Test source-placement sensitivity without changing biological parameters:
1. Repeat the passive DC comparison with NEURON max segment lengths 0.25 µm and 0.125 µm, holding dt and all passive parameters constant.
2. Report whether dendritic source input-resistance and transfer-ratio errors converge monotonically.
3. Where supported, compare an exact SWC-arc point process against the current nearest-segment placement, or build a local refinement around the source point, and quantify the difference.
4. Keep probe interpolation and source placement as separate factors.
