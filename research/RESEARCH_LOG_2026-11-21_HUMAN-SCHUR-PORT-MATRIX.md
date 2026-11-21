# Research log — exact passive Schur port-matrix audit — 2026-11-21

## Question

Can AMSN eliminate all non-source/probe cable vertices exactly and expose a compact frequency-dependent port admittance matrix, and how does that seven-port operator compare with native NEURON Import3D?

## Implementation

New core module: amsn-core/src/amsn/reduction.py.  
Public API: amsn.schur_reduce_passive_admittance.  
Tests added to amsn-core/tests/test_cable.py.

The algorithm builds the full passive nodal admittance (axial Laplacian plus membrane leak and jωC shunts), then eliminates all non-retained vertices in reverse topological order. The original graph is a tree, so fill-in is limited by the retained boundary ports. This produces the exact Schur complement on those ports.

## Human audit

New script: amsn-core/examples/human_schur_port_matrix_audit.py.  
New workflow: .github/workflows/amsn-human-schur-port-matrix.yml.

The six jobs cover three morphologies × two NEURON mesh caps. Each job uses seven unique SWC ports and eight frequencies. It compares:
1. explicit AMSN sparse Schur matrix;
2. inverse of the AMSN full-tree port impedance from seven Hines solves;
3. inverse of the native NEURON seven-port complex transfer matrix.

## Verification

Pending. The Schur identity must pass near numerical precision before cross-simulator residuals are interpreted.

## Limits

This is passive frequency-domain numerical model reduction only. The reduced operator is frequency-dependent and does not imply a frequency-independent resistor network or biological validation.
