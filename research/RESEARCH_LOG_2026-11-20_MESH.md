# Research log — 2026-11-20 — passive electrotonic mesh sensitivity

## Objective
Extend the electrotonic SWC refinement with a reproducible mesh-sensitivity experiment. The purpose is to test whether passive observables become less sensitive as the mesh is refined; not to claim biological validation.

## Sources examined
- NEURON 9.0.1 documentation for the d_lambda rule: 100 Hz and d_lambda=0.1 are shown as reasonable example values; the documented implementation uses 3-D diameter samples when available.
- Arbor documentation for maximum-extent discretization policies and the composition/union of policy boundaries.
- Existing AMSN source, tests and CI workflow in the repository.

## Code and experiment
- Added an explicit monotonic mesh-density test for d_lambda 0.2, 0.1, 0.05 and 0.025.
- Expanded the synthetic refinement example to impose a 5 µm physical segment maximum. The example now changes 7 SWC points into 18 electrical nodes.
- Added a four-level passive mesh sweep at d_lambda 0.2, 0.1, 0.05 and 0.025 with 100 pA root current, 150 ms duration and 0.1 ms time step.
- Stored the code output in `amsn-core/results/passive_mesh_convergence_2026-11-20.csv`.
- Wrote the full method/results/limitations report to `amsn-core/research/PASSIVE_MESH_CONVERGENCE_2026-11-20.md`.

## Actual CI results
GitHub Actions: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44735191202

- Python 3.12.16: 29 passed in 1.10 s.
- Python 3.13.18: 29 passed in 1.35 s.
- Both matrix jobs passed installation, test suite, compileall and all examples.
- NumPy 2.5.5; pytest 9.2.0.
- Four mesh levels returned 13, 22, 41 and 80 compartments. Input resistance decreased from 77.6958 to 77.6361 MΩ; distal/root ratio increased from 0.90595764 to 0.90740885.
- Between the two finest meshes (0.05 and 0.025), input resistance changed by about 0.00953%, and distal/root ratio by about 0.0156 percentage points.
- The 7-point synthetic geometry example refined to 18 points while preserving reported total path length (67.941125 µm) and estimated membrane area (1213.926292 µm²).

## Interpretation
This supports numerical stability of these two passive observables for this one synthetic morphology, generic parameter set and stimulus. It does not demonstrate convergence of all state variables, active responses or a biological neuron. CI wall times were single observations and are not formal benchmarks.

## Limitations
- Synthetic SWC only; no human reconstruction or biological metadata.
- Generic passive defaults, no human calibration.
- One-dimensional passive cable, spherical root-area fallback.
- No active conductances, synapses, calcium, metabolism or glia.
- No independent NEURON/Arbor comparison.
- No stochastic seed was required.

## Next experiment
Use a morphology with clear redistribution permission; conduct a multi-morphology and multi-location passive convergence sweep. Compare input resistance, time constant, transfer resistance and passive EPSP attenuation across mesh levels. Then reproduce a published Eyal et al. human L2/3 baseline unchanged in NEURON before adding new mechanisms.

## Commits
- Electrotonic refinement code: `ece904c04a6c2beccda78933ddc5e8c3e7b453c2`.
- Expanded mesh sweep and test: `0c4871df50e83e95f8446cbfe6058023312057da`.
- Report/CSV/handoff will be included in a subsequent documentation checkpoint.
