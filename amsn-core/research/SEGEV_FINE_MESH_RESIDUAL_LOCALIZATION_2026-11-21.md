# Segev fine-mesh pair-residual localization — 2026-11-21

## Data inspected

Raw CSVs were extracted from GitHub Actions artifacts for NMO_68174 and NMO_68175 at 0.125 and 0.0625 µm (120 rows per file; 3 current sources × 5 recording probes × 8 frequencies). The CSV columns include SWC IDs, frequency, NEURON/AMSN complex impedance, magnitude/phase residuals and nearest segment-centre offsets.

Artifacts:
- NMO_68174 0.125 µm: [14699989410](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14699989410)
- NMO_68175 0.125 µm: [14700104294](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14700104294)
- NMO_68174 0.0625 µm: [14700676187](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14700676187)
- NMO_68175 0.0625 µm: [14700169600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887397930/artifacts/14700169600)

## Worst source–probe pairs at 3,000 Hz

| Morphology | Mesh | Source (SWC) → probe (SWC) | Complex error | Magnitude error | Phase error | Source / probe centre offsets |
|---|---:|---|---:|---:|---:|---:|
| NMO_68175 | 0.125 µm | basal q75 (3253) → apical q50 (12177) | 0.169384% | 0.095953% | 0.079938° | 0.044099 / 0.043591 µm |
| NMO_68175 | 0.0625 µm | apical q75 (7640) → apical q50 (12177) | 0.099423% | 0.089533% | 0.024779° | 0.027810 / 0.002554 µm |
| NMO_68174 | 0.125 µm | basal q75 (1577) → apical q90 (10532) | 0.130503% | 0.073582% | 0.061777° | 0.001441 / 0.030656 µm |
| NMO_68174 | 0.0625 µm | basal q75 (1577) → apical q90 (10532) | 0.133856% | 0.073723% | 0.064037° | 0.009962 / 0.022117 µm |

The identity of the worst pair therefore changes with mesh for NMO_68175, but remains the same for NMO_68174. This is one reason aggregate maxima are not monotone across the matrix.

## Descriptive rank-correlation checks

Across all 120 rows within each cell/mesh, Spearman correlation between transfer-complex error and log10(frequency) was:

| Morphology | Mesh | Error vs log-frequency | Error vs source offset | Error vs probe offset |
|---|---:|---:|---:|---:|
| NMO_68175 | 0.125 µm | 0.783 | 0.297 | 0.126 |
| NMO_68175 | 0.0625 µm | 0.747 | 0.448 | 0.052 |
| NMO_68174 | 0.125 µm | 0.833 | 0.179 | −0.129 |
| NMO_68174 | 0.0625 µm | 0.807 | −0.096 | 0.354 |

These are descriptive statistics, not causal estimates: rows repeat the same 15 source–probe pairs at eight frequencies. The consistently high error–frequency rank association (0.747–0.833) indicates that the remaining relative discrepancy is concentrated toward the high-frequency end. Centre-offset associations vary by cell and whether the source or probe is involved; no universal offset-only explanation is supported.

## Absolute transfer impedance matters

For NMO_68174's maximum at 0.0625 µm, the NEURON transfer magnitude is only 2.4100585e−7 MΩ (0.241 Ω), versus 2.4082817e−7 MΩ in AMSN. The 0.133856% relative complex error therefore refers to a very weak cross-dendritic transfer path; it is not a 0.134% error on the cell's overall voltage response. The phase difference is 0.064°.

For NMO_68175's maximum at 0.0625 µm, NEURON transfer magnitude is 1.2357277e−4 MΩ and AMSN is 1.2346213e−4 MΩ; relative complex error 0.099423%, phase difference 0.024779°.

## Interpretation and next controlled experiment

1. Keep the passive constants frozen; the morphology conversion/area issue is already fixed.
2. Add a matched-support location experiment: for each source and probe, compare (a) exact SWC-arc interpolation, (b) NEURON nearest segment-centre locations, and (c) a consistently interpolated AMSN site. Keep morphology, conductances and mesh otherwise identical.
3. Report input and transfer impedance by source–probe pair and frequency, alongside absolute impedance and location offset.
4. Repeat at 0.125 and 0.0625 µm before adding finer meshes. Only add 0.03125 µm if matched-support residuals still decline and the extra segments are justified.

## Limits

One partial cortical region, two morphologies, passive linear membrane, incomplete axons, no fit to experimental recordings. The rank associations do not establish causality or biological validity.