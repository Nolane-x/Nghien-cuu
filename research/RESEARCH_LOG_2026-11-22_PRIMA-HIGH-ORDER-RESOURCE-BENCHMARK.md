# Research log — human passive PRIMA high-order resource benchmark

**Date:** 2026-11-22  
**PR:** #5  
**Actions run:** 44989658844  
**Fix commit:** e643782ea7ace390f651a56d2c9cb362301cff84

## Problem and repair

The first high-order resource benchmark attempts produced failed coverage-validation steps even though the simulator and /usr/bin/time completed and produced the sweep CSVs. The validator formed the expected model ID from the entire comma-separated AMSN_PRIMA_EXTENDED_ORDERS value. For an order-84 run, it incorrectly searched for six_shift_order56,84 rather than checking six_shift_order56 and six_shift_order84 separately.

The repair adds:
- amsn-core/src/amsn/resource_benchmark.py with strict order-list parsing and exact model/metric/frequency/scenario/port/rank checks;
- amsn-core/tests/test_resource_benchmark.py with 12 passing unit tests;
- a preflight job before the resource matrix;
- a distinct AMSN_BENCH_CANDIDATE_ORDER field for the chosen order;
- explicit required resource-timing fields and exit-status validation.

## Validated matrix

Run 44989658844 finished successfully. All 37 workflow jobs passed: one preflight and 36 benchmark jobs. The design covered 3 morphologies × 2 mesh caps × candidate orders 84,112,168 × 2 repetitions. This yielded 36 measurement rows and 7,560 sweep rows. All 36 artifacts were downloaded and verified against their GitHub SHA-256 digests.

## Quantitative result

Median peak RSS by order:
- 84: 267.90 MB (range 188.41–403.88 MB);
- 112: 276.15 MB (range 196.53–407.03 MB);
- 168: 301.73 MB (range 212.02–418.76 MB).

Every matched morphology/mesh/repetition pair showed increasing RSS from 84 to112, from84 to168, and from112 to168. Median paired increases were +6.24 MB, +23.48 MB and +18.32 MB respectively.

Median wall time was 101.61 s,129.11 s and124.83 s for order84,112 and168. Median user CPU was 122.00 s,273.78 s and266.60 s. These are full-audit timings, not isolated solver microbenchmarks. Seven different AMD/Intel CPU models were assigned by GitHub across jobs, so timing rankings are provisional. Peak RSS is more stable across the paired matrix.

## Decision and next work

Order84 is the low-resource candidate to evaluate against accuracy tolerances. Order168 has the strongest result from the separate equal-order port-count experiment, but increases peak memory. Don't change defaults or merge passive conclusions into active-neuron claims. Next: use held-out morphologies, compare exact error tolerances per source/probe and measure a dedicated solver-only microbenchmark on a pinned runner to improve timing comparability.
