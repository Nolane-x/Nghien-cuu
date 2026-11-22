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

## Validated result — 2026-11-22

Actions run 44990898080 completed with **3/3 successful morphology jobs**. Each ran the full AMSN test suite, used pinned NEURON 9.0.2 and uploaded model, frequency and transient CSVs.

Coverage validated from all three artifacts:
- 81 model audit rows; all requested/achieved order 56; all 81 Cholesky checks passed.
- 729 frequency rows across nine frequencies and nine parameter cases.
- 3,402 transient per-port rows across three source sites, two pulse widths and seven output nodes.
- 1,134 exact-paired transient output conditions across model variants.

The high-band extended basis improves every matched case at 6 kHz and 10 kHz for both Z and Y (27/27 per metric/frequency), with median extended/fresh-3k ratios of 0.4678/0.5059 at 6 kHz and 0.2927/0.3124 at 10 kHz. But it worsens transient per-port NRMSE in all 1,134 paired comparisons; median error ratio is 4.052× (P90 6.519×). It must not replace the 3 kHz basis as a general-purpose passive model.

Full report: amsn-core/research/HUMAN_PRIMA_BASIS_TRANSFER_PROTOCOL_ROBUSTNESS_2026-11-22.md. Reproducer: amsn-core/research/analyze_human_prima_basis_transfer_protocol_robustness.py. Summary tables and provenance manifest are in amsn-core/results/.

## Decision and next step

Retain all three basis constructions as research candidates with declared use domains. Keep Hines canonical; no production defaults changed. Next compare order 56/84/112 with narrow, extended and balanced shifts under the same parameter/source/pulse matrix, then construct a Pareto frontier across Z/Y bands, transient NRMSE, CPU and RSS. Validate the leading candidates on a held-out morphology.
