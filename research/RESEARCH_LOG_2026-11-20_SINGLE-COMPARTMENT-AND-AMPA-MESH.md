# Research log — 2026-11-20 — single-compartment equivalence and fast-AMPA mesh sensitivity

**Branch:** main  
**Research scope:** numerical verification of AMSN synaptic integration and spatial discretization against NEURON 9.0.2.  
**Code additions:** single-compartment voltage audit, fast-AMPA spatial mesh frequency sweep, NEURON segment-centre refinement sweep.  
**No biological parameters were fitted in this session.**

## 1. Questions

1. Does AMSN's implicit one-compartment membrane update reproduce NEURON's voltage and conductance for the same membrane parameters, one Exp2Syn event and the exact same fixed-step grid?
2. When one fast AMPA-like event is injected into a real partial human morphology, how sensitive is the AMSN/NEURON voltage discrepancy to the spatial reference frequency used by the AMSN sectioned mesh?
3. After fixing the AMSN mesh, does refining NEURON's own segment centres change the measured source/probe voltages enough to explain the residual q90 discrepancy?

## 2. Sources and experimental setup

### Primary simulator reference

- NEURON 9.0.2, pinned in GitHub Actions.
- Official Exp2Syn mechanism: https://github.com/neuronsimulator/nrn/blob/master/src/nrnoc/exp2syn.mod
- NEURON d-lambda guidance: https://www.neuronsimulator.org/en/9.0.1/guide/using_the_d_lambda_rule.html
- NEURON documentation and implementation explain that spatial discretization should account for the frequency content of the signals being modelled. The conventional 100-Hz d-lambda reference is a design convention, not a guarantee that it resolves every fast transient.

### Morphology

- NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc.
- Partial human temporal neocortex pyramidal-cell reconstruction: soma, basal and apical dendrites, no axon; metadata describes moderate dendritic completeness and mesiotemporal sclerosis.
- This is a single partial morphology, not a complete healthy neuron or population sample. Preserve CC BY 4.0 attribution in the data README.
- Source/probe SWC IDs: basal q75 = 3784; soma = 1; basal q90 = 3814.
- NEURON Import3D site mappings in the 5-um baseline:
  - basal q75: dend[54], x=0.61933082, total mapping offset 0.746070 um;
  - soma: soma[0], x=0.5, offset 0;
  - basal q90: dend[54], x=0.81625480, total mapping offset 2.424330 um.
- Geometry offsets at these sites are approximately 0.000004, 0 and 0.000002 um respectively; the dominant part of these reported offsets is the centre of the nearest NEURON segment.

### Shared passive and synaptic parameters for fast-AMPA experiments

- Specific axial resistivity Ri = 0.7 ohm*m.
- Specific membrane resistance Rm = 1.0 ohm*m^2.
- Specific capacitance Cm = 0.01 F/m^2.
- Leak reversal = -65 mV.
- Synaptic reversal = 0 mV.
- Peak AMPA-like conductance = 0.8 nS.
- tau_rise = 0.2 ms; tau_decay = 2.0 ms.
- Event start = 0 ms; one event, deterministic.
- These are the existing engineering cross-validation parameters and generic passive defaults. They are not a patient-specific fit or a universal human-synapse parameter set.

## 3. Single-compartment voltage/current audit

### Code and CI

- Script: `amsn-core/examples/single_compartment_voltage_audit.py`.
- Integrated in the comprehensive AMSN Core CI and a dedicated, faster workflow: `.github/workflows/amsn-single-compartment-audit.yml`.
- Dedicated workflow run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267
- Result: completed successfully; 2/2 jobs passed (Python 3.12 and 3.13), both running NEURON 9.0.2.
- Artifacts:
  - Python 3.12: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267/artifacts/14639521144
  - Python 3.13: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267/artifacts/14639160102
- Relevant code/test commit before the workflow-only index updates: `89b400a5ac2ffe9fddcb1bf2f6ca6df71ca28304`.

### Protocol

One NEURON cylinder, one AMSN compartment. Both use the exact membrane area reported by the NEURON segment, and the same Cm, Rm, Ra, leak reversal, initial voltage and Exp2Syn event. A single event is applied. Three timestep sizes are used: 0.025, 0.0125 and 0.00625 ms, over 5 ms.

The test separates:
- Conductance at the same timestamp versus the one-step-earlier aligned conductance.
- NEURON's recorded Exp2Syn BREAKPOINT current (pre-voltage-update in this fixed-step schedule).
- Current reconstructed at the previous voltage from the recorded conductance.
- The implicit end-step synaptic current used by the backward-Euler voltage equation.
- AMSN and NEURON membrane voltage.

### Results

Both Python versions produced the same metrics at printed precision.

| dt (ms) | Samples | Max voltage error (uV) | Max aligned g error (nS) | Max NEURON recorded-i reconstruction error (pA) | Max implicit-current cross-engine error (pA) |
|---:|---:|---:|---:|---:|---:|
| 0.025 | 201 | 3.1974e-10 | 2.3781e-15 | 1.2925e-14 | 1.8902e-13 |
| 0.0125 | 401 | 1.3500e-10 | 2.3781e-15 | 1.9387e-14 | 1.3571e-13 |
| 0.00625 | 801 | 1.8190e-09 | 7.0052e-15 | 1.9387e-14 | 6.6239e-13 |

The corresponding maximum voltage discrepancy is about 3.20e-16, 1.35e-16 and 1.82e-15 V respectively. These are machine-scale differences for this controlled problem.

The aligned conductance is identical at the script's printed precision to roughly 2.4e-24–7.0e-24 S. The same-time (unaligned) kernel still intentionally differs because the fixed-step NetStim/Exp2Syn protocol exhibits the previously measured one-step effective event/recording offset.

The dedicated script enforces controlled numerical equivalence gates:
- voltage error <= 1e-9 V;
- aligned conductance error <= 1e-12 S;
- NEURON recorded-current reconstruction error <= 1e-15 A;
- implicit current cross-engine error <= 1e-15 A.

All three dt cases printed `controlled_single_compartment_equivalence=PASS` in both Python matrix jobs.

### Interpretation

This establishes that the one-compartment SI units, conductance waveform alignment, and backward-Euler voltage equation agree with NEURON 9.0.2 for this exact fixed-step configuration. It does not validate the mapping of a synapse to a branched morphology, branch-junction approximations, transient spatial discretization or biology.

A subtle but important distinction is preserved: NEURON's recorded `Exp2Syn.i` reconstructs from the recorded conductance and the voltage at the beginning of the voltage update; the implicit current at the end-step voltage is a separate quantity. Comparing those without aligning the voltage time index would falsely diagnose an integration error.

## 4. Fast-AMPA spatial mesh frequency sweep

### Code and CI

- Script: `amsn-core/examples/human_ampa_mesh_frequency_sweep.py`.
- Workflow: `.github/workflows/amsn-ampa-spatial-mesh-audit.yml`.
- Successful sweep run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757763565
- Result: 1/1 job and all steps passed; Python 3.12, NEURON 9.0.2.
- Artifact: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757763565/artifacts/14640160840
- Source commit for first sweep: `e44e23d2d48dac705e26bbbd4bf8520ddedbd2dd`.
- The comprehensive AMSN Core CI for this source snapshot also completed successfully: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757671076 (4/4 jobs success).

### Controlled variables

- Same NMO_290988 morphology.
- Same basal q75 source (3784), soma probe (1) and basal q90 probe (3814); all protected in AMSN's mesh.
- Same NEURON reference and 5-um maximum segment length.
- Same event, conductance, reversal potential and dt = 0.00625 ms.
- Only the AMSN mesh reference frequency changes: 100, 250, 500, 1000, 2000 Hz.
- AMSN mesh maximum electrotonic edge extent remains 0.1; maximum physical segment length remains 100 um.

### Mesh and basal q90 results

| AMSN reference frequency | Compartments | Max physical electrical edge (um) | Max electrotonic edge | q90 max absolute error (mV) | q90 RMS error (mV) | q90 max relative error (reference >= 0.02 mV) |
|---:|---:|---:|---:|---:|---:|---:|
| 100 Hz | 689 | 37.2511 | 0.099797 | 0.175536 | 0.076589 | 27.4009% |
| 250 Hz | 993 | 28.1930 | 0.099973 | 0.150913 | 0.067562 | 19.6849% |
| 500 Hz | 1,341 | 22.3220 | 0.099775 | 0.144792 | 0.064989 | 18.8876% |
| 1,000 Hz | 1,838 | 15.8819 | 0.099973 | 0.141443 | 0.063693 | 18.9248% |
| 2,000 Hz | 2,541 | 11.7135 | 0.099995 | 0.139635 | 0.062947 | 18.9618% |

The 2,000-Hz mesh is the most resolved tested mesh, but q90 error has started to plateau. Increasing AMSN compartments from 689 to 2,541 reduces q90 RMS error from 0.076589 to 0.062947 mV, while the maximum absolute discrepancy falls from 0.175536 to 0.139635 mV.

### Relative-error floor sensitivity

Relative error near the beginning of an EPSP is unstable because the reference deflection is very small. For basal q90, the maximum relative error changes with the minimum reference-voltage floor:

| AMSN mesh frequency | Reference floor >=0.02 mV | >=0.1 mV | >=0.2 mV | >=0.5 mV | >=1.0 mV |
|---:|---:|---:|---:|---:|---:|
| 100 Hz | 27.40% | 20.85% | 17.91% | 13.22% | 10.02% |
| 250 Hz | 19.68% | 15.27% | 13.34% | 10.23% | 8.00% |
| 500 Hz | 18.89% | 14.46% | 12.64% | 9.73% | 7.63% |
| 1,000 Hz | 18.92% | 14.18% | 12.35% | 9.49% | 7.45% |
| 2,000 Hz | 18.96% | 14.03% | 12.20% | 9.37% | 7.35% |

This is why the maximum relative error alone should not be used as a single acceptance number. Absolute/RMS error, peak amplitude/time, transfer ratio, and floor sensitivity must be reported together.

### Error at 0.25 ms (basal q90)

NEURON reference deflection = 1.860319 mV at this time. AMSN values:

| Mesh | AMSN q90 deflection (mV) | Error (mV) | NEURON transfer ratio | AMSN transfer ratio |
|---:|---:|---:|---:|---:|
| 100 Hz | 1.723365 | -0.136954 | 0.454296 | 0.427104 |
| 250 Hz | 1.747797 | -0.112522 | 0.454296 | 0.429878 |
| 500 Hz | 1.752677 | -0.107642 | 0.454296 | 0.430208 |
| 1,000 Hz | 1.755162 | -0.105157 | 0.454296 | 0.430339 |
| 2,000 Hz | 1.756483 | -0.103837 | 0.454296 | 0.430416 |

The source-node error falls more strongly than the distal q90 error. For example, source-node maximum relative error falls from 26.53% at 100Hz to 1.61% at 2kHz; the q90 error remains materially larger. This points to a residual branch-path/measurement/mapping contribution, not only local mesh size.

### Interpretation and next experiment

The 100-Hz default is not sufficient for a rapidly changing synaptic transient at this location under the chosen error metrics. A higher reference frequency improves the result, but the q90 discrepancy plateaus. The NEURON q90 sample is located at the nearest segment centre with a reported 2.424330-um offset from the protected SWC node, while the AMSN probe is at the exact protected SWC control point. That difference needs its own controlled experiment.

This sweep does not prove that 2kHz is optimal or universally required. It demonstrates a mesh sensitivity for one cell, one synapse, one branch path, and one fixed dt.

## 5. NEURON segment-centre refinement sweep — implementation/validation pending

A second script has been added:
- `amsn-core/examples/human_ampa_neuron_segment_sweep.py`.
- It fixes AMSN to a 2,000-Hz sectioned mesh and changes NEURON's maximum segment length across 5, 2, 1 and 0.5 um.
- It records the source/probe centre mapping offsets and compares both AMSN-vs-NEURON voltage traces and each NEURON mesh against the finest NEURON mesh.
- The existing spatial-mesh workflow has been extended to run this script and upload both raw outputs.

At the time this log was first drafted, the latest run for the extended workflow was queued/in progress. Its completion status and log must be inspected before recording a numeric result. Do not describe this mapping-refinement experiment as passed until it has run successfully.

## 6. Scientific limitations

- One morphology only, with moderate dendritic completeness and no axon.
- The model is passive apart from a prescribed conductance waveform; no voltage-gated dendritic channels, spine neck, NMDA magnesium block or receptor state model is present.
- NEURON's 0.5-um refinement in the next experiment is still a numerical reference, not experimental truth.
- The parameter set is generic/engineering, not a matched human biological calibration.
- No experimental EPSP waveform was fitted in this session.
- The existing full-morphology AMPA script uses a 5-um NEURON segment reference; the finer-segment sweep is needed before assigning residual q90 error to AMSN alone.
- Relative error floors and exact sampling times must be included in reports.
- A successful CI run establishes reproducibility/execution and the explicit controlled equivalence gates, not biological accuracy.

## 7. Commit/workflow chain

- Single-compartment code/test snapshot: `89b400a5ac2ffe9fddcb1bf2f6ca6df71ca28304`.
- Dedicated single-compartment workflow: run 44757208267, 2/2 jobs success.
- Human AMPA mesh frequency sweep script: `e44e23d2d48dac705e26bbbd4bf8520ddedbd2dd`.
- Human AMPA mesh frequency sweep first successful workflow: run 44757763565, 1/1 job success.
- The comprehensive AMSN Core CI for the mesh script also passed: run 44757671076, 4/4 jobs success.
- NEURON segment sweep script: `166ebed5a977ffe372794a40a5ebfb4af446cf4b`.
- Extended spatial workflow (including NEURON segment sweep): latest workflow SHA to be fetched from main; run 44758503143 was the latest run at log creation and must be inspected.

## 8. Next experiments, ordered

1. Complete NEURON segment-centre refinement sweep and inspect 5/2/1/0.5-um mapping offsets, NEURON self-convergence, and AMSN-vs-NEURON differences.
2. If finer NEURON nseg materially changes q90 response, freeze a converged NEURON reference before scoring AMSN mesh accuracy.
3. If q90 does not change, investigate branch path geometry, root/soma junction, point-to-segment mapping and proximal/distal half-area assignment.
4. After spatial mapping is isolated, repeat dt = 25, 12.5, 6.25, 3.125 and 1.5625 us on one chosen high-resolution mesh; keep event-time alignment fixed.
5. Only when temporal and spatial error budgets are separated should an AMPA tolerance be proposed.
6. Reproduce an original Eyal/ModelDB model with its own morphology/mechanisms before claiming a matched human L2/3 reproduction; the ModelDB GitHub mirror has no licence field and points to a 133MB upstream ZIP, so review distribution/license terms before vendoring.

---

## 5. Final NEURON segment-centre refinement results — 2026-11-20

### Execution evidence

- Script: `amsn-core/examples/human_ampa_neuron_segment_sweep.py`.
- Successful extended workflow: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44758746509
- Result: 1/1 job; all workflow steps succeeded, including the original 100–2,000-Hz AMSN mesh sweep and the new NEURON segment-refinement sweep.
- NEURON 9.0.2, Python 3.12.
- Raw combined artifact: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44758746509/artifacts/14640046511 (893,805 bytes).
- The segment sweep uses the same partial human morphology, source/probes, passive parameters, AMPA event and dt=0.00625 ms. AMSN is fixed at 2,000-Hz reference frequency (2,541 compartments); only NEURON's max segment length is changed to 5, 2, 1 and 0.5 um.
- The earlier workflow attempt 44758503143 failed because it used bitwise array equality for time grids. The script was corrected to use a 1e-12 s allclose tolerance, consistent with the other simulator time-grid checks. The failed attempt is preserved in Actions history.

### Mapping and q90 error

| NEURON max segment length | NEURON segment count | q90 centre mapping offset | AMSN-vs-NEURON max abs error | RMS error | Max relative error |
|---:|---:|---:|---:|---:|---:|
| 5 um | 2,637 | 2.424330 um | 0.139635 mV | 0.062947 mV | 18.9618% |
| 2 um | 6,397 | 0.527632 um | 0.055024 mV | 0.039240 mV | 1.3809% |
| 1 um | 12,685 | 0.215842 um | 0.026003 mV | 0.014339 mV | 2.9332% |
| 0.5 um | 25,233 | 0.242787 um | 0.006433 mV | 0.003840 mV | 1.3170% |

The maximum relative-error metric uses a reference EPSP deflection floor of 0.02 mV. It is not expected to decrease monotonically because the location/time of the largest relative error can change. Absolute and RMS errors provide a clearer convergence picture here.

### NEURON self-convergence to the 0.5-um run

This is crucial: NEURON's own segment refinement changes the measured q90 response even though the SWC source node, probe node, event and passive parameters are unchanged.

| NEURON max segment length | q90 max abs difference vs NEURON 0.5 um | q90 RMS difference vs NEURON 0.5 um |
|---:|---:|---:|
| 5 um | 0.134360 mV | 0.062995 mV |
| 2 um | 0.053669 mV | 0.037094 mV |
| 1 um | 0.023560 mV | 0.015711 mV |
| 0.5 um | 0 | 0 |

Thus, the earlier comparison against 5-um NEURON included a sizeable reference-discretization error. The 5-um reference is not sufficiently refined for this fast basal q90 voltage comparison. It was incorrect to attribute the whole q90 discrepancy to AMSN's mesh.

The 0.5-um NEURON run has 25,233 segments and is the finest reference in this sweep. It is still a numerical reference, not experimental truth or a mathematically exact solution.

### Source and soma observations

| NEURON max segment length | q75 source max abs error | q75 source RMS | Soma max abs error | Soma RMS |
|---:|---:|---:|---:|---:|
| 5 um | 0.045356 mV | 0.033567 mV | 0.000599 mV | 0.000468 mV |
| 2 um | 0.049919 mV | 0.037018 mV | 0.000647 mV | 0.000507 mV |
| 1 um | 0.014444 mV | 0.010649 mV | 0.000204 mV | 0.000158 mV |
| 0.5 um | 0.004342 mV | 0.003300 mV | 0.000043 mV | 0.000035 mV |

For the q90 at the 0.5-um NEURON setting:
- NEURON peak = 11.241034 mV above leak, time 1.68125 ms.
- AMSN peak = 11.244652 mV above leak, time 1.68125 ms.
- Max absolute time-series difference = 0.006433 mV.
- RMS time-series difference = 0.003840 mV.

### Interpretation

The segment-centre location discrepancy is a major contributor to the earlier q90 mismatch. Reducing NEURON's segment length from 5 to 0.5 um reduces the q90 mapping offset from 2.424 to 0.243 um and makes NEURON's own q90 trace converge substantially. Against this finest NEURON reference, the fixed 2,000-Hz AMSN mesh achieves 0.00384 mV RMS and 0.00643 mV maximum absolute difference at q90.

This is strong numerical agreement for this specific passive morphology, synaptic waveform, timestep and set of protected sites. It is not a blanket claim that the entire AMSN morphology implementation is validated. More branch locations, other cells and finer timestep checks are still required.

### Updated scientific conclusion

- The original q90 discrepancy was a mixture of AMSN mesh error and NEURON reference segment-centre/discretization error.
- Increasing AMSN reference frequency from 100 to 2,000 Hz materially improved source and q90 observables.
- Refining NEURON from 5 to 0.5 um also materially changed q90 voltages; therefore a 5-um NEURON output must not be treated as ground truth for this fast EPSP.
- A 2,000-Hz AMSN mesh vs 0.5-um NEURON reference is now the preferred candidate for the next temporal-convergence study, not yet the default for all morphologies.

## 6. Comprehensive CI status at the time of handoff update

Core CI run for code snapshot `cb678620cf6cbc62feec68f5f23542079d83c54b`: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44758745994. Unit-test jobs were already successful on Python 3.12 and 3.13; NEURON cross-validation jobs were still in progress when this paragraph was first written. Refresh the run before reporting its final conclusion.

The dedicated single-compartment workflow remains fully verified: run 44757208267 (2/2 jobs success).
The extended AMPA spatial/mapping workflow is fully verified: run 44758746509 (1/1 job success).
