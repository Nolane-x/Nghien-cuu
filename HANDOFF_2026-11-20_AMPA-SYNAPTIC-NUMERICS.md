# Handoff — AMSN synaptic numerics and human L2/3 reference update

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Active branch:** main  
**Current source/test head:** 6285c104098c6a68ae7f59526de00d4216e3557c  
**Research log:** research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md  
**Literature note:** amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md

## Start here

1. Read AGENTS.md for preservation and scientific-integrity rules.
2. Read this handoff and research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md.
3. Read amsn-core/README.md and amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md.
4. Inspect the latest main commit and GitHub Actions run before changing files; this handoff was written while the latest CI run was still running.
5. Do not claim the endpoint change or alpha-limit behavior is validated until the latest workflow result and AMPA metrics have been inspected.

## Work completed in this checkpoint

### 1. Synaptic time-index correction

- File: amsn-core/src/amsn/cable.py
- Commit: 975a21db3a75a879802b681ff09733f4a1b84477
- The callback for synaptic conductance is sampled at the right endpoint t_(n+1) of each implicit voltage step, rather than the left endpoint t_n.
- Reason: NEURON's official Exp2Syn source advances the A/B kinetic states inside BREAKPOINT and then calculates g = B - A. Endpoint sampling aligns the kinetic state with the voltage step endpoint.
- The injected-current callback retains the previous left-edge zero-order-hold convention; the code comment explicitly records this distinction.
- Regression test: amsn-core/tests/test_synapses.py, test_synaptic_simulation_samples_kinetics_at_step_endpoint.

Reference: https://github.com/neuronsimulator/nrn/blob/master/src/nrnoc/exp2syn.mod

### 2. Alpha-function limit for nearly equal time constants

- File: amsn-core/src/amsn/synapses.py
- Commit: 3290aa1804bc23c4012bca7f8c560a31fd0f827f
- When tau_rise <= tau_decay and their relative gap is at most 1e-8, the implementation uses the stable alpha-function limit:
  g/g_peak = x * exp(1-x), where x = (t-onset)/tau_rise.
- Reversed constants (tau_rise > tau_decay) remain invalid.
- The rule avoids catastrophic cancellation and supports rounded literature entries that report tau1=tau2. It is a numerical limit, not evidence that the underlying unrounded biological constants are exactly equal.
- Tests were added for exactly equal and near-equal constants.

### 3. Human excitatory-synapse literature note

- File: amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md
- Commit: cfb3c872446213997ce64747d1c42f8660eff73e
- Eyal et al. 2018 values are documented with per-pair variation and source links.
- The note distinguishes abstract headline estimates (AMPA 0.88 nS; NMDA 1.31 nS) from a selected typical model (AMPA 0.73 nS; NMDA 1.31 nS; NMDA tau 8.02/34.99 ms; gamma 0.077 mV^-1) and seven pair-level Table 1 estimates.
- Current 0.8 nS / 0.2 ms / 2.0 ms AMPA-like input is an engineering test waveform, not an Eyal-calibrated or patient-specific synapse.
- The bundled NMO_290988 / Mohan morphology is a different, partial cell with mesiotemporal-sclerosis metadata; combining it with Eyal parameters is cross-source modelling, not matched-cell reproduction.

### 4. Research log

- File: research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md
- Commit: de7cf778d9f2a837675e6b74cf65b459270489e4
- Contains the baseline CI evidence, AMPA error metrics, code changes, limitations and next experiments.

## Baseline evidence before endpoint correction

Run 44749505127 on commit c608501da2df99ede3004ee6db39fad47ae8109e completed successfully. Python 3.12 and 3.13 each reported 62 tests passed; both NEURON jobs also completed the AMPA script.

The AMPA script printed metrics but had no numerical pass/fail acceptance gate. Thus green CI meant successful execution, not accepted numerical agreement.

| Observable | Max abs error | RMS abs error | Max relative error |
|---|---:|---:|---:|
| Source deflection | 0.061120023 mV | 0.027630273 mV | 1.585948% |
| Probe deflection | 0.174045110 mV | 0.037007363 mV | 7.405923% |
| Transfer ratio | 0.026541206 | 0.003311082 | 5.913765% |

Worst relative probe discrepancy was basal q75 source node 3784 -> basal q90 probe node 3814 at 0.25 ms (NEURON 1.729622377 mV; AMSN 1.601527878 mV). The source/probe mapping offsets were 0.746070 um / 2.424330 um.

These are baseline values before the endpoint sampling correction; do not reuse them as post-fix results.

## CI status at handoff creation

- The first run after the endpoint/alpha changes, run 44751896682, failed one new unit test in both Python versions. The failure was in the test's expected value: at absolute time 0.0035 s with onset 0.002 s and tau 0.001 s, elapsed time is 1.5 tau, not 0.5 tau. The implementation's observed value matched 1.5*exp(-0.5)*g_peak.
- The assertion was corrected in commit 6285c104098c6a68ae7f59526de00d4216e3557c.
- The subsequent workflow run is 44752103577: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44752103577
- It was in progress when this handoff was authored. Re-fetch its status, all jobs and logs before making claims. In the NEURON jobs, inspect the output lines for source, probe and ratio after the AMPA cross-validation step.
- Do not edit files under amsn-core while this CI is running unless a failure requires a correction; the workflow's concurrency setting cancels in-progress runs on new pushes.

## Next required experiments

1. **Complete CI readout:** confirm the corrected unit tests pass on Python 3.12/3.13, the NEURON jobs pass, and record post-endpoint AMPA error metrics. Compare to baseline.
2. **Kernel-only Exp2Syn check:** record NEURON Exp2Syn.g and AMSN conductance at identical sample times, independent of cable voltage. This will separate kernel/timing mismatch from cable geometry and voltage integration.
3. **Temporal convergence:** at fixed spatial mesh, reduce dt and compare the same event waveform in both engines.
4. **Spatial convergence:** at fixed dt, compare compact sectioned cable meshes (for example the previously measured 690/812/1052 compartment settings) against the same NEURON reference. Preserve source/probe node IDs and mapping offsets.
5. **Eyal reproduction:** obtain and inspect the original ModelDB 238347 archive, its license/provenance, morphology and mechanisms. Reproduce one original model before calling AMSN a reproduction of Eyal.
6. **NMDA mechanism:** after AMPA's numerical path has a justified error budget, add a voltage-dependent magnesium block and validate kinetics and voltage dependence against a reference mechanism.
7. **Multiple events/inhibition:** add summation, event trains, GABA_A and repeated inputs with explicit unit, event-order and conservation tests.

## Non-negotiable interpretation

- Numerical cross-simulator agreement is not biological validation.
- A single partial morphology and generic passive parameters are not a complete human neuron model.
- Do not infer cognition, intelligence or consciousness from a neuron-level statistic.
- Do not tune synaptic parameters solely to minimize the cross-simulator voltage error; first isolate solver, timing, mapping and spatial/temporal discretization errors.
- Preserve all failed tests and negative results in the research log.
