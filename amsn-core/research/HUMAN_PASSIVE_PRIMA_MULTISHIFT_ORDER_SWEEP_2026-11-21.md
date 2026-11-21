# Human passive multi-shift PRIMA and reduced-order sweep

**Date:** 2026-11-21 (Asia/Bangkok)  
**Implementation:** https://github.com/Nolane-x/Nghien-cuu/commit/9d9b4817de53002e657913f01d7b8a8a1d66c9b4  
**Human six-job sweep:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444 — 6/6 passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477434 — 4/4 passed  
**Configuration/order summary:** ../results/human_passive_prima_multishift_order_sweep_summary_2026-11-21.csv  
**Previous DC-only baseline:** HUMAN_PASSIVE_PRIMA_REDUCTION_AUDIT_2026-11-21.md

## 1. Objective

The DC-expanded PRIMA model already compressed 8,893–13,747 passive compartments to 56 states and reproduced short pulses very accurately. Its weakness was a growing frequency-response residual near 3 kHz. The next step was to construct a passive rational-Krylov basis that samples several frequency scales, then determine the smallest useful state order.

## 2. Multi-shift basis

The full passive RC model is

\[
C\dot v+Gv=Bi,\qquad y=B^Tv.
\]

For each positive-real shift \(\sigma_k=2\pi f_k\), the basis begins with

\[
(G+\sigma_k C)^{-1}B
\]

and extends through repeated actions of

\[
-(G+\sigma_k C)^{-1}C.
\]

The four expansion-frequency labels used are 0, 100, 1,000 and 3,000 Hz. These correspond to positive-real Laplace shifts; they are not imaginary-axis sinusoidal solves. Shifted solves use a real tree Hines elimination. The algorithm seeds all shifts first, then grows their Krylov blocks in round-robin order, with global reorthogonalization.

Projection remains congruent:

\[
G_r=V^TGV,\qquad C_r=V^TCV,\qquad B_r=V^TB.
\]

Thus the projected matrices retain symmetry and positive definiteness. Each reduced model is checked by Cholesky factorization. This maintains passive RC stability while moving approximation accuracy toward the higher-frequency band.

## 3. Human morphology and protocol

The same three morphology records and seven retained ports were used:
- NMO_68174 cell1125: 12,399 compartments.
- NMO_68175 cell1204: 13,747 compartments.
- NMO_290988 / 1094_Mohan_etal_2015: 8,893 compartments.

Each was tested with two NEURON reference mesh caps (0.125 and 0.0625 µm). The AMSN morphology tree and PRIMA basis are unchanged by that NEURON reference-mesh cap, so paired rows are repeated numerical checks of the same PRIMA model, not independent PRIMA discretizations.

The reduced-order sweep evaluated orders 28, 56 and 84. Every order was compared with the full Hines port impedance and its exact Schur boundary operator at 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.

Transient validation used a 10 pA pulse at basal q75, from 2–12 ms, integrated by backward Euler with dt=0.1 ms over 20 ms. All seven retained port traces were compared.

## 4. Order sweep: accuracy versus state count

Across all six configurations, all maximum frequency errors occurred at 3 kHz.

| Morphology | Order | State reduction | Max Z error | Max Y error | Max single-port transient NRMSE |
|---|---:|---:|---:|---:|---:|
| NMO_68174 cell1125 | 28 | 99.7742% | 1.8269% | 2.3319% | 0.18894% |
| NMO_68174 cell1125 | 56 | 99.5484% | 0.009914% | 0.023604% | 0.00002791% |
| NMO_68174 cell1125 | 84 | 99.3225% | 0.00002669% | 0.00014837% | 0.000000874% |
| NMO_68175 cell1204 | 28 | 99.7963% | 0.8786% | 2.1551% | 0.06943% |
| NMO_68175 cell1204 | 56 | 99.5926% | 0.006601% | 0.017386% | 0.000005437% |
| NMO_68175 cell1204 | 84 | 99.3890% | 0.00001997% | 0.00011408% | 0.000000630% |
| NMO_290988 Mohan2015 | 28 | 99.6851% | 1.8884% | 2.3475% | 1.70973% |
| NMO_290988 Mohan2015 | 56 | 99.3703% | 0.020017% | 0.021058% | 0.00031560% |
| NMO_290988 Mohan2015 | 84 | 99.0554% | 0.00009368% | 0.00018225% | 0.0000000521% |

### Global envelopes

| PRIMA order | Worst Z error | Worst Y error | Worst single-port transient NRMSE | State reduction range |
|---:|---:|---:|---:|---:|
| 28 | 1.8884% | 2.3475% | 1.70973% | 99.6851–99.7963% |
| 56 | 0.020017% | 0.023604% | 0.00031560% | 99.3703–99.5926% |
| 84 | 0.00009368% | 0.00018225% | 0.000000874% | 99.0554–99.3890% |

Order 28 gives the highest compression but is not accurate enough for a general 0.1–3 kHz port model under this test: the worst per-port transient NRMSE reaches 1.71%. Order 56 is the strongest balanced setting in this sweep: over 99.37% state reduction, both frequency errors below 0.024%, and the worst per-port transient NRMSE below 0.000316%. Order 84 increases the reduced state count by 50% relative to order 56 but lowers the worst 3 kHz admittance error to 0.000183% and the worst transient port NRMSE below 9e-7%.

## 5. Multi-shift versus DC-only PRIMA at equal order 56

At the same order 56, the multi-shift basis improves the worst frequency error by:
- 60.97–98.22× in port impedance across the three morphologies.
- 83.44–112.07× in port admittance across the three morphologies.

The largest absolute worst-case change is for NMO_290988: impedance error falls from 1.9660% to 0.02002%, and admittance error from 2.3600% to 0.02106%. NMO_68174 changes from 0.72395%/2.23607% to 0.009914%/0.023604%. NMO_68175 changes from 0.40244%/1.45069% to 0.006601%/0.017386%.

Transient behavior remains very accurate at order 56. The maximum all-port NRMSE is 2.845e-6%, while the maximum individual-port NRMSE is 0.0003156%. On NMO_290988 this is slightly higher than the DC-only order-56 run, but remains small in absolute terms. The other two morphologies have lower aggregate transient errors under multi-shift.

## 6. Reproducibility

The human order sweep workflow [44920477444](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444) passed 6/6. Each job ran 99 tests, built the DC and multi-shift references, evaluated orders 28/56/84, and uploaded a 48-row sweep CSV.

Core CI [44920477434](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477434) passed all four jobs, including 99 tests on Python 3.12 and 3.13 and both NEURON cross-validation jobs.

| Morphology | NEURON mesh cap | Actions artifact |
|---|---:|---|
| NMO_68174 cell1125 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14712733677 |
| NMO_68174 cell1125 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14713736135 |
| NMO_68175 cell1204 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14713094465 |
| NMO_68175 cell1204 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14713726193 |
| NMO_290988 Mohan2015 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14713696310 |
| NMO_290988 Mohan2015 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444/artifacts/14713132918 |

## 7. Recommendation and limits

For the currently tested passive 0.1–3 kHz, seven-port system:
- Use order 56 as the balanced research preset.
- Keep order 84 as the high-accuracy preset when a smaller frequency residual justifies 28 extra states.
- Do not use order 28 as a general-purpose preset without restricting its intended band and validating each port's transient error.

This is numerical validation of passive RC reduction, not biological validation. Reduced coordinates are global electrical modes rather than anatomical compartments. The method does not yet include voltage-gated channels, nonlinear synapses, ion concentrations, calcium, stochastic release, metabolism or plasticity. NMO_290988 is an incomplete dendritic reconstruction without an axon and has a mesiotemporal-sclerosis context; do not interpret it as a healthy control. The full Hines solver remains the reference implementation.

Next: test new pulse locations and waveform widths, vary passive parameters, include higher frequency evaluation points beyond 3 kHz, and begin a controlled coupling experiment with active channels while preserving the passive core's passivity guarantees.
