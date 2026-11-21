# Human passive frequency-domain impedance audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Base code commit:** 8532c569d9539d3088e0b35958e3fdac252036c2  
**Status:** implementation committed; CI result pending at report creation  
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

Fixed parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV. NEURON mesh cap: 0.5 µm; NEURON version pinned to 9.0.2. No parameter fitting is performed.

## Numerical safeguards

- Unit tests compare complex Hines results with an independently assembled dense complex matrix at 0, 17.5, 100 and 1,000 Hz.
- A zero-frequency invariant compares the phasor solve with the existing passive DC solver after subtracting leak reversal potential.
- Input validation rejects negative/non-finite frequencies and malformed/non-finite current arrays.
- The NEURON workflow runs the full AMSN test suite before the morphology-level audit.
- The raw CSV is uploaded as a workflow artifact even if the audit step fails.

## Results

Pending the first GitHub Actions run. Do not treat this report as evidence of cross-simulator agreement until the workflow succeeds and its metrics are recorded below.

## Interpretation boundaries

This is a passive small-signal numerical audit on one partial morphology, not a fitted human neuron model, not a test of voltage-gated channels, and not experimental biological validation. NEURON's Impedance API returns impedance amplitude and phase; the comparison is restricted to its passive linear operating point. The exact SWC arc is used to select source/probe coordinates, but NEURON's cable discretization remains finite and is recorded separately.

## Next steps after a successful baseline

1. Inspect complex-error trends by frequency and by branch; do not report only one aggregate.
2. Repeat at 0.25 µm and 0.125 µm NEURON segment caps to estimate spatial convergence of the complex response.
3. Separate source-position and probe-position effects if any residual is frequency-localized.
4. Only after passive frequency response is stable, resume active-channel calibration against published human cortical recordings.
