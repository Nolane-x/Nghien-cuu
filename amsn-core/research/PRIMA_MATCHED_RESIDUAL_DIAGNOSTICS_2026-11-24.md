# PRIMA matched transient residual localization

**Date:** 24 November 2026  
**Status:** reproducible diagnostics over archived, validated passive-RC holdouts.  
**Scope:** decomposition of existing paired results; not a new NEURON simulation or biological validation.

## Research question

For each morphology and basis order, where do the nine-port / seven-port shared-output error ratios arise: input source, output location, pulse width or passive parameter scenario?

## Method and integrity checks

The analyzer reads each holdout's matched_shared.csv. Each row is paired at identical morphology, order, parameter scenario, source, pulse width and shared SWC node ID. The script independently recomputes the stored error ratio and absolute NRMSE difference, rejects non-finite values and duplicate keys, and verifies 378 rows per order with nine scenarios × three sources × two pulse widths × seven shared outputs.

The source/output table aggregates 18 paired observations per cell (nine scenarios × two pulse widths). Ratios are medians of paired nine-port NRMSE divided by seven-port NRMSE. NRMSE values are percentages; delta is in percentage points.

## Overall paired results by morphology and order

| Holdout | Order | Pairs | Worse / better / tie | Median ratio | P90 ratio | Max 9-port NRMSE (%) | Max |delta| (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NMO_03524 | 112 | 378 | 204/173/1 | 1 | 1.0002 | 3.15539e-08 | 1.0115e-12 |
| NMO_03524 | 168 | 378 | 189/189/0 | 1 | 1.0002 | 3.15545e-08 | 2.38744e-12 |
| NMO_107159 | 112 | 378 | 378/0/0 | 42.7181 | 87.921 | 3.95066e-05 | 3.87398e-05 |
| NMO_107159 | 168 | 378 | 214/164/0 | 1.00102 | 1.10041 | 5.45589e-07 | 3.39126e-08 |
| NMO_162186 | 112 | 378 | 377/1/0 | 8.16203 | 155.255 | 1.06552e-05 | 1.06277e-05 |
| NMO_162186 | 168 | 378 | 187/190/1 | 1 | 1.00011 | 1.45425e-07 | 5.45748e-12 |
| NMO_163775 | 112 | 378 | 378/0/0 | 78.0511 | 1461.13 | 0.000193292 | 0.00019054 |
| NMO_163775 | 168 | 378 | 347/31/0 | 14.5014 | 110.627 | 6.06567e-07 | 6.01034e-07 |

## NMO_163775 — order 168 input-source decomposition

The archived median 9/7 ratio is 14.501× overall. Each source group has 126 pairs (seven outputs × nine scenarios × two pulse widths).

| Input source | Pairs | Median 9/7 | P90 9/7 | Median 7-port (%) | Median 9-port (%) | Max 9-port (%) |
| --- | --- | --- | --- | --- | --- | --- |
| apical_q75 | 126 | 1.3981 | 7.24262 | 9.5479e-10 | 2.6541e-09 | 5.63013e-08 |
| basal_q75 | 126 | 31.9577 | 110.154 | 5.06366e-10 | 1.20662e-08 | 3.81616e-07 |
| soma | 126 | 59.0547 | 137.179 | 7.05097e-10 | 2.75406e-08 | 6.06567e-07 |

## NMO_163775 — order 168 output-location decomposition

Each output-role group has 54 pairs (three sources × nine scenarios × two pulse widths).

| Shared output | Pairs | Median 9/7 | P90 9/7 | Median 7-port (%) | Median 9-port (%) | Max 9-port (%) |
| --- | --- | --- | --- | --- | --- | --- |
| soma | 54 | 65.2122 | 148.794 | 1.24106e-09 | 3.11596e-08 | 6.06567e-07 |
| basal_q50 | 54 | 52.465 | 128.285 | 9.38745e-10 | 1.84001e-08 | 3.13808e-07 |
| basal_q75 | 54 | 46.7826 | 137.179 | 4.75983e-10 | 7.20583e-09 | 3.81475e-07 |
| basal_q90 | 54 | 45.7285 | 133.248 | 9.98453e-10 | 1.97563e-08 | 3.5937e-07 |
| apical_q50 | 54 | 21.0827 | 65.3398 | 3.91919e-10 | 6.80686e-09 | 1.31302e-07 |
| apical_q90 | 54 | 3.70023 | 25.6663 | 3.96223e-10 | 3.60082e-09 | 5.26122e-08 |
| apical_q75 | 54 | 2.983 | 21.8488 | 3.8269e-10 | 3.60755e-09 | 5.40558e-08 |

## NMO_163775 — source × output interaction

These 21 groups each have 18 paired observations. They show whether a source/output combination is more sensitive than either marginal summary alone.

| Input source | Output | Median 9/7 | Max 9/7 | Median 7-port (%) | Median 9-port (%) | Max 9-port (%) |
| --- | --- | --- | --- | --- | --- | --- |
| soma | soma | 113.558 | 155.038 | 9.95905e-10 | 6.08994e-08 | 6.06567e-07 |
| soma | basal_q50 | 98.7544 | 200.771 | 5.21697e-10 | 3.45354e-08 | 3.13808e-07 |
| soma | basal_q75 | 95.9206 | 186.304 | 6.39411e-10 | 4.16707e-08 | 3.81475e-07 |
| soma | basal_q90 | 92.5675 | 203.107 | 6.32053e-10 | 3.89217e-08 | 3.5937e-07 |
| basal_q75 | basal_q75 | 83.2466 | 206.353 | 4.38629e-11 | 2.25377e-09 | 1.19449e-08 |
| basal_q75 | soma | 78.3118 | 193.867 | 8.24857e-10 | 4.16735e-08 | 3.81616e-07 |
| basal_q75 | basal_q90 | 73.4553 | 270.422 | 5.27995e-10 | 2.6453e-08 | 2.18823e-07 |
| basal_q75 | basal_q50 | 69.3939 | 300.218 | 4.56304e-10 | 2.35865e-08 | 1.94293e-07 |
| soma | apical_q50 | 40.7288 | 108.842 | 3.88035e-10 | 1.49638e-08 | 1.31302e-07 |
| basal_q75 | apical_q50 | 27.7931 | 66.2549 | 4.99839e-10 | 9.17905e-09 | 6.09824e-08 |
| soma | apical_q75 | 16.9511 | 41.2142 | 8.70906e-10 | 7.63169e-09 | 5.40558e-08 |
| soma | apical_q90 | 9.22588 | 38.2079 | 8.87242e-10 | 7.55385e-09 | 5.26122e-08 |
| basal_q75 | apical_q75 | 8.49099 | 20.9625 | 1.13769e-09 | 4.90387e-09 | 2.20864e-08 |
| basal_q75 | apical_q90 | 4.09818 | 21.3279 | 1.14712e-09 | 4.8558e-09 | 2.14404e-08 |
| apical_q75 | soma | 3.73013 | 35.7242 | 2.38987e-09 | 1.13158e-08 | 5.63013e-08 |
| apical_q75 | basal_q75 | 2.23528 | 9.72327 | 2.45655e-09 | 8.16045e-09 | 2.26738e-08 |
| apical_q75 | basal_q50 | 1.92498 | 28.7477 | 2.37044e-09 | 6.98735e-09 | 2.04865e-08 |
| apical_q75 | basal_q90 | 1.84826 | 25.0416 | 2.73781e-09 | 8.29445e-09 | 2.16229e-08 |
| apical_q75 | apical_q50 | 1.10924 | 1.80411 | 3.48715e-10 | 4.42606e-10 | 1.52659e-09 |
| apical_q75 | apical_q90 | 1.00852 | 1.15237 | 2.80463e-11 | 2.79863e-11 | 1.36433e-10 |
| apical_q75 | apical_q75 | 1.0046 | 1.14663 | 1.28005e-11 | 1.27574e-11 | 5.44796e-11 |

## Pulse-width sensitivity at NMO_163775, order 168

Each source/pulse group has 63 pairs (nine scenarios × seven outputs).

| Input source | Pulse width | Pairs | Median 9/7 | Median 9-port (%) | Max 9-port (%) |
| --- | --- | --- | --- | --- | --- |
| apical_q75 | 2 ms | 63 | 1.43106 | 1.10897e-08 | 5.63013e-08 |
| apical_q75 | 10 ms | 63 | 1.36226 | 2.56899e-09 | 1.10896e-08 |
| basal_q75 | 2 ms | 63 | 33.0564 | 2.17186e-08 | 3.81616e-07 |
| basal_q75 | 10 ms | 63 | 29.3735 | 4.67286e-09 | 9.35709e-08 |
| soma | 2 ms | 63 | 58.5859 | 5.44693e-08 | 6.06567e-07 |
| soma | 10 ms | 63 | 59.5235 | 1.24076e-08 | 1.44528e-07 |

## Parameter-scenario sensitivity at NMO_163775, order 168

Each source/scenario group has 14 pairs (seven outputs × two pulse widths). This finite deterministic ±20% sweep is descriptive and does not establish a causal parameter effect.

| Parameter scenario | Input source | Pairs | Median 9/7 | Median 7-port (%) | Median 9-port (%) | Max 9-port (%) |
| --- | --- | --- | --- | --- | --- | --- |
| Rm_plus20 | basal_q75 | 14 | 159.345 | 2.80306e-10 | 2.03333e-08 | 1.60365e-07 |
| Rm_plus20 | soma | 14 | 147.524 | 4.36413e-10 | 3.38828e-08 | 2.53094e-07 |
| all_plus20 | soma | 14 | 118.961 | 1.29022e-09 | 9.01793e-08 | 6.06567e-07 |
| Cm_plus20 | soma | 14 | 104.885 | 7.4556e-10 | 4.12203e-08 | 3.29367e-07 |
| Ra_plus20 | soma | 14 | 103.336 | 9.59934e-10 | 3.0497e-08 | 2.70554e-07 |
| all_plus20 | basal_q75 | 14 | 86.6671 | 1.24949e-09 | 3.09006e-08 | 3.81616e-07 |
| Rm_minus20 | soma | 14 | 81.6886 | 7.07921e-10 | 1.4536e-08 | 1.22539e-07 |
| nominal | soma | 14 | 73.8033 | 4.98132e-10 | 2.19608e-08 | 1.84787e-07 |
| Cm_plus20 | basal_q75 | 14 | 73.0383 | 3.72309e-10 | 2.11386e-08 | 1.92145e-07 |
| Ra_plus20 | basal_q75 | 14 | 71.8766 | 7.63021e-10 | 1.74668e-08 | 1.58055e-07 |
| Ra_minus20 | soma | 14 | 66.1099 | 5.89635e-10 | 1.62855e-08 | 1.19854e-07 |
| Ra_minus20 | basal_q75 | 14 | 63.8012 | 4.11489e-10 | 1.19618e-08 | 8.40226e-08 |
| nominal | basal_q75 | 14 | 57.438 | 3.1395e-10 | 1.44154e-08 | 1.18731e-07 |
| Rm_minus20 | basal_q75 | 14 | 40.9612 | 7.62736e-10 | 9.55607e-09 | 8.40816e-08 |
| Cm_minus20 | soma | 14 | 30.3379 | 4.19396e-10 | 7.73462e-09 | 5.44693e-08 |
| Cm_minus20 | basal_q75 | 14 | 17.5658 | 4.40761e-10 | 5.53473e-09 | 4.07576e-08 |
| all_minus20 | soma | 14 | 10.4453 | 9.58797e-10 | 5.35916e-09 | 2.91555e-08 |
| Rm_plus20 | apical_q75 | 14 | 8.49394 | 2.02002e-10 | 3.2836e-09 | 3.08096e-08 |
| all_minus20 | basal_q75 | 14 | 6.1826 | 5.57944e-10 | 3.4188e-09 | 2.37221e-08 |
| Ra_minus20 | apical_q75 | 14 | 4.00868 | 3.58949e-10 | 2.35805e-09 | 1.59158e-08 |
| nominal | apical_q75 | 14 | 2.36423 | 1.03603e-09 | 3.0879e-09 | 2.29391e-08 |
| Rm_minus20 | apical_q75 | 14 | 1.77154 | 1.52849e-09 | 2.8364e-09 | 1.77162e-08 |
| Ra_plus20 | apical_q75 | 14 | 1.70413 | 1.82904e-09 | 3.72595e-09 | 2.67198e-08 |
| Cm_plus20 | apical_q75 | 14 | 1.67358 | 2.0921e-09 | 3.75037e-09 | 3.64733e-08 |
| all_plus20 | apical_q75 | 14 | 1.40833 | 2.94667e-09 | 5.23957e-09 | 5.63013e-08 |
| Cm_minus20 | apical_q75 | 14 | 1.34849 | 1.67309e-09 | 2.36445e-09 | 1.1542e-08 |
| all_minus20 | apical_q75 | 14 | 0.971845 | 2.48252e-09 | 2.36648e-09 | 1.23762e-08 |

## Interpretation

- The relative penalty is source-dependent: soma and basal-q75 stimulation show larger median ratios than apical-q75 stimulation in this particular passive-RC protocol.
- It is also output-dependent: soma and basal output roles show larger ratios than apical q75/q90 outputs. The interaction table shows the strongest source/output combinations.
- The overall median seven-port NRMSE is 5.95711e-10% and median nine-port NRMSE is 1.10896e-08%; maximum nine-port shared-output NRMSE is 6.06567e-07%. The absolute values remain very small, so the ratio is not evidence of a large absolute voltage error.
- The two pulse-width groups have similar order-of-magnitude median ratios; the archived data do not support claiming one pulse width alone explains the residual.
- Parameter-scenario summaries vary, but the sweep is finite and deterministic. It is not a probabilistic sensitivity analysis and does not prove causal parameter mechanisms.
- These diagnostics localize where the numerical difference appears in the tested protocol; they do not explain why the projection basis produces it. A mechanism-level explanation requires a targeted basis/port ablation or controlled perturbation.

## Research decision and next experiment

1. Do not reject the nine-port order-168 Peng candidate solely from the 14.501× ratio. Define an application-level absolute-error tolerance first; the repository has not established one.
2. Preserve absolute NRMSE and paired 9/7 ratios together. Flag comparisons whose seven-port denominator is close to the numerical floor rather than presenting the ratio alone.
3. Run a four-layout q25 ablation on the same morphology and mesh: seven canonical ports, seven plus basal-q25, seven plus apical-q25, and seven plus both q25. Match orders, shifts, scenarios, sources, pulses, dt and full-Hines shared outputs.
4. Keep full Hines canonical and leave production defaults unchanged.

## Source evidence

- **NMO_162186**: [paired shared-output CSV](../results/NMO_162186_prima_7v9port_matched_order_2026-11-23_matched_shared.csv), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520).
- **NMO_03524**: [paired shared-output CSV](../results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_matched_shared.csv), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785).
- **NMO_163775**: [paired shared-output CSV](../results/NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24_matched_shared.csv), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600).
- **NMO_107159**: [paired shared-output CSV](../results/NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24_matched_shared.csv), [validated workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588).

## Limitations

- Four single-cell morphology holdouts are not a representative biological population.
- All comparisons are passive linear-RC transient comparisons against full Hines, not active-neuron or biological validation.
- Ratios can be inflated by very small seven-port denominators; no universal application tolerance is assumed.
- This decomposition is observational within a fixed deterministic experiment matrix; it does not prove a causal mechanism.
- Mesh caps differ (0.125 µm vs 0.5 µm), so absolute cross-morphology errors are not pooled.

No production solver code or defaults are changed. No new NEURON simulation is run by this analysis.
