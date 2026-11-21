# Handoff — Segev native passive transient cross-validation

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** time-domain passive pulse response of the native NEURON segment tree versus AMSN's unresampled SWC CableTree  
**Status:** implementation committed; two-cell CI pending.

## Read first

1. AGENTS.md and HANDOFF.md.
2. HANDOFF_2026-11-21_SEGEV-PASSIVE-ADMITTANCE-OPERATOR.md.
3. Reports: HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md and HUMAN_SEGEV_MEMBRANE_AREA_SUPPORT_AUDIT_2026-11-21.md.
4. This handoff and research/RESEARCH_LOG_2026-11-21_SEGEV-PASSIVE-TRANSIENT.md.

## Research question

Do the native NEURON 9.0.2 fine-segment model and AMSN's unresampled node-centred SWC cable produce matching passive voltage waveforms in the time domain when driven by the same current pulse?

This is deliberately different from the preceding matched-support admittance test:
- NEURON is simulated directly on its native Import3D segment tree at 0.125 µm.
- AMSN is simulated on its original electrical SWC-node CableTree.
- The stimulus is injected at the exact AMSN electrical node and at NEURON's nearest segment centre to the mapped SWC source arc. The source-centre offset is reported rather than hidden.
- NEURON probe voltage is read both at the nearest segment centre and by linear interpolation between adjacent segment centres bracketing the exact SWC arc.

## Protocol

For each cell:
- Three source sites: soma, basal q75 and apical q75.
- Five probe sites: soma, basal q50/q90 and apical q50/q90.
- Rectangular current pulse: +10 pA from 2 ms to 12 ms.
- Total duration 30 ms; dt=0.05 ms; 601 voltage samples.
- Fixed passive parameters: Ri=0.7 Ω·m, Rm=1.0 Ω·m², Cm=0.01 F/m², Eleak=−65 mV.
- Both simulators use fully implicit backward Euler: AMSN CableTree.step_passive; NEURON h.secondorder=0.
- NEURON 9.0.2, maximum segment length 0.125 µm.

Each morphology should produce 3×5×601 = 9,015 trace rows and 3×5×2 = 30 summary rows (nearest-centre and linearly interpolated probe readouts).

## Reported metrics

- Full waveform RMSE and maximum absolute voltage error.
- NRMSE normalized by the peak NEURON voltage deflection.
- Peak amplitude and peak-time differences.
- Signed waveform area under the curve.
- Late-pulse mean and 30 ms recovery voltage.
- Source/probe segment-centre mapping offsets.

Absolute voltage errors remain essential for weak distal transfer paths; relative errors alone can be misleading.

## Interpretation guardrails

- This compares native NEURON fine segmentation against AMSN's node-centred SWC representation. It is not the matched-support projected operator reported in the prior handoff.
- The nearest-centre source placement is not exactly the continuous SWC arc. Report its offset and do not pretend this is zero.
- Linear interpolation is a diagnostic probe readout, not automatically physical ground truth.
- Same passive parameters and integration method do not constitute biological validation.
- Do not retune Ri/Rm/Cm/Eleak based on one waveform.

## Validation gate

Both morphology jobs must pass the full 81-test AMSN suite, run NEURON 9.0.2, record exactly 9,015 rows and 30 summary rows, and upload trace CSV + summary CSV + log. Review source/probe offsets and absolute peak sizes before interpreting normalized waveform errors.

## Next step

If native transient traces and the matched-support frequency operator agree, compare direct NEURON Impedance at the same source/probe locations against the measured transient transfer function. If residuals remain, isolate spatial versus temporal error using a dt refinement sweep and source-placement refinement. Only after this passive baseline is stable should active channels/synapses be introduced.


## Verified results — native passive transient comparison (21/11/2026)

The native transient workflow [44907890895](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895) passed 2/2 cells, and Core CI [44907890934](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934) passed 4/4 jobs.

Both models used a 10 pA pulse from 2–12 ms, 30 ms duration, dt=0.05 ms and backward Euler. Each cell produced 9,015 trace rows and 30 summary rows. Maximum waveform NRMSE: 0.001641% (cell1125) and 0.002370% (cell1204); maximum peak-amplitude error: 0.002166% and 0.003375%; maximum absolute voltage error: 5.147e-6 mV and 4.424e-6 mV.

Source-centre offsets were at most 0.003185 µm / 0.044099 µm and probe offsets 0.047808 µm / 0.044767 µm for the two cells. Linear interpolation reduced the worst NRMSE, but did not improve every individual pair. Both probe readouts remain in the raw data.

Full report: [HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md), summary [CSV](amsn-core/results/human_segev_passive_transient_summary_2026-11-21.csv). Next: run the 12-point dt/mesh convergence matrix described in the report.
