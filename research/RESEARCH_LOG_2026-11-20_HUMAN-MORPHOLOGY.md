# Research log — 2026-11-20 — first human L2-3 morphology

## Work completed
Retrieved and validated the standardized NeuroMorpho SWC record NMO_290988 (`1094_Mohan_etal_2015`) as a real dendritic-geometry fixture.

## Provenance and scope
- NeuroMorpho v8.7; CC BY 4.0 terms.
- Human temporal neocortex, middle temporal gyrus, BA21, layer 2–3, pyramidal/principal cell.
- Soma + basal/apical dendrites; no axon; dendritic integrity rated moderate.
- Metadata records mesiotemporal sclerosis; shrinkage not reported. Not a healthy-control or complete-neuron model.
- Mandatory citation details in `amsn-core/data/human/README.md`.
- Exact original standardized SWC Git blob SHA: `7f06d10b929ec3ae215cbc0a2e3222e9bbaff46e`.

## File integrity
8,903 rows; 7 numeric fields each; unique IDs; one root; valid parent references; positive radii; no cycles or disconnected nodes. Type counts: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, 0 axon.

## Morphometry reproduced
- Neurite length 12,610.981 µm vs API 12,611.0.
- Distal-cylinder neurite surface 22,768.848 µm² vs API 22,768.8.
- Distal-cylinder volume 4,826.466 µm³ vs API 4,826.47.
- Soma-edge frustum surface 921.346 µm² vs API 921.346.
- 58 non-soma bifurcations and 8 stems.
These formulas reproduce one record's API values and are not asserted as a universal NeuroMorpho formula.

## Implementation work
- Fixed multi-point soma area double-counting in `morphology.py`.
- Added explicit `distal_cylinder_morphometrics` comparator.
- Added tests for source tree, soma-area behavior and API values.
- Added inspection example.
- Added attribution README, provenance JSON and full research report.

## CI
Triggered by the implementation/data commit. Check both Python matrix jobs and capture actual pytest/example output before marking verified.

## Next
1. Validate parser/tests on GitHub Actions.
2. Compare soma and branch electrical geometry with NEURON/Arbor on the same file.
3. Run multi-location passive convergence on the real morphology.
4. Locate a second L2–3 morphology with axon and stronger completeness; keep disease/shrinkage annotations.
5. Reproduce Eyal 2018 / ModelDB 238347 unchanged before new conductance fitting.
