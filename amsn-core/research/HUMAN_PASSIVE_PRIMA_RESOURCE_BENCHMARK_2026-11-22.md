# Human passive PRIMA high-order resource benchmark — validated results

**Date:** 2026-11-22 (Asia/Bangkok)  
**PR:** [#5 — High-order PRIMA CPU/RSS benchmark](https://github.com/Nolane-x/Nghien-cuu/pull/5)  
**Workflow run:** [44989658844 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44989658844)  
**Fix commit:** e643782ea7ace390f651a56d2c9cb362301cff84

## Executive result

The corrected benchmark completed **37/37 GitHub Actions jobs successfully**: one validator preflight and 36 resource measurements. The preflight ran the 12 new validator unit tests. All 36 resource artifacts were downloaded, each contained one measurement row, all 36 ZIP SHA-256 digests matched GitHub's artifact metadata, and all measurements had exit status 0.

The matrix contains 3 morphologies × 2 NEURON mesh caps × 3 candidate PRIMA orders (84, 112, 168) × 2 independent repetitions:
- 36 measurements;
- 7,560 checked sweep CSV rows (210 per run);
- every run includes 30 frequency rows, 162 per-port transient rows and 18 all-port transient rows;
- all runs record the control model, six-shift order-56 model and requested candidate model, with requested and achieved candidate order matching.

## Resource summary by candidate order

| Candidate order | Runs | Median wall time | Median user CPU | Median peak RSS | State reduction |
|---:|---:|---:|---:|---:|---:|
| 84 | 12 | 101.61 s | 122.00 s | 267.90 MB | 99.055–99.389% |
| 112 | 12 | 129.11 s | 273.78 s | 276.15 MB | 98.741–99.185% |
| 168 | 12 | 124.83 s | 266.60 s | 301.73 MB | 98.111–98.778% |

Ranges across the 12 runs per order:
- Order 84: wall 62.91–145.29 s; user CPU 64.42–172.79 s; peak RSS 188.41–403.88 MB.
- Order 112: wall 59.06–182.69 s; user CPU 118.24–384.01 s; peak RSS 196.53–407.03 MB.
- Order 168: wall 61.76–165.71 s; user CPU 121.97–357.61 s; peak RSS 212.02–418.76 MB.

## Peak-memory scaling

Peak RSS increased in every matched morphology/mesh/repetition comparison:

| Comparison | Matched pairs | Median RSS increase | Min–max increase | Positive pairs |
|---|---:|---:|---:|---:|
| 112 vs 84 | 12 | +6.24 MB | +1.77 to +13.70 MB | 12/12 |
| 168 vs 84 | 12 | +23.48 MB | +14.58 to +38.72 MB | 12/12 |
| 168 vs 112 | 12 | +18.32 MB | +11.43 to +27.52 MB | 12/12 |

This is the most consistent resource conclusion from the matrix. Higher PRIMA order retains more reduced states and costs more peak memory, with the order-168 candidate using about 23.5 MB more peak RSS than order 84 in the median paired comparison.

## Timing interpretation and environment limits

The measured command is the complete human_schur_port_matrix_audit.py process, timed with /usr/bin/time; it includes setup, full-reference computations and the reduced-order sweep. It is not an isolated microbenchmark of one matrix operation.

All jobs used Linux x86_64, Python 3.12.16 and four logical CPUs, but GitHub assigned seven different AMD EPYC / Intel Xeon CPU models. Wall time and user CPU time therefore have runner heterogeneity. The median wall time is somewhat higher for 112/168 than for 84, but the ranges overlap substantially; order 168 is not demonstrably faster than 112. User CPU time is also variable and should not be treated as a stable speed ranking across these mixed processors. The memory trend is more consistent because all 12 paired comparisons are positive at each order step.

The median user CPU time exceeds wall time in many runs because process CPU time sums across threads. This is not a contradiction.

## Morphology and mesh effects

The full electrical compartment counts were 8,893 (NMO_290988), 12,399 (NMO_68174) and 13,747 (NMO_68175). The 0.0625 µm NEURON mesh-cap runs generally used materially more RSS than the 0.125 µm runs for the same morphology and candidate order. Results are reported separately by morphology and mesh in resource_benchmark_config_summary_2026-11-22.csv; do not collapse these structural differences into a single absolute memory limit for all cells.

NMO_290988_Mohan2015 is a partial dendritic reconstruction without an axon and must not be characterized as a healthy-control morphology.

## Decision guidance

1. **Order 84 is the lowest-resource candidate tested** and is the sensible next point for an accuracy-versus-memory trade-off study. This benchmark alone does not prove that order 84 is accurate enough.
2. **Order 112 is an intermediate point** with a modest median memory increase over order 84, but higher measured CPU time in this heterogeneous runner matrix.
3. **Order 168 is the higher-fidelity research candidate** when the nine-port q25 outputs are required: the equal-order port-count study (PR #6) found that at order 168 the seven shared outputs are effectively equivalent between 7- and 9-port reductions, while the added q25 outputs are accurate. The cost is a median +23.48 MB RSS over order 84 and +18.32 MB over order 112 in matched comparisons.
4. Keep full Hines as the canonical reference and do not change production defaults based on these three morphology fixtures alone. Validate on held-out morphologies and active/nonlinear models separately.

## Reproducibility and provenance

- Raw measurements: amsn-core/results/resource_benchmark_measurements_2026-11-22.csv.
- Aggregates: resource_benchmark_order_summary_2026-11-22.csv, resource_benchmark_config_summary_2026-11-22.csv, and resource_benchmark_memory_paired_deltas_2026-11-22.csv.
- Artifact IDs, byte sizes, SHA-256 digests and expiry timestamps: resource_benchmark_artifact_manifest_2026-11-22.csv.
- Every artifact is retained by GitHub until 2027-02-20 05:30:02 UTC unless repository retention settings change.
- Each run used candidate orders 84/112/168 with the control model and six-shift order 56; see the ZIP artifacts for environment, timing log and full sweep CSV.

This is a passive RC resource benchmark. It does not measure action-potential propagation, active ion-channel dynamics, synapses, plasticity, calcium signaling or cognition.
