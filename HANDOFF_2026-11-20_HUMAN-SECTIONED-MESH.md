# Handoff — section-based cable resampling validated against full SWC passive DC reference

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** `2c41c821fbb9aa410fe0d5488d0365342989cdc7`  
**CI:** [run 44739746176 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44739746176)

## Read order for a new session
1. `AGENTS.md`
2. `HANDOFF.md` (broad goals and old recovery context).
3. `HANDOFF_2026-11-20_HUMAN-MORPHOLOGY-CI.md`.
4. `HANDOFF_2026-11-20_HUMAN-PASSIVE-DC.md`.
5. This file — latest checkpoint.
6. `amsn-core/research/SECTIONED_HUMAN_MORPHOLOGY_2026-11-20.md`.
7. `amsn-core/results/human_sectioned_mesh_sensitivity_2026-11-20.csv`.
8. `amsn-core/data/human/README.md` for source citations and cell caveats.

## What was added

`amsn-core/src/amsn/sectioned.py` decouples the detailed SWC point tree from the electrical compartment tree. It:
- creates 140 unbranched sections;
- preserves branch points, terminals, type transitions and caller-protected nodes;
- keeps the original piecewise-linear polyline, integrating rather than chord-connecting;
- sums exact arc length, tapered frustum area and axial geometry factor on every original SWC edge;
- places electrical samples by physical and electrotonic limits;
- returns mappings and per-edge metrics for all original morphology points.

API: `to_sectioned_cable_tree(..., max_segment_length_um=..., max_electrotonic_length=..., preserve_node_ids=...)`.

A caller can protect stimulus/recording SWC IDs so they are represented exactly. All 7 sites in the current experiment are protected.

## Results

Source cell NMO_290988, `1094_Mohan_etal_2015`: partial human L2–3 temporal cortical pyramidal reconstruction; 8,903 points, no axon, dendrites moderate, metadata records mesiotemporal sclerosis, shrinkage not reported. It is not a complete or healthy-control neuron.

Reference: existing fine SWC-node cable (8,903 compartments), not an experimentally validated biological trace. Passive parameters are generic defaults, not human-fitted.

| Physical max | Compartments | Reduction | Max input R error | Max transfer R error | Max transfer ratio error |
|---:|---:|---:|---:|---:|---:|
| 100 µm | 700 | 92.14% | .041690% | .043481% | .049176% |
| 50 µm | 822 | 90.77% | .041749% | .043540% | .049016% |
| 25 µm | 1,062 | 88.07% | .041560% | .043448% | .044964% |
| 12.5 µm | 1,565 | 82.42% | .010265% | .011462% | .011149% |

Four meshes × 15 site pairs = 60 data rows in the CSV. In both Python versions, electrical data matched at reported precision.

## Validation
CI run 44739746176:
- Python 3.12.16: 43 passed in 1.49 s.
- Python 3.13.18: 43 passed in 1.13 s.
- compileall and all examples passed.
- tests check original edge coverage, topology preservation, all node mappings, physical/electrotonic bounds, total path length, total membrane surface and summed axial integral.
- real morphology integration test reduces below 2,000 compartments while preserving total geometry and protected sites.

## Key interpretation
A 700-compartment electrical tree gave <0.05% maximum relative error across 15 passive DC site pairs compared with the 8,903-compartment fine mesh, for this one morphology and parameter set. This suggests section-based resampling is promising for this passive DC problem.

Do not generalize this to action potentials, EPSPs, frequency response, calcium, synapses or other morphologies. The fine SWC-node cable is a numerical reference, not experimental truth. Lumped membrane-area distribution changes when compartments are merged. The cell has disease-context and completeness caveats.

## Next tasks
1. Build/run the identical SWC and passive parameters in NEURON or Arbor; compare DC transfer and geometry conventions.
2. Add transient passive response comparisons (step current/EPSP-like current) and frequency-dependent impedance, using protected input/output sites.
3. Run another license-cleared human L2–3 morphology with its own metadata.
4. Only after reference simulator agreement, add active dendritic channels and local spikes/calcium.

Never call the model biologically validated from this numerical reduction alone.
