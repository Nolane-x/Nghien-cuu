# Independent Wilbers K voltage-clamp replay — nine released mechanisms

**Date:** 23 November 2026  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, version 3.0  
**Empirical targets:** Figure 4 per-recording workbook audit (43 cells; 13 Human, 30 Mouse)  
**Status:** implementation and validation workflow added; numerical conclusions pending the GitHub Actions replay

## Purpose

PR #9 ranked released K variants using a 200-AP H_wide command. PR #10 independently audited the Figure 4 K voltage-clamp workbook. This phase combines those tracks by replaying every unchanged K MOD mechanism through the original independent K voltage-clamp protocols and comparing their output with Figure 4 per-cell target measurements.

This is not parameter optimization. All nine published MOD files are checksum-verified and compiled unchanged.

## Original protocol reproduction

The original \`channel_tools.py\` source is fetched by immutable Dataverse ID and checked against live official metadata. The runner imports that original Python module and directly uses its \`runIk\`, \`get_tau_act\`, \`get_tau_inact_double\`, \`fit_boltz_act\`, \`fit_boltz_inact\` and \`get_double_tau_rec\` functions. It fails closed if the source functions or protocol constants change.

### K_IV_ss

- Temperature: 34 °C
- Time step: 0.1 ms
- Cell setup copied from \`k_mech_IV\`: diameter 10 µm, Ra 200 Ω·cm, Cm 1 µF/cm², ek −101 mV; NEURON default section length is not overridden
- Command durations: 20 / 500 / 50 / 100 ms
- Command voltage sequence: −140 / Vtest / +60 / −140 mV
- Test voltages: −110 to +50 mV in 10 mV steps (17 voltages)
- Activation current window: 20.4–520 ms; conductance uses I/(Vtest−ek)
- Availability/inactivation window: 520–570 ms; conductance uses I/(+60−ek)
- Activation tau and fast/slow inactivation tau use the original source fit functions.
- Boltzmann activation is fit on the complete test-voltage grid; inactivation is fit on test voltages ≤0 mV, as in the source function.

### K_recovery_ss

- Temperature: 34 °C; time step: 0.5 ms
- Hold: −120 mV for 2 ms
- Conditioning pulse: +40 mV for 5,000 ms
- Recovery voltage: −80 mV
- Recovery intervals: \`np.linspace(2, 92, 10) ** 2\` ms
- Final test pulse: +40 mV for 5 ms
- Current peak: maximum of the current during the final 5-ms test pulse
- Fast/slow recovery tau: original \`get_double_tau_rec\` fit

The raw command and fit outputs are retained for every mechanism.

## Independent comparisons

The runner compares five voltage-indexed endpoints against per-recording Figure 4 targets: activation G/Gmax, inactivation G/Gmax, activation tau, fast inactivation tau and slow inactivation tau. It also compares model Boltzmann Vhalf fits and recovery fast/slow tau with per-cell cohort summaries.

Human and Mouse remain separate. Every curve comparison records the number of target cells at each voltage, mean, SD, SEM, model value and residual. Summary tables report MAE, RMSE, bias and descriptive overlap with pointwise mean ±1.96 SEM.

## Statistical and biological limits

The Figure 4 workbook contains derived per-recording measurements, not raw current time series. The audited workbook contains 13 Human cells nested within 2 subject identifiers and 30 Mouse cells nested within 7 subject identifiers. Cell-level means are descriptive; cells are not treated as 43 independent biological subjects.

No candidate is tuned against these Figure 4 targets in this phase. Missing/failed source fit outputs remain missing and are not interpolated to improve apparent agreement. Pointwise SEM overlap is not a formal inferential test. The earlier AP-clamp ranking is not used as a voltage-clamp target.

No original MOD, parameter default, or AMSN runtime setting is modified or promoted.

## Outputs

- \`results/wilbers_k_voltage_clamp_replay_2026-11-23.json\`
- \`results/wilbers_k_voltage_clamp_model_curves_2026-11-23.csv\`
- \`results/wilbers_k_voltage_clamp_per_voltage_comparison_2026-11-23.csv\`
- \`results/wilbers_k_voltage_clamp_summary_2026-11-23.csv\`

The workflow commits the full results to the research branch and uploads a run artifact.
