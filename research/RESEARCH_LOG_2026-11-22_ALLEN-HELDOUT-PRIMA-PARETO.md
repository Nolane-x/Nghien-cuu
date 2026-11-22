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


## First completed holdout sweep — raw results independently verified

GitHub Actions [run 45010021065](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45010021065), commit `a68f833313856bbf3413e65b1cc7525d6e2b1667`, completed the full numerical sweep successfully but the post-run coverage step exited with `KeyError: 'swc_id'`. The preflight JSON's `mapping` records correctly use `swc_node_id`; the validator had incorrectly queried `swc_id`. The simulation itself returned exit status 0 and emitted all three result CSVs. This is a report-schema key mismatch, not a morphology-import or numerical-model failure.

The uploaded raw artifact [14749942004](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45010021065/artifacts/14749942004) was downloaded and SHA-256 verified against GitHub metadata: `4125c1b28c29ecfdc58c810461ecbef95c133486a2680c88ef63dd687aa5efe0`. Independent CSV inspection confirmed:

- 81 model rows = 9 candidates × 9 deterministic parameter scenarios.
- 729 frequency rows = 9 candidates × 9 scenarios × 9 frequencies.
- 3,402 transient-port rows = 9 candidates × 9 scenarios × 3 sources × 2 pulse widths × 7 ports.
- Exact candidate set: orders 56/84/112 × narrow_3khz / extended_10khz / balanced_10khz.
- All 81 rows report `cholesky_passed`; every requested basis order equals the achieved order.
- Frequency/transient keys are unique, with no duplicate rows; all numeric errors are finite and non-negative.
- Resource measurement: 222.12 s wall, 316.47 s user CPU, 198,628 KiB peak RSS; process exit status 0.
- All seven port IDs in the transient CSV match the seven `mapping[*].swc_node_id` entries in the source-preflight JSON.

### Holdout-specific candidate results

Median values are calculated over all nine parameter scenarios for the same morphology. Transient metrics are the median and maximum of individual port NRMSE (%).

| Candidate | Median Z error at 10 kHz | Median Y error at 10 kHz | Median transient NRMSE | Maximum transient NRMSE |
|---|---:|---:|---:|---:|
| order56_narrow_3khz | 0.233029% | 0.331126% | 6.22966e-6% | 9.29146e-4% |
| order56_extended_10khz | 0.0591833% | 0.117693% | 4.30070e-5% | 0.00393226% |
| order56_balanced_10khz | 0.239990% | 0.367410% | 1.00626e-5% | 0.00159414% |
| order84_narrow_3khz | 0.00571093% | 0.0123781% | 1.09419e-8% | 4.47118e-7% |
| order84_extended_10khz | 0.000157960% | 0.000299797% | 2.31884e-7% | 5.73406e-5% |
| order84_balanced_10khz | 0.00148238% | 0.00400957% | 2.19220e-8% | 2.35404e-6% |
| order112_narrow_3khz | 0.000139279% | 0.000319528% | 8.87541e-9% | 1.45425e-7% |
| order112_extended_10khz | 0.00000461244% | 0.00000958163% | 8.88355e-9% | 1.45425e-7% |
| order112_balanced_10khz | 0.000164588% | 0.000101029% | 8.87529e-9% | 1.45425e-7% |

For this single holdout, `order112_extended_10khz` cuts median 10 kHz Z error by about **30.2×** and Y error by about **33.4×** versus `order112_narrow_3khz`, while median and maximum transient errors are essentially unchanged. `order84_narrow_3khz` remains a very accurate lower-order transient candidate but has larger 10 kHz AC error. At order 56 the extended shift set clearly worsens transient error; the trade-off therefore depends on basis order.

This is one epilepsy surgical-specimen dendritic morphology under passive linear-RC assumptions. It does not prove generalization to healthy controls, complete axon-bearing neurons, active channels or a human-neuron population. The artifact and report-schema validator need to complete successfully on a fresh run before these rows are promoted as an accepted holdout result.
