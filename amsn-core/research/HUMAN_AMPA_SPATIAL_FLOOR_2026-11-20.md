# Fast-AMPA spatial-floor sweep at finest timestep — 2026-11-20

**Status:** completed, reproducible spatial sensitivity sweep; no universal mesh default selected.  
**NEURON:** 9.0.2  
**Python:** 3.12 GitHub Actions runner  
**Workflow:** [44761379734 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734)  
**Code snapshot:** `6a04ef9c41f0909200aa02a7b827389311d6c432`  
**Script:** `amsn-core/examples/human_ampa_spatial_floor_sweep.py`  
**Artifact:** [14640889259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734/artifacts/14640889259)

## Research question

The preceding temporal-convergence study reduced dt to 0.0015625 ms and found a nearly timestep-independent q90 cross-engine discrepancy of approximately 0.00385 mV RMS. This experiment fixes that finest dt and the refined NEURON reference (0.5-um segments), then increases only the AMSN sectioned-mesh reference frequency from 2,000 to 6,000 Hz.

The purpose is to determine whether further AMSN spatial refinement decreases the remaining error, and whether the benefit is consistent across the source, soma and distal basal probe.

## Fixed setup

### Morphology and recording sites

- NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`.
- Partial human temporal neocortex pyramidal-cell reconstruction with soma, basal and apical dendrites, no axon; metadata indicates moderate dendritic completeness and mesiotemporal sclerosis. Keep CC BY 4.0 attribution.
- Source: basal q75 SWC node 3784.
- Probes: basal q75 source 3784, soma 1, basal q90 3814.
- NEURON 0.5-um segment-centre mapping offsets: source 0.079655 um; soma 0 um; q90 0.242787 um.

### Spatial and temporal reference

- NEURON 9.0.2, max section segment length 0.5 um, 25,233 segments.
- Fixed dt = 0.0015625 ms; duration 5 ms; 3,200 integration steps.
- AMSN max physical electrical edge 100 um; max electrotonic extent 0.1; caller-protected source and probe SWC points.
- AMSN reference frequencies: 2,000, 3,000, 4,000 and 6,000 Hz.

### Identical electrical/synaptic parameters

- (R_i=0.7\;\Omega\,m)
- (R_m=1.0\;\Omega\,m^2)
- (C_m=0.01\;F/m^2)
- (E_{leak}=-65\;mV)
- AMPA-like peak conductance 0.8 nS; tau rise 0.2 ms; tau decay 2 ms; Erev 0 mV.
- One deterministic NetStim event at 0 ms, noise 0.

These are engineering comparison settings, not a calibrated patient-specific or universal human synapse.

## Results

### Mesh size and q90 cross-engine difference

| AMSN reference frequency | Compartments | Max physical electrical edge (um) | Max electrotonic extent | q90 max abs error (mV) | q90 RMS error (mV) |
|---:|---:|---:|---:|---:|---:|
| 2,000 Hz | 2,541 | 11.7135 | 0.099995 | 0.006475 | 0.003851 |
| 3,000 Hz | 3,077 | 9.9559 | 0.099981 | 0.005884 | 0.003752 |
| 4,000 Hz | 3,526 | 9.3741 | 0.099973 | 0.005573 | 0.003699 |
| 6,000 Hz | 4,287 | 9.3741 | 0.099984 | 0.005312 | 0.003670 |

From 2,000 to 6,000 Hz:
- compartment count rises by about 68.7%;
- q90 RMS discrepancy falls by about 4.7%;
- q90 maximum absolute discrepancy falls by about 18.0%;
- the largest physical electrical edge is reduced from 11.71 to 9.37 um, then remains unchanged between 4,000 and 6,000 Hz under the current mesh constraints.

This is a diminishing-return curve, not evidence that 6,000 Hz is globally optimal.

### q90 self-convergence inside AMSN

The finest tested AMSN mesh (6,000 Hz) is used as an internal spatial reference at the same dt:

| AMSN reference frequency | q90 max abs difference vs 6,000 Hz (mV) | q90 RMS difference vs 6,000 Hz (mV) |
|---:|---:|---:|
| 2,000 Hz | 0.001245 | 0.000540 |
| 3,000 Hz | 0.000616 | 0.000267 |
| 4,000 Hz | 0.000319 | 0.000143 |
| 6,000 Hz | 0 | 0 |

The internal AMSN mesh-to-mesh difference is substantially smaller than the cross-engine q90 discrepancy (roughly 0.00054 mV RMS at 2,000 Hz versus 0.00385 mV RMS against NEURON). This indicates that increasing the tested AMSN mesh frequency is not enough to remove the remaining inter-engine difference. Further increases may yield only small changes unless other geometric/mapping/formulation effects are addressed.

### Site dependence

| AMSN frequency | q75 source RMS error (mV) | Soma RMS error (mV) | q90 RMS error (mV) |
|---:|---:|---:|---:|
| 2,000 Hz | 0.003304 | 0.00003472 | 0.003851 |
| 3,000 Hz | 0.003320 | 0.00003733 | 0.003752 |
| 4,000 Hz | 0.003328 | 0.00003880 | 0.003699 |
| 6,000 Hz | 0.003353 | 0.00004117 | 0.003670 |

Refining the AMSN mesh improves the distal q90 comparison, but source and soma RMS discrepancies increase slightly (the soma error remains very small in absolute terms). This prevents choosing a global frequency based on q90 alone and motivates an investigation of the control-volume geometry and exact sampling locations.

### q90 relative-error floor sensitivity

| AMSN frequency | Ref >=0.02 mV | Ref >=0.1 mV | Ref >=0.2 mV | Ref >=0.5 mV | Ref >=1.0 mV |
|---:|---:|---:|---:|---:|---:|
| 2,000 Hz | 1.478% | 1.170% | 0.974% | 0.692% | 0.494% |
| 3,000 Hz | 1.364% | 1.057% | 0.882% | 0.630% | 0.451% |
| 4,000 Hz | 1.228% | 0.971% | 0.817% | 0.590% | 0.426% |
| 6,000 Hz | 1.264% | 0.951% | 0.794% | 0.570% | 0.410% |

The 0.02-mV-floor maximum relative error is not monotonic between 4,000 and 6,000 Hz because the maximum can move to a different time where the reference denominator is small. At larger reference floors, the relative error declines monotonically. Absolute and RMS values remain the primary comparisons.

### Error at 0.25 ms and peak

At the q90 probe, the cross-engine error at 0.25 ms improves from -0.006073 mV at 2,000 Hz to -0.005038 mV at 6,000 Hz. The NEURON peak is 11.251039 mV above leak at 1.678125 ms for all meshes. AMSN peak rises slightly from 11.254675 to 11.255049 mV, with its sampled peak at 1.6796875 ms. The peak-time difference is one finest time step and is grid-quantized.

## Interpretation

1. The q90 discrepancy continues to decrease as AMSN mesh frequency increases from 2,000 to 6,000 Hz, but the gain in RMS is modest relative to the increase in electrical compartments.
2. The AMSN meshes themselves are close to one another by 6,000 Hz; their q90 RMS difference from the 6,000-Hz mesh is only 0.00054 mV at 2,000 Hz.
3. The cross-engine q90 RMS remains about 0.00367 mV even at 6,000 Hz. The remaining error is unlikely to be solved by simply increasing global mesh frequency.
4. The source and soma errors do not improve with increasing frequency, so no global mesh default should be selected from this one branch experiment.
5. The likely next contributors include the different NEURON/AMSN control-volume locations, interpolation/segment-centre sampling, membrane-area lumping around protected vertices, branch-junction representation, and other formulation differences. These are hypotheses to test, not established causes.

## CI and raw data

- Workflow [44761379734](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734), 1/1 job success.
- Script: `python examples/human_ampa_spatial_floor_sweep.py`.
- Raw trace dataset: 38,412 rows, split into four durable CSV files (9,603 rows per mesh):
  - `amsn-core/results/human_ampa_spatial_floor_2026-11-20_2000Hz.csv`
  - `amsn-core/results/human_ampa_spatial_floor_2026-11-20_3000Hz.csv`
  - `amsn-core/results/human_ampa_spatial_floor_2026-11-20_4000Hz.csv`
  - `amsn-core/results/human_ampa_spatial_floor_2026-11-20_6000Hz.csv`
- Compressed workflow artifact: [14640889259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734/artifacts/14640889259).

## Limits

- One partial morphology and one fast basal AMPA event.
- Passive membrane only; no active dendritic channels, NMDA voltage dependence, spine neck, calcium dynamics or experimental waveform fit.
- NEURON 0.5 um is a refined numerical reference, not exact analytical truth or experimental ground truth.
- No scientific acceptance tolerance has been declared.
- Do not call this biological validation or a complete human neuron.

## Next experiment: sample-position and area-lumping audit

The next step should not simply increase the global mesh again.

1. For the exact basal q75 and q90 SWC locations, compare the NEURON nearest segment-centre voltage with a linear interpolation between adjacent NEURON segment-centre voltages evaluated at the SWC arc coordinate. Keep the synapse event and NEURON mesh unchanged.
2. Compare AMSN's exact protected node voltage with both NEURON measurements. Quantify how much of the remaining ~0.00367-mV RMS discrepancy can be attributed to location sampling alone.
3. Audit the proximal/distal half-area assignment at the two protected points and compare the integrated surface area and axial geometry on the source-to-probe path.
4. Only if the residual is still above the desired error budget after these checks should a local branch-adaptive mesh be added. Do not raise the entire cell's mesh frequency without evidence.
