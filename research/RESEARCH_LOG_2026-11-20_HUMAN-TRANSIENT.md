# Research log — 2026-11-20 — passive transient cross-validation

## Objective
Compare AMSN's section-reduced passive cable against NEURON 9.0.2 transient responses, for a 5 ms current pulse and a sustained current step, on the same NeuroMorpho human L2–3 morphology and source/probe sites.

## Implementation
Added `amsn-core/examples/human_transient_cross_validation.py` and a GitHub Actions workflow step.
- Uses only the 690-compartment sectioned AMSN tree to keep trace memory under control.
- NEURON uses 125 Import3D sections / 2,637 segments, same passive settings and same Import3D-compatible soma/wire normalization.
- Both use dt 0.025 ms, 10 pA input; pulse 5ms or step (clamp duration 300ms, observed through 250ms).
- Three source locations × five probes × nine measurement times × two protocols = 270 rows.
- All seven anatomical site nodes are protected in the AMSN mesh.

## Reporting correction
The first summary version filtered transfer-ratio relative errors by probe amplitude, not source amplitude. This allowed ratios with near-zero source denominators to inflate absolute error output. The source script was corrected:
- transfer-ratio absolute/RMS samples require NEURON source deflection >=0.02mV;
- transfer-ratio relative samples also require |NEURON ratio|>=0.05.
Raw traces are unchanged.

## CI evidence
Code commit: `c597a752d144883827ad828a29505016d0ad87ae`.
Reporting-fix commit: `d3099b6f4394052149b8121bfd3928a843d84cd3`.
Actions run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44747863750
- Python 3.12: 46 tests passed; NEURON DC, convergence and transient jobs success.
- Python 3.13: 46 tests passed; NEURON DC, convergence and transient jobs success.
- 270 rows each; raw rows identical across Python versions.

## Results
AMSN transient uses 690 electrical compartments; NEURON uses 2,637 segments.
- Pulse 5ms: source max abs 0.021546895mV, RMS 0.007805051mV, max relative 0.666739%; probe max abs 0.035795496mV, RMS 0.004629863mV, max relative 1.478139%.
- Step: source max abs 0.021546895mV, RMS 0.016196218mV, max relative 0.666739%; probe max abs 0.035795496mV, RMS 0.007084001mV, max relative 1.478139%.
- Transfer ratio: pulse max abs 0.007172235, RMS 0.001131877; step max abs 0.007172235, RMS 0.000864943. Relative ratio max 2.696737%, only where reference source deflection >=0.02mV and reference ratio >=0.05.

Worst probe deflection: basal q75 injection node3784 to basal q90 probe node3814 at 1ms; NEURON 2.421658962mV vs AMSN 2.385863466mV.
Worst absolute ratio difference: same source/probe/time; NEURON .878039466, AMSN .870867231.
Worst relative ratio difference: soma source to apical q50 probe at 1ms; NEURON .058971315, AMSN .060561616.

## Raw data
270-row CSV is committed at `amsn-core/results/human_transient_cross_validation_2026-11-20.csv`.

## Limitations
One partial human cell, no axon, moderate dendritic completeness, disease-context metadata, generic passive parameters. These are current-clamp transient tests, not synaptic conductance or active channel validation. Only sectioned AMSN transient was run due full-tree trace memory.

## Next
1. AMSN timestep refinement 0.025 / .0125 / .00625ms.
2. AMPA-like conductance transient vs NEURON.
3. A second license-cleared human L2–3 morphology.
4. Later active dendritic channels and synapses after passive/transient validation.
