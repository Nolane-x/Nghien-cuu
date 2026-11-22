# Research log — held-out NMO_162186 PRIMA shift/order matrix

**Date:** 2026-11-22  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**Source holdout:** NeuroMorpho.Org NMO_162186 / Allen Cell Types  
**Source SHA-256:** `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`

The source preflight has passed on GitHub Actions run [45006976569](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45006976569). It established the exact 7,287-record standardized SWC, neurite-type coverage, 48 branch points, three-point soma recognition, Import3D mapping and passive DC consistency against NEURON 9.0.2.

This follow-on job consumes the artifact emitted by that preflight (rather than retrieving a different copy), verifies the pinned SHA-256 again, then runs the same 9-candidate/9-scenario PRIMA protocol used on the three prior morphologies.

## Planned coverage

- Candidates: basis orders 56, 84 and 112 × narrow 3 kHz, extended 10 kHz and balanced 10 kHz shift sets (9 candidates).
- Scenarios: nominal, ±20% Rm, ±20% Cm, ±20% Ra and all parameters ±20% (9 deterministic stress cases).
- AC frequencies: 0.1 through 10,000 Hz (9 points).
- Transients: soma/basal-q75/apical-q75 sources × 2 ms/10 ms square pulse × 7 fixed output ports.
- Expected data: 81 model rows, 729 frequency rows and 3,402 transient-port rows.
- Reduced G/C Cholesky checks and exact requested/achieved order.
- CPU/wall-time/RSS from the job runner.

The workflow is gated on the source-preflight job and verifies the source hash `a05ad...` before starting the sweep. No production defaults change and the raw morphology remains an Actions artifact, not committed into the repository.

The held-out classification remains **single human L2–3 dendritic morphology from an epilepsy surgical specimen; axon incomplete**. This is not a healthy-control sample or a representative human-neuron population. All measurements remain passive linear RC model comparisons against full Hines.
