# Handoff — Cross-morphology PRIMA q25 basis conditioning audit

**Date:** 24 November 2026  
**Branch:** research/prima-cross-morphology-q25-conditioning-audit-2026-11-24  
**Parent:** Tamas q25 replication branch / PR #20  
**Successful workflow:** [45334425019](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019)  
**Result commit:** `7558f0bfb58296bca35bfc18dab7cb903727d793`  
**Detailed report:** [PRIMA_Q25_CROSS_MORPHOLOGY_CONDITIONING_AUDIT_2026-11-24.md](amsn-core/research/PRIMA_Q25_CROSS_MORPHOLOGY_CONDITIONING_AUDIT_2026-11-24.md)

## Research question

The dual-q25 layout produced a 14.525× median shared-output error ratio at order 168 on NMO_163775 Peng mouse morphology, but only 1.001× on NMO_107159 Tamas human pyramidal morphology. This audit measures basis orthogonality, reduced G/C spectra, generalized passive RC decay-rate ranges, q25 port leverage and initial multi-shift seed allocation to test whether these structural metrics explain the different transient behavior.

## Scope and verified execution

Two independently pinned morphologies; four layouts (7, basal-only 8, apical-only 8, dual-q25 9); orders 112/168; nine passive parameter scenarios; six expansion shifts.

Corrected workflow 45334425019 succeeded. It passed 4/4 focused tests, both SWC SHA-256 checks, both Import3D preflights, all 144 model diagnostics, result commit and artifact upload.

Read-back coverage is exact:
- 144 reduced-model structural metric rows.
- 1,152 per-port leverage rows.
- 864 initial shift-seed rows.
- 16 summary groups (2 morphologies × 4 layouts × 2 orders).

Runtime: 123.38 s wall, 215.69 s user CPU, 179,728 KB maximum RSS. Python 3.12.16 / NumPy 2.5.5 / NEURON 9.0.2.

Artifact: [prima-q25-cross-morphology-conditioning-audit](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019/artifacts/14892704511), SHA-256 `12b721916eaabb1edd39da6bc2265714f4fc2178980c77292cb8f75d6d135e55`.

## Main findings

1. **Basis orthogonality is not the explanation.** Across all 144 models, maximum (|V^TV-I|) entry error is 2.22e-15 and the basis Gram condition number stays within approximately 1.0000000000000036–1.0000000000000067. Both morphologies have numerically orthonormal bases to floating-point precision.

2. **Initial shift seeding is also not discriminating.** All 864 initial seed observations exactly equal the layout port count (7, 8 or 9) for every shift, morphology, order and scenario. Every shift accepts the entire independent input-port block. This says nothing about later round-robin Krylov growth, which was not counted in this metric.

3. **The projected G/C condition numbers vary, but do not track the order-168 penalty simply.** For the Peng mouse, the median dual-q25 order-168 G and C condition numbers are about 506,011 and 123.47, versus 521,168 and 125.28 for seven ports. For the Tamas human, dual-q25 is about 800,981 and 148.86, versus 1,502,475 and 195.90 for seven ports. The dual layout therefore has lower projected G/C condition numbers in both morphologies, yet its transient effect is very different.

4. **q25 basis-row leverage is morphology-dependent but not a direct error predictor.** At order 168, q25 port leverage medians are close to one on Peng (basal 0.99999998; apical 0.99998037) and lower on Tamas (basal 0.83548; apical 0.63030). The Tamas model nevertheless has near-parity shared-output error, while Peng has the large relative dual-q25 penalty. Leverage alone cannot explain the outcome.

Thus this audit does **not** identify a causal numerical-conditioning mechanism. It rules out a simple story based on loss of basis orthogonality or failure to seed the initial port blocks. More targeted diagnostics are needed for the later Krylov-growth trajectory and transfer-function approximation.

## Scientific constraints

Only two individual passive linear-RC reconstructions are compared, not species or cell-class populations. The audit does not validate active channels, synapses, plasticity or biological behavior. It does not alter production code, solver defaults or the canonical full-Hines reference.
