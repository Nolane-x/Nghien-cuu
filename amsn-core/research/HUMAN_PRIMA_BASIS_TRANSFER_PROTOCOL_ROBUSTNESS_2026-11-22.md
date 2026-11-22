# Human PRIMA basis-transfer protocol robustness — validated result

**Date:** 2026-11-22 (Asia/Bangkok)
**Pull request:** #7 — Stress-test PRIMA basis transfer across passive parameters and source protocols
**GitHub Actions:** Run 44990898080 — success
**Experiment branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22

## Executive result

The three-morphology experiment completed with **3/3 GitHub Actions jobs successful**. Each job installed pinned NEURON 9.0.2, ran the full AMSN test suite, executed the parameter/protocol experiment and uploaded all three result CSVs.

The downloaded artifacts contain and pass exact coverage checks for:
- **81 model-audit rows**: 3 morphologies × 9 parameter scenarios × 3 model variants;
- **729 frequency rows**: 3 morphologies × 9 parameter scenarios × 3 model variants × 9 frequencies;
- **3,402 transient per-port rows**: 3 morphologies × 9 parameter scenarios × 3 model variants × 3 source sites × 2 pulse widths × 7 retained outputs.

All 81 reduced models have requested and achieved PRIMA order 56. All 81 pass Cholesky positive-definiteness checks on their reduced conductance and capacitance matrices. All error values are finite and nonnegative. The post-processing validator paired all **1,134** transient output conditions across the three models using morphology, parameter case, source, pulse width and exact SWC output-node ID.

The central finding is a trade-off, not a universal winner:

**Extending the fresh basis shifts from 3 kHz to 6/10 kHz sharply improves the 6–10 kHz frequency-domain residual, but worsens every matched transient per-port error in this experiment.** Therefore, the 10 kHz-extended basis should not replace the 3 kHz basis as a general-purpose passive model at order 56.

## Experiment design

Three model construction paths were held at the same requested and achieved order 56:

1. frozen_nominal_3khz_basis: build the nominal 0/100/1,000/3,000 Hz basis once, then reproject it onto each perturbed passive parameter set.
2. fresh_3khz_basis: rebuild a fresh basis for each parameter set using the same 0/100/1,000/3,000 Hz shifts.
3. fresh_extended_10khz_basis: rebuild at the same order using 0/100/1,000/3,000/6,000/10,000 Hz shifts.

The nine deterministic parameter scenarios were nominal, Rm ±20%, Cm ±20%, Ra ±20%, all parameters -20% and all parameters +20%. These are sensitivity tests, not measured distributions of human biological parameters.

Frequency-domain impedance and admittance matrices were compared against the matching perturbed full Hines cable tree at 0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz. The matrix relative L2 residual is reported as a percentage.

Transient protocols used current injections at soma, basal-q75 and apical-q75. Each source was tested with 2 ms and 10 ms square pulses (10 pA, 2 ms onset, 20 ms total simulation, dt=0.1 ms). All seven retained output nodes were recorded. The per-output NRMSE is the normalized L2 trace error against the matching full Hines trace.

Morphology fixtures:
- NMO_68174 cell1125 — 12,410 SWC records, 12,399 electrical compartments.
- NMO_68175 cell1204 — 13,758 SWC records, 13,747 electrical compartments.
- NMO_290988 / 1094_Mohan_etal_2015 — 8,903 SWC records, 8,893 electrical compartments. This is a partial dendritic reconstruction without an axon; it must not be labelled a healthy-control morphology.

## Frequency-domain result

At 6 kHz, the extended basis reduced median relative residuals over the 27 matched morphology/parameter cases:

| Metric | Fresh 3 kHz basis | Fresh extended basis | Median extended / 3 kHz |
|---|---:|---:|---:|
| Impedance Z | 0.067155% | 0.030436% | 0.4678× |
| Admittance Y | 0.108554% | 0.053839% | 0.5059× |

All 27 matched cases improved for both Z and Y at 6 kHz. The maximum Z/Y residuals also fell from 0.123624% / 0.147322% to 0.061997% / 0.064497%.

At 10 kHz the improvement was larger:

| Metric | Fresh 3 kHz basis | Fresh extended basis | Median extended / 3 kHz |
|---|---:|---:|---:|
| Impedance Z | 0.287371% | 0.081212% | 0.2927× |
| Admittance Y | 0.387441% | 0.121411% | 0.3124× |

Again, all 27 matched morphology/parameter cases improved for both Z and Y. Maximum Z/Y residuals fell from 0.458655% / 0.484503% to 0.142794% / 0.137265%.

However, the extended basis is not uniformly better across the spectrum. At 100, 300, 1,000 and 3,000 Hz its median Z and Y residuals were higher than those of the fresh 3 kHz basis. For example, at 3 kHz the median Z residual rose from 0.009914% to 0.012261%, while median Y rose from 0.021055% to 0.026407%. At 0.1–1 Hz the residuals are close to numerical precision for all fresh-basis variants.

This frequency dependence matters: the wider shift set reallocates the fixed 56-dimensional basis toward the high-frequency band, rather than providing a free improvement everywhere.

## Transient result

The transient comparison is exact-paired over 1,134 output conditions per model comparison.

| Comparison (numerator / denominator) | Matched outputs | Median error ratio | P90 ratio | Wins for numerator | Regressions for numerator |
|---|---:|---:|---:|---:|---:|
| Extended 10 kHz / fresh 3 kHz | 1,134 | 4.052× | 6.519× | 0 | 1,134 |
| Fresh 3 kHz / frozen 3 kHz | 1,134 | 1.000× | 1.824× | 488 | 520 |
| Extended 10 kHz / frozen 3 kHz | 1,134 | 3.785× | 7.269× | 0 | 1,134 |

No ties occurred in the extended-vs-fresh transient pairings. The smallest extended/fresh error ratio was 1.3717×; the largest was 29.50×. Thus the degradation is not an artefact of one morphology or one source: it occurs for every matched node, parameter scenario, source location and pulse width in this dataset.

Across all three morphologies, the maximum single-port transient NRMSE was:
- Frozen nominal 3 kHz: 0.004814%.
- Fresh 3 kHz: 0.008743%.
- Fresh extended 10 kHz: 0.026977%.

The fresh 3 kHz basis is not automatically superior to the frozen basis: it lowered the per-port error in 488 pairings, raised it in 520 and tied in 126. That is why basis reuse and fresh construction must remain separate comparison arms.

## Passivity and compression checks

Every model passed Cholesky positive-definiteness checks on both reduced conductance and capacitance matrices. This is evidence of the tested positive-definiteness property; it is not a proof of global passivity for all operating conditions, nor a substitute for response-error measurements.

All three model variants achieved a state reduction of:
- NMO_68174: 99.54835% (56 / 12,399 electrical states);
- NMO_68175: 99.59264% (56 / 13,747);
- NMO_290988: 99.37029% (56 / 8,893).

The same reduced order is compared across construction paths; the observed trade-off is caused by basis construction/shift selection, not by a change in retained order.

## Interpretation and decision

1. **Do not promote the 10 kHz-extended order-56 basis as a general-purpose replacement.** It is demonstrably better for the tested 6/10 kHz frequency-domain outputs but worse for every tested transient output.
2. **Keep the fresh 3 kHz and frozen nominal 3 kHz basis as separate candidates.** Their relative performance changes with morphology, parameter case and output; neither wins every transient pairing.
3. **Treat basis design as a multi-objective problem.** A model needs a declared target band and protocol. A high-frequency impedance use case can justify an extended basis, whereas transient waveform preservation in this experiment favours the 3 kHz constructions.
4. **Do not combine or switch bases in production yet.** A frequency-specialized or multi-basis evaluator is only a hypothesis until switching continuity, transient behavior, causality and interpolation are separately validated.
5. Keep full Hines canonical. Do not change defaults or infer active neuronal behavior from these passive linear RC results.

## Recommended next experiment

Run a constrained Pareto sweep that changes both basis order and shift distribution: orders 56, 84 and 112; 3 kHz-only, 6 kHz-extended, 10 kHz-extended and a deliberately balanced low/high-frequency shift set. Keep the same nine parameter scenarios, three sources, two pulse widths, all seven ports and full Hines references. Score every candidate jointly on:
- low/mid/high-band Z and Y residuals;
- transient per-port median, P90 and worst-case NRMSE;
- state count, CPU time and peak RSS.

Then repeat the best candidates on at least one held-out morphology. This should produce a Pareto frontier instead of selecting a basis from one metric.

## Reproducibility and provenance

The 3 GitHub Actions artifacts are listed with IDs, byte sizes, SHA-256 digests and expiry in human_prima_basis_transfer_artifact_manifest_2026-11-22.csv. The extracted CSV data were locally hash-verified against GitHub's artifact digests.

The standard-library analysis program is analyze_human_prima_basis_transfer_protocol_robustness.py. After downloading and extracting the three artifacts into an artifact directory, run:

    python analyze_human_prima_basis_transfer_protocol_robustness.py \
      --artifact-root ./extracted-actions-artifacts \
      --output-dir ./analysis-output

It validates exact model identity, order, scenario, frequency, source/pulse and seven-port coverage, then emits the model-audit, frequency, high-band, transient and paired-comparison summary CSVs.

The full run remains available at https://github.com/Nolane-x/Nghien-cuu/actions/runs/44990898080. Artifacts were retained by GitHub until 2027-02-20 05:47:17 UTC at the time of validation.

## Scientific limits

This is a passive, linear RC model-reduction study. It does not validate active Na/K/Ca channels, action-potential propagation, nonlinear AMPA/NMDA/GABA synapses, plasticity, calcium signaling, gene expression, metabolism, cognition or biological completeness. The three morphology fixtures do not represent a population sample. The Mohan2015 reconstruction is partial and lacks an axon. Parameter perturbations are deterministic stress cases, not biological confidence intervals.
