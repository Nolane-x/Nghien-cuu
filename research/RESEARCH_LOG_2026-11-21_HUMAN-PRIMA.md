# Research log — human passive PRIMA reduction — 2026-11-21

## Question

Can a passive cable tree with thousands of compartments be compressed into a low-order dynamic realization while preserving the selected soma/dendrite port responses and the passive stability structure?

## Method

Implemented a PRIMA-style block Krylov projection in amsn-core/src/amsn/prima.py. The full system has the passive RC form C dv/dt + Gv = Bi. The basis starts from G inverse times the port selector and expands by the action of negative G inverse C. Inverse actions use the existing O(N) Hines solver. Projection is congruent, producing reduced G_r=V.T G V and C_r=V.T C V. Cholesky checks verify positive definiteness.

The reduced model exposes port impedance/admittance and a backward-Euler state step. It has no SciPy dependency and does not materialize a dense full-neuron matrix.

## Verification

Core CI run 44918897010 passed 4/4. Python 3.12 and 3.13 each passed 95 tests; the NEURON reference jobs also passed. The human PRIMA audit run 44918896972 passed 6/6, with each configuration running the same 95-test suite.

The six configurations are three human morphologies times two NEURON reference mesh caps. A 56-state PRIMA model was compared with the exact full AMSN Hines port response at 0.1–3,000 Hz and against a 20 ms pulse from basal q75.

## Results

- Full model sizes: 8,893, 12,399 and 13,747 compartments.
- Reduced order: 56 for each model; reduction 99.3703–99.5926%.
- Maximum port impedance Frobenius error: 1.9661%, at 3 kHz.
- Maximum port admittance Frobenius error: 2.3601%, at 3 kHz.
- Maximum individual-port transient NRMSE: 0.00015662%.
- Maximum all-port transient NRMSE: 0.00003031%.
- The 3 kHz error is notably higher than low-frequency error, consistent with a basis expanded from DC.

See the human report and aggregate results CSV in amsn-core/research and amsn-core/results. The six raw artifact archives are attached to workflow 44918896972.

## Interpretation limits

These results validate a passive numerical reduction for the tested parameters and retained ports. They do not validate active channels, synapses, physiology or population-level generalization. The reduced coordinates are global voltage modes rather than anatomical compartments. NMO_290988 is a partial dendritic reconstruction with no axon and a mesiotemporal-sclerosis context. The full Hines solver remains the reference implementation.

## Next experiment

Introduce positive-real shifted/multi-shift Krylov expansion and sweep reduced order. Track the full frequency-dependent port matrix error and transient pulse error simultaneously, and verify that Cholesky/passivity checks continue to hold.
