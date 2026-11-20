# SWC-to-cable discretization — implementation and numerical note

**Date:** 2026-11-20 (UTC+7)  
**Package:** AMSN Neuron Core v0.1.0  
**Status:** implemented and locally tested; not yet validated against a licensed biological reconstruction.

## 1. Purpose

Convert a reconstructed SWC point tree into an explicit one-dimensional, vertex-centred passive cable approximation without silently inventing taper, membrane-area or axial-resistance assumptions.

The conversion is intentionally narrow. It does not reconstruct a 3-D soma, dendritic spine, extracellular space or nanometre-scale branch junction.

## 2. Representation

Each original SWC point and each inserted subdivision point becomes a cable node/control volume. Each parent-child SWC edge becomes an axial connection. Long edges may be split using `max_segment_length_um`; inserted points lie on the straight SWC edge and their radii are linearly interpolated.

For each tapered edge with endpoint radii `r0`, `r1` and path length `L`:

- The lateral frustum area is `A = pi * (r0 + r1) * sqrt(L^2 + (r1 - r0)^2)`.
- The exact axial resistance for linearly varying circular radius is `R = rho_i * L / (pi * r0 * r1)`.
- The axial geometry factor stored by the converter is `L / (pi * r0 * r1)` in inverse metres; `CableTree` multiplies this by its selected axial resistivity.

The membrane surface area is partitioned at the edge midpoint. With `rm = (r0 + r1)/2`, each endpoint receives the surface area of its half-frustum. Summing the two halves reproduces the full frustum area. Thus a node's lumped membrane area is the sum of half-edge contributions from all incident edges.

The SWC root additionally receives a spherical soma-area approximation `4*pi*r_root^2`; callers may provide `root_soma_area_um2` to replace this estimate. This is an explicit fallback, not an assumption that every biological soma is spherical.

## 3. Numerical verification

The local test suite checks:

1. The Hines solution matches a dense direct matrix solve for a branched tree.
2. A one-compartment passive response matches the exact backward-Euler recurrence.
3. A tapered SWC edge uses `R = rho_i * L/(pi*r0*r1)`.
4. Sum of converter membrane areas equals the root-sphere-plus-frustum geometry summary to relative tolerance `1e-12`.
5. A 5,000-point linear SWC chain parses without recursive stack overflow.
6. A sealed uniform finite cable's input resistance agrees with the analytic result `Rin = R_inf * coth(L/lambda)`, with `lambda = sqrt(Rm*a/(2*Ri))` and `R_inf = sqrt(Rm*Ri/(2*pi^2*a^3))`.

For the analytic test (cable length 1 mm, radius 1 µm, `Rm=1 ohm*m^2`, `Ri=0.7 ohm*m`), relative input-resistance errors were approximately:

| Axial spacing | Nodes | Relative error |
|---:|---:|---:|
| 20 µm | 51 | 5.95e-5 |
| 10 µm | 101 | 1.49e-5 |

Halving the spatial spacing reduced this one test's error by about four times. This is an observed numerical result for this setup, not a universal convergence guarantee.

For the synthetic seven-point branching SWC bundled with the package, a 10 µm maximum segment length produced 12 cable nodes and 11 links. Total membrane area was 1,213.926 µm² both before and after conversion (within floating-point precision).

## 4. Assumptions and limitations

- Coordinates and radii are interpreted as micrometres, following SWC convention.
- Each SWC edge is a straight line; its radius varies linearly between the supplied endpoints.
- Each generated electrical node receives a lumped membrane area from adjacent half-frusta. The model is one-dimensional; it has no 3-D junction volume.
- The root uses an estimated spherical area unless the user supplies an explicit soma area. Multi-point soma reconstructions need a dedicated policy and tests before use.
- `max_segment_length_um` is a physical-length constraint, not an electrotonic-length or error-adaptive mesher.
- The default passive parameters are generic numerical defaults, not fitted human L2–3 data.
- No ion channels, synapses, dendritic spines, calcium signalling, metabolism or glia are inferred by this conversion.
- The bundled SWC is synthetic. A real reconstruction may only be added after its provenance and redistribution license are checked.

## 5. Next validation work

- Test the converter on more analytic cylinders and tapers, including asymmetric branching and nonuniform SWC sampling.
- Audit soma conventions in licensed human morphologies; avoid double-counting soma surface area where soma contours are represented by multiple SWC points.
- Add electrotonic-length refinement and branch-point convergence tests.
- Compare identical reconstructed morphology and protocols against a published NEURON implementation before claiming biological fidelity.
