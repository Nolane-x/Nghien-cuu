# AMSN implementation checkpoint — 2026-11-20

## Scope
This is the first new executable code checkpoint after the previous Alpha source directories were found empty. It is a clean v0.1 foundation, not an attempt to claim recovery of the prior Alpha implementation.

## What is implemented
- SWC parser with one-root, connected-tree, unique-ID, positive-radius and parent-integrity checks; connectivity validation uses an iterative stack so long real reconstructions do not hit Python recursion limits.
- Explicit vertex-centred SWC-to-cable conversion with optional maximum segment length, membrane-area partitioning across tapered frusta, and exact linearly tapered axial-resistance integration. The root soma uses an explicitly documented spherical-area approximation unless the caller supplies a soma area.
- Morphology summaries: node/edge counts, branch points, total path length, per-neurite-type length and approximate membrane area.
- SI-unit conversion helpers for common electrophysiology units.
- Passive branched cable solver using backward Euler and tree-structured Hines elimination.
- Canonical HH 1952 channel gates as a numerical smoke test; the voltage update is implicit with conductances frozen after a Rush–Larsen gate update.

## What is intentionally not implemented
- The converter is a 1-D lumped approximation, not a 3-D mesh. Multi-point soma shape, branch-junction nanogeometry and dendritic spines remain outside scope.
- No Eyal 2018 model reproduction in this checkpoint.
- No human cortical ion-channel distributions, synapses, calcium biochemistry, plasticity, gene expression, metabolism or glial coupling.
- No fit to human patch-clamp traces.

## Numerical formulation
For passive or frozen-conductance membrane updates:

`C_i dV_i/dt = -g_m,i V_i + b_i + I_i + sum_j g_ij (V_j - V_i)`

Backward Euler yields a symmetric tree-structured linear system. The Hines solve eliminates leaves toward the root and back-substitutes from root to leaves. Tests compare this result against a dense direct solve for a branched tree and against the analytic steady input resistance of a sealed finite cylinder. The 20 µm and 10 µm axial discretizations showed relative analytic errors of about 5.95e-5 and 1.49e-5, respectively, for the documented test geometry.

The axial conductance between two compartment centers is computed from the two half-compartment resistances using each cylinder's cross-sectional area. The membrane area approximation is lateral cylindrical area. Taper within a compartment is not represented.

## Local test results
Python 3.13.5, NumPy 2.3.5, pytest 9.0.2: 21 tests passed in the latest local run. See `TEST_REPORT_2026-11-20.md` for exact commands and result details. This does not mean that the human Eyal model was reproduced.

## Next scientific step
Reproduce the original published human L2/3 Eyal et al. (2018) implementation. The ModelDB landing page states that the downloadable model archive is approximately 133 MB and identifies NEURON and Python as simulation environments. This environment currently has no NEURON installation, and package installation was attempted but network DNS was unavailable. Therefore the published-model reproduction remains blocked in this runtime and must not be marked passed.
