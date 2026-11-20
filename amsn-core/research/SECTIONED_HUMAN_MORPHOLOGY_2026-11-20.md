# Section-based electrical resampling on a real human L2–3 morphology

**Date:** 2026-11-20 (UTC+7)  
**Implementation commit:** `2c41c821fbb9aa410fe0d5488d0365342989cdc7`  
**CI:** [run 44739746176 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44739746176)  
**Raw 60-row dataset:** `amsn-core/results/human_sectioned_mesh_sensitivity_2026-11-20.csv`

## Research question

Can AMSN reduce the electrical compartment count of a dense piecewise-linear SWC reconstruction without losing its anatomical path, total membrane surface, total axial resistance integral, or materially changing selected passive DC transfer observables?

## Morphology and reference

The source is NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015`:
- 8,903 standardized SWC points: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, no axon.
- Human temporal neocortex, middle temporal gyrus, BA21, layer 2–3, pyramidal/principal cell.
- Dendritic integrity is rated moderate; metadata records mesiotemporal sclerosis; shrinkage is not reported.
- This is a partial dendritic reconstruction, not a healthy-control cell or complete neuron.
- Preserve CC BY 4.0 attributions in `amsn-core/data/human/README.md`.

The reference cable tree uses one electrical control volume per SWC point (8,903 compartments). It is a fine discretization of this same geometry, not an experimental or independently validated biological reference.

## Method: preserve polylines, compress electrical degrees of freedom

The new module is `amsn-core/src/amsn/sectioned.py`.

### Section decomposition

The SWC tree is decomposed into 140 maximal unbranched paths. Section boundaries are retained at:
- the soma/root;
- anatomical branch points and terminals;
- neurite-type transitions (e.g. soma-to-dendrite);
- optional caller-protected stimulation and recording nodes.

The original 8,903 SWC samples remain in the morphology object and are all mapped to an electrical control point. User-selected stimulus/probe nodes are protected and remain exact control points.

### Geometry integrals

Each new electrical edge is integrated across the original piecewise-linear SWC polyline; the implementation does not replace a bent chain with a straight chord.

For each original frustum piece with arc length (L), endpoint radii (r_0,r_1):
- arc length is summed along original edge pieces;
- lateral area is (A=\pi(r_0+r_1)\sqrt{L^2+(r_1-r_0)^2});
- axial geometry is (\int ds/(\pi r(s)^2)=L/(\pi r_0r_1)) for a linear radius taper;
- electrotonic extent is integrated edge-by-edge using the passive high-frequency AC length-constant approximation.

For a coarsened electrical edge that covers multiple original SWC edges, these integrals are summed piecewise. Membrane area is divided between the proximal and distal control volumes at the arc midpoint; therefore the **total** membrane area is preserved, while its lumped distribution among control volumes is an approximation.

The result is still a 1-D passive cable. It is not a 3-D soma, spine, or branch-junction reconstruction.

### Site protection and measurement

The same seven SWC nodes were protected in every mesh:
- injection: soma 1, basal q75 node 3784, apical q75 node 5920;
- probes: soma 1, basal q50 node 3355, basal q90 node 3814, apical q50 node 6897, apical q90 node 5164.

This gives 3 × 5 = 15 source/probe pairs. Each source receives 10 pA; the passive steady-state Hines solver measures the exact linear DC solution. The same generic passive parameters are used throughout:
- (R_i=0.7\;\Omega\,m);
- (R_m=1.0\;\Omega\,m^2);
- (C_m=0.01\;F/m^2);
- (E_{leak}=-65\;mV);
- electrotonic reference frequency 100 Hz, maximum electrotonic extent 0.1.

These are generic software defaults, **not** fitted human L2–3 parameters.

## Results

### Electrical mesh size and geometry bounds

| Maximum physical extent | Compartments | Reduction vs 8,903 | Sections | Max original-node mapping error | Max actual electrical edge | Max electrotonic extent |
|---:|---:|---:|---:|---:|---:|---:|
| 100 µm | 700 | 92.14% | 140 | 17.881 µm | 37.251 µm | 0.099797 |
| 50 µm | 822 | 90.77% | 140 | 17.881 µm | 37.251 µm | 0.099797 |
| 25 µm | 1,062 | 88.07% | 140 | 12.247 µm | 24.985 µm | 0.099487 |
| 12.5 µm | 1,565 | 82.42% | 140 | 6.237 µm | 12.495 µm | 0.094335 |

The max mapping error is calculated across all 8,903 original SWC nodes. All seven protected input/output sites have zero mapping error by construction.

### Maximum relative error vs the 8,903-compartment reference

Errors are the maximum over all 15 source/probe pairs for each mesh.

| Maximum physical extent | Max input-resistance error | Max transfer-resistance error | Max transfer-ratio error |
|---:|---:|---:|---:|
| 100 µm | 0.041690% | 0.043481% | 0.049176% |
| 50 µm | 0.041749% | 0.043540% | 0.049016% |
| 25 µm | 0.041560% | 0.043448% | 0.044964% |
| 12.5 µm | 0.010265% | 0.011462% | 0.011149% |

The most compressed mesh (700 compartments) removes 92.14% of electrical control volumes while the largest observed relative error among these passive DC metrics remains below 0.05%. This is encouraging for this one geometry and stimulus protocol. Error does not decrease perfectly monotonically at each setting, and the max error is not a universal accuracy guarantee.

### Source input resistance

Reference values and sectioned estimates (MΩ):

| Injection site | Reference | 100 µm | 50 µm | 25 µm | 12.5 µm |
|---|---:|---:|---:|---:|---:|
| Soma (node 1) | 46.725504 | 46.727317 | 46.726965 | 46.727378 | 46.726027 |
| Basal q75 (node 3784) | 454.482950 | 454.293478 | 454.293210 | 454.294069 | 454.436297 |
| Apical q75 (node 5920) | 498.173230 | 498.065907 | 498.089316 | 498.099531 | 498.151210 |

These are model-derived values under generic passive assumptions, not measured human neuronal resistances.

### Runtime (single CI runner observations; not a benchmark)

| Maximum extent | Build seconds on Python 3.12 runner | Build seconds on Python 3.13 runner |
|---:|---:|---:|
| 100 µm | 0.135880 | 0.053029 |
| 50 µm | 0.153708 | 0.060002 |
| 25 µm | 0.188965 | 0.069066 |
| 12.5 µm | 0.262202 | 0.093702 |

Hosted runner timing varied between Python matrix jobs; use these only as rough observations. The number of compartments is the more reproducible complexity measure.

## Geometry-preservation tests

The new tests check:
- every original SWC edge is assigned to exactly one section;
- original branch points, terminals, type transitions and caller-protected nodes remain electrical control points;
- all original SWC nodes are represented in the mapping;
- total polyline arc length is preserved;
- total membrane surface area is preserved to numerical tolerance;
- the sum of axial geometry factors equals the sum over original frustum edges;
- every electrical edge respects the physical and electrotonic limits;
- the real human morphology is reduced below 2,000 compartments while preserving total geometry and the seven measurement locations.

The public API returns mapping error per original node, per-edge arc length, electrotonic length and axial geometry factor so later experiments can inspect each approximation.

## CI and reproducibility

GitHub Actions run [44739746176](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44739746176):
- Python 3.12.16: **43 passed in 1.49 s**;
- Python 3.13.18: **43 passed in 1.13 s**;
- package installation, pytest, compileall and all examples passed in both jobs;
- the 60 electrical measurement rows were identical between Python 3.12 and 3.13 at reported precision.

The complete CSV was captured from the Python 3.12 workflow log and committed at `amsn-core/results/human_sectioned_mesh_sensitivity_2026-11-20.csv`.

## Interpretation

This is a successful numerical-reduction result for one passive, linear DC use case. It shows that a very dense anatomical point tree can be represented by a substantially smaller electrical tree if section boundaries and the exact underlying geometry integrals are preserved.

It does **not** show:
- that the reduced model reproduces transient EPSPs, action potentials, dendritic spikes, calcium signals or plasticity;
- that the generic passive parameters represent the donor/cell;
- that the morphology is complete or healthy;
- that the result matches NEURON or Arbor;
- that the same compartment reduction is accurate on other cells, parameter sets or frequencies.

## Next experiments

1. Compare the fine and 700/822/1,062/1,565 compartment trees against a reference NEURON/Arbor cable built from the same morphology and same passive parameters.
2. Run transient step and synaptic-like current protocols; compare peak voltage, rise/decay time, transfer impedance and frequency dependence.
3. Use additional morphologies and donor metadata; keep disease/shrinkage/completeness caveats.
4. Only after passive cross-simulator agreement, add active dendritic channels and compare local spikes and calcium, then synaptic mechanisms.

Do not call the resampler biologically validated until cross-simulator and transient-activity validation are complete.
