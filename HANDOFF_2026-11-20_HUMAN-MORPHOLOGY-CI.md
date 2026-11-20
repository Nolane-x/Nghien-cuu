# Handoff — human morphology CI passed; continue to passive transfer analysis

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Last verified code/test commit:** `6b99618f8b6d76d6bb0f8c943500db8c6804d2d9`  
**CI:** [44737462769 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737462769)

## Read first
1. `AGENTS.md`
2. `HANDOFF.md`
3. `HANDOFF_2026-11-20_MESH.md`
4. `HANDOFF_2026-11-20_HUMAN-MORPHOLOGY.md`
5. This handoff and `amsn-core/research/HUMAN_MORPHOLOGY_CI_VALIDATION_2026-11-20.md`.
6. `amsn-core/data/human/README.md` for mandatory CC BY 4.0 attribution and sample caveats.

## Current verified status

The real NeuroMorpho NMO_290988 standardized SWC is committed and parsed by CI:
- 8,903 nodes: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, no axon.
- Human temporal middle temporal gyrus, BA21, layer 2–3, pyramidal/principal.
- Dendritic integrity moderate; mesiotemporal sclerosis recorded; shrinkage not reported.
- Not a complete neuron and not a healthy-control sample.

The soma multi-point double-count bug is fixed. Explicit morphometry comparison reproduces the source API values to rounding for this record.

## CI truth

First import run had one stale test (32 passed, one failure) because the old test included soma as a neurite branch point. Fixed it in commit `6b99618f8b6d76d6bb0f8c943500db8c6804d2d9`.

Final GitHub Actions run 44737462769:
- Python 3.12.16 — 33 passed in 0.98 s.
- Python 3.13.18 — 33 passed in 1.54 s.
- Installation, test, compileall and examples passed in both jobs.

## Next concrete task

Implement a reproducible **passive steady-state transfer experiment** on this exact human SWC:
- identify reproducible soma, basal dendrite and apical dendrite injection sites by deterministic SWC path distance;
- record transfer to soma and multiple distal probes;
- use the same generic passive parameters as the existing core and label them not human-fitted;
- use a large but numerically stable implicit step or converged iteration for DC response, without allocating full time-by-compartment traces;
- repeat at several electrotonic mesh levels only after estimating compartment counts/runtime and memory;
- record source-node IDs, branch/type/path distance, current and voltage at each probe, input/transfer resistance, solver timestep/method;
- keep this as a numerical passive experiment, not biological validation.

After that, compare the exact SWC, soma convention and protocols with NEURON or Arbor. Do not fit human channels until a reference reproduction is available.
