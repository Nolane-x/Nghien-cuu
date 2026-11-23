# Handoff — Wilbers released K MOD variant AP-clamp replay

**Date:** 23 November 2026  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** \`research/wilbers-k-variant-apclamp-2026-11-23\`  
**Base commit:** \`66ec185c5342d561186e52ef78b518d281972a32\`

## Read first

1. \`amsn-core/research/WILBERS_2023_K_MOD_VARIANT_PROVENANCE_AUDIT_2026-11-23.md\`
2. \`amsn-core/research/WILBERS_2023_K_MOD_APCLAMP_VARIANT_REPLAY_2026-11-23.md\`
3. \`amsn-core/research/references/wilbers2023_k_mod_variant_audit_2026-11-23.json\`
4. \`HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md\`

## Why this branch exists

The previous source-provenance checkpoint verified nine released K mechanisms and compiled all nine independently, but explicitly left replay against the original 200-AP H_wide command as an uncompleted validation gate. This branch implements and validates that gate.

## Implementation

- Reuses the hash-verified Dataverse download helper, original AP-clamp helper, protocol slicing, workbook parser and list-backed recorder from \`replay_wilbers_apclamp.py\`.
- Verifies exact source-declared SUFFIX and records STATE/RANGE/parameter metadata for every mechanism.
- Compiles the nine unchanged K MOD payloads together, then separately instantiates each exact suffix.
- Runs the original five-AP helper before and after recorder replacement for every source mechanism and requires identical outputs within 1e-12.
- Records the difference between the distinct five-AP and 200-AP source helper outputs descriptively; does not incorrectly assert that the two separate routines must match.
- Compares AP1-normalized curves against the original K workbook's human-input columns for Human and Mouse recording cohorts separately.
- Produces the complete JSON result, cohort summary CSV and per-AP residual CSV.
- No source MOD text, fitted defaults or AMSN runtime configuration is changed.

## Validation result

**PASSED — GitHub Actions**

- Run: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45170480109
- Artifact: \`wilbers-released-k-mod-variant-apclamp-replay\` (ID \`14817955509\`)
- Tests: 30 passed
- Source integrity: all nine immutable Dataverse MOD file ID, byte-size and SHA-1 pins matched
- Compilation: 9/9 K MOD sources compiled together on NEURON 9.0.2
- Replay: 9/9 mechanisms returned 200 finite AP amplitudes
- Recorder control: 9/9 same-helper comparisons exact (max absolute difference 0)
- Evidence tables: 18 cohort summary rows and 3,600 AP-level residual rows

The best full-train AP-clamp MAE was \`k_hybrid2\` for both cohorts: 0.189698 (Human, n=14) and 0.280801 (Mouse, n=11). This is a relative ranking, not a validated biological model. AP200 current remains above recording means (+0.194293 Human; +0.348123 Mouse), and only 1/200 points falls inside the pointwise mean ±1.96 SEM band for every tested mechanism/cohort pair. No variant is promoted to runtime.

## Next research gate — independent K voltage-clamp validation

1. Inspect the original Wilbers \`channel_kinetics.py\`, \`channel_tools.py\` and \`fit_k_hh_cma_human.py\` protocols and source workbook data.
2. Reconstruct independent steady-state activation and inactivation curves from the released source data; preserve individual recording identity and the original voltage steps.
3. Reproduce activation and inactivation time constants and recovery kinetics using the original source fitting routines or a validated equivalent.
4. Evaluate \`k_hybrid2\`, \`k_hybrid5\`, \`k_hybrid4\`, canonical \`k_human\` and \`k_mouse\` against those independent targets. Do not select and validate on the same AP-clamp metric.
5. Investigate why \`k_human_hm12inf\` and \`k_human\` give exactly identical amplitude trajectories under this one AP-clamp protocol despite different declared gate structures.
6. Only after independent voltage-clamp reproduction, morphology/current-clamp evaluation and uncertainty analysis should any candidate be considered for a model-level decision.

## Pull-request scope

The feature branch is intended to target \`research/wilbers-human-active-channel-baseline-2026-11-22\`, not \`main\`: comparing against \`main\` would drag 76 prior research commits and 85 files into this focused PR. Do not merge this work into \`main\` automatically.
