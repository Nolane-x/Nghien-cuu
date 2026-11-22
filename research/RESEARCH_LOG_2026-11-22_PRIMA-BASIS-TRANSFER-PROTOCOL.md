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

## Evidence status

The earlier run (Actions 44922676384) validated its original 3-morphology × 9-parameter matrix and its Cholesky checks. It is historical evidence for the 3 kHz frozen/fresh comparison only. The present protocol is a new experiment; its result remains pending until its own GitHub Actions run and artifacts are fully inspected.

## Scientific limits

The fixtures do not represent a population distribution. NMO_290988_Mohan2015 is a partial dendritic reconstruction without an axon. The model is passive and linear; no sodium/potassium/calcium channels, active spike propagation, nonlinear synapses, plasticity, calcium signaling, gene regulation or cognitive behavior are represented. A passivity check is not an accuracy check.
