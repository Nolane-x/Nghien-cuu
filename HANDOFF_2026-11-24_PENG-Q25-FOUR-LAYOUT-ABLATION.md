# Handoff — Peng four-layout q25 PRIMA ablation

**Date:** 24 November 2026  
**Branch:** research/prima-peng-q25-four-layout-ablation-2026-11-24  
**Parent:** research/prima-residual-localization-2026-11-24 / PR #18

## Research question

Does the q25 port-count trade-off on NMO_163775 arise from the basal-q25 probe, the apical-q25 probe, or their joint addition to the canonical seven ports?

## Four matched layouts

- seven: canonical seven ports.
- eight_basal_q25: canonical seven + basal-q25.
- eight_apical_q25: canonical seven + apical-q25.
- nine_both_q25: canonical seven + both q25 probes.

Every layout uses the same NMO_163775 SWC, 0.5 µm NEURON segment cap, six extended-10-kHz shifts, basis orders 112/168, nine passive parameter scenarios, nine AC frequencies, three source nodes, two pulse widths, 10 pA, 2 ms onset, 20 ms duration and dt 0.1 ms.

## Expected matrix

- 72 reduced models.
- 648 frequency matrices.
- 3,456 per-port transient rows.
- 2,268 paired shared-output comparisons versus seven ports.
- 432 q25-only output observations.
- 1,134 independent shared-Hines consistency checks.

Full Hines remains the reference. The exact seven shared SWC output IDs are matched by identity. Every Hines comparison is required to be finite and equal within the existing 1e-15 V tolerance.

## Scientific constraints

NMO_163775 is one mouse Control-condition morphology. NeuroMorpho marks the dendrites and axon complete but lists No Diameter; standardized SWC radii are not measured biological diameters. This is a passive linear-RC numerical experiment, not active-neuron or biological validation.

The workflow and result files are not considered successful until GitHub Actions completes and the archived report/CSV are read back. No production solver defaults change.

