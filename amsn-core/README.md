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

## Import3D-compatible electrical soma normalization

SWCMorphology.detect_neuromorpho_three_point_soma() recognizes the specific standardized three-point soma convention used by NEURON Import3D when its structural and geometric conditions pass. It maps the soma outline and long soma-attached zero-resistance wire roots to a single spherical soma electrical vertex. The raw SWC remains unchanged; electrical_node_mapping() retains the original-ID-to-electrical-vertex map. Both to_cable_tree() and to_sectioned_cable_tree() apply the rule by default; pass normalize_neuromorpho_soma=False to inspect the unnormalized morphology cable.

This rule is intentionally narrow. It must not be applied to arbitrary multi-point somata unless the exact conditions are satisfied.

## Real human morphology fixture

The package includes a standardized human temporal-cortex L2–3 pyramidal morphology under `data/human/1094_Mohan_etal_2015.CNG.swc`. It has 8,903 points (soma + basal/apical dendrites, no axon); dendritic integrity is moderate and metadata records mesiotemporal sclerosis. It is a real morphology fixture, not a complete neuron or healthy-control cell. See `data/human/README.md` for CC BY 4.0 attribution and `research/HUMAN_MORPHOLOGY_IMPORT_2026-11-20.md` for provenance and validation.

The electrical importer follows the verified NEURON Import3D three-point soma and wire-stem convention on this record without altering the source SWC.

## Passive transfer experiment on the human morphology

Run `python examples/human_passive_transfer.py` and `python examples/human_sectioned_mesh_sensitivity.py` to calculate DC transfer resistance between soma, basal and apical dendritic sites on the stored NeuroMorpho morphology. The example selects nodes deterministically by root-to-node path-distance quantiles and evaluates four electrotonic mesh levels. It uses the exact passive steady-state Hines solver; all membrane parameters remain generic and are not human-fitted. Results are numerical geometry sensitivity data, not biological electrophysiology.

## Transient pulse/step cross-validation

Run `python examples/human_transient_cross_validation.py` in the pinned NEURON 9.0.2 CI job. It compares the compact 690-compartment AMSN sectioned cable against Import3D on the same human SWC, with 10 pA 5 ms pulse and sustained step protocols, three source sites, five probes and nine time checkpoints.

The 270-row raw CSV and thresholded error report are in results/ and research/. This checks passive current-clamp transient response; it does not yet model AMPA/NMDA/GABA synaptic conductances or active channels.

## NEURON passive timestep and spatial convergence

Run examples/neuron_convergence.py in the pinned NEURON 9.0.2 CI job. It varies dt (0.025/0.0125ms) and maximum physical segment extent (5/2.5µm), keeps the same source/probe sites and records nine checkpoints from 1 to 250ms. The 540-row raw dataset and the separately calculated time/space convergence errors are stored in results/ and research/.

This convergence experiment characterizes NEURON's reference discretization. It is not the AMSN transient cross-comparison.

## NEURON passive cross-validation

examples/neuron_cross_validation.py is run in GitHub Actions with NEURON 9.0.2 on Python 3.12 and 3.13. It reads the same standardized SWC through Import3D, uses matched passive SI parameters, maps identical source/probe nodes, and compares NEURON with both the 8,893-compartment AMSN cable and the 690-compartment sectioned cable.

The verified passive DC run gives maximum relative errors below 0.69% for input resistance, transfer resistance and transfer ratio; normalized membrane area differs by about 0.000000843%. See research/NEURON_PASSIVE_CROSS_VALIDATION_2026-11-20.md and the raw CSV. This is one-cell passive numerical validation, not biological calibration or validation of active channels/synapses.

## Section-based electrical resampling

`amsn.sectioned.to_sectioned_cable_tree` aggregates unbranched piecewise-linear SWC chains into electrical control volumes. It keeps branch points, soma/type transitions and optional protected stimulation/recording nodes. Each new edge preserves original polyline arc length and integrates the tapered-frustum area and axial resistance along the original SWC edges. It never joins distant points with a straight chord. The result is still a 1-D cable approximation, and its voltage errors must be measured against a fine reference before use.

Run `python examples/human_sectioned_mesh_sensitivity.py` to compare four physical mesh limits with the full 8,903-node cable while protecting the exact same stimulation and probe sites.

## Critical biological scope

The HH test uses the canonical squid giant-axon parameterization at 6.3 C. **It is not a human cortical neuron model.** The passive cable defaults are explicit generic assumptions, not fitted human L2/3 parameters. This package does not yet reproduce Eyal et al. (2018), nor does it implement synapses, active dendritic conductances, calcium, gene expression, metabolism or astrocytes.

The SWC converter implements a vertex-centred 1-D cable approximation. It subdivides long edges, distributes frustum surface area to endpoint control volumes, and uses the exact axial-resistance integral for linear taper. The detected NeuroMorpho three-point soma pattern is normalized to a spherical electrical soma. Other soma/branch geometries remain 1-D approximations; true 3-D branch-junction and spine meshes are not modelled.

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
python examples/human_sectioned_mesh_sensitivity.py
python examples/neuron_cross_validation.py  # requires the optional pinned NEURON package
python examples/neuron_convergence.py  # NEURON timestep/segment sweep
python examples/human_transient_cross_validation.py  # requires pinned NEURON
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
