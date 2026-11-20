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
