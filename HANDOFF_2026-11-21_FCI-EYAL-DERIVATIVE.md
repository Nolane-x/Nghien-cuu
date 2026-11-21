# Handoff — FCI Eyal-labelled L2/3 derivatives and Segev morphology validation

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Main commit at handoff creation:** d8902f2ee978f1b9c0a2f53611f448e540d94c25  
**Status:** two direct NeuroMorpho SWC files committed; tests and four-job multi-morphology AC matrix running.

## Read first
1. `AGENTS.md`
2. `HANDOFF.md`
3. This file
4. `research/AMSN_RESEARCH_DOSSIER.md`
5. `amsn-core/research/FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md`
6. `amsn-core/research/references/FCI_EYAL_SOURCE_MANIFEST_2026-11-21.json`
7. `amsn-core/research/HUMAN_PASSIVE_FREQUENCY_RESPONSE_AUDIT_2026-11-21.md`

## New data
- NMO_68174 / cell 1125: `amsn-core/data/human/segev/2013_03_06_cell11_1125_H41_06.CNG.swc`, 12,410 rows, Git blob SHA1 `0659a889d47e44cb67b0685181ce7c8d8ebdc6f6`.
- NMO_68175 / cell 1204: `amsn-core/data/human/segev/2013_03_13_cell03_1204_H42_02.CNG.swc`, 13,758 rows, Git blob SHA1 `5bbfdb0e8c5ab49fb6eae8a873d49b89d8fd551f`.

Both NeuroMorpho records identify human temporal neocortex, Brodmann area 21, layer 2–3 pyramidal/principal neurons; dendrites are moderately complete and axons incomplete. Files are direct NeuroMorpho CNG downloads, unchanged and attributed CC BY 4.0. Details and attributions are in `amsn-core/data/human/segev/README.md`.

## FCI provenance findings
Pinned source `ido4848/fci@75ad8b4d81a7f51bf888b30650c543592340db06`. FCI has two configurations under `human/eyal`, but they are reduced derivatives, not the complete original Eyal 2018 model:
- passive dendrites, active soma + synthetic two-section 45 µm axon;
- Na/Kv scale factors based on a rat Hay L5b exemplar;
- FCI-specific AMPA/NMDA and GABAA settings;
- no explicit 3-D spine neck/head compartments in the simplified HOC.
The FCI repo has no root license and the MOD files have mixed notices. No FCI source code or ASC files were copied. Read `FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md`.

## Current known AMSN baseline
The original NMO_290988 morphology has four passive AC mesh checks (0.5/0.25/0.125/0.0625 µm) against NEURON 9.0.2. At 0.0625 µm, 201,021 NEURON segments; transfer complex median/p95/max error 0.001939/0.112637/0.229692%. The 50 Hz AC phasor vs time-domain steady-state invariant is validated. Core CI run 44882886045 passed 4/4 jobs and 75 tests on Python 3.12 and 3.13.

## New workflows on current main
- Multi-morphology matrix: [44885009077](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077), four jobs (NMO_68174/75 × 0.25/0.125 µm); each job runs full Core tests, then 3 sources × 5 probes × 8 frequencies against NEURON 9.0.2.
- Existing passive AC, fine-mesh, and Core CI were retriggered on the same commit after the new fixtures/test integration.
- Do not state numerical cross-simulator results for the new morphologies until all matrix jobs and raw artifacts pass.

## Separate ModelDB 238347 status
The original Eyal et al. 2018 ModelDB archive remains not downloaded / not integrated. The linked public GitHub repository has only a README; the official legacy Yale/SenseLab 133 MB ZIP timed out. Do not say its mechanisms were acquired.

## Next steps
1. Inspect the four matrix job logs, confirm the exact SWC paths loaded, NEURON sections/segment counts, AMSN compartment count and 120 rows per job.
2. Retrieve all four raw artifacts. Summarize input/transfer complex error by mesh, frequency, source and probe; track absolute impedance for near-zero transfer paths.
3. Compare both cells to NMO_290988 only under explicitly identical passive parameters. This is geometry/numerical cross-validation, not biological parameter fitting.
4. Only after passive stability, create a separate FCI-reduced reproduction. Audit MOD units, temperature, NMODL states and licenses first.
5. Keep the original Eyal 2018 model a separate gate until its official source archive is available.
