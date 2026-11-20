# Handoff — AMSN fast-AMPA temporal convergence (2026-11-20)

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code snapshot:** `a78fcd1ab00d4175b60898b9ad539d84d9d8bf74`  
**Temporal audit:** [GitHub Actions 44760319787 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787)  
**Research report:** `amsn-core/research/HUMAN_AMPA_TEMPORAL_CONVERGENCE_2026-11-20.md`  
**Raw traces:** `amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv`  
**Previous spatial audit:** [44758746509 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44758746509)  
**Previous single-compartment audit:** [44757208267 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267)

## Start here

1. Read `AGENTS.md`, `HANDOFF.md`, `research/AMSN_RESEARCH_DOSSIER.md`.
2. Read the latest handoff for the active AMSN topic and `amsn-core/research/HUMAN_AMPA_TEMPORAL_CONVERGENCE_2026-11-20.md`.
3. Inspect the current main head and latest CI runs before changing code.
4. Keep GitHub main as the durable research record. Do not leave results only in chat.
5. Preserve failed experiments and all source provenance. Do not overwrite old research logs or remove Actions history.

## Current status in one paragraph

The one-compartment voltage/current audit passes against NEURON 9.0.2 at dt = 0.025, 0.0125 and 0.00625 ms. On the partial NMO_290988 human morphology, an AMSN 2,000-Hz sectioned mesh (2,541 compartments) compared against a 0.5-um NEURON mesh (25,233 segments) achieved a q90 basal-probe RMS discrepancy of about 0.00384 mV at dt 0.00625 ms. A new five-timestep sweep (0.025 to 0.0015625 ms) shows each simulator's own trace converges strongly with dt reduction, but the cross-engine q90 RMS difference stays around 0.00380–0.00385 mV. The remaining difference is therefore close to a spatial/representation floor for this particular configuration; it is not dominated by the tested temporal range. This is numerical evidence for one passive morphology/input configuration, not biological validation.

## Implemented/verified experiments

### 1. Single-compartment equivalence

Script: `amsn-core/examples/single_compartment_voltage_audit.py`  
Workflow: `.github/workflows/amsn-single-compartment-audit.yml`  
Run 44757208267, 2/2 jobs successful (Python 3.12 and 3.13, NEURON 9.0.2).

A single NEURON segment and one AMSN compartment share exact NEURON-reported membrane area, passive parameters, initial voltage and an Exp2Syn event. The audit separately checks aligned conductance, NEURON's recorded pre-update synaptic current, reconstructed current, implicit end-step current and voltage. Controlled voltage/g/current reconstruction gates pass at the script's stated numerical thresholds. Read the report/log for exact metrics and units.

### 2. Spatial mesh sensitivity and NEURON segment refinement

Scripts:
- `amsn-core/examples/human_ampa_mesh_frequency_sweep.py`
- `amsn-core/examples/human_ampa_neuron_segment_sweep.py`

Workflow: `.github/workflows/amsn-ampa-spatial-mesh-audit.yml`  
Run 44758746509, 1/1 job successful; artifact 14640046511.

The first sweep varies AMSN mesh reference frequency from 100 to 2,000 Hz. The second fixes AMSN at 2,000 Hz and refines NEURON segments from 5 to 0.5 um. The 5-um NEURON q90 trace had a large self-discretization difference; with 0.5 um the q90 mapping offset is 0.242787 um and AMSN-vs-NEURON q90 error is 0.003840 mV RMS / 0.006433 mV maximum absolute at dt 0.00625 ms.

Do not use the old 5-um NEURON output as a ground-truth reference for this fast dendritic EPSP.

### 3. Fast-AMPA temporal convergence

Script: `amsn-core/examples/human_ampa_temporal_convergence.py`  
Workflow: `.github/workflows/amsn-ampa-temporal-convergence.yml`  
Run 44760319787, 1/1 job successful; artifact 14640319049.

Fixed spatial meshes:
- NEURON: 0.5-um maximum section length, 25,233 segments.
- AMSN: 2,000-Hz electrotonic mesh, 2,541 compartments.

Timesteps: 0.025, 0.0125, 0.00625, 0.003125, 0.0015625 ms. Duration 5 ms. Source SWC 3784 (basal q75); probes SWC 3784, 1 (soma), 3814 (basal q90). Event AMPA-like peak 0.8 nS; tau 0.2/2 ms; Erev 0 mV; fixed passive parameters from prior audits.

Key q90 results:

| dt (ms) | Cross-engine max abs (mV) | Cross-engine RMS (mV) | NEURON self RMS vs finest (mV) | AMSN self RMS vs finest (mV) |
|---:|---:|---:|---:|---:|
| 0.025 | 0.006266 | 0.003798 | 0.088665 | 0.088695 |
| 0.0125 | 0.006376 | 0.003826 | 0.041208 | 0.041222 |
| 0.00625 | 0.006433 | 0.003840 | 0.017625 | 0.017631 |
| 0.003125 | 0.006461 | 0.003847 | 0.005869 | 0.005871 |
| 0.0015625 | 0.006475 | 0.003851 | 0 | 0 |

Both solvers' own temporal traces converge strongly as dt is reduced. Their cross-engine error remains nearly flat (~0.00385 mV RMS and ~0.00648 mV maximum absolute at q90). This suggests the residual is now dominated by spatial representation/mapping/area-lumping differences or other fixed model-form differences rather than the tested timestep range. This is a working interpretation, not a uniquely identified cause.

### Raw data and report

- Report: `amsn-core/research/HUMAN_AMPA_TEMPORAL_CONVERGENCE_2026-11-20.md`.
- Raw CSV: `amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv`, 18,615 data rows.
- Compressed CI artifact: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787/artifacts/14640319049.
- The raw CSV contains timestep, time, site, SWC ID, NEURON deflection, AMSN deflection, difference, NEURON conductance and aligned analytic conductance.

## Harness defects preserved in history

The temporal audit took three iterations. These negative runs must remain in Actions history and should be mentioned in the research log:

1. Run 44759371095: coarse/fine timestep ratio was inverted and produced a zero slice step.
2. Run 44760000836: after fixing the ratio, old NEURON `Vector.record()` objects were retained across repeated `finitialize()` calls. Their data was mutated between dt runs and caused the nested time-grid assertion to fail.
3. Final fix in `a78fcd1ab00d4175b60898b9ad539d84d9d8bf74`: timestep nesting now uses `dt_coarse/dt_finest`, checks the nested time vectors with a tolerance, copies every NEURON record vector into independent NumPy arrays and does not retain the HOC record vectors. The NEURON docs describe how registered record vectors are updated during later runs: https://www.neuronsimulator.org/en/9.0.1/progref/programming/math/vector.html.
4. Run 44760319787: final temporal sweep passed with all five timestep values and raw output preserved.

## Provenance and scientific limits

- Morphology: NeuroMorpho NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`, partial reconstruction, moderate dendritic completeness, metadata indicates mesiotemporal sclerosis, no axon. Keep CC BY 4.0 attribution.
- The synaptic waveform and passive parameters are engineering comparison settings, not patient/cell-specific calibration.
- The model has passive cable dynamics plus a prescribed conductance synapse. It does not include voltage-gated dendritic channels, NMDA Mg2+ block, spine neck, calcium signaling, plasticity, gene expression, metabolism or astrocyte coupling.
- NEURON 0.5 um is the finest numerical reference in this sweep, not exact analytical truth or experimental truth.
- No experimental trace was fitted and no universal AMPA error tolerance has been declared.
- Do not infer intelligence, consciousness or whole-brain function from these neuron-level results.

## Next concrete work

1. **Spatial floor investigation at finest time step:** hold dt=0.0015625 ms and NEURON 0.5 um fixed; sweep AMSN reference frequency above 2,000 Hz (e.g. 2,000, 3,000, 4,000 Hz) while protecting source and probes. Measure whether the ~0.00385-mV q90 RMS floor decreases and how compartment count grows.
2. Repeat the same spatial test at another basal branch and an apical site to avoid tuning one protected path.
3. Inspect/quantify area allocation around protected SWC points and compare exact path-integral geometry with the control-volume lumping.
4. Only after spatial and temporal errors are separated, propose numerical acceptance criteria. Do not tune parameters to make CI green.
5. Reproduce the original Eyal/ModelDB 238347 cell with its own morphology and mechanisms before calling AMSN a matched human L2/3 reproduction; check its upstream archive license/provenance before vendoring.
6. Only after AMPA and voltage integration have explicit error budgets should voltage-dependent NMDA/Mg2+ block be added.
