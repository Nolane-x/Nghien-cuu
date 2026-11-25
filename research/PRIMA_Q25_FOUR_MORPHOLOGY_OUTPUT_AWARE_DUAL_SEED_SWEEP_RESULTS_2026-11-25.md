# PRIMA q25 four-morphology output-aware dual-seed sweep — results

**Date:** 25 November 2026  
**Status:** accepted research result; 4 morphology strata × 9 passive parameter scenarios  
**Workflow:** [45639939767](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767) — complete success  
**Results commit:** [fe048f52d376e3d5269f80d0009eefafd01e1565](https://github.com/Nolane-x/Nghien-cuu/commit/fe048f52d376e3d5269f80d0009eefafd01e1565)  
**Artifact:** [15035937283](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767/artifacts/15035937283), 527,486 bytes  
**Artifact ZIP SHA-256:** `fe798929f805f3702c89a704e42e4567a9371c456bc8baf71c8d9a76f7791f84`

## 1. Executive result

The first four-morphology, nine-scenario validation of output-aware dual-seed PRIMA completed successfully. The central numerical result is **strong but not universal**:

- Adding sparse q25 output-dual seeds to the state basis strongly reduces q25 transient error in Tamas, Allen and Peng across essentially every source/pulse/window/scenario case.
- Jacobs is a real exception. Its D0 q25 residuals are already close to the numerical floor; basal q25 often improves, while apical q25 frequently worsens, particularly for the 1-kHz and two-band schedules.
- The seven shared outputs change only slightly in absolute error. Their relative ratios can look larger because D0 residuals are extremely small. Some shared-output cases improve and others worsen.
- Among the predeclared schedules, **D1-high (10 kHz)** has the strongest aggregate q25 profile: the lowest median q25 candidate/D0 ratio, the best q25 P90, the highest count of improved q25 cases, and only two independent output-dual seed columns. D1-mid (1 kHz) has the smallest median shared-output ratio increase and remains a useful alternative. D2 (1/10 kHz) does not improve the aggregate trade-off enough to justify its extra seed cost.

This result supports output-aware basis enrichment as a promising **passive linear-RC numerical method**. It does not justify changing production PRIMA defaults, and it does not establish biological validity.

## 2. What was tested

The system remains

[
C\dot{x}+Gx=B_7u,\qquad y=L_9x,
]

where (B_7) is the original seven-port current-input selector and (L_9) observes seven shared outputs plus basal-q25 and apical-q25.

For selected dual shifts (sigma=2pi f), the basis includes columns of

[
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T
]

alongside the six established primal input shifts. The final reduced operators remain congruent:

[
G_r=V^TGV,\quad C_r=V^TCV,\
B_r=V^TB_7,\quad L_{9,r}=L_9V.
]

The q25 coordinates influence the state basis but are never added to (B_7). Each schedule is therefore still a **seven-input-port** model, not a nine-input-port model.

### Fixed protocol

| Dimension | Fixed value |
|---|---|
| Morphologies | NMO_03524 Jacobs; NMO_107159 Tamas; NMO_162186 Allen; NMO_163775 Peng |
| Passive scenarios | nominal; Rm ±20%; Cm ±20%; Ra ±20%; all ±20% |
| Basis order | 224 |
| Primal input shifts | 0, 100, 1,000, 3,000, 6,000, 10,000 Hz |
| Input ports / output rows | 7 / 9 |
| Sources | soma, basal-q75, apical-q75 |
| Current pulses | 10 pA; onset 2 ms; widths 2 and 10 ms |
| Timestep | 0.00625 ms |
| Windows | 20 and 40 ms |
| NEURON segment cap | 0.5 µm |
| Runtime | Python 3.12.16; NumPy 2.5.5; SciPy 1.16.3; NEURON 9.0.2 |
| BLAS / SIMD | Haswell OpenBLAS, 1 thread; NumPy X86_V3 + baseline(X86_V2) |

Four checksum-pinned individual reconstructions were used. Their SWC source hashes and preflights all passed. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 metadata says No Diameter.

### Five predeclared schedules

| Schedule | q25 dual shifts | Initial independent dual columns |
|---|---:|---:|
| D0 — control | none | 0 |
| D1-low | 0 Hz | 2 |
| D1-mid | 1,000 Hz | 2 |
| D1-high | 10,000 Hz | 2 |
| D2-mid-high | 1,000 and 10,000 Hz | 3–4 |

D2 sometimes has three rather than four accepted initial dual columns because one proposed direction is linearly dependent after orthogonalization. All schedules reached order224 and retained exactly seven input ports.

## 3. Acceptance and reproducibility

All 36 morphology/scenario workers passed. The global expected and read-back counts were exact:

| Evidence | Expected | Read back |
|---|---:|---:|
| Morphology × scenario workers | 36 | 36 |
| Case metrics | 19,440 | 19,440 |
| Worker group summaries | 3,240 | 3,240 |
| Per-morphology summaries | 360 | 360 |
| Per-scenario summaries | 810 | 810 |
| Pooled summaries | 90 | 90 |
| Finite-record DFT identities | 72 | 72 |
| Basis/schedule metadata rows | 180 | 180 |

There were no duplicate case keys. Every worker asserted exact D0 equality against the existing production multishift PRIMA basis, projected G/C and input matrix. All 180 metadata rows report order224 and unchanged seven-port input selectors.

Numerical checks:
- Maximum basis orthogonality error: (1.77636\times10^{-15}).
- Reduced-G condition numbers: (3.41\times10^5) to (4.18\times10^6).
- Reduced-C condition numbers: 62.94 to 338.30.
- All 180 reduced G/C pairs passed Cholesky positive-definiteness checks.
- All 72 finite-record BE DFT identities passed the (2\times10^{-8}) tolerance.
- Maximum full-Hines DFT identity relative residual: (3.28627\times10^{-12}).
- Maximum reduced-model DFT identity relative residual: (3.26117\times10^{-13}).

The DFT identity sample is deliberately limited to the declared soma / 2-ms pulse / 20-ms record for D0 and D2 in each morphology/scenario group. It is not a complete frequency audit of every case.

Runtime: 1,085.85 s wall time; 1,007.71 s accumulated worker time; slowest individual worker 36.69 s. The exact pinned Haswell/NumPy dispatch contract passed.

## 4. Aggregate q25 output accuracy

Each schedule has 864 matched q25 cases: 4 morphologies × 9 scenarios × 2 windows × 6 source/pulse records × 2 q25 outputs. Ratios are paired against D0 for the exact same morphology, scenario, output, source, pulse and window.

| Schedule | Median candidate/D0 ratio | P90 ratio | Worst ratio | Cases improved | Median D0 NRMSE (%) | Median candidate NRMSE (%) |
|---|---:|---:|---:|---:|---:|---:|
| D1-high, 10 kHz | 0.00421 | 0.904 | 9.69 | 790 / 864 (91.4%) | 1.491e-8 | 2.053e-11 |
| D2, 1/10 kHz | 0.00424 | 1.300 | 17.50 | 730 / 864 (84.5%) | 1.491e-8 | 2.107e-11 |
| D1-mid, 1 kHz | 0.00985 | 1.084 | 15.10 | 758 / 864 (87.7%) | 1.491e-8 | 2.764e-11 |
| D1-low, 0 Hz | 0.01679 | 1.036 | 8.89 | 772 / 864 (89.4%) | 1.491e-8 | 3.687e-11 |

D1-high has the best aggregate q25 profile: lowest median ratio, P90 below one, and the highest number of improved paired cases. D2 has nearly the same median ratio but a worse P90 and worst-case ratio, fewer improved cases, and more initial dual directions.

### Morphology-specific q25 results

| Morphology | D0 median NRMSE (%) | D1-high median NRMSE (%) | D1-high median ratio | D1-high improved cases |
|---|---:|---:|---:|---:|
| Tamas NMO_107159 | 3.343e-8 | 1.368e-10 | 0.00367 | 216 / 216 |
| Allen NMO_162186 | 7.099e-9 | 2.517e-11 | 0.00447 | 216 / 216 |
| Peng NMO_163775 | 2.383e-7 | 1.686e-11 | 0.0000700 | 216 / 216 |
| Jacobs NMO_03524 | 1.266e-11 | 9.646e-12 | 0.726 | 142 / 216 |

For Tamas, Allen and Peng, D1-high improved both q25 outputs in every source/pulse/window/scenario case. The largest effects are in Peng and Tamas, whose D0 residuals were substantially higher than the resulting dual-seed residuals.

Jacobs behaves differently. Its D0 q25 residual is already around (10^{-11}\%). D1-high improves basal q25 in 86/108 cases, but apical q25 in only 56/108 cases. The apical median paired ratio is 0.979 (near neutral), while several individual scenario/window groups worsen. D1-mid and D2 are less robust on Jacobs apical output.

Across all q25 morphology/scenario/window/output groups (144 groups per schedule), the group median candidate/D0 ratio was below one in:
- D1-high: 129/144 groups.
- D1-low: 129/144.
- D1-mid: 127/144.
- D2: 121/144.

The remaining adverse groups are concentrated mainly in Jacobs apical-q25. This is why the aggregate improvement must not be described as universal.

## 5. Effect on the seven shared outputs

There are 3,024 shared-output cases per schedule: four morphologies × nine scenarios × two windows × six source/pulse records × seven shared outputs.

| Schedule | Median candidate/D0 ratio | P90 ratio | Worst ratio | Median absolute delta (percentage points) | Maximum absolute delta (percentage points) |
|---|---:|---:|---:|---:|---:|
| D1-mid | 1.0086 | 2.119 | 16.71 | (3.99\times10^{-13}) | (1.49\times10^{-10}) |
| D1-high | 1.0098 | 2.032 | 10.58 | (5.15\times10^{-13}) | (1.04\times10^{-10}) |
| D1-low | 1.0115 | 2.719 | 22.60 | (5.76\times10^{-13}) | (1.15\times10^{-10}) |
| D2 | 1.0230 | 2.478 | 18.65 | (1.09\times10^{-12}) | (1.10\times10^{-10}) |

The D0 median shared-output transient NRMSE is (1.436\times10^{-11}\%). Candidate medians remain around (1.6\times10^{-11}\%)–(1.8\times10^{-11}\%). The absolute changes are tiny in percentage-point terms, but the ratios show that some shared-output residuals are redistributed upward and others downward.

This is a genuine trade-off, not a free improvement. D1-mid has the smallest median shared-output ratio and median absolute delta, while D1-high has the lower P90 and smaller maximum shared-output absolute delta. D2 has the largest median shared-output ratio increase.

There is also morphology dependence: under D1-high the shared-output median paired ratio is about 0.983 in Jacobs, 1.004 in Tamas, 1.004 in Allen, and 1.331 in Peng. D1-mid is slightly below one for Peng shared outputs (about 0.982), whereas D1-high is stronger on q25 outputs. Because shared-output D0 residuals are near (10^{-11}\%), these ratios should be interpreted alongside absolute deltas.

## 6. Schedule decision

**D1-high (10 kHz) is the strongest current research candidate**, not a production default:
- It uses only two independent dual-seed directions.
- It has the best aggregate q25 median ratio and P90.
- It improves all 648 q25 cases in Tamas, Allen and Peng.
- Its overall shared-output median ratio is close to one, and its P90/worst shared ratio and maximum absolute shared-output delta are better than the other schedules in this sweep.

**D1-mid (1 kHz) should remain as a Pareto alternative** if the priority is minimizing median shared-output change. Its q25 improvement is weaker but still strong in Tamas, Allen and Peng; it is slightly more favorable for Peng's shared outputs.

**D2 (1/10 kHz) is not preferred in aggregate**: it requires more independent dual directions yet has worse q25 P90/worst-case ratios, fewer improved q25 cases, and a larger shared-output median ratio than D1-high.

The Jacobs apical exception prevents a universal recommendation. A future refinement should investigate morphology-specific output weighting or a selective basal/apical dual schedule, but such optimization must be predeclared and validated on holdout scenarios rather than tuned on the current results.

## 7. Artifact and Git integrity

- Canonical workflow [45639939767](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767) passed all steps, including all 36 workers, exact global read-back, DFT identities, Git commit and artifact upload.
- Results commit: `fe048f52d376e3d5269f80d0009eefafd01e1565`.
- Artifact [15035937283](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767/artifacts/15035937283), 527,486 bytes; ZIP SHA-256 `fe798929f805f3702c89a704e42e4567a9371c456bc8baf71c8d9a76f7791f84`.
- All nine numerical/report files in the artifact were downloaded; each local Git blob SHA-1 matches the blob recorded in the result commit.

The complete case matrix, grouped summaries, finite-DFT identities, 180 basis metadata records and report JSON are under `amsn-core/results/` with prefix `prima_q25_four_morphology_output_aware_dual_seed_order224_2026-11-25`.

## 8. Limits and next steps

This study covers four individual morphology reconstructions and nine passive parameter scenarios. It is not a biological population sample. Allen is an epilepsy-surgery specimen; Peng metadata says No Diameter. The model is passive linear-RC only; it does not test active channels, action potentials, synapses, plasticity, calcium signalling or biological computation.

Next:
1. Keep D1-high and D1-mid as research candidates; do not change defaults.
2. Investigate the Jacobs apical-q25 exception with a predeclared selective-output schedule and a holdout analysis.
3. Consider a targeted output-weighting experiment for Peng shared outputs, since D1-mid is more favorable there than D1-high.
4. If a research API is added later, expose schedule choice explicitly and preserve the exact seven-port input selector.
5. Only after broader validation should any production integration be considered.

Full Hines remains the canonical solver. No production PRIMA solver, retained-port default or basis-order default changed.
