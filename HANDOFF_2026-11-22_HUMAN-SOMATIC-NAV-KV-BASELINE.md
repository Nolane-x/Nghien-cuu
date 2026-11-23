# Handoff — human somatic NaV/KV evidence baseline

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Base commit:** `7655389b9d95dc85a54f81185a037ab026e32300`  
**PR:** none opened; this evidence track is kept separate from passive PR #8.

## Read first

1. [Human somatic NaV/KV evidence report](amsn-core/research/HUMAN_SOMATIC_NAV_KV_EVIDENCE_BASELINE_2026-11-22.md).
2. [Machine-readable evidence registry](amsn-core/research/references/human_nav_kv_evidence_2023.json).
3. [Research log](research/RESEARCH_LOG_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md).
4. Existing [Eyal 2018 ModelDB source review](amsn-core/research/EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md).
5. Existing [FCI/Eyal derivative source audit](amsn-core/research/FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md).

## Research decision

Keep three distinct classes:

- Wilbers 2023 somatic nucleated-patch measurements — direct experimental Na+/K+ current density and voltage dependence.
- Wilbers 2023 single-compartment HH parameters — model-fit conductances used in an AP simulation.
- Eyal 2018 compartment-specific Na/K conductances — model estimates from six cells and about 900 spikes, under an assumed rodent-like channel-kinetics prior.

None is promoted to AMSN runtime defaults. The somatic patch values are not axon/AIS measurements. Human dendritic Na+ density and back-propagating AP behavior remain unresolved in the cited Eyal work.

## Files added

- `amsn-core/research/references/human_nav_kv_evidence_2023.json`
- `amsn-core/research/HUMAN_SOMATIC_NAV_KV_EVIDENCE_BASELINE_2026-11-22.md`
- `amsn-core/tests/test_human_channel_evidence_registry.py`
- `research/RESEARCH_LOG_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md`

## Validation status

- JSON syntax, provenance groups and stored unit-conversion identities were checked before commit.
- The pytest file has not been run; no CI pass is claimed.
- DataverseNL released v3.0, CC0-1.0, 65-file inventory has been verified. Selected Na/K MOD and fitting source files were downloaded/read and SHA-256 hashed; raw numeric workbooks and the 15.1 MB AP-clamp trace remain undownloaded.
- The original Eyal 2018 ModelDB ZIP remains not downloaded/not reproduced in AMSN.
- Existing PR #8 remains draft/open, unmerged; its latest PRIMA profiler and core jobs were still queued when checked. This branch does not alter PR #8.

## Next steps

1. Retrieve and hash the original Wilbers data archive and identify the actual source files/mechanism equations.
2. Verify parameter equations and units against the archived code, not just extracted thesis table labels.
3. Reproduce somatic voltage-clamp activation, inactivation, recovery and AP-command protocols at the source temperatures.
4. Add a separate opt-in human somatic channel mechanism only after the reproduction gate passes.
5. Do not extrapolate soma density to AIS, axon or dendrites without independent regional evidence.


## New source-code audit checkpoint

- [Full Dataverse/NMODL audit](amsn-core/research/WILBERS_2023_DATAVERSE_AND_NMODL_SOURCE_AUDIT_2026-11-22.md)
- [Curated source manifest](amsn-core/research/references/wilbers2023_dataverse_source_manifest_2026-11-22.json)
- [Machine-readable mechanism audit](amsn-core/research/references/wilbers2023_nmodl_mechanism_audit_2026-11-22.json)
- Source code warning: the original trap0 branch condition/limit appears inconsistent; reproduce the unmodified mechanism first.
- Potassium fit provenance warning: intermediate fit dictionary matches the released MOD, later final-best-fit dictionary does not.
- Current-clamp conductance fitting uses a 50:50 mixed human/mouse target; do not call it a human-only density estimate.
- Original MOD files and scripts have not been compiled/run in NEURON. Raw spreadsheets/AP-clamp traces not downloaded. No runtime change, no production default change.

## Next experiments

1. Compile unmodified source MOD files with the repository's pinned NEURON.
2. Probe trap0 at each (v=th\pm\epsilon) point against a stable analytic limit.
3. Reproduce the original Na/K voltage-clamp protocols and published AP-clamp data.
4. Resolve the K fitting snapshot mismatch and mixed-species objectives.
5. Only after reproduction, implement an opt-in somatic mechanism; no AIS/axon/dendrite extrapolation.


## Executable source-reproduction workflow

A dedicated workflow is now added at `.github/workflows/amsn-wilbers-nmodl-reproduction-audit.yml`. It installs pinned `neuron==9.0.2`, runs the evidence-registry tests, downloads the two canonical MOD files, verifies their SHA-256 values, compiles the unchanged sources with `nrnivmodl`, probes rate observables around the source-declared characteristic voltages and uploads a JSON artifact. Its first CI result is pending; no compilation/probe success is claimed.


## Initial NEURON 9.0.2 compilation result

Workflow [45039313143](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143) succeeded: 11 provenance tests passed; original Na/K source hashes verified; both mechanisms compiled and loaded. Initial point probe: Na all finite at tested points; K returned non-finite `mtau` at `tha`, and non-finite `h1tau` at `thi1` and `thi2` (the exact source singular voltages). Adjacent points were finite. This is a confirmed source runtime issue at exact probe values, but not yet a measured protocol-level failure. The workflow now adds a stable diagnostic clone comparison; it never modifies the original file and is not runtime-eligible. Artifact: [14764015969](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45039313143/artifacts/14764015969).


## Extended NEURON source-vs-stable comparison — 23/11/2026

- Workflow [45115543259](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259) succeeded; both unmodified and diagnostic clone compiled with NEURON 9.0.2; 11 evidence tests passed.
- Na: 41 probe points, including 19 source test voltages. Rates and time constants matched the diagnostic clone at exported precision; all were finite/positive.
- K: 38 points. Positive exact singulars produced NaN; mirror branches produce negative `h1tau` around -40.5659 mV and at +75.9382 mV. At +29.9618 mV, source `mtau` differed by 91.61% from the stable diagnostic clone.
- The 17 discrete static K test voltages match the stable diagnostic clone at exported precision. This is not a full time-domain voltage-clamp/AP-clamp reproduction; raw trace replay remains pending.
- See [source audit report](amsn-core/research/WILBERS_2023_DATAVERSE_AND_NMODL_SOURCE_AUDIT_2026-11-22.md), [machine-readable audit](amsn-core/research/references/wilbers2023_nmodl_mechanism_audit_2026-11-22.json), and [artifact 14790704932](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45115543259/artifacts/14790704932).


## Figure 2 raw workbook analysis gate — 23/11/2026

Added a reproducible audit for the original Na/K Figure 2 workbooks and the Dataverse plotting/statistics scripts. The workbooks were downloaded in a research session and their official Dataverse SHA-1 and independent SHA-256 values were verified:

- Na workbook, file ID 318668, 548,562 bytes, SHA-1 `cd702d7f1ca65b0b88a2565f289740546902e36b`, SHA-256 `2fac600523d596a4dccbe167d3283b2e506dfdb9c7b1caef2a490c2c5dff184a`. It contains 49 recordings and 4 × 200 normalized AP-amplitude groups.
- K workbook, file ID 318669, 302,011 bytes, SHA-1 `287720f8db3b20b167edd9e639dd67b0a1194def`, SHA-256 `f00714c534c9658b8c07d2a473d39b2fd5a99c392e6e2ab50fb52fbb3b6ca74d`. It contains 25 recordings, explicit H/M species labels, and 201 raw/normalized AP measurements for human and mouse waveform inputs.

Source script `Figure2/plots_fig2.py` assigns Na recording species by filename prefix (M = Mouse, otherwise Human), uses Hnarrow for the main Na Figure 2 curve, and uses Hwide/Mwide for the supplementary waveform comparison. The Na workbook variables sheet gives duplicate descriptions for Mwide and Hwide; the new audit preserves raw labels and flags the discrepancy rather than silently fixing it. K workbook explicitly separates cell species and input waveform.

A GitHub Actions workflow has been added to verify Dataverse metadata SHA-1, raw SHA-256, parse the original workbooks and output descriptive per-recording normalized-amplitude curves. It deliberately does not generate inferential p-values or claim complete trace replay. First Actions result is pending. The larger 15.1 MB AP-clamp H_wide.csv trace file remains not downloaded.

## Figure 2 data audit branch files
- Report: `amsn-core/research/WILBERS_2023_FIGURE2_RAW_DATA_AUDIT_2026-11-23.md`
- Script: `amsn-core/examples/audit_wilbers_figure2_data.py`
- Workflow: `.github/workflows/amsn-wilbers-figure2-data-audit.yml`
- Workbook SHA-1/SHA-256 pinned in the Dataverse manifest. First Actions result is pending.


## Verified Figure 2 AP-clamp workbook results — 23/11/2026

- Figure 2 data workflow [45116703439](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439) passed, with artifact [14791708917](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439/artifacts/14791708917). It verified SHA-1 and SHA-256 for both workbooks and the original plot/statistics scripts.
- Na: 49 recordings (16 Human, 33 Mouse per the source filename rule), 4 distinct APwave groups × 200 APs. Main Hnarrow normalized Na amplitude at AP200: Human 0.7487 (SD 0.1211), Mouse 0.5167 (SD 0.0883). Keep Mwide/Hwide description conflict visible.
- K: 25 recordings (14 H, 11 M), 2 input waveforms × 201 samples; original code uses AP1–AP200. Human cells at AP200: 0.4275 under H input and 0.4063 under M input; Mouse cells: 0.2736 and 0.2693.
- Descriptive only; no new p-values. Original OLS/Type-II ANOVA script inspected; exact execution is next. Raw AP-clamp H_wide.csv still not replayed.
- Summary report: [WILBERS_2023_FIGURE2_RAW_DATA_AUDIT_2026-11-23.md](amsn-core/research/WILBERS_2023_FIGURE2_RAW_DATA_AUDIT_2026-11-23.md). Summary CSV: [wilbers_figure2_apclamp_normalized_summary_2026-11-23.csv](amsn-core/results/wilbers_figure2_apclamp_normalized_summary_2026-11-23.csv).
