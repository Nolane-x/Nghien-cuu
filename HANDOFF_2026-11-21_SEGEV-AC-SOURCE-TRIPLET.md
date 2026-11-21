# Handoff — Segev three-reference passive AC source audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** distinguish legacy segment-centre, exact SWC-arc and refined segment-centre source references  
**Implementation commit:** pending at creation  
**Validation:** pending GitHub Actions.

## Start here

1. Read AGENTS.md, HANDOFF.md and HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md.
2. Read HANDOFF_2026-11-21_SEGEV-AC-SOURCE-PLACEMENT.md and its research log for the preceding two-reference AC sensitivity experiment.
3. Read this handoff and research/RESEARCH_LOG_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md.

## Why a three-reference experiment is needed

The preceding same-mesh AC audit compared two positions: the old 0.125 µm base-mesh segment centre and the nearest centre after local refinement. It established within-NEURON sensitivity to that shift.

However, the existing AMSN-versus-NEURON frequency audit calls Impedance.loc() at the exact SWC-derived section coordinate (normalized_x), not at either segment-centre coordinate. A direct comparison with the cross-simulator baseline therefore needs to include the exact SWC coordinate as an explicit third mode.

NEURON 9.0 documentation describes Impedance.loc(x, sec=...) as the fixed current-stimulus or voltage-electrode location used for transfer impedance; compute(freq) then calculates transfer impedance relative to that location. See https://www.neuronsimulator.org/en/9.0.0/progref/analysis/programmatic/impedance.html.

## Experimental design

For each non-somatic source, compare on one identical final NEURON mesh:

1. legacy_base_center: base-mesh nearest segment centre captured before local refinement.
2. exact_swc_arc: exact section coordinate derived from the SWC arc; this matches the coordinate used by human_passive_frequency_response_audit.py.
3. refined_center: nearest segment centre after local section refinement.

All three modes share:
- The same Import3D morphology and NEURON 9.0.2 process.
- The same final section segmentation.
- The same five SWC-derived probe coordinates.
- The same passive parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.
- Frequencies 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.

The raw CSV contains the three impedance values plus pairwise complex, magnitude and phase deltas for:
- legacy → exact SWC arc (the primary comparison with the source-coordinate convention in the prior cross-simulator AC audit);
- exact SWC arc → refined centre (the residual from snapping the exact coordinate to a refined centre);
- legacy → refined centre (continuity with the earlier two-reference audit).

## Interpretation rules

- The three-reference experiment quantifies source-coordinate sensitivity within NEURON; it does not itself validate AMSN.
- legacy_to_exact should be compared with the source-coordinate convention used by the prior cross-simulator matrix.
- exact_to_refined measures the extra effect of centre-snapping.
- legacy_to_refined reproduces the preceding two-reference contrast.
- pre_aligned and unresolved_nseg_cap remain explicitly labelled. The unresolved legacy/refined-centre pair is not a valid distinct-centre contrast; do not treat a zero delta as evidence of source insensitivity.
- Keep absolute transfer magnitudes alongside relative errors, especially for weak paths.
- Do not tune Ri/Rm/Cm/Eleak to improve agreement.

## Validation gate

Both morphology jobs must run all AMSN tests with NEURON 9.0.2, produce 80 rows per morphology (2 sources × 5 probes × 8 frequencies), and upload the raw CSV and log. Inspect the row count, source statuses, per-source frequency profiles and pairwise effect sizes before updating the multi-morphology interpretation.

## Known limits

The two Segev morphologies are individual human temporal L2/3 reconstructions with moderate dendritic completeness and incomplete axons. Passive parameters remain generic assumptions, not fitted human parameters. This experiment does not establish active channel, synaptic, calcium, plasticity, metabolic or network validity.
