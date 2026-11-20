# AMSN Alpha — Recovery status as of 2026-11-20

## Why this file exists

A prior Alpha README described a substantial executable prototype. A filesystem inspection was performed because the source modules and tests could not be located. This note separates surviving descriptions from executable artifacts that were actually present.

## What was present

| Path | Observed state | Meaning |
|---|---|---|
| `/mnt/data/AMSN_research_dossier_v1.md` | Present, 32,586 bytes, 340 lines | Research/architecture dossier, not executable software |
| `/mnt/data/amsn_alpha/README.md` | Present, 9,341 bytes | A feature and CLI description for “AMSN Alpha 0.2.0a2” |
| `/mnt/data/amsn_alpha/amsn/` | Empty | No Python implementation files found |
| `/mnt/data/amsn_alpha/tests/` | Empty | No test files found |
| `/mnt/data/amsn_alpha/scripts/` | Empty | No scripts found |
| `/mnt/data/amsn_alpha/docs/` | Empty | No documentation files found |
| `/mnt/data/amsn_alpha/results/` | Empty | No results under the project results directory |
| `/mnt/data/amsn_alpha/data/` | Empty | No input datasets under the project data directory |

Three PNGs were found in a temporary mounted location:
- `astrocyte_eaat_sweep.png` — 253,682 bytes
- `amsn_astrocyte_closed_loop.png` — 296,540 bytes
- `amsn_alpha_integrated.png` — 88,397 bytes

They are not in the normal project results folder and no matching source data/code was found next to them in the inspected project. Treat them as orphaned visual artifacts, not as validated or reproducible scientific evidence.

## What the old README claimed

It described, among other things:
- SWC morphology import and morphology coarsening;
- explicit spine neck/head compartments;
- an O(N) implicit Hines tree solver;
- HH and Mainen-style Na/K channel profiles;
- AMPA/NMDA and GABA-A synapses;
- stochastic vesicle release and STDP;
- calcium-dependent and reduced molecular plasticity;
- voltage-gated calcium and SK-like potassium currents;
- calcium diffusion, ER and mitochondrial stores;
- biochemical reactions via SciPy BDF;
- Na/K/ATP feedback and chloride homeostasis;
- optional astrocyte microdomain/glutamate uptake;
- CLI experiments, JSON/NPZ outputs and “69 passing” tests.

These are **claims in a README only** at this checkpoint. With implementation and test directories empty, none of these features or the 69-test result is verified. The README's CLI commands should not be presented as runnable until source is recovered and tested.

## Recovery rules

1. Do not reconstruct source by pretending the previous code still exists.
2. Search only real, authorized backup locations/repositories/Actions artifacts; record provenance and commit SHA.
3. If source cannot be recovered, create a new clean implementation in a separate branch/version, preserving the README and this recovery note as historical records.
4. Start with the smallest validated electrical baseline. Do not attempt to recreate every advertised feature at once.
5. Every new feature must include unit tests, integration tests, numerical checks and scientific references.
6. Never claim passing tests without the actual test output and commit SHA.
7. Preserve any old artifact found; do not overwrite it. Make a copy, hash it, and record where it came from before changing anything.

## Current decision

The research direction is intact, but the prior Alpha executable source is not present in the inspected filesystem. Treat the project as **research dossier recovered; implementation recovery unresolved**. The next defensible step is to reproduce a published human-neuron baseline from its original source and then rebuild AMSN incrementally with tests.
