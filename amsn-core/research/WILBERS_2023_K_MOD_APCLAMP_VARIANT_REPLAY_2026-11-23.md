# Wilbers 2023 — replay of released potassium MOD variants on the original AP-clamp command

**Date:** 23 November 2026  
**Branch:** \`research/wilbers-k-variant-apclamp-2026-11-23\`  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, released version 3.0, CC0-1.0  
**Validation:** GitHub Actions execution is pending; no variant performance result is claimed in this initial implementation checkpoint.

## Research question

Do the nine released potassium mechanisms (canonical human and mouse sources, two named human variants, and five source-documented hybrid variants) reproduce the original 200-AP H_wide voltage-clamp response differently when driven by exactly the same command?

This is the next gate identified by the 23 November source-provenance audit. That audit established that all nine original K MOD files pass official Dataverse file-ID/SHA-1/byte-size checks and compile independently under NEURON 9.0.2, but it did not test their AP-clamp performance.

## Protocol

- Download the original H_wide trace, K recording workbook, AP-clamp helper and all nine K MOD files by immutable Dataverse file ID.
- Verify each downloaded payload against the pinned official Dataverse SHA-1 and exact byte size; record a fresh SHA-256.
- Parse each MOD source and require the declared NMODL SUFFIX to equal the requested mechanism name. Preserve its STATE, RANGE and parameter structure.
- Compile all nine unchanged MOD sources into one NEURON 9.0.2 mechanism library and load each source-declared SUFFIX separately.
- Replay the original first-five-AP window (199–307 ms, 13,501 samples) with the original helper recorder.
- Replay the complete first-200-AP window (199–5,182 ms, 622,876 samples; 125 kHz; dt 0.008 ms; 34 °C) using the already-tested list-backed current recorder. The potassium command has no liquid-junction offset.
- Require each 200-AP output to contain exactly 200 finite amplitudes and require its first five amplitudes to match the independent original five-AP replay within 1e-12.
- Normalize each model by its own AP1 amplitude and compare against the K workbook's human-input \`amp_h_n_\` columns. Keep Human and Mouse recording cohorts separate (14 and 11 recordings, respectively).
- Report MAE/RMSE over AP1–200 and separately over AP1–5, AP1–100 and AP101–200, as well as AP5/AP200 error and pointwise mean ±1.96 SEM overlap. The overlap count is descriptive, not a hypothesis test.

## Mechanisms in scope

| Mechanism | Source role |
|---|---|
| \`k_human\` | Canonical human potassium reference |
| \`k_mouse\` | Canonical mouse potassium comparator |
| \`k_human_h1\` | Released reduced-state human variant with m,h gates |
| \`k_human_hm12inf\` | Released human variant with m,m1,m2,h1,h2 gates |
| \`k_hybrid1\` | Human G/Gmax activation + inactivation |
| \`k_hybrid2\` | Human G/Gmax activation |
| \`k_hybrid3\` | Human G/Gmax inactivation |
| \`k_hybrid4\` | Human activation time constant |
| \`k_hybrid5\` | Human G/Gmax activation + activation time constant |

The five hybrid roles are read from the original \`channel_kinetics.py\` source annotations; they are not inferred from the AP-clamp comparison.

## Scientific boundaries

The existing K fit-provenance audit found that the original human CMA fitting vectors do **not** optimize \`prop_inact\`, \`prop_h2\`, \`h2tau_inact\`, \`h2tau_inact_rec\` or \`inact_rate_factor\`. The prior local sensitivity-grid minimum at \`prop_inact=0.99\`, \`h2tau_inact=112.5 ms\` was at both search boundaries and is not an identified biological parameter set. Released-source replay is a distinct test and must not be used to retroactively label that sensitivity point as an original fit.

A lower AP-clamp MAE on this one command does not establish parameter identifiability or agreement with independent voltage-clamp activation, inactivation and recovery protocols. The deterministic single-compartment model is not a complete human neuron. No mechanism source, canonical parameter default, AMSN runtime or production setting is modified or promoted by this experiment.

## Outputs

The workflow writes:
- \`results/wilbers_k_mod_variant_apclamp_200_2026-11-23.json\` — exact protocol, source hashes, gate metadata, full amplitudes, comparisons and interpretation limits.
- \`results/wilbers_k_mod_variant_apclamp_summary_2026-11-23.csv\` — one row per mechanism and recording cohort.
- \`results/wilbers_k_mod_variant_apclamp_per_ap_2026-11-23.csv\` — complete 200-point curve, workbook mean/SD/SEM and residual for every mechanism/cohort.

The raw outputs are also uploaded as the GitHub Actions artifact \`wilbers-released-k-mod-variant-apclamp-replay\`. Numerical conclusions will be added only after the workflow and artifacts are inspected.
