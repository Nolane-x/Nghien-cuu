# Research log — equal-order seven-port versus nine-port PRIMA comparison

**Date:** 2026-11-22 (Asia/Bangkok)  
**Branch:** `research/prima-equal-order-seven-vs-nine-ports-2026-11-22`

## Motivation

Earlier validated studies established:
- seven-port six-shift order84 has strong transient accuracy;
- adding basal/apical q25 ports at unchanged orders 28/56/84 worsened apical-q90 in every matched comparison;
- increasing nine-port basis order to 112/168 restored accuracy, beating the seven-port order84 model in 252/252 shared-port pairs.

The last comparison was not an equal-order comparison. It confounded the port set and basis capacity. This matrix directly addresses that confound.

## Protocol

Run seven- and nine-port sets at the same six-shift orders 56/112/168, with the four-shift order56 control, across three morphologies and two NEURON mesh caps. Keep the same ten frequencies, three current sources, six pulse scenarios, passive parameters and timestep. Shared ports must be paired by SWC node ID, not ordinal position.

## Exact coverage

Per seven-port job: 232 sweep rows (40 frequency + 168 transient-port + 24 all-port aggregate). Per nine-port job: 280 rows (40 + 216 + 24). Six configurations per port set = 1,392 and 1,680 rows respectively; total expected 3,072 rows across 12 jobs.

The workflow checks metric counts and all four expected model IDs for each configuration. Every job runs the full test suite, verifies SWC record count and uploads the sweep/log/Schur artifacts.

## Falsifiable question

At equal achieved basis order, does adding q25 retained probes materially reduce the shared-port errors, or does the seven-port model retain equal/better accuracy at a lower order budget? The q25 ports have no seven-port counterpart, so report their errors separately rather than forcing a false pair.

## Validated result — 2026-11-22

Actions run [44987393352](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44987393352) completed with **12/12 successful jobs**. Each job ran the complete AMSN test suite and asserted exact SWC record count, model identity and row coverage. All 12 artifacts were downloaded and inspected.

The expected output matrix was complete:
- Seven ports: 6 configurations × 232 rows = 1,392.
- Nine ports: 6 configurations × 280 rows = 1,680.
- Total = 3,072 sweep rows.
- Six morphology/mesh configurations × six transient scenarios × seven shared output nodes = 252 pairs per order.

The full pair analysis found:
- Order 56: 252/252 shared-output pairs regress in the nine-port model; median NRMSE ratio 131.329×. Max single-output NRMSE: 0.00869138% (7-port) vs 0.52309925% (9-port).
- Order 112: 252/252 pairs regress; median ratio 3.32556×. Absolute maximum NRMSE remains 0.00000344983% (7-port) vs 0.00003446882% (9-port).
- Order 168: 148 regressions / 104 improvements; median ratio 1.00000062× and worst ratio 1.00064571×. Maximum absolute NRMSE is effectively identical at 0.00000344984%.
- The 72 q25-only observations per order show maximum NRMSE 0.14042521%, 0.0000123083% and 0.00000097486% for orders 56, 112 and 168 respectively.

Interpretation: additional retained ports require sufficient basis capacity; port count cannot be judged independently. At order 168, the common seven outputs are numerically equivalent and the q25-only outputs are highly accurate under this passive protocol. Keep full Hines canonical and do not promote production defaults.

Reproducible analysis is checked in at amsn-core/research/analyze_human_prima_equal_order_port_count.py. The report, summary CSVs and 12-artifact SHA-256 manifest are stored under amsn-core/research/ and amsn-core/results/. The analysis script was executed against the downloaded sweep artifacts and validated all 756 matched shared-port pairs and 216 q25-only observations.

## Limits and next steps

This result applies only to passive linear RC reduction and the exact morphology/mesh/protocol matrix above. The frequency-domain 7-port and 9-port Frobenius matrices have different dimensions and are reported separately against their respective references, not interpreted as a direct elementwise port-count comparison. No active channel, synaptic nonlinearity, plasticity, calcium, metabolic or cognitive claim is supported. Next priorities: complete the separate CPU/RSS benchmark, validate held-out morphologies and perturb Rm/Cm/Ra without fitting against native NEURON.
