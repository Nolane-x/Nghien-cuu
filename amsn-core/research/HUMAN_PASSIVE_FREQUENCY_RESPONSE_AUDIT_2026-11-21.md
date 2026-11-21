# Human passive frequency-domain impedance audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** 99daea4ea0cbaacc19b2e79f621e028fe5ccbf62  
**Three-mesh sweep commit:** 62a5d288f23084001c70e7580ac334140c09b967  
**Status:** 0.5 µm baseline verified; three-mesh sweep (0.5/0.25/0.125 µm) queued  
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

The parameterized 3-mesh workflow was added in commit `62a5d288f23084001c70e7580ac334140c09b967`; run [44880470858](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858) evaluates 0.5, 0.25 and 0.125 µm. Its results are pending and must be added before selecting a reference mesh.

## Interpretation boundaries

This is a passive small-signal numerical audit on one partial morphology, not a fitted human neuron model, not a test of voltage-gated channels, and not experimental biological validation. NEURON's Impedance API returns impedance amplitude and phase; the comparison is restricted to its passive linear operating point. The exact SWC arc is used to select source/probe coordinates, but NEURON's cable discretization remains finite and is recorded separately.

## Next steps after a successful baseline

1. Inspect the 0.5/0.25/0.125 µm matrix results and decide whether the high-frequency discrepancy converges monotonically.
2. Decompose residuals by source, probe, frequency and absolute transfer impedance; avoid percentage-only claims for near-zero transfer.
3. Separate source-position and probe-position effects if any residual remains frequency-localized.
4. Only after passive frequency response is stable, resume active-channel calibration against published human cortical recordings.
