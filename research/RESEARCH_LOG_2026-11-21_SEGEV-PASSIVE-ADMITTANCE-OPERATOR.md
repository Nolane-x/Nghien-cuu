# Research log — Segev matched-support passive admittance operator — 2026-11-21

## Question

After independently validating axial conductance edges and membrane-area control volumes, how closely do AMSN and NEURON agree on the combined passive complex admittance operator when both are represented on the same electrical SWC nodes?

## Motivation

The Segev full-tree axial conductance matrix passed with sampled operator relative L2 maximum errors below 0.011%. The matched-support membrane area audit passed with total-area mismatch below 1.2e-6% and node-support maximum error below 0.026%. The next experiment combines these validated components.

## Method

New script: amsn-core/examples/human_segev_passive_admittance_operator_audit.py.
Workflow: .github/workflows/amsn-segev-passive-admittance-operator.yml.

The matched-support operator uses
Y(ω) = L_axial + diag(A/Rm + j·2πf·Cm·A),
with fixed Rm=1 Ω·m² and Cm=0.01 F/m². It compares axial, leak and capacitance components separately and samples 32 deterministic complex voltage vectors at 8 frequencies from DC to 3 kHz.

## Verification

Pending. The NEURON-side operator is a finite-volume projection onto the SWC node support, not an exact Schur complement of the original fine segment matrix. Preserve that distinction in any conclusion.

## Limits

This is still a passive linear model. No active channels, synapses, spines or biological parameter fitting. No biological accuracy claim.
