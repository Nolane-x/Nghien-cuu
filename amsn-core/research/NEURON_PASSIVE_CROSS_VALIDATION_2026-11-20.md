# NEURON cross-validation of AMSN passive human L2–3 cable

**Date:** 2026-11-20 (UTC+7)  
**Code commit:** 56eaf350334a3f1795f4070edc5b96a1748fcc89  
**GitHub Actions:** [run 44745099560 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44745099560)  
**Reference simulator:** NEURON 9.0.2, Import3D SWC  
**Raw data:** amsn-core/results/neuron_passive_cross_validation_2026-11-20.csv

## Question

After matching NEURON Import3D's special soma and wire-attachment conventions, how closely does AMSN reproduce passive steady-state input and transfer resistance on the same standardized human L2–3 SWC? Does the section-reduced AMSN cable remain close to both the fine AMSN tree and NEURON?

This is a numerical cross-simulator validation of a passive cable implementation. It is not a fit to experimental human electrophysiology.

## Source morphology and provenance

NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc:
- Human temporal neocortex, middle temporal gyrus, BA21, layer 2–3 pyramidal/principal cell.
- 8,903 standardized SWC points: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, no axon.
- Dendritic physical integrity is marked moderate.
- Source metadata records mesiotemporal sclerosis; shrinkage is not reported.
- The file is a partial dendritic reconstruction, not a complete or healthy-control neuron.

The file remains unmodified. Its CC BY 4.0 license and three required attribution elements are recorded in amsn-core/data/human/README.md.

## Important model correction: NEURON Import3D soma and wire convention

The initial unnormalized AMSN cable did not use the same electrical topology as NEURON Import3D. Inspecting NEURON's own read_swc.hoc and import3d_gui.hoc showed two morphology-specific rules.

### Three-point soma

For a standardized NeuroMorpho soma where:
- the first three SWC rows are type 1;
- the two non-root soma points are direct children of the root and have no children;
- all three diameters are equal;
- the sum of root-to-outline-point distances is within 1% of the soma diameter;

NEURON recognizes the pattern and converts it into a spherical soma represented by a three-point cylinder. Its electrical membrane area is \(4\pi r^2\), not the raw two-frustum area of the three SWC points.

This reconstruction satisfies the rule:
- soma diameter: 17.13 µm;
- sum of the two root-to-outline distances: 17.120467 µm;
- relative difference from the diameter: about 0.0556%;
- NEURON-compatible sphere area: 921.859209332 µm².

### Zero-resistance wire attachments

NEURON also treats a soma-attached neurite section as a wire when its same-type unbranched section continues beyond its first point. For this SWC, eight soma-to-neurite connector edges meet that rule:
4, 1035, 1731, 1782, 2645, 3404, 4001, 4055.

Those connector edges are omitted as membrane and axial cable segments in NEURON; the downstream dendritic cable is attached isopotentially to the soma. The total length of the eight omitted connectors is 72.224194 µm.

AMSN now detects this exact standardized pattern and:
- collapses the three soma outline points into the root electrical soma;
- maps the eight zero-resistance wire attachment nodes to the root soma potential;
- omits the eight connector edges from the electrical cable;
- uses the spherical soma area;
- leaves the original SWC geometry and IDs unchanged;
- exposes electrical_node_mapping() so original anatomical IDs still resolve to their electrical vertices.

The special rule is only applied when its structural/geometric conditions pass. Other morphologies retain their original mapping unless explicitly normalized by a supported rule.

## Matching electrical configuration

Both simulators use the same passive physical parameters:

| Parameter | SI value | NEURON value |
|---|---:|---:|
| Axial resistivity | 0.7 Ω·m | 70 Ω·cm |
| Specific membrane resistance | 1.0 Ω·m² | 10,000 Ω·cm² |
| Specific membrane conductance | 1.0 S/m² | 0.0001 S/cm² |
| Specific capacitance | 0.01 F/m² | 1 µF/cm² |
| Leak reversal | −65 mV | −65 mV |
| Current injection | 10 pA | 0.01 nA |

NEURON 9.0.2 imports the exact standardized SWC using Import3D. Each imported section is discretized with an odd number of segments and no segment longer than 5 µm, so the soma centre lies at x=0.5. It produced 125 sections and 2,637 segments.

The NEURON simulation uses fixed-step integration at 0.025 ms, with the passive clamp held through 250 ms. Voltage at 200 ms and 250 ms is compared; the maximum residual across recorded sites is \(1.0\times10^{-9}\) mV.

AMSN uses its exact linear passive steady-state Hines solve:
\[
(G_{leak}+G_{axial})V=G_{leak}E_{leak}+I.
\]

The two AMSN representations are:
- fine normalized cable: 8,893 compartments;
- section-reduced normalized cable: 690 compartments.

## Source and probe sites

Three injection sites and five recording sites are selected by deterministic root-to-node path-distance quantiles in the original SWC. All are mapped directly through NEURON Import3D's SWC point-to-section index and retained exactly in AMSN.

| Site | SWC type | SWC node ID | Selection |
|---|---:|---:|---|
| Soma injection/probe | 1 | 1 | Root |
| Basal injection | 3 | 3784 | 75th path-distance percentile |
| Apical injection | 4 | 5920 | 75th path-distance percentile |
| Basal probe | 3 | 3355 | 50th path-distance percentile |
| Basal probe | 3 | 3814 | 90th path-distance percentile |
| Apical probe | 4 | 6897 | 50th path-distance percentile |
| Apical probe | 4 | 5164 | 90th path-distance percentile |

This gives 3 × 5 = 15 source/probe pairs.

Import3D's geometry-point matching error is at most 0.000027 µm. The distance from an anatomical site to the centre of its selected NEURON segment is at most 2.424330 µm. The soma maps to the segment centre exactly at x=0.5.

## Surface-area agreement after normalization

| Representation | Total membrane area |
|---|---:|
| Raw SWC frustum area (before electrical normalization) | 26,209.054174614 µm² |
| AMSN normalized electrical tree | 23,338.439002801 µm² |
| NEURON segment area | 23,338.438806144 µm² |
| NEURON PT3D frustum area | 23,338.438807496 µm² |

The difference between normalized AMSN and NEURON segment area is **−0.000000843%** (NEURON relative to AMSN). NEURON's PT3D frustum calculation independently reproduces the segment surface area to approximately 0.0000014 µm².

The large 10.95% area difference in earlier runs was not a physical-model discrepancy: it resulted from comparing NEURON's normalized electrical geometry against the unnormalized raw SWC surface. Those failed comparisons are retained in Actions history; the final report uses the corrected like-for-like geometry.

## Electrical results

Each source/probe row reports input resistance at the source, transfer resistance at the probe, and the probe/source voltage ratio. Full 15-row results are stored in the CSV.

### Maximum relative error across all 15 source/probe pairs

| Observable | Fine AMSN vs NEURON | 690-compartment AMSN vs NEURON |
|---|---:|---:|
| Input resistance | 0.422794% | 0.463750% |
| Transfer resistance | 0.517393% | 0.560092% |
| Transfer ratio | 0.664039% | 0.685124% |

### Input resistance by injection site

| Injection site | NEURON | AMSN fine | AMSN sectioned |
|---|---:|---:|---:|
| Soma (MΩ) | 53.932291 | 53.931197 | 53.933617 |
| Basal q75 (MΩ) | 461.691120 | 459.739118 | 459.550028 |
| Apical q75 (MΩ) | 500.928398 | 498.888606 | 498.781506 |

The sectioned representation reduces the number of AMSN electrical compartments from 8,893 to 690, a **92.24% reduction**, while keeping the maximum error below 0.69% for the tested passive DC observables.

All 15 electrical rows were identical between the Python 3.12.16 and Python 3.13.18 Actions jobs at the reported precision.

## Reproducibility and CI

GitHub Actions run [44745099560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44745099560) completed successfully:

| Job | Result |
|---|---|
| Python 3.12.16 package tests | 46 passed in 1.55 s |
| Python 3.13.18 package tests | 46 passed in 1.98 s |
| NEURON 9.0.2 cross-validation, Python 3.12 | success |
| NEURON 9.0.2 cross-validation, Python 3.13 | success |

Both NEURON jobs completed:
- pinned simulator installation;
- Import3D availability check;
- passive cross-simulator run;
- raw workflow output artifact upload.

The 15-row CSV was extracted from the Python 3.12 workflow log; its values match Python 3.13 exactly.

## Interpretation

This is meaningful **cross-simulator numerical validation** of AMSN's normalized passive cable representation on one real partial human dendritic morphology. Three parts now agree:
1. the electrical surface area generated from the morphology;
2. source input resistances;
3. multi-site passive voltage transfer.

The section-reduced electrical model also remains within approximately 0.69% of NEURON in the tested observables.

This does not establish biological accuracy. Both simulators use the same generic passive parameters and the same reconstructed geometry; there are no matched experimental voltage traces in this checkpoint. It also does not validate transient EPSPs, frequency-dependent impedance, active dendritic spikes, voltage-gated calcium, synapses, glia, plasticity or axonal propagation.

## Limitations

- Only one morphology was tested; it has no axon, moderate dendritic completeness and mesiotemporal-sclerosis context.
- Passive parameters are generic, not fitted to this cell, donor, cortical depth, temperature or recording condition.
- The probe locations are mapped to NEURON segment centres; the maximum offset is 2.424330 µm.
- NEURON uses finite-step integration, while AMSN solves the linear DC system directly. The very small 200-to-250 ms voltage residual indicates the NEURON run is near steady state but does not replace a timestep-convergence study.
- Both models use a 1-D cable approximation. No 3-D soma, spine or branch-junction mesh is included.

## Next experiments

1. Repeat NEURON validation at smaller time steps (0.0125 and 0.00625 ms) and segment limits (2.5 and 1.25 µm); record convergence of the 15 observables.
2. Compare transient passive step and synaptic-like current responses, not only DC steady states.
3. Validate on at least two additional license-cleared human L2–3 morphologies with different completeness/pathology metadata.
4. Only after passive reference convergence, reproduce a published human L2–3 active model unchanged and then add dendritic channels and synapse kinetics.

Do not describe this as a complete human-neuron digital twin or biologically calibrated model.

## Sources

- NEURON Import3D SWC reader, including its three-point soma and wire-attachment conventions: https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/read_swc.hoc
- NEURON Import3D section creation, section names and PT3D construction: https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/import3d_gui.hoc
- NeuroMorpho.Org record NMO_290988 and data terms: see amsn-core/data/human/README.md.
- SWC data format: https://github.com/INCF/swc-specification
