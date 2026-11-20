# Handoff — human passive DC transfer completed; build section-based cable resampler next

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Code commit:** `136b524ef073b3d53771ebf6515a6bbcd19cdc17`  
**CI run:** [44737999994 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737999994)

## Read order
1. `AGENTS.md`
2. `HANDOFF.md`
3. `HANDOFF_2026-11-20_MESH.md`
4. `HANDOFF_2026-11-20_HUMAN-MORPHOLOGY-CI.md`
5. This handoff.
6. `amsn-core/research/HUMAN_PASSIVE_DC_TRANSFER_2026-11-20.md`
7. `amsn-core/results/human_passive_transfer_2026-11-20.csv`
8. `amsn-core/data/human/README.md` and provenance JSON.

## Current source morphology
NeuroMorpho NMO_290988 / `1094_Mohan_etal_2015`; human temporal cortex BA21 L2–3 pyramidal/principal cell, soma and dendrites, no axon; dendrites moderate; mesiotemporal sclerosis is recorded; shrinkage not reported. Preserve CC BY attribution in data README. This is not a whole-neuron or healthy-control morphology.

## New DC solver
`CableTree.solve_passive_steady_state(injected_current_a)` solves the exact passive linear DC system with Hines elimination:
[
(G_{leak}+G_{axial})V=G_{leak}E_{leak}+I.
]
It does not approximate DC by taking a huge timestep and does not allocate a time series. It is not valid for nonlinear active-channel/synaptic steady state.

Tests compare it with an independently assembled dense matrix and check leak reversal/invalid inputs.

## Experiment
`examples/human_passive_transfer.py`:
- root soma injection;
- basal type-3 q75 injection;
- apical type-4 q75 injection;
- five probes (soma, basal q50/q90, apical q50/q90);
- 10 pA current;
- passive defaults Ri=0.7 ohm m, Rm=1.0 ohm m², Cm=0.01 F/m², Eleak=-65 mV (generic, not human fitted);
- d_lambda 0.2, 0.1, 0.05, 0.025.

CI measured 60 source/probe/mesh records. Full CSV is in results.

## Verified CI
Run 44737999994:
- Python 3.12.16 — 38 passed in 1.12 s.
- Python 3.13.18 — 38 passed in 1.55 s.
- install, pytest, compileall, all examples passed.
- Python version outputs match at printed precision.

## Key finding
Compartments across the four d_lambda values: 8,903; 8,903; 8,903; 8,905. The 8,903-point input SWC is already finely sampled relative to the 100 Hz passive electrotonic criterion used here. Across 15 source/probe pairs, max relative change between d_lambda 0.2 and 0.025 was <=0.00000399% for transfer ratio. This is not proof of global convergence because the mesh itself hardly changed.

Representative source input resistances with generic passive parameters: soma 46.725504 MΩ, basal q75 454.482950 MΩ, apical q75 498.173230 MΩ. They are geometry/model outputs, not experimental human values.

## Next mandatory implementation
Build section-based electrical resampling that decouples SWC sample points from cable compartments:
1. Identify maximal unbranched chains; always preserve soma and neurite type transitions, branch points and terminals.
2. For each section, use cumulative polyline arc length, not Euclidean chords.
3. Integrate exact piecewise-linear tapered-frustum surface and axial resistance over every original edge.
4. Place electrical control points using physical extent and electrotonic coordinate; preserve original root and branch topology.
5. Compare coarse meshes at 200/500/1,000/2,000 control volumes against the 8,903-point baseline.
6. Measure input resistance and all 15 site transfers; report absolute/relative errors and runtime.
7. Only after this, compare the identical model and morphology in NEURON or Arbor.

Do not just skip every kth SWC node: that would erase bends, shorten arc length and change resistance. Don't call any reduced mesh validated until error tolerances are met.
