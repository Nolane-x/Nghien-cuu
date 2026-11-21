# Handoff — Segev AC source-placement alignment

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** transfer-impedance comparison of exact SWC source, nearest segment-centre source and weighted adjacent-centre source in NEURON 9.0.2  
**Status:** implementation committed; four morphology/mesh jobs pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-TRANSIENT-SOURCE-ALIGNMENT.md.
3. HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md.
4. HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md.

## Research question

The native transient source-placement experiment showed that splitting a point current between adjacent NEURON segment centres can materially improve some morphologies, but the effect is not universal. This AC experiment checks whether the same source placement choice changes complex transfer impedance in the frequency domain.

## Method

For each of the two Segev morphologies at mesh caps 0.125 and 0.0625 µm:
- Frequencies: 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.
- Three source modes:
  1. exact_swc_arc: NEURON Impedance.loc at the exact SWC-derived section coordinate;
  2. nearest_segment_centre: NEURON Impedance.loc at the nearest segment centre;
  3. weighted_adjacent_centres: linear complex superposition of NEURON transfer responses from the lower/upper segment centres using weights (1-w),w.
- Three probe readouts: exact SWC arc, nearest centre and complex-linear interpolation between adjacent centres.
- AMSN always injects the AC current at the exact SWC electrical node on its unresampled CableTree.

The weighted source is mathematically equivalent to distributing the same total AC current across the two bracket locations in a linear passive system. It is not asserted to be the unique exact continuum source.

Expected per configuration: 3 sources × 5 probes × 8 frequencies × 3 source modes × 3 probe modes = 1,080 raw rows and 135 grouped summary rows.

## Validation gates

- Full 81-test AMSN suite passes.
- Every source interpolation bracket is valid and weights sum to one.
- All source/probe/frequency/source-mode/probe-mode combinations are emitted exactly once.
- All transfer magnitudes, phases and errors are finite.
- Raw CSV and grouped summary are uploaded.

## Interpretation limits

This compares discrete source-placement approximations on a passive linear model. A better numerical match does not prove the source model is physically exact or biologically valid. Preserve all source and probe modes; do not change Ri/Rm/Cm/Eleak.

## Next step

If transient and AC source-placement conclusions agree, keep weighted source placement as an optional diagnostic for the morphologies where it improves results. If they disagree, investigate how the discrete source distribution maps to NEURON's AC current reference before changing any default.


## Verified results — AC source-placement alignment (21/11/2026)

AC source-placement workflow [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4 jobs; Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4.

Each configuration generated 1,080 raw rows and 135 summaries across 3 sources × 5 probes × 8 frequencies × 3 source modes × 3 probe modes.

Weighted adjacent-centre source placement strongly improves NMO_68175:
- 0.125 µm: exact/nearest probe max error 0.169222%→0.068720%; interpolated max 0.125637%→0.071947%.
- 0.0625 µm: exact/nearest 0.099512%→0.069568%; interpolated 0.104835%→0.072209%.

NMO_68174 remains mixed:
- 0.125 µm: modest improvement for exact/nearest probes; interpolation median improves but tail worsens slightly.
- 0.0625 µm: median/P95 worsen for exact/nearest; all three aggregate interpolated metrics worsen.

**Decision:** keep weighted source as an optional diagnostic, not a universal default. The AC result corroborates the transient source-placement finding on NMO_68175.

Full report: [HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md); summary [CSV](amsn-core/results/human_segev_ac_source_alignment_summary_2026-11-21.csv); comparison [CSV](amsn-core/results/human_segev_ac_source_alignment_comparison_2026-11-21.csv).


## Raw AC worst-path localization — 21/11/2026

All four raw AC configurations reach maximum exact/nearest-probe error at 3 kHz. NMO_68174's worst path remains basal q75→apical q90 at both meshes. NMO_68175's nearest-source worst path changes with mesh; weighted source placement moves the worst remaining path to basal q75→apical q90 at both mesh caps.

The residual is concentrated in high-frequency apical transfers. Weighted source changes the spatial distribution of the remaining error, not merely its magnitude. See [worst-pair CSV](amsn-core/results/human_segev_ac_source_alignment_worst_pairs_2026-11-21.csv).
