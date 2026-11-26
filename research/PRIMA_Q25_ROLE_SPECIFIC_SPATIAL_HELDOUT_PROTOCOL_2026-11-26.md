# PRIMA q25 role-specific seed sweep — held-out spatial generalization protocol

**Date:** 26 November 2026  
**Status:** preregistered research-only follow-up  
**Basis order:** 224  
**Model class:** passive linear-RC

## 1. Research question

Do q25 output-dual seeds improve only the two q25 target readouts, or does the resulting reduced state space also improve predictions at independent dendritic locations that were not used as output-dual seeds and are not retained input ports?

This is a spatial generalization test, not another optimization of seed frequency or target selection.

## 2. Locked construction

Keep the original seven input ports, six primal input shifts, order-224 basis cap, 0.00625-ms backward-Euler timestep, full-Hines reference, four morphologies, nine passive parameter scenarios, three input sources, 10-pA pulse protocol, and four role-specific schedules unchanged:

- D0_none
- BASAL_10K
- APICAL_10K
- BOTH_10K

Output-dual seed vectors are still formed only from the q25 basal/apical observation selectors at 10 kHz. The four held-out readouts must never be passed to the output-dual basis builder or to the seven-port input selector.

## 3. Preregistered held-out locations

Use path-distance quantiles along the existing basal and apical dendritic domains:

| Label | Domain | Quantile |
|---|---|---:|
| basal_q10 | Basal dendrite | 0.10 |
| basal_q95 | Basal dendrite | 0.95 |
| apical_q10 | Apical dendrite | 0.10 |
| apical_q95 | Apical dendrite | 0.95 |

The mapper must resolve four distinct SWC nodes and fail closed if any location collides with one of the seven canonical shared nodes or the two q25 target nodes. The exact SWC node IDs, electrical-compartment indices, and source-file checksum are retained per worker.

These are numerical spatial readout holdouts within the four existing reconstructions, not independent biological specimens. The q10/q95 labels describe path-distance quantiles in the existing morphology mapper, not universal biological compartments.

## 4. Measurements

For each of 36 morphology/scenario groups, compare the same four schedules on 13 output rows: seven canonical shared outputs, two q25 outputs, and four held-out spatial outputs.

Keep all 3 input sources, 2 pulse widths, and 2 observation windows. Report for every matched candidate-vs-D0 pair:

- transient NRMSE (%);
- candidate/D0 error ratio;
- absolute percentage-point delta;
- better/worse paired-case counts.

Do not rank schedules using ratios alone. Retain absolute errors because some baseline errors can be close to the numerical floor.

## 5. Expected exact coverage

- 36 morphology/scenario workers.
- 22,464 case-level rows (624 per worker).
- 3,744 worker-group summary rows (104 per worker).
- 416 morphology/window summaries.
- 936 scenario/window summaries.
- 104 pooled/window summaries.
- 144 finite-record DFT identity summaries (four schedules per worker).
- 144 basis metadata rows.

The finite-record DFT identity is recomputed over all 13 observed rows for the declared soma / 2-ms pulse / 20-ms record in every worker. This is an algebraic consistency check for these simulated records, not a separate validation of every source/pulse/window combination.

## 6. Acceptance gates

- All four SWC sources match pinned SHA-256 values and morphology preflights.
- Exactly seven input ports are preserved for every schedule.
- q25 seed roles and frequencies match the predeclared schedules.
- All models reach order 224 and D0 matches production multishift PRIMA exactly.
- Projected G and C are Cholesky-positive and basis orthogonality is below 2e-12.
- The four held-out nodes are distinct from each other, the seven shared nodes and both q25 target nodes.
- All 144 finite-record identities pass the 2e-8 relative tolerance.
- All CSV read-backs, uniqueness checks and exact coverage counts pass.


## 7. Interpretation rules

- Treat the paired absolute NRMSE delta (percentage points) as the primary practical effect size when the D0 denominator is near the numerical floor; report candidate/D0 ratios as a secondary scale-free view.
- Report basal q10, basal q95, apical q10 and apical q95 separately. Do not hide a branch-specific regression inside a pooled average.
- A pooled median below 1 is not sufficient evidence of spatial generalization by itself. Inspect direction and absolute magnitude separately in all four morphology strata and at both path-distance extremes.
- If q25 target errors improve but all four held-out outputs remain unchanged or worsen, interpret the result as target-local basis specialization rather than broad spatial generalization.
- If held-out outputs improve consistently across both branch classes and most morphology strata without material regression in the seven shared outputs, this supports spatial generalization within this passive linear-RC model family only.
- Any improvement remains a numerical model-reduction result; it does not establish active-neuron, synaptic, cellular or biological generalization.

## 8. Scientific limits

This is a numerical spatial-generalization test on four individual morphology reconstructions under a passive linear-RC model. It does not establish population-level generalization, active-channel or action-potential fidelity, synaptic computation, plasticity, calcium signalling, metabolism, cognition, or biological validity. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 has no-diameter metadata and must not be described as measured-diameter data.

No production PRIMA solver, default port layout, integration method, or basis-order default is changed. Full Hines remains the canonical reference.
