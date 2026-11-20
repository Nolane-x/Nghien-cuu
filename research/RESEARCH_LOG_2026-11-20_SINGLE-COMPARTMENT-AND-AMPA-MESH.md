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

---

## 7. Final fast-AMPA temporal convergence — 2026-11-20

### Execution evidence

- Script: `amsn-core/examples/human_ampa_temporal_convergence.py`.
- Workflow: `.github/workflows/amsn-ampa-temporal-convergence.yml`.
- Successful workflow: [44760319787](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787), 1/1 job success.
- Environment: Python 3.12.16, NEURON 9.0.2.
- Code snapshot: `a78fcd1ab00d4175b60898b9ad539d84d9d8bf74`.
- Report: `amsn-core/research/HUMAN_AMPA_TEMPORAL_CONVERGENCE_2026-11-20.md`.
- Raw dataset: `amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv`, 18,615 data rows, committed in `4a9f966f2f883c6fc19cc93cfbf38eb96eadf8ed`.
- CI artifact: [14640319049](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787/artifacts/14640319049).

### Fixed protocol

The spatial meshes are held constant throughout all trials:
- NEURON 9.0.2: max section segment length 0.5 um, 25,233 segments.
- AMSN: sectioned mesh at 2,000-Hz electrotonic reference, 2,541 compartments.

Morphology and sites:
- NMO_290988 / 1094_Mohan_etal_2015.CNG.swc.
- Input basal q75 SWC node 3784.
- Probes: basal q75 3784, soma 1, basal q90 3814.
- NEURON mapping offsets at the selected 0.5-um mesh: source 0.079655 um, soma 0 um, q90 0.242787 um.

Passive parameters and synaptic event are unchanged from the previous spatial experiment: Ri 0.7 ohm*m, Rm 1.0 ohm*m^2, Cm 0.01 F/m^2, Eleak -65 mV, AMPA-like peak conductance 0.8 nS, tau rise 0.2 ms, tau decay 2 ms, Erev 0 mV, one deterministic event at t=0. Duration 5 ms.

Only dt changes: 0.025, 0.0125, 0.00625, 0.003125, 0.0015625 ms. Coarse grids are nested integer multiples of the finest grid. Each simulator is compared with its own finest-dt trace and the two simulators are compared at identical physical times.

### q90 results

| dt (ms) | Cross-engine max abs (mV) | Cross-engine RMS (mV) | NEURON vs finest RMS (mV) | AMSN vs finest RMS (mV) |
|---:|---:|---:|---:|---:|
| 0.025 | 0.006266 | 0.003798 | 0.088665 | 0.088695 |
| 0.0125 | 0.006376 | 0.003826 | 0.041208 | 0.041222 |
| 0.00625 | 0.006433 | 0.003840 | 0.017625 | 0.017631 |
| 0.003125 | 0.006461 | 0.003847 | 0.005869 | 0.005871 |
| 0.0015625 | 0.006475 | 0.003851 | 0 | 0 |

Both simulators' own temporal traces converge monotonically toward the finest-dt reference as dt is reduced. Their cross-engine discrepancy stays almost constant: q90 RMS changes from 0.003798 to 0.003851 mV (~1.4%), and max absolute error from 0.006266 to 0.006475 mV (~3.3%).

Interpretation: the remaining cross-engine error is close to a non-temporal floor for this fixed spatial configuration. It is likely associated with spatial representation, control-volume geometry/area allocation, mapping or other fixed formulation differences. This audit does not uniquely identify which component dominates.

At the finest dt, NEURON q90 peak is 11.251039 mV above leak and AMSN is 11.254675 mV above leak; sampled peak times are 1.678125 ms and 1.6796875 ms respectively. Peak-time estimates remain quantized to the fixed time grid.

The relative-error floor sensitivity is retained in the report and raw data. For q90, the max relative error at a 0.02-mV reference floor rises from 1.03% to 1.48% as dt is reduced, even while absolute/RMS error remains nearly constant. This occurs because relative error is sensitive to small denominators near EPSP onset; report absolute/RMS and relative errors with their floors together.

### Harness failures and fixes preserved in Actions history

- Run 44759371095 failed because the coarse/fine timestep ratio was inverted, producing `slice step = 0`.
- Run 44760000836 corrected the ratio but showed that NEURON record vectors were retained between successive `finitialize()` calls and previous data arrays were mutated by later runs. The failing nested-grid assertion exposed this lifecycle issue.
- The final script now computes the integer ratio as `dt_coarse / dt_finest`, verifies the nested time vectors, copies each NEURON `Vector` into independent NumPy arrays, and lets HOC record vectors be released before the next simulation.
- Official NEURON Vector record documentation: https://www.neuronsimulator.org/en/9.0.1/progref/programming/math/vector.html.
- Run 44760319787 completed successfully with the full five-dt sweep and raw dataset preserved.

### Scientific interpretation

1. The single-compartment audit establishes equivalence of the one-compartment implicit voltage/current calculation under the exact tested fixed-step protocol.
2. The spatial sweep and NEURON segment refinement established a refined candidate spatial configuration (AMSN 2,000 Hz vs NEURON 0.5 um) for this one fast basal AMPA event.
3. The temporal sweep demonstrates each simulator's own trace converges as dt is reduced.
4. The q90 cross-engine error is nearly timestep-independent over the tested range. The remaining ~0.00385-mV RMS / ~0.00648-mV maximum absolute discrepancy should now be treated as a spatial/representation floor candidate, not blamed on temporal integration.
5. This is not biological validation, not a universal tolerance and not a matched Eyal 2018 cell reproduction.

### Next experiment

Hold dt=0.0015625 ms and the NEURON 0.5-um reference fixed; sweep AMSN spatial reference frequency above 2,000 Hz (e.g. 2,000, 3,000 and 4,000 Hz). Keep the same source/probes and AMPA input. Measure whether the remaining q90 discrepancy decreases and how electrical compartment count scales. Follow with an independent branch and apical input. Do not alter conductance/time constants to force agreement.

### Core CI status when appended

After adding the temporal report to the AMSN tree, Core CI run [44760827496](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760827496) was in progress. Refresh it before claiming final comprehensive CI status. The dedicated temporal workflow itself is confirmed green.

---

## 8. Final spatial-floor sweep at finest dt — 2026-11-20

### Execution evidence

- Script: `amsn-core/examples/human_ampa_spatial_floor_sweep.py`.
- Workflow: `.github/workflows/amsn-ampa-spatial-floor-audit.yml`.
- Run [44761379734](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734), conclusion success, 1/1 job.
- NEURON 9.0.2, Python 3.12.
- Code snapshot: `6a04ef9c41f0909200aa02a7b827389311d6c432`.
- Raw artifact: [14640889259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734/artifacts/14640889259).
- Durable raw traces: four CSVs under `amsn-core/results/human_ampa_spatial_floor_2026-11-20_*`, 9,603 data rows each (38,412 total).

### Controlled configuration

- Same NMO_290988 partial human morphology.
- NEURON held fixed at max segment 0.5 um (25,233 segments).
- dt held fixed at 0.0015625 ms for 5 ms.
- Same AMPA-like engineering event and passive parameters as the temporal sweep.
- Source SWC 3784 (basal q75); probes 3784, soma 1, basal q90 3814.
- Only AMSN mesh reference frequency changes: 2k, 3k, 4k, 6k Hz; max physical extent 100 um, max electrotonic extent 0.1, same protected nodes.

### Results

| AMSN frequency | Compartments | q90 max abs error (mV) | q90 RMS error (mV) | q90 mesh self RMS vs 6k (mV) |
|---:|---:|---:|---:|---:|
| 2,000 Hz | 2,541 | 0.006475 | 0.003851 | 0.000540 |
| 3,000 Hz | 3,077 | 0.005884 | 0.003752 | 0.000267 |
| 4,000 Hz | 3,526 | 0.005573 | 0.003699 | 0.000143 |
| 6,000 Hz | 4,287 | 0.005312 | 0.003670 | 0 |

From 2k to 6k:
- compartment count increases by 68.7%;
- q90 RMS cross-engine difference improves by about 4.7%;
- q90 max absolute difference improves by about 18%;
- q90 error at 0.25 ms improves from -0.006073 to -0.005038 mV.

But source and soma RMS differences rise slightly:
- source q75: 0.003304 → 0.003353 mV;
- soma: 0.00003472 → 0.00004117 mV.

Thus higher global mesh frequency improves the distal q90 result but not every site. The 2k-to-6k internal AMSN q90 mesh difference (0.000540 mV RMS) is far smaller than the cross-engine residual (~0.00367 mV RMS). Further global refinement is unlikely to solve the residual efficiently by itself.

### Interpretation

The q90 discrepancy has begun to approach a representation/measurement floor. This is consistent with the prior temporal sweep, where the cross-engine q90 RMS error remained around 0.00380–0.00385 mV despite reducing dt by 16×.

Do not select 6k as a global default: it costs 68.7% more compartments than 2k while delivering only a 4.7% q90 RMS improvement and slightly worsening source/soma RMS discrepancies. The mesh trend is site-dependent.

The most likely remaining candidates to investigate are:
- NEURON's nearest segment-centre sample versus the exact SWC arc coordinate used by protected AMSN vertices;
- per-control-volume membrane-area lumping at source/probe positions;
- branch-junction and piecewise morphology representation differences.

These are hypotheses, not identified causes.

### Next precise experiment

At dt=0.0015625 ms and NEURON 0.5 um, record the voltages of the two NEURON segment centres bracketing the Import3D SWC arc coordinate for source 3784 and probe 3814. Interpolate linearly between the two segment-centre voltages to the exact SWC arc coordinate. Compare that interpolated measurement to:
1. NEURON's nearest-centre measurement;
2. AMSN's protected SWC control-point voltage.

Do this without changing the synapse, mesh, event, or solver. In parallel, inspect and report the exact proximal/distal area split on the AMSN control volumes at these sites. This is more informative than immediately increasing the whole-cell mesh frequency again.

### Core CI status

Core CI run [44761340640](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761340640) was in progress at the time this entry was appended. Refresh the latest CI run after the report/raw-data commits.

---

## 9. NEURON probe interpolation and equal-support area audits — 2026-11-20

### 9.1 Probe interpolation

Execution:
- Script: `amsn-core/examples/human_ampa_probe_interpolation_audit.py`.
- Workflow: [44762715648 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648), 1/1 job.
- Python 3.12, NEURON 9.0.2, NEURON 0.5-um max segments, dt=0.0015625 ms, 5 ms.
- Artifact: [14642920467](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648/artifacts/14642920467).
- Code: `amsn-core/examples/human_ampa_probe_interpolation_audit.py`.
- Three durable raw CSVs (9,603 data rows each):
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_2000Hz.csv`
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_4000Hz.csv`
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_6000Hz.csv`

Method: NEURON voltage is recorded at the nearest segment centre and linearly interpolated between the two adjacent segment-centre voltages to the exact Import3D SWC arc coordinate. The synapse remains at the nearest segment; the interpolation is a readout-only diagnostic and does not change the NEURON dynamics.

Results:

| AMSN mesh | q90 nearest RMS (mV) | q90 interpolated RMS (mV) | q75 nearest RMS (mV) | q75 interpolated RMS (mV) |
|---:|---:|---:|---:|---:|
| 2,000 Hz | 0.003851 | 0.003448 | 0.003304 | 0.003696 |
| 4,000 Hz | 0.003699 | 0.003646 | 0.003328 | 0.003872 |
| 6,000 Hz | 0.003670 | 0.003736 | 0.003353 | 0.003941 |

NEURON readout shift RMS due to interpolation is 0.003269 mV at q90 and 0.001559 mV at q75. At q90, interpolation improves the cross-engine RMS at 2k and 4k, but slightly worsens it at 6k; at q75 it worsens the RMS at all three meshes. The effect is clearly site-dependent and cannot be treated as a global correction.

The maximum absolute q90 error also changes:
- 2k: 0.006475 -> 0.004613 mV;
- 4k: 0.005573 -> 0.005151 mV;
- 6k: 0.005312 -> 0.005409 mV.

Interpretation: NEURON segment-centre readout is a material contributor at q90, but it does not explain all residual error and the correction is not uniformly beneficial across sites/mesh sizes. A linear interpolation is not exact continuous-cable truth, and the point process remains on the nearest segment.

### 9.2 Equal-support membrane-area integration

Execution:
- Script: `amsn-core/examples/human_ampa_matched_support_area_audit.py`.
- Workflow: [44763720776 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776), 1/1 job.
- NEURON 9.0.2, max segment length 0.5 um, Python 3.12.
- Artifact: [14642971232](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776/artifacts/14642971232).
- Raw summary: `amsn-core/results/human_ampa_matched_support_area_2026-11-20.csv`.

Method: for q75/q90 in an unbranched section, take half the incoming and half the outgoing AMSN electrical edge lengths to define the protected node's local area support. Map the interval to the same NEURON section using Import3D arc coordinates, then sum NEURON segment areas weighted by fractional overlap of each segment's x interval.

Results:

| Mesh | Site | NEURON area on matched support (um²) | AMSN node area (um²) | Difference |
|---:|---|---:|---:|---:|
| 2k Hz | q75 | 8.753409 | 8.756880 | +0.039661% |
| 2k Hz | q90 | 6.924175 | 6.924175 | -0.000001814% |
| 4k Hz | q75 | 6.531920 | 6.535293 | +0.051636% |
| 4k Hz | q90 | 5.054776 | 5.054776 | -0.000001814% |
| 6k Hz | q75 | 5.404350 | 5.407040 | +0.049770% |
| 6k Hz | q90 | 4.239368 | 4.239368 | -0.000001814% |

The q90 matched-support area agrees essentially exactly; q75 differs by only about 0.04–0.05%. Thus the earlier apparent 6–10× discrepancy between one NEURON segment area and the AMSN node area was due to comparing different support sizes. It was not evidence that AMSN had a gross local membrane-area excess.

Limits:
- Only two unbranched basal nodes were included; soma requires separate treatment of the soma surface term and multiple proximal branch contributions.
- NEURON segment areas are integrated by fractional segment overlap, a fine numerical estimate, not an analytic continuous-surface integral.
- This does not test all branchpoints or all morphologies.

### 9.3 Updated interpretation and next work

The q90 voltage residual includes a readout-position component, but gross control-volume membrane-area mismatch is not supported at the two tested basal sites when supports are matched. The remaining candidates now include axial-resistance integration, axial discretization, branch-junction treatment, and the fact that the NEURON point process is attached to a nearest segment while the AMSN conductance is attached to an exact protected SWC vertex.

Next steps:
1. Build an equal-support axial resistance audit for incoming/outgoing basal q75/q90 edges using the same NEURON section intervals and AMSN edge geometry integrals.
2. Preserve the distinction between local area and axial geometry; do not tune Ri or other biological parameters to force voltage agreement.
3. Repeat probe interpolation and matched-support area at another basal branch and an apical point.
4. Treat the 2k–6k mesh trend as site-dependent; do not select a global default solely based on q90.
5. Only after axial, interpolation and local area terms are bounded should a numerical acceptance tolerance be proposed.

### Workflow/C​​I status notes

The interpolation workflow 44762715648 and matched-support area workflow 44763720776 both completed successfully (1/1). Core CI jobs triggered during this documentation sequence were cancelled by subsequent commits before the full NEURON matrix finished; their unit-test jobs completed successfully where reported. Do not claim a full comprehensive Core CI pass for the latest main head until a current Core CI run completes all four jobs.
