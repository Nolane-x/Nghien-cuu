# NEURON temporal and spatial convergence on the human L2–3 passive morphology

**Date:** 2026-11-20 (UTC+7)  
**Code commit:** d6c67083c727e862356a7268671d2fa79bf01a3b  
**GitHub Actions:** [run 44746105586 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44746105586)  
**Reference simulator:** NEURON 9.0.2  
**Raw dataset:** amsn-core/results/neuron_passive_convergence_2026-11-20.csv

## Question

How sensitive are NEURON's passive transient responses to (1) integration timestep and (2) spatial segment size when the same standardized human L2–3 morphology, passive parameters, current injection sites and probe locations are held fixed?

This experiment characterizes the numerical reference simulator independently. It does not yet compare the AMSN transient solver to NEURON.

## Morphology and passive configuration

Source: NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015.CNG.swc:
- human temporal-cortex BA21, layer 2–3 pyramidal/principal cell;
- 8,903 SWC points; soma and basal/apical dendrites, no axon;
- dendritic completeness rated moderate;
- metadata records mesiotemporal sclerosis; shrinkage not reported;
- partial reconstruction, not a healthy-control or complete neuron.

The same Import3D-aware three-point soma and zero-resistance wire normalization described in the NEURON cross-validation report is used. The source SWC is never modified.

Passive parameters:
- Ri = 0.7 Ω·m (NEURON Ra = 70 Ω·cm);
- Rm = 1.0 Ω·m² (g_pas = 0.0001 S/cm²);
- Cm = 0.01 F/m² (1 µF/cm²);
- Eleak = −65 mV;
- injected current = 10 pA;
- fixed-step integration, CVode off;
- clamp current remains on through the 250 ms measurement window.

## Factorial numerical sweep

Two independent numerical factors are changed:

| Factor | Coarse | Fine |
|---|---:|---:|
| Maximum physical segment extent | 5.0 µm | 2.5 µm |
| Fixed integration timestep | 0.025 ms | 0.0125 ms |

This yields four combinations:

| Maximum segment extent | Timestep | NEURON segments |
|---:|---:|---:|
| 5.0 µm | 0.025 ms | 2,637 |
| 5.0 µm | 0.0125 ms | 2,637 |
| 2.5 µm | 0.025 ms | 5,149 |
| 2.5 µm | 0.0125 ms | 5,149 |

The odd nseg rule is retained so section midpoints, including the soma centre, are segment centres. Total NEURON segment area remains 23,338.438806144 µm² in all four configurations.

### Anatomical sites

The same 3 injection sites and 5 probe sites are reused:
- injection: soma 1, basal q75 node 3784, apical q75 node 5920;
- probes: soma 1, basal q50 node 3355, basal q90 node 3814, apical q50 node 6897, apical q90 node 5164.

Each source is paired with all five probes. Nine time checkpoints are recorded: 1, 2, 5, 10, 20, 50, 100, 200 and 250 ms. Total rows: 4 configurations × 3 sources × 5 probes × 9 times = **540**.

Import3D resolves each SWC node to its actual section and arc position, then maps it to the nearest segment centre after each nseg change. The segment-centre mapping offset is therefore reported per source/probe row rather than silently treated as zero.

## Results: temporal timestep sensitivity

At a fixed spatial limit, reducing dt from 0.025 to 0.0125 ms gives:

| Spatial cap | Max absolute voltage difference | RMS voltage difference | Max relative error where reference deflection ≥0.05 mV |
|---:|---:|---:|---:|
| 5.0 µm | 0.008936221 mV | 0.000982751 mV | 0.367656% |
| 2.5 µm | 0.009017677 mV | 0.000991579 mV | 0.372450% |

Relative errors are computed from probe voltage deflections at matching source, probe and time checkpoints. Values below 0.05 mV are excluded from the relative-error maximum to avoid magnifying near-zero values.

## Results: spatial segment sensitivity

At a fixed timestep, reducing the maximum physical segment extent from 5.0 to 2.5 µm gives:

| Timestep | Max absolute voltage difference | RMS voltage difference | Max relative error where reference deflection ≥0.05 mV |
|---:|---:|---:|---:|
| 0.025 ms | 0.009498791 mV | 0.001421479 mV | 0.738397% |
| 0.0125 ms | 0.009417335 mV | 0.001417490 mV | 0.740058% |

The finer mesh increases the segment count from 2,637 to 5,149 (about 95.2% more segments), while retaining exactly the same total PT3D surface area. For the sampled probes and checkpoints, the maximum relative response difference remains below 0.75%.

## Combined coarse-to-fine comparison

Comparing the coarsest configuration (5 µm, 0.025 ms) against the finest tested configuration (2.5 µm, 0.0125 ms):
- maximum absolute voltage difference: 0.006348748 mV;
- RMS voltage difference: 0.001329536 mV;
- maximum relative error for reference deflections ≥0.05 mV: 0.734900%.

The combined maximum absolute difference is smaller than some one-factor differences because temporal and spatial errors can partially cancel. Do not interpret the combined error as evidence that the coarse configuration is more accurate. The separate one-factor comparisons are the relevant sensitivity results.

## Reproducibility

GitHub Actions run [44746105586](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44746105586) completed successfully:
- Python 3.12.16 package suite: 46 passed;
- Python 3.13.18 package suite: 46 passed;
- NEURON 9.0.2 convergence sweep: success on both Python versions;
- each runner produced 540 measurement rows;
- all 540 rows matched exactly at printed precision between Python 3.12 and 3.13.

The complete 540-row dataset from Python 3.12 is committed as a CSV in the results directory. GitHub Actions also preserves the full run output as a workflow artifact for each Python version.

## Interpretation

Within this one partial human morphology, generic passive parameter set, three injection locations, five recording locations and nine observation times:
- halving dt changed recorded responses by less than 0.38% relative on the specified amplitude threshold;
- halving the maximum physical segment extent changed responses by less than 0.75%;
- both tested segmentations preserve the same total membrane area;
- numerical settings are now characterized well enough to select a stable NEURON reference configuration for the next AMSN transient comparison.

This does not prove the morphology or passive parameter set is biologically accurate. It only characterizes numerical sensitivity of NEURON under the chosen passive model.

## Limitations

- One partial morphology; no axon; dendrites moderate; mesiotemporal-sclerosis context; no shrinkage correction reported.
- Generic passive parameters, not experimentally fitted.
- Only passive current clamps; no voltage-gated channels, synaptic conductances, calcium or glia.
- The two spatial meshes are not an exhaustive convergence study; 2.5 µm is the finest tested cap.
- The relative-error threshold excludes reference deflections under 0.05 mV.
- No AMSN transient simulation was compared in this experiment; only NEURON's own numerical convergence was measured.

## Next experiment

Use the finest tested NEURON reference (2.5 µm, 0.0125 ms) to compare against AMSN's time-domain passive solver at the same seven anatomical sites and 10 pA step-current protocol. Compare time traces and summary observables:
1. voltage at 1, 2, 5, 10, 20, 50, 100 and 200 ms;
2. peak and steady-state deflection;
3. rise/decay time and transfer ratio;
4. source and probe mapping positions;
5. timestep refinement of AMSN's backward-Euler solver.

Then repeat on a second license-cleared human L2–3 morphology. Do not add active channels until the transient passive comparison is stable.

## Sources

- NEURON Import3D SWC reader and section creation: https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/read_swc.hoc and https://github.com/neuronsimulator/nrn/blob/master/share/lib/hoc/import3d/import3d_gui.hoc
- NeuroMorpho.Org record NMO_290988 and terms: amsn-core/data/human/README.md.
- SWC file specification: https://github.com/INCF/swc-specification
