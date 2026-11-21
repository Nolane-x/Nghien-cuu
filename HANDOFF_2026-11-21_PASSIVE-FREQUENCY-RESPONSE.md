# Handoff — AMSN passive frequency-domain impedance

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Implementation commit:** 99daea4ea0cbaacc19b2e79f621e028fe5ccbf62  
**Three-mesh convergence commit:** 62a5d288f23084001c70e7580ac334140c09b967  
**Status:** four-mesh passive frequency-domain convergence verified through 0.0625 µm.

## Start here

1. Read AGENTS.md, HANDOFF.md, this file and the linked report.
2. Check current main head and the latest frequency-response workflow before modifying files.
3. Keep the passive parameters frozen: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV.
4. Do not claim biological validation from this numerical cross-simulator test.
5. Read [Eyal 2018 ModelDB source review](amsn-core/research/EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md) before importing any published active mechanisms.

## What changed

- \`amsn-core/src/amsn/cable.py\`: added \`CableTree.solve_passive_frequency_response()\`, a complex small-signal phasor solve using O(N) Hines elimination/back-substitution.
- \`amsn-core/tests/test_cable.py\`: dense-complex reference checks, 0-Hz/DC invariant, and input validation tests.
- \`amsn-core/examples/human_passive_frequency_response_audit.py\`: compares complex input/transfer impedance with NEURON 9.0.2 for 3 sources, 5 probes and 8 frequencies.
- \`.github/workflows/amsn-passive-frequency-response-audit.yml\`: runs the complete test suite and NEURON audit; uploads the raw CSV.
- \`amsn-core/research/HUMAN_PASSIVE_FREQUENCY_RESPONSE_AUDIT_2026-11-21.md\`: methods and interpretation limits.

## Model and protocol

Morphology: NeuroMorpho NMO_290988, file \`1094_Mohan_etal_2015.CNG.swc\`, partial temporal-cortex L2–3 pyramidal morphology (soma and basal/apical dendrites; no axon; moderate completeness). Preserve provenance from \`amsn-core/data/human/README.md\`.

Frequencies: 0.1, 1, 10, 30, 100, 300, 1,000, 3,000 Hz. Source sites: soma, basal q75, apical q75. Probe sites: soma, basal q50/q90, apical q50/q90. NEURON segment caps under sweep: 0.5, 0.25 and 0.125 µm.

The AMSN phasor is a voltage perturbation (not absolute V):
\`(G_leak + G_axial + j 2π f C) ΔV = I\`.
The \(e^{jωt}\) convention is documented in the method. Input/transfer impedance is \`ΔV/I\`; phase is compared modulo 360 degrees.

## Verified frequency-domain convergence — four meshes

All four mesh tests passed: [three-mesh workflow 44880470858](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858) and [0.0625 µm refinement 44880843864](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880843864). Each job ran 74 AMSN tests and produced 120 raw measurements on NEURON 9.0.2.

| NEURON max segment length | Segment count | Input complex median / p95 / max | Transfer complex median / p95 / max |
|---:|---:|---:|---:|
| 0.5 µm | 25,233 | 0.043796 / 0.073407 / 0.078027% | 0.039583 / 0.711515 / 1.592748% |
| 0.25 µm | 50,353 | 0.025170 / 0.064441 / 0.068446% | 0.012377 / 0.264956 / 0.534125% |
| 0.125 µm | 100,571 | 0.009610 / 0.036138 / 0.060370% | 0.006550 / 0.172349 / 0.273631% |
| 0.0625 µm | 201,021 | 0.002441 / 0.024339 / 0.025801% | 0.001939 / 0.112637 / 0.229692% |

From 0.5 to 0.0625 µm, transfer complex median/p95/max improve by ~20.42×/~6.32×/~6.93×. At 0.0625 µm, transfer magnitude maximum is 0.178790% and phase maximum is 0.117113°. Worst pair: apical q75 → apical q90 at 3 kHz; its absolute transfer impedance is about 5.16e-7 MΩ, and source/probe segment-centre offsets are 0.005167/0.002339 µm.

Raw artifacts: [0.5](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697044290), [0.25](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14696684877), [0.125](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697712070), [0.0625](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880843864/artifacts/14698056883).

All aggregate median/p95/max metrics improve with finer mesh, but some low-frequency individual maxima are not monotonic because the worst source-probe pair changes. No production mesh is declared until accuracy and compute cost are weighed.

## Validation gates

- Dense-matrix equivalence for the complex Hines solver at several frequencies.
- The 0-Hz response equals the existing DC perturbation.
- Full AMSN pytest suite.
- NEURON 9.0.2 Import3D/Impedance cross-check.
- Keep raw measurements as a downloadable workflow artifact.

## Known limitations and failure analysis

- NEURON's \`Impedance\` result is a linearized passive impedance at the selected operating point; no voltage-gated channel kinetics are included.
- The morphology is one partial cell with no axon. The source record's metadata reports mesiotemporal sclerosis; do not generalize to healthy cortical neurons.
- The 0.5 µm NEURON mesh is a reference discretization, not a mathematical continuum.
- A difference in source/probe interpolation or section-junction handling can create frequency-dependent residuals. Record locations and do not hide outliers.
- Do not tune Ri/Rm/Cm to force agreement; any mismatch should be diagnosed through geometry, capacitance, location mapping or solver math.

## Next actions

1. Run and inspect the 0.0625 µm follow-up and quantify reduction versus 0.125 µm.
2. Compare per-frequency, per-source and per-probe behavior; track absolute transfer values for weak paths.
3. If any residual persists, isolate source/probe placement, section junctions and Import3D interpolation.
4. Continue to active human cortical channels only after passive AC and transient baselines are stable.

## Source workflow and output

Workflow: https://github.com/Nolane-x/Nghien-cuu/actions/workflows/amsn-passive-frequency-response-audit.yml  
Raw artifact name: \`amsn-passive-frequency-response-neuron-9.0.2\`  
Raw CSV path inside the artifact: \`human-passive-frequency-response.csv\`.


## Latest complete Core CI

The full Core CI for current baseline commit `ccde2542c62843ac2a7f3c41efe2206e16eee543` passed 4/4 jobs: Python 3.12 and 3.13 test/compile/examples, plus NEURON cross-validation on both versions. The NEURON workflow completed passive, temporal/spatial convergence, transient pulse/step, AMPA conductance, Exp2Syn event timing and matched single-compartment checks. [Run 44881036875](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44881036875).

## Published-model source gate

Eyal et al. 2018 ModelDB 238347 has been identified as a relevant six-cell human L2/3 reference, but the official 133 MB archive is not yet verified locally. See [source review](amsn-core/research/EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md). Do not integrate mechanisms until archive integrity, cell identities, units, temperature assumptions, model provenance and license are inspected.


## Additional AC/transient invariant

A new unit test compares the complex phasor solver with a fitted steady-state 50 Hz sinusoidal response generated by AMSN's own time-domain passive solver. It explicitly accounts for the left-edge current sample convention and allows only a small backward-Euler discretization residual. This supplements dense-matrix equivalence and the 0-Hz/DC invariant; the next Core CI run must pass before this test is treated as validated.
