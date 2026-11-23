# Wilbers 2023 Dataverse v3 and NMODL source audit

**Date:** 2026-11-22 (Asia/Bangkok)  
**Dataset:** [DataverseNL DOI 10.34894/L5J0SD](https://doi.org/10.34894/L5J0SD), released version 3.0  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Status:** selected source bytes inspected and hashed; no mechanism execution or biological reproduction claimed.

## Dataset identity and access

The official DataverseNL API resolves DOI 10.34894/L5J0SD to dataset ID 317867, released version 3.0 (internal version ID 24561), published 2022-11-10 and last updated 2022-12-13. The dataset declares CC0-1.0 and contains 65 files.

The inventory includes raw Figure 1–4 workbooks, AP-clamp traces and amplitudes, channel-fitting code, two distinct MOD folders, current-clamp code and conductance-density grids, and frequency-tracking data. A curated inventory with file paths, IDs, MIME types, byte sizes, official SHA-1 checksums and independently computed SHA-256 values is stored in `references/wilbers2023_dataverse_source_manifest_2026-11-22.json`.

Selected Na/K mechanism files and fitting/helper scripts were read from the Dataverse public object-store endpoints in an isolated research session and SHA-256 hashed. Their byte counts and SHA-1 values were cross-checked against the Dataverse file metadata API. The source bytes were not committed into AMSN. Numeric workbooks and the 15.1 MB AP-clamp `H_wide.csv` remain undownloaded; this manifest is a curated subset, not a 65-file mirror.

## Sodium mechanism — Figures5_6/MOD/na_human.mod

Dataverse file ID 318629; 3,602 bytes; SHA-1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970`; observed SHA-256 `e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd`.

The source comments describe an HH-style sodium channel based on Mainen (1994), edited by Kole (2006), then modified/fitted by René Wilbers at VU in 2020. It uses two gates `m,h`:

[
g_{Na}=tadj\,\bar g_{Na}m^3h,\qquad I_{Na}=10^{-4}g_{Na}(V-E_{Na}).
]

Steady-state activation/inactivation are separated from activation/inactivation time constants. Reference temperature is 25 °C, (Q_{10}=2.3), and the MOD file has an active 199-point `TABLE` over -120 to +100 mV. The fitting driver uses a 10 µm single-compartment section (`Ra=200`, `cm=1`) and sequentially fits inactivation/recovery, activation kinetics, and activation steady-state Vhalf/slope. The script's final parameter dictionary matches the distributed Na MOD values. Its voltage-clamp analysis runs steps from -80 to +10 mV in 5 mV increments at 25 °C.

## Potassium mechanism — Figures5_6/MOD/k_human.mod

Dataverse file ID 318647; 4,220 bytes; SHA-1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`; observed SHA-256 `899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063`.

This is a mixed population of fast-, slow- and non-inactivating potassium channels. It uses `m,h1,h2`; default mixture values are `prop_inact=0.85`, `prop_h2=0.4`, `h2tau_inact=450 ms`, and `h2tau_inact_rec=2789.7929 ms`. Reference temperature is 34 °C and (Q_{10}=2.3). Unlike the sodium file, the `TABLE` directive in the distributed potassium MOD is commented out.

The fitting driver uses test steps from -110 to +50 mV in 10 mV increments and a long recovery protocol. **A parameter-provenance discrepancy remains unresolved:** its intermediate inactivation-fit dictionary matches the distributed MOD, but a later dictionary labelled “final best fit” reports different values for `thi1, thi2, qi1, qi2, Rd, Rg`. The driver also sets `h12factor=10.5`, while the distributed MOD comments out the `h1tau*h12factor` expression and uses fixed slow-inactivation/recovery time constants. No K kinetic snapshot is selected as definitive.

## Separate current-clamp variants

The dataset also contains `na_human.mod` and `k_human.mod` under `Figures5_6/Current_clamp/mod`. These are different Dataverse file records with different hashes; they add global conductance scaling and human-fraction variables `na_human_ratio` and `k_human_ratio`. They must not be silently substituted for the `Figures5_6/MOD` variants used for the channel comparison.

The current-clamp helper initializes a 10 µm compartment at 34 °C, inserts both human and mouse mechanisms and adjusts reversal potentials/voltage offsets for liquid-junction potentials. Its Powell gbar fit uses a target constructed as a **50:50 average of human and mouse median AP amplitude, upstroke and downstroke**. The resulting conductance densities are therefore not a human-only fit. The K voltage-clamp helper's recovery target is also explicitly the mean of human and mouse values.

## High-priority source-level warning — trap0

Both canonical human MOD files contain a `trap0` implementation where:

- the branch condition tests `fabs((v+th)/q)`;
- the main quotient uses `a*(v-th)/(1-exp(-(v-th)/q))`;
- the commented intended limit is `a*q`;
- the active fallback is `q*(1--(v-th)/q/2)`, omitting multiplier `a`.

At (v=th), the main expression has a removable (0/0) limit, but for nonzero `th` the current branch condition does not select that limit. The active fallback also does not equal the standard (a q) limit. This is a source-level numerical warning, **not yet a proven simulation failure**. The Na MOD uses tabulated rates while K calculates rates directly, so the runtime consequences may differ.

Before porting, compile the original mechanisms and probe values at (v=th-\epsilon), (v=th), and (v=th+\epsilon), comparing with a stable analytic reference and the published voltage-clamp protocols. Do not patch the source and claim equivalence without that comparison.

## Verification state and next gates

Verified: dataset DOI/version/license/file count, selected file metadata, source bytes, and selected SHA-256 digests. Inspected: original Na/K MODs, current-clamp variants, Na/K fitting drivers, channel tools and current-clamp helpers.

Not yet completed: NEURON compilation/execution of the original MOD files, reproduction of channel voltage-clamp/AP-clamp traces, downloading the raw numerical workbooks/AP-clamp matrix, or integrating a mechanism into AMSN.

1. Download and SHA-256 verify the numerical workbooks and AP-clamp trace file.
2. Compile the unchanged original Na/K MOD files with the pinned NEURON version.
3. Test the `trap0` singular points against a stable analytic reference.
4. Reproduce Na/K activation, inactivation, recovery and AP-clamp protocols at the published temperatures.
5. Resolve the K parameter-snapshot mismatch and mixed-species fitting objectives.
6. Only then implement an opt-in human somatic channel mechanism. Do not infer AIS, axonal or dendritic densities from soma measurements.

A dedicated GitHub Actions source audit was added to re-download the exact canonical MOD files, verify SHA-256, compile with NEURON 9.0.2 and probe near source-declared characteristic voltages. The first workflow result is pending. No human mechanism was added to AMSN runtime and no production defaults were changed.


## First compiled NEURON result — 22/11/2026

GitHub Actions run [45039313143](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143) completed successfully on Python 3.12 / NEURON 9.0.2. All 11 provenance-registry tests passed. Both original Dataverse MOD files were downloaded again, their SHA-256 values matched the pinned manifest, and both compiled and loaded into NEURON.

The initial point probe found:

- NaV source: all 9 tested exact/near-positive-singularity observations were finite. This is not proof of correctness; the Na mechanism uses a 199-point TABLE.
- KV source: non-finite time constants were observed exactly at `tha=-29.9618 mV` (`mtau`), `thi1=40.5659 mV` (`h1tau`) and `thi2=-75.9382 mV` (`h1tau`). At the immediately adjacent ±0.00001 mV values, the same observables were finite.

The source workflow therefore proves successful compilation but exposes a real pointwise runtime singularity in the unmodified potassium mechanism. It does not yet prove how often the singularity is encountered in physiological voltage trajectories or how much it distorts the published protocols. An extended comparison now compiles a temporary corrected `trap0` clone for diagnostic reference only, probes both +th and -th as well as the published command-voltage grids, and requires the diagnostic clone to maintain finite positive time constants. The original Dataverse source remains unchanged; the corrected clone is not accepted for production.

The first workflow artifact is [`wilbers-original-nmodl-source-audit`](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143/artifacts/14764015969). The run's artifact ZIP SHA-256 is `31a5883d6cb46670b3b8795afc7fa656ba0632ef544db2b328e922921ce82658`.


## Extended original-vs-stable `trap0` comparison — 23/11/2026

Workflow [45115543259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259) passed after the registry assertions were synchronized with the already verified NEURON compilation. It compiled both the unmodified source and a separate diagnostic-only clone whose `trap0` branch uses `v-th` and whose limiting expansion is (a q(1+(v-th)/(2q))). Original source files remain unchanged.

The extended audit tested both signs of each characteristic voltage, adjacent points at ±0.00001 mV, and the discrete command-voltage grids listed in the original fitting helpers:

- Na: 41 points, 19 command test voltages. Original and diagnostic rates were identical at exported precision at every probe; all original and diagnostic time constants were finite and positive.
- K: 38 points, 17 command test voltages. The original mechanism has three non-finite time-constant points at the positive source singularities: `mtau` at -29.9618 mV; `h1tau` at +40.5659 mV and -75.9382 mV.
- The mirror-branch defect also creates negative K `h1tau`: -0.072506 ms around -40.56590 mV, and -0.013253 ms at +75.9382 mV. At +29.9618 mV, original K `mtau` is 0.075868 ms versus 0.903835 ms for the stable diagnostic clone (91.61% relative difference).
- On the *discrete static test-voltage samples* in the archived fitting scripts, K source and diagnostic outputs agree at the exported precision and all original time constants are positive. This does not prove full time-domain clamp equivalence: dynamic membrane voltage passes through values between those test steps, and raw trace replay has not yet been performed.

The stable clone is only a mathematical diagnostic comparator. It is not the published source, not a validated fix, and not eligible for AMSN runtime. See the complete point-level JSON artifact [14790704932](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259/artifacts/14790704932) (artifact ZIP SHA-256 `c53df1ef02993fddc2ee466203c700e949e36cc71a0e2cfb74ab25ac07fec7d3`).


# Wilbers 2023 Figure 2 raw Na/K workbook audit

**Date:** 2026-11-23  
**Dataset:** DataverseNL DOI 10.34894/L5J0SD, released version 3.0, CC0-1.0  
**Status:** source workbooks inspected and checksum verified; automated descriptive audit workflow added, first CI result pending.

## Verified source files

| File | Dataverse ID | Bytes | SHA-1 | SHA-256 |
|---|---:|---:|---|---|
| `Figure2/Na_data_fig2.xlsx` | 318668 | 548,562 | `cd702d7f1ca65b0b88a2565f289740546902e36b` | `2fac600523d596a4dccbe167d3283b2e506dfdb9c7b1caef2a490c2c5dff184a` |
| `Figure2/K_data_fig2.xlsx` | 318669 | 302,011 | `287720f8db3b20b167edd9e639dd67b0a1194def` | `f00714c534c9658b8c07d2a473d39b2fd5a99c392e6e2ab50fb52fbb3b6ca74d` |

Both workbook payloads matched the official Dataverse file metadata SHA-1 and the independent SHA-256 values listed above. No raw workbook bytes are committed to the repository; the Dataverse release remains canonical.

## Workbook structure

- Na workbook: `data` sheet range A1:ADX50 (49 recording rows, 4 metadata fields, four groups of 200 normalized AP amplitudes); `variables` sheet A1:B213.
- K workbook: `data` sheet A1:ADZ26 (25 recording rows; explicit species H/M; four raw/normalized current series with 201 AP values each); `variables` sheet A1:B213.

## Source-controlled label rules

The Dataverse `Figure2/plots_fig2.py` script provides the exact Na species assignment:

- Filename starting with `M` is classified as Mouse.
- All other recording filenames are classified as Human.
- `Hnarrow` is the main Na Figure 2 waveform group.
- `Hwide` and `Mwide` are used for the supplementary waveform comparison.

This is why the Na workbook's missing explicit species column can be reconstructed from the source plotting script, rather than guessing from filename prefixes. The resulting sample counts are expected to match the published AP-clamp recordings (human n=16, mouse n=33).

The Na workbook's own variables tab has a metadata conflict: it labels both `Mwide` and `Hwide` as "Human waveform 2". The plotting script treats these as distinct APwave labels in the waveform comparison. The audit preserves the workbook's group labels and records the conflicting description; it does not silently rewrite one label.

The K workbook explicitly labels recording species (`H`/ `M`) and separates input waveforms with `amp_h_n_` and `amp_m_n_`. The original plotting script uses AP1..AP200 for normalized curves and excludes AP201.

## Analysis method

The new audit script `amsn-core/examples/audit_wilbers_figure2_data.py`:

1. Fetches Dataverse metadata and the exact workbook file IDs.
2. Checks official metadata SHA-1, byte size, and pinned independent SHA-256.
3. Verifies the plotting and statistics scripts by their official file IDs and SHA-1.
4. Parses the workbook `data` and `variables` sheets without modifying them.
5. Computes descriptive per-recording mean, median, SD, SEM and normalized amplitude curves at AP1, AP5 and AP200, separately by cell species and source condition.
6. Reports missing values and paired descriptive waveform differences for K.

These are descriptive summaries only. They do not replace the original paper's linear/multiple regression analysis, inferential statistics, or time-domain replay of raw currents.

## Scope and limitations

- These are AP-clamp normalized current-amplitude data from somatic nucleated patches, not absolute conductance densities.
- The K workbook has explicit species counts H=14, M=11; the Na species classification follows the original plotting script.
- The Na variable-description discrepancy is unresolved and must remain visible.
- The AP-clamp raw trace matrix `Figures5_6/APclamp/H_wide.csv` (15,095,411 bytes), `amps_na.csv`, and `amps_k.csv` have not been downloaded.
- The new GitHub Actions workflow is the reproducibility gate; first result is pending. No new p-values or biological generalization are claimed.

## Next reproducibility gate

Run the original Figure 2/Stats scripts in a controlled Python environment after checksum verification, compare regenerated curves to the published figure, retrieve the raw AP-clamp trace matrix and reproduce the authors' time-domain protocol. Only then should a human/mouse AP-clamp benchmark be used to assess any NMODL fix or AMSN active-channel mechanism.


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


## Original Figure 2 inferential statistics — source reproduction underway

The article reports species-by-AP-number interactions in its original OLS analysis: Na current adaptation AP1–200, (p<10^{-323}); Na AP1–5, (p<10^{-53}); K AP1–200, (p<10^{-45}); and K AP1–5, (p=0.07). These are the publication's reported results, not yet results from the AMSN reproduction. <Cite refs={["turn465333search0"]}/>

The new runner downloads the exact Na/K workbooks and `Figure2/stats_fig2.py`, verifies official Dataverse SHA-1 plus pinned SHA-256, and executes the original script unchanged. Only its Windows Excel paths and imported ANOVA function are wrapped so the four Type-II tables can be captured. A separate cluster-robust interaction test groups by recording filename to assess the repeated-AP design; those are additional sensitivity tests and must not be confused with the publication's OLS p-values.


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


## Original K MOD variant provenance audit — completed 23/11/2026

GitHub Actions [45144507180](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45144507180) completed successfully. The workflow passed all **5 source/parser tests**, verified each immutable Dataverse file ID against its official SHA-1 and exact byte size, calculated an independent SHA-256 for every source, parsed each NMODL PARAMETER/RANGE block, compared it with canonical `k_human.mod`, and compiled all **9 K mechanisms** under NEURON 9.0.2. There were zero compile failures. The artifact is [14803831434](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45144507180/artifacts/14803831434), SHA-256 `7e6e4855a390610313d2769ac87f90bf60b418f5e5e3126aacd92f33acc24e43`.

The eight additional source variants are `k_mouse`, `k_human_h1`, `k_human_hm12inf` and `k_hybrid1`–`k_hybrid5`. The original channel-kinetics helper labels the five hybrid variants as combinations of human activation/inactivation G/Gmax curves and human activation time constants. Two human variants have structurally different gates: `k_human_h1` uses `m,h`, while `k_human_hm12inf` uses `m,m1,m2,h1,h2`.

A crucial fitting-provenance result: the human CMA fit vectors include the activation/inactivation threshold and rate parameters (`tha, qa, Ra, th_act_inf, q_act_inf, thi1, thi2, qi1, qi2, Rd, Rg`), but **do not include** the mixture/slow-inactivation parameters `prop_inact`, `prop_h2`, `h2tau_inact`, `h2tau_inact_rec` or `inact_rate_factor`. Those mixture terms were fixed in the published mechanism and were not estimated by the archived K fit vectors. This matters because the exploratory long-train grid that reduced AP-clamp MAE varied `prop_inact` and `h2tau_inact`; that grid is a diagnostic sensitivity experiment, not a direct reproduction of the original CMA fit.

No K variant has yet been replayed against the 200-AP H_wide command in this provenance gate. Compilation and parameter diff are not evidence of physiological fit. All original mechanism files and production defaults remain unchanged.
