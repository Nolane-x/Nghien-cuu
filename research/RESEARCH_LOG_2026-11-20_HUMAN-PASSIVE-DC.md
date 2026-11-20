# Research log — 2026-11-20 — passive DC transfer on real human L2-3 morphology

## Implementation
- Added `CableTree.solve_passive_steady_state()`, a direct Hines solve of the passive linear DC equation without a huge implicit timestep.
- Added dense-matrix equivalence, leak-reversal and input-validation tests.
- Added `examples/human_passive_transfer.py`, selecting soma, basal and apical sites deterministically by geodesic path-distance quantiles.
- Sweeps d_lambda 0.2/0.1/0.05/0.025; 3 injection sites × 5 recording sites × 4 meshes = 60 measurements.
- Stored CI-captured CSV in `amsn-core/results/human_passive_transfer_2026-11-20.csv`.

## Exact CI evidence
Commit: `136b524ef073b3d53771ebf6515a6bbcd19cdc17`
Actions: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737999994
- Python 3.12.16: 38 passed in 1.12 s.
- Python 3.13.18: 38 passed in 1.55 s.
- compileall and all examples passed on both.
- identical measurements at printed precision across both Python versions.

## Site selection
- soma: root node 1;
- basal q75 injection node 3784 at 211.065895 µm;
- apical q75 injection node 5920 at 802.205567 µm;
- probes basal q50 node3355 (140.136824 µm), basal q90 node3814 (258.183183 µm), apical q50 node6897 (346.492715 µm), apical q90 node5164 (930.122423 µm), plus soma.

## Key result
The 8,903-point SWC converts to:
- d_lambda 0.2: 8,903 compartments;
- 0.1: 8,903;
- 0.05: 8,903;
- 0.025: 8,905.

The maximal relative changes between 0.2 and 0.025 across all 15 source/probe pairs:
- input resistance 0.00000161%;
- transfer resistance 0.00000161%;
- transfer ratio 0.00000399% (absolute max 2e-9).

This is not broad evidence of mesh convergence: the mesh graph barely changed. It instead demonstrates that the current SWC-to-cable converter uses one compartment per input node and that this morphology was already finely sampled relative to the passive 100 Hz criterion.

## Representative passive outputs
Input resistance with generic, not human-fitted, defaults:
- soma 46.725504 MΩ;
- basal q75 454.482950 MΩ;
- apical q75 498.173230 MΩ.

All 60 detailed measurement rows are in the CSV and cited report.

## Interpretation / next
Next software improvement is section-based electrical resampling: preserve piecewise-linear morphology, type changes, branch points, arc length, tapered frustum area and integrated axial resistance while reducing electrical control volumes. Do not merely skip SWC points and connect with straight chords. Compare multiple reduced-mesh sizes and later validate against NEURON or Arbor.

## Limits
No biological calibration, no active channels/synapses/axon/calcium/glia, pathology caveat remains, and there is no external simulator comparison yet.
