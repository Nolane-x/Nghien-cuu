# Handoff — Segev AC source-alignment sensitivity audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** passive frequency-domain source-location sensitivity on two Segev human L2/3 morphologies  
**Status at creation:** implementation committed; GitHub Actions result pending.

## Read first

1. `AGENTS.md`
2. `HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md`
3. `amsn-core/research/HUMAN_MULTI_MORPHOLOGY_AUDIT_2026-11-21.md`
4. `amsn-core/research/SEGEV_FINE_MESH_RESIDUAL_LOCALIZATION_2026-11-21.md`
5. This handoff and its research log.

## Research question

How much of the residual passive AC mismatch between AMSN and NEURON can be attributed to the chosen source-reference location, when both candidate source locations are evaluated on the same refined NEURON morphology and mesh?

The previous Segev source-placement control used DC current clamp. It found that some source coordinates can be separated into two distinct segment centres, while other sources are already aligned or remain indistinguishable under NEURON's per-section nseg cap. A DC result does not establish the frequency dependence of this effect.

## Implementation

- Script: `amsn-core/examples/human_segev_ac_source_alignment_audit.py`
- Workflow: `.github/workflows/amsn-segev-ac-source-alignment.yml`
- Reuses the same SWC importer, source/probe selection and alignment classifier from the existing passive source-placement audit.
- For each non-somatic source, locally refines its NEURON section once. It then compares `Impedance.loc()` at (a) the legacy centre derived from the 0.125 µm base mesh and (b) the SWC-aligned centre on that same final mesh.
- All probe coordinates, morphology, passive parameters and NEURON mesh are held fixed between the two source-reference modes.
- Frequencies: 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.
- Probes: the same five soma/basal/apical points as the existing Segev AC matrix.
- Expected raw output: 2 non-somatic sources × 5 probes × 8 frequencies = 80 rows per morphology.
- Parameters remain Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.

NEURON's `Impedance.loc(x)` defines the current-stimulus or voltage-electrode reference location; `Impedance.compute(freq)` calculates transfer impedance relative to that location. See the [NEURON 9.0 documentation](https://www.neuronsimulator.org/en/9.0.0/progref/analysis/programmatic/impedance.html).

## Interpretation rules

- `distinct_aligned`: two different segment centres exist on one common mesh. Only these rows can contribute to a source-placement sensitivity estimate.
- `pre_aligned`: the base mesh already places the legacy source within the strict 0.002 µm target tolerance. The two modes are identical and are not a sensitivity experiment.
- `unresolved_nseg_cap`: the NEURON nseg cap prevents distinct source placements. Identical-mode rows are retained for traceability but excluded from sensitivity summaries.
- A small within-NEURON source-placement effect would bound this particular numerical confound; it would not prove AMSN biologically accurate.
- A large effect would motivate matched-source AC comparisons and a careful review of whether the original matrix used equivalent physical reference positions.
- Do not change Ri/Rm/Cm/Eleak to force agreement.

## Validation gate

The workflow must pass the full AMSN pytest suite, verify NEURON 9.0.2, write exactly 80 rows per morphology, and upload raw CSV artifacts. Inspect source alignment statuses before interpreting aggregate metrics.

## Known limits

This is a passive, linearized, within-NEURON source-reference sensitivity test. It does not validate active channels, synaptic kinetics, calcium, healthy human physiology, or a biological parameter set. It does not turn a source placement that is unresolved under nseg into a valid paired contrast.

## Next step

Inspect both job logs and raw CSV artifacts, calculate per-source/per-frequency effects, and compare the largest effects with the previously observed AMSN-versus-NEURON transfer residuals. If the source-reference effect is insufficient to explain those residuals, move to probe interpolation/section-junction and axial/capacitance mapping audits without changing passive parameters.
