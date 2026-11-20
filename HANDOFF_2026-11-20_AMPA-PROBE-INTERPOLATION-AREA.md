# Handoff — AMSN probe interpolation and matched-support area (2026-11-20)

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Probe interpolation workflow:** [44762715648 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648)  
**Matched-support area workflow:** [44763720776 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776)  
**Interpolation report:** `amsn-core/research/HUMAN_AMPA_PROBE_INTERPOLATION_AUDIT_2026-11-20.md`  
**Matched-area report:** `amsn-core/research/HUMAN_AMPA_MATCHED_SUPPORT_AREA_AUDIT_2026-11-20.md`  
**Full research log:** `research/RESEARCH_LOG_2026-11-20_SINGLE-COMPARTMENT-AND-AMPA-MESH.md`

## Read first

1. `AGENTS.md`, `HANDOFF.md`, `research/AMSN_RESEARCH_DOSSIER.md`.
2. `HANDOFF_2026-11-20_AMPA-SPATIAL-FLOOR.md` for the fixed temporal/spatial baseline.
3. The two reports above and the latest appended sections of the research log.
4. Check current main head and current CI before making changes.

## Current verified baseline

### Single-compartment equivalence
- NEURON 9.0.2 vs AMSN one compartment.
- Identical NEURON-reported area, passive parameters and one Exp2Syn event.
- Dedicated audit [44757208267](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267) passed on Python 3.12 and 3.13.
- Voltage difference is at machine precision for the exact controlled protocol.

### Fast-AMPA temporal/spatial baseline
- Morphology: NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`, partial human temporal cortex pyramidal neuron, no axon, moderate dendritic completeness, metadata indicates mesiotemporal sclerosis; keep CC BY 4.0.
- Source q75 SWC 3784, distal basal q90 SWC 3814, soma 1.
- Passive defaults: Ri 0.7 ohm*m; Rm 1.0 ohm*m^2; Cm 0.01 F/m^2; Eleak -65 mV.
- AMPA-like engineering event: peak 0.8 nS; tau 0.2/2 ms; Erev 0 mV; one deterministic event at 0 ms.
- NEURON 9.0.2 fixed 0.5-um max segment mesh, 25,233 segments.
- Timestep for finest audits: 0.0015625 ms.
- AMSN mesh candidate range: 2k/4k/6k Hz; 2k=2,541 compartments, 4k=3,526, 6k=4,287.
- Temporal audit shows q90 cross-engine RMS roughly 0.00380–0.00385 mV over dt 0.025 to 0.0015625 ms; self-convergence falls strongly, so residual is not dominated by tested temporal range.

### Probe interpolation results

Workflow [44762715648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648), 1/1 job success. NEURON readout is compared at the nearest segment centre and by linear interpolation between the two adjacent segment-centre voltages to the exact SWC arc coordinate. The point process remains on the nearest segment; interpolation changes readout only.

| AMSN mesh | q90 nearest RMS (mV) | q90 interpolated RMS (mV) | q75 nearest RMS (mV) | q75 interpolated RMS (mV) |
|---:|---:|---:|---:|---:|
| 2k | 0.003851 | 0.003448 | 0.003304 | 0.003696 |
| 4k | 0.003699 | 0.003646 | 0.003328 | 0.003872 |
| 6k | 0.003670 | 0.003736 | 0.003353 | 0.003941 |

Interpolation shifts NEURON q90 readout by 0.003269 mV RMS and q75 by 0.001559 mV RMS. The effect is site- and mesh-dependent: it helps q90 at 2k/4k but not 6k, and worsens the q75 source comparison for all tested meshes. Linear interpolation is a diagnostic estimate, not continuous-cable truth.

Raw data:
- `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_2000Hz.csv`
- `..._4000Hz.csv`
- `..._6000Hz.csv`
- artifact [14642920467](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648/artifacts/14642920467).

### Matched-support area results

Workflow [44763720776](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776), 1/1 job success.

For q75/q90, the AMSN node's area support is defined from half the incoming and half the outgoing electrical edge. NEURON segment areas are integrated by fractional overlap across the same section-arc interval.

| AMSN mesh | Site | NEURON area same support (um²) | AMSN node area (um²) | Difference |
|---:|---|---:|---:|---:|
| 2k | q75 | 8.753409 | 8.756880 | +0.039661% |
| 2k | q90 | 6.924175 | 6.924175 | -0.000001814% |
| 4k | q75 | 6.531920 | 6.535293 | +0.051636% |
| 4k | q90 | 5.054776 | 5.054776 | -0.000001814% |
| 6k | q75 | 5.404350 | 5.407040 | +0.049770% |
| 6k | q90 | 4.239368 | 4.239368 | -0.000001814% |

This strongly indicates that gross local membrane-area allocation is not responsible for the remaining q90 voltage residual at these two sites. Previous apparent 6–10x area ratios were due to comparing one short NEURON segment's area with a full AMSN node-centred control volume, i.e. different supports.

Raw summary: `amsn-core/results/human_ampa_matched_support_area_2026-11-20.csv`; artifact [14642971232](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776/artifacts/14642971232).

## Important distinctions

- The area matched-support audit only covers two unbranched basal points in one section, not the soma or branchpoints.
- It integrates NEURON segment area proportional to overlap, which is a fine numerical approximation, not an exact analytical continuous surface integral.
- The NEURON point process is still at the nearest segment; readout interpolation does not relocate the synapse.
- One morphology, one synaptic event, generic passive settings. No experimental EPSP trace fitted; no biological validation.
- No universal error tolerance has been declared.

## Next concrete experiment: axial-resistance support audit

The local membrane area now matches closely over equal support. Next isolate axial geometry:

1. For the same q75/q90 incoming and outgoing edge halves, calculate AMSN's exact edge axial geometry factor (int ds/(pi r(s)^2)) from `SectionedCableResult.edge_axial_geometry_factor_m_inv`.
2. Compute the equivalent NEURON axial geometry/resistance over the same section intervals using its section diameter profile and segment/pt3d geometry. Keep Ri unchanged.
3. Report each incoming/outgoing half separately and compare the total support-path integral; do not compare a whole node's area against a single segment again.
4. Verify the NEURON implementation of axial resistance being used (segment centres and half-segment contributions) before asserting equivalence. Preserve units: geometry factor m^-1; multiply by Ri (ohm*m) to obtain ohms.
5. Only if a real discrepancy is observed should a solver or geometry change be proposed.

After that, repeat at another basal branch and an apical path before selecting a global mesh policy. Do not tune Ri or AMPA kinetics to force voltage agreement.
