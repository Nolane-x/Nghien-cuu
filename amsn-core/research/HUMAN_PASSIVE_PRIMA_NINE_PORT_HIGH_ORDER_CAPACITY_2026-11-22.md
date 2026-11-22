# Human passive PRIMA nine-port high-order basis-capacity study

**Date:** 2026-11-22 (Asia/Bangkok)  
**Implementation PR:** https://github.com/Nolane-x/Nghien-cuu/pull/4 — merged  
**Merge commit:** `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`  
**High-order matrix:** [workflow 44979673244 — 6/6 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244)  
**Core CI:** [workflow 44979673250 — 4/4 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673250)  
**Matched seven-port reference:** [workflow 44979673239 — 6/6 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673239)  
**Nine-port order 28/56/84 reference:** [workflow 44979673251 — 6/6 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673251)

## 1. Question

The previous nine-port experiment showed that adding basal/apical q25 ports while holding PRIMA order at 28/56/84 worsened the apical-q90 transient in every paired comparison against the seven-port order-84 reference. This study tested whether the regression could be overcome by allocating more basis states to the same nine-port boundary set.

The tested six-shift positive-real orders were 28, 56, 84, 112 and 168, alongside the four-shift order-56 control. The four-shift model remains a distinct baseline from the six-shift order-56 candidate.

## 2. Fixed protocol and coverage

- Morphologies: NMO_68174 cell1125, NMO_68175 cell1204, and NMO_290988 / 1094_Mohan_etal_2015.
- NEURON maximum segment lengths: 0.125 and 0.0625 µm.
- Six morphology × mesh configurations.
- Nine unique retained SWC/electrical ports: soma; basal q25/q50/q75/q90; apical q25/q50/q75/q90.
- Three current sources: soma, basal-q75 and apical-q75. The q75 source/probe locations remain one electrical port apiece.
- Ten frequencies from 0.1 Hz to 10 kHz.
- Six transients: three source locations × 2/10 ms pulses; 10 pA, 2 ms onset, 20 ms run, 0.1 ms backward-Euler timestep.
- Every transient is scored at all nine ports.
- Six model variants per configuration.

Each configuration emitted exactly **420 rows**: 60 frequency responses (6 models × 10 frequencies), 324 per-port transient rows (6 × 6 × 9), and 36 all-port aggregate rows (6 × 6). Total: **2,520 rows** over six jobs. All six logs confirm 420 rows and the expected six model IDs; all six coverage assertions passed.

## 3. Validation

- High-order matrix [44979673244](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244): 6/6 morphology × mesh jobs passed; all six artifacts uploaded.
- Core CI [44979673250](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673250): 4/4 jobs passed, including Python 3.12/3.13 test, compile/example and NEURON cross-validation jobs.
- Seven-port Schur baseline [44979673239](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673239): 6/6 jobs passed.
- Nine-port order-28/56/84 baseline [44979673251](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673251): 6/6 jobs passed.
- The audit checks Cholesky positive-definiteness of each projected conductance/capacitance pair and verifies achieved order remains below the full compartment count.
- PR #4 was merged as `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`.

The sweep is a passive linear RC reduced-order study. Full Hines remains canonical.

## 4. Aggregate results

Worst-case frequency errors are maxima across the six configurations and ten frequencies. Transient columns are NRMSE (%).

| Model | State reduction | Max Z vs Hines | Max Y vs Hines | Max Z vs NEURON | Max Y vs NEURON | Max all-port transient | Max single-port transient |
|---|---:|---:|---:|---:|---:|---:|---:|
| Four-shift order 56 control | 99.370–99.593% | 3.4854 | 1.6552 | 3.3455 | 1.5510 | 0.00439293 | 0.02619245 |
| Six-shift order 28 | 99.685–99.796% | 35.0307 | 9.1357 | 35.2070 | 9.1940 | 1.32490183 | 12.09981448 |
| Six-shift order 56 | 99.370–99.593% | 0.2196 | 0.2214 | 0.3273 | 0.3146 | 0.07309632 | 0.52309925 |
| Six-shift order 84 | 99.055–99.389% | 0.0429510 | 0.0111241 | 0.1713402 | 0.1111113 | 0.000119447 | 0.001775061 |
| Six-shift order 112 | 98.741–99.185% | 0.0002128 | 0.0002642 | 0.2032995 | 0.1191557 | 0.0000023643 | 0.0000344712 |
| Six-shift order 168 | 98.111–98.778% | 0.000000145 | 0.000000194 | 0.2033937 | 0.1194065 | 0.0000003551 | 0.0000034498 |

### Interpretation

Order 28 remains unacceptable. Order 56 is also inadequate for the enriched port set under the full transient protocol. Orders 112 and 168 reduce the nine-port passive transient error markedly while retaining at least 98.11% state reduction.

Increasing from order 112 to 168 cuts the maximum all-port transient NRMSE from 2.3643e-6% to 3.5507e-7%. The maximum individual-port transient error falls from 3.4471e-5% to 3.4498e-6%; apical-q90 is the worst individual port in these two aggregate summaries.

The internal PRIMA-versus-Hines frequency residual falls to approximately 1.45e-7% Z and 1.94e-7% Y at order 168. However, the direct comparison with native NEURON remains near 0.2034% Z and 0.1194% Y. Moving from order 112 to 168 does not improve that cross-simulator residual; it is now the limiting discrepancy in this protocol, and requires a separate investigation rather than further basis-order escalation alone.

## 5. Matched transient comparison with the seven-port order-84 reference

The common seven output ports have identical SWC node IDs across the seven- and nine-port runs. Pair keys include morphology, mesh, source, pulse width, scenario and SWC port ID. The comparison includes 7 ports × 6 scenarios × 6 configurations = **252 pairs per candidate**.

| Nine-port candidate | Improved common-port pairs | Median candidate/reference NRMSE ratio | Worst candidate/reference ratio |
|---|---:|---:|---:|
| Six-shift order 112 | 252/252 | 0.12795 | 0.87630 |
| Six-shift order 168 | 252/252 | 0.01906 | 0.87334 |

Both nine-port high-order candidates improve every matched common-port transient comparison against the existing seven-port six-shift order-84 reference. This includes soma, basal q50/q75/q90, and apical q50/q75/q90; no matched common port regressed in these paired data.

For the primary apical-q90 output alone (36 matched pairs per candidate):

| Candidate | Improved pairs | Median ratio vs seven-port order 84 | Maximum ratio |
|---|---:|---:|---:|
| Nine-port order 84 | 0/36 | 7.8139 | 28.7485 |
| Nine-port order 112 | 36/36 | 0.25658 | 0.87630 |
| Nine-port order 168 | 36/36 | 0.15774 | 0.87334 |

Thus order 112 reduces the median paired apical-q90 error by about 74.3% relative to the seven-port order-84 result, and order 168 by about 84.2%. Even the worst matched q90 pair is lower than its seven-port reference for each high-order candidate.

The paired comparisons are evidence that higher basis capacity can overcome the earlier nine-port q90 regression in this tested setup. They do **not** isolate the effect of port count at equal order: the current comparator is the seven-port order-84 baseline, not a seven-port order-112/168 run.

## 6. Order 168 versus order 112 within the nine-port set

Across all nine ports × six scenarios × six configurations, order 168 has lower per-port transient NRMSE in **324/324 matched comparisons** against order 112. The median order-168/order-112 ratio across those observations is 0.4031. The median ratio at apical-q90 is 0.6365.

This additional accuracy costs 50% more reduced states (168 versus 112). Order 112 is therefore the more economical high-accuracy candidate; order 168 is the highest-fidelity candidate among the tested orders. For the NMO_290988 partial morphology, the q90 worst case benefits particularly strongly from order 168, while the two Segev morphologies are already close to their residual floor at order 112.

The two choices should remain research presets rather than global defaults. Neither replaces full Hines as the reference.

## 7. Decisions

1. Keep full Hines canonical.
2. Keep the seven-port order-84 result as the documented previous reference.
3. Retain nine-port six-shift order 112 as the efficient high-accuracy candidate and order 168 as an optional maximum-fidelity candidate for this passive protocol.
4. Do not use order 28 or six-shift order 56 for the expanded nine-port transient requirement.
5. Do not change production defaults based on this study.
6. Treat the remaining ~0.20% Z / ~0.12% Y direct-NEURON discrepancy as a separate cross-simulator floor to investigate.

## 8. Next experiment — equal-order port-count control

To separate the effect of additional retained ports from the effect of additional basis states, run the same six configurations at **seven and nine ports using identical six-shift orders 56, 112 and 168**, with the same frequencies, source locations and six transients. The comparison must use actual achieved ranks and exact shared SWC node IDs. The central question is whether nine ports at a matched order have a material transfer/transient benefit over seven ports, or whether the same accuracy is achievable more cheaply with the seven-port basis.

Also investigate why the direct NEURON residual plateaus while the PRIMA-vs-Hines residual approaches floating-point precision. Keep geometry, source/probe interpolation, mesh and simulator effects separate; do not tune passive parameters to force agreement.

## 9. Artifacts

All six high-order artifacts were uploaded by [workflow 44979673244](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244):

- [NMO_68174 cell1125, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14737601761)
- [NMO_68174 cell1125, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14737690715)
- [NMO_68175 cell1204, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14737870431)
- [NMO_68175 cell1204, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14736949497)
- [NMO_290988 Mohan2015, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14737810288)
- [NMO_290988 Mohan2015, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244/artifacts/14737785139)

Each high-order artifact preserves its log, 420-row frequency/order/transient sweep, Schur summary and port-localization table. The NMO_290988 reconstruction is a partial dendritic morphology without an axon, not a healthy-control specimen. None of these results validate active channels, nonlinear synapses, calcium, plasticity, gene expression, metabolism, cognition or full biological completeness.
