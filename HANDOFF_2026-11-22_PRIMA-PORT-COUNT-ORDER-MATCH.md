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

## Validation state

This handoff records the planned equal-order matrix. No numerical result is claimed until all 12 jobs emit their exact row counts and six artifacts per port set are inspected.
