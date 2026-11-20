# Handoff — AMSN electrotonic discretization checkpoint

**Checkpoint:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation:** `amsn-core/`  
**New module:** `amsn-core/src/amsn/discretization.py`

## Read first

1. `AGENTS.md`
2. `HANDOFF.md` for original scientific goals and recovery history.
3. `HANDOFF_2026-11-20_AMSN-CORE.md` for the existing v0.1.0 numerical core.
4. This file for the latest addition.
5. `amsn-core/research/ELECTROTONIC_DISCRETIZATION_2026-11-20.md`.
6. `research/RESEARCH_LOG_2026-11-20_ELECTROTONIC.md`.
7. Check current main HEAD, tree and workflow result before editing.

## Current source-of-truth correction

The current repository includes executable source under `amsn-core/`, tests, examples, package metadata, a source archive and a GitHub Actions workflow. Some earlier paragraphs in the original `HANDOFF.md` accurately described the repository at its initial empty-repo checkpoint but are historical. The newer `HANDOFF_2026-11-20_AMSN-CORE.md` and this file describe the implementation that now exists.

## New implementation

`amsn-core/src/amsn/discretization.py` adds:

- `ac_length_constant_um(...)`: passive high-frequency AC length constant, using explicit SI parameters and micrometre diameters.
- `electrotonic_length_um(...)`: analytic integral of `dx/lambda_f` on a linearly tapered frustum.
- `edge_subdivision_fractions(...)`: union of physical-length cuts and equally spaced electrotonic-distance cuts.
- `refine_swc_morphology(...)`: non-mutating SWC refinement preserving original IDs, branch structure and interpolated taper.
- `to_electrotonic_cable_tree(...)`: convenience conversion to the passive cable tree.

Defaults: `max_electrotonic_length=0.1`, `reference_frequency_hz=100`, `Ri=0.7 ohm*m`, `Cm=0.01 F/m²`. They match the NEURON d_lambda example frequency/ratio and AMSN's generic passive defaults, but are not human L2/3-fitted values. Every run should record any overridden parameters.

## Local verification

- Python 3.13.5, NumPy 2.3.5, pytest 9.0.2, Linux x86_64.
- New standalone tests: 7 passed in 0.08 s.
- `compileall` passed.
- Local testing used a lightweight morphology-compatible test double because the shell could not resolve github.com. It did not execute the existing full AMSN package.
- GitHub Actions full-suite result is pending at the time this handoff was written. Read the workflow run and update this handoff only after checking its actual conclusion/logs.

## Scientific status

This is a numerical discretization tool, not biological validation. The AC length constant approximation is passive/high-frequency and does not establish convergence for nonlinear channels, synaptic integration, spikes, calcium or metabolism. The example uses synthetic morphology. No human reconstruction, NEURON comparison or Eyal 2018 reproduction is included.

## Next required task

1. Check this commit's GitHub Actions result and fix any integration failures.
2. Add a successive-mesh convergence experiment to the passive cable solver: `d_lambda = 0.2, 0.1, 0.05` plus physical-length controls. Measure input resistance, membrane time constant, transfer ratio and runtime.
3. Test more taper profiles and branch points.
4. Obtain a human SWC with explicit redistribution permission and metadata; audit soma representation before using it.
5. Reproduce Eyal et al. 2018/ModelDB 238347 unchanged under a compatible NEURON version. Do not claim this is done.
6. Only after a passive reference baseline is stable, add active dendritic channels, synaptic kinetics and causal calcium-to-plasticity coupling.

Always preserve previous commits and negative results. Never claim the new code is human-calibrated or validated from the synthetic tests.
