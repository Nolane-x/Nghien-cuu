# Research log — nine-port high-order PRIMA basis capacity

**Date:** 2026-11-22 (Asia/Bangkok)  
**Merged PR:** https://github.com/Nolane-x/Nghien-cuu/pull/4  
**Commit:** `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`

## Question

Can the error increase caused by adding q25 retained ports be resolved by increasing the six-shift positive-real PRIMA basis order, while preserving accuracy at the seven shared output ports?

The prior nine-port study found all 144 paired q90 comparisons worsened when moving from seven to nine ports with orders 28/56/84. This experiment therefore kept the nine-port geometry fixed and tested orders 28/56/84/112/168.

## Implementation

The optional extended sweep is parameterized by `AMSN_PRIMA_EXTENDED_ORDERS`. The default remains 28/56/84. A dedicated workflow requests 28/56/84/112/168. The change is restricted to research configuration; no production/default order was promoted.

## Matrix

Three SWC morphologies × two NEURON mesh caps; nine ports; three current sources; ten frequencies; six transient source/pulse scenarios; six model variants including the four-shift order-56 control. Each config produced 420 rows (60 frequency, 324 port transient, 36 all-port transient). Six configs yielded 2,520 rows.

## Validation evidence

- High-order workflow 44979673244: 6/6 jobs passed.
- Core CI 44979673250: 4/4 jobs passed, Python 3.12 and 3.13.
- Nine-port control 44979673251: 6/6 passed.
- Seven-port Schur control 44979673239: 6/6 passed.
- Each high-order job ran the full pytest suite, verified exact SWC record count, executed the numerical matrix, asserted exact row counts/model IDs, and uploaded CSV/log artifacts.
- The post-run local standard-library analyzer validated all six artifact files against six matching seven-port and nine-port reference files. It required exact metrics/scenario/port coverage and constant actual basis rank across frequency.

## Results

For order 112, apical-q90 error improved against nine-port order84 in 36/36 cases (median ratio 0.02216, maximum 0.44677) and against seven-port order84 in 36/36 cases (median ratio 0.25658, maximum 0.87630). For order168, corresponding ratios were 0.01411/0.44527 and 0.15774/0.87334. No q90 comparison worsened.

Shared outputs: 252 matched probe/scenario/config comparisons per candidate. Neither order112 nor order168 regressed in any of the seven shared ports; maximum ratios versus seven-port order84 were 0.87630 and 0.87334 respectively. The probe-level CSV preserves all fourteen grouped probe summaries.

Worst-case apical-q90 NRMSE across the matrix: order112 3.4471e-5%; order168 3.4498e-6%. Worst all-port transient NRMSE: 2.3643e-6% and 3.5507e-7%. Both ranks achieved exactly as requested across every config.

Trade-offs: order112 and order168 reduce state count by 98.74–99.19% and 98.11–98.78%. Their worst frequency-domain errors versus native NEURON (Z/Y 0.2033/0.1192% and 0.2034/0.1194%) are slightly above order84 (0.1713/0.1111%). Their Hines residuals are dramatically smaller. Actual CPU time and peak RSS were not measured.

## Decision

The higher-capacity basis resolves the q90 regression in the tested passive RC matrix without shared-port regressions. Order168 is the accuracy leader; order112 is a smaller compromise. Keep both opt-in research candidates only. Do not change defaults. Full Hines remains canonical, and the standard order sweep remains 28/56/84 until resource and held-out validation.

## Next work

Instrument CPU wall-time and peak RSS for basis construction, projection, frequency evaluation and transients. Compare orders84/112/168 in repeated cold/warm runs. Then test held-out morphologies and passive parameter perturbations. Keep native NEURON discrepancy distinct from Hines residual and avoid parameter fitting that merely forces simulator agreement.

This experiment concerns passive linear RC dynamics only. It does not establish active channel, nonlinear synaptic, plasticity, calcium, gene-expression, metabolic, cognitive or biological-completeness claims. NMO_290988/Mohan is partial dendrite-only morphology without axon, not a healthy-control morphology.
