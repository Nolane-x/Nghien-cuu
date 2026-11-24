# PRIMA matched 7-port / 9-port synthesis across four morphologies

**Date:** 24 November 2026  
**Status:** reproducible synthesis of archived, successful single-morphology workflows; no production solver defaults changed.  
**Scope:** passive linear-RC reduced models compared with full Hines references; not active-neuron or biological validation.

## Research question

Does adding basal-q25 and apical-q25 output ports impose a consistent accuracy cost on the seven shared outputs, or does that cost depend on morphology and basis order?

The analysis reads each morphology's report JSON, matched-summary CSV, q25-summary CSV and all 378 shared-Hines rows. It checks their agreement, complete coverage, common protocol and exact Hines trace equality before generating the summary. It does not rerun the underlying NEURON simulations.

## Holdout metadata and mesh strata

| Holdout | Experimental context | Axon metadata | Mesh cap (µm) | SWC records | Electrical compartments |
|---|---|---:|---:|---:|---:|
| NMO_162186 | epilepsy surgical specimen | incomplete / not marked complete | 0.125 | 7287 | 7278 |
| NMO_03524 | Control-condition human morphology; dendrites moderate and axon incomplete | incomplete / not marked complete | 0.125 | 869 | 862 |
| NMO_163775 | Control-condition mouse morphology; dendrites and axon complete; metadata says No Diameter | complete | 0.5 | 4209 | 4200 |
| NMO_107159 | Control-condition human pyramidal comparison morphology; dendrites and axon complete; Diameter, 3D, Angles | complete | 0.5 | 7228 | 7222 |

Two holdouts use a 0.125 µm NEURON segment cap (NMO_162186 and NMO_03524); two use 0.5 µm (NMO_163775 and NMO_107159). NMO_163775 is a mouse Control-condition reconstruction whose NeuroMorpho record says No Diameter; its standardized SWC radii are not measured biological diameters. NMO_107159 is a human pyramidal comparison cell with Diameter/3D/Angles metadata, not a rosehip interneuron. The cell-level contexts are not a matched biological population.

## Protocol and coverage checks

All four reports use the same orders (112, 168), six extended-10-kHz shifts (0, 100, 1,000, 3,000, 6,000, 10,000 Hz), nine passive parameter scenarios, nine AC frequencies (0.1 Hz–10 kHz), three current-source locations, two pulse widths (2/10 ms), 10 pA pulses, 2 ms onset, 20 ms duration and dt = 0.1 ms. The mesh cap is the documented protocol difference.

| Output across four holdouts | Verified rows |
|---|---:|
| Model configurations | 144 |
| AC frequency matrices | 1,296 |
| Per-port transient measurements | 6,912 |
| Paired shared-output comparisons | 3,024 |
| q25-only output observations | 864 |
| Shared full-Hines consistency checks | 1,512 |

The four archived Hines CSVs each contain 378 rows. Across all 1,512 checks, the maximum absolute trace difference is exactly 0 V and the maximum relative L2 difference is exactly 0%. This confirms that the two layouts use identical shared-node Hines reference traces within each matched experiment.

## Matched shared-output results

Each ratio is the median or maximum of the paired nine-port / seven-port transient NRMSE ratios over 378 matched shared-output pairs at that basis order. Ratios are dimensionless; NRMSE columns are percentages.

| Holdout | Mesh (µm) | Order | 9-port worse / better / tie | Median 9/7 ratio | Max 9/7 ratio | Max 7-port NRMSE (%) | Max 9-port NRMSE (%) | Max q25 NRMSE (%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NMO_162186 | 0.125 | 112 | 377 / 1 / 0 | 8.16203 | 395.261 | 1.45425e-07 | 1.06552e-05 | 3.67112e-06 |
| NMO_162186 | 0.125 | 168 | 187 / 190 / 1 | 1 | 1.00144 | 1.45424e-07 | 1.45425e-07 | 8.62264e-08 |
| NMO_03524 | 0.125 | 112 | 204 / 173 / 1 | 1 | 1.00614 | 3.1554e-08 | 3.15539e-08 | 3.0585e-08 |
| NMO_03524 | 0.125 | 168 | 189 / 189 / 0 | 1 | 1.00721 | 3.15544e-08 | 3.15545e-08 | 3.05856e-08 |
| NMO_163775 | 0.5 | 112 | 378 / 0 / 0 | 78.0511 | 6739.21 | 5.22142e-06 | 0.000193292 | 0.000215882 |
| NMO_163775 | 0.5 | 168 | 347 / 31 / 0 | 14.5014 | 300.218 | 1.28956e-08 | 6.06567e-07 | 4.28236e-07 |
| NMO_107159 | 0.5 | 112 | 378 / 0 / 0 | 42.7181 | 140.029 | 7.66713e-07 | 3.95066e-05 | 3.53235e-05 |
| NMO_107159 | 0.5 | 168 | 214 / 164 / 0 | 1.00102 | 4.37298 | 5.45115e-07 | 5.45589e-07 | 2.3679e-07 |

## Interpretation

- At order 112, 1/4 holdouts fall within a descriptive 0.99–1.01 median-ratio band. NMO_03524 is effectively at parity; NMO_162186, NMO_163775 and NMO_107159 show larger relative nine-port penalties.
- At order 168, 3/4 holdouts fall within that same descriptive band. NMO_162186, NMO_03524 and NMO_107159 are near parity; NMO_163775 remains the exception with a 14.501× median ratio.
- The large ratios must not be read without the absolute errors. For NMO_163775 at order 168, the maximum nine-port shared-output NRMSE is 6.0657e−7%, despite its 14.501× median ratio. This is a relative regression against an already very small seven-port baseline, not evidence of a large absolute voltage error.
- The q25-only outputs are represented at both orders in all four experiments. Order 168 reduces the maximum q25 NRMSE substantially on NMO_162186, NMO_163775 and NMO_107159; NMO_03524 is already at very small q25 error at order 112.
- The result rejects a universal rule that nine ports always require order 168, but it also rejects assuming order 112 is uniformly safe. Port-count cost depends on morphology under this passive protocol.

The 0.125 µm and 0.5 µm strata prevent a pooled interpretation of absolute error or runtime across all four morphologies. The paired ratio is valid within each morphology/order comparison because its seven- and nine-port candidates share that run's geometry, parameters, mesh, sources and exact output identities. It is not a substitute for a mesh-convergence study.

## Research decision

1. Keep full Hines as the canonical reference and do not change production defaults from these passive holdouts.
2. Treat order 168 as a strong candidate for q25-enriched output layouts, but retain NMO_163775 as an unresolved relative-error exception and compare its absolute error against an application-defined tolerance before any recommendation.
3. Do not pool absolute NRMSE, wall time or memory across different mesh caps, morphology classes or source conditions.

## Next experiments

1. **Mesh-harmonization factorial:** rerun at least one morphology from each existing mesh stratum at both 0.125 and 0.5 µm, with identical seven/nine ports, orders, shifts and parameter scenarios. Separate mesh sensitivity from morphology effects and preserve per-run resource measurements.
2. **Ablation/localization:** for the NMO_163775 order-168 residual, localize which shared ports, sources, pulse widths and passive-parameter scenarios dominate the 9/7 ratio; report absolute NRMSE and the seven-port denominator for every worst pair.
3. **Separate field-coupled solver track:** audit the 23 November 2026 bioRxiv preprint on hierarchical matrix compression for Cable-BEM (DOI 10.64898/2026.11.20.768225). It reports 2.7–6.1× memory reduction for one L2/3 bidomain case and markedly different errors for HSS/HODLR versus H/H2 formats at tolerance 10⁻³. This is a distinct bidomain / extracellular-field problem, not a directly comparable PRIMA result; benchmark it separately only if extracellular coupling or multicellular ephaptic effects become an AMSN requirement.

## Source reports and workflows

- **NMO_162186**: [report JSON](../results/NMO_162186_prima_7v9port_matched_order_2026-11-23_report.json), [matched summary](../results/NMO_162186_prima_7v9port_matched_order_2026-11-23_matched_summary.csv), [q25 summary](../results/NMO_162186_prima_7v9port_matched_order_2026-11-23_q25_summary.csv), [Hines checks](../results/NMO_162186_prima_7v9port_matched_order_2026-11-23_hines_shared.csv), [successful workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520).
- **NMO_03524**: [report JSON](../results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_report.json), [matched summary](../results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_matched_summary.csv), [q25 summary](../results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_q25_summary.csv), [Hines checks](../results/NMO_03524_JacobsControl_prima_7v9port_matched_order_2026-11-23_hines_shared.csv), [successful workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785).
- **NMO_163775**: [report JSON](../results/NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24_report.json), [matched summary](../results/NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24_matched_summary.csv), [q25 summary](../results/NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24_q25_summary.csv), [Hines checks](../results/NMO_163775_PengControl_prima_7v9port_matched_order_2026-11-24_hines_shared.csv), [successful workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600).
- **NMO_107159**: [report JSON](../results/NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24_report.json), [matched summary](../results/NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24_matched_summary.csv), [q25 summary](../results/NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24_q25_summary.csv), [Hines checks](../results/NMO_107159_TamasHumanPyramidalControl_prima_7v9port_matched_order_2026-11-24_hines_shared.csv), [successful workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588).

External lead: Esparza Rivera & Gomez, *Hierarchical Matrix Compression for Fast Bidomain Simulation of Multicellular Neuron Models*, bioRxiv v1 posted 23 November 2026, DOI [10.64898/2026.11.20.768225](https://doi.org/10.64898/2026.11.20.768225). It is a preprint and requires independent reproduction before adoption.

## Limitations

- Four single-cell morphology holdouts are not a representative human or mouse population.
- All comparisons are passive linear-RC numerical checks against full Hines; they do not validate active ion channels, nonlinear synapses, plasticity, calcium signaling or biological function.
- Relative ratios can be large when the seven-port denominator is very small; both relative and absolute errors must be reported.
- Two mesh caps are present, and the Peng record has no measured diameter metadata. Absolute cross-holdout errors are not pooled.
- The synthesis validates archived result consistency and coverage; it does not rerun the original simulations.

Full Hines remains canonical. No production order default, solver behavior or runtime path is changed.
