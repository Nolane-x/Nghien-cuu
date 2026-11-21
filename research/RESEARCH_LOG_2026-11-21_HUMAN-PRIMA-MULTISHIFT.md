# Research log — passive multi-shift PRIMA order sweep — 2026-11-21

## Question

Can a frequency-aware Krylov basis maintain passive RC stability while reducing the high-frequency error of DC-only PRIMA, and what reduced order is justified by measured frequency and transient accuracy?

## Implementation

Added amsn.prima_reduce_passive_cable_multishift in amsn-core/src/amsn/prima.py. Expansion points correspond to positive-real shifts 0, 100, 1,000 and 3,000 Hz (sigma=2*pi*f). Each shifted system is solved with a real Hines tree elimination. Shift blocks are seeded before round-robin expansion and globally reorthogonalized. The reduced C/G matrices are still formed by congruence and checked by Cholesky.

The human audit now builds multi-shift models of order 28, 56 and 84 while retaining the DC-only order-56 baseline. Every model is compared at seven ports, eight frequencies and a 20 ms basal-q75 pulse.

## Results

Six human morphology/reference-mesh jobs passed, and each ran 99 tests. Core CI passed 4/4 with 99 tests on Python 3.12 and 3.13 and both NEURON jobs.

- Order 28: worst port-admittance error 2.3475%; worst individual-port transient NRMSE 1.70973%.
- Order 56: worst port-admittance error 0.023604%; worst individual-port transient NRMSE 0.00031560%.
- Order 84: worst port-admittance error 0.00018225%; worst individual-port transient NRMSE 0.000000874%.

At equal order 56, multi-shift improves worst-case impedance 60.97–98.22× and admittance 83.44–112.07× relative to the DC-only basis across the three morphologies. All worst frequency residuals occur at 3 kHz.

## Recommendation

Order 56 is the balanced research preset, while order 84 is a high-accuracy choice. Order 28 should not be used for the full tested band without further port-specific constraints. The full Hines implementation remains canonical.

## Limits and next work

This is passive numerical validation, not biological validation. Active channel and synaptic dynamics are not included. NMO_290988 is a partial dendritic morphology with no axon and a mesiotemporal-sclerosis context. Next tests should vary pulse location and waveform, perturb passive parameters, extend frequency points above 3 kHz, then evaluate controlled coupling to active channels.
