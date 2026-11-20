# Research log — 2026-11-20 — section-based electrical resampling

## Objective
Reduce the 8,903-control-volume cable generated from a real human temporal L2–3 SWC while preserving anatomical polyline geometry and selected passive DC transfers.

## Implementation
Added `amsn-core/src/amsn/sectioned.py`:
- splits SWC into 140 unbranched sections at branch points, terminals, neurite type transitions and optional protected sites;
- preserves all original SWC nodes through a nearest-control-point map with per-node path-distance error;
- keeps selected injection/probe nodes exact;
- resamples with combined physical-length and electrotonic-extent limits;
- integrates original polyline arc length, tapered frustum surface, axial factor integral and electrotonic distance piecewise over the original SWC edges;
- avoids replacing bent morphology with Euclidean chords;
- returns per-edge geometry integrals for validation.

Added:
- `amsn-core/tests/test_sectioned.py` (5 tests, including real human fixture);
- `amsn-core/examples/human_sectioned_mesh_sensitivity.py`;
- package README and CI workflow update.

## Exact method
For a linearly tapered SWC edge:
- lateral area: pi*(r0+r1)*sqrt(L²+(r1-r0)²);
- axial geometry factor: integral(ds/(pi*r²)) = L/(pi*r0*r1);
- electrical edge metrics are the sum of these integrals across all original polyline edge pieces.
Total path length, surface area and axial factor are preserved to numerical tolerance in tests. Membrane area is distributed between adjacent control volumes by midpoint split; that lumped allocation is approximate.

## Measurement setup
- reference cable: morphology.to_cable_tree(), 8,903 compartments;
- d_lambda=0.1, reference frequency 100 Hz;
- physical caps: 100, 50, 25 and 12.5 µm;
- generic passive defaults (not human fitted): Ri=.7 ohm*m, Rm=1 ohm*m², Cm=.01 F/m², Eleak=-65mV;
- 10pA injection;
- 3 sources (soma1, basal q75 3784, apical q75 5920) × 5 probes (soma1, basal q50 3355, basal q90 3814, apical q50 6897, apical q90 5164) = 15 pairs per mesh, 60 rows total;
- all 7 selected nodes protected and exact.

## Results
Compartments: baseline 8,903; sectioned 700, 822, 1,062, 1,565 respectively. Reductions 92.14%, 90.77%, 88.07%, 82.42%.

Max relative errors against fine baseline across all 15 pairs:
- 100µm: Rin .041690%, transfer R .043481%, transfer ratio .049176%;
- 50µm: Rin .041749%, transfer R .043540%, transfer ratio .049016%;
- 25µm: Rin .041560%, transfer R .043448%, transfer ratio .044964%;
- 12.5µm: Rin .010265%, transfer R .011462%, transfer ratio .011149%.

Max mapping error over all original SWC samples: 17.881, 17.881, 12.247, 6.237 µm. Selected input/output nodes mapping error is 0. Max electrical edge and electrotonic bound are recorded in the full report.

## CI evidence
Code commit `2c41c821fbb9aa410fe0d5488d0365342989cdc7`.
GitHub Actions run `44739746176` succeeded:
- Python 3.12.16: 43 passed in 1.49s.
- Python 3.13.18: 43 passed in 1.13s.
- install, compileall and all examples passed.
- exactly 60 output data rows per matrix job; all values identical between Python versions at reported precision.
Raw CSV saved in `amsn-core/results/human_sectioned_mesh_sensitivity_2026-11-20.csv`.

## Interpretation / limits
Encouraging reduction for this single partial morphology and passive DC setup. Reference is the full SWC-node discretization, not experimental truth. No active channels, transient EPSPs, spikes, calcium, synapses, glia, human parameter calibration or cross-simulator comparison yet.

## Next
Run same morphology/passive setup in NEURON or Arbor. Then transient passive step/current protocols at multiple positions; only then introduce active dendritic mechanisms.
