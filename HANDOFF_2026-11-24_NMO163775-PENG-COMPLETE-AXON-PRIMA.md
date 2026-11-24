# Handoff — NMO_163775 Peng complete-axon PRIMA holdout

**Branch:** `research/prima-peng-complete-axon-third-morphology-2026-11-24`  
**PR:** [#16](https://github.com/Nolane-x/Nghien-cuu/pull/16)  
**NeuroMorpho:** NMO_163775 / Peng / `18453_5766_x31719_y6139-semi_r`

## Source lock

- Mouse, Cux2-CreERT2;Ai166, 56 days, Male/Female metadata.
- Neocortex, somatosensory, layer 2–3; principal pyramidal IT projection.
- Control; in vitro; whole mount; GFP; Vaa3D.
- NeuroMorpho marks dendrites and axon complete.
- Morphological attributes: **No Diameter**.
- SWC path: `amsn-core/data/mouse/neuromorpho_peng/NMO_163775_18453_5766_x31719_y6139_semi_r.CNG.swc`
- SHA-256: `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`
- 4,209 records: soma 3, axon 3,602, basal 306, apical 298; one root; all nodes connected; no duplicate IDs/missing parents.

## AMSN/Import3D preflight checkpoint

- 4,200 electrical compartments.
- 251 NEURON sections, 82,587 segments.
- 0.5 µm max segment cap, actual maximum 0.4999943591 µm.
- Seven canonical common node IDs: `1, 40, 144, 3926, 3948, 4104, 4180`.
- q25 IDs are derived in preflight and pinned there; replay must match them exactly.

## Replay design

- 7/9 ports; basis orders 112 and 168.
- Six extended10kHz shifts 0/100/1,000/3,000/6,000/10,000 Hz.
- Nine deterministic passive Rm/Cm/Ra scenarios.
- AC 0.1 Hz–10 kHz; three injection sources; 2/10 ms pulses, 10 pA, 2 ms onset, 20 ms duration, dt 0.1 ms.
- Coverage target: 36 models, 324 frequency, 1,728 transient, 756 common pairs, 216 q25 observations, 378 Hines checks.
- Mesh cap 0.5 µm is intentionally different from 0.125 µm on the two human holdouts; do not compare absolute errors across morphologies as if mesh were equal.

## Important scientific caveat

No Diameter means standardized SWC radii are not measured diameters. Do not infer diameter-grounded biological parameters or biological accuracy from the passive model. The holdout tests topology/port-count behavior under the standardized geometry representation. This is a single mouse cell and passive linear-RC comparison only; full Hines remains canonical and no production defaults change.

## Validated numerical result

Successful run [45311916600](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600) passed the full test suite (173/173), Peng-specific tests (19/19), checksum, Import3D preflight, replay, exact coverage, archive commit and artifact upload. Artifact [#14883752560](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45311916600/artifacts/14883752560); ZIP SHA-256 `9060b04e6e769a1e9b40700197361bf67a59b164965441849e8cd3effb716a58`.

| Order | 9-port worse / better / tie | Median 9/7 shared error ratio | Maximum absolute 9-port shared NRMSE |
|---:|---:|---:|---:|
| 112 | 378 / 0 / 0 | 78.051× | 0.0001933% |
| 168 | 347 / 31 / 0 | 14.501× | 6.0657e−7% |

q25 nodes are basal 224 and apical 4096. q25 maximum NRMSE is 2.1588e−4% at order112 and 4.2824e−7% at order168. All 378 shared-Hines traces were exactly equal (0 V difference). Coverage: 36 models, 324 AC rows, 1,728 transient rows, 756 shared pairs, 216 q25 observations, 378 Hines checks.

Interpret ratios with absolute error: the 9/7 ratios are large because the seven-port baseline error is extremely small; the absolute nine-port errors remain small under this passive protocol. No universal tolerance is assumed.

This adds a third morphology and again supports morphology-dependent port-count cost. The Peng mesh cap is 0.5 µm (vs 0.125 µm in the two human holdouts), and NeuroMorpho lists No Diameter; do not pool cross-morphology absolute errors or interpret the standardized SWC radii as biological measurements. Full Hines remains canonical; no production defaults changed.
