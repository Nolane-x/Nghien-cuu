# Research log — Cross-morphology PRIMA q25 basis conditioning audit

**Date:** 24 November 2026  
**Branch:** research/prima-cross-morphology-q25-conditioning-audit-2026-11-24  
**Successful workflow:** [45334425019](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019)  
**Result archive commit:** `7558f0bfb58296bca35bfc18dab7cb903727d793`

## Motivation

The Peng mouse q25 ablation found a large dual-q25 order-168 penalty (14.525× median shared-output NRMSE ratio), while the independent Tamas human pyramidal replication found an approximately neutral result (1.001×). This audit asks whether basis orthogonality, reduced matrix conditioning, q25 port leverage or the initial multi-shift block seeding explains this morphology-by-order difference.

## Design

For both morphologies, all four layouts, basis orders 112/168 and all nine passive parameter scenarios:
- rebuild the PRIMA multi-shift basis with the existing builder;
- measure (V^TV-I), Gram eigenvalues and Gram condition number;
- measure projected conductance/capacitance eigenvalue ranges and condition numbers;
- measure generalized passive RC decay-rate dynamic range from the symmetric whitened G/C pair;
- measure each retained port's basis-row leverage;
- reproduce the initial seed stage and count independent seed columns per expansion shift.

Initial seed counts are explicitly not the later round-robin Krylov growth.

## Execution and read-back

- Workflow [45334425019](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019): **success**.
- Tests: 4 passed.
- Both pinned SWC checksums passed.
- Both Peng and Tamas Import3D preflights passed.
- Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.
- Runtime: 123.38 s wall, 215.69 s user CPU, 179,728 KB peak RSS.
- Result commit: `7558f0bfb58296bca35bfc18dab7cb903727d793`.
- Artifact: [prima-q25-cross-morphology-conditioning-audit](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019/artifacts/14892704511), SHA-256 `12b721916eaabb1edd39da6bc2265714f4fc2178980c77292cb8f75d6d135e55`.

All generated files were read back. Exact rows: 144 model metrics, 1,152 port leverage entries, 864 shift-seed entries and 16 summary groups (2 × 4 × 2).

## Findings

### Basis orthogonality

The maximum absolute entry of (V^TV-I) is 2.22e-15 over all models. Basis Gram condition numbers range only from approximately 1.0000000000000036 to 1.0000000000000067. Both morphologies' basis matrices are therefore orthonormal to numerical precision. A simple loss-of-orthogonality explanation for the Peng residual is not supported.

### Projected matrix conditioning

Median condition numbers over nine passive scenarios:

| Morphology | Layout | Order | cond((G_r)) | cond((C_r)) | RC rate dynamic range |
|---|---|---:|---:|---:|---:|
| Peng | seven | 112 | 371,069 | 107.26 | 51,417 |
| Peng | eight_basal_q25 | 112 | 223,427 | 84.26 | 46,399 |
| Peng | eight_apical_q25 | 112 | 219,171 | 83.66 | 46,184 |
| Peng | nine_both_q25 | 112 | 192,763 | 79.93 | 44,279 |
| Peng | seven | 168 | 521,168 | 125.28 | 54,299 |
| Peng | eight_basal_q25 | 168 | 512,608 | 124.17 | 53,941 |
| Peng | eight_apical_q25 | 168 | 513,437 | 124.15 | 54,060 |
| Peng | nine_both_q25 | 168 | 506,011 | 123.47 | 53,824 |
| Tamas | seven | 112 | 441,256 | 118.21 | 159,437 |
| Tamas | eight_basal_q25 | 112 | 306,611 | 105.86 | 88,900 |
| Tamas | eight_apical_q25 | 112 | 314,329 | 103.79 | 149,114 |
| Tamas | nine_both_q25 | 112 | 281,354 | 102.32 | 110,035 |
| Tamas | seven | 168 | 1,502,475 | 195.90 | 249,128 |
| Tamas | eight_basal_q25 | 168 | 902,628 | 163.13 | 212,266 |
| Tamas | eight_apical_q25 | 168 | 897,136 | 165.11 | 257,762 |
| Tamas | nine_both_q25 | 168 | 800,981 | 148.86 | 230,369 |

The dual-q25 layout has lower projected G/C condition numbers than seven ports on both morphologies. Yet the order-168 transient ratio is 14.525× on Peng and 1.001× on Tamas. These condition numbers therefore do not provide a simple explanation of the observed difference.

### q25 port leverage

Median basis-row leverage over nine passive scenarios:

| Morphology | Layout | Order | Basal-q25 leverage | Apical-q25 leverage |
|---|---|---:|---:|---:|
| Peng | eight single-probe | 112 | 0.999987 | 0.998827 |
| Peng | eight single-probe | 168 | 0.999999995 | 0.999988825 |
| Peng | nine dual-probe | 112 | 0.999954 | 0.998539 |
| Peng | nine dual-probe | 168 | 0.999999977 | 0.999980365 |
| Tamas | eight single-probe | 112 | 0.6569997 | 0.4796983 |
| Tamas | eight single-probe | 168 | 0.8461985 | 0.6598251 |
| Tamas | nine dual-probe | 112 | 0.6016558 | 0.4591285 |
| Tamas | nine dual-probe | 168 | 0.8354788 | 0.6302985 |

The larger Peng q25 leverage does not correspond to better shared-output accuracy: Peng has the larger dual-q25 penalty while Tamas has lower q25 leverage but near-parity shared-output error. This metric alone is not an error predictor.

### Initial shift-seed allocation

All 864 initial seed records accept exactly the full port count at every expansion shift (0, 100, 1,000, 3,000, 6,000 and 10,000 Hz): 7 for seven-port, 8 for either single-q25 layout, and 9 for dual-q25. This holds for both morphologies, both orders and all nine scenarios. The metric only counts the first seed block at each shift; it does not measure later Krylov growth.

## Conclusion

The audit does not identify a causal numerical-conditioning mechanism for the morphology-dependent transient error. It does rule out two overly simple explanations: the basis is not losing orthogonality, and the dual-q25 model is not failing to seed one of its initial port directions. The projected G/C condition numbers and q25 row leverage vary, but their changes do not track the Peng-vs-Tamas transient difference in a simple way.

The next diagnostic should inspect later round-robin block Krylov growth, per-shift accepted vectors after reorthogonalization, incremental basis overlap/novelty, and frequency-domain transfer residuals on the seven shared outputs. These should be compared against the same source/output/pulse slices where Peng diverges and Tamas remains near baseline.

## Files

- `amsn-core/research/audit_prima_q25_basis_conditioning.py`
- `amsn-core/tests/test_prima_q25_cross_morphology_conditioning.py`
- `.github/workflows/amsn-prima-q25-cross-morphology-conditioning-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-CROSS-MORPHOLOGY-CONDITIONING.md`
- Detailed report: `amsn-core/research/PRIMA_Q25_CROSS_MORPHOLOGY_CONDITIONING_AUDIT_2026-11-24.md`
- Result tables: `amsn-core/results/prima_q25_cross_morphology_conditioning_2026-11-24_{models,port_leverage,shift_seeds,summary}.csv`
- Result JSON and timing log use the same stem.

## Limitations

The audit covers two individual passive linear-RC reconstructions only. It does not establish population-level or biological validity. Full Hines remains canonical, and production code/defaults are unchanged.
