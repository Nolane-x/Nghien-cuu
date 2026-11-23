# Handoff — independent Wilbers Figure 4 K voltage-clamp target audit

**Date:** 23 November 2026  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** \`research/wilbers-k-figure4-voltage-clamp-audit-2026-11-23\`  
**Base:** \`research/wilbers-k-variant-apclamp-2026-11-23\`

## Context

PR #9 reproduced the original 200-AP H_wide AP-clamp command for all nine released K mechanisms. \`k_hybrid2\` ranked first in the two AP-clamp cohorts, but that is not independent biological validation. The original Figure 4 workbook contains separate voltage-clamp endpoints.

## Added

- \`amsn-core/examples/audit_wilbers_figure4_voltage_clamp.py\`
- \`amsn-core/tests/test_wilbers_figure4_voltage_clamp.py\`
- \`.github/workflows/amsn-wilbers-figure4-voltage-clamp-audit.yml\`
- \`amsn-core/research/WILBERS_2023_FIGURE4_INDEPENDENT_K_VOLTAGE_CLAMP_AUDIT_2026-11-23.md\`

On green CI the workflow commits:
- \`results/wilbers_figure4_voltage_clamp_audit_2026-11-23.json\`
- \`results/wilbers_figure4_voltage_clamp_per_recording_2026-11-23.csv\`
- \`results/wilbers_figure4_voltage_clamp_cohort_summary_2026-11-23.csv\`

## Scope

Verify the official Figure 4 workbook and original analysis sources, assert the per-cell data schema, reproduce quality filters, and convert the wide workbook into per-recording/per-voltage observations. The workbook contains derived measurements, not raw time-series traces. This phase does not simulate channel variants yet.

## Next model gate

Run the original released K voltage-step and recovery protocols using each unchanged MOD at 34 °C. Compare activation/inactivation curves, activation tau, fast/slow inactivation tau and recovery endpoints against the per-cell targets, retaining Human and Mouse separately. Keep the AP-clamp selection metric independent from this validation. Do not promote a hybrid to AMSN runtime based on the AP-clamp ranking alone.
