# Handoff — human L2–3 morphology integrated into AMSN

**Checkpoint:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Source SWC blob:** `7f06d10b929ec3ae215cbc0a2e3222e9bbaff46e`

## Read first in a new session
1. `AGENTS.md` — preservation and scientific-integrity rules.
2. `HANDOFF.md` — overall research goals and historical recovery notes.
3. `HANDOFF_2026-11-20_MESH.md` — passive mesh convergence on synthetic morphology.
4. This handoff.
5. `amsn-core/research/HUMAN_MORPHOLOGY_IMPORT_2026-11-20.md`.
6. `amsn-core/data/human/README.md` and adjacent provenance JSON.
7. Check the current main HEAD and the CI run status before editing.

## New real morphology in the repo

File: `amsn-core/data/human/1094_Mohan_etal_2015.CNG.swc`

NeuroMorpho.Org record NMO_290988 / API ID 290988, DeKock archive. Human temporal neocortex, middle temporal gyrus, BA21, layer 2–3, pyramidal/principal cell. 8,903 points: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, no axon.

Crucial caveats: the metadata records mesiotemporal sclerosis; axon is absent; dendritic integrity is moderate; shrinkage is not reported. This is a real dendritic-geometry fixture, not a complete neuron and not a healthy-control cell. NeuroMorpho data terms are CC BY 4.0; preserve the three citations in the data README.

## Structural and morphometry checks

The file has one root, unique IDs, valid parent links, positive radii, seven numeric fields per row, and no disconnected/cyclic points.

An explicit distal-node cylinder convention reproduces this record's API:
- length 12,610.981 µm (API 12,611.0);
- surface 22,768.848 µm² (API 22,768.8);
- volume 4,826.466 µm³ (API 4,826.47);
- soma type-1 frustum surface 921.346 µm² (API 921.346);
- 58 neurite bifurcations and 8 stems.
This is empirical reproduction for one record only. AMSN's frustum estimates are separate from this comparator.

## Soma bug fixed

The CNG standard represents this soma using 3 type-1 points. Previous code unconditionally added a sphere at the root, double-counting the multi-point soma. The new code:
- adds a sphere only for a single-point type-1 soma;
- uses type-1 edges for a multi-point soma;
- does not assume soma if the root isn't type 1;
- rejects an explicit root spherical area on multi-point soma;
- excludes soma nodes from neurite bifurcation counts.

## New code/report/tests
- `src/amsn/morphology.py`: fixed multi-point soma handling.
- `src/amsn/morphometrics.py`: explicit distal-cylinder comparator.
- `tests/test_human_morphology.py`: 4 tests.
- `examples/human_morphology_inspect.py`: inspect real fixture.
- `data/human/README.md`, provenance JSON, and research report.
- Root/package README and CI workflow updated.

## Current limits
AMSN is still not a full human neuron digital twin. This fixture lacks an axon and has moderate dendritic completeness; there are no associated electrical parameters, synaptic maps or matched voltage traces. No cell-specific ion-channel fitting, human electrophysiology reproduction or cross-simulator comparison has yet been performed.

## Next concrete work
1. Check the CI outcome for the commit that imports the SWC; fix actual failures before claiming success.
2. Compare the multi-point soma and multiple dendritic-stem cable conversion against NEURON or Arbor using the same SWC.
3. Run passive mesh convergence with multiple stimulation/recording locations on this real morphology.
4. Select another human L2–3 reconstruction with axon and stronger completeness, retaining pathology and shrinkage caveats.
5. Reproduce Eyal et al. 2018 / ModelDB 238347 unchanged before fitting channels.
6. Then add active dendritic conductances, synaptic kinetics, and causal calcium-to-plasticity coupling.

Never call this record a whole-neuron twin or healthy-control morphology.
