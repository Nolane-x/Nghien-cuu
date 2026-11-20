# Research log — 2026-11-20 — NEURON passive cross-validation

## Objective
Cross-validate AMSN's passive cable and section-reduced cable against NEURON 9.0.2 using the same NeuroMorpho standardized human L2–3 SWC and equivalent passive physical parameters.

## Source review and model correction
Read NEURON Import3D source:
- share/lib/hoc/import3d/read_swc.hoc
- share/lib/hoc/import3d/import3d_gui.hoc

Found NEURON's special three-point soma recognition and zero-resistance wire attachment handling for long soma-attached dendritic stems. The source morphology satisfies these conditions:
- first three SWC rows are soma;
- root-to-outline-point path sum 17.120467 µm vs diameter 17.13 µm;
- 8 soma-attached dendrite root edges meet the Import3D wire rule;
- wire connector path total 72.224194 µm.

Added automatic exact-pattern detection to AMSN. It collapses the 3-point outline and 8 wire roots to the soma electrical vertex, removes the connector edges from cable geometry, and uses a sphere area of 4πr². The raw SWC remains unchanged and has a traceable SWC-to-electrical node map. The same rule is now applied to the section-based cable resampler.

## Final CI and exact source commit
- AMSN code commit: 56eaf350334a3f1795f4070edc5b96a1748fcc89
- Final NEURON script uses the Import3D section naming map, odd nseg, centre-aligned soma, and normalized area comparison.
- GitHub Actions: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44745099560
- Python 3.12.16: 46 passed in 1.55 s.
- Python 3.13.18: 46 passed in 1.98 s.
- NEURON 9.0.2 cross-validation jobs passed on both Python versions.
- All 15 source/probe rows were identical between Python versions at printed precision.

## Configuration
- NEURON 9.0.2; Import3D same SWC.
- 125 sections, 2,637 NEURON segments; odd nseg; maximum physical segment 5 µm.
- AMSN fine normalized tree 8,893 compartments; sectioned tree 690 compartments.
- Ri 0.7 Ω·m; Rm 1.0 Ω·m²; Cm 0.01 F/m²; Eleak −65 mV.
- 10 pA injection; 3 sources × 5 probes = 15 pairs.
- NEURON dt 0.025 ms, compare 200 ms and 250 ms; maximum residual 1e-9 mV.
- NEURON site mapping via Import3D id2pt/point2sec, section type/nameindex/first and PT3D arc position.

## Geometry result
- Raw SWC frustum summary: 26,209.054174614 µm².
- AMSN normalized electrical tree area: 23,338.439002801 µm².
- NEURON segment area: 23,338.438806144 µm².
- Relative area difference: −0.000000843%.
- NEURON PT3D frustum area 23,338.438807496 µm².

## Cross-simulator metrics
Maximum relative error across 15 source/probe pairs:
- input resistance: 0.422794% fine AMSN; 0.463750% sectioned;
- transfer resistance: 0.517393% fine; 0.560092% sectioned;
- transfer ratio: 0.664039% fine; 0.685124% sectioned.

NEURON source input resistances: soma 53.932291 MΩ, basal q75 461.691120 MΩ, apical q75 500.928398 MΩ.
AMSN fine: 53.931197, 459.739118, 498.888606 MΩ.
AMSN sectioned: 53.933617, 459.550028, 498.781506 MΩ.
Sectioned reduction: 8,893 to 690 compartments (92.24%).

## Raw data
Complete 15-row CI measurement table is saved at amsn-core/results/neuron_passive_cross_validation_2026-11-20.csv.

## Interpretation and limitations
The passive cable geometry and transfer are numerically close between NEURON and AMSN on this one cell. This is simulator cross-validation, not experimental biological validation. Parameters are generic; the cell is a partial dendritic reconstruction with no axon, moderate dendritic integrity, mesiotemporal-sclerosis context and no shrinkage record. Active channels, synaptic dynamics, calcium, glia and transient response are not validated.

## Next
Perform NEURON timestep convergence (dt 0.0125/0.00625 ms; segment cap 2.5/1.25 µm); then transient passive response comparisons; then a second human morphology; later reproduce Eyal et al. unchanged before active fitting.
