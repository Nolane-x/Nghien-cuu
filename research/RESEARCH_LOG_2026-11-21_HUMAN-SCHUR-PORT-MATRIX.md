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


## Completed exact passive Schur port-matrix audit

The six-job human Schur audit [44916411567](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567) passed 6/6; Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed 4/4.

The Schur matrix agrees with an independent inversion of the full AMSN port impedance to at most 9.40e-11%. AMSN and NEURON reciprocity errors remain below 1.23e-12%. Seven-port matrix-level errors are below 0.0262% (admittance) and 0.0895% (impedance), with all maxima at 3 kHz. Off-diagonal transfer coupling errors are larger than diagonal self-admittance errors.

See [HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md](../amsn-core/research/HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md) and the two Schur port summary CSVs under ../amsn-core/results.
