# Handoff — AMSN synaptic timing audit (final verified checkpoint)

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Verified code/test commit:** 9e07c540edb8b298f27c21e000eec9130c846fea  
**Verification workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879  
**Research log:** research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md  
**Literature reference:** amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md

## Start here for the next AI session

1. Read AGENTS.md. Treat GitHub main as the canonical research record.
2. Read HANDOFF.md for the long-term research direction.
3. Read this file before changing AMSN synaptic code.
4. Read research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md for the full baseline, failed attempts, timing audit and current evidence.
5. Read amsn-core/README.md and amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md.
6. Check the live main head and most recent Actions run before editing. The code/test commit recorded above is the exact commit validated by the workflow; later README/research documentation commits do not alter that code snapshot.
7. Do not describe the AMPA comparison as a biological validation or accepted accuracy pass. A numerical acceptance tolerance has not yet been established.

## Research direction

AMSN (Adaptive Multi-Scale Neuron) is a research codebase for a reproducible multiscale biological-neuron simulator. Current validated scope is mainly morphology handling, passive cable dynamics and numerical cross-simulator comparison. Synaptic conductance is being developed, but the next work must first isolate kernel timing, membrane-current integration, morphology mapping and temporal/spatial discretization.

Do not jump to a multi-neuron cognitive/AI claim. A single simulated morphology does not demonstrate cognition, intelligence or consciousness.

## Implemented work in the current code snapshot

### 1. Conductance-based synapse integration

- amsn-core/src/amsn/cable.py: implicit Hines step with membrane leak plus conductance-based synaptic current g_syn * (E_rev - V).
- amsn-core/src/amsn/synapses.py: peak-normalized double-exponential conductance kernel.
- The callback is sampled at the left edge t_n and held over [t_n, t_(n+1)] for the implicit voltage solve.
- The injected-current callback uses the same left-edge zero-order-hold convention.
- Regression: test_synaptic_simulation_samples_kinetics_at_step_left_edge.

### 2. Equal-time-constant numerical limit

The double-exponential kernel supports tau_rise == tau_decay and a near-equal relative gap <= 1e-8 through the normalized alpha-function limit:

g(t)/g_peak = x * exp(1 - x), where x = (t - onset)/tau.

The implementation still rejects tau_rise > tau_decay. The alpha limit avoids cancellation for equal or nearly equal constants, which matters when literature tables round both constants to the same value. This is a mathematical limit; it does not prove that the original unrounded biological time constants are equal.

Regression tests cover equal and near-equal time constants.

### 3. Independent NEURON Exp2Syn event-timing audit

Script: amsn-core/examples/exp2syn_kernel_timing_audit.py  
CI step: "Audit NEURON Exp2Syn kernel event timing"  
Workflow run: 44754148879  
NEURON version: 9.0.2  
Protocol:
- fixed step dt = 0.025 ms
- NetStim start = 0 ms, number = 1, noise = 0
- Exp2Syn tau1 = 0.2 ms, tau2 = 2.0 ms
- peak event weight = 0.8 nS (0.0008 uS for NEURON Exp2Syn)
- duration = 5 ms
- record NEURON g and compare it to the AMSN analytical conductance at t, t-dt and t+dt

Observed in this exact protocol: the NEURON conductance recorded at t matches the analytic AMSN kernel at t-dt, not at t. Across 199 samples above the conductance floor, the one-step-earlier comparison had zero error at the script's printed precision. Same-time max relative error was 87.007470308%; one-step-later max relative error was 162.564504510%.

Interpretation: the fixed-step event/recording sequence creates a one-step effective sample offset. The kernel formula itself matches once aligned. This is a protocol-specific observation; do not generalize it to variable-step NEURON, other event sources, other event times or different recording schedules without a new audit.

This is why the final implementation uses left-edge sampling in the voltage solve. A temporary endpoint-sampling change worsened full-morphology AMPA cross-validation and was reverted. Its history and metrics remain documented in the research log.

## Final validation evidence

Workflow run 44754148879 completed with conclusion success. All four jobs passed:

| Job | Result |
|---|---|
| test (Python 3.12) | 65 passed |
| test (Python 3.13) | 65 passed |
| neuron-cross-validation (Python 3.12) | all steps passed |
| neuron-cross-validation (Python 3.13) | all steps passed |

Both NEURON jobs completed:
- independent passive cross-simulator experiment
- temporal/spatial convergence sweep
- passive transient pulse/step comparison
- AMPA-like conductance cross-validation
- isolated Exp2Syn kernel timing audit
- artifact preservation

### AMPA-like full-morphology comparison

Both NEURON jobs reproduced the pre-endpoint baseline after left-edge sampling was restored:

| Observable | Max absolute error | RMS absolute error | Max relative error |
|---|---:|---:|---:|
| Source deflection | 0.061120022 mV | 0.022560023 mV | 1.585947581% |
| Probe deflection | 0.174045110 mV | 0.022578342 mV | 7.405922860% |
| Transfer ratio | 0.026541206 | 0.003311082 | 5.913764483% |

These values are measured, not a pass against a scientifically approved tolerance. The AMPA script currently reports metrics but does not enforce a numerical acceptance threshold. Maximum probe relative error remains about 7.41%.

Artifacts:
- Python 3.12 validation: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879/artifacts/14637166626
- Python 3.13 validation: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879/artifacts/14637031574

## Human synapse literature: use carefully

The reference note documents Eyal et al. 2018 human L2/3 connection estimates. Pair-level AMPA/NMDA conductances and time constants vary substantially. The published table includes rounded examples where tau1=tau2; an alpha-function limit is numerically appropriate for the rounded values, while source-model unrounded values should be preferred for exact reproduction.

Important distinctions:
- Abstract headline per-contact estimates, pair-wise fitted Table 1 values and one selected "typical" model are different quantities.
- The current 0.8 nS / 0.2 ms / 2.0 ms AMPA-like test waveform is an engineering test input, not a calibrated human synapse.
- The bundled NMO_290988 / 1094_Mohan_etal_2015.CNG.swc morphology is not one of Eyal's cells. Combining them is cross-source modelling, not a matched-cell reproduction.
- No experimental trace was fitted in this checkpoint.

## What is not yet validated

- A matched single-compartment voltage audit comparing identical membrane parameters, NEURON current evaluation and AMSN backward-Euler voltage integration.
- Temporal convergence of the AMPA response across smaller dt values with exactly aligned events.
- Spatial mapping/convergence for the basal q75 to basal q90 probe path; mapping offsets must remain visible.
- Independent reproduction of the original Eyal/ModelDB 238347 cell with its own morphology and mechanisms.
- NMDA's voltage-dependent Mg2+ block and its calibration.
- Calcium dynamics, plasticity, gene/protein regulation, metabolism and astrocyte coupling.

## Next work — do these in order

1. **Single-compartment voltage audit:** create a minimal cylinder with matched area, Cm, Rm, Ra, leak reversal and synapse placement in NEURON and AMSN. Compare voltage and current at each fixed time step; run both left-edge and endpoint variants only in the audit harness, not by changing production semantics without evidence.
2. **Temporal convergence:** repeat the single-compartment and full-morphology AMPA experiments at dt=0.025, 0.0125, 0.00625 ms and document whether errors converge monotonically.
3. **Morphology mapping sensitivity:** focus on source SWC node 3784 (basal q75) to probe SWC node 3814 (basal q90); record section identity, normalized x, anatomical path distance and mapping offsets for both engines.
4. **Acceptance design:** use convergence and reference-solver evidence to propose absolute/relative error budgets. Do not choose tolerances solely to make the current comparison green.
5. **Eyal model reproduction:** inspect and import the original ModelDB 238347 archive after license/provenance review; use matched morphology and mechanisms for a true reproduction.
6. **NMDA:** only after AMPA kernel and voltage integration have independent error budgets, add a voltage-dependent magnesium block and compare it to an established reference mechanism.
7. **Broader biology:** after validated AMPA/NMDA, add inhibitory synapses, event trains, calcium and plasticity with source-backed parameter ranges and uncertainty distributions.

## Integrity notes

- Preserve the failed endpoint experiment, failed test expectation and early kernel script failures in the research log; they are part of the evidence chain.
- Do not claim the one-step offset is universal; it is specific to the tested NEURON fixed-step configuration.
- Do not label current AMPA results as biologically accurate or patient-specific.
- Do not tune parameters just to reduce a cross-simulator voltage discrepancy. Isolate the numerical and mapping sources first.
- Record code commit, workflow run, parameters, units, raw outputs, tolerances and limitations for every experiment.
