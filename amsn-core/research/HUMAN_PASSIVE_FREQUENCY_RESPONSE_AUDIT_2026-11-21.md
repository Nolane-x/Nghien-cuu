# Human passive frequency-domain impedance audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** 99daea4ea0cbaacc19b2e79f621e028fe5ccbf62  
**Three-mesh sweep commit:** 62a5d288f23084001c70e7580ac334140c09b967  
**Status:** three-mesh spatial convergence sweep verified; next refinement 0.0625 µm  
**Scope:** one partial human temporal-cortex L2–3 pyramidal SWC morphology; passive linear membrane only.

## Research question

Does the AMSN full-tree passive cable produce the same complex input and transfer impedance as NEURON when the morphology, passive parameters and stimulation/recording locations are matched? DC agreement alone cannot establish that the capacitance term or frequency-dependent phase response is correct.

## Method

AMSN solves the small-signal phasor system

\[
(G_{\mathrm{leak}} + G_{\mathrm{axial}} + j\,2\pi f C)\,\Delta V = I
\]

using a complex-valued Hines elimination/back-substitution on the rooted compartment tree. The result is a complex voltage perturbation around the leak reversal potential. At \(f=0\), the solution must reduce to the passive DC perturbation.

NEURON imports the same SWC with Import3D and runs its passive linear impedance calculation. A fixed set of 3 sources (soma, basal q75, apical q75) and 5 probes (soma, basal q50/q90, apical q50/q90) is used at 8 logarithmically-spaced frequencies: 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz. NEURON's reported impedance amplitude and phase are reconstructed into complex values for comparison.

Fixed parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV. NEURON version pinned to 9.0.2. No parameter fitting is performed. The audit is parameterized for mesh caps 0.5, 0.25 and 0.125 µm; each job writes a separate CSV.

## Numerical safeguards

- Unit tests compare complex Hines results with an independently assembled dense complex matrix at 0, 17.5, 100 and 1,000 Hz.
- A zero-frequency invariant compares the phasor solve with the existing passive DC solver after subtracting leak reversal potential.
- Input validation rejects negative/non-finite frequencies and malformed/non-finite current arrays.
- The NEURON workflow runs the full AMSN test suite before the morphology-level audit.
- The raw CSV is uploaded as a workflow artifact even if the audit step fails.

## Results — initial 0.5 µm baseline

Dedicated workflow [44880205634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880205634) succeeded on Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2. The full AMSN test suite passed 74/74. The morphology had 8,903 SWC records, 8,893 AMSN compartments, 125 NEURON sections and 25,233 NEURON segments. The experiment generated 120 raw rows; artifact [14697319208](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880205634/artifacts/14697319208).

| Metric | Median | p95 | Maximum |
|---|---:|---:|---:|
| Input complex impedance error | 0.043796% | 0.074104% | 0.078027% |
| Input magnitude error | 0.041556% | 0.069450% | 0.073563% |
| Input phase error | 0.000474° | 0.026935° | 0.035298° |
| Transfer complex impedance error | 0.039583% | 0.711515% | 1.592748% |
| Transfer magnitude error | 0.024972% | 0.528179% | 1.094346% |
| Transfer phase error | 0.010726° | 0.301248° | 0.666724° |

Transfer complex error by frequency (15 source-probe pairs per frequency):

| Hz | Median % | p95 % | Maximum % | Max magnitude error % | Max phase error |
|---:|---:|---:|---:|---:|---:|
| 0.1 | 0.013000 | 0.039573 | 0.039608 | 0.039608 | 0.000132° |
| 1 | 0.013026 | 0.039625 | 0.039634 | 0.039621 | 0.001316° |
| 10 | 0.015353 | 0.042452 | 0.046624 | 0.040654 | 0.013117° |
| 30 | 0.027740 | 0.071074 | 0.083009 | 0.048775 | 0.038494° |
| 100 | 0.064226 | 0.186968 | 0.219066 | 0.117201 | 0.106104° |
| 300 | 0.171799 | 0.368519 | 0.417319 | 0.298873 | 0.167128° |
| 1,000 | 0.387919 | 0.705906 | 0.751436 | 0.527942 | 0.361085° |
| 3,000 | 0.692483 | 1.321337 | 1.592748 | 1.094346 | 0.666724° |

The largest relative transfer discrepancy is apical q75 → basal q90 at 3,000 Hz: complex error 1.592748%, magnitude error 1.094346%, phase error 0.666724°. Its absolute transfer impedance is very small (approximately 8.37e-9 MΩ in NEURON), so the relative percentage must be interpreted with the absolute value. By source, maximum complex transfer errors were 0.925997% for soma, 0.717327% for basal q75 and 1.592748% for apical q75.

Input impedance remains closely aligned: global maximum complex error 0.078027%. Transfer mismatch increases with frequency; this justifies a spatial convergence sweep but does not prove the remaining error is caused only by mesh spacing.

## Three-mesh spatial convergence — verified

Workflow [44880470858](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858) succeeded in all 3 jobs. Each job installed NEURON 9.0.2 and passed the complete 74-test AMSN suite. All three use the same 8,893-compartment AMSN reference, fixed passive parameters, 3 source sites, 5 probe sites and 8 frequencies (120 rows per mesh).

| NEURON maximum segment length | NEURON segments | Input complex error median / p95 / max | Transfer complex error median / p95 / max | Transfer magnitude max | Transfer phase max |
|---:|---:|---:|---:|---:|---:|
| 0.5 µm | 25,233 | 0.043796 / 0.073407 / 0.078027% | 0.039583 / 0.711515 / 1.592748% | 1.094346% | 0.666724° |
| 0.25 µm | 50,353 | 0.025170 / 0.064441 / 0.068446% | 0.012377 / 0.264956 / 0.534125% | 0.436561% | 0.176708° |
| 0.125 µm | 100,571 | 0.009610 / 0.036138 / 0.060370% | 0.006550 / 0.172349 / 0.273631% | 0.199264% | 0.152002° |

From 0.5 to 0.125 µm, aggregate transfer-complex median error decreases about 6.04×, p95 about 4.13× and maximum about 5.82×. Input-complex maximum error decreases from 0.07803% to 0.06037%. The transfer-complex median and p95 also decrease at every tested frequency across the three meshes.

Do not claim every individual pair or per-frequency maximum decreases monotonically. At low frequencies, a few maximum-error pairs are slightly larger at 0.25 µm than at 0.5 µm because the worst pair shifts with segment-centre placement; those maxima fall again at 0.125 µm. Aggregate median/p95 and the overall maximum improve consistently.

At 0.125 µm the overall worst pair changes to basal q75 → apical q50 at 3,000 Hz: complex error 0.273631%, magnitude error 0.087343%, phase error 0.148513°. This is materially smaller than the 0.5 µm worst case; the earlier 1.592748% error occurred on a very weak apical q75 → basal q90 transfer.

Raw data artifacts:
- [0.5 µm CSV artifact 14697044290](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697044290)
- [0.25 µm CSV artifact 14696684877](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14696684877)
- [0.125 µm CSV artifact 14697712070](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697712070)

The summary tables are committed in `amsn-core/results/`. A dedicated 0.0625 µm refinement workflow has been added to test whether high-frequency transfer error continues to decline; no production mesh is declared yet.

## Interpretation boundaries

This is a passive small-signal numerical audit on one partial morphology, not a fitted human neuron model, not a test of voltage-gated channels, and not experimental biological validation. NEURON's Impedance API returns impedance amplitude and phase; the comparison is restricted to its passive linear operating point. The exact SWC arc is used to select source/probe coordinates, but NEURON's cable discretization remains finite and is recorded separately.

## Next steps after a successful baseline

1. Run and inspect the 0.0625 µm mesh; compare high-frequency error and computational cost against 0.125 µm.
2. Decompose remaining residuals by source, probe, frequency and absolute transfer impedance; avoid percentage-only claims for near-zero transfer.
3. Separate source-position and probe-position effects if any residual remains frequency-localized.
4. Only after passive frequency response is stable, resume active-channel calibration against published human cortical recordings.
