# Passive PRIMA reduced-order model — human morphology audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** https://github.com/Nolane-x/Nghien-cuu/commit/7cfd4b7b59b828582fa81c336d3073ef05fe579b  
**Human morphology audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972 — 6/6 jobs passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918897010 — 4/4 jobs passed  
**Summary data:** ../results/human_passive_prima_reduction_summary_2026-11-21.csv  
**Exact Schur reference:** HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md

## 1. Research question

Can a passive multicompartment neuron with roughly 9,000–14,000 electrical compartments be replaced by a much smaller dynamic model that preserves the current-to-voltage behavior at selected soma and dendritic ports, while retaining mathematical stability and passivity?

The preceding Schur experiment gives an exact frequency-dependent port operator at each requested frequency. It does not by itself provide a compact, frequency-independent state-space realization. This experiment therefore adds a structure-preserving Krylov projection (PRIMA-style) and tests its dynamic realization against the full Hines cable model.

## 2. Reduced model and preservation of passivity

For the linear passive cable, write the perturbation voltage relative to leak reversal as

\[
C\dot v + Gv = Bi,\qquad y=B^Tv.
\]

Here:
- C is the positive diagonal membrane-capacitance matrix.
- G is the membrane-leak diagonal plus the symmetric axial graph Laplacian.
- B selects the retained current-injection ports.
- i is the retained-port current vector and y is the corresponding port-voltage vector.

The block Krylov basis is generated from the DC port responses and repeated applications of the passive RC operator:

\[
\mathcal K_r = \operatorname{span}\{G^{-1}B,\; -G^{-1}CG^{-1}B,\;
(-G^{-1}C)^2G^{-1}B,\ldots\}.
\]

The implementation orthogonalizes this block with twice-reorthogonalized modified Gram–Schmidt, capped at 56 independent basis vectors for the human audit. It applies G inverse using the existing tree-structured Hines solver; it does not materialize a dense full-neuron matrix.

With an orthonormal basis V, the reduced matrices are formed by congruence:

\[
C_r=V^TCV,\qquad G_r=V^TGV,\qquad B_r=V^TB.
\]

The reduced dynamics are

\[
C_r\dot x+G_rx=B_ri,\qquad y=B_r^Tx.
\]

Because C and G are symmetric positive definite and the projection is congruent, the reduced C_r and G_r are also symmetric positive definite when the basis has full column rank. The implementation checks this with Cholesky factorization. The resulting passive RC realization has positive decay rates and no unstable poles, up to floating-point error. This guarantee applies to this linear passive subsystem; it does not automatically extend to nonlinear active channels or synapses.

## 3. Human morphology experiment

The audit retained seven unique SWC ports:
- source ports: soma, basal q75 and apical q75;
- probe ports: soma, basal q50/q90 and apical q50/q90;
- the soma is shared between source and probe roles.

Three human morphology records were evaluated with two NEURON reference mesh caps each:
- NMO_68174 cell1125: 12,399 AMSN compartments;
- NMO_68175 cell1204: 13,747 AMSN compartments;
- NMO_290988 / 1094_Mohan_etal_2015: 8,893 AMSN compartments.

The PRIMA order was fixed at 56. Each model was evaluated at 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz. The full-order reference is the same morphology converted into an AMSN cable tree and solved using the full Hines solver; the exact Schur port operator supplies an independent reduced-boundary check. The NEURON mesh cap belongs to the parallel AMSN-versus-NEURON comparison. It does not change the AMSN cable tree or PRIMA basis, which explains why the paired PRIMA metrics are effectively identical across the two NEURON mesh settings.

## 4. Results

| Morphology | Full compartments | PRIMA order | States removed | Max Z error | Max Y error | Worst frequency | Max single-port transient NRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|
| NMO_68174 cell1125 | 12,399 | 56 | 99.5484% | 0.7239% | 2.2361% | 3 kHz | 0.00009392% |
| NMO_68175 cell1204 | 13,747 | 56 | 99.5926% | 0.4024% | 1.4507% | 3 kHz | 0.00015661% |
| NMO_290988 Mohan2015 | 8,893 | 56 | 99.3703% | 1.9660% | 2.3600% | 3 kHz | 0.00014027% |

The 56-state realization removes between 99.37% and 99.59% of the full compartment state count. At 0.1–100 Hz, the port impedance and admittance errors remain essentially at floating-point levels. Error increases with frequency: the largest 1 kHz impedance/admittance errors are approximately 0.0778%/0.1122%, and the worst 3 kHz errors across the three morphologies are 1.9660%/2.3600%.

All six morphology/mesh jobs ran the same eight-point frequency comparison. The exact values are preserved in the six Actions artifacts linked below; the six-row configuration summary is committed alongside this report.

### Transient validation

A 10 pA current pulse was injected at the basal q75 source port from 2 ms to 12 ms. The full and reduced models were advanced with backward Euler at dt=0.1 ms over 20 ms. All seven retained port traces were compared.

- Worst all-port NRMSE across the three morphologies: 0.00003031%.
- Worst individual retained-port NRMSE across all runs: 0.00015662%.
- Worst absolute port-trace error: 1.252e-6 mV.
- The maximum source/probe peak relative error remained below 0.000505%.

The very small transient errors are consistent with the low-frequency moment matching in the Krylov basis. They do not imply equally small errors at every frequency: the 3 kHz impedance/admittance residual is visibly larger.

## 5. Reproducibility and artifacts

Human audit workflow 44918896972 passed all six jobs. Each job ran the complete 95-test AMSN suite, built the morphology-specific PRIMA model, checked the reduced frequency response and transient traces, and uploaded raw data.

| Morphology | NEURON mesh cap | Actions artifact |
|---|---:|---|
| NMO_68174 cell1125 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14713151497 |
| NMO_68174 cell1125 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14713220691 |
| NMO_68175 cell1204 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14712593119 |
| NMO_68175 cell1204 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14713385271 |
| NMO_290988 Mohan2015 | 0.125 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14712617807 |
| NMO_290988 Mohan2015 | 0.0625 µm | https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972/artifacts/14713360759 |

Core CI 44918897010 passed all four jobs: Python 3.12 and 3.13 test/example jobs, plus the two NEURON cross-validation jobs. Both Python versions passed 95/95 tests. The DC solve cast warning observed in the first implementation was corrected; the final 7cfd4b7 run completed without ComplexWarning.

## 6. Interpretation and limits

This is a successful numerical reduced-order model for the passive RC cable subsystem at the tested ports and parameterization. It shows that a very small, passive state-space model can preserve the selected port responses with high accuracy for the tested frequency band and pulse.

It is not yet a biological validation, a fully active neuron model or a universal compression ratio. The basis is morphology- and parameter-specific. It does not retain each physical compartment as a one-to-one state; each reduced state is a global combination of full-order compartment voltages. The model does not currently cover voltage-gated channel dynamics, nonlinear synaptic conductances, stochastic release, calcium signaling, ion concentration dynamics, energy metabolism or plasticity.

NMO_290988 is a partial dendritic reconstruction with no axon and a mesiotemporal-sclerosis context; do not interpret it as a healthy-control cell. The two NEURON mesh caps are reference discretizations, not two independent PRIMA meshes. The passive parameter values used here are numerical defaults, not a fitted population-level distribution.

The full Hines solver remains the canonical model. Do not replace it as the default runtime solver solely on this audit. The PRIMA implementation should be treated as an optional reduced passive subsystem until an order/frequency sweep, independent transient protocols, parameter-perturbation tests and active/synaptic coupling tests have been completed.

## 7. Next technical question

The current basis is expanded from DC, which explains its excellent low-frequency and transient behavior and its larger residual at 3 kHz. The next experiment should build a multi-shift or frequency-aware passive Krylov basis, while retaining congruence projection and positive definiteness, then map the trade-off among reduced order, 3 kHz error and transient accuracy. Test order values 28, 56, 84 and 112 before choosing a runtime preset.
