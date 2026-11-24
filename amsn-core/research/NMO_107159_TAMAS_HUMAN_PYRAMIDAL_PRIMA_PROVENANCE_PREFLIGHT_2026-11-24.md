# NMO_107159 Tamas human pyramidal comparison cell — provenance and preflight

**Date:** 24 November 2026  
**NeuroMorpho ID:** NMO_107159  
**PR:** [#17](https://github.com/Nolane-x/Nghien-cuu/pull/17)

## Purpose

Add a fourth independent morphology to the passive PRIMA matched 7-port/9-port × morphology validation. This record is a human frontal neocortical pyramidal comparison cell with dendrites and axon marked complete and explicit 3D diameter metadata. It provides a diameter-recorded comparison alongside the Peng complete-axon record whose metadata says No Diameter.

## NeuroMorpho provenance

- NeuroMorpho.Org ID: NMO_107159
- Cell: `Fig5c_141009_2og_B`
- Archive: Tamas
- Species: human
- Gender: female
- Age: not reported
- Region: neocortex, frontal, layer 1 and layer 2–3
- Cell class: principal cell, pyramidal
- Experimental condition: Control
- Protocol: in vitro
- Stain: biocytin
- Slicing direction: perpendicular to cortical layers
- Slice thickness: 70 µm
- Reconstruction software: Neurolucida
- Objective: oil, 100×
- Structural domain: Dendrites, Soma, Axon
- Physical integrity: Dendrites & Axon Complete
- Morphological attributes: Diameter, 3D, Angles
- Original format: Neurolucida.dat
- Published source DOI: 10.1038/s41593-018-0205-2
- PMID: 30150662

Official sources:
- [NeuroMorpho detail page](https://neuromorpho.org/neuron_info.jsp?neuron_name=Fig5c_141009_2og_B)
- [NeuroMorpho API record](https://neuromorpho.org/api/neuron/id/107159)
- [Morphometry](https://neuromorpho.org/api/morphometry/id/107159)
- [Standardized SWC](https://neuromorpho.org/dableFiles/tamas/CNG%20version/Fig5c_141009_2og_B.CNG.swc)
- [Published article](https://doi.org/10.1038/s41593-018-0205-2)
- [bioRxiv version](https://www.biorxiv.org/content/10.1101/216085v1.full-text)

### Correct cell identity in the source article

The source article is about a specialized human cortical GABAergic rosehip cell type. Its Figure 5C nevertheless explicitly shows a pyramidal comparison cell in connection with a rosehip cell. The NeuroMorpho cell name `Fig5c_141009_2og_B` and record class `principal cell, pyramidal` identify this reconstruction as the **pyramidal comparison cell**, not as a rosehip interneuron. Preserve this distinction in all reports and citations.


Official NeuroMorpho morphometry (API `/api/morphometry/id/107159`): total length 12,320.7 µm; mean diameter 0.285193 µm; 61 bifurcations; 126 branches; 4 stems; max path distance 1,662.83 µm; max Euclidean distance 1,420.16 µm; width 777.889 µm, height 1,595.1 µm, depth 91.47 µm; surface 9,693.02 µm²; volume 1,624.96 µm³. These are repository morphometry measurements/derived descriptors; passive membrane and axial parameters remain separate model assumptions.

## Pinned repository source

Repository path:
`amsn-core/data/human/neuromorpho_tamas/NMO_107159_Fig5c_141009_2og_B.CNG.swc`

SHA-256:
`6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`

The file contains the original standardized SWC's numeric seven-column records unchanged; upstream comments are replaced with a provenance/attribution header.

Independent topology scan:
- 7,228 SWC records
- Soma: 3
- Axon: 4,030
- Basal dendrite: 1,767
- Apical dendrite: 1,428
- One soma root
- All 7,228 nodes reachable from root
- No duplicate IDs
- No missing parent references
- Three-point soma convention preserved

## Path-distance quantiles and candidate ports

The quantile helper uses root-to-node Euclidean path distance and deterministic rank selection.

Seven canonical ports:
- Soma: 1
- Basal q50/q75/q90: 5564 / 6363 / 7023
- Apical q50/q75/q90: 4301 / 4735 / 4623

Two q25-only probes:
- Basal q25: 6609
- Apical q25: 4404

The preflight pins the canonical seven and recomputes q25 with the same helper used by the replay. Replay reads the two q25 IDs from `preflight.json` and fails closed if its own mapping differs.

## Matched 7-port / 9-port experiment

- Port counts: 7 and 9, preserving exactly the same seven shared SWC node identities.
- Basis orders: 112 and 168.
- Six extended10kHz expansion shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Nine deterministic passive Rm/Cm/Ra scenarios.
- Nine AC frequencies: 0.1 Hz through 10 kHz.
- Three current sources: soma, basal-q75 and apical-q75.
- Two square-pulse widths: 2 ms and 10 ms; 10 pA; onset 2 ms; total duration 20 ms; dt 0.1 ms.
- Full-Hines references are computed for both layouts and checked at all seven common outputs.
- Same 0.5 µm NEURON segment cap as the Peng complete-axon holdout; the two earlier human holdouts used 0.125 µm.

Expected coverage: 36 models, 324 AC rows, 1,728 transient-port rows, 756 matched shared-output pairs, 216 q25 observations and 378 shared-Hines checks.

## Scientific limits

This is one human pyramidal reconstruction, not a representative population. The record has measured-diameter attributes (Diameter, 3D, Angles), but the passive membrane parameters, conductance assumptions and reference discretization still affect absolute numerical errors. The source article concerns rosehip cells; this specific reconstruction is a pyramidal comparison cell, not a rosehip interneuron.

The experiment is passive linear-RC reduction against full Hines only. It does not validate active channels, action potentials, nonlinear synapses, plasticity or biological physiology. Full Hines remains canonical; no production defaults change.

## Data attribution

NeuroMorpho.Org data are supplied under CC BY 4.0. Use requires attribution to:
1. The original article: DOI 10.1038/s41593-018-0205-2.
2. NeuroMorpho.Org (RRID:SCR_002145).
3. Tecuatl C, Ljungquist B, Ascoli GA (2024), “Accelerating the continuous community sharing of digital neuromorphology data,” FASEB Bioadv. 6(7):207–221, doi:10.1096/fba.2024-00048.

See [NeuroMorpho terms of use](https://neuromorpho.org/useterm.jsp).

## Validation checkpoint

The GitHub Actions run [45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588) passed the complete AMSN regression suite, Tamas source/metadata tests, source SHA-256 verification, Import3D preflight, matched replay, exact coverage, result commit and artifact upload. Validated numerical results are recorded below.


## Validated matched-port results

**Successful GitHub Actions run:** [45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588)  
**Artifact:** [#14884183988](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588/artifacts/14884183988)  
**Artifact ZIP SHA-256:** \`b01bbce48bc62931c10b78f5a97a8e334f26bd0ea186ede6335a92484b8d3808\`

The full AMSN regression suite, Tamas-specific source/mapping tests, source checksum, Import3D preflight, matched replay, exact coverage, results commit and artifact upload all passed. The workflow completed successfully.

Preflight:
- 7,222 electrical compartments
- 127 NEURON sections
- 24,737 NEURON segments
- Maximum observed segment length 0.49997753 µm under the 0.5 µm cap
- Seven common SWC nodes: [1, 6363, 4735, 5564, 7023, 4301, 4623]
- q25-only nodes: basal 6609, apical 4404

Exact numerical coverage:
- 36 reduced models
- 324 AC frequency rows
- 1,728 transient-port rows
- 756 matched shared-output pairs
- 216 q25-only observations
- 378 shared-Hines checks

All 36 models achieved their requested order and passed Cholesky checks. The 378 shared-Hines reference traces were exactly equal between port layouts: maximum absolute difference 0 V and maximum relative L2 difference 0%.

### Shared-output comparison

| Basis order | 9-port worse / better / tie | Median 9/7 error ratio | Maximum ratio | Maximum absolute 9-port shared NRMSE |
|---:|---:|---:|---:|---:|
| 112 | 378 / 0 / 0 | **42.718×** | 140.029× | 3.9507e−5% |
| 168 | 214 / 164 / 0 | **1.00102×** | 4.373× | 5.4559e−7% |

At order112, adding q25 probes consistently increases error on all seven shared outputs. At order168, the median 9/7 ratio is effectively 1.0, with 164 pairs improved and 214 degraded. Both models are extremely accurate in absolute terms: maximum shared-output NRMSE is below 4.0e−5% at order112 and 5.46e−7% at order168.

### q25-only output accuracy

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 3.0201e−6% | 3.5323e−5% |
| 168 | 108 | 2.4896e−8% | 2.3679e−7% |

Both q25 probes are accurately represented at either order, with substantially lower errors at order168.

### 10 kHz AC residuals and numeric storage

| Port count | Order | Median Z residual | Maximum Z residual | Median Y residual | Maximum Y residual | Numeric storage |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 112 | 7.1967e−7% | 3.2187e−6% | 1.3984e−5% | 1.6948e−5% | 6.3625 MB |
| 9 | 112 | 1.7339e−5% | 6.0449e−5% | 1.8783e−4% | 2.2165e−4% | 6.3625 MB |
| 7 | 168 | 6.8793e−12% | 1.9317e−11% | 5.9280e−10% | 8.6152e−10% | 9.6874 MB |
| 9 | 168 | 2.8131e−9% | 3.2578e−9% | 2.9439e−7% | 3.2752e−7% | 9.6874 MB |

Numeric storage is basis plus reduced G/C matrices; at the same order it is identical for seven and nine ports in this implementation.

### Runtime

- Wall time: 322.00 s
- User CPU: 408.14 s
- System CPU: 0.22 s
- Peak RSS: 144,420 KiB
- Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2

This is a single hosted-run measurement, not a controlled performance benchmark.

## Interpretation across the four morphology holdouts

| Morphology | Context / structural caveat | Order112 median 9/7 ratio | Order168 median 9/7 ratio | Main observation |
|---|---|---:|---:|---|
| NMO_162186 | Human epilepsy surgical specimen; axon incomplete | 8.162× | 0.99999985× | Order168 restored shared-output parity |
| NMO_03524 | Human Jacobs Control; dendrites moderate, axon incomplete | 1.00000465× | 0.99999991× | Near parity at both orders |
| NMO_163775 | Mouse Peng Control; dendrites/axon complete by metadata; No Diameter | 78.051× | 14.501× | Relative penalty persists, but absolute errors remain very small |
| NMO_107159 | Human Tamas Control pyramidal comparison cell; complete arbors and Diameter/3D/Angles | **42.718×** | **1.00102×** | Order168 restores near parity; q25 errors fall to 2.37e−7% maximum |

This fourth holdout adds a diameter-recorded human pyramidal reconstruction with complete arbors. It reinforces the morphology-dependent pattern: order112 can impose a relative penalty when q25 ports are added, while order168 brings the shared outputs near parity on this cell. The absolute nine-port shared error is still very small at order112 (maximum 3.95e−5%).

The Tamas run and Peng run both use a 0.5 µm NEURON segment cap, so those two complete-axon holdouts have a matched reference discretization. The first two human holdouts used 0.125 µm; do not pool their absolute errors or timings with the 0.5 µm runs without mesh harmonization.

This is one human pyramidal comparison reconstruction, not a population sample. The source article concerns rosehip interneurons, but this specific record is the pyramidal comparison cell shown in Fig. 5C, not a rosehip interneuron. The experiment is passive linear-RC validation against full Hines only; it does not establish active-neuron or population-level biology. Full Hines remains canonical and no production defaults change.

Sources: [PR #17](https://github.com/Nolane-x/Nghien-cuu/pull/17), [successful workflow 45314100588](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588), [artifact #14884183988](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45314100588/artifacts/14884183988).
