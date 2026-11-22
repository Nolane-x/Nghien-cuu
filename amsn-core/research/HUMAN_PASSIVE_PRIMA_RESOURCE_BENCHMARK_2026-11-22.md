# Human passive PRIMA high-order resource benchmark — complete validated results

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**Code head tested:** `e556625b9f0b1f31f9c822e603cf0ae220eefe0f`  
**GitHub Actions run:** [45016243390](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45016243390)  
**Purpose:** Complete the previously partial CPU/RSS analysis for PRIMA orders 84, 112 and 168 without changing model defaults.

## 1. Executive result

The resource benchmark is now complete: **37/37 GitHub Actions jobs passed** (one validator job and 36 resource-measurement jobs). All 36 artifact ZIPs were downloaded and their SHA-256 digests matched the values returned by GitHub's artifact API (**36/36**). Each resource artifact contains one resource row, one environment row and a 210-row passive audit sweep. The independent analysis verified 36 unique matrix conditions and **7,560 raw sweep rows**, with no coverage, identity, rank, exit-status or digest errors.

Across 12 runs per selected candidate order, the median process-level metrics were:

| Selected PRIMA order | Runs | Median user CPU (s) | Median peak RSS (MiB) | Median wall time (s) | Median state reduction |
|---:|---:|---:|---:|---:|---:|
| 84 | 12 | 141.45 | 268.16 | 116.58 | 99.3225% |
| 112 | 12 | 205.96 | 277.29 | 98.78 | 99.0967% |
| 168 | 12 | 278.31 | 300.76 | 129.95 | 98.6451% |

Relative to order 84, order 112 used **45.61% more median user CPU time** and **3.40% more median peak RSS**. Order 168 used **96.76% more median user CPU time** and **12.16% more median peak RSS**. These are descriptive whole-process measurements, not isolated PRIMA-kernel costs.

The wall-time medians are not a reliable ranking: the 36 jobs ran on seven different CPU models provided by GitHub-hosted runners, and wall-time variation is large. In particular, the lower median wall time at order 112 must not be read as proof that order 112 is faster than order 84.

## 2. Experimental design and coverage

The matrix contained:

- Three existing morphology fixtures: `NMO_68174_cell1125`, `NMO_68175_cell1204` and `NMO_290988_Mohan2015`.
- Two NEURON maximum segment-length caps: 0.125 µm and 0.0625 µm.
- Three selected PRIMA orders: 84, 112 and 168.
- Two independent repetitions for each morphology × mesh × order combination.
- 36 measured jobs in total, plus one validator-test job.

Each job compared the fixed four-shift order-56 control, a six-shift order-56 control, and the selected six-shift candidate. Each output CSV had exactly 210 rows: 30 frequency-response rows, 162 per-port transient rows and 18 all-port transient rows. Across the complete matrix, these were 1,080 frequency rows, 5,832 per-port transient rows and 648 all-port transient rows.

Each resource process measured elapsed wall time, user CPU time, system CPU time and maximum resident set size using `/usr/bin/time`. The audit also recorded the runner CPU model, logical CPU count, Python version, morphology, mesh cap and achieved PRIMA order. Every resource record reported exit status 0 and the requested candidate order equaled the achieved order.

## 3. Results by mesh resolution

| NEURON mesh cap (µm) | PRIMA order | Runs | Median user CPU (s) | Median peak RSS (MiB) | State reduction |
|---:|---:|---:|---:|---:|---:|
| 0.1250 | 84 | 6 | 141.45 | 262.54 | 99.3225% |
| 0.1250 | 112 | 6 | 205.96 | 275.84 | 99.0967% |
| 0.1250 | 168 | 6 | 308.95 | 298.19 | 98.6451% |
| 0.0625 | 84 | 6 | 147.92 | 393.18 | 99.3225% |
| 0.0625 | 112 | 6 | 215.19 | 398.03 | 99.0967% |
| 0.0625 | 168 | 6 | 262.94 | 417.28 | 98.6451% |

For this matrix, the finer 0.0625 µm reference mesh increased median process RSS relative to 0.125 µm by approximately **49.76% at order 84**, **44.30% at order 112** and **39.94% at order 168**. This suggests that reference-mesh resolution is a major driver of total process memory in these jobs. It is not a universal law: these are three morphology fixtures and two mesh settings under one workflow.

The user-CPU medians by mesh do not show a simple monotonic mesh effect, and they should not be over-interpreted because runner CPU models differ. The morphology-stratified measurements are available in the accompanying CSV rather than compressed into a single ranking.

## 4. Interpretation and decision

**Observation from this completed benchmark:** increasing the selected reduced order from 84 to 112 or 168 is associated with larger median process CPU time and RSS in this workflow, while state compression decreases from 99.3225% to 99.0967% and 98.6451%.

**Research decision:**

- Order 84 remains the lower-resource high-compression candidate in this tested matrix.
- Order 112 is an intermediate capacity option; its additional transient/high-band accuracy from earlier PRIMA experiments must be weighed against its measured process resource cost.
- Order 168 has the largest resource footprint and should remain an opt-in research candidate unless its morphology-specific accuracy gain is needed.
- No production default is changed. Full Hines remains the canonical passive reference. Seven ports remain the canonical retained-output set; nine-port order 168 is a research option, not a universal replacement.

This is not a recommendation that order 84 is always best. Earlier accuracy studies found order 112/168 can materially improve difficult transient outputs, and the added benefit of order 168 varied by morphology. Candidate selection remains a multi-objective accuracy/resource decision.

## 5. Limitations

1. The measured process includes the complete audit, including the Hines/reference path and comparison models, not just PRIMA basis construction, projection or reduced solves. The reported CPU/RSS values cannot be attributed to the candidate model alone.
2. GitHub-hosted runners supplied seven different CPU models. Wall-clock medians are therefore not a controlled hardware comparison; the full wall-time range is included in the per-order CSV.
3. There are two repetitions per morphology/mesh/order, enough for an initial profile but not a high-confidence performance distribution.
4. The benchmark uses three previously studied morphology fixtures, not the independent Allen/NeuroMorpho holdout NMO_162186. NMO_290988_Mohan2015 is a partial dendritic reconstruction without an axon; it is not a complete neuron or a healthy-control population sample.
5. All results concern passive linear RC model reduction. They do not validate active ion channels, action potentials, nonlinear synaptic integration, calcium signaling, plasticity, gene expression, metabolism, cognition or biological completeness.

## 6. Reproduction and audit trail

The benchmark workflow used Python 3.12.16 and pinned NEURON 9.0.2. The separate validator job ran:

```bash
python -m pytest -q research/test_prima_resource_benchmark_validator.py
```

The GitHub Actions log records **16 passed in 0.02 s**. All 36 resource jobs completed successfully; the run's complete job endpoint reports 37/37 successful jobs.

To independently re-check downloaded ZIPs using only the Python standard library:

```bash
python research/analyze_prima_resource_benchmark_artifacts.py \
  --input-dir /path/to/downloaded-artifact-zips \
  --manifest amsn-core/results/human_prima_resource_benchmark_artifact_manifest_2026-11-22.csv \
  --output-dir /tmp/prima-resource-recheck
```

The script verifies the expected artifact set, SHA-256, one resource/environment row per artifact, exact model IDs and realized rank, exit status, metric row counts and unique matrix coverage. It then writes the per-run table, grouped summaries, refreshed digest manifest and validation JSON.

Committed evidence:

- `amsn-core/results/human_prima_resource_benchmark_36_runs_2026-11-22.csv` — one row per resource run, including artifact ID.
- `amsn-core/results/human_prima_resource_benchmark_by_order_2026-11-22.csv` — order-level medians and ranges.
- `amsn-core/results/human_prima_resource_benchmark_by_mesh_2026-11-22.csv` — mesh/order breakdown.
- `amsn-core/results/human_prima_resource_benchmark_by_morphology_2026-11-22.csv` — per-morphology breakdown.
- `amsn-core/results/human_prima_resource_benchmark_artifact_manifest_2026-11-22.csv` — all 36 artifact IDs and expected/downloaded SHA-256 values.
- `amsn-core/results/human_prima_resource_benchmark_validation_2026-11-22.json` — machine-readable validation summary.
- `research/analyze_prima_resource_benchmark_artifacts.py` — standard-library reproducer.

The older `HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_PARTIAL_2026-11-22.md` and its 12-artifact CSV are intentionally retained as an earlier checkpoint, not overwritten. This report supersedes their partial status for workflow run 45016243390.

## 7. Next experiment

Run a **kernel-isolated profile** on a fixed, declared CPU environment (or the same pinned runner where possible). Record separate timings and peak memory for: (a) shifted Krylov basis construction, (b) orthogonalization, (c) congruence projection, (d) frequency-domain solves and (e) transient solves. Repeat enough times to report medians and dispersion, and include full Hines in a separate baseline process. Then apply the same focused profile to the independent NMO_162186 holdout and a second provenance-qualified human morphology before deciding whether any order preset should be promoted.

Until those tests exist, all model defaults remain unchanged and full Hines remains canonical.
