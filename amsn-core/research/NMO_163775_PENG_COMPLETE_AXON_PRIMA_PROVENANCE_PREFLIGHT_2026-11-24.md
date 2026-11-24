# NMO_163775 Peng complete-axon morphology — provenance and preflight

**Date:** 24 November 2026  
**NeuroMorpho ID:** NMO_163775  
**PR:** [#16](https://github.com/Nolane-x/Nghien-cuu/pull/16)  
**Branch:** `research/prima-peng-complete-axon-third-morphology-2026-11-24`

## Purpose

Add a third morphology to the PRIMA port-count × morphology validation. This record is independently sourced from the Peng archive and is a mouse somatosensory neocortical pyramidal IT projection cell with dendrites and axon marked complete in NeuroMorpho metadata. It differs from the two earlier holdouts in species, source archive, study and reconstruction context.

## Provenance and source metadata

- NeuroMorpho.Org ID: NMO_163775
- Cell name: `18453_5766_x31719_y6139-semi_r`
- Archive: Peng
- Species: mouse
- Strain: Cux2-CreERT2;Ai166
- Age: 56 days
- Gender metadata: Male/Female
- Primary / secondary / tertiary region: neocortex / somatosensory / layer 2–3 (supplemental)
- Primary / secondary / tertiary cell class: principal cell / pyramidal / projection, Intratelencephalic (IT)
- Experimental condition: Control
- Protocol: in vitro, whole mount
- Stain: green fluorescent protein
- Reconstruction software: Vaa3D
- NeuroMorpho physical integrity: Dendrites & Axon Complete
- NeuroMorpho morphological attributes: **No Diameter**
- Related article: *Brain-wide single neuron reconstruction reveals morphological diversity in molecularly defined striatal, thalamic, cortical and claustral neuron types*
- Related article DOI: 10.1101/675280

Official source links:
- [NeuroMorpho detail page](https://neuromorpho.org/neuron_info.jsp?neuron_name=18453_5766_x31719_y6139-semi_r)
- [Standardized SWC source](https://neuromorpho.org/dableFiles/peng/CNG%20version/18453_5766_x31719_y6139-semi_r.CNG.swc)
- [NeuroMorpho API record](https://neuromorpho.org/api/neuron/id/163775)
- [NeuroMorpho morphometry](https://neuromorpho.org/api/morphometry/id/163775)

## Local pinned source and topology

Repository path:
`amsn-core/data/mouse/neuromorpho_peng/NMO_163775_18453_5766_x31719_y6139_semi_r.CNG.swc`

Pinned SHA-256:
`94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`

The canonical extract contains all numeric seven-column SWC records from the standardized upstream file. Original comment blocks were replaced with a provenance and attribution header; node IDs, types, coordinates, radii and parent IDs were not modified.

Independent structural scan and repository preflight report:
- 4,209 SWC records
- Type 1 soma: 3
- Type 2 axon: 3,602
- Type 3 basal dendrite: 306
- Type 4 apical dendrite: 298
- One soma root
- All 4,209 records reachable from the root
- No duplicate IDs
- No missing parent references

NeuroMorpho morphometry reports total length 41,180.6 µm, 121 bifurcations, 251 branches and maximum path distance 9,944.2 µm. Those are repository-provided morphometry values.

## Import3D / AMSN preflight

The successful preflight observed:
- 4,200 electrical compartments
- 251 NEURON sections
- 82,587 NEURON segments
- Seven unique canonical retained ports
- Maximum NEURON segment length: 0.4999943591 µm, below the 0.5 µm cap
- Finite 1 kHz full-Hines passive response

The AMSN/Import3D mapper's canonical seven shared SWC node IDs are:
`1, 40, 144, 3926, 3948, 4104, 4180`.

The basal-q25 and apical-q25 node IDs are computed using the same path-distance quantile helper and Import3D mapping as the canonical seven. They are recorded in `results/NMO_163775_PengControl_holdout/preflight.json`; the matched replay fails closed if its independently recomputed q25 IDs differ from preflight.

The manual path-distance estimate from raw SWC records did not match the actual Import3D site mapper. The checked-in preflight is therefore the authority for the retained ports and q25 node identities. Do not substitute the earlier manual estimate.

## Matched 7-port / 9-port experiment

The replay is configured to compare:
- Seven canonical ports vs nine ports (same shared seven plus basal-q25 and apical-q25).
- Basis orders 112 and 168.
- Same six extended10kHz shifts for both port layouts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.
- Nine deterministic passive Rm/Cm/Ra parameter scenarios.
- Nine AC frequencies: 0.1 Hz through 10 kHz.
- Three current sources: soma, basal-q75 and apical-q75.
- Two square-pulse widths: 2 ms and 10 ms; amplitude 10 pA, onset 2 ms, duration 20 ms, dt 0.1 ms.
- Full-Hines references independently computed for both port layouts, with exact shared-node consistency checks.

Expected coverage:
- 36 reduced models
- 324 AC frequency rows
- 1,728 transient-port rows
- 756 matched shared-output pairs
- 216 q25-only observations
- 378 shared-Hines checks

## Mesh comparability

This morphology uses a maximum NEURON segment length of 0.5 µm. The two earlier human holdouts used 0.125 µm. Therefore, absolute accuracy, resource and runtime values from this mouse holdout must not be pooled or compared directly with those earlier human runs. The valid within-morphology comparison is the matched seven-port vs nine-port design using exactly the same mesh and passive scenarios.

## Scientific limits and interpretation

**Critical limitation — No Diameter.** NeuroMorpho lists this morphology's morphological attributes as No Diameter. The standardized SWC has a radius field, but these radius values are not documented measured biological diameters. Passive geometry and resulting absolute numerical metrics are therefore dependent on the standardized radius representation and the chosen passive parameter assumptions. This morphology is useful for testing topology/port-count effects under a fixed standardized passive model, but it must not be presented as diameter-grounded biological validation.

This is one mouse Control-condition reconstruction, not a population sample. Repository metadata marks dendrites and axon complete, but this does not establish biological completeness beyond that metadata. The experiment validates passive linear-RC reduction against full Hines only. It does not validate active channels, action potentials, nonlinear synapses, plasticity or biological physiology. Full Hines remains canonical; no production defaults or runtime behavior are changed.

## Data attribution

NeuroMorpho.Org states that downloaded data are available under CC BY 4.0 and requires all three citations when used in publications:
1. The original reconstruction article linked on the cell detail page (DOI 10.1101/675280).
2. NeuroMorpho.Org (RRID:SCR_002145).
3. Tecuatl C, Ljungquist B, Ascoli GA (2024), “Accelerating the continuous community sharing of digital neuromorphology data,” FASEB Bioadv. 6(7):207–221. DOI: 10.1096/fba.2024-00048.

See [NeuroMorpho terms of use](https://neuromorpho.org/useterm.jsp).

## Validation state

At successful run 45311916600, the full AMSN suite passed 173/173; Peng-specific source/mapping tests passed 19/19; source checksum, Import3D preflight, matched replay, exact coverage, result commit and artifact upload passed. See the validated numerical results below.


## Validated matched-port numerical results

**Successful GitHub Actions run:** [45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600)  
**Artifact:** [#14883752560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600/artifacts/14883752560)  
**Artifact ZIP SHA-256:** \`9060b04e6e769a1e9b40700197361bf67a59b164965441849e8cd3effb716a58\`

The full AMSN test suite passed **173/173**; Peng-specific tests passed **19/19**; source checksum, Import3D preflight, matched replay, exact coverage, result commit and artifact upload all passed.

Exact output coverage:
- 36 reduced models (7/9 ports × 112/168 × nine parameter scenarios).
- 324 AC rows.
- 1,728 transient-port rows.
- 756 matched shared-output pairs.
- 216 q25-only observations.
- 378 shared-Hines checks.

All 36 reduced models achieved their requested order and passed the conductance/capacitance Cholesky checks. The 378 common Hines reference traces were **exactly equal** between seven-port and nine-port layouts: maximum absolute voltage difference 0 V and relative L2 difference 0%.

### Shared-output comparison

| Basis order | 9-port worse / better / tie | Median 9/7 error ratio | Maximum ratio | Maximum absolute 9-port shared NRMSE |
|---:|---:|---:|---:|---:|
| 112 | 378 / 0 / 0 | **78.051×** | 6,739.21× | 0.0001933% |
| 168 | 347 / 31 / 0 | **14.501×** | 300.22× | 6.0657e−7% |

The ratios show a consistent relative loss on shared outputs when the two q25 ports are included, particularly at order112. However, the seven-port baseline errors are themselves extremely small. Therefore the large ratios must be read alongside the absolute errors: even the maximum nine-port shared-output NRMSE is 1.933e−4% at order112 and 6.066e−7% at order168. No universal application tolerance was assumed.

### q25-only output accuracy

| Basis order | Observations | Median q25 NRMSE | Maximum q25 NRMSE |
|---:|---:|---:|---:|
| 112 | 108 | 1.8480e−5% | 2.1588e−4% |
| 168 | 108 | 1.5567e−8% | 4.2824e−7% |

The actual q25-only SWC IDs derived and confirmed by the AMSN/Import3D mapper are basal **224** and apical **4096**. Both are distinct from the shared seven.

### 10 kHz AC residuals and numeric storage

| Port count | Order | Median Z residual | Maximum Z residual | Median Y residual | Maximum Y residual | Numeric storage |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 112 | 4.3254e−7% | 5.7369e−7% | 2.7321e−6% | 4.3868e−6% | 3.7803 MB |
| 9 | 112 | 3.2464e−5% | 3.8892e−5% | 4.8096e−5% | 6.9852e−5% | 3.7803 MB |
| 7 | 168 | 6.7621e−12% | 9.8598e−12% | 1.1370e−10% | 3.8025e−10% | 5.8140 MB |
| 9 | 168 | 6.8670e−9% | 1.0472e−8% | 4.8906e−8% | 7.7469e−8% | 5.8140 MB |

Numeric storage is basis plus reduced G/C matrices; at the same order it is equal for seven and nine ports in this implementation.

### Runtime

- Wall time: 187.50 s
- User CPU: 273.21 s
- System CPU: 0.26 s
- Peak RSS: 160,272 KiB
- Runtime: Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2

This is one run on a hosted runner, not a controlled repeated performance benchmark.

## Interpretation across the three morphology holdouts

The matched 7/9-port results now cover three morphologies:

| Morphology | Context / reconstruction boundary | Order112 median 9/7 ratio | Order168 median 9/7 ratio |
|---|---|---:|---:|
| NMO_162186 | Human epilepsy surgical specimen; axon incomplete | 8.162× | 0.99999985× |
| NMO_03524 | Human Jacobs Control; dendrites moderate, axon incomplete | 1.00000465× | 0.99999991× |
| NMO_163775 | Mouse Peng Control; dendrites and axon complete by metadata, but No Diameter | 78.051× | 14.501× |

This further confirms that the **relative incremental cost of q25 ports is morphology-dependent**. On NMO_163775 the shared-output ratios favor seven ports, but the absolute nine-port errors remain small in this passive experiment, and order168 gives q25 maximum NRMSE below 4.3e−7%. The appropriate choice depends on the application's absolute error tolerance and required outputs; do not choose solely from the relative 9/7 ratio.

The Peng run uses a 0.5 µm NEURON segment cap, whereas the two human runs used 0.125 µm. Do not pool absolute errors or runtimes across those morphologies as if their reference discretizations were identical.

**Scientific boundary:** the Peng record explicitly says No Diameter. Its standardized SWC radius values are not measured biological diameters. The results therefore test topology/port-count behavior for the standardized geometry representation under the selected passive parameters; they are not diameter-grounded biological validation, do not represent a mouse population, and do not validate active channels or nonlinear physiology. Full Hines remains canonical; no production defaults are changed.
