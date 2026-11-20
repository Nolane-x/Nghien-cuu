# Handoff — AMSN AMPA spatial-floor and next mapping audit (2026-11-20)

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Spatial sweep code:** `4f53fa23834ac3a1865f14a963d6b77f63b04f6c`  
**Spatial sweep workflow:** [44761379734 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734)  
**Report:** `amsn-core/research/HUMAN_AMPA_SPATIAL_FLOOR_2026-11-20.md`  
**Temporal checkpoint:** `HANDOFF_2026-11-20_AMPA-TEMPORAL-CONVERGENCE.md`  
**Temporal workflow:** [44760319787 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787)

## Start here

1. Read `AGENTS.md`, `HANDOFF.md`, `research/AMSN_RESEARCH_DOSSIER.md`.
2. Read `HANDOFF_2026-11-20_AMPA-TEMPORAL-CONVERGENCE.md`.
3. Read `amsn-core/research/HUMAN_AMPA_SPATIAL_FLOOR_2026-11-20.md`.
4. Check current main head and latest Core CI before editing.
5. Treat the raw CSVs under `amsn-core/results/` as the durable numerical record; preserve all prior runs and negative results.

## Current verified numerical foundation

### Single-compartment
The dedicated single-compartment audit passed for Python 3.12 and 3.13 against NEURON 9.0.2 at dt 0.025, 0.0125 and 0.00625 ms. It matched a single NEURON segment's reported area, passive parameters and one Exp2Syn event. Voltage discrepancy was at machine-scale in this exact controlled test.

### Spatial reference refinement
On the NMO_290988 partial human morphology, AMSN at 2,000 Hz (2,541 compartments) versus NEURON 0.5 um (25,233 segments) achieved q90 RMS mismatch 0.003840 mV at dt 0.00625 ms. The NEURON q90 segment-centre mapping offset was 0.242787 um.

### Temporal convergence
With spatial meshes fixed and dt = 0.025, 0.0125, 0.00625, 0.003125, 0.0015625 ms:
- NEURON and AMSN self-convergence errors fall monotonically.
- q90 cross-engine RMS remains nearly flat, about 0.003798–0.003851 mV.
- q90 maximum absolute error remains about 0.006266–0.006475 mV.
This says the residual is not dominated by the tested temporal range.

### Spatial-floor sweep at finest dt
At dt = 0.0015625 ms, with NEURON fixed at 0.5 um and AMSN mesh frequency varied:

| AMSN frequency | Compartments | q90 RMS cross-engine error | q90 max abs error | q90 RMS vs AMSN 6,000-Hz mesh |
|---:|---:|---:|---:|---:|
| 2,000 Hz | 2,541 | 0.003851 mV | 0.006475 mV | 0.000540 mV |
| 3,000 Hz | 3,077 | 0.003752 mV | 0.005884 mV | 0.000267 mV |
| 4,000 Hz | 3,526 | 0.003699 mV | 0.005573 mV | 0.000143 mV |
| 6,000 Hz | 4,287 | 0.003670 mV | 0.005312 mV | 0 mV |

Increasing AMSN frequency 2,000→6,000 Hz increases compartments by 68.7%, reduces q90 RMS cross-engine error by only about 4.7%, and reduces max absolute error by about 18%. AMSN self-convergence differences are smaller than the remaining NEURON-versus-AMSN mismatch.

The trend is not uniformly better at every site:
- q90 improves as mesh frequency rises;
- source q75 RMS discrepancy rises slightly from 0.003304 to 0.003353 mV;
- soma RMS discrepancy rises slightly from 0.00003472 to 0.00004117 mV (still a very small absolute difference).

Do not select 6,000 Hz as a universal default. The result demonstrates diminishing returns and a site-dependent tradeoff.

## Exact experiment/provenance

- Morphology: NeuroMorpho NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`; partial human temporal cortex cell, moderate dendritic completeness, metadata indicates mesiotemporal sclerosis, no axon. Preserve CC BY 4.0.
- Source: basal q75 SWC 3784.
- Probes: 3784, soma 1, basal q90 3814.
- NEURON mapping offsets: source 0.079655 um, soma 0 um, q90 0.242787 um.
- NEURON: 9.0.2, 0.5-um max segment, 25,233 segments.
- dt: 0.0015625 ms, duration 5 ms.
- AMPA-like engineering event: 0.8 nS, tau 0.2/2 ms, Erev 0 mV, one NetStim event at 0 ms, noise 0.
- Passive defaults: Ri 0.7 ohm*m, Rm 1 ohm*m^2, Cm 0.01 F/m^2, Eleak -65 mV.
- AMSN electrotonic edge cap 0.1, physical cap 100 um, three sites protected.

These are engineering/numerical test parameters, not patient-specific or universal human values.

## Durable raw data

Four CSV files, each with 9,603 rows (three recording sites × 3,201 time points):

- `amsn-core/results/human_ampa_spatial_floor_2026-11-20_2000Hz.csv`
- `amsn-core/results/human_ampa_spatial_floor_2026-11-20_3000Hz.csv`
- `amsn-core/results/human_ampa_spatial_floor_2026-11-20_4000Hz.csv`
- `amsn-core/results/human_ampa_spatial_floor_2026-11-20_6000Hz.csv`

Report: `amsn-core/research/HUMAN_AMPA_SPATIAL_FLOOR_2026-11-20.md`.  
CI artifact: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734/artifacts/14640889259.

The earlier temporal raw data remains in `amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv` (18,615 rows).

## Scientific limitations

- One partial morphology, one basal synapse, three sites; no external experimental EPSP fitted.
- Passive membrane, prescribed AMPA conductance only; no active channels, NMDA Mg2+ block, spine neck, Ca2+, plasticity, gene/protein or metabolism.
- NEURON 0.5 um is the finest tested reference, not analytical truth or experimental truth.
- AMSN 6,000-Hz mesh is the finest tested mesh, not guaranteed converged.
- Mesh frequency trends are site-dependent.
- No numerical acceptance threshold has been established.
- Do not describe this as a complete human neuron or biological validation.

## Next task — location interpolation and control-volume area audit

Do not immediately raise the global mesh to 8k/12k/20k. Investigate the residual discrepancy with targeted measurements:

1. For basal q75 (SWC 3784) and q90 (SWC 3814), obtain NEURON voltage at the nearest segment centre and linearly interpolate between the two adjacent segment-centre voltages to the exact Import3D arc coordinate of the SWC node. Keep NEURON mesh, dt, event and synapse placement unchanged.
2. Compare the interpolated NEURON voltage with AMSN's exact protected-SWC control-point voltage at 2k/4k/6k. Determine whether point-sampling offset accounts for the remaining q90 mismatch.
3. Audit the proximal/distal half-area assignment around each protected AMSN control point. Report total area, per-control-volume area, path-arc integrals and axial conductance before considering a code change.
4. If area lumping or site interpolation explains the residual, design a local conservative refinement that does not increase compartments across the whole cell.
5. Repeat the test on another basal and one apical branch before selecting any default mesh policy.

Do not change production solver semantics or tune biophysical parameters solely to improve this comparison. First identify which discretization term causes the residual.
