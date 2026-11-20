# Handoff — AMSN passive mesh validation checkpoint

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Latest code commit at this checkpoint:** `0c4871df50e83e95f8446cbfe6058023312057da`  
**CI run:** [44735191202 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44735191202)

## Read first in a new session

1. `AGENTS.md` — preservation and scientific-integrity requirements.
2. `HANDOFF.md` — broad research goals and historical recovery context. Its initial empty-source note is historical; the new core was built in later commits.
3. `HANDOFF_2026-11-20_AMSN-CORE.md` — implementation of the initial runnable numerical core.
4. `HANDOFF_2026-11-20_ELECTROTONIC.md` — derivation and API for electrotonic mesh refinement.
5. This file — latest mesh-sensitivity experiment and exact next actions.
6. `amsn-core/README.md`, `amsn-core/research/PASSIVE_MESH_CONVERGENCE_2026-11-20.md`, and `research/RESEARCH_LOG_2026-11-20_MESH.md`.
7. Check current main HEAD, tree and Actions status before editing.

## Current state

The repo contains an executable Python package under `amsn-core/`. It was created anew after the previous Alpha source directories were found empty; it is not recovered old Alpha code.

The core currently contains:
- strict SWC parsing and morphology summaries;
- vertex-centred 1-D SWC-to-cable conversion;
- SI-unit helpers;
- passive branched cable simulation using backward Euler and Hines elimination;
- classic HH1952 kinetics used only as a squid-axon numerical smoke test;
- electrotonic mesh refinement for tapered SWC edges.

It is **not** a complete human cortical neuron model. It does not yet reproduce Eyal et al. 2018 and does not yet include synapses, active human dendritic conductances, calcium, plasticity, gene/protein regulation, ATP metabolism or astrocytes.

## New numerical work in the latest code checkpoint

- `amsn-core/src/amsn/discretization.py`: passive high-frequency AC length constant, analytic integrated electrotonic distance for a linearly tapered edge, union of physical and electrotonic cuts, non-mutating SWC refinement and wrapper to a cable tree.
- `amsn-core/tests/test_discretization.py`: test that tighter electrotonic limits do not reduce node count; the four tested values are 0.2, 0.1, 0.05, 0.025.
- `amsn-core/examples/electrotonic_refinement.py`: synthetic example now visibly refines 7 nodes to 18 with 5 µm physical extent, retaining total path length and area summary.
- `amsn-core/examples/passive_mesh_convergence.py`: four-level passive experiment.
- `amsn-core/research/PASSIVE_MESH_CONVERGENCE_2026-11-20.md`: full report.
- `amsn-core/results/passive_mesh_convergence_2026-11-20.csv`: raw numbers from both CI Python jobs.

## Verified automated results

GitHub Actions run 44735191202:
- Python 3.12.16: 29 tests passed in 1.10 s.
- Python 3.13.18: 29 tests passed in 1.35 s.
- Both jobs completed install, pytest, compileall and all examples successfully.
- CI used NumPy 2.5.5 and pytest 9.2.0.

Synthetic mesh values:

| d_lambda | Compartments | Input resistance | Distal/root voltage ratio |
|---:|---:|---:|---:|
| 0.2 | 13 | 77.6958 MΩ | 0.90595764 |
| 0.1 | 22 | 77.6752 MΩ | 0.90658815 |
| 0.05 | 41 | 77.6435 MΩ | 0.90725289 |
| 0.025 | 80 | 77.6361 MΩ | 0.90740885 |

Between d_lambda 0.05 and 0.025, input resistance changed by about 0.00953% and transfer ratio changed by about 0.0156 percentage points. This is a narrow numerical stability finding for one synthetic morphology, generic passive parameters and one injection protocol. It is not biological validation.

## Scientific limits

- d_lambda uses a passive high-frequency AC approximation. It is a spatial discretization heuristic; time-domain accuracy must still be checked against the observables of interest.
- AMSN treats each SWC edge as a straight line with linear taper between endpoint diameters. It does not reproduce NEURON's full 3-D section interpolation logic exactly.
- No licensed human morphology was used.
- No cross-simulator validation against NEURON or Arbor has been executed.
- No human L2/3 parameters have been fitted.
- Runtime values are single hosted-runner timings only.

## Next concrete tasks — do not skip ahead to gene expression

1. **Multi-location passive convergence:** inject at multiple branch locations and record transfer resistance at several distal probes; compare d_lambda 0.2/0.1/0.05/0.025.
2. **Passive analytical check:** add a validation against an analytic sealed cylinder and a branch-network linear solve, including input resistance and time constant, not just finiteness.
3. **Human morphology provenance:** locate an SWC reconstruction that is explicitly redistributable, capture metadata/license, audit soma convention and only then place it in the repo.
4. **Reference simulator:** install a pinned NEURON 8.2.x toolchain in GitHub Actions or a reproducible environment; run a published model unchanged before translating/reimplementing mechanisms.
5. **Eyal 2018 / ModelDB 238347:** obtain the original archive, hash it, run its published MOD mechanisms unchanged, capture voltage traces and compare to published protocol outputs. Do not claim this was achieved yet.
6. Only after a validated passive and active electrophysiology baseline, add voltage-dependent dendritic channels and synaptic kinetics, then causal calcium-to-plasticity coupling.

## Preservation instructions

Do not delete or overwrite previous checkpoints. Add a new dated log/report for every substantive experiment. Record actual GitHub Actions output and read the exact current commit before further changes.
