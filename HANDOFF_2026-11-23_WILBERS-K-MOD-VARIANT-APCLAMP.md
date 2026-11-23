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

The previous source-provenance checkpoint verified nine released K mechanisms and compiled all nine independently, but explicitly stated that no released variant had yet been replayed against the original 200-AP H_wide command. This branch implements that exact next gate.

## Implementation

- Reuses the hash-verified Dataverse download helper, original AP-clamp helper, protocol slicing, workbook parser and list-backed recorder from \`replay_wilbers_apclamp.py\`.
- Verifies exact source-declared SUFFIX and records STATE/RANGE/parameter metadata for every mechanism.
- Compiles the nine unchanged K MOD payloads together, then separately instantiates each exact suffix.
- Runs the original five-AP helper for each mechanism before the recorder optimization, then the full 200-AP helper after optimization.
- Requires the first five amplitudes from the two runs to match within 1e-12.
- Compares AP1-normalized curves against the original K workbook's human-input columns for Human and Mouse recording cohorts separately.
- Produces machine-readable JSON, cohort summary CSV and per-AP residual CSV.
- No source MOD text, fitted defaults or AMSN runtime configuration is changed.

## Validation status

The GitHub Actions workflow is triggered by this branch's implementation commit. Until its run completes and the artifact is inspected, do not state that the variants were successfully replayed or quote performance numbers.

## Next actions after CI

1. Inspect the complete workflow run and all nine mechanism outcomes.
2. Inspect the JSON and CSV artifacts, especially finite AP coverage, the 5-AP/full-run prefix check, workbook cohort counts and the source SHA-1/SHA-256 manifest.
3. Add the actual measured results, failures and interpretation to the research report and research log.
4. Open a PR for review; do not merge into \`main\` automatically.
5. If a released mechanism looks promising, test it against original steady-state activation, inactivation and recovery protocols before considering a biological claim.
