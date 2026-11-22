# Research log — PRIMA basis transfer under passive parameter and protocol variation

**Date:** 2026-11-22  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22

## Motivation

The 2026-11-21 passive parameter robustness result found that reprojecting a frozen order-56 basis preserves positive definiteness under ±20% Rm/Cm/Ra perturbations, but approximation accuracy can vary. Fresh basis construction was not uniformly superior. The former audit also used one basal-q75 10 ms pulse and did not preserve a separate extended 6/10 kHz result CSV.

A fair next test should distinguish three effects while holding requested order constant: reusing the nominal basis, rebuilding with the original 3 kHz shift band, and rebuilding with an extended 10 kHz shift band. It should also challenge source location and pulse duration.

## Protocol and expected data

Three human SWC fixtures × nine parameter cases × three model variants. Frequency errors against perturbed Hines at 0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz. Transient errors against perturbed Hines at soma, basal-q75 and apical-q75 source locations, with 2 ms and 10 ms square pulses. Seven unique output ports are recorded by SWC ID.

Expected records per morphology:
- 27 model summary rows;
- 243 frequency rows;
- 1,134 transient per-port rows.

All reduced conductance and capacitance matrices undergo Cholesky positive-definiteness checks. The full Hines tree is run once per source/pulse protocol and compared against all three reduced variants.

## Validated evidence — 2026-11-22

The present experiment completed in Actions run 44990898080, 3/3 jobs successful. Pinned NEURON 9.0.2 and the full AMSN test suite passed in each job. Three artifacts were downloaded and SHA-256 checked against GitHub metadata.

Validated totals: 81 model rows, 729 frequency rows and 3,402 transient-port rows. All 81 models achieved order 56 and passed Cholesky positive-definiteness checks. The analysis paired 1,134 transient output conditions by morphology, scenario, source, pulse width and exact SWC node.

The extended 10 kHz basis improved 6 kHz and 10 kHz frequency residuals in all 27 matched morphology/parameter cases for both Z and Y. Median extended/fresh-3k ratios:
- 6 kHz: Z 0.4678, Y 0.5059.
- 10 kHz: Z 0.2927, Y 0.3124.

But it worsened transient error in all 1,134 paired outputs, with median extended/fresh-3k ratio 4.052× and P90 6.519×. Fresh 3 kHz versus frozen 3 kHz was mixed: 488 improvements, 520 regressions and 126 ties.

The post-processing script, report, summary CSVs and artifact manifest are committed in this branch.

## Scientific limits

The fixtures do not represent a population distribution. NMO_290988_Mohan2015 is a partial dendritic reconstruction without an axon. The model is passive and linear; no sodium/potassium/calcium channels, active spike propagation, nonlinear synapses, plasticity, calcium signaling, gene regulation or cognitive behavior are represented. A passivity check is not an accuracy check.
