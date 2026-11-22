# Handoff — PRIMA high-order resource validator correction

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repo:** https://github.com/Nolane-x/Nghien-cuu  
**Active PR:** [#7](https://github.com/Nolane-x/Nghien-cuu/pull/7)

## Current state

The PR #7 high-order resource benchmark run [45004163258](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45004163258) exposed a deterministic workflow validator bug. The six jobs that had started completed the simulator and resource measurement successfully (process exit status 0), but failed because the validator treated the environment value `56,112` as one model order and expected the impossible ID `six_shift_order56,112`. Their measurement artifacts were uploaded but are not accepted as a passing matrix.

## Correction prepared on this branch

- Parse comma-separated orders into a validated ordered tuple.
- Derive the exact expected model IDs from those orders.
- Verify per-model frequency/transient coverage and each requested six-shift model's achieved rank.
- Select the final requested order as the resource candidate.
- Run a dedicated 16-test validator suite as a preflight dependency before the measurement matrix.

The local validator test command returned **16 passed**. This uses synthetic rows and does not substitute for the forthcoming GitHub Actions run.

## Next steps

1. Inspect the new GitHub Actions preflight result and all resource jobs on the corrected head.
2. Verify uploaded artifacts and aggregate actual elapsed time, CPU and RSS by morphology, mesh, order and repetition.
3. Record the corrective commit SHA and validated run ID here after completion.
4. Keep full Hines canonical; no production defaults change.
5. Continue only passive RC claims until active-channel and nonlinear-synapse experiments are independently established.

## Scope guardrails

The current benchmark is passive linear RC. The three morphology fixtures are not a representative human population. NMO_290988 is a partial dendritic reconstruction without an axon and is associated with mesiotemporal sclerosis. Resource coverage or Cholesky checks do not prove all aspects of biological passivity, and deterministic parameter stress tests are not biological distributions.
