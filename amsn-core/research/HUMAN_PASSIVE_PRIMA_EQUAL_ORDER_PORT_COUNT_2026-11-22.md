# Human passive PRIMA equal-order seven-port vs nine-port comparison — validated result

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Experiment branch:** research/prima-equal-order-seven-vs-nine-ports-2026-11-22  
**PR:** [#6 — Compare seven- and nine-port PRIMA at equal basis order](https://github.com/Nolane-x/Nghien-cuu/pull/6)  
**Actions run:** [44987393352](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44987393352)  
**Workflow head:** 8863ddfa03762c4822121c5422bd581dc7048495

## Executive result

The equal-order matrix completed successfully: **12/12 GitHub Actions jobs passed**, including the complete AMSN test suite, morphology record-count checks, the port-matrix experiment and exact output coverage checks. All 12 artifacts were downloaded and inspected.

The key finding is that **adding two retained q25 ports at the same PRIMA basis order does not improve transient accuracy at the seven shared outputs**:

- At order 56, every one of the 252 matched shared-output comparisons has a larger NRMSE in the nine-port model. The median nine/seven error ratio is 131.33×.
- At order 112, all 252 comparisons again have a larger nine-port error ratio; the median is 3.33×. However, the absolute maximum single-output NRMSE remains only 0.00003446882% for nine ports versus 0.00000344983% for seven ports.
- At order 168, the two models are effectively indistinguishable at shared outputs: median ratio 1.00000062×, and the worst ratio is 1.00064571×. There are 148 tiny relative regressions and 104 tiny improvements.

The additional q25 outputs themselves become highly accurate at higher orders. Across 72 q25 observations per order, the worst q25 NRMSE falls from 0.14043% at order 56 to 0.00001231% at order 112 and 0.0000009749% at order 168.

**Decision:** port count and basis order must be selected together. Order 168 is the first tested equal-order point where the nine-port expansion retains the extra q25 outputs without a material loss at the seven shared outputs. This is a result for the tested passive linear RC models and protocol only. Keep full Hines canonical; do not change production defaults or infer active neuronal biology from it.

## Experimental design and coverage

Three morphology fixtures were tested at two NEURON maximum segment lengths:

- NMO_68174 cell1125 — 12,410 SWC records.
- NMO_68175 cell1204 — 13,758 SWC records.
- NMO_290988 / 1094_Mohan_etal_2015 — 8,903 SWC records; this is a partial dendritic reconstruction without an axon and must not be described as a healthy-control morphology.

Mesh caps were 0.125 and 0.0625 µm. Seven-port and nine-port configurations were run at the same achieved six-shift PRIMA orders 56, 112 and 168, alongside a four-shift order-56 control. Ten frequencies were measured (0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz). Transient tests used soma, basal-q75 and apical-q75 sources × 2 ms and 10 ms pulses; current 10 pA, onset 2 ms, total duration 20 ms and dt 0.1 ms.

Exact coverage:
- Each seven-port configuration: 40 frequency rows + 168 transient-port rows + 24 all-port rows = **232**; six configurations = **1,392**.
- Each nine-port configuration: 40 + 216 + 24 = **280**; six configurations = **1,680**.
- Total: **3,072 sweep rows** across 12 successful jobs.
- The analysis pairs common outputs by exact SWC node ID, morphology, mesh, source/pulse scenario and actual PRIMA order. Each order has 6 configurations × 6 scenarios × 7 shared outputs = **252 matched pairs**.
- The nine-port-only q25 outputs produce 6 configurations × 6 scenarios × 2 added ports = **72 observations per order**.

## Matched transient errors at the seven shared output nodes

All errors below are NRMSE percentages against the corresponding full Hines transient trace. Ratios are nine-port error divided by seven-port error. “Common-seven RMS” first computes an RMS across the seven matched outputs for each morphology/mesh/scenario, then summarizes its nine/seven ratio across 36 scenarios.

| Six-shift order | Matched pairs | Nine-port regressions | Improvements | Median pair ratio | Worst pair ratio | Median common-seven RMS ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 56 | 252 | 252 | 0 | 131.329× | 1,696.570× | 191.032× |
| 112 | 252 | 252 | 0 | 3.326× | 2,580.830× | 1.512× |
| 168 | 252 | 148 | 104 | 1.00000062× | 1.00064571× | 1.00000010× |

| Order | Seven-port max single-output NRMSE | Nine-port max single-output NRMSE |
|---:|---:|---:|
| 56 | 0.00869138% | 0.52309925% |
| 112 | 0.00000344983% | 0.00003446882% |
| 168 | 0.00000344984% | 0.00000344983% |

The large relative ratios at order 112 are partly a denominator effect: the seven-port errors are already extremely close to zero. The absolute nine-port maximum remains 0.00003447%, not a large physical-response discrepancy. At order 168, relative differences are at the level of a few parts in 10^4 or less, with absolute errors essentially the same.

## Added q25 output accuracy

The two added outputs are basal-q25 and apical-q25. They do not have seven-port counterparts and therefore are not included in the shared-port pairing.

| Order | q25 observations | Median NRMSE | Maximum NRMSE |
|---:|---:|---:|---:|
| 56 | 72 | 0.00972849% | 0.14042521% |
| 112 | 72 | 0.0000002199% | 0.0000123083% |
| 168 | 72 | 0.00000009782% | 0.00000097486% |

This confirms that higher basis capacity is important for preserving the two new spatial observations. It does not show that adding ports at a fixed small order improves the old outputs.

## Frequency-domain check and state compression

Maximum values across six morphology/mesh configurations and ten frequencies are shown below. The seven-port and nine-port impedance/admittance matrices have different dimensions; these maxima are therefore reported separately against each matching reference, not treated as a strict elementwise 7-vs-9 ranking.

| Ports | Order | State reduction range | Max Z/Y residual vs Hines | Max Z/Y discrepancy vs NEURON |
|---:|---:|---:|---:|---:|
| 7 | 56 | 99.370–99.593% | 0.113574 / 0.124064% | 0.216765 / 0.211010% |
| 7 | 112 | 98.741–99.185% | 0.000009861 / 0.000014183% | 0.216501 / 0.119634% |
| 7 | 168 | 98.111–98.778% | 0.000000003264 / 0.000000001357% | 0.216498 / 0.119621% |
| 9 | 56 | 99.370–99.593% | 0.219616 / 0.221433% | 0.327323 / 0.314562% |
| 9 | 112 | 98.741–99.185% | 0.000212708 / 0.000264203% | 0.203300 / 0.119156% |
| 9 | 168 | 98.111–98.778% | 0.000000150963 / 0.000000193883% | 0.203394 / 0.119407% |

The internal PRIMA-vs-Hines residual can be extremely small while a separate discrepancy to native NEURON remains around 0.1–0.33%. These are different comparisons and must not be conflated. Maximum NEURON impedance condition numbers were 91.263 (seven-port) and 91.268 (nine-port).

## Interpretation and next decision

1. **Do not choose port count in isolation.** At equal order 56 or 112, nine ports are worse on each matched shared-output transient pair. At order 168, common outputs are numerically equivalent while the two extra q25 ports are represented accurately.
2. **Do not over-interpret relative ratios near zero.** The order-112 absolute NRMSE remains very small even though all ratios are greater than one.
3. **Keep order 168 and nine ports as an opt-in high-fidelity passive candidate**, not a new default. It increases model order and is not yet justified by measured runtime/memory; the separate resource benchmark is still being repaired and rerun.
4. Keep the seven-port order-84 / four-shift order-56 controls and full Hines reference intact. Do not tune against NEURON in this comparison.
5. Next, finish CPU/RSS profiling, test held-out morphologies and perturb passive parameters (Rm, Cm and Ra). Only after that should an active channel or nonlinear synapse experiment begin as a separate validation stage.

## Reproducibility

The standard-library analysis program is analyze_human_prima_equal_order_port_count.py. After downloading and extracting the 12 Actions artifacts, place the six seven-port sweep CSVs in one directory and the six nine-port sweep CSVs in another. Run:

    python analyze_human_prima_equal_order_port_count.py \
      --seven-dir ./artifacts/seven-port \
      --nine-dir ./artifacts/nine-port \
      --output-dir ./analysis-output

The script validates exact row counts, model IDs, requested/achieved order, frequency counts, scenario coverage and exact SWC node matching. It writes detailed 756-row shared-port pairs, 108 common-seven RMS records, 216 q25-only records and aggregate summary CSVs.

The original 12 compressed artifacts are indexed in HUMAN_PASSIVE_PRIMA_EQUAL_ORDER_ARTIFACT_MANIFEST_2026-11-22.csv. Artifact IDs and SHA-256 digests are provided; GitHub currently lists expiry as 2027-02-20.

## Scientific limits

These are passive linear RC model reduction experiments. They do not validate active Na/K/Ca channels, action-potential propagation, nonlinear AMPA/NMDA/GABA synapses, plasticity, calcium signaling, gene expression, metabolism, cognition or biological completeness. They validate numerical preservation of specified passive port responses under the stated source/probe and pulse protocol.
