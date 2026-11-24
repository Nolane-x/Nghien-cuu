# Handoff — Cross-morphology PRIMA q25 Krylov-prefix transfer audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-krylov-transfer-stage-cross-morphology-2026-11-24  
**Parent:** source/output map branch / PR #23  
**Successful workflow:** [45337038089](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089)  
**Result commit:** `a0d6e8e2c9a8f203d53a0c0c04c2691f9cc8702f`  
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
- Maximum orthogonality error: 1.78e-15.

Runtime: 220.51 s wall time, 308.03 s user CPU, 300,248 KB maximum RSS. Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

Artifact: [prima-q25-krylov-transfer-stages-cross-morphology](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45337038089/artifacts/14893398287), SHA-256 `a274bcd3ff1ce31bc2659bd6d3f12b0bd93b7d2853f8d6f62bdf82f7e0a1e9d`.

## Main finding — transfer error falls sharply at every prefix

For the dual-q25 layout at order 168, the median across the three source summaries of the median seven-output complex transfer L2 error (%) is:

| Prefix | Peng mouse | Tamas human pyramidal |
|---|---:|---:|
| Seed | 7.788e-2% | 1.848e-2% |
| After Krylov round 1 | 4.427e-5% | 6.521e-6% |
| After Krylov round 2 | 7.466e-8% | 1.065e-8% |
| After Krylov round 3 / order 168 | 2.140e-8% | 2.638e-9% |

Each round therefore improves the transfer approximation substantially on both morphologies. However, at the final order-168 prefix the dual-q25 transfer error remains larger than the seven-port baseline on all seven output groups for every source in both morphologies.

Median of the seven output-specific dual-q25/seven transfer-error ratios:

| Morphology | Source | Median ratio | Output groups worse than seven-port |
|---|---|---:|---:|
| Peng | Soma | 53.32× | 7 / 7 |
| Peng | Basal-q75 | 50.48× | 7 / 7 |
| Peng | Apical-q75 | 45.29× | 7 / 7 |
| Tamas | Soma | 23.15× | 7 / 7 |
| Tamas | Basal-q75 | 9.56× | 7 / 7 |
| Tamas | Apical-q75 | 6.16× | 7 / 7 |

Absolute transfer L2 errors remain very small: final dual-q25 source-level medians range from 8.79e-9% to 7.28e-8% on Peng and 2.30e-9% to 7.90e-9% on Tamas. These ratios use the seven-port transfer error as the denominator.

## Relation to the earlier transient results

The earlier order-168 matched pulse results showed a 14.525× median shared-output NRMSE ratio for dual-q25 on Peng, but 1.001× on Tamas. The transfer-stage audit now shows dual-q25 AC transfer error above seven-port on both morphologies, with a larger relative gap on Peng.

These metrics are not interchangeable: the transfer audit aggregates complex frequency responses over nine AC frequencies, while the earlier transient NRMSE measures time-domain pulse traces. A residual in a frequency response does not automatically create an equal-sized pulse-trace error. The Tamas AC/transient difference is therefore a useful finding, not a contradiction to smooth over.

## Scientific constraints

This is passive linear-RC transfer validation only. It is not active-neuron or biological validation, and two individual reconstructions are not populations. The full-Hines response remains canonical. No production code or defaults were changed.
