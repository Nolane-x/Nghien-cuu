# PRIMA order, input-location and pulse-width validation on human passive morphologies

**Date:** 2026-11-22 (Asia/Bangkok)  
**Implementation branch:** `research/prima-order-transient-matrix-2026-11-22`  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/2  
**Schur/PRIMA workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373 — 6/6 jobs passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510441 — 4/4 jobs passed  
**Frequency audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510356 — 3/3 jobs passed

## 1. Research question

Does the six-shift 10 kHz PRIMA basis generalize beyond the prior order-56, basal-q75, 10 ms pulse experiment when both reduced order and transient input location change?

The four-shift control uses positive-real expansion frequencies (0, 100, 1,000, 3,000) Hz. The six-shift models use (0, 100, 1,000, 3,000, 6,000, 10,000) Hz. Four model configurations are compared: four-shift order 56 control, six-shift order 28, six-shift order 56 and six-shift order 84.

## 2. Protocol and coverage

- Three human morphology records: NMO_68174 cell1125 (12,399 AMSN compartments), NMO_68175 cell1204 (13,747 compartments) and NMO_290988 / 1094_Mohan_etal_2015 (8,893 compartments). The NMO_290988 record is a partial dendritic reconstruction without an axon; it is not a healthy-control morphology.
- Two NEURON maximum-segment lengths per morphology: 0.125 and 0.0625 µm, giving six independent morphology/mesh configurations.
- Seven retained SWC-defined ports and ten frequencies: 0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz.
- Six transient inputs per model: soma, basal-q75 and apical-q75 stimulation, each with 2 ms and 10 ms pulse widths. Each pulse is 10 pA, starts at 2 ms, is observed for 20 ms and uses backward Euler at dt=0.1 ms.
- All transient responses are measured at all seven ports and against full Hines. Frequency-domain Z/Y responses are compared with both full AMSN Hines and native NEURON.
- Each configuration must contain 40 frequency rows plus 192 transient rows, for 232 rows. All six CSVs passed the exact row-count assertion: 1,392/1,392 total rows.

## 3. Aggregate frequency-domain results

All values below are worst-case relative Frobenius errors (%) across the six configurations and ten frequencies. Transient columns in the next section are NRMSE percentages.

| Model | State reduction | Max Z vs NEURON | Max Y vs NEURON | Max Z vs Hines | Max Y vs Hines |
|---|---:|---:|---:|---:|---:|
| Four-shift order 56 control | 99.370–99.593% | 0.527304 | 0.404489 | 0.416133 | 0.432732 |
| Six-shift order 28 | 99.685–99.796% | 9.490221 | 8.453951 | 9.524511 | 8.392428 |
| Six-shift order 56 | 99.370–99.593% | 0.216765 | 0.211010 | 0.113574 | 0.124064 |
| Six-shift order 84 | 99.055–99.389% | 0.216299 | 0.119252 | 0.000296 | 0.000376 |

The order-28 model is not acceptable for the full 0.1–10 kHz band: the maximum direct-NEURON impedance/admittance errors exceed 9.49%/8.45%, despite removing the most states. Order 56 halves or better the worst direct-NEURON errors versus the four-shift control. Order 84 reduces the internal PRIMA-vs-Hines residual to below 0.0004% for both Z and Y, and improves worst direct-NEURON Y error to 0.1193%. Its worst direct-NEURON Z error (0.2163%) is nearly the same as order 56 (0.2168%), indicating that increasing order further primarily reduces the projection error against Hines rather than removing the remaining cross-simulator discrepancy.

The worst aggregate Z/Y errors occur at 10 kHz. The full per-frequency maxima are in [frequency summary CSV](../results/human_passive_prima_order_transient_frequency_summary_2026-11-22.csv).

## 4. Transient robustness across source locations and pulse widths

| Model | Worst all-port NRMSE | Worst individual-port NRMSE |
|---|---:|---:|
| Four-shift order 56 control | 0.0002864% | 0.0025174% |
| Six-shift order 28 | 0.416069% | 5.119891% |
| Six-shift order 56 | 0.0009012% | 0.0086914% |
| Six-shift order 84 | 0.00001835% | 0.0002290% |

Order 28 fails transient generalization, especially for short apical/soma pulses. Its worst single-port NRMSE reaches 5.12% at the apical-q90 probe. Order 56 remains numerically small in absolute terms, but its worst all-port and single-port transient errors are higher than the four-shift order-56 control. Order 84 is the best transient model in this test: its worst all-port NRMSE is about 49× lower than six-shift order 56 and its worst single-port error is about 38× lower.

The six-scenario summary shows the most difficult conditions are short 2 ms pulses; basal-q75 stimulation is generally easier than apical-q75 or soma stimulation. The apical-q90 probe is the recurring worst output port in the scenario-wise aggregation. This is a clear target for subsequent port-localized basis enrichment, not evidence of a biological hotspot by itself.

Detailed data: [scenario summary CSV](../results/human_passive_prima_order_transient_scenario_summary_2026-11-22.csv) and [per-configuration/model summary CSV](../results/human_passive_prima_order_transient_config_summary_2026-11-22.csv).

## 5. Numerical and software validation

- Schur/PRIMA workflow [44966510373](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373): 6/6 morphology × mesh jobs passed. Each job ran 111 tests and generated exactly 232 sweep rows.
- Core CI [44966510441](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510441): 4/4 jobs passed, including Python 3.12/3.13 test, compile/example and NEURON cross-validation jobs.
- Frequency-domain audit [44966510356](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510356): 3/3 jobs passed.
- All four reduced models per configuration passed Cholesky checks for their projected conductance and capacitance matrices; all retained-port ordering checks passed.
- Maximum observed NEURON port-impedance condition number: 91.263. No ill-conditioned matrix failure was reported.

## 6. Decision

1. **Reject six-shift order 28** as a general 0.1–10 kHz reduced model. The state reduction is greatest, but the frequency and transient errors are too large.
2. **Keep four-shift order 56 as the current default/control** where transient fidelity and a smaller state budget matter. It has the best transient result of the two order-56 alternatives in this particular protocol, but the worst 10 kHz frequency error is larger.
3. **Keep six-shift order 56 as an optional high-band compromise**. It materially improves 10 kHz Z/Y against NEURON but introduces a modest transient-error penalty versus the four-shift order-56 control.
4. **Promote six-shift order 84 as the preferred optional high-fidelity passive RC preset for this tested port set and frequency band**, not as the global default. It keeps 99.055–99.389% of the original states eliminated, reduces internal Hines projection residuals below 0.0004%, and produces the smallest transient errors. More retained states are required than at order 56.

No default solver or production behavior has been changed. The full Hines model remains canonical.

## 7. Reproducibility artifacts

Six per-configuration workflow artifacts contain raw port matrices, summaries, localization tables, order sweeps, transient rows and logs:

- [NMO_290988, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14732020626)
- [NMO_290988, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14731589116)
- [NMO_68174, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14732270037)
- [NMO_68174, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14731708587)
- [NMO_68175, mesh 0.125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14731039030)
- [NMO_68175, mesh 0.0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373/artifacts/14731429692)

## 8. Limits and next experiment

This remains validation of a passive linear RC subsystem at seven selected ports and three available morphology records. It does not validate active ion channels, nonlinear synapses, calcium dynamics, gene regulation, metabolism, plasticity, biological variability or cognition. The passive parameters are fixed numerical reference values rather than population-fitted distributions.

The next experiment should focus on the recurring apical-q90 error path: compare the existing seven-port basis with port-enriched alternatives, add additional apical/basal transfer ports, and test whether a locally enriched or adaptive Krylov basis reduces the apical transient residual without sacrificing soma/basal accuracy. Keep morphology-specific results separate; do not tune parameters to force simulator agreement.