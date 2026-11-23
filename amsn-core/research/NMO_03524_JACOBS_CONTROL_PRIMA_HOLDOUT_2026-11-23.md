# Independent PRIMA shift/order validation on NMO_03524 Jacobs control morphology

**Date:** 23 November 2026  
**Morphology:** NeuroMorpho NMO_03524 / Jacobs / 1-5-3  
**Status:** validated — all nine passive PRIMA candidates replayed successfully

## Why this holdout matters

The earlier NMO_162186 holdout is a human epilepsy surgical specimen with incomplete axon. This experiment adds a distinct published **Control-condition** human cortical pyramidal morphology from the Jacobs archive. Its source study used Golgi reconstructions; the cortical region is occipital Brodmann area 18.

This is not described as a pristine complete neuron: NeuroMorpho labels dendrites moderate and the axon incomplete. It is one control-condition cell, not a representative human population.

## Source and preflight

- NeuroMorpho ID: NMO_03524; cell 1-5-3.
- Human, 23-year-old male; neocortex, occipital, Brodmann area 18.
- Control, in vitro, Golgi, 120 µm slice.
- Soma, basal and apical dendrites, plus incomplete axon.
- Official source SWC: https://neuromorpho.org/dableFiles/jacobs/CNG%20version/1-5-3.CNG.swc
- Metadata: https://neuromorpho.org/neuron_info.jsp?neuron_name=1-5-3

The immutable downloaded source is **31,199 bytes**, SHA-256:

`6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748`

The CI preflight passed:
- 869 SWC records; one soma root; no missing parent references.
- Type counts: soma 3, axon 42, basal dendrite 816, apical dendrite 8.
- 30 branch points and 4,453.468 µm total path length.
- 862 AMSN electrical compartments; 68 NEURON sections and 35,248 segments.
- NEURON 9.0.2; maximum segment length 0.12499949 µm under the 0.125 µm cap.
- Seven distinct PRIMA ports and a finite 1 kHz passive response.

One terminal probe, SWC node 751 at normalized section position x=1.0, lies beyond the last segment centre. The shared probe mapper now uses the nearest endpoint segment for that readout and records the fallback explicitly; it does not extrapolate beyond the available NEURON segment-centre values. The measured centre offset is 0.06250 µm. All other selected probes use the normal bracketed interpolation path.

## Numerical experiment

The validated seven-port PRIMA shift/order matrix was reused without changing the reduction algorithm:

- Orders: 56, 84 and 112.
- Shift distributions: narrow 3 kHz, extended 10 kHz, balanced 10 kHz.
- Nine deterministic passive parameter scenarios: nominal, Rm ±20%, Cm ±20%, Ra ±20%, all parameters −20%, all parameters +20%.
- AC frequencies: 0.1 Hz to 10 kHz (nine points).
- Source ports: soma, basal-q75, apical-q75.
- Transients: 2 ms and 10 ms square pulses; 10 pA; 2 ms onset; 20 ms total; 0.1 ms timestep.
- Reference: full Hines on the same exact morphology and passive parameter scenario.

All nine candidates achieved the requested basis order and passed Cholesky passivity checks. Exact coverage was **81 model rows, 729 frequency rows and 3,402 transient-port rows**. No conductance fitting or parameter optimization was performed.

## Validated results

GitHub Actions run [45196546471](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471) passed **146/146 repository tests**, the pinned-source and Import3D preflight, the full nine-candidate matrix, result validation, commit and artifact upload.

Artifact: [nmo03524-jacobs-control-prima-holdout #14827204708](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471/artifacts/14827204708)  
Artifact ZIP SHA-256: `21f3298613f7660908388ddebc4a0d9e3df88123b513d22b60fdc6edece19ed6`

The table reports median residuals across the nine deterministic parameter scenarios at 10 kHz. Transient NRMSE is likewise summarized across the full source × pulse × probe × scenario matrix. Numeric storage is the basis plus reduced G/C arrays; it is **not** whole-process RSS.

| Candidate | Median Z error at 10 kHz | Median Y error at 10 kHz | Median transient NRMSE | Maximum transient NRMSE | Numeric storage |
|---|---:|---:|---:|---:|---:|
| Order 56, narrow 3 kHz | 0.0085692% | 0.0054551% | 3.5394e−9% | 3.1554e−8% | 0.4161 MB |
| Order 56, extended 10 kHz | 0.0011971% | 0.00024464% | 9.0554e−9% | 1.8051e−7% | 0.4161 MB |
| Order 56, balanced 10 kHz | 0.0057947% | 0.0060288% | 4.4369e−9% | 4.5654e−8% | 0.4161 MB |
| Order 84, narrow 3 kHz | 9.2260e−6% | 9.1022e−6% | 3.2713e−9% | 3.1554e−8% | 0.6601 MB |
| **Order 84, extended 10 kHz** | **5.5775e−7%** | **2.8753e−7%** | **3.2709e−9%** | **3.1554e−8%** | **0.6601 MB** |
| Order 84, balanced 10 kHz | 2.9230e−5% | 8.1139e−6% | 3.2710e−9% | 3.1554e−8% | 0.6601 MB |
| Order 112, narrow 3 kHz | 6.8748e−9% | 3.9628e−9% | 3.2708e−9% | 3.1554e−8% | 0.9280 MB |
| **Order 112, extended 10 kHz** | **3.6005e−10%** | **1.8143e−10%** | **3.2708e−9%** | **3.1554e−8%** | **0.9280 MB** |
| Order 112, balanced 10 kHz | 9.1883e−8% | 1.6398e−8% | 3.2708e−9% | 3.1554e−8% | 0.9280 MB |

### Interpretation and conditional choice

- **Highest high-frequency accuracy:** order112 with extended 10 kHz shifts. It yields the smallest median 10 kHz impedance/admittance residuals in this holdout, 3.60e−10% / 1.81e−10%.
- **Best accuracy/storage compromise:** order84 with extended 10 kHz shifts. Its median 10 kHz Z/Y residuals are already only 5.58e−7% / 2.88e−7%, while numeric storage is 0.6601 MB instead of 0.9280 MB at order112 — about 29% less.
- **Smallest numerical footprint:** order56 uses 0.4161 MB. The narrow 3 kHz shift set retains very small transient errors, but its median 10 kHz Z/Y residuals are higher (0.00857% / 0.00546%). Use this lower-order option only when that high-frequency trade-off is acceptable.
- The balanced 10 kHz distribution was not the best high-frequency choice on this morphology; extended 10 kHz shifts were more accurate at orders 56, 84 and 112.

The full run took 50.25 s wall time, 119.73 s user CPU and peaked at 90,748 KiB RSS. This is one end-to-end GitHub runner measurement, not a controlled per-candidate performance benchmark. These process-level figures must not be confused with the numeric storage column.

## Relationship to the NMO_162186 holdout

The earlier NMO_162186 epilepsy-morphology experiment also found extended 10 kHz shifts to be a strong high-frequency choice. The new Jacobs control-condition holdout provides independent support for that shift strategy in a different human morphology and experimental context.

The two morphologies differ substantially in size and structure, so their absolute residuals and memory figures should not be compared as though they were a matched factorial experiment. Also, this Jacobs experiment used seven ports only: it does **not** independently validate the nine-port q25 decision on this control morphology. The q25/order168 result remains supported by the matched 7-vs-9-port experiment on NMO_162186 only.

## Outputs

- Pinned SWC: `amsn-core/data/human/neuromorpho_jacobs/1-5-3.CNG.swc`
- Provenance: `amsn-core/data/human/neuromorpho_jacobs/NMO_03524_PROVENANCE.md`
- Preflight and explicit port mapping: `amsn-core/results/NMO_03524_JacobsControl_holdout/`
- Candidate model, frequency, transient and summary CSVs plus report JSON: `amsn-core/results/NMO_03524_JacobsControl_human_prima_shift_order_pareto_2026-11-23_*`
- Run timing: `amsn-core/results/NMO_03524_JacobsControl_prima_shift_order_2026-11-23.time.txt`

## Scientific limits and next gates

This is one human Control-condition morphology; it does not establish population-level validity. Dendrites are rated moderate and the axon incomplete. The results validate passive linear-RC numerical reduction against full Hines only. They do not validate active ion channels, action potentials, nonlinear synapses, plasticity or biological function.

Next:
1. Run the matched 7-port/9-port order112/order168 comparison on NMO_03524 to test whether the q25 conclusion also transfers to a control-condition morphology.
2. Add another independent morphology with different source/experimental context and, preferably, a more complete axon reconstruction.
3. Repeat resource timing on fixed hardware if a solver-time ranking is needed.
4. Keep active-channel/nonlinear validation as separate experiments.

Full Hines remains canonical. No solver, order default, port count or production runtime behavior is changed.
