# Research log — PRIMA accuracy/memory/holdout synthesis

**Date:** 23 November 2026  
**Branch:** research/prima-accuracy-memory-holdout-synthesis-2026-11-23

## Work performed

Read and cross-checked the validated reports and CSVs from PRs #4–#8:
- PR #4 high-order nine-port matrix
- PR #5 resource/RSS benchmark
- PR #6 equal-order seven-port versus nine-port
- PR #7 shift/order Pareto matrix
- PR #8 independent NMO_162186 morphology holdout

No source matrices were re-run; all referenced workflows had already passed and their outputs were committed. The purpose of this checkpoint is to reconcile the evidence without mixing non-identical protocols or port configurations.

## Result

The current high-frequency passive candidate is seven-port order112 with the extended 10 kHz shift distribution. On three morphologies and nine deterministic parameter scenarios it achieved median 10 kHz Z/Y residuals 4.681e−6% / 1.390e−5%, with worst transient error effectively identical to order112 narrow shifts. On the NMO_162186 holdout its median 10 kHz Z/Y residuals were 4.630e−6% / 9.474e−6%, again with essentially unchanged transient metrics.

For nine retained ports, order168 is the first equal-order test point where the seven shared outputs are effectively at parity with the seven-port model while the new q25 outputs are accurate (max q25 NRMSE 9.7486e−7%). The result is passive and specific to the tested protocol.

The separate resource benchmark reports median peak RSS 267.90 / 276.15 / 301.73 MB for orders84/112/168. Every one of 12 paired RSS comparisons is positive at both order transitions. Wall and user CPU timing is not a controlled order ranking because GitHub used seven CPU models.

## Decision

Full Hines remains canonical. Do not change production defaults. Keep 7-port order112 extended10kHz as a high-frequency passive research candidate; 9-port order168 as opt-in only when q25 outputs are needed; order84 as lower-memory alternative. These are conditional choices, not one universal winner.

## Remaining validation gaps

- No matched 7/9-port order112/168 matrix on the NMO_162186 held-out morphology.
- Only one external holdout, from an epilepsy surgical specimen with incomplete axon.
- No controlled fixed-hardware timing comparison.
- No active/nonlinear biological validation.
