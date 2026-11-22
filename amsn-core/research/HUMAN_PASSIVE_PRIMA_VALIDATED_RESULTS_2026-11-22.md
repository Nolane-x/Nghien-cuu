# PRIMA validated results — held-out morphology, port count and basis order

**Checkpoint:** 2026-11-22; branch `research/allen-human-morphology-heldout-preflight-2026-11-22`; PR #8; validated head `5180f0bc72dbfad0a460b0870ca80fec772db0e3`.

## 1. Independent human morphology holdout

Workflow [45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648) passed **2/2 jobs**: source preflight and full PRIMA matrix. The exact standardized NeuroMorpho SWC was passed from the preflight artifact to the PRIMA job and SHA-256 checked again.

Source: **NMO_162186 / 770307286_transformed**, Allen Cell Types, human L2–3 pyramidal cell, right middle temporal gyrus. NeuroMorpho marks dendrites complete, axon incomplete and experimental condition epilepsy. Do not call it a healthy control or complete neuron.

- SWC: 7,287 records; type counts soma 3 / axon 23 / basal 3,411 / apical 3,850; 48 branch points.
- Source SWC SHA-256: `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`.
- AMSN: 7,278 full-node electrical compartments; normalized electrical surface 21,324.6492 µm², −0.198674% versus NeuroMorpho's 21,367.1 µm².
- NEURON 9.0.2: 104 sections, 83,306 segments, maximum section segment 0.125 µm.
- Seven unique ports mapped; maximum Import3D mapping offset 0.0592673 µm.
- Maximum AMSN/NEURON five-probe transfer-ratio discrepancy 0.00109651%; NEURON soma input resistance 60.041589 MΩ.

The electrical-area check explicitly subtracts seven virtual soma-wire frusta and replaces the two three-point soma outline frusta with the spherical soma membrane area. This yields a strict area identity against the AMSN cable-area sum; no tolerance was loosened.

### Holdout PRIMA matrix

Nine candidates: orders 56/84/112 × narrow-3k / extended-10k / balanced-10k. Nine deterministic scenarios: nominal; Rm, Cm and Ra ±20%; and all-parameter ±20%. AC: 9 frequencies from 0.1 Hz to 10 kHz. Transients: soma/basal-q75/apical-q75 × 2/10 ms pulse × seven fixed output ports.

**Accepted coverage:** 81 model rows, 729 frequency rows, 3,402 transient-port rows. All 81 models achieved their requested basis order and passed reduced G/C Cholesky checks. Exact key coverage and finite, non-negative error validation passed. Runtime: 264.28 s wall, 352.94 s user CPU, 197,068 KiB peak RSS, exit status 0.

| Candidate | Median Z error @10 kHz | Median Y error @10 kHz | Median transient NRMSE | Max transient NRMSE | Numeric storage |
|---|---:|---:|---:|---:|---:|
| order56 narrow | 0.233028% | 0.331131% | 6.22125e−6% | 9.29145e−4% | 3.31 MB |
| order56 extended | 0.0591833% | 0.117693% | 4.27989e−5% | 0.00393226% | 3.31 MB |
| order56 balanced | 0.239990% | 0.367419% | 1.00084e−5% | 0.00159416% | 3.31 MB |
| order84 narrow | 0.00570729% | 0.0123381% | 1.10192e−8% | 4.10627e−7% | 5.00 MB |
| order84 extended | 0.000157810% | 0.000299701% | 2.30108e−7% | 5.73164e−5% | 5.00 MB |
| order84 balanced | 0.00148209% | 0.00400671% | 2.19252e−8% | 2.35417e−6% | 5.00 MB |
| order112 narrow | 0.000139586% | 0.000310408% | 8.72298e−9% | 1.45426e−7% | 6.72 MB |
| order112 extended | 4.63044e−6% | 9.47438e−6% | 8.72745e−9% | 1.45425e−7% | 6.72 MB |
| order112 balanced | 0.000164586% | 0.000100642% | 8.72310e−9% | 1.45425e−7% | 6.72 MB |

For this single holdout, order112 extended-10k reduces median 10 kHz Hines-relative Z/Y error by **30.15× / 38.39×** versus order112 narrow, with essentially unchanged transient median and maximum. Order84 narrow is a lower-storage transient-oriented alternative. No single shift strategy wins at every order.

## 2. Equal-order seven-port vs nine-port

Workflow [45012282737](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282737) passed **12/12 jobs**: three morphologies × two mesh caps × two port sets. Twelve ZIP artifact hashes were independently verified. Raw coverage: **3,072 rows** (six 7-port configs ×232 rows and six 9-port configs ×280 rows). Paired comparisons: 1,008 common-output transient pairs and 144 apical-q90 pairs.

| Equal-order model | q90 pairs | 9-port worse | 9-port better | Median 9/7 ratio | Max ratio |
|---|---:|---:|---:|---:|---:|
| Four-shift order56 control | 36 | 36 | 0 | 11.515× | 22.350× |
| Six-shift order56 | 36 | 36 | 0 | 127.706× | 613.199× |
| Six-shift order112 | 36 | 36 | 0 | 1.577× | 699.068× |
| Six-shift order168 | 36 | 14 | 22 | 0.99999977× | 1.00006334× |

The very large order112 maximum is denominator-sensitive: on Mohan2015 apical-q75 2 ms, the seven-port q90 error is only 4.93e−8%, versus 3.45e−5% for nine ports. Its median q90 errors are 4.196e−7% (7-port) and 2.036e−6% (9-port).

Across all seven shared outputs, order56 control worsens 252/252 pairs (median ratio 4.697×); six-shift order56 worsens 252/252 (131.329×); order112 worsens 252/252 (3.326×). At order168, 138/252 worsen and 114/252 improve; median ratio is 1.000001×, range 0.999037–1.000360. Thus order168 restores near-parity but is not an accuracy improvement.

At 10 kHz, full-Schur vs NEURON median admittance/impedance errors are similar between seven and nine ports: 0.10972%/0.14680% for seven ports versus 0.10968%/0.14125% for nine.

**Decision:** keep seven ports as the canonical reference. If nine retained outputs are needed, order168 is the only tested equal-order candidate that preserves near-parity on the common transient outputs. Do not promote nine ports at order56 or 112.

## 3. Nine-port high-order capacity

Workflow [45012282650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282650) passed **6/6 jobs** across three morphologies × two meshes. The six ZIP digests were independently verified. Coverage: 2,520 rows = 360 frequency, 1,944 per-port transient and 216 all-port transient records.

| Model | Median transient NRMSE | P90 transient NRMSE | Maximum transient NRMSE | Max Z error @10 kHz | Max Y error @10 kHz |
|---|---:|---:|---:|---:|---:|
| Order28 | 0.163541% | 1.87235% | 12.0998% | 35.0307% | 9.13573% |
| Order56 | 0.0182071% | 0.128596% | 0.523099% | 0.219616% | 0.221433% |
| Order84 | 6.29555e−6% | 9.72489e−5% | 0.00177506% | 0.0429510% | 0.0111241% |
| Order112 | 2.66073e−7% | 3.21067e−6% | 3.44712e−5% | 0.000212762% | 0.000264203% |
| Order168 | 5.96715e−8% | 4.09537e−7% | 3.44984e−6% | 1.45011e−7% | 1.93883e−7% |

Order168's extra transient benefit versus 112 is morphology-dependent: maximum NRMSE falls ~76.8× on NMO_290988, but only ~1.04× on NMO_68174 and ~1.003× on NMO_68175. This argues against a blanket production order168 without a cost/benefit and runtime/RSS study.

## 4. CI checkpoint and outstanding item

On PR #8 head `5180f0bc72dbfad0a460b0870ca80fec772db0e3`, 28/29 workflow runs completed successfully, with zero failures. Core CI [45012282476](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282476) passed 4/4; parameter robustness [45012282485](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282485) 3/3; enrichment [45012282496](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282496) 6/6.

The high-order runtime/RSS workflow [45012282723](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723) passed its 16-test validator preflight, but 23/30 resource jobs were still queued at the latest check. **Do not claim resource benchmarking complete** until all jobs pass and artifacts are verified.

## 5. Scientific limits

All work here is passive linear-RC numerical validation against full Hines. NMO_162186 is an epilepsy surgical-specimen dendritic reconstruction with incomplete axon, not a healthy control or population sample. ±20% parameter scenarios are deterministic stress tests, not biological parameter distributions. No active-channel, nonlinear-synapse, calcium, plasticity, gene, metabolic or cognitive validity is established. Full Hines remains canonical; production defaults are unchanged.
