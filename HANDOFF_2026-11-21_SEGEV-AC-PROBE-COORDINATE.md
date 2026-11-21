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

## Verified results — workflow 44901688035

**Status:** both NEURON 9.0.2 morphology jobs passed; each produced 120 rows and a raw CSV/log artifact. Core CI [44901673896](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901673896) also passed, including Python 3.12/3.13 tests/examples and both NEURON cross-validation jobs.

### Exact versus nearest-centre probe readout

For all 120 rows in each morphology, exact-SWC Impedance.transfer(x) and nearest-segment-centre readout were identical at exported precision. This is consistent with both coordinates resolving to the same NEURON segment for these probe sites; it does not establish that segment-centre readout is a continuum-exact value.

### Complex-linear interpolation versus exact-SWC readout

Maximum transfer-complex change by probe across the tested sources and frequencies:

| Probe | NMO_68174 / cell1125 | NMO_68175 / cell1204 |
|---|---:|---:|
| Basal q50 | 0.001654% | 0.011556% |
| Basal q90 | 0.018746% | 0.001704% |
| Apical q50 | 0.024816% | 0.095872% |
| Apical q90 | 0.057785% | 0.040445% |
| Soma | 0% | 0% |

The strongest effects occur at 3 kHz. Linear interpolation is a diagnostic alternative, not a declared ground truth.

### Matched cross-simulator re-evaluation at 0.125 µm

The two probe-audit CSVs were joined one-to-one to the original 120-row AMSN/NEURON frequency audits using source, source SWC ID, probe, probe SWC ID and frequency. This directly tests whether replacing NEURON's exact-SWC readout with the complex-interpolated readout changes the residual against the same AMSN output.

| Metric | Cell1125 exact-SWC | Cell1125 interpolated | Cell1204 exact-SWC | Cell1204 interpolated |
|---|---:|---:|---:|---:|
| Median transfer-complex error | 0.001555% | 0.000670% | 0.002297% | 0.001105% |
| P95 | 0.049634% | 0.046984% | 0.073495% | 0.059094% |
| Maximum | 0.130599% | 0.132786% | 0.169222% | 0.125637% |

- Cell1125: 26 rows improve, 70 worsen, 24 are unchanged. The median and p95 improve slightly, but the worst case increases slightly.
- Cell1204: 64 rows improve, 32 worsen, 24 are unchanged. Median, p95 and maximum all improve; the worst matched pair (basal q75 source → apical q50 probe at 3 kHz) falls from 0.169222% to 0.077077%.
- The largest cell1204 change is not universal: some basal-probe pairs worsen under interpolation.

**Interpretation:** probe interpolation is a material, site-dependent numerical choice and can account for a substantial share of the residual in selected cell1204 apical paths. It does not consistently improve both morphologies or all pairs. Do not replace exact-SWC readout by complex interpolation as the default without mesh-convergence and matched-support validation.

### Raw artifacts

- [NMO_68174 CSV + log, artifact 14706460979](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901688035/artifacts/14706460979)
- [NMO_68175 CSV + log, artifact 14706590616](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901688035/artifacts/14706590616)
- [Probe audit workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901688035)
- [Core CI](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901673896)

### Next experiment

Run the same probe audit at 0.25, 0.125 and 0.0625 µm mesh caps for both cells. Assess whether the exact-vs-interpolated effect and its cross-simulator benefit converge with refinement. Continue from [HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md](HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md).
