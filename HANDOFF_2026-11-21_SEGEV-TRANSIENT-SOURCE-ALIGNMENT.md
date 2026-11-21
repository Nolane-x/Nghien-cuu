# Handoff — Segev transient source-placement alignment

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** nearest-centre point-current injection versus charge-conserving weighted split across adjacent NEURON segment centres  
**Status:** implementation committed; four morphology/mesh jobs pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-PASSIVE-TRANSIENT.md.
3. HANDOFF_2026-11-21_SEGEV-PASSIVE-ADMITTANCE-OPERATOR.md.
4. HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md.

## Research question

The time/space matrix showed that cross-simulator disagreement is nearly invariant with dt, while spatial refinement affects the two cells differently. The NEURON stimulus is currently injected at the nearest segment centre, while AMSN injects at the exact SWC electrical node.

Does distributing the same 10 pA current across the two adjacent NEURON segment centres using barycentric interpolation weights reduce the source-location component of the transient discrepancy?

## Source-placement variants

1. nearest_segment_centre: one IClamp at the nearest NEURON segment centre, the existing baseline.
2. weighted_adjacent_centres: two IClamps at the bracketing segment centres, with amplitudes (1-w)*10 pA and w*10 pA, where w is the exact SWC arc interpolation weight.

The weighted split conserves total injected current at every active time sample. If both bracket locations resolve to the same segment, the full current is placed there once.

The NEURON probes are still read in two ways: nearest segment centre and linear interpolation at the exact SWC arc. AMSN remains injected at the exact SWC electrical node.

## Matrix

- Morphologies: NMO_68174 / cell1125 and NMO_68175 / cell1204.
- NEURON mesh caps: 0.125 and 0.0625 µm.
- Time step: 0.05 ms; duration 30 ms; pulse +10 pA from 2 to 12 ms.
- Fixed passive parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.
- NEURON 9.0.2; both solvers use backward Euler.

Each cell/mesh configuration produces 60 summary rows and 18,030 trace rows.

## Validation gates

- Full 81-test AMSN suite passes.
- The exact NEURON current sum equals the 10 pA baseline at every active time sample.
- Both variants use identical time grids.
- Source weights sum to one; no zero-weight clamps are created.
- All traces and metrics are finite.
- Raw traces preserve source weights, bracket geometry, nearest-centre offsets and total IClamp current.

## Interpretation limits

A weighted split current is a discrete source-mapping diagnostic, not asserted to be the exact continuum point source. A better match would identify source-placement sensitivity, not validate biological current injection geometry. Keep both modes; do not tune passive membrane parameters.

## Next step

If the weighted split improves agreement consistently, retain it as an optional source-alignment mode and test it against direct NEURON impedance. If improvement is morphology-/source-dependent, preserve it as a diagnostic only and proceed to a true reduced fine-tree operator.


## Verified results — source-placement alignment (21/11/2026)

Final workflow [44910070325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325) passed all four morphology/mesh jobs. Core CI [44910070326](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326) passed 4/4.

Each job produced 18,030 trace rows and 60 summary rows. Total clamp current was checked at every sample; maximum error was 1.735e-18 nA.

Weighted two-centre source placement is morphology-/mesh-dependent:
- NMO_68175 benefits at both meshes: maximum interpolated-probe NRMSE falls to 0.000192% from 0.000791% at 0.125 µm and from 0.002633% at 0.0625 µm.
- NMO_68174 at 0.125 µm is mixed, with interpolated maximum falling 0.000357%→0.000265%.
- NMO_68174 at 0.0625 µm worsens for interpolated probes: 0.000190%→0.000265%, 10 worsened / 0 improved / 5 unchanged pairs.

**Decision:** retain weighted source placement as an optional diagnostic, not a universal default.

Full report: [HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md); summary [CSV](amsn-core/results/human_segev_transient_source_alignment_summary_2026-11-21.csv).


## AC source-placement corroboration — 21/11/2026

The AC source-placement experiment [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4, Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4. It corroborates the transient result: weighted source placement strongly improves NMO_68175 at both meshes, while NMO_68174 remains mixed and worsens on interpolated probes at 0.0625 µm. Do not promote weighted source to a universal default. See [AC source report](HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md).


## AC cross-domain source-placement localization — 21/11/2026

The AC source-placement experiment [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4. Across all four configurations, maximum errors occur at 3 kHz and are concentrated in apical transfer paths. Weighted source changes the worst remaining source/probe pair for NMO_68175, consistent with a path-dependent rather than global effect. See [AC source report](amsn-core/research/HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md) and [worst-pair CSV](amsn-core/results/human_segev_ac_source_alignment_worst_pairs_2026-11-21.csv).
