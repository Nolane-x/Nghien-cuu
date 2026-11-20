# Research log — 2026-11-20 — AMSN synaptic integration audit

## Question

Does the new AMSN conductance-based synaptic path use the same kinetic time indexing as NEURON Exp2Syn, and can the tested double-exponential kernel represent published limiting cases without numerical instability?

## Scope and sources inspected

- Repository rules: AGENTS.md; current main branch and latest commit history.
- AMSN implementation: amsn-core/src/amsn/cable.py, amsn-core/src/amsn/synapses.py.
- Tests: amsn-core/tests/test_synapses.py.
- Cross-validation: amsn-core/examples/human_ampa_synapse_cross_validation.py.
- CI: .github/workflows/amsn-core.yml, workflow run 44749505127.
- NEURON Exp2Syn source: https://github.com/neuronsimulator/nrn/blob/master/src/nrnoc/exp2syn.mod
- NEURON mechanism docs: https://www.neuronsimulator.org/en/9.0.1/progref/modelspec/programmatic/mechanisms/mech.html
- Human L2/3 synapse literature: Eyal et al. 2018, https://doi.org/10.3389/fncel.2018.00181; full text https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/; Table 1 https://academic.oup.com/view-large/43203137.

## Observed baseline before the fix

Workflow run 44749505127, commit c608501da2df99ede3004ee6db39fad47ae8109e, completed successfully. Both Python 3.12 and 3.13 test jobs passed (62 tests each); both NEURON cross-validation jobs completed all steps successfully.

Important distinction: the AMPA comparison had no numerical acceptance gate. CI success established that the script executed, not that AMSN was within an approved scientific tolerance.

The AMPA output had 180 voltage samples per job. Before endpoint sampling was corrected:

| Observable | Max absolute error | RMS absolute error | Max relative error |
|---|---:|---:|---:|
| Source deflection | 0.061120023 mV | 0.027630273 mV | 1.585948% |
| Probe deflection | 0.174045110 mV | 0.037007363 mV | 7.405923% |
| Transfer ratio | 0.026541206 | 0.003311082 | 5.913765% |

Relative voltage errors used the script's stated 0.02 mV reference-deflection threshold. Transfer-ratio relative errors also required reference ratio magnitude >= 0.05. No pass/fail tolerance had been scientifically justified or declared.

Worst relative probe discrepancy: basal q75 source SWC node 3784 to basal q90 probe SWC node 3814 at 0.25 ms. NEURON probe deflection was 1.729622377 mV; AMSN was 1.601527878 mV. The reported anatomical mapping offsets were 0.746070 um at the source and 2.424330 um at the probe.

## Changes made

1. Commit 975a21db3a75a879802b681ff09733f4a1b84477:
   - Changed AMSN synaptic kinetic callback sampling from the left edge t_n to the implicit-step endpoint t_(n+1).
   - NEURON's Exp2Syn source integrates the A/B kinetic states in BREAKPOINT before calculating g = B - A, so endpoint sampling aligns the kinetic state with the voltage step endpoint.
   - The existing injected-current callback retains its historical left-edge zero-order-hold convention; this is explicit in the code comment.

2. Commit a469ba242cf1a0f5bd9d46d12b8a181a720de9f3:
   - Added a regression test that records the exact times at which synaptic conductance is sampled.

3. Commit cfb3c872446213997ce64747d1c42f8660eff73e:
   - Added amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md.
   - Recorded Eyal et al. human L2/3 pair-level parameter variation and distinguished population/model-derived estimates from universal constants.
   - Explicitly classified the existing 0.8 nS / 0.2 ms / 2 ms waveform as an engineering test input, not a human-calibrated synapse.

4. Commit 3290aa1804bc23c4012bca7f8c560a31fd0f827f:
   - Added a stable alpha-function limit for double-exponential kinetics when tau_rise approaches tau_decay.

5. Commit bde04efe77b9c61e5d8c1916df1a755bfac7bb06:
   - Added equal-time-constant and near-equal-time-constant regression tests.
   - This is the current code/test head at the time of this log.

## Validation status at log creation

The final relevant workflow run is 44751896682 for commit bde04efe77b9c61e5d8c1916df1a755bfac7bb06. It was queued/in progress when this log was written. Earlier runs were cancelled because subsequent commits triggered a newer run. Do not report the new endpoint or alpha-limit changes as validated until the final run's jobs and AMPA metrics are inspected.

## Scientific interpretation and limitations

- NEURON Exp2Syn uses two kinetic states and peak normalization; source implementation is the reference for time-index semantics.
- Eyal et al. report substantial pair-level variation. Rounded entries in Table 1 include tau1=tau2; the exact unrounded model mechanism or analytically justified alpha limit must be used.
- The AMSN morphology fixture NMO_290988 / 1094_Mohan_etal_2015.CNG.swc is a separate partial reconstruction with clinical metadata noting mesiotemporal sclerosis and moderate dendritic completeness. It is not one of Eyal's six cells.
- Numerical cross-simulator agreement is not biological validation. Generic passive parameters and a cross-source combination of morphology and literature synapses cannot be called a calibrated complete human neuron.
- No numerical tolerance for AMPA voltage/transfer error has yet been established. Do not declare an AMPA validation pass based only on workflow success.

## Next concrete work

1. Inspect final CI run 44751896682; confirm all Python and NEURON jobs, exact test counts, and endpoint-corrected AMPA error metrics.
2. If the run passes, compare new and baseline metrics and retain the raw logs/artifact. If errors worsen, inspect event time alignment, mapping offsets and integration order rather than changing conductance values to force a fit.
3. Build an isolated synaptic-kernel verification against NEURON Exp2Syn conductance itself, then temporal and spatial convergence sweeps for the cable response.
4. Reproduce one original Eyal/ModelDB model with its matching morphology and active mechanisms before calling the project a biological reproduction.
5. Add voltage-dependent NMDA only after the AMPA numerical path has a declared, justified error budget. Preserve per-connection uncertainty and the magnesium-block dependence.

## Status labels

- Repository code edits: implemented but final CI pending.
- Baseline AMPA result: locally reproducible from GitHub Actions log, but not accepted as a validation pass.
- Literature review: source observations recorded; no new experimental fit performed.
- Biological calibration: not achieved.

---

## Final timing audit and verified result — 2026-11-20

### Corrected interpretation

The initial endpoint-sampling change was rejected after two independent observations:

1. Full-morphology AMPA cross-validation worsened when the AMSN synaptic conductance callback was moved from the left edge to the implicit-step endpoint.
2. A new kernel-only NEURON 9.0.2 experiment showed that the recorded Exp2Syn conductance at timestamp t matched the analytic AMSN double-exponential kernel at t - dt, not at t or t + dt.

The isolated protocol was: dt=0.025 ms; NetStim start=0 ms, number=1, noise=0; Exp2Syn tau1=0.2 ms, tau2=2.0 ms; peak weight=0.8 nS; duration=5 ms. NEURON's first recorded nonzero conductance appeared at t=0.050 ms; it exactly matched the AMSN analytic kernel at t=0.025 ms. This observed one-step effective offset is specific to this fixed-step event/recording protocol and must not be generalized to all NEURON configurations without testing.

### Kernel-only results

199 samples met the audit's conductance floor (NEURON g >= 0.02 nS):

| Alignment | Max absolute error (nS) | RMS absolute error (nS) | Max relative error |
|---|---:|---:|---:|
| Same timestamp t | 0.104963645496 | 0.015194879573 | 87.007470308% |
| One step earlier t-dt | 0.000000000000 | 0.000000000000 | 0.000000000% |
| One step later t+dt | 0.196113770015 | 0.028435257587 | 162.564504510% |

Errors are reported at the script's output precision. The result establishes the effective sample alignment for this exact test setup; it does not validate the cable voltage solve by itself.

### Final implementation decision

- Reverted the temporary endpoint sampling change.
- CableTree.simulate_synaptic() now samples the synaptic conductance callback at the left edge t_n, holding it constant over [t_n, t_(n+1)] for the implicit voltage solve.
- Added/updated test_synaptic_simulation_samples_kinetics_at_step_left_edge.
- Kept the stable alpha-function limit for equal/nearly equal rise and decay constants, plus exact/near-equal regression tests.
- Kept amsn-core/examples/exp2syn_kernel_timing_audit.py in the NEURON CI workflow and added its raw output to the uploaded validation artifact.

### Final CI evidence

Workflow: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879  
Verified code/test commit: 9e07c540edb8b298f27c21e000eec9130c846fea

All four jobs completed successfully:
- Python 3.12 unit tests: 65 passed.
- Python 3.13 unit tests: 65 passed.
- NEURON cross-validation (3.12): all steps passed, including AMPA and kernel timing audit.
- NEURON cross-validation (3.13): all steps passed, including AMPA and kernel timing audit.

With left-edge sampling restored, both NEURON jobs reproduced the previous AMPA metrics:

| Observable | Max absolute error | RMS absolute error | Max relative error |
|---|---:|---:|---:|
| Source deflection | 0.061120022 mV | 0.022560023 mV | 1.585947581% |
| Probe deflection | 0.174045110 mV | 0.022578342 mV | 7.405922860% |
| Transfer ratio | 0.026541206 | 0.003311082 | 5.913764483% |

The final metrics match the pre-endpoint baseline. They are reported measurements, not a scientific acceptance pass: the AMPA script still has no declared numerical tolerance, and the maximum relative probe error remains 7.41%.

Artifacts:
- Python 3.12: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879/artifacts/14637166626
- Python 3.13: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879/artifacts/14637031574

### Additional implementation history worth preserving

- The temporary endpoint-sampling change (commit 975a21d...) was not retained in the final code; its inferior metrics and kernel audit evidence are deliberately preserved above.
- The first alpha-limit CI attempt exposed a wrong expected value in a newly written test (elapsed time was 1.5 tau, not 0.5 tau); the test expectation was corrected in commit 6285c104....
- Two earlier kernel-audit attempts failed on unsupported HOC conveniences (steps_per_ms, then continuerun without stdrun.hoc). The final script uses h.dt and an explicit h.fadvance() loop and is green in both NEURON matrix jobs.
- These failures are retained in the GitHub Actions history; do not remove them from the research narrative.

### Remaining limits and next steps

1. The kernel-only result explains the sample alignment, but a matched single-compartment voltage experiment is still needed to isolate current evaluation and backward-Euler membrane integration from morphology.
2. Keep the AMPA tolerance open until dt convergence and spatial mapping effects are separated; do not pick a threshold solely to make CI green.
3. Investigate the 7.41% maximum relative probe discrepancy at the basal q75 to basal q90 path, keeping source/probe mapping offsets visible.
4. Reproduce an original Eyal/ModelDB 238347 cell with its own morphology and mechanisms before claiming reproduction of human L2/3 biology.
5. Only after the AMPA kernel and voltage path have explicit error budgets should voltage-dependent NMDA/Mg2+ block be added.
