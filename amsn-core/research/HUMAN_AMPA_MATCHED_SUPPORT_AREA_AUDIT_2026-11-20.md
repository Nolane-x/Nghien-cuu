# Matched-support membrane-area audit — 2026-11-20

**Status:** successful geometry audit on two protected basal control points.  
**NEURON:** 9.0.2, 0.5-um max segment length, 25,233 segments.  
**Python:** 3.12 GitHub Actions runner.  
**Workflow:** [44763720776 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776)  
**Code:** `amsn-core/examples/human_ampa_matched_support_area_audit.py`  
**Raw metrics:** `amsn-core/results/human_ampa_matched_support_area_2026-11-20.csv`  
**Artifact:** [14642971232](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776/artifacts/14642971232)

## Why this audit was needed

The earlier probe interpolation audit compared:
- one NEURON 0.5-um segment's surface area (or a linear interpolation between two individual segment-area values); and
- AMSN's node-centred lumped control-volume area, which aggregates proximal/distal half-area contributions from incident electrical edges.

Those are different support domains. The resulting 6–10x area ratios on dendrites and >40x at the soma were not evidence that AMSN membrane area was wrong; they mainly reflected comparing one tiny NEURON segment to a larger AMSN control volume.

This audit defines an equal physical support for two unbranched basal sites and integrates NEURON segment areas across that interval.

## Method

For a protected unbranched AMSN control point:
- obtain its incoming electrical edge length (L_{in});
- obtain its outgoing electrical edge length (L_{out});
- the node's area support consists of the proximal half of the incoming edge plus the distal half of the outgoing edge;
- map that support to the same NEURON section's Import3D arc coordinate (x);
- integrate NEURON segment area using the fractional overlap of each segment's x interval with the matched support interval;
- compare the resulting area with the AMSN node's lumped `tree.area_m2[index]`.

For each NEURON segment, area was apportioned in proportion to the fraction of its x interval overlapped. At 0.5-um segment length this is a fine-grained numerical integration estimate; it is not an exact analytical integration of the continuous taper.

The audit deliberately requires one incoming and one outgoing edge on the same NEURON section. Branch points and multi-section supports are rejected rather than silently approximated. The two tested basal sites satisfy this constraint in `dend[54]`.

## Results

| AMSN frequency | Site | AMSN compartments | Matched support length (um) | NEURON area over same support (um²) | AMSN control-volume area (um²) | Difference (%) |
|---:|---|---:|---:|---:|---:|---:|
| 2,000 Hz | basal q75 / SWC 3784 | 2,541 | 5.162152 | 8.753409 | 8.756880 | +0.039661 |
| 2,000 Hz | basal q90 / SWC 3814 | 2,541 | 4.791377 | 6.924175 | 6.924175 | -0.000001814 |
| 4,000 Hz | basal q75 / SWC 3784 | 3,526 | 3.825811 | 6.531920 | 6.535293 | +0.051636 |
| 4,000 Hz | basal q90 / SWC 3814 | 3,526 | 3.497794 | 5.054776 | 5.054776 | -0.000001814 |
| 6,000 Hz | basal q75 / SWC 3784 | 4,287 | 3.147962 | 5.404350 | 5.407040 | +0.049770 |
| 6,000 Hz | basal q90 / SWC 3814 | 4,287 | 2.933549 | 4.239368 | 4.239368 | -0.000001814 |

The q90 matched-support area agrees to roughly 1.8×10⁻⁶ percent across all three meshes. The q75 matched-support area differs by about 0.04–0.05 percent. These are extremely small discrepancies for the tested geometry and segment-integration method.

### Exact support geometry

All six cases are in the NEURON `dend[54]` section. The parent/site/child coordinates remain fixed as mesh frequency changes; only the AMSN half-edge extents shrink as the electrical mesh is refined.

| Site | Parent x | Target x | Child x |
|---|---:|---:|---:|
| q75 / 3784 | 0.614951171 | 0.619330824 | 0.631127014 |
| q90 / 3814 | 0.813087764 | 0.816254797 | 0.823111869 |

For q75 at 2,000 Hz, the support uses 2.743878 um on the incoming side plus 2.418274 um on the outgoing side. For q90, it uses 2.348930 + 2.442447 um. NEURON area integration overlaps 11 and 10 segments, respectively.

## Interpretation

1. The very large area ratios previously reported for a single segment versus an AMSN control volume were not a like-for-like comparison.
2. When both simulators are compared over the same support interval, AMSN's lumped membrane area closely matches NEURON's integrated segment areas at q75 and q90.
3. Therefore, a gross membrane-area allocation error is unlikely to explain the remaining approximately 0.0037-mV RMS q90 voltage discrepancy at these protected basal nodes.
4. This does not rule out small area differences elsewhere, branch-junction effects, axial-resistance differences, point-process placement or voltage readout effects.
5. The q75 residual remains different from q90, which is consistent with interpolation tests showing that voltage readout corrections are site-dependent.

## Related voltage interpolation audit

Workflow [44762715648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648) completed successfully and produced three raw CSVs (2k/4k/6k Hz, 9,603 samples each). Linear interpolation between NEURON segment-centre voltages:
- shifted the q90 readout by 0.003269 mV RMS;
- reduced q90 cross-engine RMS from 0.003851 to 0.003448 mV at 2k, and 0.003699 to 0.003646 mV at 4k;
- slightly increased q90 RMS at 6k (0.003670 to 0.003736 mV);
- worsened the q75 source comparison at all three meshes.

The point process remains at the nearest NEURON segment; the interpolation is a readout-only diagnostic, not a correction to synapse placement or a continuous-cable ground truth.

Report: `amsn-core/research/HUMAN_AMPA_PROBE_INTERPOLATION_AUDIT_2026-11-20.md`.

## Limits

- Only two unbranched basal sites were tested for equal-support area.
- Soma root is not included because its support combines the soma surface and multiple branch contributions; it must be audited as separate geometric terms.
- Area integration uses fractional segment overlap; very fine but still a numerical discretization.
- One partial morphology, one passive parameter set, one synaptic event. No biological calibration or experimental waveform fitting.
- NEURON 0.5 um remains a refined numerical reference, not experimental or mathematical truth.

## Next work

The area audit suggests that gross local membrane-area allocation is not the primary residual source at basal q75/q90. The next numerical separation should be:
1. compare axial resistance integrals on the same incoming/outgoing support intervals;
2. inspect voltage differences at the segment centres versus interpolated arc locations at source and q90;
3. repeat at a second basal branch and one apical site;
4. only after those checks consider any local, conservative mesh or solver change.

Do not make the global mesh denser just because more compartments are possible. The 2k→6k sweep increased compartment count by 68.7% for only a 4.7% q90 RMS improvement, while source and soma RMS differences did not improve.
