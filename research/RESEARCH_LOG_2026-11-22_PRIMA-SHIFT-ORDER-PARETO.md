# Research log — PRIMA shift distribution × order Pareto sweep

**Date:** 2026-11-22  
**Pull request:** #7  
**Actions run:** 45002816664  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22

## Validated matrix

All three jobs succeeded after the full AMSN test suite. Three morphology fixtures were evaluated across nine candidate models (orders 56, 84, 112 × narrow-3k, extended-10k, balanced-10k shifts) and nine passive-parameter scenarios.

The complete matrix produced 243 model records, 2,187 frequency records and 10,206 transient per-port records. Exact requested/achieved orders and all 243 Cholesky positive-definiteness checks passed. All three artifact SHA-256 digests were checked against GitHub metadata.

## Main findings

- Order112_extended_10khz had the smallest 3/6/10 kHz impedance and admittance residuals. At 10 kHz, median Z/Y residuals were 4.681e-6% / 1.390e-5%.
- Versus order112_narrow_3khz, it lowered median 10 kHz Z/Y residual by 41.7× / 44.8×, while median transient NRMSE increased only 1.38% and the maximum was effectively unchanged.
- Order84_narrow_3khz delivered very low transient errors with less numeric storage, but its median 10 kHz Z/Y residual was 0.006487% / 0.015528%.
- Order56_narrow_3khz is the smallest candidate but has the largest errors among narrow-shift strategies.
- Balanced 10 kHz allocation did not dominate the narrow or extended strategies; it makes different low-/mid-/high-frequency trade-offs.
- All nine candidates remain on the 19-objective Pareto frontier. This is a multi-objective outcome, not evidence that all choices are equivalent.

## Resource observations

Median candidate-specific numeric storage was about 5.35 MB at order 56, 8.05 MB at order 84 and 10.79 MB at order 112. Median basis-build time rose from about 1.02 s to 1.57 s and 2.14 s respectively. These figures are per-candidate numerical arrays/build-time summaries, not total process RSS.

Whole-job peak RSS varied by morphology from 221.9 MB to 321.9 MB. Whole-job wall time ranged from 265 to 397 seconds and included all 81 basis builds, frequency solves and transient reference comparisons for that morphology.

## Decision and next steps

Keep Hines canonical and do not change production defaults. Use order112_extended_10khz as the strongest high-fidelity passive candidate and order84_narrow_3khz as the lower-storage transient-oriented candidate for further validation, not as production defaults. Next, validate both on a held-out human morphology with traceable provenance and usage rights. Then test a broader passive-parameter grid. Active-channel or nonlinear-synapse work remains a separate research stage.

## Limits

This remains passive linear RC model reduction. The three morphologies do not constitute a representative human-neuron population. The Mohan2015 reconstruction is partial and lacks an axon. Deterministic ±20% parameter perturbations are stress cases, not biological confidence intervals. Cholesky positive definiteness is not a full biological validation.
