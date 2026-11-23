# Handoff — independent Wilbers K voltage-clamp replay

**Date:** 23 November 2026  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** \`research/wilbers-k-independent-voltage-clamp-replay-2026-11-23\`  
**Base:** PR #10 head \`research/wilbers-k-figure4-voltage-clamp-audit-2026-11-23\`

## Context

- PR #9: all nine released K MOD mechanisms replayed on the original 200-AP H_wide clamp command.
- PR #10: Figure 4 workbook and original plot/statistics scripts verified; 43 per-recording rows expanded into 3,732 voltage-indexed measurements.
- This branch: replay the nine unchanged K MOD sources under independent original K voltage-step and recovery protocols.

## Added

- \`amsn-core/examples/replay_wilbers_k_voltage_clamp.py\`
- \`amsn-core/tests/test_wilbers_k_voltage_clamp_replay.py\`
- \`.github/workflows/amsn-wilbers-k-independent-voltage-clamp-replay.yml\`
- \`amsn-core/research/WILBERS_2023_INDEPENDENT_K_VOLTAGE_CLAMP_REPLAY_2026-11-23.md\`

## Validation protocol

The runner downloads and verifies all nine K MOD files plus original \`channel_tools.py\` and \`channel_kinetics.py\`. It imports the original channel tools and directly calls its current recorder and fitting routines. The K-IV and recovery loops preserve the original voltages, durations, temperatures, timesteps, single-section setup, measurement windows and fit methods.

The workflow runs regression tests, jointly compiles the unchanged MOD sources, executes all nine models, compares curves with the audited Figure 4 per-cell data, commits outputs to the branch and uploads an artifact.

## Review after CI

1. Verify each source ID/byte-size/SHA-1 and the original protocol-source audit.
2. Confirm all nine models completed K_IV_ss and K_recovery_ss with finite conductance/current traces.
3. Inspect tau-fit missingness; do not treat source fit failures as zeros.
4. Review Human and Mouse comparisons separately and note the small subject counts (2 Human, 7 Mouse).
5. Report endpoint-specific results, not a single blended score.
6. Do not promote any hybrid or edit the MOD source/defaults from these results alone.

## Next gate

If one or more variants agree better on independent Figure 4 endpoints, validate that ranking on raw independent voltage-clamp traces or another released voltage-clamp dataset, check subject-level uncertainty, then evaluate current-clamp/morphology behavior. No mechanism is promoted to production in this branch.
