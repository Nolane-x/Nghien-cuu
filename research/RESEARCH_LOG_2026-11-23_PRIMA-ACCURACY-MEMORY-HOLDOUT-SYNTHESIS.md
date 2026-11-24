# Research log — PRIMA accuracy/memory/holdout synthesis

**Date:** 23 November 2026  
**Branch:** research/prima-accuracy-memory-holdout-synthesis-2026-11-23

## Work performed

Read and cross-checked validated reports and CSVs from PRs #4–#8, then incorporated shift/order, matched port-count and two distinct morphology holdouts:
- PR #4 high-order nine-port matrix
- PR #5 resource/RSS benchmark
- PR #6 equal-order seven-port versus nine-port
- PR #7 shift/order Pareto matrix
- PR #8 independent NMO_162186 morphology holdout

No source matrices were re-run; all referenced workflows had already passed and their outputs were committed. The purpose of this checkpoint is to reconcile the evidence without mixing non-identical protocols or port configurations.

## Result

The current high-frequency passive candidate is seven-port order112 with the extended 10 kHz shift distribution. On three morphologies and nine deterministic parameter scenarios it achieved median 10 kHz Z/Y residuals 4.681e−6% / 1.390e−5%, with worst transient error effectively identical to order112 narrow shifts. On the NMO_162186 holdout its median 10 kHz Z/Y residuals were 4.630e−6% / 9.474e−6%, again with essentially unchanged transient metrics.

For nine retained ports, order168 is the first equal-order test point where the seven shared outputs are effectively at parity with the seven-port model while the new q25 outputs are accurate (max q25 NRMSE 9.7486e−7%). The result is passive and specific to the tested protocol.

The separate resource benchmark reports median peak RSS 267.90 / 276.15 / 301.73 MB for orders84/112/168. Every one of 12 paired RSS comparisons is positive at both order transitions. Wall and user CPU timing is not a controlled order ranking because GitHub used seven CPU models.

## Decision

Full Hines remains canonical. Do not change production defaults. Keep 7-port order112 extended10kHz as a high-frequency passive candidate and order84 extended10kHz as an accuracy/storage compromise on NMO_03524. Matched port-count tests show the incremental cost of q25 ports is morphology-dependent: order168 was needed for parity on NMO_162186, while NMO_03524 was already at parity at order112.

## Remaining validation gaps

- Only two matched 7/9-port morphology holdouts have been tested; both are individual cells with incomplete axons or other reconstruction limitations. A third morphology with a more complete axon is needed.
- No controlled fixed-hardware timing comparison.
- No active/nonlinear biological validation.


## Matched 7-port / 9-port holdout completed

PR #13 / workflow 45184621520 closed the previous port-count × holdout validation gap on NMO_162186. Coverage was 36 models, 324 frequency rows, 1,728 transient rows, 756 shared-output pairs, 216 q25-only observations and 378 full-Hines shared-port checks. All 378 Hines comparisons were exactly equal.

Order112 nine-port regressed on 377/378 shared pairs; median 9/7 transient-error ratio 8.162×. Order168 was effectively at parity (190 better, 187 worse, 1 tie; median 0.99999985×). q25 max NRMSE was 3.6711e−6% at order112 and 8.6226e−8% at order168.

Updated conditional choice: use a matched seven/nine-port test on the target morphology. NMO_162186 needed order168 for shared-output parity; NMO_03524 did not. Extended10kHz remains the high-frequency shift family, with order84 a good accuracy/storage compromise on NMO_03524. Full Hines remains canonical.

Outstanding work: add a third independent morphology with a more complete axon and distinct source study; controlled fixed-machine performance benchmark; separate active/nonlinear validation.


## Second independent morphology completed — NMO_03524 Jacobs Control

PR #14 / workflow 45196546471 passed 146/146 tests, source checksum/topology and Import3D preflight, and the complete seven-port shift/order matrix. Artifact #14827204708 was uploaded.

Source: NeuroMorpho NMO_03524 / Jacobs / 1-5-3; human 23-year-old male, Control metadata, occipital BA18, in vitro Golgi; dendrites moderate, axon incomplete. The immutable SWC is 31,199 bytes, SHA-256 6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748. It has 869 records, one root, no missing parents; NEURON 9.0.2 Import3D produced 862 AMSN electrical compartments, 68 sections and 35,248 segments at max 0.125 µm, with seven unique ports.

The sweep covered 81 models, 729 frequency rows and 3,402 transient-port rows, all candidates passively positive definite. Order112 extended10kHz produced median 10 kHz Z/Y residuals 3.6005e−10% / 1.8143e−10%; order84 extended10kHz produced 5.5775e−7% / 2.8753e−7% using 0.6601 MB numeric storage vs 0.9280 MB for order112. Order56 remains lowest footprint (0.4161 MB) but with a higher high-frequency residual trade-off.

Conclusion: extended10kHz shift family is independently supported on a second human morphology in a Control metadata context. It is not a matched factorial comparison with NMO_162186. PR #14 is seven-port only and does not replicate q25/9-port transfer there.

Next gate: add a third independent morphology, preferably with a more complete axon; fixed-hardware timing and active/nonlinear validation remain separate.


## Second matched port-count morphology completed — NMO_03524

PR #15 / workflow 45198630080 passed the matched seven-port/nine-port order112/order168 comparison on the NMO_03524 Jacobs Control-condition morphology. Exact coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations and 378 shared-Hines checks. All 378 common Hines references were identical.

At order112, nine-port was worse on 204 shared pairs, better on 173 and tied on one; median nine/seven transient-error ratio 1.000004647 and maximum 1.006136. At order168, there were 189 better and 189 worse; median ratio 0.999999905 and maximum 1.007211. q25 maximum NRMSE was 3.058499e−8% at order112 and 3.058557e−8% at order168.

This contrasts with NMO_162186 (PR #13): order112 nine-port had 377/378 regressions and median error ratio 8.162×, while order168 restored parity. Port-count cost is morphology-dependent under the tested passive protocol, not a universal order threshold.

Artifact #14829912332; ZIP SHA-256 cba24b3c36c24b125339feefbb3a10d0f105adf9cda2c80030a5577e80350b03.

Next: add a third independent morphology with a more complete axon and different source study. Fixed-hardware timing and active/nonlinear validation remain separate.


## Updated synthesis decision after PR #15

Do not encode a universal order168 requirement for nine-port PRIMA. The same matched design gave a median nine/seven error ratio 8.162× at order112 on NMO_162186, but 1.00000465× on NMO_03524. Both q25 probes were accurate on NMO_03524 at order112 (maximum NRMSE 3.0585e−8%). This is morphology-specific evidence; a third, structurally more complete morphology is the next gate.


## Third matched port-count morphology validated — NMO_163775

PR #16 / workflow 45311916600 passed all 173 AMSN tests, 19 Peng-specific tests, source SHA-256, Import3D preflight, exact replay coverage, result archive and artifact upload. Artifact #14883752560; ZIP SHA-256 9060b04e6e769a1e9b40700197361bf67a59b164965441849e8cd3effb716a58.

NMO_163775 is a mouse Peng archive Control-condition somatosensory neocortical L2–3 pyramidal IT projection cell. NeuroMorpho marks dendrites and axon complete but lists No Diameter. SWC SHA-256 94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f; 4,209 records; 4,200 electrical compartments. NEURON preflight: 251 sections, 82,587 segments, 0.5 µm maximum mesh cap, observed maximum 0.49999436 µm. Shared ports: [1,40,144,3926,3948,4104,4180]; q25 probes basal 224, apical 4096.

Exact replay coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations, 378 shared-Hines checks. All 378 Hines traces were exactly equal (0 V difference).

Order112: 9-port worse on all 378 shared pairs, median 9/7 error ratio 78.051×, max ratio 6,739.21×. Maximum absolute nine-port shared NRMSE was only 0.0001933%. Order168: 347 worse / 31 better, median ratio 14.501×, max ratio 300.22×; maximum absolute nine-port shared NRMSE 6.0657e−7%. q25 max NRMSE 2.1588e−4% at order112 and 4.2824e−7% at order168.

The high 9/7 ratios are relative to a very small seven-port baseline; use the absolute NRMSE values when comparing to a predeclared application tolerance. At 10 kHz, nine-port median Z/Y residuals are 3.2464e−5% / 4.8096e−5% at order112 and 6.8670e−9% / 4.8906e−8% at order168. Numeric storage is 3.7803 MB / 5.8140 MB at orders112/168. Runtime 187.50 s wall, 273.21 s user CPU, peak RSS 160,272 KiB.

The third morphology strengthens the morphology-dependent conclusion. Unlike the two earlier human fixtures it has complete arbors by repository metadata, but No Diameter and a 0.5 µm mesh cap (vs 0.125 µm for the human holdouts). Do not interpret this as diameter-grounded biological validation or pool absolute errors across different meshes. Full Hines remains canonical; no production defaults change.

Source: [PR #16](https://github.com/Nolane-x/Nghien-cuu/pull/16), [run 45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600), [artifact #14883752560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600/artifacts/14883752560).
