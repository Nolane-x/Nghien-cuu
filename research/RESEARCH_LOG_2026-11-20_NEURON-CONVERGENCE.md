# Research log — 2026-11-20 — NEURON temporal/spatial convergence sweep

## Question
How much do passive NEURON traces change when fixed timestep and maximum physical segment size are refined independently on the same human L2–3 SWC and source/probe locations?

## Implementation
Added examples/neuron_convergence.py and wired it into the pinned NEURON 9.0.2 CI job. The sweep:
- imports the same NMO_290988 standardized SWC with Import3D;
- preserves the same three sources and five probes;
- tests max segment limits 5.0 and 2.5 µm;
- tests fixed timesteps 0.025 and 0.0125 ms;
- records 9 checkpoints (1,2,5,10,20,50,100,200,250ms);
- produces 540 rows per Python matrix job;
- prints isolated time and spatial sensitivity summaries.

## CI
Commit: d6c67083c727e862356a7268671d2fa79bf01a3b
Actions: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44746105586
- Python 3.12.16 tests: 46 passed.
- Python 3.13.18 tests: 46 passed.
- NEURON convergence job succeeded for both versions.
- 540 rows on each Python version; values identical at printed precision.

## Configurations and segment counts
- cap 5 µm, dt 0.025 ms: 2,637 segments;
- cap 5 µm, dt 0.0125 ms: 2,637 segments;
- cap 2.5 µm, dt 0.025 ms: 5,149 segments;
- cap 2.5 µm, dt 0.0125 ms: 5,149 segments.
All segment configurations report total area 23,338.438806144 µm².

## Temporal timestep sensitivity
At cap5: max absolute 0.008936221 mV, RMS 0.000982751 mV, max relative 0.367656% for reference deflection ≥0.05mV.
At cap2.5: max absolute 0.009017677 mV, RMS 0.000991579 mV, max relative 0.372450%.

## Spatial segment sensitivity
At dt .025: max absolute 0.009498791 mV, RMS 0.001421479 mV, max relative 0.738397%.
At dt .0125: max absolute 0.009417335 mV, RMS 0.001417490 mV, max relative 0.740058%.

## Combined coarse/fine
5µm/.025ms vs 2.5µm/.0125ms: max absolute 0.006348748mV, RMS 0.001329536mV, max relative 0.734900%. Combined error can exhibit cancellation; do not use it to assert one coarse mesh is more accurate than a one-factor comparison.

## Raw output
540-row CSV stored at amsn-core/results/neuron_passive_convergence_2026-11-20.csv. The workflow preserves complete stdout as an artifact for Python 3.12 and 3.13.

## Limitations
Only one partial human morphology, generic passive params, passive step current, finite number of segment/time levels. This is reference-simulator convergence, not biological validation or AMSN transient cross-validation.

## Next
Compare AMSN time-domain passive solver to the finest tested NEURON reference (2.5µm, dt0.0125ms) at identical nodes and protocol. Check timestep refinement in AMSN. Then add a second human morphology.
