# Handoff — PRIMA shift-distribution and order Pareto sweep

**Date:** 2026-11-22 (Asia/Bangkok)  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22  
**Workflow:** AMSN Human PRIMA Shift-Order Pareto Sweep

## Research question

The order-56 basis-transfer audit showed that a 10 kHz-extended shift set can greatly reduce 6–10 kHz impedance/admittance residuals while worsening all paired transient-output NRMSE measurements. The next step is to vary both the retained order and the distribution of positive-real expansion shifts, rather than picking a winner from only one frequency or transient metric.

## Candidate matrix

Three achieved PRIMA orders are tested: 56, 84 and 112.

Each order is crossed with three shift strategies:

- narrow_3khz: 0, 100, 1,000 and 3,000 Hz.
- extended_10khz: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- balanced_10khz: 0, 10, 100, 1,000, 3,000 and 10,000 Hz.

The balanced strategy retains the 10 kHz endpoint but replaces the 6 kHz shift with a 10 Hz shift to strengthen the low-frequency part of the basis. The design does not assume that this improves results; it is a falsifiable candidate.

## Fixed validation protocol

The same three public human morphology fixtures and nine passive parameter scenarios are used. Each candidate is freshly generated for each perturbed parameter set and compared against the corresponding full Hines cable tree.

Frequency-domain checks cover 0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz. Transient checks cover soma, basal-q75 and apical-q75 sources, 2 ms and 10 ms square pulses, 10 pA current, 2 ms onset, 20 ms total duration and 0.1 ms time step. All seven retained outputs are recorded by exact SWC node ID.

Each candidate records basis build wall time, basis storage bytes, reduced G/C matrix storage bytes and state reduction. The workflow also records process wall time, CPU time and peak RSS for each morphology. Reduced conductance and capacitance matrices must pass Cholesky positive-definiteness checks; every requested order must be achieved exactly.

## Expected coverage per morphology

- 9 candidates × 9 parameter scenarios = 81 model-summary rows.
- 81 × 9 frequencies = 729 frequency rows.
- 9 candidates × 9 scenarios × 3 sources × 2 pulse widths × 7 outputs = 3,402 per-port transient rows.

Across all three morphologies: 243 model rows, 2,187 frequency rows and 10,206 transient per-port rows.

## Interpretation guardrails

- No model is selected before the full accuracy/resource tables are inspected.
- Frequency and transient errors remain separate objectives; the order-56 result already demonstrates that high-band gains can trade against transient accuracy.
- Build time and numeric storage are candidate-specific. Process RSS is morphology/job-level and must not be presented as per-model RSS.
- Full Hines remains canonical. Production defaults stay unchanged.
- The fixtures are passive linear RC models only. They do not validate active channels, spikes, nonlinear synapses, plasticity or cognition.

## Validation state

Implementation and workflow are staged for Actions. No Pareto conclusion is claimed until all three jobs pass, all CSV row counts and exact model/parameter/source/pulse/output coverage are checked, and all artifacts are independently inspected.
