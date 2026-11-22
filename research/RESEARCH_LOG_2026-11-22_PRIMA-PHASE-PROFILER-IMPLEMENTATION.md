# Research log — PRIMA kernel phase profiler implementation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**PR:** [#8 — draft/open](https://github.com/Nolane-x/Nghien-cuu/pull/8)  
**Profiler code checkpoint:** `9050c6a075c12af564fa86c0e5c2b1ce1564eac4`  
**Targeted Actions run:** [45034830634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45034830634)

## Question and hypothesis

The completed high-order resource benchmark measured the whole audit process, which mixed PRIMA construction with reference-model work. The next question is how much time is spent in the existing PRIMA build stages and in the reduced frequency/transient solvers, compared with a full-Hines baseline.

Hypothesis: larger reduced orders increase some build and solve costs, but the current whole-process resource measurements cannot identify which PRIMA stage is responsible. Profiling must observe the existing builder rather than reimplement it, and Hines memory must be measured outside the PRIMA process.

## Sources examined

- `AGENTS.md`, `HANDOFF.md`, `HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md`.
- `amsn-core/src/amsn/prima.py` — actual multishift basis construction, Hines shifted solve, orthogonalization and congruence projection.
- `amsn-core/src/amsn/cable.py` — full-tree frequency and transient Hines solvers.
- `amsn-core/examples/human_prima_shift_order_pareto.py` — established seven-port mapping and PRIMA candidate protocol.
- `amsn-core/examples/neuron_cross_validation.py` and `human_fine_mesh_passive_dc_audit.py` — Import3D mapping and established source/probe sites.
- Completed resource benchmark report and its whole-process measurement limitations.

## Implementation performed

1. Added `amsn-core/examples/prima_phase_profile.py`. It wraps the existing `prima_reduce_passive_cable_multishift` call with cProfile; it does not duplicate the algorithm.
2. Extracted function-level timing for shifted Hines solves, block orthogonalization, congruence projection and multishift orchestration.
3. Separated named Python function self-time, other Python self-time and native-function self-time. Per-phase cumulative time includes nested work and overlaps with the parent orchestrator; it must not be summed.
4. Added a same-order unprofiled builder reference for each order to estimate cProfile instrumentation overhead.
5. Added reduced frequency-domain timing at six frequencies and reduced transient timing over 100 backward-Euler steps.
6. Added a full-Hines frequency/transient baseline in a separate process. The same seven matched port nodes are used; the independent process allows `/usr/bin/time` peak RSS to be attributed separately.
7. Added deterministic tests on a four-compartment synthetic cable and a GitHub Actions matrix for three human morphology fixtures, orders 84/112/168 and two profiled repetitions.

## Fixed experimental settings

- Morphologies: NMO_68174_cell1125 (12,410 SWC records), NMO_68175_cell1204 (13,758 records) and NMO_290988_Mohan2015 (8,903 records).
- NEURON 9.0.2 is used to map the established seven source/probe nodes; the simulated AMSN tree is built from the same raw SWC.
- Shift frequencies: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Evaluation frequencies: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Transient: 100 steps, dt 0.1 ms, 10 pA square pulse over 2–4 ms, applied at the first retained port (soma).
- PRIMA build: two cProfile repeats per order, plus one same-order unprofiled reference. Full Hines is timed in its own process with two repetitions.

## Test and CI status

The workflow and source files were read back from GitHub after each edit. The interpolation-token escaping issue in the workflow was corrected, and validation was updated to expect six phase groups per order/repetition.

At the final checkpoint, Actions run [45034830634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45034830634) was **queued**, with three morphology jobs waiting for runners. The test command is:

```bash
python -m pytest -q tests/test_prima_phase_profile.py
```

This command has **not yet been observed passing** in GitHub Actions. No phase timing, process-RSS result or performance conclusion is reported as validated. The existing completed 36-artifact resource benchmark remains the last accepted resource result.

## Limitations and interpretation rules

- cProfile changes execution cost. The same-order unprofiled build records an overhead reference, but phase-level measurements remain profiler-instrumented.
- Named function self-time excludes child calls. Cumulative time includes nested NumPy/native calls and overlaps with the parent orchestration; never sum parent and child cumulative values.
- Native-function self-time is separated but not assigned back to individual phases. Use phase cumulative time to inspect inclusive stage cost.
- Frequency and transient measurements are timing audits, not new numerical-accuracy validation. The full-Hines path and reduced path are measured separately; their response equivalence remains governed by existing validated reports.
- These are passive linear-RC experiments only. No active-channel, nonlinear-synapse, calcium, plasticity, gene, metabolism or cognition validation is implied.

## Files added or updated

- `amsn-core/examples/prima_phase_profile.py`
- `amsn-core/tests/test_prima_phase_profile.py`
- `.github/workflows/amsn-prima-kernel-phase-profile.yml`
- `HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md`
- `HANDOFF.md`
- `README.md`

## Commit and next concrete work

Profiler implementation checkpoint: `9050c6a075c12af564fa86c0e5c2b1ce1564eac4`. This log and handoff are committed together in the documentation checkpoint recorded by the branch's latest commit.

Next: inspect the targeted phase-profile workflow and core CI on the latest PR head, fix test/runtime failures, download and inspect all three profile artifacts, then summarize median/dispersion per phase and order. Keep full Hines canonical and production defaults unchanged.
