# Handoff — PRIMA phase profiler implementation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**PR:** [#8 — draft/open](https://github.com/Nolane-x/Nghien-cuu/pull/8)  
**Latest implementation commit:** `fb642cce096a1fb2920c5b30bbaf471c1dd2d3a0`  
**Latest profile workflow at this checkpoint:** [45035222028](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222028)

## Read first

1. `AGENTS.md` — preservation and scientific-integrity requirements.
2. `HANDOFF.md` — current project checkpoint.
3. `amsn-core/examples/prima_phase_profile.py` — phase and solver profiler.
4. `amsn-core/tests/test_prima_phase_profile.py` — deterministic small-cable tests.
5. `.github/workflows/amsn-prima-kernel-phase-profile.yml` — three-morphology CI matrix.
6. `research/RESEARCH_LOG_2026-11-22_PRIMA-PHASE-PROFILER-IMPLEMENTATION.md` — implementation log and validation status.

## What was added

- The profiler calls the existing `prima_reduce_passive_cable_multishift`; it does not copy or alter the production reduction algorithm.
- cProfile extracts function self-time for shifted Hines solves, block orthogonalization, congruence projection and multishift orchestration.
- Other Python self-time and native-function self-time are reported separately. Per-phase cumulative time includes child/native work and overlaps the parent orchestrator; do not sum those cumulative values.
- A same-order **unprofiled builder reference** is captured alongside each cProfile repeat to estimate instrumentation overhead.
- Reduced and full-Hines frequency/transient solver timings use seven matched ports. Full Hines runs as a separate process to keep process-level peak RSS independent from the PRIMA process.
- The GitHub Actions matrix covers three existing morphology fixtures × orders 84/112/168 × two profiled repetitions per candidate, followed by separate full-Hines baselines.

## Experimental settings

- Expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Frequency solves: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Transient: 100 backward-Euler steps, dt 0.1 ms, 10 pA square pulse from step 20 to 39 (2–4 ms), source at the first retained port (soma).
- Reference: full AMSN cable-tree Hines solver; NEURON 9.0.2 is used only for the established SWC/port mapping.
- All simulations remain passive linear RC.

## Validation status — do not overstate

The workflow file, script and test file were read back from GitHub. The Actions interpolation tokens and expected six phase names were checked after correcting an escaping issue. However, the actual profiler CI run [45034830634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45034830634) was still **queued** at the last inspection; its three morphology jobs had not started. The latest-head profile workflow is [45035222028](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222028), and Core CI is [45035222163](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222163). Both were **queued** at the last inspection. The command `python -m pytest -q tests/test_prima_phase_profile.py` has therefore **not yet been observed passing** in Actions. No phase timings or new numerical conclusions have been accepted.

## Next steps

1. Inspect the targeted profile workflow and the core CI on the latest PR head.
2. Fix any real test/runtime failures and rerun only the necessary checks.
3. Verify exact build-phase row counts, output order coverage, finite measurements and the full-Hines process records.
4. Download and hash-check all three profile artifacts; aggregate the per-phase median and dispersion by morphology/order.
5. Interpret cProfile cumulative phase times separately from self-time and report the cProfile/unprofiled overhead ratio.
6. Keep full Hines canonical and production defaults unchanged. Do not merge or mark PR #8 ready without user authorization.

