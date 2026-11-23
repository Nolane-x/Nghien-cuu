# Research log — human somatic NaV/KV evidence baseline

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Base:** `7655389b9d95dc85a54f81185a037ab026e32300`  
**Status:** literature audit and data-registry implementation; no active-channel simulation run.

## Question and hypothesis

The passive AMSN core is already numerically grounded, while the existing HH smoke test is a squid-axon model. The next biological gap is an evidence-based human cortical active-channel baseline. The hypothesis is that published somatic channel measurements and existing human L2/3 model estimates can provide useful constraints, but only if measurement, model fit and compartment-specific inference are represented as distinct evidence classes.

## Sources examined

- Wilbers et al. 2023, *Science Advances* 9, eade3300, DOI 10.1126/sciadv.ade3300.
- Wilbers thesis appendix, Tables S1-S3, for detailed mean/SD and model parameter tables.
- VU Research Portal DataverseNL record, DOI 10.34894/L5J0SD.
- Eyal et al. 2018, *Frontiers in Cellular Neuroscience* 12:181, DOI 10.3389/fncel.2018.00181.
- Existing AMSN source: `amsn-core/src/amsn/hh.py`, `cable.py`, `synapses.py`.
- Existing source audits: `FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md` and `EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md`.

## Main source observations

1. Wilbers et al. directly measured isolated voltage-gated Na+ and K+ currents in somatic nucleated patches. Main-article mean +/- SEM conductance densities are 5.9 +/- 0.8 pS/um^2 for Na+ (n=17) and 31.2 +/- 4.2 pS/um^2 for K+ (n=13).
2. The paper describes human-specific voltage dependence and kinetics: Na+ activation/inactivation curves shift toward depolarized voltages, activation and inactivation are slower, and recovery from inactivation is faster. K+ steady-state curves are also right-shifted; at lower voltages the measured K+ activation was faster, while recovery time constants were similar and recovery amplitude was larger in human.
3. The study's fitted single-compartment HH AP model uses gbarNa=114.5 and gbarK=29.05 pS/um^2. These are model parameters, not patch measurements. The paper explicitly notes that the sodium density needed for the single-compartment AP model exceeds the somatic patch density.
4. Eyal et al. 2018 model six human L2/L3 pyramidal cells with about 900 recorded spikes and multi-objective optimization. Their reported axonal/somatic channel densities are model estimates and assume rodent-like channel kinetics. Direct human dendritic channel recordings were unavailable in that paper.
5. The Wilbers data record is published at DataverseNL DOI 10.34894/L5J0SD, but the archive files could not be retrieved through the accessible landing page in this checkpoint.

## Implementation performed

- Added a provenance-aware JSON evidence registry separating measured somatic patch data, fitted single-compartment parameters and Eyal 2018 compartment-specific model estimates.
- Preserved raw reported means and uncertainty types, plus SI conversions.
- Captured sample counts, experimental region, channel recording temperature nuance, liquid-junction-potential caveat and the unknown dendritic/AIS mapping.
- Added tests that validate JSON structure, evidence labels, unit conversions, sample counts and the guard against runtime use.
- Added a human-readable research report and handoff.
- Updated the top-level handoff pointer without modifying the existing PR #8 branch.

## Validation status

- The JSON was parsed and its unit/evidence fields were programmatically checked before commit.
- The new pytest file has **not** been executed in this checkpoint.
- No Python active-channel solver was added or executed.
- No raw Wilbers Dataverse files or Eyal ModelDB archive bytes were obtained, hashed or replayed.
- No conductance values were assigned to AMSN runtime parameters.
- Existing CI runs on PR #8 remain queued at the last inspection; see the handoff for exact IDs.

## Limitations

- Wilbers conductance measurements are from somatic nucleated patches, not the AIS or axon.
- The cohort consists of neurosurgical human tissue; source context includes deeper pathology and cortical regions. It is not a population-wide healthy control reference.
- The voltage-dependence table is uncorrected for a 15 mV liquid-junction potential.
- The Table S1 slope-factor unit label in the thesis extraction is dimensionally suspect, so slope factors are not marked runtime-ready.
- The Wilbers single-compartment HH gbar values and Eyal compartment-specific densities are model-derived, not direct measurements.
- The original model equations and raw data must be retrieved and reproduced before implementation.

## Files added

- `amsn-core/research/references/human_nav_kv_evidence_2023.json`
- `amsn-core/research/HUMAN_SOMATIC_NAV_KV_EVIDENCE_BASELINE_2026-11-22.md`
- `amsn-core/tests/test_human_channel_evidence_registry.py`
- `HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md`

## Next concrete experiment

Retrieve and hash the Wilbers DataverseNL archive; reconstruct the original human Na+ and K+ equations and reproduce the published voltage-clamp command protocols before building a separate opt-in human somatic channel mechanism. Only after single-cell traces and channel kinetics pass should an independently justified spatial distribution be explored.


## Dataverse v3 / original NMODL source audit — 22/11/2026

- Official DataverseNL API verified DOI 10.34894/L5J0SD, released v3.0, CC0-1.0, 65 files.
- Selected Na/K mechanisms, human fitting drivers and supporting Python tools were read from public object-store downloads and SHA-256 hashed. The file manifest records IDs, bytes, official SHA-1 and observed SHA-256.
- Na mechanism: m/h states, m^3h conductance, 25 C reference, Q10=2.3, active TABLE lookup. Its script's final parameter dictionary agrees with distributed MOD.
- K mechanism: m/h1/h2 states, mixed fast/slow/non-inactivating populations, 34 C reference, Q10=2.3. Intermediate fit values match the MOD, but the later final-best-fit dictionary differs on six inactivation parameters; no snapshot is selected.
- Separate current-clamp MOD variants add human-fraction conductance scaling; they are not byte-identical to the channel-comparison files.
- Current-clamp gbar fitting uses a 50:50 human/mouse median AP target; it is not a human-only fit. K recovery fitting also uses a human/mouse average target.
- Both canonical MOD files contain a potential trap0 branch/limit mismatch. This is a source-level warning, not yet a proven NEURON failure.
- Raw spreadsheets and the 15.1 MB AP-clamp matrix were not downloaded. Selected source files were not vendored. Original mechanisms not compiled or executed; no pytest run is claimed; no runtime mechanism or default changed.

Files added:
- `amsn-core/research/references/wilbers2023_dataverse_source_manifest_2026-11-22.json`
- `amsn-core/research/references/wilbers2023_nmodl_mechanism_audit_2026-11-22.json`
- `amsn-core/research/WILBERS_2023_DATAVERSE_AND_NMODL_SOURCE_AUDIT_2026-11-22.md`

Next gate: compile original MOD files with pinned NEURON, probe trap0 around singular points, reproduce voltage clamp and AP-clamp traces, and resolve the K fit snapshot before implementing a distinct opt-in human somatic channel.


## Extended NMODL stable-reference comparison — 23/11/2026

- Workflow 45115543259 passed with 11 registry tests. The audit compiled unchanged source and a separate diagnostic clone with mathematically stable trap0 handling.
- Na: no non-finite values on 41 probe points; all fields matched the diagnostic clone at exported precision.
- K: three non-finite values at positive singular parameters; negative h1tau in the mirror region around -thi1 and at -thi2; 91.61% mtau discrepancy at -tha's mirror voltage.
- On 19 discrete Na and 17 discrete K command test-step voltages, original and diagnostic clone outputs matched at exported precision; this is only static initialization of rate variables, not a time-domain voltage-clamp or AP-clamp replay.
- No stable clone was promoted into runtime; raw workbooks/traces remain to be replayed.


## Figure 2 raw workbook analysis gate — 23/11/2026

Added a reproducible audit for the original Na/K Figure 2 workbooks and the Dataverse plotting/statistics scripts. The workbooks were downloaded in a research session and their official Dataverse SHA-1 and independent SHA-256 values were verified:

- Na workbook, file ID 318668, 548,562 bytes, SHA-1 `cd702d7f1ca65b0b88a2565f289740546902e36b`, SHA-256 `2fac600523d596a4dccbe167d3283b2e506dfdb9c7b1caef2a490c2c5dff184a`. It contains 49 recordings and 4 × 200 normalized AP-amplitude groups.
- K workbook, file ID 318669, 302,011 bytes, SHA-1 `287720f8db3b20b167edd9e639dd67b0a1194def`, SHA-256 `f00714c534c9658b8c07d2a473d39b2fd5a99c392e6e2ab50fb52fbb3b6ca74d`. It contains 25 recordings, explicit H/M species labels, and 201 raw/normalized AP measurements for human and mouse waveform inputs.

Source script `Figure2/plots_fig2.py` assigns Na recording species by filename prefix (M = Mouse, otherwise Human), uses Hnarrow for the main Na Figure 2 curve, and uses Hwide/Mwide for the supplementary waveform comparison. The Na workbook variables sheet gives duplicate descriptions for Mwide and Hwide; the new audit preserves raw labels and flags the discrepancy rather than silently fixing it. K workbook explicitly separates cell species and input waveform.

A GitHub Actions workflow has been added to verify Dataverse metadata SHA-1, raw SHA-256, parse the original workbooks and output descriptive per-recording normalized-amplitude curves. It deliberately does not generate inferential p-values or claim complete trace replay. First Actions result is pending. The larger 15.1 MB AP-clamp H_wide.csv trace file remains not downloaded.


## Verified Figure 2 workbook analysis — 23/11/2026

GitHub Actions run [45116703439](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439) passed, including the four parser/statistics-helper tests and the 11 existing provenance tests. It fetched and verified the original Na/K workbooks, plus the original Figure 2 plotting and statistics scripts. The workbook artifact [14791708917](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439/artifacts/14791708917) has SHA-256 `2b6ecc549d07b498e3e6122f8677c0da4a3abad2134f752b41ce4e7146900432`.

### Na current adaptation

The Na workbook has 49 recordings; the original plotting script classifies filenames beginning with `M` as mouse and all others as human, yielding 16 human and 33 mouse recordings. It contains 200 normalized AP-amplitude values for each of four raw APwave groups. The source plotting script uses `Hnarrow` for the main Figure 2 curve and `Hwide`/`Mwide` for its supplementary waveform comparison.

For the main `Hnarrow` group, mean normalized Na current amplitude was:

| Recording species | AP5 | AP200 |
|---|---:|---:|
| Human (n=16) | 0.7745 ± 0.0985 SD | 0.7487 ± 0.1211 SD |
| Mouse (n=33) | 0.5244 ± 0.1093 SD | 0.5167 ± 0.0883 SD |

The other raw waveform groups are retained separately in [the summary CSV](../results/wilbers_figure2_apclamp_normalized_summary_2026-11-23.csv); none are renamed or merged. The Na workbook's `variables` sheet gives both `Mwide` and `Hwide` the description "Human waveform 2", while the plotting script treats them as distinct APwave groups. This metadata discrepancy remains open and is explicitly flagged.

### K current adaptation

The K workbook has 25 recordings with explicit species labels: 14 human, 11 mouse. It contains 201 AP observations for each raw/normalized human- and mouse-input waveform. The original plotting/statistics code filters to AP1–AP200; the audit mirrors that range.

Mean normalized K current amplitude for the two waveform inputs:

| Recording species | Human input AP5 / AP200 | Mouse input AP5 / AP200 |
|---|---:|---:|
| Human (n=14) | 0.7214 / 0.4275 | 0.7310 / 0.4063 |
| Mouse (n=11) | 0.7928 / 0.2736 | 0.7900 / 0.2693 |

These are descriptive per-recording means; the summary CSV also contains median, SD and SEM. They are not p-values and do not replace the authors' original model.

### Original Figure 2 statistical script — audit finding

The source `Figure2/stats_fig2.py` was also downloaded and checksum verified. It uses Type-II ANOVA on ordinary least-squares models:

- Na: `relative_amp ~ APnr*C(Species) - C(Species)`, run over AP1–200 and again over AP1–5. All four APwave groups are stacked into the data; the formula contains no APwave term.
- K: `amp ~ APnr*C(species)`, using only the normalized human-input condition `_h_n_`, run over AP1–200 and again over AP1–5.

The original script has been inspected but its four ANOVA tables have **not yet been re-executed** in this audit. A separate reproduction step is planned so source-faithful p-values can be checked against the article without conflating them with the descriptive summaries. The repeated AP observations and multiple APwave conditions should also be retained as a statistical-design caveat when considering any independent model.

The machine-readable summary is [`wilbers2023_figure2_data_summary_2026-11-23.json`](references/wilbers2023_figure2_data_summary_2026-11-23.json). The raw 15.1 MB `Figures5_6/APclamp/H_wide.csv` trace matrix is still not downloaded; thus the voltage-command current traces are not yet replayed.


## Original OLS/Type-II ANOVA reproduction — CI pending

The source-faithful Figure 2 statistics reproduction has been added. The first GitHub Actions run will validate the four original models (Na AP1–200 / AP1–5; K AP1–200 / AP1–5), compare their interaction p-values against the article's reported thresholds, and emit a distinct cluster-robust-by-recording sensitivity analysis. No new p-value is accepted until the workflow passes and its artifact is inspected.


## Source-faithful inferential statistics reproduced — 23/11/2026

GitHub Actions [45117497613](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45117497613) completed successfully. All 18 tests passed, and the original Dataverse `Figure2/stats_fig2.py` ran unchanged after its workbooks and script were verified by official SHA-1 metadata and pinned SHA-256. Environment: Python 3.12.16, pandas 2.2.3, SciPy 1.15.3, statsmodels 0.14.4. Full output: [artifact 14792550979](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45117497613/artifacts/14792550979).

### Original OLS / Type-II ANOVA interaction results

| Ion / AP range | Observations | Recordings | Reproduced interaction p | Article reference |
|---|---:|---:|---:|---:|
| Na AP1–200 | 39,200 | 49 | 0.0 (underflow) | < 10⁻³²³ — matched |
| Na AP1–5 | 980 | 49 | 1.4087 × 10⁻⁵⁴ | < 10⁻⁵³ — matched |
| K AP1–200 | 5,000 | 25 | 3.1883 × 10⁻⁴⁶ | < 10⁻⁴⁵ — matched |
| K AP1–5 | 125 | 25 | 0.072096 | 0.07 — matched |

All four reproduce the publication's reported thresholds. Na AP1–200's 0.0 is a floating-point underflow, not a literal zero-probability result.

### Cluster-robust sensitivity by recording

The added covariance sensitivity groups repeated AP observations by recording filename. It preserves strong interactions for Na (AP1–200: p=8.50×10⁻¹¹; AP1–5: p=5.80×10⁻⁹) and K AP1–200 (p=0.00373). K AP1–5 remains non-significant (p=0.0759), consistent with original OLS p=0.0721. These are AMSN sensitivity tests, not the authors' published p-values.

The original OLS stacks many AP observations from each recording but does not model within-recording dependence. Cluster-robust covariance reduces that source of pseudoreplication; it does not solve every design issue. Na stacks four waveform groups without an APwave term, while K uses only normalized human-input waveforms. No wider biological inference is drawn from these tests alone.

Machine-readable output: [`wilbers2023_figure2_stats_reproduction_2026-11-23.json`](references/wilbers2023_figure2_stats_reproduction_2026-11-23.json), and [summary CSV](../results/wilbers_figure2_stats_reproduction_2026-11-23.csv).

This is statistical reproduction of published AP-clamp amplitude adaptation, not replay of raw time-domain traces. The 15.1 MB `H_wide.csv` archive remains a separate unfinished gate.


## Original AP-clamp time-domain replay — workflow added 23/11/2026

The original raw `H_wide.csv` trace (Dataverse file ID 318541) is now the next reproducibility gate. A new workflow downloads the trace, experimental `amps_na.csv`/`amps_k.csv`, the original AP-clamp helper and protocol scripts, and four original Na/K human/mouse MOD mechanisms. It verifies official Dataverse SHA-1 and byte size, computes SHA-256, then replays the exact source 5-AP command window (199–307 ms, 125 kHz). The Na replay applies the source's -10 mV liquid-junction offset; K uses no offset. First CI result is pending. Original K numerical singularities remain visible; no code correction or production parameter change is applied.


## 200-AP full-train replay gate — added 23/11/2026

The verified raw `H_wide.csv` has 800,752 samples at 125 kHz and 240 voltage-command peaks over the full recording. The 200-AP source window is 199–5182 ms (622,876 samples), and is required to contain exactly the first 200 command peaks. A 200-AP execution mode now calls the original `Ina_AP1_5_200` / `Ik_AP1_5_200` helper functions and compares the full AP1–AP200 modeled curves with the experimental `amps_na.csv` / `amps_k.csv` recording means.

To avoid the original helper's quadratic `np.append` current-recorder cost, only the 200-AP mode swaps its data collector for an equivalent list-backed recorder; the same NEURON VClamp command, 0.008 ms step, voltage initialization, current variable and time-stepping loop are retained. The 5-AP baseline remains on the untouched original collector. First 200-AP CI run is pending; no long-train result is accepted until its artifact is inspected.


## Per-recording workbook cross-check for the 200-AP command — implementation added 23/11/2026

The 200-AP run is now extended to read the original Na/K Figure 2 Excel workbooks after SHA-1/size verification. It will compare the complete model curves with per-recording means, SD and SEM from the workbook, rather than relying only on the legacy `amps_na.csv`/`amps_k.csv` mean series. For Na, both `Hnarrow` (main Figure 2 group, also matching the legacy CSV mean curve) and `Hwide` (candidate suggested by the raw input filename) are reported separately because the workbook's own waveform descriptions conflict. For K, the explicit normalized human-input columns `amp_h_n_` are used, matching the AP command family. This gives n=16/33 Na recordings and n=14/11 K recordings, with per-AP SD/SEM. First CI result is pending.


## Full 200-AP replay and per-recording workbook validation — completed 23/11/2026

GitHub Actions [45126687672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45126687672) completed successfully with **9/9 tests passing**. The original Dataverse `H_wide.csv` command was downloaded and checksum verified; NEURON 9.0.2 compiled and replayed the original human/mouse Na/K mechanisms through the first 200 AP peaks over 199–5182 ms (622,876 samples at 125 kHz). Each of the four models returned exactly 200 finite peak amplitudes; none were non-finite. The artifact is [14796251799](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45126687672/artifacts/14796251799), SHA-256 `81e6fc2cd8d5859bdf92a75b330711fd8ea0b9693fdd4e913868c75572bda1b2`.

The full replay compares model curves against the original Figure 2 workbooks at the recording level, not just against legacy aggregate CSV curves. Na uses separate Hnarrow and Hwide groups; K uses normalized human-input workbook columns `amp_h_n_`.

| Comparison | Recordings | MAE | RMSE | Model AP200 | Experiment AP200 mean ± SEM | Delta | Pointwise ±1.96 SEM overlaps |
|---|---:|---:|---:|---:|---:|---:|---:|
| Na human · Hnarrow | 16 | 0.0940 | 0.0995 | 0.8931 | 0.7487 ± 0.0303 | +0.1444 | 18/200 |
| Na mouse · Hnarrow | 33 | 0.2137 | 0.2169 | 0.7535 | 0.5167 ± 0.0154 | +0.2368 | 2/200 |
| Na human · Hwide | 16 | 0.1162 | 0.1236 | 0.8931 | 0.7327 ± 0.0281 | +0.1604 | 20/200 |
| Na mouse · Hwide | 33 | 0.1860 | 0.1898 | 0.7535 | 0.5080 ± 0.0150 | +0.2455 | 1/200 |
| K human · human input | 14 | 0.2419 | 0.2432 | 0.6750 | 0.4275 ± 0.0321 | +0.2475 | 1/200 |
| K mouse · human input | 11 | 0.2857 | 0.2943 | 0.6284 | 0.2736 ± 0.0231 | +0.3548 | 1/200 |

All six comparisons have a positive AP200 model-minus-experiment gap. This means the original single-compartment models retain too much normalized current late in the train (i.e. model use-dependent attenuation is too weak), with the largest difference in mouse K. The gap is visible well before AP200: for example, at AP5 the human-input K model is 0.9389 (human) / 0.9209 (mouse) after AP1 normalization, whereas the workbook means are 0.7214 / 0.7928.

### Equivalence of the long-run performance optimization

The 200-AP replay avoids quadratic `np.append` reallocations by storing the current samples in a list. Before the long replay, all four models were run on the exact original first-five-AP command once with the original collector and once with the optimized collector. The four amplitude series were identical: maximum absolute difference was **0** for Na human, Na mouse, K human and K mouse (comparison tolerance rtol/atol (10^{-12})). Only the recorder storage changed; VClamp, voltage command, initialization, 0.008 ms time step, integration loop, current variable and NMODL equations were unchanged.

### Interpretation boundaries

- `Hnarrow` is the main Figure 2 Na waveform group. `Hwide` is retained separately as a candidate match to the raw `H_wide.csv` filename because the workbook description of Hwide/Mwide is inconsistent. No silent relabelling or pooling is performed.
- K model values in the workbook comparison are normalized to AP1 to match the workbook's `amp_h_n_` series. The original K plotting code separately uses model-maximum normalization; that legacy comparison remains distinct in the replay artifact.
- MAE/RMSE and AP200 differences are descriptive, not new significance tests. Pointwise mean ±1.96 SEM overlap counts are not simultaneous confidence bands or hypothesis tests.
- This replay identifies a quantitative adaptation mismatch, not its cause. Channel kinetics, conductance density, slow inactivation, ionic accumulation and the limitations of a single-compartment model need separate controlled sensitivity/identifiability tests.

Machine-readable summary: [`wilbers2023_200ap_replay_summary_2026-11-23.json`](references/wilbers2023_200ap_replay_summary_2026-11-23.json); CSV: [`wilbers_200ap_model_vs_recording_means_2026-11-23.csv`](../results/wilbers_200ap_model_vs_recording_means_2026-11-23.csv).


## Fit-driver versus compiled MOD parameter reconciliation — implementation added 23/11/2026

A new source-only audit has been added to verify whether the archived human Na/K `final best fit` dictionaries in the fitting drivers match the parameter values in the exact Dataverse MOD files. It downloads all four original sources by immutable file ID and checks official SHA-1, byte size and pinned SHA-256 before parsing. It only reports differences; it does not apply fit values or modify mechanisms. The first GitHub Actions result is pending. A K discrepancy would be a source-version/provenance issue to investigate, not proof of the AP-clamp mismatch's cause.


## Runtime replay of archived K-human fit snapshot — CI pending

The source reconciliation audit confirms the archived K-human final-fit dictionary differs from the canonical `k_human.mod` in six inactivation/recovery parameters. The 200-AP runner now evaluates that dictionary as a separate runtime-only sensitivity variant, with no MOD file edits. It uses the same 200-AP command and the K human-input recording workbook target; baseline and fit-snapshot outputs will be reported side by side. This is not a replacement mechanism or a production candidate. First sensitivity replay result is pending.


## K-human final-fit snapshot provenance and runtime sensitivity — 23/11/2026

The source reconciliation workflow [45128132847](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45128132847) passed 3/3 tests and checksum-verified the original Dataverse MOD files and fitting drivers. It found:

- Na human: all **13/13** values in the terminal final-fit dictionary match the canonical `na_human.mod` PARAMETER block.
- K human: only **5/11** match the canonical `k_human.mod` defaults. Six archived fitting-driver values differ: `Rd`, `Rg`, `qi1`, `qi2`, `thi1`, and `thi2`. The largest proportional difference is `qi2`: 0.4018338 in the canonical MOD versus 6.8091265 in the terminal snapshot (~16.95×).

This snapshot is printed at the end of the original K fitting driver after the fitting calls; the script does not pass the terminal dictionary to `mod_cell` after that marker. It is therefore a saved, unapplied candidate snapshot and not proof that the compiled MOD uses those values.

### Runtime-only 200-AP K-human sensitivity

A separate NEURON 9.0.2 run [45128589224](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45128589224) passed 10/10 tests and applied the six snapshot values only to a temporary K-human mechanism instance. Parameter readback matched all six requested values, all 200 AP peaks remained finite, and the canonical `.mod` source and production runtime were unchanged. The artifact is [14796936650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45128589224/artifacts/14796936650), SHA-256 `8848be91b545d0d43def0a8a76e6bec7722e8d9e17ad9000c37a05e137fc59e1`.

Compared with the canonical MOD baseline against the 14 human recordings in the normalized human-input K workbook condition:

| Metric | Canonical MOD | Archived fit snapshot |
|---|---:|---:|
| MAE, AP1–200 | 0.24192 | 0.26004 |
| RMSE, AP1–200 | 0.24322 | 0.26144 |
| Model AP5 | 0.93888 | 0.94905 |
| Experimental AP5 mean | 0.72142 | 0.72142 |
| Model AP200 | 0.67497 | 0.69462 |
| Experimental AP200 mean ± SEM | 0.42745 ± 0.03213 | 0.42745 ± 0.03213 |
| AP200 model-minus-experiment | +0.24752 | +0.26717 |

The snapshot increases MAE by **7.49%**, RMSE by **7.49%** and the AP200 overestimation by **7.94%**. It therefore makes the long-train match worse, despite running stably. The candidate is rejected as a replacement for the canonical K mechanism under this AP-clamp objective.

The proper interpretation is a provenance discrepancy plus a negative sensitivity result: the printed fit snapshot is not the MOD default, and applying it does not explain or fix the 200-AP adaptation gap. No channel code, parameter default or production behaviour is changed. Machine-readable details are stored in [`wilbers2023_k_human_fit_snapshot_sensitivity_2026-11-23.json`](references/wilbers2023_k_human_fit_snapshot_sensitivity_2026-11-23.json) and [the CSV](../results/wilbers_k_human_fit_snapshot_sensitivity_2026-11-23.csv).


## K-human two-factor interaction grid — implementation added 23/11/2026

A 3×3 crossed sensitivity experiment is being added for `prop_inact` (0.70, 0.85, 0.95) and `h2tau_inact` (225, 450, 900 ms). The five canonical/one-factor grid cells are reused from the already completed AP1–AP200 runs; only the four crossed cells are newly simulated. Each point is scored against the 14 human K recordings using AP1-normalized `amp_h_n_` data, MAE/RMSE over all 200 APs, AP5 and AP200 gaps, and pointwise SEM overlap. The four crossed models are transient runtime overrides only; canonical MOD defaults and production runtime remain unchanged. The new CI result is pending.


## Local K-human parameter refinement around coarse-grid best point — implementation added 23/11/2026

The coarse 3×3 grid selected `prop_inact=0.95`, `h2tau_inact=225 ms` as its best point. A second bounded 3×3 neighbourhood is being evaluated: `prop_inact={0.95, 0.975, 0.99}` and `h2tau_inact={112.5, 168.75, 225 ms}`. The known best point is reused, and the other eight points are run with temporary parameter overrides. The new report adds separate MAE for AP1–100 and AP101–200 so an apparent full-train improvement can be checked across early and late epochs. This remains exploratory; no runtime MOD defaults are changed and no fit candidate is promoted. CI is pending.


## K-human 200-AP crossed sensitivity and local refinement — completed 23/11/2026

The full-train sensitivity workflows completed successfully on NEURON 9.0.2 using the checksum-verified H_wide command and the 14 human K recordings in the normalized human-input `amp_h_n_` workbook condition. The latest 200-AP workflow is [45142188274](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45142188274); artifact [14801794804](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45142188274/artifacts/14801794804), SHA-256 `fa517cf33b541f3826c64dd64003d5ee02a2ac6eb63803a4fd21581c972789cc` (676,046 bytes).

### Crossed 3×3 grid

A coarse `prop_inact × h2tau_inact` grid at prop={0.70,0.85,0.95} and tau={225,450,900 ms} completed 9/9 points. The best point was (0.95,225 ms), MAE 0.14956 versus 0.24192 for the canonical MOD defaults.

### Local 3×3 refinement

A second grid around that point at prop={0.95,0.975,0.99} and tau={112.5,168.75,225 ms} also completed 9/9 points; each new model returned 200/200 finite amplitudes and the parameter overrides were read back. Best tested point:

| Metric | Canonical MOD | Best tested sensitivity |
|---|---:|---:|
| `prop_inact` | 0.85 | 0.99 |
| `h2tau_inact` | 450 ms | 112.5 ms |
| MAE, AP1–200 | 0.24192 | **0.07229** |
| RMSE, AP1–200 | 0.24322 | **0.07424** |
| MAE, AP1–100 | — | 0.06960 |
| MAE, AP101–200 | — | 0.07498 |
| AP5 model | 0.93888 | 0.86576 |
| AP5 experiment | 0.72142 | 0.72142 |
| AP200 model | 0.67497 | 0.49852 |
| AP200 experiment ± SEM | 0.42745 ± 0.03213 | 0.42745 ± 0.03213 |
| AP200 model-minus-experiment | +0.24752 | +0.07107 |
| points within pointwise mean ±1.96 SEM | 1/200 | 6/200 |

MAE falls by 70.1% relative to canonical defaults. The improvement appears in both halves of the train, not only at AP200. However the AP200 gap remains about 2.21 SEM, and only 6/200 points lie within their pointwise mean ±1.96 SEM. This is not a complete model fit.

### Critical provenance boundary

The archived K-human fitting driver (Dataverse file ID 326237) fits the voltage-clamp parameter vector `thi1, thi2, qi1, qi2, Rd, Rg, tha, qa, Ra, th_act_inf, q_act_inf`. It does **not** fit `prop_inact` or `h2tau_inact`; these remain fixed mixture parameters in the distributed MOD source. Consequently this sensitivity grid explores parameters outside the original voltage-clamp fit vector. Its best point lies at both tested boundaries (largest prop, shortest tau), which is a reason to stop unrestricted MAE chasing, not evidence that those values are biologically correct.

No MOD file, canonical parameter default, or production runtime was modified. The result is an exploratory calibration signal only. Next work should establish provenance/physiological bounds for the mixture parameters and cross-check against the other published K MOD variants or independent protocols before any further tuning.

Machine-readable results: [JSON](references/wilbers2023_k_human_local_refinement_grid_2026-11-23.json) and [CSV](../results/wilbers_k_human_local_refinement_grid_2026-11-23.csv).


## Original K MOD variant provenance gate — CI pending 23/11/2026

Added a separate workflow to inspect the nine released K MOD files (canonical human/mouse, two named human variants, and five hybrid models) together with the original channel-fitting helper and human/mouse fitting drivers. For each immutable Dataverse ID the script verifies the official metadata SHA-1 and exact byte size, records a SHA-256, parses the NMODL PARAMETER block, diffs it against canonical k_human, and independently compiles each source under NEURON 9.0.2. The original channel_kinetics.py comments identify hybrid1..5 as combinations of human activation/inactivation G/Gmax and activation-time-constant characteristics. Workflow 45144507180 is in progress; no variant AP-clamp replay or production promotion is claimed yet.
