# Handoff — Segev matched-support passive admittance operator

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** combine the verified axial graph and per-node membrane-area support into a complex passive admittance operator  
**Status:** implementation committed; workflow pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md.
3. HANDOFF_2026-11-21_SEGEV-MEMBRANE-AREA-SUPPORT.md.
4. Reports: HUMAN_SEGEV_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md and HUMAN_SEGEV_MEMBRANE_AREA_SUPPORT_AUDIT_2026-11-21.md.

## Research question

On one shared electrical SWC node set, how closely do the full passive admittance operators agree after combining:
- the validated AMSN and NEURON reduced axial edge conductances; and
- the independently measured membrane-area support assigned to every electrical node?

The matched-support phasor operator is
Y(ω) = L_axial + diag(A/Rm + j·2πf·Cm·A).
The same passive constants are used for both models: Rm=1 Ω·m², Cm=0.01 F/m², Eleak=−65 mV. Eleak is a source/reversal term and does not enter the small-signal admittance matrix itself.

## Important scope

The NEURON side is the matched-support finite-volume operator built from:
- actual segment ri()-based reduced edge conductances;
- actual segment.area() values distributed over the pt3d overlap with each SWC edge half-control-volume.

This is **not** an exact Schur complement of the original fine NEURON segment-level admittance matrix. It is a controlled comparison on the same SWC electrical support, suitable for testing whether geometry/area mapping can support the passive operator. Do not describe it as an exact reproduction of native NEURON's full segment matrix.

## Method

For each morphology, at 0.125 µm NEURON mesh:
1. Run the area-support audit to build per-node AMSN and NEURON area arrays.
2. Run the whole-tree axial matrix audit to build AMSN and NEURON edge conductance arrays.
3. Verify node/edge counts and tree connectivity.
4. Build Y(ω) for 0, 0.1, 1, 10, 100, 300, 1,000 and 3,000 Hz.
5. Apply both complex operators to 32 deterministic complex voltage vectors with seed 20261121 and 10 mV standard deviation.
6. Report axial, leak, capacitance and combined operator differences independently.
7. Verify axial current conservation and the constant-voltage axial nullspace.

## Validation gate

- Exactly identical electrical node IDs and axial edge topology.
- No duplicate, missing or disconnected axial edges.
- Finite positive edge conductances and positive membrane areas.
- Separate statistics for axial conductance, leak diagonal and capacitance diagonal.
- Per-frequency complex operator relative L2 statistics and raw CSV.
- No retuning Ri/Rm/Cm/Eleak to absorb residuals.

## Interpretation limits

This is matched-support passive numerical validation, not a native NEURON Schur complement and not biological validation. It excludes active channels, synapses, nonlinear conductances, calcium, and dendritic spines. A small sampled-vector error is not a formal induced operator norm.

## Next step

If the matched-support operator passes, compare it with direct NEURON impedance at selected exact SWC source/probe sites and verify the area-support mapping at finer meshes. If there is a residual, inspect per-node area and edge conductance contributors before considering a full Schur-complement reduction of the fine NEURON tree.


## Verified results — matched-support passive admittance operator (21/11/2026)

The passive operator workflow [44904475571](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571) passed 2/2 Segev jobs; Core CI [44904475559](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475559) passed 4/4 jobs.

With Rm=1.0 Ω·m², Cm=0.01 F/m², NEURON 9.0.2 at 0.125 µm and 32 deterministic complex voltage probes:
- NMO_68174 maximum sampled passive-operator relative L2 error was 0.0078381% over DC–3 kHz.
- NMO_68175 maximum was 0.0025449%.
- Leak and capacitance diagonal sampled errors were each below 0.00025%; axial current conservation residuals were below 6.1e-21 A; constant-voltage axial nullspace residual was zero.

The NEURON side is a matched-support finite-volume projection, not an exact Schur complement of the original fine segment-level matrix. This is numerical passive consistency, not biological validation.

Full report: [HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md); summary [CSV](amsn-core/results/human_segev_passive_admittance_operator_summary_2026-11-21.csv). Next: compare the matched-support operator to selected direct NEURON impedance and transient outputs before adding active mechanisms.
