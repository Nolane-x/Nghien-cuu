# Research log — fix PRIMA resource-benchmark order-list validation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/prima-basis-transfer-protocol-robustness-2026-11-22`  
**Parent checkpoint:** `bd3ceda901c85d48aa628ef9b408297075f546c9`

## Question and diagnosis

Why did the current PR #7 high-order resource benchmark complete its simulations but mark the first six jobs failed during coverage validation?

The logs for run [45004163258](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45004163258) show that the six jobs completed the full resource-measurement step with process exit status 0. Their CSVs and process logs were uploaded. The following validation step failed with:

```
RuntimeError: model identity coverage mismatch
```

The workflow read `AMSN_PRIMA_EXTENDED_ORDERS=56,112` as one literal order string, then expected a model named `six_shift_order56,112`. The actual sweep correctly emitted the control model `four_shift_order56_control` and separate six-shift models `six_shift_order56` and `six_shift_order112`. The failure is a validator parsing bug, not an NEURON installation failure or a simulation exit failure. However, those six jobs must not be counted as validated resource measurements until the corrected validator passes.

## Work completed

- Added `research/prima_resource_benchmark_validator.py` with strict comma-separated order parsing, ordered/unique/positive checks, exact model identity checks, per-model metric coverage checks and requested-versus-realized PRIMA rank validation.
- Updated the high-order benchmark workflow to parse all requested orders, derive the expected candidate model from the last order, and use the shared validator.
- Added a dedicated `validator-tests` job so parsing and artifact-coverage tests run once before the 36 resource measurements.
- Added 16 unit tests covering valid two-/three-order matrices, whitespace, empty/non-integer/duplicate/unsorted/non-positive order lists, model identity, missing rows and wrong realized rank.
- No production defaults, model equations, biological parameters or Hines reference behavior were changed.

## Local validation actually run

Command:

```bash
PYTHONPATH=/tmp/prima-validator-check pytest -q /tmp/prima-validator-check/tests
```

Result: **16 passed** (Python test environment in the current container). The tests used synthetic CSV-shaped rows; they validate parser/coverage logic, not the numerical neuron model.

## GitHub Actions status at the time of this log

- The failed run [45004163258](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45004163258) is diagnostic only: first six resource measurements executed and uploaded artifacts, but validator failure means the benchmark matrix is not a completed/accepted run.
- The corrected workflow commit must trigger a fresh preflight plus resource matrix. New workflow results are pending; do not claim the 36-job matrix is green until the new run is completed and its artifacts/coverage are inspected.
- The independent core CI retry [45004163087](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45004163087) is also being checked separately.

## Limitations and next experiment

The benchmark remains passive linear RC PRIMA reduction against the full Hines reference. Passing this validator will establish artifact coverage and requested numerical model order only; it will not establish active-channel, nonlinear-synapse or biological generalization validity. After the corrected benchmark completes, inspect every job, aggregate repeated measurements by morphology/order/mesh, compare artifacts and SHA-256 digests, and append the verified outcomes and resulting Git commit SHA to this research record.
