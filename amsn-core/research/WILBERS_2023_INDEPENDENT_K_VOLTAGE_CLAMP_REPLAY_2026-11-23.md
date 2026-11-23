# Independent Wilbers K voltage-clamp replay — nine released mechanisms

**Date:** 23 November 2026  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, version 3.0  
**Empirical targets:** Figure 4 per-recording workbook audit (43 cells; 13 Human, 30 Mouse)  
**Status:** validated — all nine released K mechanisms replayed under original K-IV and recovery protocols

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


## Validated results — GitHub Actions run 45180834231

**Status:** passed 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45180834231  
**Artifact:** \`wilbers-independent-k-voltage-clamp-replay\`, ID \`14821441838\`  
**Artifact ZIP SHA-256:** \`64ea571889de5ab0ffcf233fa8aab0a5ea42f53af6f50bc962f457b6191806e6\`  
**Runtime:** Python 3.12.16, NEURON 9.0.2, NumPy 2.2.5, pandas 2.2.3

The workflow passed **9/9 tests**, verified the immutable Dataverse file IDs, byte sizes and SHA-1 values for all nine K MODs and both original source scripts, compiled the nine unchanged MOD files together, and completed both original protocols for **9/9 mechanisms**. No parameter optimization or source MOD modification occurred.

The original source helpers were verified:
- \`channel_tools.py\`: Dataverse ID 326242, 35,609 bytes, SHA-1 \`615595a270c6170987757cd35743f5d5b5b2af0e\`
- \`channel_kinetics.py\`: Dataverse ID 326241, 2,482 bytes, SHA-1 \`a462fc4f9c725150c1bc83a9cf21c535d67c451f\`

The run archived **855 model-curve rows**, **945 per-voltage comparisons**, and **162 endpoint/cohort summaries**. Each K-IV replay includes 17 test voltages; each recovery replay includes the original 10 recovery delays.

### Endpoint-specific leaders

The table shows the lowest descriptive MAE for each voltage-indexed endpoint. Point counts in parentheses are model points within the pointwise target mean ±1.96 SEM; they are not inferential tests.

| Endpoint | Human cohort | Mouse cohort |
|---|---|---|
| Activation G/Gmax | \`k_human_h1\`: MAE 0.01003; 11/12 points | \`k_hybrid4\`: MAE 0.02076; 6/12 points |
| Inactivation G/Gmax | \`k_human\` / \`k_human_hm12inf\`: MAE 0.01242; 15/17 | \`k_mouse\`: MAE 0.02987; 7/17 |
| Activation tau | \`k_human_h1\`: MAE 0.04014 ms; 7/7 | \`k_hybrid2\`: MAE 0.45084 ms; 2/7 |
| Fast inactivation tau | \`k_human\`: MAE 9.227 ms; 6/7 | \`k_human_h1\`: MAE 11.814 ms; 8/8 |
| Slow inactivation tau | \`k_hybrid5\`: MAE 189.312 ms; 4/9 | \`k_hybrid5\`: MAE 148.356 ms; 6/9 |

The scalar-fit and recovery comparisons show the same endpoint dependence:

| Endpoint | Human cohort | Mouse cohort |
|---|---|---|
| Activation Vhalf | \`k_hybrid5\`: −3.054 vs target −3.032 mV (n=13) | \`k_mouse\`: −7.892 vs −7.913 mV (n=29) |
| Inactivation Vhalf | \`k_hybrid1\`: −51.539 vs −52.686 mV (n=11) | \`k_hybrid2\`: −62.418 vs −65.027 mV (n=26) |
| Fast recovery tau | \`k_human_h1\`: 236.902 vs 254.540 ms (n=12) | \`k_human_h1\`: 236.902 vs 315.314 ms (n=14) |
| Slow recovery tau | \`k_hybrid3\`: 2,790.349 vs 2,483.909 ms (n=11) | \`k_hybrid5\`: 2,799.290 vs 3,079.748 ms (n=10) |

### Interpretation

There is **no single best mechanism across all endpoints and both cohorts**. The prior AP-clamp winner \`k_hybrid2\` is not a universal voltage-clamp winner: it ranks first for Mouse activation tau and Mouse inactivation Vhalf, but it is weak for Human activation tau and does not lead the other curve endpoints. Human activation and inactivation targets are generally better represented by canonical/reduced-state human variants; Mouse endpoints often favor the mouse or selected hybrid variants.

\`k_human_hm12inf\` produced exactly the same K-IV curves, fitted values and recovery outputs as \`k_human\` under these two protocols and this initialization. This is a reproducible observation for the tested commands only; it does not prove the two channel mechanisms are generally equivalent. The extra gate structure and its state initialization require separate source-equation and alternate-protocol investigation.

Some fitted slow inactivation values approach the original \`get_tau_inact_double\` bounds (300–1,000 ms). The \`k_human_h1\` recovery slow-tau fit is 1,000.006 ms, essentially at the original recovery fit's 1,000-ms lower bound. These near-boundary estimates are weakly identified and must not be over-interpreted.

The workbook contains 13 Human cells from 2 subject identifiers and 30 Mouse cells from 7 subject identifiers. Cell-level comparisons are descriptive, not 43 independent subject-level biological replicates. No candidate is promoted to the AMSN runtime.

### Next validation gate

1. Reproduce the independent voltage-step comparisons from raw current traces, if the released raw traces can be accessed; the Figure 4 workbook itself contains derived fit measurements, not raw time series.
2. Repeat the model/target comparison at subject-level or with a hierarchical model that preserves cells nested within subjects.
3. Investigate the exact \`k_human\` / \`k_human_hm12inf\` output identity and the source-bound slow-tau fits.
4. Run current-clamp and morphology-level validation only after the endpoint-specific voltage-clamp discrepancies are understood.
