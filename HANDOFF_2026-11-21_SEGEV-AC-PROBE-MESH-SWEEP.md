# Handoff — Segev AC probe-coordinate mesh convergence

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** convergence of exact-SWC, nearest-centre and complex-interpolated probe readouts  
**Status:** mesh-sweep workflow committed; Actions result pending.

## Read first

1. AGENTS.md, HANDOFF.md and HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md.
2. HANDOFF_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md.
3. HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md.
4. This handoff and research/RESEARCH_LOG_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md.

## Why a mesh sweep is required

The 0.125 µm probe audit showed:
- Exact-SWC and nearest-centre NEURON transfer readouts were identical at exported precision.
- Complex-linear interpolation changed some probe values by up to 0.057785% for NMO_68174 and 0.095872% for NMO_68175.
- Rejoining the probe audit to the 0.125 µm AMSN/NEURON frequency matrix showed interpolation did not improve every pair. NMO_68174: 26 improved, 70 worsened, 24 unchanged. NMO_68175: 64 improved, 32 worsened, 24 unchanged.
- NMO_68175's worst exact-SWC cross-simulator transfer error fell from 0.169222% to 0.077077% under interpolation for basal q75 → apical q50 at 3 kHz. The same method was not uniformly beneficial for NMO_68174.

This is a material, morphology-dependent readout effect. It must be tested across spatial resolution before any readout convention is changed.

## Experimental matrix

Six NEURON 9.0.2 jobs:
- NMO_68174 / cell1125 at 0.25, 0.125 and 0.0625 µm maximum segment length.
- NMO_68175 / cell1204 at 0.25, 0.125 and 0.0625 µm maximum segment length.

Each job uses:
- Three exact-SWC source references: soma, basal q75 and apical q75.
- Five exact-SWC probes: soma, basal q50/q90 and apical q50/q90.
- Eight frequencies: 0.1, 1, 10, 30, 100, 300, 1,000 and 3,000 Hz.
- Three probe readouts: exact SWC coordinate, nearest segment centre, complex-linear interpolation between adjacent segment centres.
- Fixed passive parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m² and Eleak=−65 mV.

Expected: 120 rows per job, 720 rows total. Each output row records its mesh cap.

## Analysis protocol

For each morphology / mesh / source / probe / frequency:
1. Confirm exact-SWC vs nearest-centre equality/difference.
2. Compute exact-SWC vs complex-interpolated complex, magnitude and phase changes.
3. Join the result one-to-one to the matching cross-simulator frequency audit by morphology, source, source SWC ID, probe, probe SWC ID and frequency.
4. Compare both NEURON readouts against the same AMSN complex impedance.
5. Report medians, p95, maxima, rows improved/worsened/unchanged, and the identity of worst pairs.
6. Compare all statistics across mesh caps. Do not infer convergence from a single maximum or from a single cell.

## Interpretation guardrails

- Complex interpolation remains a diagnostic, not ground truth.
- A smaller aggregate residual does not justify changing the canonical readout if a subset of probes worsens.
- Relative complex error must be interpreted with absolute transfer magnitude; weak pathways can have inflated relative residuals.
- Do not change Ri/Rm/Cm/Eleak.
- Numerical simulator agreement does not establish biological validity.

## Validation gate

All six jobs must pass the complete 81-test AMSN suite, verify NEURON 9.0.2, produce exactly 120 rows per job and upload raw CSV + logs. Inspect all six raw artifacts before recording final conclusions.

## Next step after this sweep

If interpolation effects reduce consistently with mesh refinement, quantify their continuum limit and determine whether any matched-support interpolation should be adopted for specific probe classes only. If effects remain site-specific or non-monotone, move to explicit matched-support geometry at branchpoints and section junctions, and keep exact-SWC as the documented baseline.
