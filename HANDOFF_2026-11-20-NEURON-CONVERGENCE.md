# Handoff — NEURON passive numerical convergence completed

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Code commit:** d6c67083c727e862356a7268671d2fa79bf01a3b  
**CI:** [44746105586 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44746105586)

## Read first
1. AGENTS.md
2. HANDOFF_2026-11-20_NEURON-CROSS-VALIDATION.md
3. This handoff.
4. amsn-core/research/NEURON_TEMPORAL_SPATIAL_CONVERGENCE_2026-11-20.md
5. amsn-core/results/neuron_passive_convergence_2026-11-20.csv
6. amsn-core/data/human/README.md

## New workflow/script
examples/neuron_convergence.py runs in the pinned NEURON 9.0.2 job. It keeps the same NMO_290988 SWC and the same three injection / five probe sites, but varies:
- physical segment cap: 5.0 and 2.5 µm;
- fixed timestep: 0.025 and 0.0125 ms;
- observation times: 1,2,5,10,20,50,100,200,250 ms.

540 rows per runner (4 configurations × 3 sources × 5 probes × 9 times). Python 3.12 and 3.13 outputs match exactly.

## Results
| Change | Max abs error | RMS error | Max relative error for ref deflection ≥0.05 mV |
|---|---:|---:|---:|
| dt .025→.0125 at cap5 | .008936221 mV | .000982751 mV | .367656% |
| dt .025→.0125 at cap2.5 | .009017677 mV | .000991579 mV | .372450% |
| cap5→2.5 at dt .025 | .009498791 mV | .001421479 mV | .738397% |
| cap5→2.5 at dt .0125 | .009417335 mV | .001417490 mV | .740058% |

NEURON segment counts: 2,637 at cap5, 5,149 at cap2.5. Total segment area remains 23,338.438806144 µm².

Combined coarse/fine comparison gives .006348748 mV max absolute and .734900% max relative, but temporal/spatial errors can partially cancel; use separate factor comparisons.

## Verified CI
Run 44746105586:
- Python 3.12: 46 passed.
- Python 3.13: 46 passed.
- NEURON 9.0.2 convergence script passed on both.
- 540 rows on both runners, identical at printed precision.

## Scope
This is NEURON's own passive solver convergence, not yet a transient AMSN vs NEURON comparison. Same partial cell limitations apply (no axon, moderate dendritic integrity, mesiotemporal sclerosis metadata, shrinkage not reported). Parameters are generic.

## Next concrete experiment
Compare AMSN backward-Euler passive time-domain solver with NEURON at the finest tested reference (2.5 µm, 0.0125 ms):
1. exact same seven source/probe SWC nodes;
2. same 10 pA step current;
3. trace values at 1,2,5,10,20,50,100,200 ms;
4. source and probe time courses, rise/decay and transfer ratios;
5. refine AMSN timestep separately.
Do this before any active channels or synapse dynamics.
