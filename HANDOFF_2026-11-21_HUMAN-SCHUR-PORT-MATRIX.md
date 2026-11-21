# Handoff — exact passive Schur port-matrix audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** exact frequency-dependent Schur reduction of AMSN cable trees onto the seven shared SWC source/probe ports, compared with the native NEURON port impedance matrix  
**Status:** implementation and workflow committed; six morphology/mesh jobs pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HUMAN_MORPHOLOGY_SOURCE_ALIGNMENT_REPLICATION_2026-11-21.md.
3. HUMAN_NMO_290988_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md.
4. HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md.

## New core API

amsn.reduction.schur_reduce_passive_admittance(tree, retained_indices, frequency_hz) constructs the full passive complex nodal admittance and eliminates every non-retained vertex by sparse symmetric Kron elimination. It retains the supplied port order and returns a dense complex port matrix.

The reduction is exact for the assembled AMSN passive cable at each frequency, up to floating-point roundoff. It is frequency-dependent because internal membrane capacitances are eliminated with the axial graph. Do not treat it as a frequency-independent static cable.

Unit tests compare the sparse reduction against a dense Schur complement and compare reduced port voltages against the full Hines solution at multiple frequencies.

## Human audit

New script: amsn-core/examples/human_schur_port_matrix_audit.py.  
New workflow: .github/workflows/amsn-human-schur-port-matrix.yml.

The seven retained ports are the unique set formed by three source locations (soma, basal q75, apical q75) and five probe locations (soma, basal q50/q90, apical q50/q90). Soma is shared, so there are seven unique ports.

At each of eight frequencies (0.1–3,000 Hz):
- AMSN produces its exact Schur-reduced port admittance.
- AMSN independently produces the full 7×7 port impedance by seven unit-current Hines solves and inverts it. This checks the Schur reduction independently.
- NEURON 9.0.2 produces the 7×7 complex port transfer-impedance matrix on the native Import3D fine tree using exact SWC section coordinates; its inverse is the effective port admittance.
- The workflow reports admittance and impedance Frobenius errors, diagonal/off-diagonal contributions, reciprocity error, conditioning and every complex matrix entry.

Matrix: three human morphologies × two NEURON mesh caps (0.125/0.0625 µm), six jobs. Each job runs the complete AMSN suite and uploads 8×7×7 = 392 raw matrix entries plus eight frequency summaries.

## Interpretation limits

The reduced operator is exact for the discretized AMSN tree. The NEURON port operator is inferred from its passive complex transfer matrix. Their difference includes morphology discretization, membrane support, Import3D location mapping and numerical conditioning. It is not biological validation.

Exact SWC ports are canonical. No weighted source mode is used in this audit, so source weighting cannot mask the port operator comparison.

## Next

Inspect the Schur identity error first; it must remain near numerical precision relative to the independent full-tree AMSN port inverse. Then examine AMSN–NEURON port admittance differences by frequency and diagonal/off-diagonal terms before any reduced operator is promoted into runtime use.


## Completed exact passive Schur port-matrix audit — 21/11/2026

Workflow [44916411567](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567) passed 6/6 jobs; Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed 4/4.

The new Schur API reproduces the independent AMSN full-tree port inverse to a maximum relative error of 9.40e-11%. Reciprocity errors remain below 1.23e-12%. Across the 3 morphologies × 2 mesh caps, all seven-port admittance matrix errors stay below 0.0262%; impedance errors stay below 0.0895%. Every worst case occurs at 3 kHz and off-diagonal coupling errors are larger than diagonal self-admittance errors.

Full report: [HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md); configuration summary [CSV](amsn-core/results/human_schur_port_matrix_summary_2026-11-21.csv); frequency detail [CSV](amsn-core/results/human_schur_port_matrix_frequency_summary_2026-11-21.csv).


## Core suite count correction — 21/11/2026

The six Schur matrix jobs each ran **90 passing tests** (not the earlier 81-test baseline). Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) also passed the 90-test suite on Python 3.12 and 3.13 and both NEURON validation jobs.
