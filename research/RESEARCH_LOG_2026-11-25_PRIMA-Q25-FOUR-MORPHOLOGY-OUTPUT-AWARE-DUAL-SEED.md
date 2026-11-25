# Research log — four-morphology q25 output-aware dual-seed sweep

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Accepted workflow:** [45639939767](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767)  
**Results commit:** `fe048f52d376e3d5269f80d0009eefafd01e1565`  
**Artifact:** [15035937283](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767/artifacts/15035937283)

## 1. Purpose

The accepted Peng nominal-scenario pilot showed a large reduction in q25 transient residuals when output-dual resolvent directions were added to the PRIMA state basis while preserving the canonical seven-port input selector. This confirmatory sweep tested whether the effect generalized across four established morphology strata and all nine passive parameter scenarios.

## 2. Method and exact protocol

For the passive system

[
C\dot{x}+Gx=B_7u,\qquad y=L_9x,
]

the same six positive-real primal shifts (0, 100, 1,000, 3,000, 6,000, 10,000 Hz) were used at order224. Five schedules were compared: D0 none; D1-low 0 Hz; D1-mid 1,000 Hz; D1-high 10,000 Hz; D2 1,000 + 10,000 Hz. q25 dual vectors alter V but never enter B7. The reduced G/C/input/output matrices are formed by the existing congruence projection.

The four reconstructions were NMO_03524 Jacobs, NMO_107159 Tamas, NMO_162186 Allen L2/3 and NMO_163775 Peng. Each was tested under nominal, Rm ±20%, Cm ±20%, Ra ±20% and joint ±20% passive scenarios (nine total).

The transient protocol retained the same three input sources, two pulse widths, 10-pA amplitude, 2-ms onset, dt 0.00625 ms and 20/40-ms windows. Each morphology/scenario pair ran in a fresh Python/NEURON subprocess.

## 3. Acceptance and artifact

Workflow 45639939767 completed **success** through calculation, exact read-back, Git archive and artifact upload.

- 36/36 isolated morphology/scenario workers passed.
- 19,440/19,440 case metrics; 3,240/3,240 group summaries; 360 morphology summaries; 810 scenario summaries; 90 pooled summaries; 72/72 finite-DFT identity rows; 180 basis metadata rows.
- No duplicate case keys.
- D0 exactly matched the existing production multishift PRIMA basis, projected G/C and input matrix in every worker.
- All 180 reduced G/C pairs passed Cholesky; all retained exactly seven input ports; all bases reached order224.
- Maximum basis orthogonality error 1.77636e-15.
- All 72 finite-record DFT identities passed the 2e-8 tolerance. Max full-Hines relative residual 3.28627e-12; max reduced relative residual 3.26117e-13.
- Pinned runtime: Python3.12.16, NumPy2.5.5, SciPy1.16.3, NEURON9.0.2, Haswell OpenBLAS one thread, NumPy active targets X86_V3 and baseline(X86_V2).
- Wall time 1,085.85 s; max individual worker 36.69 s.

Artifact 15035937283 is 527,486 bytes with ZIP SHA-256 `fe798929f805f3702c89a704e42e4567a9371c456bc8baf71c8d9a76f7791f84`. All nine committed result/report files were checked: local Git blob SHA-1 values computed from the downloaded artifact match the Git tree for result commit `fe048f52...`.

## 4. Aggregate q25 results

There are 864 paired q25 cases per schedule. Candidate/D0 ratios were computed case by case with exact morphology, scenario, output, source, pulse and window matching.

| Schedule | Median ratio | P90 | Worst | Improved cases |
|---|---:|---:|---:|---:|
| D1-high 10 kHz | 0.00421 | 0.904 | 9.69 | 790/864 |
| D2 1/10 kHz | 0.00424 | 1.300 | 17.50 | 730/864 |
| D1-mid 1 kHz | 0.00985 | 1.084 | 15.10 | 758/864 |
| D1-low 0 Hz | 0.01679 | 1.036 | 8.89 | 772/864 |

The D0 median q25 error across the matrix is 1.491e-8%; D1-high median candidate error is 2.053e-11%. D1-high has the strongest aggregate profile by median, P90 and number of improved q25 cases. However, the median and P90 do not mean every case improves: the worst D1-high ratio is 9.69.

## 5. Morphology-specific q25 effect

D1-high improved all 216 q25 cases in each of Tamas, Allen and Peng. Their median paired ratios were:
- Tamas: 0.00367 (D0 median 3.343e-8%; candidate 1.368e-10%).
- Allen: 0.00447 (D0 median 7.099e-9%; candidate 2.517e-11%).
- Peng: 0.0000700 (D0 median 2.383e-7%; candidate 1.686e-11%).

Jacobs is different: D0 median residual is already 1.266e-11%; D1-high candidate median is 9.646e-12%, but improves only 142/216 cases. Basal q25 improves more consistently (86/108 cases; median ratio 0.462), while apical q25 is near-neutral (56/108 improved; median ratio0.979). D1-low, D1-mid and D2 show more frequent apical regressions in Jacobs. This is the key morphology-specific exception and prevents a universal dual-seed claim.

Across all morphology/scenario/window/output q25 groups (144 per schedule), group median ratios are below one in 129 groups for D1-high, 129 for D1-low, 127 for D1-mid and 121 for D2. The worst group medians are driven by Jacobs apical-q25.

## 6. Shared-output trade-off

There are 3,024 paired shared-output cases per schedule. D0 median shared-output error is 1.436e-11%.

| Schedule | Median shared ratio | P90 ratio | Median absolute delta (pp) | Max absolute delta (pp) |
|---|---:|---:|---:|---:|
| D1-mid | 1.0086 | 2.119 | 3.99e-13 | 1.49e-10 |
| D1-high | 1.0098 | 2.032 | 5.15e-13 | 1.04e-10 |
| D1-low | 1.0115 | 2.719 | 5.76e-13 | 1.15e-10 |
| D2 | 1.0230 | 2.478 | 1.09e-12 | 1.10e-10 |

The absolute changes are very small, but shared-output fidelity is not mathematically unchanged. D1-mid minimizes the median shared-output ratio and median absolute delta. D1-high has better P90/worst shared-output ratios and smaller maximum absolute change. The shared-output response is also morphology-dependent: Peng is the main stratum with a higher shared-output median ratio under D1-high; D1-mid is slightly favorable for Peng shared outputs.

## 7. Interpretation and schedule choice

D1-high (10 kHz) is the leading **research candidate** for q25 error reduction at low seed cost. D1-mid (1 kHz) is a Pareto alternative if median shared-output stability is prioritized. D2 is not preferred in aggregate: it adds dual-seed directions without beating D1-high on q25 P90/worst-case behavior, improved-case count or shared-output median ratio.

Do not promote any schedule to production default. The Jacobs apical exception merits a separate, predeclared selective-output experiment (basal-only, apical-only and joint dual-seed controls) with holdout scenarios. A further Peng shared-output weighting study may be useful, but should not be tuned on the current full matrix and reported as confirmatory.

## 8. Limits

These are four individual morphology reconstructions, not a biological population. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 metadata says No Diameter. The study is passive linear-RC model reduction only; active channels, action potentials, synapses, plasticity, calcium signalling and biological validity are not tested. Finite-record DFT identity is checked for only the declared soma/2-ms/20-ms record under D0 and D2 for each morphology/scenario group.

Full Hines remains canonical. No production solver, retained-port default or PRIMA order default changed.
