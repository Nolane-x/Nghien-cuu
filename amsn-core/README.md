# AMSN Neuron Core v0.1.0

A first **runnable and tested** foundation for Adaptive Multi-Scale Neuron research. The package is intentionally much smaller than the long-term AMSN design.

## Included and tested

- Strict SWC point-tree parser with structural validation and stack-safe traversal for long reconstructions.
- Geometry summary using conical-frustum lateral area plus a spherical root estimate.
- SI-unit conversion helpers.
- Explicit SWC-to-cable discretization: optional maximum segment length, half-frustum membrane-area allocation, and exact tapered-frustum axial resistance integral.
- Passive branched cable tree with backward-Euler integration and an O(N) Hines elimination/back-substitution solver.
- Classic Hodgkin–Huxley 1952 kinetics as a numerical smoke test, with Rush–Larsen gate updates and implicit voltage updates.
- Tests comparing the Hines tree solve against a dense NumPy linear system, analytic backward-Euler passive decay, analytic sealed-cable input resistance and spatial refinement, morphology validation (including 5,000-node stack safety), a classic HH action-potential test and HH timestep refinement.

## Electrotonic refinement

The new `amsn.discretization` module refines SWC edges using both a maximum physical extent and a maximum integrated electrotonic distance. For linearly tapered edges, it integrates `dx/lambda_f` analytically and places cut points at equal electrotonic-distance intervals.

```python
from amsn.discretization import refine_swc_morphology
from amsn.morphology import SWCMorphology

morphology = SWCMorphology.from_file("cell.swc")
refined = refine_swc_morphology(
    morphology,
    max_segment_length_um=20.0,
    max_electrotonic_length=0.1,
    reference_frequency_hz=100.0,
)
cable = refined.to_cable_tree()
```

The defaults mirror the widely used NEURON d_lambda example (100 Hz, 0.1) and AMSN generic passive parameters. They are numerical defaults, not human L2/3 measurements. Read `research/ELECTROTONIC_DISCRETIZATION_2026-11-20.md` for equations and limits. A d_lambda-like mesh criterion does not replace convergence testing for the observables of interest.

## Real human morphology fixture

The package includes a standardized human temporal-cortex L2–3 pyramidal morphology under `data/human/1094_Mohan_etal_2015.CNG.swc`. It has 8,903 points (soma + basal/apical dendrites, no axon); dendritic integrity is moderate and metadata records mesiotemporal sclerosis. It is a real morphology fixture, not a complete neuron or healthy-control cell. See `data/human/README.md` for CC BY 4.0 attribution and `research/HUMAN_MORPHOLOGY_IMPORT_2026-11-20.md` for provenance and validation.

The importer handles CNG multi-point somata without adding a second spherical area at the root.

## Passive transfer experiment on the human morphology

Run `python examples/human_passive_transfer.py
python examples/human_sectioned_mesh_sensitivity.py` to calculate DC transfer resistance between soma, basal and apical dendritic sites on the stored NeuroMorpho morphology. The example selects nodes deterministically by root-to-node path-distance quantiles and evaluates four electrotonic mesh levels. It uses the exact passive steady-state Hines solver; all membrane parameters remain generic and are not human-fitted. Results are numerical geometry sensitivity data, not biological electrophysiology.

## Section-based electrical resampling

`amsn.sectioned.to_sectioned_cable_tree` aggregates unbranched piecewise-linear SWC chains into electrical control volumes. It keeps branch points, soma/type transitions and optional protected stimulation/recording nodes. Each new edge preserves original polyline arc length and integrates the tapered-frustum area and axial resistance along the original SWC edges. It never joins distant points with a straight chord. The result is still a 1-D cable approximation, and its voltage errors must be measured against a fine reference before use.

Run `python examples/human_sectioned_mesh_sensitivity.py` to compare four physical mesh limits with the full 8,903-node cable while protecting the exact same stimulation and probe sites.

## Critical biological scope

The HH test uses the canonical squid giant-axon parameterization at 6.3 C. **It is not a human cortical neuron model.** The passive cable defaults are explicit generic assumptions, not fitted human L2/3 parameters. This package does not yet reproduce Eyal et al. (2018), nor does it implement synapses, active dendritic conductances, calcium, gene expression, metabolism or astrocytes.

The SWC converter implements a vertex-centred 1-D cable approximation. It subdivides long edges, distributes frustum surface area to endpoint control volumes, and uses the exact axial-resistance integral for linear taper. The SWC root is still represented by a spherical-area estimate (or a caller-supplied soma area); true multi-point soma reconstruction, 3-D branch-junction geometry and spine geometry are not modelled.

## Install and test

```bash
python -m pip install -e '.[test]'
pytest -q
python examples/inspect_swc.py
python examples/passive_tree.py
python examples/electrotonic_refinement.py
python examples/passive_mesh_convergence.py
python examples/human_morphology_inspect.py
python examples/human_passive_transfer.py
```

Requires Python >=3.10 and NumPy >=1.24. Tests run without NEURON; external NEURON reproduction is a separate milestone.

## SI unit conventions

- length: m
- time: s
- voltage: V
- current: A
- conductance: S
- capacitance: F
- resistivity: ohm*m
- specific membrane resistance: ohm*m^2
- specific capacitance: F/m^2
- conductance density: S/m^2

Conversion helper checks prevent common factors-of-10/1000 errors. The cable solver assumes each compartment is a uniform cylinder and connects compartment centers using the sum of half-compartment axial resistances.

## Research context

The pilot biological target is a human temporal-cortex layer 2–3 pyramidal neuron, but a single parameter set is not representative of the population. Planert et al. (2026) report four electrophysiological subtypes in a large human L2/3 dataset. A human-specific parameterization must preserve subtype, cortical depth and experimental provenance.
