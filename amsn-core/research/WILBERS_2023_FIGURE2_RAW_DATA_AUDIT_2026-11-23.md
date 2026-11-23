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
- The new GitHub Actions workflow completed successfully; see run [45116703439](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439). No new p-values or biological generalization are claimed.

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
