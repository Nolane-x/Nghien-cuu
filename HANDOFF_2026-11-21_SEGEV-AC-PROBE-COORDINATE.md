# Handoff — Segev AC probe-coordinate sensitivity audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** exact SWC probe coordinate vs nearest segment-centre vs complex interpolation  
**Status:** implementation committed; CI result pending.

## Read first

1. AGENTS.md, HANDOFF.md and HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md.
2. HANDOFF_2026-11-21_SEGEV-AC-SOURCE-PLACEMENT.md and HANDOFF_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md.
3. This handoff and research/RESEARCH_LOG_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md.

## Why this experiment follows the source audit

The three-reference AC experiment showed that, for the tested source sites, exact SWC source coordinates and the refined segment centres returned indistinguishable NEURON impedances, while legacy base-mesh source centres could change transfer impedance by up to 0.228926%. It also showed the exact-SWC-to-refined-centre comparison was zero at exported precision.

The next independent location variable is the probe/readout. The existing passive frequency audit queries NEURON transfer impedance at the exact SWC-derived section coordinate and maps AMSN probes to SWC electrical nodes. The DC fine-mesh audit already records nearest-centre and linearly interpolated readouts. This AC audit tests the same issue in the frequency domain.

## Design

For each of three source locations (soma, basal q75, apical q75), five probes (soma, basal q50/q90, apical q50/q90) and eight frequencies (0.1–3,000 Hz), compare:

- exact_swc_arc: NEURON Impedance.transfer at the exact Import3D section arc coordinate;
- nearest_segment_center: NEURON Impedance.transfer at the nearest segment centre;
- complex_linear_interpolation: complex-linear interpolation of transfer impedance at the adjacent segment centres bracketing the exact SWC coordinate.

The interpolation is performed on real and imaginary parts through complex arithmetic, not by separately interpolating magnitude and phase. The source reference is fixed at the exact SWC arc coordinate used by the existing cross-simulator AC audit. Morphology, source, probe, membrane parameters and section mesh remain unchanged between readout modes.

Parameters remain Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV. NEURON is pinned to 9.0.2.

## Interpretation rules

- The exact-vs-nearest-centre comparison isolates whether the NEURON API readout changes when evaluated at a segment centre rather than the SWC coordinate.
- The exact-vs-complex-interpolated comparison tests whether adjacent-centre interpolation materially changes the complex readout.
- Complex interpolation is a diagnostic readout rule, not automatically the mathematically correct physical solution. Compare with the existing finite-volume/cable node interpretation before choosing a canonical mapping.
- Retain absolute transfer magnitudes because relative errors can overstate differences on very weak paths.
- Do not change Ri/Rm/Cm/Eleak to improve agreement.
- This is numerical validation only, not biological validation.

## Validation gate

Both cells must pass the full AMSN test suite with NEURON 9.0.2, produce exactly 120 rows per morphology (3 sources × 5 probes × 8 frequencies), and upload raw CSV plus job log. Check row counts and finite values before summarizing.

## Next step

Compare the exact-vs-interpolated change with the AMSN-vs-NEURON residuals at the same source/probe/frequency coordinates. If a readout effect is too small to explain the residual, proceed to matched-support probe geometry / branch-junction mapping and the full-tree passive voltage operator audit.
