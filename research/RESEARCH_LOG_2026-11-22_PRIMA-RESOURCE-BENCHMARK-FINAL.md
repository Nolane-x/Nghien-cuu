# Research log — complete PRIMA order resource benchmark and artifact audit

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**Code head tested:** `e556625b9f0b1f31f9c822e603cf0ae220eefe0f`  
**Actions run:** [45016243390](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45016243390)

## Question and hypothesis

Can the pending PRIMA high-order runtime/peak-RSS benchmark be closed with a complete, independently inspectable result across all planned morphologies, mesh caps, candidate orders and repetitions? The working hypothesis was that larger reduced orders would require additional process CPU time and memory, but the size of that cost relative to mesh refinement needed to be measured rather than assumed.

## Sources examined

- `AGENTS.md`, `HANDOFF.md`, `HANDOFF_2026-11-22_PRIMA-HELDOUT-AND-PORT-ORDER.md`.
- `amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md`.
- Historical partial resource report and its 12-artifact CSV.
- `.github/workflows/amsn-human-prima-high-order-resource-benchmark.yml`.
- GitHub Actions run 45016243390, complete jobs endpoint, step records and validator job log.
- GitHub artifact API metadata for all 36 resource ZIPs.

## Work performed

1. Re-read current handoff and confirmed the previous resource note covered only 12 of 36 artifacts from an earlier workflow run.
2. Inspected the latest PR #8 branch head and the new workflow run. The run was on code head `e556625...`; it completed with 37 successful jobs: one validator job and 36 resource jobs.
3. Downloaded all 36 resource ZIP artifacts from run 45016243390 and checked every local ZIP SHA-256 against the digest exposed by GitHub's artifact API.
4. Parsed every ZIP using Python standard library only. Verified one resource row, one environment row, 210 sweep rows, exactly 30 frequency / 162 per-port transient / 18 all-port transient rows, expected model IDs, exact realized candidate order, replicate identity and exit status 0.
5. Verified 36 unique matrix conditions and aggregate coverage of 1,080 frequency, 5,832 per-port transient and 648 all-port transient rows (7,560 total).
6. Generated per-run, per-order, per-mesh and per-morphology CSVs, a 36-artifact manifest, validation JSON and a reusable standard-library analysis script.
7. Executed the analysis script on the downloaded artifact set; final result: 36/36 digests matched, 36/36 conditions present, 7,560 rows validated and no errors. Ran Python bytecode compilation for the script successfully.

## Actual test and command evidence

GitHub Actions validator job `137189051425`:

```bash
python -m pytest -q research/test_prima_resource_benchmark_validator.py
```

Observed log output: `16 passed in 0.02s` (Python 3.12.16).

GitHub Actions resource job sample `137190271912` completed all steps, including pinned NEURON installation, morphology record-count check, runner-environment capture, `/usr/bin/time` process measurement, output-coverage validation and artifact preservation. The complete run API reports 37/37 jobs with conclusion `success`.

Local analysis command used during this session:

```bash
python research/analyze_prima_resource_benchmark_artifacts.py \
  --input-dir /mnt/data \
  --manifest /mnt/data/prima_resource_final/amsn-core/results/human_prima_resource_benchmark_artifact_manifest_2026-11-22.csv \
  --output-dir /mnt/data/prima_resource_final/recheck
```

The committed reproducer was also checked with `python -m py_compile`.

## Results

Across 12 runs per candidate order:

- Order 84: median user CPU 141.45 s; peak RSS 268.16 MiB; state reduction 99.3225%.
- Order 112: median user CPU 205.96 s; peak RSS 277.29 MiB; state reduction 99.0967%.
- Order 168: median user CPU 278.31 s; peak RSS 300.76 MiB; state reduction 98.6451%.

Relative to order 84, order 112 had +45.61% median user CPU and +3.40% median RSS; order 168 had +96.76% median user CPU and +12.16% median RSS. The finer 0.0625 µm mesh showed 39.94–49.76% higher median RSS than the 0.125 µm mesh, depending on candidate order.

Wall time is not interpreted as a speed ranking because seven different CPU models were used by the hosted runners. Measurements cover the whole audit process, not isolated PRIMA kernels.

## Files added

- `amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md`
- `amsn-core/results/human_prima_resource_benchmark_36_runs_2026-11-22.csv`
- `amsn-core/results/human_prima_resource_benchmark_by_order_2026-11-22.csv`
- `amsn-core/results/human_prima_resource_benchmark_by_mesh_2026-11-22.csv`
- `amsn-core/results/human_prima_resource_benchmark_by_morphology_2026-11-22.csv`
- `amsn-core/results/human_prima_resource_benchmark_artifact_manifest_2026-11-22.csv`
- `amsn-core/results/human_prima_resource_benchmark_validation_2026-11-22.json`
- `research/analyze_prima_resource_benchmark_artifacts.py`
- `HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md`

## Interpretation and limits

This is a validated resource profile for one workflow configuration, not a general benchmark of all PRIMA implementations. CPU/RSS values include Python, NEURON, the full reference model and multiple candidate/control audits in each process. Runner CPU heterogeneity limits wall-time comparability. Two repeats per matrix cell are preliminary. All underlying simulations remain passive linear RC; the three benchmark morphologies are not a representative human population and NMO_290988 is an incomplete dendritic reconstruction without axon.

No default is changed. Full Hines stays canonical. The historic partial report is preserved unchanged and is superseded for the new run only by the complete report.

## Commit and next experiment

This log is part of the PR #8 branch update that records the completed analysis; see the branch commit history for the final documentation commit. The tested code head is separately recorded above.

Next: isolate timings and memory for basis construction, orthogonalization, projection, frequency solves and transient solves, on fixed hardware with repeated runs. Repeat the focused profile on the NMO_162186 holdout and a second provenance-qualified human morphology. Do not promote production defaults based only on the whole-process resource profile.
