# PRIMA q25 four-morphology role-specific output-dual seed sweep — protocol

**Date:** 26 November 2026  
**Status:** pre-registered research experiment  
**Target:** four pinned human reconstructions — Jacobs, Allen, Tamas and Peng  
**Basis order:** 224  
**Research scope:** passive linear-RC model reduction only

## 1. Research question

The accepted Jacobs role-specific experiment found that apical-only dual seeding did not improve apical q25 readout; the D0 error was already close to the numerical floor. The same experiment showed that basal q25 was more responsive and that BOTH_10K was the best observed Jacobs compromise.

This cross-morphology experiment asks whether the role-specific response is morphology-dependent or shared across all four individual reconstructions. It does not attempt to tune a new frequency: the dual-seed frequency is fixed at 10 kHz for every non-D0 schedule so that only the target output role changes.

## 2. Fixed construction

The original seven retained input coordinates remain unchanged:

\[
C\dot{x}+Gx=B_7u,\qquad y=L_9x,\qquad
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T.
\]

The six accepted primal expansion shifts, order 224, congruent PRIMA projection, reduced backward-Euler integrator, NEURON segment cap, full-Hines reference, and transient readout protocol remain unchanged. q25 output-dual vectors are added to the state basis only; they are never inserted into the seven-port input selector.

## 3. Predeclared schedules

| Schedule | Output-dual seed rows | Dual shift |
|---|---|---:|
| D0_none | none | none |
| BASAL_10K | basal q25 only | 10,000 Hz |
| APICAL_10K | apical q25 only | 10,000 Hz |
| BOTH_10K | basal and apical q25 | 10,000 Hz |

The D0 schedule still exposes both q25 coordinates as observation rows, but contributes no output-dual seed columns. No other shifts or schedules will be added after inspection.

## 4. Morphology and scenario matrix

Run all four SWC sources with their pinned SHA-256 checksums and the nine existing passive parameter scenarios:

- nominal
- Rm −20%, Rm +20%
- Cm −20%, Cm +20%
- Ra −20%, Ra +20%
- all passive parameters −20%, all +20%

The worker protocol uses the three existing input locations (soma, basal-q75, apical-q75), two pulse widths (2 ms, 10 ms), 10 pA amplitude, 2 ms onset, 0.00625 ms time step and 20/40 ms windows. It records all seven shared outputs and both q25 outputs.

The fixed expected coverage is:

- 36 independent morphology/scenario workers
- 15,552 case-level paired error rows
- 2,592 worker-group summaries
- 288 per-morphology summaries
- 648 per-scenario summaries
- 72 pooled summaries
- 144 finite-record DFT identity rows (all four schedules in every worker)
- 144 basis metadata rows

## 5. Verification gates

Every worker must pass source checksum/preflight, exact D0 parity with production multishift PRIMA, exact seven-port input selector, nine-row output map, order 224, positive-definite reduced G and C Cholesky checks, and basis orthogonality below 2e-12.

Every schedule is checked with the finite-record BE DFT identity on the declared soma / 2 ms / 20 ms reference record. All identity residuals must remain below 2e-8. All CSVs must read back with exact expected row counts, unique case keys, and complete paired D0 values.

No numerical model or schedule is accepted solely from a relative error ratio. The report must show absolute NRMSE percentage values, percentage-point deltas, paired improvement counts and baseline floor diagnostics alongside ratios.

## 6. Interpretation limits

These are four individual human reconstructions, not a biological population. The models are passive linear-RC approximations. Active channels, action potentials, synapses, plasticity, calcium signalling and biological validity are out of scope. A role-specific effect in this study is morphology-specific evidence only. No production solver, default retained-port layout or default PRIMA order is changed; full Hines remains canonical.
