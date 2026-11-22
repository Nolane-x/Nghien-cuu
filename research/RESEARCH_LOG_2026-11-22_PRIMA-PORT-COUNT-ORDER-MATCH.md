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

## Result status

Implementation and workflow are staged in the PR branch. No numerical result is yet claimed. Results remain pending until the 12 job matrix completes and all 3,072 rows have been validated and analyzed.
