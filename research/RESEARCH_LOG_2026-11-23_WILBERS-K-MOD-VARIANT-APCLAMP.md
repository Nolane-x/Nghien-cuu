# Research log — Wilbers released K MOD AP-clamp variant replay

**Date:** 23 November 2026  
**Branch:** \`research/wilbers-k-variant-apclamp-2026-11-23\`

## Motivation

The latest preceding K MOD provenance audit passed 5/5 source/parser tests, verified all nine immutable Dataverse K mechanism files against official SHA-1 and byte-size metadata, and compiled all nine with NEURON 9.0.2. Its report explicitly left the full AP-clamp replay of released variants as the next research gate.

## Implementation checkpoint

Added \`amsn-core/examples/replay_wilbers_k_mod_variants.py\`, its focused regression tests and a pinned GitHub Actions workflow. The runner uses the original H_wide trace and K workbook, performs Dataverse integrity checks for every source, preserves each mechanism's declared SUFFIX and state structure, and executes the original 5-AP and 200-AP K helper routines.

The test design also requires the first five amplitudes from the 200-AP execution to agree with the separate original 5-AP execution for every mechanism. Model curves are AP1-normalized and compared with Human and Mouse recording cohorts separately. All outputs are machine-readable and include per-AP residuals.

## Validation

**Pending.** No numerical performance result, all-nine replay pass, or model promotion is claimed until the Actions run and uploaded artifacts have been checked.
