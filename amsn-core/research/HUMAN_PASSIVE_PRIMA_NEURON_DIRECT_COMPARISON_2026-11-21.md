# Direct PRIMA-to-NEURON validation of human passive port models

**Date:** 2026-11-21 (Asia/Bangkok)  
**Code commit:** https://github.com/Nolane-x/Nghien-cuu/commit/5c0a19323829e0668b68cbe8c6b21a2158eeef13  
**Human audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635 — 6/6 passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474632 — 4/4 passed  
**Summary CSV:** ../results/human_passive_prima_neuron_direct_comparison_summary_2026-11-21.csv  
**Order-sweep report:** HUMAN_PASSIVE_PRIMA_MULTISHIFT_ORDER_SWEEP_2026-11-21.md

## 1. Why another comparison was needed

Earlier reports measured how closely each reduced model reproduced the full AMSN Hines network. That isolates the error introduced by reduction, but it does not directly show the final reduced model's agreement with the independent NEURON reference.

The human audit already computes the NEURON 7×7 port impedance and admittance matrices at the same SWC source/probe locations. The PRIMA audit was extended to compare its reduced matrices directly against those NEURON matrices at every frequency and for all tested orders. No new neuron model or source coordinates were introduced.

This gives three distinct comparisons:
1. Schur/Hines identity: verifies the exact port reduction inside AMSN.
2. PRIMA versus full AMSN Hines: isolates model-reduction residual.
3. PRIMA versus NEURON: checks end-to-end agreement with the independent compartment simulator.

These errors should not be conflated or arithmetically added. They are Frobenius relative errors of complex port matrices calculated independently.

## 2. Protocol

The experiment covers three human morphology records:
- NMO_68174 cell1125: 12,399 AMSN compartments.
- NMO_68175 cell1204: 13,747 compartments.
- NMO_290988 / 1094_Mohan_etal_2015: 8,893 compartments.

Each is run against NEURON reference meshes with maximum segment lengths 0.125 and 0.0625 µm. The PRIMA basis is constructed from the same AMSN morphology tree; changing the NEURON mesh cap changes only the NEURON comparison discretization, not the PRIMA basis. Therefore there are six configuration checks but three distinct PRIMA morphology bases.

Seven retained ports are used, representing soma, basal and apical source/probe locations. Matrices are compared at 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz. The multi-shift basis expands at positive-real shifts associated with 0, 100, 1,000 and 3,000 Hz. Model orders are 28, 56 and 84.

Transient checks continue to use a 10 pA basal-q75 pulse from 2 to 12 ms, a 20 ms observation duration and backward Euler at dt=0.1 ms.

## 3. End-to-end comparison results

The following table gives global worst errors across the tested frequencies and the two NEURON mesh caps. "AMSN" columns measure the PRIMA residual against the full AMSN Hines result; "NEURON" columns compare the PRIMA port matrix directly with the NEURON reference.

| Order | State reduction | Max Z vs AMSN | Max Y vs AMSN | Max Z vs NEURON | Max Y vs NEURON | Max single-port transient NRMSE |
|---:|---:|---:|---:|---:|---:|---:|
| 28 | 99.685–99.796% | 1.8884% | 2.3475% | 1.8792% | 2.3316% | 1.70973% |
| 56 | 99.370–99.593% | 0.02002% | 0.02360% | 0.09393% | 0.02133% | 0.0003156% |
| 84 | 99.055–99.389% | 0.00009368% | 0.0001823% | 0.08943% | 0.02611% | 0.0000008743% |

The full-order AMSN-versus-NEURON reference discrepancy over the same six configurations is:
- Maximum impedance Frobenius error: 0.08941851%.
- Maximum admittance Frobenius error: 0.02617965%.

Thus, at order 84, the direct PRIMA-to-NEURON errors (0.08942854% impedance and 0.02610733% admittance) are essentially at the full AMSN-to-NEURON discrepancy level. The order-84 reduction residual against AMSN itself is much smaller: at most 0.00009368% for impedance and 0.0001823% for admittance. This indicates that, for this tested passive band and retained port set, further increasing order beyond 84 is unlikely to materially improve agreement with NEURON unless the underlying full-model discretization mismatch is also reduced.

Order 56 is a useful compromise: it retains the direct NEURON agreement within 0.09394% impedance and 0.02134% admittance while removing at least 99.37% of the compartment states. Order 84 is justified when the reduced-versus-full AMSN residual itself must be driven very low. Order 28 remains unsuitable for the full band and all tested pulse ports because its worst individual-port transient NRMSE reaches 1.71%.

## 4. Morphology-specific observations

- NMO_290988 at order 56: worst direct impedance error 0.06011% at 3 kHz; worst direct admittance error 0.00800% at 0.1 Hz. The admittance maximum occurs at low frequency, unlike the other morphologies.
- NMO_68174 at order 56: worst direct impedance and admittance errors are 0.09393% and 0.02133%, respectively, at 3 kHz.
- NMO_68175 at order 56: worst direct impedance and admittance errors are 0.05118% and 0.01853%, respectively, at 3 kHz.

For all three morphologies, the worst single-port transient error is localized at an apical-q90 probe for orders 56 and 84. For order 28, the worst port is usually apical q90, but NMO_68175's largest transient error occurs at the apical-q75 source port. This supports continued testing of apical transfer paths rather than relying only on aggregate all-port metrics.

## 5. Reproducibility

The direct comparison workflow [44921474635](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635) passed all six morphology/mesh jobs. Every job ran 99 AMSN tests before evaluating its seven-port frequency and transient matrices.

Core CI [44921474632](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474632) passed all four jobs:
- Python 3.12: 99/99 tests.
- Python 3.13: 99/99 tests.
- NEURON cross-validation on Python 3.12 and 3.13: passed.

The raw order-sweep CSVs and logs are preserved in the six workflow artifacts:
- NMO_68174 .125 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14713563252
- NMO_68174 .0625 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14713579653
- NMO_68175 .125 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14713856985
- NMO_68175 .0625 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14714265622
- NMO_290988 .125 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14714310494
- NMO_290988 .0625 µm: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635/artifacts/14714026553

## 6. Interpretation and limits

This validates a passive numerical reduction at seven selected ports, across the tested 0.1–3 kHz frequency band and one basal-q75 current-pulse protocol. It does not establish biological validity or accuracy for active membrane channels, nonlinear synapses, stochastic release, ion concentration, calcium, metabolism or plasticity.

The direct NEURON residual includes differences between the AMSN and NEURON implementations/discretizations and the shared passive parameterization; it is not a pure biological error. NMO_290988 is a partial dendritic reconstruction without an axon and has a mesiotemporal-sclerosis context. It must not be described as a healthy-control morphology. The full Hines model remains the canonical simulator; PRIMA remains an optional passive reduced model.

## 7. Current recommendation

- Order 56: balanced reduced passive port model for the present seven-port, 0.1–3 kHz protocol.
- Order 84: high-accuracy passive reduction; its internal error is below the observed full-model cross-simulator residual.
- Order 28: use only for a narrower or explicitly error-tolerant task, not as the general-purpose preset.

Next work should test additional source ports and pulse widths, perturb passive parameters without rebuilding the Krylov basis, and extend the comparison above 3 kHz. These checks are needed before making the reduced model a default or coupling it to active and synaptic dynamics.


## Parameter-basis reuse follow-up

A further audit perturbed Rm, Cm and Ra by ±20% on three human morphologies and compared a frozen nominal basis with a fresh same-order multi-shift basis. The 27-scenario audit passed 3/3; all 54 reduced projections passed Cholesky. Frozen-basis global maxima were 0.9946% Z / 0.9768% Y at 10 kHz, with worst single-port transient NRMSE 0.0006268%. See [HUMAN_PASSIVE_PRIMA_PARAMETER_ROBUSTNESS_2026-11-21.md](HUMAN_PASSIVE_PRIMA_PARAMETER_ROBUSTNESS_2026-11-21.md) and [morphology summary data](../results/human_passive_prima_parameter_robustness_morphology_summary_2026-11-21.csv).
