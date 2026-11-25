# Research log — PRIMA q25 output-observer artifact recovery

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Original workflow:** [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599)  
**Recovered artifact:** [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308)  
**Corrected replay:** [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575)

## 1. Why the earlier workflow was marked failed

The original run completed its numerical output-observer analysis with report status `passed`, but the subsequent Git archival step failed. The artifact-preservation step succeeded. The job-step record confirms that all runtime, source checksum, regression and order-168 primary-reference gates passed; only the Git commit/archive step failed.

## 2. Artifact recovery and independent integrity checks

Downloaded the original workflow artifact ZIP and computed SHA-256 locally. The result exactly matches GitHub's artifact metadata:
- ZIP size: 1,441,656 bytes.
- ZIP SHA-256: `2391661263ef1c959d550e8a336c8fed89e1f1dfcc626ddab16b3db60bed8aa3`.
- Artifact ID: 15027601308.
- Artifact contains eight expected files, including report JSON, case metrics, comparisons, basis hashes, source/morphology summaries and finite-DFT identity rows.

Extracted CSV row counts:
- Basis hash rows: 144.
- Case metric rows: 3,456.
- Candidate-vs-seven comparisons: 2,592.
- Source summaries: 2,016.
- Morphology summaries: 336.
- Finite-DFT identity rows: 3,456.

The observer JSON reports 144/144 basis hash matches against the accepted order-168 primary report. Its primary case-metric SHA-256 is `dff980e065b2f497f8aea930b3fd5a16e1db680e80ff84c1d79968430b020c13`.

Maximum finite-DFT identity relative residual is `5.386622461553216e-12`, below the declared `2e-8` tolerance.

## 3. Numerical method

For each of four port layouts, both q25 voltages are read out from the corresponding rows of the full-compartment PRIMA basis. A q25 output is not included in the input selector B unless it is a retained port in that layout. This permits a direct distinction between:
- a q25 output measured only as an observer;
- the same q25 output included as a retained port;
- both q25 outputs simultaneously retained.

The study uses the same four morphology strata, nine passive parameter scenarios, three source locations, two pulse widths, order 168, 0.00625-ms timestep and 20/40-ms windows as the accepted primary experiment.

## 4. Main findings

Per morphology/q25-role/window, each median below is over 54 cases (nine scenarios × three sources × two pulse widths). Values are candidate/seven perturbation-coordinate transient NRMSE ratios. Columns:
- retained singly: the matching q25 port is retained in its own 8-port layout;
- observer-only: the opposite q25 port is retained, but this q25 output stays observation-only;
- both retained: the combined 9-port layout.

| Morphology | Q25 role | Window | Retained singly | Observer-only | Both retained |
|---|---|---:|---:|---:|---:|
| Jacobs | Basal | 20 ms | 0.0252 | 1.341 | 0.0232 |
| Jacobs | Basal | 40 ms | 0.0314 | 1.371 | 0.0307 |
| Jacobs | Apical | 20 ms | 1.370 | 0.885 | 1.307 |
| Jacobs | Apical | 40 ms | 1.388 | 1.010 | 1.404 |
| Tamas | Basal | 20 ms | 0.000233 | 3.078 | 0.00551 |
| Tamas | Basal | 40 ms | 0.000398 | 2.712 | 0.00742 |
| Tamas | Apical | 20 ms | 0.000504 | 3.587 | 0.00948 |
| Tamas | Apical | 40 ms | 0.000904 | 3.243 | 0.0173 |
| Allen | Basal | 20 ms | 0.000423 | 3.599 | 0.000819 |
| Allen | Basal | 40 ms | 0.000495 | 3.599 | 0.000970 |
| Allen | Apical | 20 ms | 0.001122 | 4.146 | 0.001230 |
| Allen | Apical | 40 ms | 0.001184 | 4.146 | 0.001545 |
| Peng | Basal | 20 ms | 0.0000236 | 2.121 | 0.000951 |
| Peng | Basal | 40 ms | 0.0000502 | 1.814 | 0.001346 |
| Peng | Apical | 20 ms | 0.0000672 | 0.621 | 0.001513 |
| Peng | Apical | 40 ms | 0.000146 | 0.625 | 0.003053 |

Interpretation:
1. Retaining a q25 port often sharply improves its own q25 readout versus the seven-port observer-only baseline, especially in Tamas, Allen and Peng. Jacobs apical is a clear near-neutral exception.
2. The other q25 output can become worse when it is left observer-only while the opposite q25 is retained. Tamas and Allen show ratios around 2.7–4.1; Peng basal output also worsens under the apical-only layout, while Peng apical output improves under the basal-only layout.
3. The combined 9-port basis improves both q25 outputs over the seven-port baseline for Tamas, Allen and Peng, but typically worsens each q25 output relative to its own single-port basis. This is consistent with fixed-order basis-budget competition, not proof that seed allocation is the only mechanism.
4. Ratios are reported with absolute deltas because the seven-port q25 observer residual may be very small.

## 5. Scientific limits

The four inputs are individual reconstructions, not a biological population. Allen NMO_162186 is an epilepsy-surgery specimen, and Peng NMO_163775 metadata says No Diameter. The study remains a passive linear-RC numerical reduction experiment. It does not establish active-channel, action-potential, synaptic, plasticity, calcium-signalling or biological validity. Full Hines remains canonical and no production solver/default was changed.

## 6. Files and next actions

- Detailed report: `amsn-core/research/PRIMA_Q25_Q25_OUTPUT_OBSERVER_FIXED_VS_ENRICHED_BASIS_RESULTS_2026-11-25.md`.
- Recovery manifest with original ZIP digest and extracted file hashes: `amsn-core/results/prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25_recovery_manifest.json`.
- Handoff updated: `HANDOFF.md`.
- Corrected archival replay [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575) was still performing the full calculation at the last check. It must complete the corrected commit/rebase/push and artifact steps before raw observer outputs are called branch-archived.

## 7. Corrected workflow now archives the outputs officially

The repaired archival replay [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575) completed **success** through Git commit and artifact upload:
- Result commit: `8f971b74807ec715cff2f4db39ebc9db7398cf32`.
- Artifact 15032389094, 1,441,661 bytes; SHA-256 `8c82e3a4c43eabe98e95e482749ccf3f7af7a1c7145ba2ecf39f6f1e9a00f4d1`.
- Corrected report Git blob: `09c03edbce0cbb0661c2507cef3abcfdd308ce74`.
- Report still declares `passed`; 144/144 primary basis hashes match; max finite-DFT identity relative residual remains `5.386622461553216e-12` against `2e-8`.
- Corrected wall time: 3,617.80 s; peak RSS 365,204 KiB. Verified dispatch list is X86_V3 and baseline(X86_V2); Haswell OpenBLAS one thread.
- SHA-256 for all six numerical CSVs matches the recovered artifact byte-for-byte. Report JSON and timing text differ only as run-specific metadata.

The recovery manifest and detailed report now identify 45625185575 as the canonical committed archive. The original artifact is retained as independent recovery evidence, not substituted or deleted.

