# Human passive PRIMA high-frequency validation against NEURON

**Date:** 2026-11-22 (Asia/Bangkok)  
**Implementation:** research/prima-high-frequency-neuron-validation-2026-11-22  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/1  
**Schur/PRIMA workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079 — 6/6 jobs passed  
**Frequency audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325128 — 3/3 jobs passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325088 — 4/4 jobs passed, including Python 3.12/3.13 tests and both NEURON cross-validation jobs. Post-merge main checks also passed: Core CI [44965966066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966066), Schur/PRIMA [44965966021](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966021), fine-mesh [44965966005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966005), frequency audit [44965965999](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965965999).

## 1. Research question

At a fixed PRIMA order of 56, does adding positive-real expansion shifts at 6 and 10 kHz improve the reduced seven-port passive response against native NEURON, compared with the current four-shift basis?

The control basis uses shifts (0, 100, 1,000, 3,000) Hz. The experimental basis uses (0, 100, 1,000, 3,000, 6,000, 10,000) Hz. Both bases are measured in the same process against the same full AMSN Hines model and the same NEURON port matrices. Thus the comparison does not change the state budget, retained ports, morphology, reference mesh or passive parameterization.

## 2. Protocol and scope

- Three existing human morphology records: NMO_68174 cell1125 (12,399 AMSN compartments), NMO_68175 cell1204 (13,747 compartments), and NMO_290988 / 1094_Mohan_etal_2015 (8,893 compartments).
- Two NEURON maximum-segment lengths per morphology: 0.125 and 0.0625 µm, for six independent jobs.
- Seven retained SWC-defined source/probe ports.
- Ten frequencies: 0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz.
- PRIMA order 56 in both the control and extended model.
- Transient comparison uses the existing basal-q75 10 pA pulse, 2–12 ms, 20 ms observation, backward Euler dt=0.1 ms.
- Full AMSN Hines is retained as the internal reference; native NEURON is the independent simulator reference.

## 3. Per-configuration results

Each frequency-domain value below is the maximum over the ten tested frequencies for that morphology/mesh configuration. Error columns are Frobenius relative errors in percent. The frequency of the maximum direct-NEURON error is 10 kHz in every case except the extended-basis impedance maximum for NMO_68174 at 0.125 µm, which occurs at 6 kHz.

| Morphology | NEURON mesh (µm) | Four-shift Z vs NEURON | Six-shift Z vs NEURON | Four-shift Y vs NEURON | Six-shift Y vs NEURON |
|---|---:|---:|---:|---:|---:|
| NMO_290988 | 0.125 | 0.527300 | 0.216765 | 0.360664 | 0.184927 |
| NMO_290988 | 0.0625 | 0.525405 | 0.214797 | 0.360650 | 0.184925 |
| NMO_68174 | 0.125 | 0.424855 | 0.144176 | 0.404489 | 0.210977 |
| NMO_68174 | 0.0625 | 0.367613 | 0.110644 | 0.403749 | 0.211010 |
| NMO_68175 | 0.125 | 0.266066 | 0.118789 | 0.358725 | 0.192735 |
| NMO_68175 | 0.0625 | 0.259146 | 0.107832 | 0.358613 | 0.192758 |

The complete per-configuration measurements, including Hines residuals, frequencies of maxima, state reduction and transient summaries, are preserved in [the aggregate CSV](../results/human_passive_prima_high_frequency_neuron_aggregate_2026-11-22.csv). Raw per-frequency results and matrices are retained in the six workflow artifacts linked below.

## 4. Aggregate result and frequency-dependent trade-off

Across all six configurations:

| Metric (maximum across configurations and frequencies) | Four-shift control | Six-shift 10 kHz |
|---|---:|---:|
| PRIMA impedance vs full Hines | 0.416133% | 0.113574% |
| PRIMA admittance vs full Hines | 0.432732% | 0.124064% |
| PRIMA impedance vs NEURON | 0.527300% | 0.216765% |
| PRIMA admittance vs NEURON | 0.404489% | 0.211010% |

At 10 kHz, the worst direct-NEURON impedance error falls by about 2.43× and the worst admittance error by about 1.92×. The maximum residual against full Hines falls by about 3.66× for impedance and 3.49× for admittance. All six morphology/mesh cases show lower worst-case direct-NEURON errors for both Z and Y with the extended basis.

The improvement is concentrated in the upper band, not uniform at every frequency. Taking the maximum across the six configurations at each frequency:

| Frequency | Four-shift Z/Y vs NEURON | Six-shift Z/Y vs NEURON |
|---:|---:|---:|
| 0.1 Hz | 0.021792% / 0.013401% | 0.021792% / 0.013401% |
| 1 Hz | 0.021800% / 0.013397% | 0.021800% / 0.013397% |
| 10 Hz | 0.022375% / 0.013005% | 0.022375% / 0.013005% |
| 30 Hz | 0.024279% / 0.011124% | 0.024279% / 0.011123% |
| 100 Hz | 0.027640% / 0.008549% | 0.027621% / 0.008566% |
| 300 Hz | 0.029767% / 0.008413% | 0.029639% / 0.008751% |
| 1 kHz | 0.051102% / 0.012648% | 0.050378% / 0.018335% |
| 3 kHz | 0.093933% / 0.021333% | 0.085640% / 0.042362% |
| 6 kHz | 0.215721% / 0.183684% | 0.144176% / 0.032613% |
| 10 kHz | 0.527300% / 0.404489% | 0.216765% / 0.211010% |

The extended basis slightly increases the worst admittance residual at some intermediate frequencies (1–3 kHz), although those errors remain below 0.043%. It materially improves both metrics at 6–10 kHz. This is a genuine band-allocation trade-off and should not be hidden by a single aggregate score.

## 5. Stability, conditioning and transient checks

- All six morphology × mesh jobs passed; each job reported 109/109 AMSN tests passed.
- Both projected conductance and capacitance matrices passed Cholesky positive-definiteness checks for the control and extended bases.
- The largest NEURON port-impedance condition number observed was 91.263; no high-frequency matrix-conditioning failure was reported.
- The maximum all-port transient NRMSE was 2.845e-6% for the four-shift control and 9.073e-6% for the extended basis. The worst individual-port NRMSE was 0.000316% and 0.000901%, respectively. The extended basis is therefore slightly worse for this pulse protocol, but absolute errors remain below 0.001% NRMSE.
- The aggregate matrix audit completed 6/6. The separate passive frequency audit completed 3/3. The Core CI's two regular test jobs passed on Python 3.12 and 3.13; its two NEURON cross-validation jobs were still in progress at report time.

## 6. Decision

**Keep the six-shift 10 kHz model experimental and optional. Do not replace the four-shift default.**

The new basis consistently improves the worst direct-NEURON Z/Y errors in the tested 10 kHz band, but it allocates approximation budget differently and modestly worsens some 1–3 kHz admittance and transient metrics. The 56-state order removes 99.370–99.593% of the original compartment states, but this reduction result applies only to the specified passive RC network and seven retained ports.

The workflow has not changed the simulator default. The full Hines model remains canonical.

## 7. Reproducibility and raw artifacts

Six independent workflow artifacts are available:

- [NMO_290988, 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731028424)
- [NMO_290988, 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731137993)
- [NMO_68174, 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731342405)
- [NMO_68174, 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731516061)
- [NMO_68175, 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731576685)
- [NMO_68175, 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079/artifacts/14731596611)

The artifacts contain the raw 7×7 port matrices, Schur summaries, port-localization data, the four-shift baseline, the six-shift extended basis, order-sweep results and transient rows.

## 8. Limits and next experiment

This validates a passive, linear RC reduction at seven selected ports. It does not validate active ion channels, nonlinear synapses, calcium, metabolism, gene regulation, plasticity, cognition or biological realism. The passive parameter values remain numerical reference parameters, not population-fitted human physiological distributions. NMO_290988 is a partial dendritic reconstruction without an axon and must not be described as a healthy-control morphology.

Next, compare order 56 and 84 using both the four-shift and six-shift basis, expand the retained port set, and test multiple pulse widths/input locations. Only after those checks should a broader operating-band recommendation be made.


## Follow-up: order and transient robustness

The subsequent experiment is documented in [HUMAN_PASSIVE_PRIMA_ORDER_TRANSIENT_SWEEP_2026-11-22.md](HUMAN_PASSIVE_PRIMA_ORDER_TRANSIENT_SWEEP_2026-11-22.md). It compares four-shift order 56 with six-shift orders 28/56/84 and six source/width scenarios across three morphologies and two NEURON mesh caps. The results reject order 28, retain order 56 as the default/control, and identify six-shift order 84 as an optional high-fidelity passive RC preset. The apical-q90 output port is the recurring transient error location.
