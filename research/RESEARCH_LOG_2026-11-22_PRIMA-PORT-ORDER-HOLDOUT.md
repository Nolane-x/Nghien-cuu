# Research log — PRIMA held-out morphology and equal-order port comparison

**Date:** 2026-11-22  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**Validated head:** `5180f0bc72dbfad0a460b0870ca80fec772db0e3`

## Completed independent holdout

Workflow [45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648) passed 2/2. Source NMO_162186 is a human L2–3 pyramidal morphology from an epilepsy surgical specimen. Dendrites are marked complete, axon incomplete. SWC SHA-256 `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`. The matrix validated 81 model, 729 frequency and 3,402 transient-port rows; all 81 achieved the requested order and passed Cholesky. Runtime 264.28 s wall, 352.94 s user CPU, 197,068 KiB peak RSS.

Order112 extended-10k reduced median 10 kHz Z/Y errors 30.15×/38.39× relative to order112 narrow with essentially unchanged transient median/max. Order84 narrow remains a lower-storage transient-oriented candidate. Results and source constraints are in `amsn-core/research/HUMAN_PASSIVE_PRIMA_VALIDATED_RESULTS_2026-11-22.md`.

## Equal-order seven vs nine ports

Workflow [45012282737](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282737) passed 12/12. Twelve artifacts were downloaded and hash-verified (manifest CSV). Raw total 3,072 records. At orders56/112, all 252 common outputs per model and all 36 apical-q90 pairs per model worsened with nine ports. At order168, 138/252 common outputs worsened and 114 improved; median ratio 1.000001, range 0.999037–1.000360. For q90, 22/36 improved and 14/36 worsened, all within 0.999643–1.000063. This is practical parity, not an accuracy gain.

## Nine-port high-order capacity

Workflow [45012282650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282650) passed 6/6 and 2,520 records were independently inspected. Maximum per-port transient NRMSE: order28 12.10%, order56 0.5231%, order84 0.001775%, order112 3.447e-5%, order168 3.450e-6%. The extra benefit of order168 over112 is highly morphology-dependent: about 76.8× at the worst Mohan path, but only 1.04× / 1.003× on NMO_68174 / NMO_68175.

## Artifact integrity

All 20 ZIP artifacts associated with the holdout, equal-order and high-order runs were downloaded and independently hashed. Every digest matches GitHub Actions metadata; details and sizes are in `amsn-core/results/human_prima_verified_artifact_manifest_2026-11-22.csv`.

## CI and outstanding resource study

On current PR #8 head, 28/29 workflow runs completed successfully, zero failures. Core CI [45012282476] passed 4/4. Holdout [45012282648] 2/2; equal-order [45012282737] 12/12; high-order capacity [45012282650] 6/6; enrichment [45012282496] 6/6; parameter robustness [45012282485] 3/3.

High-order runtime/RSS workflow [45012282723] passed its 16-test validator preflight but had 23/30 resource jobs queued at the time of this checkpoint. Do not report the resource matrix as complete until every job and artifact has been inspected.

All research remains passive linear-RC. Full Hines is canonical; no production defaults changed. NMO_162186 is not a healthy-control sample or a complete axon-bearing neuron; ±20% stress scenarios are not biological parameter distributions.
