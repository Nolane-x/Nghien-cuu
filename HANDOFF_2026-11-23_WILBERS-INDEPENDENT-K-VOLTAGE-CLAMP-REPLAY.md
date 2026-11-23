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

## Validation result — passed

- GitHub Actions: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45180834231
- Tests: 9 passed
- Source integrity: 9/9 MODs plus both original helper scripts verified against official Dataverse metadata
- Compilation: 9/9 unchanged MODs compiled together under NEURON 9.0.2
- Replay: 9/9 completed original K_IV_ss and K_recovery_ss
- Outputs: 855 model curve rows, 945 per-voltage comparisons, 162 endpoint/cohort summaries
- Artifact: ID 14821441838; ZIP SHA-256 \`64ea571889de5ab0ffcf233fa8aab0a5ea42f53af6f50bc962f457b6191806e6\`
- Result JSON: \`amsn-core/results/wilbers_k_voltage_clamp_replay_2026-11-23.json\`

## Main findings

There is no single winning mechanism across all endpoints and both cohorts. Human activation G/Gmax and activation tau favor \`k_human_h1\`; Human inactivation G/Gmax and fast inactivation tau favor \`k_human\`; Human slow inactivation tau favors \`k_hybrid5\`. Mouse activation G/Gmax favors \`k_hybrid4\`, Mouse inactivation G/Gmax favors \`k_mouse\`, Mouse activation tau and inactivation Vhalf favor \`k_hybrid2\`, while fast/slow inactivation tau favor \`k_human_h1\` / \`k_hybrid5\`.

The AP-clamp winner \`k_hybrid2\` therefore does not generalize as a universal voltage-clamp winner. \`k_human_hm12inf\` is numerically identical to \`k_human\` under the tested K_IV and recovery commands; investigate before inferring general equivalence. Some slow tau fits approach source-defined parameter bounds, including \`k_human_h1\` recovery tau2 ≈1,000 ms at the 1,000-ms lower bound.

## Next step

Validate against raw voltage-clamp current traces where available, preserve subject nesting (13 Human cells / 2 subjects; 30 Mouse cells / 7 subjects), investigate exact-identical mechanisms and bound-limited fits, then proceed to current-clamp/morphology. No source MOD/default or production runtime is promoted.

## Review after CI

1. Verify each source ID/byte-size/SHA-1 and the original protocol-source audit.
2. Confirm all nine models completed K_IV_ss and K_recovery_ss with finite conductance/current traces.
3. Inspect tau-fit missingness; do not treat source fit failures as zeros.
4. Review Human and Mouse comparisons separately and note the small subject counts (2 Human, 7 Mouse).
5. Report endpoint-specific results, not a single blended score.
6. Do not promote any hybrid or edit the MOD source/defaults from these results alone.

## Next gate

If one or more variants agree better on independent Figure 4 endpoints, validate that ranking on raw independent voltage-clamp traces or another released voltage-clamp dataset, check subject-level uncertainty, then evaluate current-clamp/morphology behavior. No mechanism is promoted to production in this branch.
