# Handoff — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Parent:** source/output map branch / PR #23  
**Successful workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089)  
**Result commit:** `83ccc27d21d87e1a50a2ad48414958fe62a4c63e`  
**Detailed report:** [PRIMA_Q25_KRYLOV_TRANSFER_STAGE_AUDIT_2026-11-24.md](amsn-core/research/PRIMA_Q25_KRYLOV_TRANSFER_STAGE_AUDIT_2026-11-24.md)

## Research question

The Krylov-growth audit found identical accepted-vector counts on Peng and Tamas, but morphology-dependent candidate residual ratios. This experiment tests whether each seed/round prefix improves source-to-output transfer responses at the seven shared outputs.

## Verified execution and coverage

The successful workflow passed all five focused tests, both pinned SWC SHA-256 checks, both Import3D preflights, all transfer computations, final production basis and projected G/C parity checks, result commit and artifact upload.

Exact read-back:
- 504 Krylov-prefix snapshots.
- 10,584 per-scenario source/output transfer summaries.
- 95,256 source/output/frequency rows.
- 1,176 output summaries aggregated across nine passive scenarios.
- 168 source summaries aggregated across seven shared outputs.
- Maximum final instrumented basis difference versus production: exactly 0.0.
- Maximum orthogonality error: 2.22e-15.

Runtime: 220.51 s wall time, 308.03 s user CPU, 300,248 KB maximum RSS. Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

Artifact: [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14894466250), SHA-256 `6f11321129aa05bc6208e67723fd211f7d4723c85138ea80e879eb25c7313026`.

## Main finding — transfer error falls sharply at every prefix

For the dual-q25 layout at order 168, the median across the three source summaries of the median seven-output complex transfer L2 error (%) is:

| Prefix | Peng mouse | Tamas human pyramidal |
|---|---:|---:|
| Seed (54 basis vectors) | 7.788e-2% | 1.848e-2% |
| After Krylov round 1 (108) | 4.427e-5% | 6.521e-6% |
| After Krylov round 2 (162) | 7.466e-8% | 1.065e-8% |
| After Krylov round 3 / order 168 | 2.140e-8% | 2.638e-9% |

Each round therefore improves the median transfer approximation substantially on both morphologies.

However, at the final order-168 prefix the dual-q25 transfer error remains larger than the seven-port baseline on all seven output groups for every source in both morphologies.

Median of the seven paired output-specific dual-q25/seven transfer-error ratios:

| Morphology | Source | Median ratio | Output groups worse than seven-port |
|---|---|---:|---:|
| Peng | Soma | 53.32× | 7 / 7 |
| Peng | Basal-q75 | 52.01× | 7 / 7 |
| Peng | Apical-q75 | 43.07× | 7 / 7 |
| Tamas | Soma | 23.06× | 7 / 7 |
| Tamas | Basal-q75 | 8.60× | 7 / 7 |
| Tamas | Apical-q75 | 6.70× | 7 / 7 |

Source-level absolute relative-L2 transfer errors remain very small: Peng 8.79e-9% to 7.28e-8%; Tamas 2.30e-9% to 7.90e-9%. The ratios use the seven-port error as the denominator, which is itself extremely small.

## 8-port comparison at final order 168

Median source-level complex transfer L2 error (%) across the seven outputs:

| Morphology | Source | Seven | Basal-q25 8 | Apical-q25 8 | Dual-q25 9 |
|---|---|---:|---:|---:|---:|
| Peng | Soma | 1.366e-9 | 1.757e-9 | 3.795e-9 | 7.281e-8 |
| Peng | Basal-q75 | 4.115e-10 | 5.628e-10 | 1.120e-9 | 2.140e-8 |
| Peng | Apical-q75 | 2.041e-10 | 2.647e-10 | 5.005e-10 | 8.792e-9 |
| Tamas | Soma | 3.427e-10 | 5.387e-10 | 5.195e-10 | 7.902e-9 |
| Tamas | Basal-q75 | 3.069e-10 | 4.455e-10 | 4.238e-10 | 2.638e-9 |
| Tamas | Apical-q75 | 3.431e-10 | 3.873e-10 | 3.858e-10 | 2.298e-9 |

The dual-q25 configuration has the largest AC transfer residual in every source/morphology row in this table. Nevertheless, all reported absolute relative-L2 transfer errors remain extremely small.

## Relation to the earlier transient results

The earlier order-168 matched pulse results showed a 14.525× median shared-output transient NRMSE ratio for dual-q25 on Peng, but 1.001× on Tamas. This AC transfer-stage audit finds dual-q25 transfer error above seven-port on both morphologies, with a larger relative gap on Peng.

These metrics are not interchangeable: the transfer audit aggregates complex frequency responses over nine discrete frequencies (0.1–10,000 Hz), while the earlier transient NRMSE measures time-domain pulse traces. A frequency-response residual does not automatically create an equal-sized pulse-trace error. The Tamas AC/transient difference is a real unresolved finding, not a contradiction to smooth over.

At order 112, final dual-q25/seven transfer-error ratios are also elevated on both samples: Peng 40.21× / 40.21× / 37.75× and Tamas 39.79× / 40.19× / 35.33× for soma / basal-q75 / apical-q75.

## Next step

Measure a denser, pulse-weighted frequency response for the seven- and nine-port models and compare it with the exact 2-ms and 10-ms transient protocols. This should identify whether the AC residual is concentrated in frequency bands that contribute little to the sampled pulse response, especially on Tamas.

## Scientific constraints

This is passive linear-RC transfer validation only. It is not active-neuron or biological validation, and two individual reconstructions are not populations. The full-Hines response remains canonical. No production code or defaults were changed.
