# AMSN full-tree axial network and topology audit

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Code commit:** [e65a347ef1c51bb44ecbc1deca35c8a4d5712a90](https://github.com/Nolane-x/Nghien-cuu/commit/e65a347ef1c51bb44ecbc1deca35c8a4d5712a90)  
**Workflow:** [44871993854 — successful](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854)  
**Artifact:** [14693349082 — raw CSV bundle](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082)  
**Script:** \`amsn-core/examples/human_full_tree_axial_network_audit.py\`

## 1. Question and hypothesis

The earlier matched-support audit tested five local unbranched sites. This experiment expands the scope to the entire imported morphology:

1. Can every electrically retained SWC edge be matched to its corresponding adjacent NEURON Import3D \`pt3d\` interval?
2. Does NEURON's actual segment-centre \`ri()\` reproduce the axial resistance implied by its own \`pt3d\` diameter profile?
3. Do all parent/child section connections and all SWC branchpoints preserve the expected topology?
4. Are soma-outline and stem-wire connections represented explicitly rather than silently mistaken for ordinary cable edges?

**Hypothesis:** every active SWC edge should map to one unambiguous NEURON \`pt3d\` interval; segment resistances should match the simulator's own geometry integration; section topology should reproduce the SWC child counts at branchpoints. Unmatched or geometrically displaced connections must be reported separately.

This is a numerical geometry and topology audit. It does not fit biological parameters, compare voltage waveforms, or claim biological validation.

## 2. Provenance and morphology

The fixture is NeuroMorpho.Org NMO_290988 / \`1094_Mohan_etal_2015.CNG.swc\`:

- Human temporal neocortex, middle temporal gyrus, Brodmann area 21, layer 2–3.
- 8,903 SWC records: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite.
- 58 non-soma branchpoints and 8 dendritic stems.
- Soma and dendrites only; no axon in this reconstruction.
- Dendritic completeness is marked moderate; source metadata records mesiotemporal sclerosis; shrinkage correction is not reported.
- Source distribution is CC BY 4.0. Required attribution and exact source metadata are retained in \`amsn-core/data/human/README.md\` and \`1094_Mohan_etal_2015.provenance.json\`.

This is one partial morphology, not a representative healthy human neuron or a population sample.

## 3. Environment and model configuration

| Item | Value |
|---|---|
| CI runner | Ubuntu 26.04.1 |
| Python | CPython 3.12.16 |
| NumPy | 2.5.5 |
| NEURON | 9.0.2 |
| NEURON sections | 125 |
| NEURON segments | 25,233 |
| NEURON maximum segment length | 0.5 µm |
| Axial resistivity | 0.7 Ω·m |
| SWC nodes | 8,903 |
| SWC branchpoints | 58 |

The audit uses the repository's established headless NEURON Import3D loader and exact human SWC fixture. NEURON's segment discretization is capped at 0.5 µm; \`Ra\` is set to 70 Ω·cm (=0.7 Ω·m).

Run commands from \`amsn-core/\`:

\`\`\`bash
python -m pip install -e ".[test]"
python -m pip install --only-binary=neuron "neuron==9.0.2"
python examples/human_full_tree_axial_network_audit.py
\`\`\`

## 4. Geometry equations and matching procedure

For a circular cable with linearly varying diameter from \(d_0\) to \(d_1\), the axial geometry factor is

\[
G = \int \frac{ds}{\pi r(s)^2}
  = \frac{4L}{\pi d_0d_1}.
\]

The integral is evaluated in SI units and reported in m⁻¹. The corresponding axial resistance is \(R=R_iG\), with \(R_i=0.7\;\Omega\,m\).

For each SWC parent-child edge not collapsed by AMSN's NeuroMorpho soma policy:

1. Map both SWC nodes through NEURON Import3D's \`id2pt\` and \`point2sec\` index rather than a nearest-in-3D guess.
2. Find an adjacent pair of NEURON \`pt3d\` points that matches the SWC endpoints and diameters.
3. Integrate the source SWC taper and the mapped NEURON taper independently.
4. Record the mapping offsets, the two diameters, the two path lengths, and the axial-factor difference.
5. Reject and count any active SWC edge with no unambiguous adjacent \`pt3d\` interval.

Separately, for every NEURON segment:
- Compare actual \`segment.ri()\` between adjacent segment centres with the \`pt3d\` integral over the same interval.
- For the first segment of every child section, compare its \`ri()\` with the child-side half-interval from the child section's connection orientation to its first segment centre.
- At ordinary parent-endpoint section connections, compare the parent-side \`h.ri(parent_connection)\` with the parent-side half-interval.
- Keep the soma wire-attachment convention separate because those sections connect at the soma centre rather than at a normal parent-section endpoint.

At each SWC branchpoint, count NEURON child sections whose parent connection maps to that branchpoint. Do not infer branchpoint correctness from cable geometry alone.

## 5. Full-tree edge coverage and axial geometry

<badge color="success">8,892 / 8,892 active edges mapped</badge>

There are 8,903 SWC records and 8,892 active cable edges after excluding 10 soma-outline / wire-attachment edges collapsed by the existing NeuroMorpho soma normalization policy. All 8,892 active edges matched one adjacent NEURON \`pt3d\` interval; zero active edges were unmapped.

### Absolute axial geometry-factor difference

The difference is \(|G_{SWC}-G_{NEURON}|/G_{NEURON}\times100\%\).

| Statistic | Difference |
|---|---:|
| Median | 0.000163823% |
| Mean | 0.000446514% |
| 90th percentile | 0.001245677% |
| 95th percentile | 0.002034756% |
| 99th percentile | 0.003617250% |
| 99.9th percentile | 0.006019737% |
| Maximum | 0.015288401% |

### By dendritic class

| SWC child type | Edges | Median absolute difference | 95th percentile | Maximum |
|---|---:|---:|---:|---:|
| Basal dendrite (3) | 4,044 | 0.000096135% | 0.000522880% | 0.002227986% |
| Apical dendrite (4) | 4,848 | 0.000316721% | 0.002609395% | 0.015288401% |

### Dependence on source edge length

| Source SWC edge length | Edges | 95th percentile | Maximum |
|---|---:|---:|---:|
| \(0<L\le0.25\) µm | 22 | 0.005296595% | 0.015288401% |
| \(0.25<L\le0.5\) µm | 84 | 0.003771776% | 0.009013102% |
| \(0.5<L\le1\) µm | 1,693 | 0.002775290% | 0.006940361% |
| \(1<L\le2\) µm | 6,035 | 0.001981736% | 0.004982922% |
| \(2<L\le5\) µm | 1,056 | 0.001128368% | 0.002528304% |
| \(5<L\le10\) µm | 2 | 0.000035189% | 0.000035189% |

The largest discrepancy is on SWC edge 5560→5842, an apical edge of length 0.156525 µm. Its endpoint coordinate offsets in the mapped \`pt3d\` record are approximately 0.0000293 µm and 0.0000075 µm; endpoint diameter differences are approximately \(9.5\times10^{-9}\) µm. The short physical length makes small coordinate-rounding differences more visible in a *relative* resistance comparison.

**Interpretation:** the observed residual is consistent with the finite precision of NEURON's \`pt3d\` geometry representation, which stores point coordinates and diameters as 32-bit floats. This is a plausible explanation, not a separately proven causal attribution. The result must not be converted into a universal error tolerance. See the [NEURON geometry documentation](https://www.neuronsimulator.org/en/latest/progref/modelspec/programmatic/topology/geometry.html) and the [NEURON 9.0.2 geometry/resistance implementation](https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/treeset.cpp).

## 6. NEURON's own \`ri()\` consistency

<badge color="success">25,233 / 25,233 finite records checked</badge>

| Connection class | Count | Maximum relative difference vs \`pt3d\` integral |
|---|---:|---:|
| Within-section segment-centre connections | 25,108 | \(2.2788054\times10^{-11}\%\) |
| Child-section first-segment half intervals | 124 | \(7.3003891\times10^{-14}\%\) |
| Parent endpoint half intervals | 116 | \(1.1385008\times10^{-11}\%\) |

All 25,233 rows were checked; none reported an unexpected infinite \`ri()\`. The single root-section start is not a parent-child connection. The eight soma-centre wire attachments have no ordinary parent-endpoint half-interval, so they are excluded from the count of 116 parent endpoint checks; they remain present in the section-connection report.

**Locally reproduced result:** for the selected NEURON 9.0.2 fixed-step segmentation and this morphology, actual NEURON axial resistances reproduce its own \`pt3d\` taper integrals to near machine precision. This does not validate every solver equation or prove that the imported morphology is biologically exact.

## 7. Branchpoint and section-connection topology

<badge color="success">58 / 58 branchpoints have exact child counts</badge>

- All 58 non-soma SWC branchpoints have the same number of NEURON child sections connected at the corresponding parent-section location.
- The largest branchpoint-to-\`pt3d\` location discrepancy is approximately 0.00002935 µm, consistent with the small coordinate offsets seen in the edge mapping.
- There are 124 NEURON section connections in total.
- 116 ordinary section-endpoint connections have zero measured endpoint coordinate gap and have both parent-side and child-side half-resistance contributions checked.
- 8 soma wire attachments connect to \`soma[0](0.5)\` with child orientation 0. Their child \`pt3d\` origins are 7.631–10.537 µm from the soma-centre connection coordinate.

### Important soma-wire distinction

The eight soma attachments are an explicit representation convention in the current import policy: their stem nodes are mapped to the soma electrical vertex, so the connector is not represented as an ordinary active SWC cable edge. This explains why the child section's anatomical \`pt3d\` origin can be several micrometres from the soma-centre connection coordinate while the electrical topology still connects at the soma centre.

This is **not evidence that a biological soma-to-dendrite stem has zero physical resistance**. It identifies a modelling assumption that should be revisited against the original CNG soma convention and the original Eyal model before treating the soma-stem resistance as biologically resolved.

## 8. Overall interpretation

The audit supports three limited conclusions for this one partial morphology and NEURON 9.0.2 configuration:

1. **Edge coverage:** all active SWC edges were matched to an adjacent NEURON \`pt3d\` interval; no active edge was silently dropped.
2. **Reference-solver self-consistency:** NEURON's actual \`ri()\` values agree extremely closely with the corresponding geometry integrals at internal segment connections and the audited parent/child section half-intervals.
3. **Topology:** all 58 SWC branchpoints reproduce their child-section counts; 116 ordinary section connections have coincident endpoints. The eight soma-centre wire attachments are separately identified as an import-policy assumption.

The edge-wise SWC-vs-\`pt3d\` factor difference is small (maximum 0.0153%, 99th percentile 0.00362%) and is largest on very short apical edges. It is consistent with finite \`pt3d\` coordinate precision; it is not evidence of a large axial-resistance error in the AMSN solver.

**Not established:** equality of every entry in the full AMSN and NEURON global cable conductance matrices; correctness of 3-D branch-junction or soma volume physics; passive voltage equivalence across all protocols; active dendritic channel calibration; synaptic biological accuracy; or biological validation. No parameters were tuned in this audit.

## 9. Limitations

- One partial human temporal-cortex morphology; no axon, moderate dendritic completeness and a disease-context metadata field.
- One simulator version (NEURON 9.0.2) and one reference segment cap (0.5 µm).
- The \`pt3d\` representation is the geometry produced by Import3D from the same SWC, not an independent experimental 3-D measurement.
- Branchpoint verification checks section counts and connection locations, not a finite-volume 3-D branch-junction resistance model.
- The eight soma wire attachments remain a representation-policy question; the audit exposes rather than resolves their physical interpretation.
- No experimental voltage traces or synaptic responses were fit.
- No scientifically approved absolute/relative error budget has been established.

## 10. Reproducibility record and files

- Code: \`amsn-core/examples/human_full_tree_axial_network_audit.py\`.
- Workflow: \`.github/workflows/amsn-full-tree-axial-network-audit.yml\`.
- Successful workflow: [44871993854](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854).
- Artifact: [14693349082](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082).
- Code commit: \`e65a347ef1c51bb44ecbc1deca35c8a4d5712a90\`.
- Raw artifact CSVs:
  - \`human_full_tree_axial_edges_2026-11-21.csv\` — 8,892 active edges.
  - \`human_neuron_ri_connections_2026-11-21.csv\` — 25,233 NEURON segment rows.
  - \`human_branchpoint_connection_audit_2026-11-21.csv\` — 58 branchpoints.
  - \`human_neuron_section_connections_2026-11-21.csv\` — 124 section connections.

The dedicated audit workflow completed successfully. Comprehensive AMSN Core CI for code commit \`e65a347ef1c51bb44ecbc1deca35c8a4d5712a90\` is tracked at [44871993797](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993797); record its final conclusion after completion.
