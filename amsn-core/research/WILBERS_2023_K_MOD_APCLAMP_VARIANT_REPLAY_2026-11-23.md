# Wilbers 2023 — replay of released potassium MOD variants on the original AP-clamp command

**Date:** 23 November 2026  
**Branch:** \`research/wilbers-k-variant-apclamp-2026-11-23\`  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, released version 3.0, CC0-1.0  
**Validation:** passed — 30 tests and all nine original K MOD variants reproduced on the original 200-AP H_wide command.

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
- Require each 200-AP output to contain exactly 200 finite amplitudes. For each mechanism, run the same original five-AP helper before and after the current-recorder replacement and require identical outputs within 1e-12. Keep the distinct 5-AP and 200-AP helper outputs side by side as a diagnostic; do not assume the two source routines produce equal amplitudes.
- Normalize each model by its own AP1 amplitude and compare against the K workbook's human-input \`amp_h_n_\` columns. Keep Human and Mouse recording cohorts separate (14 and 11 recordings, respectively).
- Report MAE/RMSE over AP1–200 and separately over AP1–5, AP1–100 and AP101–200, as well as AP5/AP200 error and pointwise mean ±1.96 SEM overlap. The overlap count is descriptive, not a hypothesis test. The source's five-AP and 200-AP helpers are separate procedures; only same-helper recorder equivalence is an acceptance gate.

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


## Validated results — GitHub Actions run 45170480109

**Status:** passed on 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45170480109  
**Artifact:** \`wilbers-released-k-mod-variant-apclamp-replay\`, ID \`14817955509\`  
**Artifact ZIP SHA-256:** \`45e1287889191a03b2a31de50fab67be7b2dd9a90f3dfc2fcacadf70cd83312d\`  
**Commit under test:** \`9242a7d411b5f6b5b2d4faeb0993d20d42b50d31\`

The full workflow completed successfully: **30 tests passed**, all nine source MOD files matched the pinned Dataverse ID/size/SHA-1 manifest, all nine compiled together under NEURON 9.0.2, and all nine completed the 200-AP replay. Each output had exactly 200 finite amplitudes and zero non-finite values. The same original \`Ik_AP1_5\` helper produced exactly identical amplitudes before and after the list-backed recorder replacement for all nine mechanisms (maximum absolute difference 0; tolerance 1e-12).

The original H_wide command window contained 622,876 samples and 200 detected AP command peaks (199–5,182 ms, 125 kHz, dt=0.008 ms, 34 °C). The first-five-AP control window contained 13,501 samples and five peaks. The original 5-AP and 200-AP helper functions are distinct source procedures; their prefix differences are retained as diagnostics, not treated as a model failure.

### Ranking by AP1-normalized MAE across AP1–200

| Released mechanism | Human recordings (n=14) | Mouse recordings (n=11) | Source role |
|---|---:|---:|---|
| \`k_hybrid2\` | **0.189698** | **0.280801** | Human G/Gmax activation |
| \`k_hybrid5\` | 0.189957 | 0.281061 | Human G/Gmax activation + activation time constant |
| \`k_hybrid4\` | 0.194284 | 0.285388 | Human activation time constant |
| \`k_mouse\` | 0.194580 | 0.285684 | Canonical mouse K |
| \`k_hybrid1\` | 0.241609 | 0.332713 | Human G/Gmax activation + inactivation |
| \`k_human\` | 0.241916 | 0.333020 | Canonical human K |
| \`k_human_hm12inf\` | 0.241916 | 0.333020 | Human multi-state m/m1/m2/h1/h2 |
| \`k_hybrid3\` | 0.246885 | 0.337989 | Human G/Gmax inactivation |
| \`k_human_h1\` | 0.266970 | 0.358074 | Reduced-state human m/h mechanism |

The same ranking is obtained for the Mouse cohort. Relative to canonical \`k_human\`, \`k_hybrid2\` reduces full-train MAE by **21.6%** for Human recordings and **15.7%** for Mouse recordings; RMSE falls by 21.6% and 15.3%, respectively. Its AP101–200 MAE is also lower by 21.4% (Human) and 14.2% (Mouse), so the gain is not limited to the first few spikes.

\`k_hybrid5\` is very close to \`k_hybrid2\` (MAE difference approximately 0.00026 in each cohort); this difference is descriptive and has not been established as statistically meaningful. \`k_human_hm12inf\` produced an exactly identical 200-point amplitude trajectory to \`k_human\` under this particular command and initialization. That observation must be checked against the original equations and independent voltage-clamp protocols before inferring anything about general mechanism equivalence.

### What remains wrong

The lower-error variants still overpredict late potassium current. At AP200, \`k_hybrid2\` predicts 0.621744 versus the Human recording mean 0.427450 (absolute excess +0.194293; 45.5% above the mean). For Mouse recordings it predicts 0.621744 versus 0.273621 (excess +0.348123; 127.2% above the mean). The canonical \`k_human\` AP200 excess is +0.247521 for Human and +0.401351 for Mouse.

Only **1 of 200 AP points** falls within the pointwise mean ±1.96 SEM band for every tested mechanism/cohort pair. This is a descriptive overlap count, not a formal test, but it makes clear that the relative ranking does not constitute a good absolute fit. No released hybrid is promoted to the production AMSN model.

### Interpretation and next gate

The released human-activation hybrid is the best AP-clamp candidate in this comparison, while the inactivation-focused \`k_hybrid3\` and reduced-state \`k_human_h1\` perform worse on the full train. The next validation must use independent source voltage-clamp evidence: steady-state activation, steady-state inactivation, activation kinetics, inactivation kinetics and recovery. It must retain the original stimulus protocol and per-cell observations and avoid reusing the same AP-clamp cohort as both selection and validation. The original human CMA fitting vectors do not identify the slow mixture parameters, so no fitted-parameter or biological-identifiability claim follows from this ranking.

### Durable result files

- \`results/wilbers_k_mod_variant_apclamp_200_2026-11-23.json\` — full machine-readable source, runtime, protocol, model curves, comparison and helper-equivalence evidence.
- \`results/wilbers_k_mod_variant_apclamp_summary_2026-11-23.csv\` — 18 mechanism × cohort summary rows.
- \`results/wilbers_k_mod_variant_apclamp_per_ap_2026-11-23.csv\` — 3,600 rows with model output, cohort mean/SD/SEM and residual per AP.
