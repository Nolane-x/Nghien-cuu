# Handoff — PRIMA basis-transfer protocol robustness

**Date:** 2026-11-22 (Asia/Bangkok)  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22  
**Purpose:** Extend the existing passive parameter sensitivity audit with persisted, independently inspectable results for the extended 6/10 kHz basis and source/pulse diversity.

## Why this experiment exists

The validated 2026-11-21 parameter audit tested Rm, Cm and Ra perturbations of ±20% on three human morphology fixtures. It compared a frozen nominal 56-state basis against a freshly generated 56-state basis. The previous research log then identified an open question: does extending PRIMA expansion shifts through 6 and 10 kHz improve the residual above the original 3 kHz band?

This branch adds a separately versioned experiment rather than rewriting the earlier historical result.

## Fixed design

Three morphology records:
- NMO_68174_cell1125 — 12,410 SWC records.
- NMO_68175_cell1204 — 13,758 SWC records.
- NMO_290988_Mohan2015 — 8,903 SWC records; a partial dendritic reconstruction with no axon, not a healthy-control sample.

Nine parameter scenarios: nominal; Rm ±20%; Cm ±20%; Ra ±20%; all parameters -20%; all parameters +20%.

Three order-56 model construction paths:
1. Frozen nominal basis, generated using 0/100/1,000/3,000 Hz shifts and reprojected onto each target parameter set.
2. Fresh target basis, same order and same 0/100/1,000/3,000 Hz shifts.
3. Fresh target basis, same requested order but 0/100/1,000/3,000/6,000/10,000 Hz shifts.

Frequency comparison: nine points from 0.1 Hz through 10 kHz against the full perturbed Hines reference.

Transient protocols: three current-injection source locations (soma, basal-q75, apical-q75) × two square-pulse widths (2 ms and 10 ms). Each is 10 pA, onset 2 ms, 20 ms total duration, dt 0.1 ms. Every retained output port is recorded and paired by exact SWC node ID.

## Expected coverage per morphology

- Model audit: 9 scenarios × 3 model variants = 27 rows.
- Frequency: 9 scenarios × 3 variants × 9 frequencies = 243 rows.
- Transient: 9 scenarios × 3 variants × 3 source sites × 2 pulse widths × 7 output ports = 1,134 rows.

Across the three morphologies the expected total is 81 model rows, 729 frequency rows and 3,402 transient-port rows.

Every model must pass Cholesky checks on both reduced conductance and capacitance matrices. These checks establish positive definiteness for each saved model; they do not establish response accuracy, which is reported separately against full Hines.

## Interpretation guardrails

- This is a passive linear RC sensitivity experiment, not active electrophysiology.
- The fresh extended-shift basis must not be presumed better before measured results are read.
- The frozen and fresh models share the same requested order; results isolate basis reuse/rebuild/shift selection at fixed order, not the effect of increasing order.
- Parameter perturbations are deterministic numerical stress cases, not measured biological ranges.
- Keep full Hines canonical and production defaults unchanged.
- Do not compare against NEURON as if it were the same error target: this experiment reports reduced PRIMA versus the corresponding perturbed Hines tree.

## Validation status

Protocol, implementation and workflow are staged for CI. No numerical result is claimed in this handoff. Results become validated only after all three jobs pass, all artifacts are inspected, exact row counts are confirmed and aggregate analysis is committed.
