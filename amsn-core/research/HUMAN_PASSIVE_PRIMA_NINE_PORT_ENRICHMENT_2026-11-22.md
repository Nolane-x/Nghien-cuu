# Human passive PRIMA nine-port enrichment — validated results and seven-port comparison

**Date:** 2026-11-22 (Asia/Bangkok)  
**Implementation:** PR #3, squash merge  
**Merge commit:** `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`  
**Nine-port workflow:** [44976224651 — 6/6 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651)  
**Core CI:** [44976224745 — 4/4 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224745)  
**Seven-port baseline:** [44966510373 — 6/6 jobs passed](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373)  
**Implementation PR:** https://github.com/Nolane-x/Nghien-cuu/pull/3

## 1. Research question

The previous seven-port order/transient study repeatedly identified the apical-q90 output as the worst individual transient port. This experiment tested whether adding intermediate basal and apical probe locations (q25) to the retained port set would improve that output while preserving the original q50/q75/q90 paths.

The experiment is a controlled **passive linear RC** comparison, not a test of active dendritic biology. The full AMSN Hines solver remains canonical.

## 2. Port design and protocol

Three current injection locations were preserved: soma, basal-q75 and apical-q75. Nine unique electrical ports were retained:

- soma
- basal-q25, basal-q50, basal-q75, basal-q90
- apical-q25, apical-q50, apical-q75, apical-q90

The basal-q75 and apical-q75 locations are simultaneously source and probe roles; each is represented once in the electrical boundary set. The run-time and morphology tests require nine unique SWC nodes and nine unique mapped electrical vertices after soma/wire normalization.

Four reduction variants were compared: four-shift order-56 control; six-shift order 28, 56 and 84. Ten frequencies were evaluated from 0.1 Hz through 10 kHz. Six transient protocols used 10 pA current pulses (soma/basal-q75/apical-q75 × 2/10 ms), 2 ms onset, 20 ms observation, and 0.1 ms backward-Euler timestep. Every transient was scored at all nine ports.

Coverage:
- Morphologies: NMO_68174 cell1125, NMO_68175 cell1204, and NMO_290988 / 1094_Mohan_etal_2015.
- NEURON maximum segment lengths: 0.125 and 0.0625 µm.
- Six morphology × mesh configurations.
- Each configuration emitted 280 sweep rows: 40 frequency rows + 6 × (9 per-port rows + 1 all-port aggregate) × 4 models = 240 transient rows.
- Total: **1,680 rows**, comprising 240 frequency rows, 1,296 per-port transient rows and 144 all-port aggregate rows.

## 3. Validation status

The dedicated nine-port workflow completed all six matrix jobs successfully on the merged PR code. Each job ran the full test suite, checked the exact SWC record count, executed the nine-port Schur/PRIMA audit, and uploaded its raw data/log artifact. A sampled job log confirms Python 3.12.16, NEURON 9.0.2 and 118/118 tests passing in 5.36 s; the six jobs all report success.

Core CI completed 4/4 jobs across Python 3.12 and 3.13, including test/compile/example and independent NEURON cross-validation jobs. The seven-port control also completed 6/6 jobs. The implementation changed only the optional nine-port path; the established seven-port mapper remains the default path.

## 4. Aggregate nine-port results

Worst-case values across six morphology/mesh configurations and ten frequencies; transient error is NRMSE (%).

| Model | State reduction | Max Z vs Hines | Max Y vs Hines | Max Z vs NEURON | Max Y vs NEURON | Max all-port transient | Max single-port transient |
|---|---:|---:|---:|---:|---:|---:|---:|
| Four-shift order 56 control | 99.370–99.593% | 3.485388 | 1.655248 | 3.345529 | 1.550977 | 0.00439293 | 0.02619245 |
| Six-shift order 28 | 99.685–99.796% | 35.030708 | 9.135727 | 35.206969 | 9.193970 | 1.32490183 | 12.09981448 |
| Six-shift order 56 | 99.370–99.593% | 0.219616 | 0.221433 | 0.327323 | 0.314562 | 0.07309632 | 0.52309925 |
| Six-shift order 84 | 99.055–99.389% | 0.042951 | 0.011124 | 0.171340 | 0.111111 | 0.00011945 | 0.00177506 |

The worst individual transient output is apical-q90 in all four variants. The worst individual-port values occur on short 2 ms conditions. Order 28 is unacceptable for this expanded retained-port set. Order 84 is the best of the tested nine-port variants by both aggregate and individual transient metrics, but its worst single-port transient error is still greater than the same model's seven-port result.

## 5. Direct paired comparison against the seven-port baseline

The key comparison pairs identical morphology, mesh, model, transient source/pulse scenario and the shared apical-q90 output port. This produces 36 matched comparisons per model (6 configs × 6 scenarios), 144 total.

| Model | Median nine-port / seven-port apical-q90 error | Maximum ratio | Worse comparisons |
|---|---:|---:|---:|
| Four-shift order 56 control | 11.515× | 22.350× | 36/36 |
| Six-shift order 28 | 2.118× | 3.394× | 36/36 |
| Six-shift order 56 | 127.706× | 613.199× | 36/36 |
| Six-shift order 84 | 7.814× | 28.749× | 36/36 |

**All 144 paired apical-q90 comparisons worsened when expanding from seven to nine ports at the same tested model orders.** The effect is not an artifact of changing the all-port aggregation denominator: apical-q90 is the same named output node in each matched pair. Other common outputs also mostly worsened, particularly for six-shift order 56. The per-model paired summary is preserved in `human_passive_prima_nine_vs_seven_port_q90_summary_2026-11-22.csv`; the 24-row morphology/mesh/model breakdown is in `human_passive_prima_nine_port_config_model_summary_2026-11-22.csv`. All 144 individual q90 pair observations are reproducible from the per-port transient rows in the six seven-port and six nine-port workflow artifacts.

This is a negative result with a clear design implication: adding more retained boundary ports at the same reduction order increases the burden on the reduced basis; it does not guarantee improved accuracy at a difficult output. The data do not establish the underlying mechanism beyond this numerical observation.

## 6. Decision

1. **Do not promote the nine-port configuration as an accuracy improvement.** It failed the primary apical-q90 non-degradation criterion in every matched comparison.
2. **Retain the seven-port set as the reference port configuration** for the next passive PRIMA study. Keep the full Hines model as the canonical solution.
3. **Keep order 84 as an optional high-fidelity passive candidate only within the tested configuration.** It remains the best of the nine-port candidates, but the nine-port order-84 apical-q90 maximum (0.001775%) is about 7.8× the median paired seven-port error and up to 28.75× in an individual matched scenario.
4. **Reject order 28** for the full 0.1–10 kHz, six-scenario protocol.
5. Do not change production defaults based on this experiment.

## 7. Next experiment

Test whether the nine-port basis needs additional capacity or source-aware/block-Krylov enrichment rather than simply more retained probes. A follow-up should compare orders 112 and 168, plus a source/probe-weighted block basis, against the unchanged seven-port and nine-port controls. Preserve identical source locations, frequency grid, six transient scenarios and mesh matrix; record actual basis rank, positive-definiteness, Hines residual, native NEURON error, and every shared-port transient NRMSE. The primary success criterion is a reproducible reduction at apical-q90 **without** sacrificing soma, basal and other shared-port outputs. Use held-out morphology/configuration checks and do not tune parameters to force cross-simulator agreement.

## 8. Raw artifacts and reproducibility

### Nine-port (this experiment)

All six artifacts were uploaded by [workflow 44976224651](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651):

- [NMO_68174 cell1125, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14735389729)
- [NMO_68174 cell1125, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14735449253)
- [NMO_68175 cell1204, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14736610394)
- [NMO_68175 cell1204, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14736144273)
- [NMO_290988 Mohan2015, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14736516060)
- [NMO_290988 Mohan2015, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651/artifacts/14735389638)

### Seven-port matched baseline

The six baseline artifacts are retained in [workflow 44966510373](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373). Each artifact contains the same frequency/order/transient family for its morphology and mesh configuration.

The NMO_290988 reconstruction is a partial dendritic morphology without an axon and must not be treated as a healthy-control morphology. This entire study validates a passive linear RC reduction against numerical references; it does not validate active channels, nonlinear synapses, plasticity, calcium, gene expression, metabolism, cognition or biological completeness.
