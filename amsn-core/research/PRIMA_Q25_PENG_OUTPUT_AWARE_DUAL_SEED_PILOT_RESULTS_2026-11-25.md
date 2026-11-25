# PRIMA q25 output-aware dual-seed pilot — Peng NMO_163775

**Date:** 25 November 2026  
**Status:** accepted single-morphology numerical pilot; broader morphology/scenario validation remains required  
**Workflow:** [45636631081](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081) — complete success  
**Results commit:** [22ba7b6994c871d3784f5abf15a2fe9311abe60d](https://github.com/Nolane-x/Nghien-cuu/commit/22ba7b6994c871d3784f5abf15a2fe9311abe60d)  
**Artifact:** [15033336785](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081/artifacts/15033336785), 77,205 bytes  
**Artifact ZIP SHA-256:** `a19c928f99eb361300a6f5c8e793550e3cc1854dd177ed4739271ba459d5a95b`

## 1. Executive finding

The pilot demonstrates that the q25 voltage outputs can be substantially improved by adding output-dual resolvent vectors to the PRIMA **state basis**, while leaving the reduced input selector at its original seven current-injection ports.

At order 224, all four dual-seed schedules lowered the transient NRMSE of **both q25 outputs in all 24 matched q25 cases** (two output locations × six source/pulse records × two windows). Across these 24 cases, the median q25 error fell from (5.16\times10^{-7}\%) under the seven-port primal control to (0.99\times10^{-11}\%)–(2.08\times10^{-11}\%\), depending on the dual schedule. The median paired candidate/D0 error ratios were (1.60\times10^{-5})–(4.11\times10^{-5}), equivalent to roughly 24,000–62,000× lower residuals at the median. Even the worst q25 paired ratio in each schedule was below 0.0052.

This is a strong **numerical proof of concept**, but not yet a practical or biological claim. The D0 q25 residuals were already extremely small in absolute terms. The seven shared outputs also began near the numerical floor; dual enrichment changes their relative ratios, but their absolute transient errors remain around (10^{-11}\%\). The next decision must therefore be based on all outputs, absolute deltas, multiple morphologies and passive scenarios—not q25 ratios alone.

## 2. Mathematical treatment and fixed input boundary

The passive system is

[
C\dot{x}+Gx=B_7u,\qquad y_q=L_qx,
]

where (B_7) selects the canonical seven retained input coordinates and (L_q) selects basal-q25 and apical-q25 observations.

For each selected dual shift \(\sigma=2\pi f\), the prototype adds columns of

[
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T
]

to the state basis alongside the six conventional primal input shifts. The final projection remains congruent:

[
G_r=V^TGV,\quad C_r=V^TCV,\quad
B_r=V^TB_7,\quad L_{q,r}=L_qV.
]

Thus q25 coordinates influence the basis directions but are **not added to the current-input selector**. This is a seven-input-port, nine-output-row model—not a nine-input-port model.

The runner asserts exact equality of the D0 basis, projected G/C and input matrix against the existing production multishift PRIMA builder. The D0 run completed successfully, so this parity assertion passed on the actual Peng morphology, not only the small unit-test fixture.

## 3. Protocol

| Setting | Fixed value |
|---|---|
| Morphology | Neuromorpho NMO_163775, Peng mouse Control |
| SWC records | 4,209 |
| SWC SHA-256 | `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f` |
| q25 nodes | basal SWC node 224; apical SWC node 4096 |
| Shared output nodes | 1, 144, 3926, 4180, 40, 4104, 3948 |
| Passive scenario | nominal only |
| Basis order | 224 |
| Primal input shifts | 0, 100, 1,000, 3,000, 6,000, 10,000 Hz |
| Input ports | original seven |
| Output rows | seven shared + two q25 |
| Sources | soma, basal-q75, apical-q75 |
| Current | 10 pA, onset 2 ms, pulse widths 2 and 10 ms |
| Timestep | 0.00625 ms |
| Windows | 20 and 40 ms |
| NEURON segment cap | 0.5 µm |

Five schedules were declared before the run:

| Schedule | Output-dual shifts | Initial dual seed columns |
|---|---:|---:|
| D0 — control | none | 0 |
| D1-low | 0 Hz | 2 |
| D1-mid | 1,000 Hz | 2 |
| D1-high | 10,000 Hz | 2 |
| D2-mid-high | 1,000 and 10,000 Hz | 4 |

Each primal shift seeded seven input columns (42 total across six shifts). The actual basis order remained 224 in all five schedules. The output-dual blocks added two or four initial columns; the original seven-port input matrix retained shape (224\times7).

## 4. q25 output accuracy

The table pools both q25 roles, six source/pulse records and both windows (24 matched cases per schedule). Errors are transient NRMSE in percent. Ratios are paired against the same D0 output/source/pulse/window case.

| Schedule | Median q25 error (%) | Median ratio to D0 | P90 ratio | Worst ratio | q25 cases improved |
|---|---:|---:|---:|---:|---:|
| D0 | 5.162e-7 | 1.000 | 1.000 | 1.000 | reference |
| D1-low | 1.840e-11 | 1.924e-5 | 8.975e-4 | 2.859e-3 | 24/24 |
| D1-mid | 2.079e-11 | 4.115e-5 | 6.423e-4 | 1.826e-3 | 24/24 |
| D1-high | 9.924e-12 | 1.659e-5 | 1.043e-3 | 5.169e-3 | 24/24 |
| D2-mid-high | 1.138e-11 | 1.596e-5 | 1.058e-3 | 3.714e-3 | 24/24 |

The best median absolute q25 error is D1-high, with D2-mid-high close behind. D2 has a slightly lower median paired ratio, but its tail is not better than D1-low or D1-mid. The schedules therefore do not form a single unambiguous winner.

Per q25 location, the median errors by window are:

| q25 output | Window | D0 | D1-low | D1-mid | D1-high | D2-mid-high |
|---|---:|---:|---:|---:|---:|---:|
| Basal | 20 ms | 4.391e-7 | 2.543e-11 | 2.170e-11 | 9.386e-12 | 1.090e-11 |
| Basal | 40 ms | 7.718e-7 | 2.547e-11 | 2.245e-11 | 1.037e-11 | 1.345e-11 |
| Apical | 20 ms | 2.643e-7 | 1.701e-11 | 1.761e-11 | 1.347e-11 | 9.211e-12 |
| Apical | 40 ms | 4.861e-7 | 1.836e-11 | 1.795e-11 | 1.334e-11 | 1.148e-11 |

## 5. Effect on the seven shared outputs

The seven shared outputs contain 84 matched cases per schedule across both windows (seven outputs × six source/pulse records × two windows). Their baseline errors are already very small.

| Schedule | Median shared-output error (%) | P90 error (%) | Maximum error (%) | Median paired ratio to D0 | Maximum absolute paired delta (percentage points) |
|---|---:|---:|---:|---:|---:|
| D0 | 1.230e-11 | 1.832e-11 | 3.798e-11 | 1.000 | 0 |
| D1-low | 1.408e-11 | 3.997e-11 | 6.010e-11 | 1.103 | 3.395e-11 |
| D1-mid | 1.843e-11 | 2.675e-11 | 4.629e-11 | 1.280 | 2.453e-11 |
| D1-high | 1.631e-11 | 3.543e-11 | 4.991e-11 | 1.758 | 2.612e-11 |
| D2-mid-high | 1.388e-11 | 6.197e-11 | 7.732e-11 | 1.398 | 6.782e-11 |

Relative ratios can look large because D0 shared-output errors are near zero. The absolute changes are between roughly (10^{-13}\) and (10^{-11}\) percentage points. This is a measurable redistribution of approximation error, but it is not evidence of a material loss of shared-output fidelity at ordinary engineering tolerances. It should still be tracked as the study expands.

A first trade-off reading:
- D1-low uses only two dual seed columns and has the smallest median shared-output ratio increase; it is a conservative candidate.
- D1-high gives the lowest median q25 absolute error, but has a larger median relative change on shared outputs.
- D2 is marginally best on the pooled q25 median ratio but uses twice as many dual seed columns as a single-shift schedule and has the largest maximum shared-output absolute delta.
- D1-mid has the smallest worst-case q25 ratio and a relatively small maximum shared-output delta, despite a weaker q25 median.

No schedule is promoted as a default from this one nominal case.

## 6. Numerical and passivity checks

All five models:
- reached order 224;
- retained exactly the original seven input ports;
- passed Cholesky factorization of reduced G and C;
- had basis orthogonality error between (9.99\times10^{-16}) and (1.55\times10^{-15});
- had reduced-C condition numbers about 125.47–125.54 and reduced-G condition numbers about (5.251\times10^5)–(5.258\times10^5).

The finite-record backward-Euler DFT identity was checked over 1,601 frequency bins for the predeclared soma, 2-ms pulse, 20-ms record under D0 and D2-mid-high:
- full-Hines maximum relative identity residual: (3.3615\times10^{-13});
- reduced D0 residual: (1.0969\times10^{-13});
- reduced D2 residual: (2.2534\times10^{-13});
- declared tolerance: (2\times10^{-8}).

Both identity checks passed. This identity audit is deliberately limited to one input record and two schedules; it is not a complete frequency audit of all 540 cases.

## 7. Reproducibility and archive integrity

Canonical workflow [45636631081](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081) completed success through:
- pinned runtime and Haswell one-thread OpenBLAS checks;
- active NumPy dispatch check (`X86_V3`, `baseline(X86_V2)`);
- compileall and five focused unit tests;
- the actual Peng dual-seed pilot;
- 540 case rows and 90 summary rows, both read back exactly;
- Git commit and artifact upload.

Runtime was 28.82 seconds. The archived artifact contains six files: the Peng SWC and preflight, pilot case CSV, summary CSV, report JSON and timing file. Independently recomputed ZIP SHA-256 matches GitHub's artifact digest. Per-file SHA-256 values and Git blob IDs are stored in the companion manifest.

An overlapping rerun [45636849975](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636849975) also completed the numerical calculation and coverage checks, but its duplicate Git archival step encountered add/add conflicts on the report and timing files because the canonical successful run had already committed them. It uploaded no artifact and is not the accepted source. The clean successful run 45636631081 is canonical.

## 8. Interpretation limits

This pilot covers one individual mouse morphology and one nominal passive parameter scenario. It does not establish robustness across the nine passive scenarios or the four morphology strata. The model is passive linear-RC; no active channels, action potentials, synapses, plasticity, calcium signalling or biological validity are tested. The q25 residuals in D0 were already extremely small, so the large relative improvement should not be confused with a large practical improvement in a physical measurement.

Full Hines remains canonical. No production solver, retained-port default or PRIMA order default changed.

## 9. Next validation step

Expand the experiment to all four morphology strata and all nine passive parameter scenarios, retaining order 224 and the same six primal shifts. Keep D0, D1-low, D1-mid, D1-high and D2-mid-high initially so the trade-off is not prematurely optimized to Peng. Require:
1. bitwise D0 parity with existing multishift PRIMA for every morphology/scenario;
2. exactly seven input ports and nine independent output rows for every treatment;
3. positive-definite reduced G/C, orthogonality, rank/condition diagnostics and source checksums;
4. transient metrics and absolute deltas for all seven shared outputs and both q25 outputs;
5. exact case/summary read-back counts and a predeclared finite-DFT identity sample for every morphology/scenario under D0 and D2;
6. separate morphology/scenario strata in the result report.

Only after that matrix is complete should any schedule be proposed as a generally useful output-aware PRIMA option.
