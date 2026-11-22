# Human passive PRIMA nine-port high-order basis capacity — validated result

**Date:** 2026-11-22 (Asia/Bangkok)  
**Merged PR:** [#4](https://github.com/Nolane-x/Nghien-cuu/pull/4)  
**Merge commit:** `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`

## Executive result

The nine-port enrichment experiment previously found that simply adding basal/apical q25 retained ports at six-shift orders 28/56/84 worsened the difficult apical-q90 transient relative to the seven-port order-84 control. This follow-up tested whether additional basis capacity resolves that trade-off.

Across all six morphology × mesh configurations, **six-shift PRIMA orders 112 and 168 improved apical-q90 transient error in every matched scenario** against both the nine-port order-84 and seven-port order-84 controls. Neither candidate regressed at any of the seven shared output ports in the 252 matched comparisons per candidate.

This supports a conditional research conclusion: the nine-port basis can be made more accurate for this passive RC protocol by increasing its Krylov basis capacity. It does not justify changing the production default: order 112/168 have lower state compression and slightly higher worst-case frequency-domain error versus native NEURON than order 84. Wall-clock and peak-memory costs have not yet been benchmarked.

## Workflow and coverage evidence

- High-order nine-port matrix: [run 44979673244](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673244), 6/6 jobs passed.
- AMSN Core CI: [run 44979673250](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673250), 4/4 jobs passed across Python 3.12 and 3.13, including independent NEURON validation.
- Nine-port baseline/control: [run 44979673251](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673251), 6/6 jobs passed.
- Seven-port Schur control: [run 44979673239](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44979673239), 6/6 jobs passed.
- Six configurations × 420 records = **2,520 validated sweep rows**. Each configuration contains 60 frequency-response rows, 324 individual-port transient rows and 36 all-port transient aggregate rows. The workflow asserts exact row counts and model identities.
- Requested and achieved basis ranks match exactly at 28, 56, 84, 112 and 168.

## Experimental protocol

Three SWC morphologies were evaluated at NEURON maximum segment lengths of 0.125 and 0.0625 µm:

- NMO_68174 cell1125 (12,410 SWC records)
- NMO_68175 cell1204 (13,758 SWC records)
- NMO_290988 / 1094_Mohan_etal_2015 (8,903 SWC records)

The nine electrical ports were soma, basal q25/q50/q75/q90 and apical q25/q50/q75/q90. Current sources were soma, basal-q75 and apical-q75; source/probe roles at q75 share a single electrical port. Four-shift order 56 was retained as a control. Six-shift candidates used orders 28, 56, 84, 112 and 168. Frequency responses were evaluated at ten points from 0.1 Hz to 10 kHz. Transients used 10 pA pulses, 2 ms and 10 ms widths, 2 ms onset, 20 ms total time and 0.1 ms timestep, at every retained port.

## Aggregate numerical results

All error columns are maxima across six configurations and the tested frequency/transient matrix. Frequency-domain errors are Frobenius-relative percentages. Transient errors are NRMSE percentages.

| Model | Actual order | State reduction | Max Z/Y vs NEURON | Max Z/Y vs Hines | Max all-port transient | Max single-port transient |
|---|---:|---:|---:|---:|---:|---:|
| Four-shift order 56 control | 56 | 99.370–99.593% | 3.3455 / 1.5510% | 3.4854 / 1.6552% | 0.00439293% | 0.02619245% |
| Six-shift order 28 | 28 | 99.685–99.796% | 35.2070 / 9.1940% | 35.0307 / 9.1357% | 1.32490183% | 12.09981448% |
| Six-shift order 56 | 56 | 99.370–99.593% | 0.3273 / 0.3146% | 0.2196 / 0.2214% | 0.07309632% | 0.52309925% |
| Six-shift order 84 | 84 | 99.055–99.389% | 0.1713 / 0.1111% | 0.04295 / 0.01112% | 0.000119447% | 0.001775061% |
| Six-shift order 112 | 112 | 98.741–99.185% | 0.2033 / 0.1192% | 0.0002128 / 0.0002642% | 0.000002364% | 0.000034471% |
| Six-shift order 168 | 168 | 98.111–98.778% | 0.2034 / 0.1194% | 0.000000145 / 0.000000194% | 0.000000355% | 0.000003450% |

The worst apical-q90 transient NRMSE across all six configs was 0.000034471% at order 112 and 0.000003450% at order 168. Order 168 is the most accurate tested transient option; order 112 gives a lower-rank compromise with substantially better transient accuracy than order 84.

## Matched apical-q90 comparison

The comparison pairs the same morphology, mesh, transient source/pulse scenario and apical-q90 output. There are 36 paired cases per comparison (six configurations × six scenarios).

| Candidate | Reference | Paired cases | Worse cases | Median error ratio | Worst error ratio |
|---|---|---:|---:|---:|---:|
| Order 112 | Nine-port order 84 | 36 | 0 | 0.02216 | 0.44677 |
| Order 112 | Seven-port order 84 | 36 | 0 | 0.25658 | 0.87630 |
| Order 168 | Nine-port order 84 | 36 | 0 | 0.01411 | 0.44527 |
| Order 168 | Seven-port order 84 | 36 | 0 | 0.15774 | 0.87334 |

Against the seven-port order-84 reference, the median apical-q90 error ratio is 0.2566 for order 112 (about 74.3% lower error) and 0.1577 for order 168 (about 84.2% lower error). Even the worst paired case remains below one for both candidates.

## Shared-output non-regression

Seven shared output ports were compared against the seven-port order-84 reference: soma, basal q50/q75/q90 and apical q50/q75/q90. Each candidate has 252 matched comparisons (six configurations × six scenarios × seven outputs).

| Candidate | Comparisons | Regressions | Median error ratio | Worst error ratio |
|---|---:|---:|---:|---:|
| Order 112 | 252 | 0 | 0.12795 | 0.87630 |
| Order 168 | 252 | 0 | 0.01906 | 0.87334 |

All 14 per-probe summaries also have zero regressions. The detailed breakdown is in `human_passive_prima_nine_port_high_order_shared_port_by_probe_2026-11-22.csv`.

## Accuracy–cost trade-off and decision

- **Order 168** gives the lowest transient errors and the lowest Hines frequency-domain residuals in this matrix. It reduces state count by 98.11–98.78%, still above 98%.
- **Order 112** is a smaller candidate, with 98.74–99.19% state reduction and very strong transient accuracy. It is a plausible compromise if order 168's computational cost proves excessive.
- Both higher orders have slightly larger worst-case frequency-domain error versus native NEURON than order 84 (order 84: Z/Y 0.1713/0.1111%; order 112: 0.2033/0.1192%; order 168: 0.2034/0.1194%). The very low Hines residual at higher orders does not remove this cross-simulator discrepancy.
- No measured CPU runtime or peak RSS/memory is included in this sweep. Therefore order 168 is the accuracy leader, not yet the performance-optimal choice.
- Keep full Hines canonical. Keep the existing default sweep unchanged at orders 28/56/84. Treat 112 and 168 as opt-in high-fidelity research candidates until resource benchmarking and held-out morphology validation are complete.

## Reproducibility and files

The six raw high-order artifacts are indexed in `human_passive_prima_nine_port_high_order_artifact_manifest_2026-11-22.csv`. The original seven-port and nine-port control data are preserved in their respective Actions runs. The standard-library analysis program `analyze_human_prima_nine_port_high_order_artifacts.py` validates artifact coverage, rank consistency, scenario/port completeness and writes detailed matched-pair CSVs.

Run after extracting the six artifacts for each port set:

```bash
python analyze_human_prima_nine_port_high_order_artifacts.py \
  --high-root ./artifacts/high-order \
  --nine-root ./artifacts/nine-port \
  --seven-root ./artifacts/seven-port \
  --out ./analysis-output
```

The program writes aggregate/configuration metrics, all 72 q90 pair records, all 504 shared-output pair records and their grouped summaries.

## Scientific limits

This is validation of a passive linear RC cable reduction only. It does not validate active ion channels, nonlinear synapses, plasticity, calcium, gene expression, metabolism, cognition or biological completeness. The NMO_290988 / Mohan morphology is a partial dendritic reconstruction without an axon and must not be described as a healthy-control morphology.
