# Handoff — equal-order seven-port versus nine-port PRIMA comparison

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Research branch:** `research/prima-equal-order-seven-vs-nine-ports-2026-11-22`  
**Previous validated report:** `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md`

## Question

The validated nine-port high-order experiment shows that orders 112 and 168 outperform the seven-port order-84 baseline in all 252 matched common-port transient observations. This does not yet isolate port-count effects because the comparator has a lower basis order. The next controlled experiment tests seven and nine retained ports at identical requested and achieved six-shift orders 56, 112 and 168.

## Fixed matrix

- Three morphologies: NMO_68174 cell1125, NMO_68175 cell1204, NMO_290988 / 1094_Mohan_etal_2015.
- Two NEURON mesh caps: 0.125 and 0.0625 µm.
- Two retained port sets: seven and nine.
- Six-shift PRIMA orders: 56, 112, 168.
- Four models per configuration: four-shift order-56 control plus six-shift orders 56/112/168.
- Ten frequencies: 0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz.
- Six transient scenarios: soma, basal-q75, apical-q75 sources × 2/10 ms pulses; 10 pA, 2 ms onset, 20 ms duration, dt=0.1 ms.
- All transient outputs recorded at every retained port.

Expected matrix:
- Seven-port job: 40 frequency + 168 port transient + 24 all-port rows = **232 rows/job**; six configs = 1,392 rows.
- Nine-port job: 40 frequency + 216 port transient + 24 all-port rows = **280 rows/job**; six configs = 1,680 rows.
- Total: 12 jobs and **3,072 rows**.

The workflow `.github/workflows/amsn-human-prima-port-count-order-match.yml` parameterizes port count through `AMSN_EXPECTED_PORTS` and `AMSN_PORT_ENRICHMENT`. The default seven-port path is unchanged. Nine-port output uses the isolated optional quantile mapper. The matrix validator asserts exact row counts, per-metric counts and model IDs for each job.

## Main validation question

Compare shared output nodes by exact SWC node ID, morphology, mesh, model, source and pulse scenario. This isolates the effect of retaining q25 ports under equal order and identical protocol.

Report:
- frequency-domain Z/Y errors vs full Hines and native NEURON;
- every shared-port transient NRMSE and all-port aggregate;
- q25-only output behavior;
- actual achieved order and state reduction;
- positive-definiteness checks and matrix conditioning;
- CPU wall time and peak RSS if available.

## Acceptance/decision rule

Do not promote nine ports merely because a higher-order model improves against a lower-order seven-port baseline. First establish equal-order accuracy/cost trade-offs. Keep full Hines canonical and do not change production defaults in this experiment. Keep the native NEURON discrepancy separate from the internal PRIMA-vs-Hines projection residual.

## Validated result — 2026-11-22

The full matrix completed in Actions run [44987393352](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44987393352): **12/12 jobs succeeded**, including each job's complete AMSN test suite, SWC record check, experiment and exact row-coverage assertion. All 12 artifacts were downloaded and checked.

- Seven-port coverage: 6 × 232 = 1,392 rows.
- Nine-port coverage: 6 × 280 = 1,680 rows.
- Total: 3,072 rows.
- Shared-output transient pairs: 252 per order (756 total), matched by exact SWC node ID.
- q25-only observations: 72 per order (216 total).

| Order | Nine-port regressions | Improvements | Median NRMSE ratio (9/7) | Worst absolute nine-port NRMSE |
|---:|---:|---:|---:|---:|
| 56 | 252/252 | 0 | 131.329× | 0.52309925% |
| 112 | 252/252 | 0 | 3.326× | 0.00003446882% |
| 168 | 148/252 | 104/252 | 1.00000062× | 0.00000344983% |

The order-168 common-port difference is numerically negligible. The added q25 ports have median/max NRMSE of 0.00972849/0.14042521% at order 56, 0.0000002199/0.0000123083% at order 112, and 0.00000009782/0.00000097486% at order 168.

Full results: amsn-core/research/HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_PORT_COUNT_2026-11-22.md. Reproduction script: amsn-core/research/analyze_human_prima_equal_order_port_count.py. Raw artifact IDs and SHA-256 digests: amsn-core/results/HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_ARTIFACT_MANIFEST_2026-11-22.csv.

## Decision and next work

Keep Hines canonical and keep the current production defaults unchanged. Do not choose port count without basis order: at order 56 and 112, the nine-port model had higher transient NRMSE on every shared-port pair; at order 168, shared-port responses were effectively equivalent while the additional q25 outputs were accurate. Treat nine-port/order-168 as an opt-in passive research candidate pending CPU/RSS measurements and held-out morphology tests. This does not validate active channels, nonlinear synapses or other biological mechanisms.
