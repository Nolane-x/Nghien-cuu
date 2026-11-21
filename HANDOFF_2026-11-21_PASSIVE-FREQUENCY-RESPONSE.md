# Handoff — AMSN passive frequency-domain impedance

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Implementation commit:** 99daea4ea0cbaacc19b2e79f621e028fe5ccbf62  
**Three-mesh convergence commit:** 62a5d288f23084001c70e7580ac334140c09b967  
**Status:** 0.5/0.25/0.125 µm convergence matrix passed; 0.0625 µm follow-up pending.

## Start here

1. Read AGENTS.md, HANDOFF.md, this file and the linked report.
2. Check current main head and the latest frequency-response workflow before modifying files.
3. Keep the passive parameters frozen: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV.
4. Do not claim biological validation from this numerical cross-simulator test.

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

## Verified initial result — 0.5 µm

Workflow [44880205634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880205634) passed, including 74 tests. NEURON 9.0.2 used 25,233 segments; AMSN used 8,893 compartments; the audit generated 120 rows. Input complex error median/p95/max was 0.043796/0.074104/0.078027%. Transfer complex error was 0.039583/0.711515/1.592748%. Maximum transfer magnitude error was 1.094346%; phase error 0.666724°. Input impedance is much closer than the worst distal transfer measurements.

The largest transfer percentage occurred for apical q75 → basal q90 at 3,000 Hz, where transfer impedance itself is very small (~8.37e-9 MΩ in NEURON). Interpret relative error with absolute impedance.

The three-mesh run [44880470858](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858) passed all three jobs. Segment counts were 25,233 / 50,353 / 100,571 for 0.5 / 0.25 / 0.125 µm. Transfer complex median/p95/max errors were 0.039583/0.711515/1.592748%, 0.012377/0.264956/0.534125%, and 0.006550/0.172349/0.273631%, respectively. The aggregate improvement is consistent, but not every individual pair maximum is monotone at the low end. Artifacts: [0.5 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697044290), [0.25 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14696684877), [0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697712070). A 0.0625 µm follow-up is next; do not tune passive parameters or declare a production mesh yet.

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
