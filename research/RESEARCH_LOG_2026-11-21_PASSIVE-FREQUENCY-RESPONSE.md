# Research log — passive frequency-domain impedance — 2026-11-21

## Decision

Extend the passive cable validation from steady-state DC and time-domain traces to the frequency domain. Do not start active-channel fitting yet.

## Implementation

Added a complex-valued passive cable phasor solver to the AMSN core:

\`(G_leak + G_axial + j 2πf C) ΔV = I\`.

The solver uses complex Hines elimination and back-substitution and scales linearly with the number of compartments. The computed voltage is a perturbation around the leak reversal potential.

Tests independently assemble the dense complex matrix and compare the result at four frequencies. A separate 0-Hz invariant checks equivalence with the existing exact passive DC solution.

## Cross-simulator protocol

NEURON 9.0.2 Import3D on the same NMO_290988 SWC; fixed generic passive parameters; 0.5 µm segment cap; 3 current source sites × 5 recording sites × 8 frequency values. Compare both magnitude and phase for input and transfer impedance, retaining source/probe location offsets in raw output.

## Status

Implementation and workflow are committed. The first CI result is pending; no cross-simulator numerical result should be claimed until the workflow passes.

## Scientific guardrails

One partial morphology, passive membrane only, no fitting, no experimental validation. A successful result will validate only numerical equivalence for this specific model/configuration.
