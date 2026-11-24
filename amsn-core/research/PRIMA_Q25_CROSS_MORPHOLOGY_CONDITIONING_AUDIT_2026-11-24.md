# Cross-morphology PRIMA q25 basis conditioning audit

**Date:** 24 November 2026  
**Workflow:** [GitHub Actions run 45334425019](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019) — success  
**Result archive commit:** `7558f0bfb58296bca35bfc18dab7cb903727d793`  
**Artifact:** [prima-q25-cross-morphology-conditioning-audit](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45334425019/artifacts/14892704511)  
**Artifact SHA-256:** `12b721916eaabb1edd39da6bc2265714f4fc2178980c77292cb8f75d6d135e55`

## 1. Research question

Why does the dual-q25 layout show a 14.525× median shared-output NRMSE ratio at basis order 168 on the NMO_163775 Peng mouse morphology but only 1.001× on the independent NMO_107159 Tamas human pyramidal morphology?

This audit tests four candidate explanations using structural diagnostics:
- loss of basis orthogonality;
- poor conditioning of projected conductance/capacitance matrices;
- low representation of the additional q25 port rows in the basis;
- failure of particular expansion shifts to contribute independent initial seed directions.

It is descriptive, not a causal proof.

## 2. Experimental design

Both morphology sources were checksum-pinned and independently preflighted:
- NMO_163775 Peng mouse Control, 4,209 SWC records, SHA-256 `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`.
- NMO_107159 Tamas human pyramidal Control comparison cell, 7,228 SWC records, SHA-256 `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`.

For each morphology the audit rebuilt four matched layouts (seven, basal-q25-only, apical-q25-only, dual-q25), at basis orders 112 and 168, across nine passive parameter scenarios and six expansion shifts (0, 100, 1,000, 3,000, 6,000, 10,000 Hz). It reused the existing PRIMA builder and existing shifted-Hines / orthogonalization primitives. The production PRIMA implementation was not modified.

Metrics include:
- maximum and Frobenius error of (V^TV-I), eigenvalues and condition number of the basis Gram matrix;
- eigenvalue ranges and condition numbers of (G_r) and (C_r);
- generalized RC decay-rate minimum, maximum and dynamic range from the symmetric whitened operator (C_r^{-1/2}G_rC_r^{-1/2});
- per-port basis-row leverage (|V_{i,:}|_2^2);
- number of independent columns accepted by each initial shifted seed block.

The initial seed metric deliberately stops before the later round-robin Krylov growth.

## 3. Validation and data coverage

The corrected GitHub Actions run completed successfully:
- 4/4 focused tests passed.
- Both morphology SHA-256 checks passed.
- Both Import3D preflights passed.
- All 144 reduced-model diagnostics completed and were archived.
- Artifact upload and GitHub result commit passed.

| Dataset | Expected rows | Verified rows |
|---|---:|---:|
| Reduced-model structural metrics | 144 | 144 |
| Per-port basis leverage | 1,152 | 1,152 |
| Initial shift-seed contributions | 864 | 864 |
| Summary groups | 16 | 16 |

Runtime: 123.38 seconds wall time, 215.69 seconds user CPU, 179,728 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2.

## 4. Basis orthogonality

Across all 144 reduced models:
- maximum absolute entry of (V^TV-I): **2.22e-15**;
- basis Gram condition number range: **1.0000000000000036 to 1.0000000000000067**.

The bases are orthonormal to floating-point precision on both morphologies, all layouts and both orders. Loss of basis orthogonality is not supported as the explanation for the Peng-only order-168 residual.

## 5. Projected G/C conditioning

Condition numbers below are medians over nine passive parameter scenarios. The RC dynamic range is the ratio of maximum to minimum generalized passive decay rate.

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

At order 168, dual-q25 has slightly lower projected G/C condition numbers than seven ports on Peng, and substantially lower condition numbers on Tamas. Yet the measured transient effect differs: 14.525× on Peng versus 1.001× on Tamas. These matrix condition numbers do not track the transient anomaly in a simple way.

## 6. q25 port basis leverage

Median basis-row leverage (|V_{i,:}|_2^2) over nine passive scenarios:

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

The Peng q25 rows have leverage closer to one, despite having the larger dual-q25 shared-output penalty. The Tamas q25 rows have lower leverage but near-parity shared-output results. This rules out treating q25 row leverage alone as a predictor of the transient error.

## 7. Initial shift-seed allocation

All 864 initial seed rows accept exactly the input port count at every expansion shift:
- seven-port: 7 independent columns;
- either single-q25 layout: 8;
- dual-q25: 9.

This holds for both morphologies, both orders, all nine parameter scenarios and all six expansion shifts. Every initial shift seed accepts its full port block. The metric does not include later round-robin Krylov growth and therefore cannot explain later basis differences by itself.

## 8. Interpretation

The audit does **not** identify a causal numerical-conditioning mechanism for the Peng-only order-168 transient penalty. It does rule out two simple explanations:
1. The PRIMA basis is not losing orthogonality; (V^TV) is identity to floating-point precision.
2. No initial shift is failing to add the input-port block; every seed accepts all 7/8/9 port directions.

Projected G/C condition numbers and q25 row leverage differ by morphology, but their changes do not track the observed transient error ratios in a direct, monotonic way. In particular, Peng dual-q25 has almost the same projected G/C conditioning as seven-port at order168, while Tamas dual-q25 is materially better conditioned than Tamas seven-port and still near the baseline error.

The next useful experiment is to inspect the **later round-robin Krylov growth**: incremental vector counts by shift and block iteration, residual norms before/after reorthogonalization, overlap between shift-generated subspaces, plus frequency-response residuals at each shared output. That targets what the current seed-only diagnostic deliberately did not measure.

## 9. Reproducible files

Result stem: `prima_q25_cross_morphology_conditioning_2026-11-24`.

- `models.csv`: 144 rows of structural matrix metrics.
- `port_leverage.csv`: 1,152 rows of port-row leverage.
- `shift_seeds.csv`: 864 rows of initial per-shift seed contributions.
- `summary.csv`: 16 morphology/layout/order summary groups.
- `report.json`: run metadata, coverage and summaries.
- `.time.txt`: execution resource measurements.

Verified Git blob SHA-1:
- report JSON: `2d719f411a41d53662235f1f062912355bdee689`
- models CSV: `6889a81cab2aabb5d5313fb0b3d2ae35336869cf`
- port leverage CSV: `db44d709bd88c9663cc298c0d041e991efc9e47e`
- shift seeds CSV: `acf7de06e8089017f63c2b7fbfdc17010b356338`
- summary CSV: `c5d3c603bc2f0adece43e9d16821801c76d3c8a4`

## 10. Limitations

Only two individual morphologies are compared, both using passive linear-RC models. This is not a species/cell-type population result or biological validation. Full Hines remains canonical. No active conductances, synapses, plasticity or production solver defaults have been altered.
