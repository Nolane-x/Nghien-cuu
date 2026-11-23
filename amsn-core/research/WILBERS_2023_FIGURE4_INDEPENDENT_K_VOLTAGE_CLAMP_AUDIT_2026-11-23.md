# Wilbers 2023 Figure 4 — independent K voltage-clamp target audit

**Date:** 23 November 2026  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, released v3, CC0-1.0  
**Workbook:** \`Figure4/data_fig4.xlsx\`, ID 318667, 108,029 bytes, SHA-1 \`30ba48520d8d27a7f4db8aaa6abc7ae0f80ba7d3\`  
**Plot script:** \`Figure4/plots_fig4.py\`, ID 318536, 5,373 bytes, SHA-1 \`f9c4e70aba0760d00bb2ae911554c5e262fe8a7a\`  
**Statistics script:** \`Figure4/stats_fig4.py\`, ID 318535; official metadata/checksum are captured at runtime

## Why this is the next gate

The preceding 200-AP H_wide experiment ranked \`k_hybrid2\` first on AP1-normalized MAE in both AP-clamp cohorts. That result is relative to one AP-clamp command and does not establish biological validity. The original study provides separate Figure 4 voltage-clamp measurements for K activation, inactivation, activation/inactivation kinetics and recovery.

This branch makes those independent per-recording targets reproducible before evaluating the nine MOD variants under voltage-step protocols.

## Source provenance

The public workbook and plot script are pinned to immutable released Dataverse metadata. The statistics script is downloaded by immutable file ID and verified against official Dataverse metadata; its byte count, SHA-1 and SHA-256 are retained in the run report.

A source-path inconsistency is preserved rather than silently "fixed": released Figure 4 scripts locally reference \`Data/data_fig5.xlsx\`, while the public Figure 4 directory contains \`data_fig4.xlsx\`. The audit uses the immutable public workbook ID 318667 and validates its exact schema.

At runtime the script verifies the original source rules:
- Vhalf activation: \`gof_boltz_act > 0.9\`
- Vhalf inactivation: \`gof_boltz_inact > 0.9\`
- Activation tau: \`volt_act >= -10 mV\` and \`gof_act > 0.8\`
- Fast/slow inactivation tau statistics: all nonmissing values in the released statistics script; fast-tau plot only at \`volt >= 0 mV\`
- Recovery selection: \`K_IKrecv2_1_h0_DA_0\`

## What is retained

The workbook is wide-per-cell. The runner expands it to long form while preserving Filename and Species:
- Activation G/Gmax and activation time constant by voltage
- Steady-state inactivation G/Gmax by prepulse voltage
- Fast and slow inactivation time constants by voltage
- Fast, slow and steady inactivation fractions
- Recovery fraction by interpulse delay for the specified protocol
- Per-recording Vhalf, slope factor, fit-quality and recovery parameters

Human and Mouse remain separate. Cohort summaries include observed N, N retained by the authors' filters, exclusions, missingness, mean, SD, SEM, median and quartiles. The original filename-based subject count convention is retained.

## Scientific boundaries

This is a derived per-recording fit/measurement workbook, not raw voltage/current time-series traces. It cannot substitute for a full raw-trace fitting reproduction.

This phase audits experimental targets. It does not yet execute the nine K MOD equations under independent voltage steps. The next gate must run the original K voltage-step and recovery protocols at 34 °C, fit the same response quantities and compare model curves with these per-cell observations. AP-clamp MAE must not be reused as the independent validation score.

No original MOD, canonical parameters, AP-clamp output or AMSN runtime is modified.

## Outputs

- \`results/wilbers_figure4_voltage_clamp_audit_2026-11-23.json\`
- \`results/wilbers_figure4_voltage_clamp_per_recording_2026-11-23.csv\`
- \`results/wilbers_figure4_voltage_clamp_cohort_summary_2026-11-23.csv\`

The workflow commits the outputs to this research branch and uploads the full audit artifact.
