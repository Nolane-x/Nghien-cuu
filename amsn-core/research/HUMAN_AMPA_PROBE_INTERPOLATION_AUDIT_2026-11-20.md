# NEURON probe interpolation and AMSN control-volume area audit — 2026-11-20

**Status:** completed and reproducible; interpolation effect is site- and mesh-dependent.  
**NEURON:** 9.0.2  
**Python:** 3.12 GitHub Actions runner  
**Workflow:** [44762715648 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648)  
**Code snapshot:** `7f9de4dff060ac22d6220299860f83faadc30167`  
**Script:** `amsn-core/examples/human_ampa_probe_interpolation_audit.py`  
**Artifact:** [14642920467](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648/artifacts/14642920467)

## Question

The previous spatial/temporal audits left an approximately 0.0037–0.0039 mV RMS q90 discrepancy between AMSN and NEURON. The SWC-protected AMSN voltage is recorded at the exact SWC node, while the NEURON reference had been sampled at the nearest 0.5-um segment centre.

This experiment asks how much the reported discrepancy changes when NEURON voltage is linearly interpolated between the two segment-centre voltages bracketing the exact SWC arc coordinate. It also records local segment-area and AMSN control-volume area values to prepare a separate equal-support area audit.

## Fixed setup

- Morphology: NeuroMorpho NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`, partial human temporal cortex reconstruction, moderate dendritic completeness, metadata indicates mesiotemporal sclerosis, no axon; preserve CC BY 4.0 attribution.
- NEURON 9.0.2, max segment length 0.5 um (25,233 segments).
- dt=0.0015625 ms; duration 5 ms.
- NEURON point process remains attached to the nearest segment for basal q75 SWC 3784. Interpolation is a readout-only diagnostic: it does not move the synapse or alter the NEURON dynamics.
- Probes: basal q75 source 3784, soma 1, basal q90 3814.
- AMPA engineering input: 0.8 nS peak, tau 0.2/2 ms, Erev 0 mV, one deterministic event at 0 ms.
- Passive parameters remain the same as earlier audits: Ri 0.7 ohm*m, Rm 1 ohm*m^2, Cm 0.01 F/m^2, Eleak -65 mV.
- AMSN meshes: 2,000, 4,000 and 6,000 Hz; source/probe SWC nodes protected.

### NEURON arc locations

| Site | SWC ID | NEURON section | Target x | Nearest-centre offset | Left-centre x | Right-centre x | Interpolation weight |
|---|---:|---|---:|---:|---:|---:|---:|
| basal q75 source | 3784 | dend[54] | 0.61933082 | 0.079655 um | 0.61904762 | 0.61944444 | 0.159465 |
| soma | 1 | soma[0] | 0.50000000 | 0 um | 0.5 | 0.5 | 0 |
| basal q90 | 3814 | dend[54] | 0.81625480 | 0.242787 um | 0.81587302 | 0.81626984 | 0.486048 |

The interpolation is a linear estimate between two nearby segment-centre voltages. It is a diagnostic estimate of voltage at the SWC arc coordinate, not an exact analytical solution of the continuous cable equation.

## Voltage-readout results

The table compares the same AMSN trace against (a) NEURON's nearest-segment-centre voltage and (b) the linearly interpolated NEURON voltage at the SWC arc coordinate.

### Basal q90 probe

| AMSN mesh | Nearest-centre RMS error (mV) | Interpolated RMS error (mV) | Nearest max abs (mV) | Interpolated max abs (mV) | Interpolated readout shift RMS (mV) |
|---:|---:|---:|---:|---:|---:|
| 2,000 Hz | 0.003851 | 0.003448 | 0.006475 | 0.004613 | 0.003269 |
| 4,000 Hz | 0.003699 | 0.003646 | 0.005573 | 0.005151 | 0.003269 |
| 6,000 Hz | 0.003670 | 0.003736 | 0.005312 | 0.005409 | 0.003269 |

At q90, interpolation improves the cross-engine RMS by about 10.5% at 2,000 Hz and 1.4% at 4,000 Hz, but makes it about 1.8% worse at 6,000 Hz. The interpolated-versus-nearest NEURON readout changes by a fixed 0.003269 mV RMS at this site; whether that makes AMSN look closer depends on the sign and time structure of the pre-existing residual.

At 0.25 ms, q90 interpolated cross-engine errors are:
- 2,000 Hz: +0.001297 mV;
- 4,000 Hz: +0.002116 mV;
- 6,000 Hz: +0.002332 mV.

For comparison, the earlier nearest-centre q90 errors at 0.25 ms were negative (-0.006073, -0.005254, -0.005038 mV respectively). Interpolation changes the sign at this sample and substantially changes the comparison; this is evidence that readout location matters, not proof that linear interpolation is ground truth.

### Basal q75 source

| AMSN mesh | Nearest-centre RMS error (mV) | Interpolated RMS error (mV) | Nearest max abs (mV) | Interpolated max abs (mV) | Interpolated readout shift RMS (mV) |
|---:|---:|---:|---:|---:|---:|
| 2,000 Hz | 0.003304 | 0.003696 | 0.004347 | 0.005253 | 0.001559 |
| 4,000 Hz | 0.003328 | 0.003872 | 0.004438 | 0.005800 | 0.001559 |
| 6,000 Hz | 0.003353 | 0.003941 | 0.004493 | 0.005980 | 0.001559 |

Unlike q90, interpolation consistently worsens the source comparison. This matters because the event itself remains applied to the nearest NEURON segment; the diagnostic does not relocate the synapse to the SWC point. Thus the source readout, point-process placement and exact SWC point are three related but distinct locations.

### Soma

The soma mapping lands exactly at the segment centre x=0.5, so interpolation weight is zero. The nearest and interpolated voltage traces are identical. The very small soma RMS discrepancy is unchanged (roughly 0.0000347–0.0000412 mV across the three AMSN meshes).

## Area measurements: interpretation warning

The script records:
- NEURON's area for the nearest 0.5-um segment;
- a linear interpolation of the adjacent NEURON segment areas at the SWC x-coordinate;
- AMSN's lumped local control-volume area at the protected node.

The resulting ratios are large (approximately 5.9–10.0 on the dendritic sites and over 40 at the soma), but these areas are **not yet like-for-like**:

- The NEURON values describe one short segment's membrane area (or an interpolation between two segment-sized area values).
- AMSN's node area is constructed from the proximal and distal half-area contributions of all incident electrical edges; the soma root also includes the soma surface term and connected branch contributions.
- Therefore, comparing one NEURON segment area directly with the entire AMSN node control-volume area does not establish that AMSN area is too large. The supports differ substantially.

For example, at 2,000 Hz:
- q90 nearest NEURON segment area = 0.721861 um²;
- q90 interpolated single-segment area = 0.721861 um²;
- AMSN q90 control-volume area = 6.924175 um².
- soma NEURON centre-segment area = 26.338832 um² while AMSN root control volume = 1,152.774341 um², because the AMSN root volume aggregates the modeled soma area and proximal contributions from connected branches; NEURON's one central segment is only a slice of the imported soma section.

This diagnostic flags an important support-definition issue; it is not an area-conservation failure.

## CI and raw output

- Workflow [44762715648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648), 1/1 job success.
- Python 3.12, NEURON 9.0.2.
- Raw artifact [14642920467](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648/artifacts/14642920467).
- Durable raw traces (9,603 rows each, 28,809 total):
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_2000Hz.csv`
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_4000Hz.csv`
  - `amsn-core/results/human_ampa_probe_interpolation_2026-11-20_6000Hz.csv`

## Interpretation

1. NEURON nearest-centre sampling contributes materially to the q90 comparison, because interpolation changes q90 readout by 0.003269 mV RMS.
2. The effect is not uniform. It improves q90 at 2k/4k but slightly worsens at 6k; it worsens q75 source for all tested meshes.
3. Linear interpolation is diagnostic, not truth. The synaptic point process remains at the nearest NEURON segment; therefore source dynamics still reflect that placement.
4. The area values currently compare different control-volume supports. No conclusion about incorrect AMSN membrane area can be drawn from the large ratios.
5. The residual cross-engine discrepancy is not explained by a single universal point-sampling correction.

## Next experiment — equal-support control-volume area

1. From the AMSN sectioned tree, identify the parent edge and child edges incident to each protected point. The local area support is the sum of the proximal/distal half-edge surfaces assigned to that node.
2. For q75 and q90, translate those half-edge arc lengths to a matching interval on the same NEURON section around the exact Import3D SWC arc coordinate.
3. Integrate NEURON's 0.5-um segment areas by their overlap fractions with that same support interval, rather than using a single segment's area.
4. Compare this matched-support NEURON area with AMSN's node area and report edge-by-edge geometry contributions.
5. At the soma, treat the soma surface term and each branch proximal half separately; do not compare the whole AMSN root volume with the central NEURON soma segment.
6. Only if the matched-support area differs materially should a conservative area-allocation change be proposed.

Do not move synapses, alter reversal/time constants or tune parameters to force voltage agreement. First isolate location readout and area support.

---

## Follow-up: equal-support membrane-area audit completed

The previously listed next experiment has now been implemented in `amsn-core/examples/human_ampa_matched_support_area_audit.py` and passed in [workflow 44763720776](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776).

Instead of comparing one short NEURON segment's area with the whole AMSN node area, the follow-up reconstructs the AMSN support interval from half the incoming and outgoing electrical edges. It then integrates NEURON segment areas by the fractional overlap with that same interval.

| AMSN mesh | Site | NEURON area on matched support (um²) | AMSN node area (um²) | Difference |
|---:|---|---:|---:|---:|
| 2,000 Hz | q75 / 3784 | 8.753409 | 8.756880 | +0.039661% |
| 2,000 Hz | q90 / 3814 | 6.924175 | 6.924175 | -0.000001814% |
| 4,000 Hz | q75 / 3784 | 6.531920 | 6.535293 | +0.051636% |
| 4,000 Hz | q90 / 3814 | 5.054776 | 5.054776 | -0.000001814% |
| 6,000 Hz | q75 / 3784 | 5.404350 | 5.407040 | +0.049770% |
| 6,000 Hz | q90 / 3814 | 4.239368 | 4.239368 | -0.000001814% |

This shows the earlier 6–10× area ratios were a support-domain mismatch, not evidence of incorrect AMSN local membrane-area totals. The q90 matched-support area agrees essentially exactly; q75 differs by about 0.04–0.05%.

Full method, geometry intervals, limits and raw data are in:
- `amsn-core/research/HUMAN_AMPA_MATCHED_SUPPORT_AREA_AUDIT_2026-11-20.md`
- `amsn-core/results/human_ampa_matched_support_area_2026-11-20.csv`

The interpolation conclusion remains site-dependent: interpolating the NEURON readout reduces q90 mismatch at 2k/4k but not at 6k, while q75 source mismatch worsens. It is a diagnostic readout, not a global correction.
