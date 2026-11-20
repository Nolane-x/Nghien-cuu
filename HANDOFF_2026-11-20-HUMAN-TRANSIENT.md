# Handoff — AMSN passive transient cross-validation completed

**Date:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Final implementation/reporting commit:** d3099b6f4394052149b8121bfd3928a843d84cd3  
**CI:** [44747863750 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44747863750)

## Read first
1. AGENTS.md
2. HANDOFF_2026-11-20-NEURON-CONVERGENCE.md
3. HANDOFF_2026-11-20_NEURON-CROSS-VALIDATION.md
4. This handoff.
5. amsn-core/research/HUMAN_TRANSIENT_CROSS_VALIDATION_2026-11-20.md
6. amsn-core/results/human_transient_cross_validation_2026-11-20.csv
7. amsn-core/data/human/README.md

## Cell / model scope
NeuroMorpho NMO_290988 / 1094_Mohan_etal_2015.CNG.swc: human temporal-cortex BA21 layer 2–3 pyramidal/principal, 8,903 SWC nodes, no axon, dendritic completeness moderate, metadata records mesiotemporal sclerosis, shrinkage not reported. Not a complete or healthy-control cell. Keep CC BY 4.0 attribution.

The transient comparison uses Import3D-compatible soma and 8 wire-attachment normalization. NEURON: 125 sections / 2,637 segments; AMSN sectioned cable: 690 compartments / 130 sections. Generic passive params: Ri=.7Ω·m; Rm=1Ω·m²; Cm=.01F/m²; Eleak=-65mV. Same 10pA input at soma, basal q75 node3784 or apical q75 node5920; 5 probes (soma, basal q50/q90, apical q50/q90).

## Protocol
- Pulse: 10pA for 5ms then passive decay.
- Step: 10pA held through 250ms measurement window (NEURON clamp dur=300ms).
- Both engines dt=.025ms; NEURON secondorder=0; AMSN backward Euler.
- Nine sample times 1,2,5,10,20,50,100,200,250ms.
- Two protocols × 3 sources × 5 probes × 9 times = 270 data rows.
- All protected source/probe sites exact in AMSN; NEURON locations use Import3D point mapping to segment centres.

## Verified results
Run 44747863750:
- Python 3.12 and 3.13 each 46 tests passed.
- All 4 jobs passed: normal tests, NEURON DC and convergence, NEURON transient.
- 270 rows each; Python outputs identical at printed precision.

| Metric | Pulse 5ms | Step |
|---|---:|---:|
| Source max abs error | .021546895mV | .021546895mV |
| Source RMS error | .007805051mV | .016196218mV |
| Source max relative error | .666739% | .666739% |
| Probe max abs error | .035795496mV | .035795496mV |
| Probe RMS error | .004629863mV | .007084001mV |
| Probe max relative error | 1.478139% | 1.478139% |
| Transfer ratio max abs error | .007172235 | .007172235 |
| Transfer ratio RMS error | .001131877 | .000864943 |
| Transfer ratio max relative error | 2.696737% | 2.696737% |

Thresholds:
- Source/probe relative errors only when NEURON reference deflection >=0.02mV.
- Transfer-ratio absolute/RMS samples only when reference source deflection >=0.02mV.
- Transfer-ratio relative errors also require reference ratio magnitude >=0.05, avoiding near-zero denominator artifacts.

Worst probe: basal q75 source 3784 to basal q90 probe 3814 at 1ms (NEURON 2.421658962mV, AMSN 2.385863466mV). Worst ratio relative: soma source to apical q50 probe at 1ms (2.696737%).

## Important resource choice
The 8,893-compartment full AMSN cable was not run through the six 250ms transient simulations because its dense time-by-compartment trace would consume ~700MB per trace and much more Python runtime. Full AMSN was already DC cross-validated against NEURON. This transient experiment tests the compact 690-compartment sectioned model.

## Limits
One partial human cell, generic passive parameters, no synaptic conductance or active channels. Current-clamp transient validation only, not a biologically calibrated model.

## Next
1. Run AMSN timestep convergence on the sectioned tree (.025/.0125/.00625ms).
2. Compare an AMPA-like conductance waveform against NEURON, then NMDA/GABA kinetics.
3. Import a second human L2–3 morphology with clear CC BY-compatible terms and its own clinical/completeness metadata.
4. Only after passive/transient validations, add voltage-gated dendritic channels, calcium and plasticity.
