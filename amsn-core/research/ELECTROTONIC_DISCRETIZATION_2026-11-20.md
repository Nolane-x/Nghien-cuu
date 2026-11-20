# AMSN — Electrotonic discretization for tapered SWC edges

**Date:** 2026-11-20 (UTC+7)  
**Status:** implementation added; standalone numerical tests run locally; full-repository CI pending at commit time.  
**Code:** `amsn-core/src/amsn/discretization.py`

## Research question

Can an SWC-to-cable converter constrain both physical compartment extent and electrotonic extent along a tapered dendritic segment, without changing the original reconstructed geometry or its branch topology?

## Why physical length alone is not enough

The same physical segment length can represent different fractions of a cable's AC length constant when its diameter, axial resistivity, membrane capacitance or reference frequency changes. NEURON's documented `d_lambda` example uses a 100 Hz reference frequency and `d_lambda = 0.1`, with segment lengths bounded relative to the AC length constant. Its implementation accounts for 3-D diameter samples along a section. This is a useful numerical discretization convention, not a universal biological constant or a guarantee of convergence.

Arbor separately documents physical-extent CV policies. Such policies show why physical-length constraints are useful, but they are not interchangeable with the electrotonic criterion.

## Model and units

For the passive high-frequency approximation used here,

`lambda_f = sqrt(d / (4*pi*f*Ri*Cm))`

where:
- `d` is diameter in metres;
- `f` is reference frequency in hertz;
- `Ri` is axial resistivity in ohm metres;
- `Cm` is specific membrane capacitance in farads per square metre.

For API inputs in micrometres, the local length constant is:

`lambda_f_um = 1000 * sqrt(diameter_um / (4*pi*f*Ri*Cm))`

For a straight SWC edge of length `L` whose diameter varies linearly from `d0` to `d1`, AMSN integrates the local dimensionless electrotonic distance exactly:

`E = integral_0^L dx/lambda_f(d(x))`

`E = (L/1000) * sqrt(4*pi*f*Ri*Cm) * 2/(sqrt(d0)+sqrt(d1))`

Here `L`, `d0` and `d1` are numerical values in micrometres. The taper integral is analytic; an independent midpoint quadrature test checks it.

## Algorithm

1. Compute the physical cut set so no edge portion exceeds `max_segment_length_um`.
2. Compute total integrated electrotonic distance for each tapered SWC edge.
3. Place additional cuts at equal fractions of the integrated `dx/lambda` coordinate. For a linear taper, the inverse coordinate has a closed form.
4. Union the physical and electrotonic cut sets.
5. Insert nodes by linear interpolation of 3-D coordinates and radius. Preserve every original node ID, neurite type on inserted points, and branch structure.
6. Pass the refined SWC into the existing vertex-centred cable converter, which retains the documented frustum-area and tapered-edge axial-resistance approximations.

The default `max_electrotonic_length=0.1` and `reference_frequency_hz=100` mirror the commonly used NEURON d_lambda example. Defaults for `Ri` and `Cm` match AMSN's generic passive cable defaults (0.7 ohm m and 0.01 F/m²). They are explicit numerical defaults, not measured human L2/3 values.

## Public API

```python
from amsn.discretization import (
    ac_length_constant_um,
    electrotonic_length_um,
    refine_swc_morphology,
    to_electrotonic_cable_tree,
)

refined = refine_swc_morphology(
    morphology,
    max_segment_length_um=20.0,
    max_electrotonic_length=0.1,
    reference_frequency_hz=100.0,
)
cable = refined.to_cable_tree()
```

Use `to_electrotonic_cable_tree(...)` to perform both operations in one call.

## Verification performed

Local environment: Python 3.13.5, NumPy 2.3.5, pytest 9.0.2, Linux x86_64.

Command:
```bash
PYTHONPATH=src python -m pytest -q
python -m compileall -q src tests
```

Result: **7 passed** for the newly added test file in a local isolated harness. That harness used a minimal morphology-compatible test double because this shell could not resolve `github.com` to clone the full repository. Therefore these seven tests verify the equations, cut-set bounds, topology/area-preservation algorithm and wrapper call shape, but they are not a full integration run against the existing `CableTree` implementation. The GitHub Actions workflow is configured to run the complete repository suite and the new example after this commit; its result must be checked separately before claiming full integration passed.

Tested properties:
- constant-diameter result equals `L/lambda_f`;
- tapered integral agrees with 100,000-step midpoint quadrature;
- every generated interval meets both physical and electrotonic bounds in the test case;
- refinement preserves original IDs, total length, approximate frustum surface area and branch-point count to the stated tolerances;
- input morphology is not mutated;
- invalid bounds are rejected;
- wrapper converts the refined morphology to a cable object.

## Limitations

- This is a passive, high-frequency AC-length approximation. It does not incorporate voltage-dependent active conductances, synaptic impedance, membrane leak in the high-frequency approximation, channel kinetics or local frequency spectra.
- A `d_lambda` target is a meshing heuristic. It does not establish accuracy for input resistance, transfer impedance, EPSPs, dendritic spikes, action potentials or calcium events.
- No human morphology was used in this checkpoint; the example uses the repository's synthetic branching SWC.
- The generic `Ri` and `Cm` defaults are not fitted to a human cortical subtype, cortical depth or temperature.
- No NEURON or Arbor cross-simulator comparison was executed.
- The converter remains a 1-D vertex-centred approximation with a spherical root-area fallback, not a 3-D soma, branch-junction or spine mesh.

## Next experiment

Take a morphology with explicit redistribution permission and recorded metadata. Compare meshes at `d_lambda = 0.2, 0.1, 0.05` and multiple physical extents. For each mesh, record compartment count, input resistance, membrane time constant, somatic-to-distal transfer ratio and runtime. Require numerical convergence on held-out stimulation locations before extending to active channels or human parameter fitting.

## Sources

- NEURON 9.0.1 documentation, “Using the d_lambda Rule”: https://www.neuronsimulator.org/en/9.0.1/guide/using_the_d_lambda_rule.html
- Hines, M.L. & Carnevale, N.T. (2001), “NEURON: a tool for neuroscientists,” *The Neuroscientist* 7, 123–135.
- Arbor documentation, “Discretization”: https://docs.arbor-sim.org/en/latest/concepts/discretization.html
- Arbor documentation, “Cable cell morphology”: https://docs.arbor-sim.org/en/latest/concepts/morphology.html
