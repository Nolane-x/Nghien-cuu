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

## Verified results — workflow 44899442076

**Status:** both NEURON 9.0.2 morphology jobs passed; both produced 80 rows and uploaded raw CSV + log. The accompanying Core CI workflow 44899349672 passed Python 3.12/3.13 tests and NEURON cross-validation.

### Source-coordinate results

- NMO_68174 / cell1125:
  - basal q75 (SWC 1577) is pre_aligned at 0.00144089 µm; it is not a distinct-source contrast.
  - apical q75 (SWC 9934) is distinct_aligned: legacy centre offset 0.00832399 µm, refined-centre offset 0.00196022 µm.
  - legacy → exact-SWC transfer-complex maximum by frequency (0.1, 1, 10, 30, 100, 300, 1,000, 3,000 Hz): 0.0003209, 0.0003215, 0.0003790, 0.0006844, 0.0020304, 0.0057770, 0.0141009, 0.0219544%.
  - exact-SWC → refined-centre complex deltas are 0 at exported precision for all eight frequencies.
- NMO_68175 / cell1204:
  - basal q75 (SWC 3253) is distinct_aligned: legacy centre offset 0.0876304 µm, refined-centre offset 0.000504592 µm.
  - legacy → exact-SWC transfer-complex maximum by frequency: 0.0017634, 0.0017668, 0.0020825, 0.0037624, 0.0112115, 0.0330902, 0.1042289, 0.2289258%.
  - exact-SWC → refined-centre complex deltas are 0 at exported precision for all eight frequencies.
  - apical q75 (SWC 7640) is unresolved_nseg_cap. The identical legacy/exact/refined output in this case is not evidence of source insensitivity and must be excluded from distinct-source sensitivity summaries.

Interpretation: the measurable legacy-to-exact effect is concentrated in the source site that actually changes segment identity; the exact SWC coordinate and refined segment centre return identical NEURON impedance values for the tested source sites. The existing cross-simulator frequency audit uses the exact SWC coordinate, so its reference convention is consistent with this result. This does not establish biological validity or explain all remaining AMSN–NEURON residuals.

### Raw artifacts

- [NMO_68174 CSV + log, artifact 14705865103](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076/artifacts/14705865103)
- [NMO_68175 CSV + log, artifact 14705880425](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076/artifacts/14705880425)
- [Triplet workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076)
- [Core CI](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899349672)

### Follow-up

The next controlled variable is probe/readout position. Continue from [HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md](HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md). Keep source fixed at the exact SWC coordinate, and compare exact SWC probe readout, nearest segment centre and complex interpolation on one mesh.
