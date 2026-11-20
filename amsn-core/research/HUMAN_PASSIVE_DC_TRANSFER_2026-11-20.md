# Human morphology passive DC transfer and mesh-sensitivity experiment

**Date:** 2026-11-20 (UTC+7)  
**Code commit:** `136b524ef073b3d53771ebf6515a6bbcd19cdc17`  
**CI:** [run 44737999994 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737999994)  
**Raw measurements:** `amsn-core/results/human_passive_transfer_2026-11-20.csv`

## Question

What steady-state voltage transfer does the passive AMSN cable built from the real human temporal L2–3 morphology predict between soma, basal dendrite and apical dendrite sites, and how sensitive are those values to the current electrotonic refinement rule?

## Data and biological scope

The morphology is NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015`, with 8,903 standardized SWC points (3 soma, 4,051 basal dendrite, 4,849 apical dendrite, no axon). Metadata marks dendritic physical integrity as moderate and records mesiotemporal sclerosis; shrinkage is not reported. This is a partial dendritic reconstruction, not a complete or healthy-control neuron. The data attribution/license requirements are recorded in `amsn-core/data/human/README.md`.

## Method

### Node selection

Root-to-node path distance is computed over the SWC tree. Candidate sites are sorted by (path distance, SWC node ID); quantiles are calculated separately within SWC type 3 (basal) and type 4 (apical).

| Site | Selection | SWC ID | Path distance from root |
|---|---|---:|---:|
| Soma injection / probe | Root | 1 | 0.000000 µm |
| Basal injection | Type 3, 75th percentile | 3784 | 211.065895 µm |
| Basal probe | Type 3, 50th percentile | 3355 | 140.136824 µm |
| Basal probe | Type 3, 90th percentile | 3814 | 258.183183 µm |
| Apical injection | Type 4, 75th percentile | 5920 | 802.205567 µm |
| Apical probe | Type 4, 50th percentile | 6897 | 346.492715 µm |
| Apical probe | Type 4, 90th percentile | 5164 | 930.122423 µm |

Three injection sites were paired with five probes, producing 15 source/probe pairs per mesh and 60 result rows over four meshes.

### Passive parameters

These are generic AMSN defaults, not values fitted to this cell:
- axial resistivity (R_i=0.7\;\Omega\,m);
- specific membrane resistance (R_m=1.0\;\Omega\,m^2);
- specific membrane capacitance (C_m=0.01\;F/m^2);
- leak reversal (-65\;mV);
- injected current (+10\;pA) at the source node;
- discretization reference frequency 100 Hz and (d_\lambda=0.2,0.1,0.05,0.025).

### Exact DC Hines solve

Added `CableTree.solve_passive_steady_state()`, which solves the passive linear DC system directly:

[
(G_{leak}+G_{axial})V=G_{leak}E_{leak}+I.
]

This removes the capacitive term exactly; it does not approximate steady state by integrating for a very long time. The solver uses Hines elimination/back-substitution on the rooted tree. This method applies only to the passive linear membrane; it does not solve active-channel or synaptic steady states.

For each source, input resistance is ((V_{source}-E_{leak})/I). Transfer resistance is ((V_{probe}-E_{leak})/I). Transfer ratio is the probe voltage deflection divided by the source voltage deflection.

## Results

### Mesh sizes

| (d_\lambda) | Compartments | Build time on Python 3.12 CI |
|---:|---:|---:|
| 0.2 | 8,903 | 0.122815 s |
| 0.1 | 8,903 | 0.130722 s |
| 0.05 | 8,903 | 0.118877 s |
| 0.025 | 8,905 | 0.122892 s |

The source morphology is already sampled densely relative to this passive 100 Hz electrotonic criterion: the first three limits create no new compartments, and the finest creates only two additional compartments.

### Representative transfer ratios

Values below are from the (d_\lambda=0.2) mesh. The other first three meshes return the same values at the printed precision; the 0.025 mesh differs only in the last few decimal places.

| Injection site | Soma probe | Basal 50% | Basal 90% | Apical 50% | Apical 90% |
|---|---:|---:|---:|---:|---:|
| Soma (SWC 1) | 1.000000 | 0.935702 | 0.848943 | 0.688801 | 0.288992 |
| Basal q75 (SWC 3784) | 0.088945 | 0.083226 | 0.981280 | 0.061266 | 0.025704 |
| Apical q75 (SWC 5920) | 0.029564 | 0.027663 | 0.025098 | 0.041512 | 0.073152 |

Input resistance at the three source sites:
- soma: 46.725504 MΩ;
- basal q75: 454.482950 MΩ;
- apical q75: 498.173230 MΩ.

These values describe the chosen passive tree and generic parameters. They are **not** experimentally measured human neuronal properties.

### Change between coarsest and finest tested criteria

Across the 15 source/probe pairs:
- maximum relative input-resistance change: **0.00000161%**;
- maximum relative transfer-resistance change: **0.00000161%**;
- maximum relative transfer-ratio change: **0.00000399%** (maximum absolute ratio change (2.0\times10^{-9})).

This very small difference is unsurprising because the mesher produced identical 8,903-compartment trees at (d_\lambda=0.2,0.1,0.05) and only 8,905 compartments at 0.025. It demonstrates weak sensitivity across these particular settings, **not general mesh convergence**.

### Reproducibility and CI

GitHub Actions run [44737999994](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737999994):
- Python 3.12.16: **38 passed in 1.12 s**;
- Python 3.13.18: **38 passed in 1.55 s**;
- install, pytest, compileall and every example completed successfully;
- the experiment printed 60 measurement rows on both Python versions with matching electrical values to the reported precision.

The CSV contains the full 60 rows parsed from the Python 3.12 CI log. Runtime measurements are single hosted-runner observations and are not a performance benchmark.

## Interpretation

The real SWC contains many short reconstruction edges. The current converter uses one passive compartment per SWC point, so the input morphology itself imposes a much denser electrical mesh than the 100 Hz (d_\lambda) rule requires for most edges. This design is safe against large geometric under-sampling but wastes electrical degrees of freedom and makes a simple refinement sweep uninformative.

A better next architecture separates:
1. the detailed piecewise-linear anatomical reconstruction;
2. the electrical compartment mesh along cable sections;
3. exact integration of path length, frustum surface area and tapered axial resistance between electrical control points.

The next resampler must preserve original branch points, soma points, neurite type transitions, path arc length and geometry integrals. It should not simply connect distant SWC nodes with straight chords, because that would erase bends and shorten the path.

## Limitations

- One partial human morphology, with no axon and moderate dendritic completeness.
- Metadata records mesiotemporal sclerosis; shrinkage correction not reported.
- Generic passive parameters; no cell-specific fit.
- No active channels, synapses, voltage-gated spikes, calcium dynamics or glia.
- One current amplitude and one static DC protocol.
- No comparison to a reference simulator yet.
- Mesh-level similarity is weak evidence because most tested levels generated exactly the same compartment graph.
- The 1-D cable soma/branch junction geometry remains an approximation.

## Next experiment

Implement section-based electrical resampling over the original piecewise-linear SWC:
- preserve every branch point and type transition;
- coalesce unbranched chains into sections;
- integrate exact arc length, tapered lateral area and axial resistance along each original edge;
- place control points by physical length and electrotonic distance along section arc length;
- compare 8,903-point reference mesh against 200/500/1,000/2,000-compartment reductions;
- measure input resistance and all 15 transfers;
- compare fine vs resampled trees and validate against NEURON or Arbor on exactly the same morphology and passive parameters.

Do not call the reduced mesh accurate until the selected observables meet explicit error tolerances.
