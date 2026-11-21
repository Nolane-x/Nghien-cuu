# Research log — passive frequency-domain impedance — 2026-11-21

## Decision

Extend the passive cable validation from steady-state DC and time-domain traces to the frequency domain. Do not start active-channel fitting yet.

## Implementation

Added a complex-valued passive cable phasor solver to the AMSN core:

\`(G_leak + G_axial + j 2πf C) ΔV = I\`.

The solver uses complex Hines elimination and back-substitution and scales linearly with the number of compartments. The computed voltage is a perturbation around the leak reversal potential.

Tests independently assemble the dense complex matrix and compare the result at four frequencies. A separate 0-Hz invariant checks equivalence with the existing exact passive DC solution.

## Cross-simulator protocol

NEURON 9.0.2 Import3D on the same NMO_290988 SWC; fixed generic passive parameters; 0.5 µm segment cap; 3 current source sites × 5 recording sites × 8 frequency values. Compare both magnitude and phase for input and transfer impedance, retaining source/probe location offsets in raw output.

## Status

Implementation and workflow are committed. The first CI result is pending; no cross-simulator numerical result should be claimed until the workflow passes.

## Scientific guardrails

One partial morphology, passive membrane only, no fitting, no experimental validation. A successful result will validate only numerical equivalence for this specific model/configuration.

## Verified 0.5 µm baseline — workflow 44880205634

- NEURON 9.0.2, 125 sections, 25,233 segments; AMSN 8,893 compartments; 120 rows; 74 tests passed.
- Input complex error median/p95/max: 0.043795832/0.074104209/0.078027291%.
- Transfer complex error median/p95/max: 0.039582892/0.711515188/1.592748090%.
- Transfer magnitude error max: 1.094346040%; phase error max: 0.666723670°.
- High-frequency growth is visible: median transfer complex error rises from 0.013000318% at 0.1 Hz to 0.692482780% at 3,000 Hz.
- Worst case: apical q75 to basal q90 at 3,000 Hz; absolute transfer impedance is ~8.37e-9 MΩ in NEURON.

## Spatial convergence follow-up

The audit script and workflow were parameterized in commit 62a5d288f23084001c70e7580ac334140c09b967 to run mesh caps of 0.5, 0.25 and 0.125 µm. Workflow 44880470858 is the three-mesh run. Do not select a production reference mesh until its three per-mesh CSVs are inspected.
## Three-mesh AC convergence — workflow 44880470858

- All three matrix jobs passed; each ran the full 74-test AMSN suite and NEURON 9.0.2.
- 0.5 µm: 25,233 segments; input complex median/p95/max 0.043795832/0.073407268/0.078027291%; transfer complex 0.039582892/0.711515188/1.592748090%.
- 0.25 µm: 50,353 segments; input complex 0.025169814/0.064440836/0.068445691%; transfer complex 0.012377350/0.264955807/0.534124819%.
- 0.125 µm: 100,571 segments; input complex 0.009609508/0.036137713/0.060370374%; transfer complex 0.006549744/0.172349280/0.273631126%.
- From 0.5 to 0.125 µm, transfer complex median/p95/max decreases by ~6.04×/~4.13×/~5.82×. The 0.125 µm worst pair is basal q75 → apical q50 at 3 kHz (0.273631%).
- Median and p95 transfer errors decrease at every tested frequency across meshes; a few low-frequency per-frequency maxima are not monotone because the worst pair shifts.
- Raw artifacts: 0.5 µm 14697044290; 0.25 µm 14696684877; 0.125 µm 14697712070 (all within Actions run 44880470858).

Next: add a 0.0625 µm mesh to inspect diminishing returns and high-frequency residual floor.

## 0.0625 µm next refinement

A dedicated NEURON 9.0.2 workflow was added to test a 0.0625 µm maximum segment length. It reuses the same fixed-parameter AMSN/NEURON frequency-response audit, reruns the complete 74-test suite and uploads a separate raw CSV. The run is triggered by the workflow-file push. No claim is made about its result until Actions completes.

## Fourth mesh — 0.0625 µm (workflow 44880843864)

- Dedicated workflow succeeded; all 74 AMSN tests passed; NEURON 9.0.2; 125 sections; 201,021 segments; AMSN 8,893 compartments; 120 rows.
- Input complex error median/p95/max: 0.002441032/0.024339286/0.025800537%.
- Transfer complex error median/p95/max: 0.001938596/0.112636790/0.229691689%.
- Transfer magnitude error max: 0.178790008%; phase error max: 0.117113331°.
- Worst pair: apical q75 → apical q90 at 3 kHz; source and probe nearest-centre offsets 0.005167/0.002339 µm.
- Versus 0.5 µm the transfer complex median/p95/max improve by ~20.42×/~6.32×/~6.93×. Aggregate median and p95 decrease at every sampled frequency through all four meshes.
- Raw artifact 14698056883, workflow 44880843864.

## AC-to-transient phasor invariant and latest Core CI

Added `test_frequency_phasor_matches_time_domain_sinusoidal_steady_state`: 50 Hz cosine current on the branch compartment; fit the final five cycles from the time-domain solver; account for the left-edge input-sampling offset; compare fitted complex response with the continuous phasor solver within 0.2%. Core CI [44882886045](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44882886045) passed 4/4 jobs on commit d85f8d9; Python 3.12 and 3.13 each passed 75 tests; both NEURON cross-validation jobs passed.

## Eyal 2018 source retrieval

The official ModelDB 238347 archive URL is documented by the ModelDB-linked GitHub README as `http://senselab.med.yale.edu/modeldb/data/238347/EyalEtAl2018.zip` (stated 133 MB). The legacy Yale/SenseLab URL timed out in both page and archive attempts. The GitHub repository tree contains only `readme.html`; it is not the model code. No archive was received or integrated. See `amsn-core/research/EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md`.


## Segev morphology expansion

See the newer log research/RESEARCH_LOG_2026-11-21_FCI-EYAL-DERIVATIVE.md and handoff HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md. The original Eyal 2018 archive remains unavailable; FCI is read-only and is not the source of the committed SWCs.
