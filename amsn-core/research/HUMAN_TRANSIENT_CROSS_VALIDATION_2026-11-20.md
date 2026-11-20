# AMSN transient passive cross-validation against NEURON 9.0.2

**Date:** 2026-11-20 (UTC+7)  
**Code commit:** `d3099b6f4394052149b8121bfd3928a843d84cd3`  
**GitHub Actions:** [run 44747863750 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44747863750)  
**Raw data:** `amsn-core/results/human_transient_cross_validation_2026-11-20.csv`

## Research question

Does the section-reduced AMSN passive cable reproduce NEURON's transient voltage response after current injection, not only the steady-state DC input and transfer resistances?

Two current-clamp protocols were compared:
- a 10 pA pulse lasting 5 ms, followed by passive relaxation;
- a 10 pA step held throughout the 250 ms observation window.

The same human SWC morphology, passive parameters, anatomical source/probe IDs, fixed timestep and measurement times were used in both engines.

This is transient cross-simulator numerical validation of a passive 1-D cable. It is not an experimental human-neuron fit.

## Morphology and model

Source: NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`.
- Human temporal neocortex, middle temporal gyrus, BA21, layer 2–3 pyramidal/principal cell.
- 8,903 standardized SWC points: soma, basal and apical dendrites; no axon.
- Dendritic completeness is rated moderate.
- Metadata records mesiotemporal sclerosis; shrinkage is not reported.
- It is a partial dendritic reconstruction, not a complete or healthy-control neuron.

The original SWC is unchanged. CC BY 4.0 attribution is retained in `amsn-core/data/human/README.md`.

The electrical soma normalization follows the verified NEURON Import3D convention for this standardized three-point soma, including its eight zero-resistance wire attachments. It uses a spherical electrical soma and preserves all selected anatomical source/probe IDs.

### Electrical configurations

| Parameter | Value |
|---|---:|
| NEURON | 9.0.2, Import3D SWC |
| NEURON sections / segments | 125 / 2,637 |
| AMSN model | section-reduced cable |
| AMSN electrical compartments | 690 |
| AMSN unbranched sections | 130 |
| Axial resistivity | 0.7 Ω·m |
| Specific membrane resistance | 1.0 Ω·m² |
| Specific membrane conductance | 1.0 S/m² |
| Specific membrane capacitance | 0.01 F/m² |
| Leak reversal | −65 mV |
| Current injection | 10 pA |
| Fixed timestep | 0.025 ms |
| NEURON integration | fixed-step, secondorder=0 |
| AMSN integration | backward Euler |
| Pulse duration | 5 ms |
| Step current duration | 300 ms clamp, 250 ms simulated |
| Observation times | 1, 2, 5, 10, 20, 50, 100, 200, 250 ms |

All passive parameters are generic software defaults, not fitted to this cell or donor.

### Source and probe sites

Three current-injection sites and five voltage probes were reused:
- Sources: soma SWC 1; basal q75 SWC 3784; apical q75 SWC 5920.
- Probes: soma SWC 1; basal q50 SWC 3355; basal q90 SWC 3814; apical q50 SWC 6897; apical q90 SWC 5164.

All seven SWC sites were protected as exact control points in AMSN's sectioned cable. NEURON locations were mapped through Import3D's own SWC point-to-section index and then to the nearest segment centre.

## Measurement volume and reproducibility

For each protocol there are 3 sources × 5 probes × 9 times = 135 samples. For both protocols, the complete output contains **270 measurement rows**.

GitHub Actions run [44747863750](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44747863750):
- Python 3.12.16 package tests: **46 passed**.
- Python 3.13.18 package tests: **46 passed**.
- NEURON 9.0.2 cross-validation, spatial/temporal convergence and transient pulse/step experiment: all successful on both Python versions.
- Both Python runners generated 270 transient rows; all rows were identical at reported precision.

The exact raw rows from Python 3.12 are stored in the accompanying CSV.

## Results

Relative voltage errors are reported only when the corresponding NEURON reference deflection is at least 0.02 mV. Transfer-ratio errors need an additional safeguard because the ratio divides by source voltage:
- ratio absolute/RMS statistics use samples where the NEURON source deflection is at least 0.02 mV;
- ratio relative statistics additionally require the NEURON reference ratio to be at least 0.05 in magnitude.

This avoids reporting large meaningless relative errors when the source or reference ratio is close to zero.

### Source deflection

| Protocol | Samples | Max absolute error | RMS error | Max relative error |
|---|---:|---:|---:|---:|
| 5 ms pulse | 135 | 0.021546895 mV | 0.007805051 mV | 0.666739% |
| 250 ms step observation | 135 | 0.021546895 mV | 0.016196218 mV | 0.666739% |

### Probe deflection

| Protocol | Samples | Max absolute error | RMS error | Max relative error |
|---|---:|---:|---:|---:|
| 5 ms pulse | 135 | 0.035795496 mV | 0.004629863 mV | 1.478139% |
| 250 ms step observation | 135 | 0.035795496 mV | 0.007084001 mV | 1.478139% |

The maximum probe voltage error occurs for current injection at basal q75 SWC node 3784, recording at basal q90 SWC node 3814, at 1 ms:
- NEURON: 2.421658962 mV;
- AMSN sectioned: 2.385863466 mV;
- absolute difference: 0.035795496 mV.

### Probe/source transfer ratio

| Protocol | Samples used for absolute/RMS | Max absolute ratio error | RMS ratio error | Samples used for relative error | Max relative ratio error |
|---|---:|---:|---:|---:|---:|
| 5 ms pulse | 75 | 0.007172235 | 0.001131877 | 42 | 2.696737% |
| 250 ms step observation | 135 | 0.007172235 | 0.000864943 | 73 | 2.696737% |

The maximum absolute ratio difference occurs for basal q75 injection (SWC 3784) and basal q90 probe (SWC 3814), at 1 ms:
- NEURON ratio: 0.878039466;
- AMSN ratio: 0.870867231;
- absolute difference: 0.007172235.

The maximum relative ratio difference occurs for soma injection and apical q50 probe at 1 ms:
- NEURON ratio: 0.058971315;
- AMSN ratio: 0.060561616;
- relative difference: 2.696737%.

## Interpretation

The 690-compartment AMSN sectioned cable tracks NEURON's passive transient response closely for the two current-clamp protocols tested:
- source deflection error is below 0.67% relative at the defined threshold;
- probe deflection error is below 1.48%;
- transfer-ratio error is below 0.00718 absolute, or below 2.70% relative when the reference ratio magnitude is at least 0.05.

The pulse experiment also checks passive relaxation after the current is switched off. The step experiment checks the approach toward steady state over the same observation window.

These results extend the earlier DC comparison into the time domain. They do not yet test synaptic conductances, AMPA/NMDA/GABA receptor kinetics, voltage-gated channels, dendritic spikes or calcium signals.

## Corrected reporting note

An earlier transient-summary draft used the probe deflection threshold for transfer-ratio relative errors. This was incorrect because a transfer ratio is divided by the source deflection; a small source can make the ratio unstable even when the probe is not negligible.

The script now applies:
- source threshold 0.02 mV for absolute/RMS transfer-ratio samples;
- additional reference-ratio threshold 0.05 for relative transfer-ratio error.

The raw 270 measurement rows were not changed by this reporting correction.

## Limitations

- One partial human morphology; no axon, moderate dendritic completeness, mesiotemporal-sclerosis context and no shrinkage correction report.
- Generic passive parameters, not donor/cell fitted.
- One current amplitude; no experimental voltage trace was used as a biological target.
- Transient AMSN comparison uses the 690-compartment sectioned cable; the full 8,893-compartment AMSN tree was validated against NEURON for passive DC in the separate cross-validation report, not run through all six transient simulations due to memory/runtime cost.
- NEURON and AMSN both represent a passive 1-D cable; there is no 3-D soma, spine, extracellular space or glial environment.
- No synaptic conductance waveform or active channel was used.
- Timestep convergence was characterized separately for NEURON; AMSN transient timestep refinement remains to be done.

## Next experiment

1. Run AMSN transient timestep refinement at 0.025, 0.0125 and 0.00625 ms for the same 690-compartment tree.
2. Compare an AMPA-like conductance input (g(t)(V-E_{rev})) against NEURON, rather than relying only on current-clamp steps.
3. Validate a second license-cleared human L2–3 morphology with its own completeness/clinical metadata.
4. Only after passive/transient validation, begin active dendritic channel and synaptic kinetics work.

Do not call the model a complete or biologically calibrated human neuron from these results alone.

## Sources

- NEURON Import3D SWC reader and section creation: https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/read_swc.hoc and https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/import3d_gui.hoc
- NeuroMorpho.Org NMO_290988, license and required attribution: see `amsn-core/data/human/README.md`.
- SWC format specification: https://github.com/INCF/swc-specification
