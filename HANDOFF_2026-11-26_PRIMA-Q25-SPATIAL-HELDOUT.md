# HANDOFF — PRIMA q25 spatial held-out generalization

**Date:** 26 November 2026  
**Active PR:** [#35 — Test q25 role-specific PRIMA seeds on held-out dendritic locations](https://github.com/Nolane-x/Nghien-cuu/pull/35)  
**Branch:** `research/prima-q25-spatial-heldout-generalization-2026-11-26`

## Objective

Test whether output-dual q25 basis enrichment improves readouts away from the two q25 locations used to construct the dual seeds. This is a numerical spatial-generalization experiment, not a biological-population validation.

## Design

- Keep the 7-port input selector, order 224, six primal expansion shifts, 4 seed schedules, 4 pinned morphology sources, 9 passive parameter scenarios, 3 input sources, 2 pulse widths, and 20/40-ms windows unchanged.
- Add four observation-only spatial holdouts: basal q10, basal q95, apical q10, apical q95.
- The four new rows must be distinct from each other, the seven canonical shared nodes, and both q25 target nodes.
- Only basal-q25/apical-q25 observation vectors may enter the role-specific dual-seed builder. The new q10/q95 nodes are only projected as output rows.
- Full Hines remains the canonical reference; no production solver/default change.

## Expected coverage

36 morphology/scenario workers; 22,464 case rows; 3,744 worker-group summaries; 416 morphology/window summaries; 936 scenario/window summaries; 104 pooled/window summaries; 144 finite-record DFT identity summaries; 144 basis metadata rows.

## Current validation state

- Protocol: `research/PRIMA_Q25_ROLE_SPECIFIC_SPATIAL_HELDOUT_PROTOCOL_2026-11-26.md`.
- Runner: `research/run_prima_q25_role_specific_spatial_heldout.py`.
- Focused tests: `research/test_prima_q25_role_specific_spatial_heldout.py`.
- Workflow: `.github/workflows/amsn-prima-q25-role-specific-spatial-heldout.yml`.
- GitHub Actions run [45764442287](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45764442287) passed runtime installation, all four SWC checksum/preflight checks, SIMD preflight, compileall and focused pytest. At checkpoint, its four-morphology numerical sweep was still running. No numerical result is accepted yet.
- Parent role-specific run [45760007155](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45760007155) failed in the numerical sweep. The prior handoff records a native exit `-11` in the first Peng worker before any stage marker. It produced no accepted cross-morphology numerical archive. Treat it as a failure, not a partial result.
- The GitHub job-log download endpoint currently returns a BlobNotFound response through the connector, so the native crash's detailed backtrace is unavailable from this session.

## Acceptance and recovery procedure

Do not promote this result until every worker completes, the exact CSV row counts and unique keys match, D0 is bit-exact with production multishift PRIMA, all projected G/C matrices pass Cholesky, all basis orthogonality gates pass, all 144 finite-record identities pass, and Git archival plus artifact upload succeed.

If the numerical worker fails:
1. Preserve the failed run and its status; do not interpret partial matrices as accepted results.
2. Inspect or expose per-worker stdout/stderr and the first failing morphology/scenario. Focus first on the documented Peng native exit `-11`.
3. Consider a worker isolation change that removes unnecessary NEURON Import3D/segment mapping from the CableTree-only q25 experiment, but validate exact SWC-node/electrical-index mapping against the existing canonical port construction before adopting it.
4. Re-run the same pinned protocol only after a code/test change explains the failure.

## Scientific limits

Four individual morphologies are not a population. This study is passive linear-RC only; it does not validate active channels, spikes, synapses, plasticity, calcium signalling, metabolism, cognition or biological function. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 has no-diameter metadata. Keep absolute NRMSE and percentage-point deltas beside error ratios.


## Worker-isolation update — 26 November 2026

The initial PR #35 workflow run [45764442287](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45764442287) was launched before the SWC-only worker revision and is still tracked separately. The worker has since been changed to construct canonical seven-port and q25 node indices directly from the pinned SWC instead of calling NEURON Import3D. This removes a native subsystem that the CableTree numerical reduction does not need.

Compatibility gates now pin the legacy q25 and spatial holdout node IDs for the three SWC files present in the repository (Peng, Tamas and Jacobs); Allen remains covered by runtime distinctness/collision checks and its pinned source checksum. The test suite now includes a synthetic branched SWC layout test. The workflow concurrency key was separated so the revised SWC-only run does not have to wait behind the older Import3D run.

The revised run's full numerical result is still pending. Do not treat the older run or its partial execution state as accepted data.


## SWC mapping audit — pinned node identities

The repository-resident SWC files were independently re-read and the deterministic node maps were recomputed using the same parent-to-child path-distance accumulation and Python rank-rounding convention as the runner.

| Morphology | Type-3 nodes | Type-4 nodes | Basal q25 / apical q25 | Basal q10 / q95 | Apical q10 / q95 |
|---|---:|---:|---|---|---|
| Peng NMO_163775 | 306 | 298 | 224 / 4096 | 7 / 94 | 3967 / 4042 |
| Tamas NMO_107159 | 1,767 | 1,428 | 6609 / 4404 | 6739 / 7206 | 4355 / 4820 |
| Jacobs NMO_03524 | 816 | 8 | 272 / 864 | 631 / 702 | 863 / 869 |

For all three files, all four q10/q95 nodes are distinct from one another, the seven canonical shared nodes, and both q25 targets. Jacobs has only eight type-4 nodes; its apical q10/q95 values are therefore discrete node-rank endpoints within a very small apical sample, not dense spatial coverage. These identifiers are now enforced as compatibility pins in the runner. The Allen SWC is fetched by CI and is validated at runtime against its pinned SHA-256 and fail-closed node-collision gates.


## Archive completeness update — 26 November 2026

The result metadata schema has been strengthened to record, for every morphology/scenario/schedule basis:
- the exact seven shared SWC node IDs;
- both q25 target node IDs;
- all four held-out SWC node IDs, electrical tree indices, branch labels and path-distance quantiles.

The workflow now validates those maps in addition to the existing exact coverage, D0 parity, Cholesky, orthogonality and DFT gates. Run [45767091643](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45767091643) is queued behind the in-progress first SWC-only computation [45766414695](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45766414695). The in-progress run does not contain this final metadata-schema extension; the queued run is the archival-complete version.


## Reporter utility validation — passed

- Independent report workflow [45767963050](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45767963050) completed success: compileall plus **4/4 tests** passed.
- The reporter verifies all nine manifest file hashes/byte counts, accepted numerical gates, exact case keys, 144 basis/node maps, and paired D0 joins. Its output includes absolute median D0/candidate NRMSE, paired percentage-point deltas, morphology strata, and all nine passive scenarios.
- Report-generation is intentionally skipped until the accepted numerical archive is committed. The numerical matrix and archival-complete run remain pending.


## Current reporting infrastructure status

- Report workflow [45768111004](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768111004) completed success: reporting code compiled, **4/4** tests passed, and the archive-completeness gate correctly skipped report generation because the numerical archive is not yet present.
- The workflow will generate the paired-case Markdown report automatically when the complete 144-row node-map metadata and accepted result manifest are committed. It deliberately refuses to publish results from an incomplete earlier archive.
- Numerical run [45766414695](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45766414695) remains in the four-morphology calculation step; archive-complete run [45767091643](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45767091643) remains queued.


## End-to-end report fixture — passed

- Reporting workflow [45768511692](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768511692) passed: compileall and **5/5 tests in 0.28 s**.
- The fifth test generates a full Markdown report from a synthetic complete archive with 22,464 cases, 144 basis/node maps and nine hash-manifest files. It exercises the real report generator, morphology-stratified output, all nine passive scenarios and absolute NRMSE columns.
- This synthetic fixture validates the reporting pipeline only. It is not scientific simulation data; the real numerical run and archival-complete run remain pending.



## Failure diagnosis and bounded recovery — 26 November 2026

The previously running numerical attempts have now completed and their job logs are available:

- [Run 45766414695](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45766414695) completed all 36/36 morphology/scenario workers (22,464 case rows and 3,744 worker summaries were produced inside the ephemeral runner), but failed during parent-process manifest assembly. The morphology registry stores preflight paths relative to `amsn-core`; the parent process ran from the repository root and incorrectly tried to read `results/...` relative to that root. No accepted result archive or artifact was committed/uploaded, so the temporary matrices from that failed runner must not be treated as a preserved scientific result.
- [Run 45767091643](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45767091643) failed in the first Peng/nominal subprocess with exit `-11` after the SWC-only layout completed and immediately upon entering production D0 PRIMA construction. The available stdout stage markers localize the failure to that call boundary; they do not establish the native root cause. Do not claim the cause is known.

Code and regression changes now pushed:
- `resolve_preflight_path(spec)` resolves registry paths against the absolute AMSN core checkout for both isolated workers and parent manifest assembly.
- `run_worker_with_sigsegv_retry(...)` retries only subprocess exit `-11`, up to two additional clean attempts, deleting partial worker output before each retry. All other exit codes remain fail-fast with their stdout/stderr preserved. Attempt counts and retry counts are recorded in the run report.
- New tests cover cwd-independent preflight resolution, successful retry after a simulated SIGSEGV with output cleanup, and immediate failure for other exit codes.

Latest CI at this handoff revision:
- [Numerical run 45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271), runner-fix commit `32741e56b877fc00f0e16b426ca957336c2b026b`: environment, source verification, compileall and the then-current focused tests passed; the 36-group numerical step was in progress at last inspection.
- [Numerical run 45788063611](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788063611), test commit `c3b47dcf4a9b80dd1dafc0a7687752e2e8492f2e): queued behind the first run and will execute the expanded regression suite plus the complete numerical workflow.
- [Report workflow 45768511692](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768511692) passed 5/5 reporter tests, including a synthetic full-archive fixture. This validates report generation only, not the scientific simulation.

The PR remains Draft. No numerical archive is accepted until exact coverage, all numerical gates, node-map metadata, manifest SHA-256/byte counts, Git commit and Actions artifact upload all succeed. Full Hines remains the canonical reference; no production behavior is changed.


## Worker checkpoint preservation — 26 November 2026

The current runner now retains the isolated worker directories until the complete global archive and its checksum manifest have been written and read back successfully. If any earlier stage raises, completed worker-level `case_metrics.csv`, `summary.csv` and `worker_report.json` files remain under the temporary worker root rather than being removed in `finally`. The workflow has a failure-only `upload-artifact` step that captures `/tmp/prima-q25-dual-seed-workers-*/` for 14 days. The scratch root is removed only once the global manifest is verified as `passed`.

Regression coverage verifies both branches: failed/incomplete global archive retains worker checkpoints, while a complete archive permits cleanup.

Implementation commits:
- Runner checkpoint retention: [ae51876](https://github.com/Nolane-x/Nghien-cuu/commit/ae51876fd0b4bac2eaef27034aa3217130b88318)
- Checkpoint cleanup regression: [c6f5975](https://github.com/Nolane-x/Nghien-cuu/commit/c6f5975fd8e9c993dbf412fdd260d91e76405403)
- Failure-only checkpoint artifact: [94dd28d](https://github.com/Nolane-x/Nghien-cuu/commit/94dd28dd22f78e243ce398dca325fc132a48482c)

At the latest inspection, numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271), based on the earlier bounded-retry patch, was still in the four-morphology numerical step. The newer workflow [45789499169](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45789499169) was pending behind it and contains the checkpoint-preservation changes plus the regression tests. Do not infer numerical progress beyond the state reported by GitHub Actions.


### Checkpoint test import correction — 26 November 2026

Reviewing the new checkpoint cleanup regression exposed a missing import of `cleanup_worker_checkpoints` in the test module. The test itself and helper were present, but the test would have raised `NameError`. This has been corrected in commit [0568971](https://github.com/Nolane-x/Nghien-cuu/commit/056897139dd32da42cb6f4a87dfaaf06fad9260d). Latest workflow [45789829523](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45789829523) was pending at the last check and includes the import fix. The preceding run [45789499169](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45789499169) was cancelled by GitHub's branch concurrency policy when the corrected test commit superseded it.

The earlier numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) was still in progress in its numerical sweep step. Do not treat it as a result for the latest code revision.


## Report provenance and baseline display — 26 November 2026

The global numerical archive now records the live GitHub Actions `GITHUB_RUN_ID` and attempt number. The Markdown reporter uses the archived run ID for its workflow provenance link rather than a hard-coded historical run ID. This prevents a future accepted report from linking to an earlier failed attempt.

The pooled D0 rows now show median absolute D0 NRMSE in both the reference and candidate columns, rather than leaving those fields blank. The end-to-end synthetic reporter fixture asserts the dynamic run URL and an explicit D0 baseline row.

- Runner runtime provenance commit: [ef7b1cb](https://github.com/Nolane-x/Nghien-cuu/commit/ef7b1cb15a415277e98b1680ff52ae78f1893347)
- Reporter correction: [546e67d](https://github.com/Nolane-x/Nghien-cuu/commit/546e67d41a0af019deed041bbfab9ea7b5b62a1c)
- End-to-end regression update: [d49f727](https://github.com/Nolane-x/Nghien-cuu/commit/d49f727395729459e32d6000479af68f1e51aedd)
- Report workflow [45790090210](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790090210) passed the reporter suite at the reporter-only revision; archive-specific report generation was correctly skipped because no accepted numerical archive was present.
- Latest report workflow [45790113319](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790113319) was running the updated end-to-end tests at last inspection.
- Numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) remained in its 36-group sweep. The updated full numerical workflow [45790064294](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790064294) was queued behind it.

These changes improve archive traceability and reporting clarity only; they do not change the passive PRIMA numerical method or any scientific acceptance gate.


### Latest reporter CI validation — passed

Report workflow [45790113319](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790113319) completed success on the dynamic workflow-provenance and D0-baseline report revision. Job logs confirm compileall and **5/5 tests passed in 0.42 s**. The end-to-end test verified a generated report links to the run ID in its synthetic archive and displays the D0 basal-q10 absolute NRMSE row. Archive-specific report generation was correctly skipped because there is still no accepted numerical archive.

Numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) was still at the 36-group calculation step; updated numerical run [45790064294](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790064294), which records its own Actions run ID, was queued behind it.


## 2026-11-26 — live worker telemetry and runtime accounting

- Reviewed the in-flight numerical job and identified why it appeared silent: the parent runner used `subprocess.run(capture_output=True)`, so each worker's existing flushed stage markers were buffered until that entire worker exited.
- Updated `research/run_prima_q25_role_specific_spatial_heldout.py` to inherit the Actions job's stdout/stderr for live stage telemetry, emit an explicit worker-start record, and retain useful retry/failure messages when output is inherited rather than captured.
- Moved the worker stopwatch to the beginning of `worker()`. Previously its `wall_seconds` started only after D0 construction and the full-Hines reference run, understating per-worker elapsed time.
- Added regression tests for inherited output, absence of output capture, timeout configuration, and failure handling when `CompletedProcess.stdout/stderr` are `None`.
- Commits: `262c88198ea4362ff66f709cde7a16e7a2c23d72` and `00e389a478c81709476c563da9fffc2f7e4f8520`.
- CI state at documentation update: legacy numerical run `45788056271` remains in its numerical sweep; run `45790064294` was superseded/cancelled by the newer branch push; the latest streaming-enabled numerical run is queued as `45791629647`. No numerical archive has yet been accepted.
- The independent report-workflow regression run `45790113319` completed successfully (5 tests). This verifies report-generation mechanics only, not the scientific sweep.


### Latest CI queue state — 26 Nov 2026, 09:25 UTC

- `45791623532` (runner streaming code) and `45791629647` (streaming regression tests) were both cancelled while queued, because the next branch push replaced the pending run in the workflow concurrency group.
- The docstring-only follow-up is included in the newest queued run `45791762970`: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45791762970
- Legacy run `45788056271` is still active in its numerical sweep. It predates live log streaming and checkpoint retention.
- The next run, `45791762970`, includes the complete current runner, tests, bounded SIGSEGV retry, and failure checkpoint upload.
- Report mechanics remain verified by `45790113319` (5/5 tests); no accepted numerical archive or scientific conclusion yet.


## Accepted numerical archive — 26 November 2026

Source execution: [GitHub Actions run #45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271), conclusion `success`. The 36 isolated morphology/scenario workers completed with zero native SIGSEGV retries. Wall time was 1,667.54 seconds; worker-process time totaled 1,593.98 seconds (maximum worker 58.74 seconds).

The workflow committed the complete archive as commit `b49a53d5aa31574ce3ae73d68d1a30a1bac17168` and uploaded artifact `prima-q25-role-specific-spatial-heldout-order224` (artifact ID `15102807205`, 595,032 bytes; retained through 24 February 2027). The artifact was downloaded and independently inspected. All nine archive files matched their manifest byte counts and SHA-256 digests.

### Numerical integrity

- 36/36 worker groups; 22,464/22,464 unique case rows.
- 3,744 worker summaries; 416 morphology/window summaries; 936 scenario/window summaries; 104 pooled/window summaries.
- 144/144 finite-record DFT identities; 144 basis metadata rows; 13 distinct observed nodes per morphology.
- D0 exact production-basis parity: passed for every scenario.
- All reduced conductance/capacitance matrices Cholesky-positive; every model reached order 224; seven input ports unchanged.
- Maximum basis orthogonality error: `1.9984014443252818e-15` (< `2e-12`).
- Maximum full-Hines finite-record identity residual: `3.1660560529975156e-12`; reduced residual: `3.591793134473286e-13` (tolerance `2e-8`).

### Descriptive scientific result

Across the four spatial holdouts and both windows, each seed schedule has 1,728 paired cases:

| Schedule | Median candidate/D0 ratio | Median D0 NRMSE (%) | Median candidate NRMSE (%) | Median delta (pp) | Better / worse |
| --- | ---: | ---: | ---: | ---: | ---: |
| BASAL_10K | 0.9789 | 1.9135e-8 | 1.6922e-8 | -4.4300e-13 | 879 / 849 |
| APICAL_10K | 1.1805 | 1.9135e-8 | 2.0869e-8 | +5.8267e-12 | 742 / 986 |
| BOTH_10K | 1.2647 | 1.9135e-8 | 2.2848e-8 | +2.7403e-11 | 700 / 1,028 |

Only 3 of the 12 held-out-label × schedule medians (four locations × three candidate schedules) are below 1. Basal q10 has some median improvement for basal/joint seeds; basal q95, apical q10 and much of apical q95 are mixed or worse, with the joint schedule showing the clearest spatial regressions. Results are not consistent across branch classes or morphology strata.

At the q25 target outputs, matched medians improve substantially under their corresponding role-specific seeds: basal-q25 median ratio is about 0.00203 for BASAL_10K and 0.00228 for BOTH_10K; apical-q25 is about 0.00566 for APICAL_10K and 0.00667 for BOTH_10K. This is evidence of target-local basis specialization in this passive model, not broad spatial transfer.

The D0 held-out median errors are already very small (approximately `8.4e-9%` to `3.6e-8%` across the four labels/windows). Thus ratios can be numerically sensitive; absolute candidate/D0 percentage-point deltas and morphology-specific breakdowns must be considered. No inferential significance or population-level effect is claimed.

### Follow-up engineering status

The latest logging-enabled run `45792818861` showed a repeatable SIGSEGV boundary in the first Peng/nominal worker: it reached `before_production_d0`, then exited `-11` on all three attempts. The failed run had zero completed worker directories, so there was no partial archive to salvage. A subsequent runner revision enables Python `faulthandler`; run `45793076160` is testing that diagnostic change. The successful archive above remains the accepted result; this later failure does not invalidate it, but the current runner's reliability change is not yet cleared.

The report generator now separates q25-target specialization from spatial holdout transfer and computes pooled paired summaries over all four holdouts and both windows. Report workflow runs `45793176156` and `45793184489` are validating report generation and its new assertions.


## Reporting and provenance follow-up — 26 November 2026

- [Report workflow #45793176156](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793176156) completed successfully: archive metadata was accepted, the report was generated from the 22,464 case archive, and the report commit was pushed/reconciled.
- [Report workflow #45793184489](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793184489) completed successfully; compile and the **5-test** report suite passed in 0.38 s, including assertions for the new descriptive spatial verdict and target-vs-holdout separation.
- Generated report: [PRIMA q25 spatial held-out results](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-q25-spatial-heldout-generalization-2026-11-26/research/PRIMA_Q25_ROLE_SPECIFIC_SPATIAL_HELDOUT_RESULTS_2026-11-26.md). It includes pooled schedule results, 12 heldout-label/schedule summaries, four morphology strata, nine passive scenarios, exact node maps, and explicit scientific limits.
- The original successful archive predates recording `GITHUB_RUN_ID` inside its report JSON. The generated Markdown now links explicitly to source numerical run #45788056271 and discloses this provenance limitation; the source run is verified by its GitHub Actions page and artifact.
- Native-crash follow-up: run #45792818861 reproduced a SIGSEGV at the first Peng/nominal production-D0 stage on all three attempts. Python faulthandler was enabled in subprocess invocation. Diagnostic run #45793076160 is active in the numerical step; run #45793084446 is queued with the latest focused tests. Do not replace the accepted archive with an unverified rerun.


## Morphology-level heterogeneity — 26 November 2026

The generated report now adds a direct morphology aggregate: four held-out sites × both windows = 432 paired cases per morphology/schedule.

| Morphology | BASAL_10K median ratio | APICAL_10K median ratio | BOTH_10K median ratio |
| --- | ---: | ---: | ---: |
| NMO_03524 (Jacobs) | 1.215 | 1.242 | 0.9261 |
| NMO_107159 (Tamas) | 1.045 | 1.259 | 1.519 |
| NMO_162186 (Allen) | 1.080 | 1.333 | 1.614 |
| NMO_163775 (Peng) | 0.4748 | 0.9065 | 1.015 |

This makes the heterogeneity explicit: both Tamas and Allen have ratios above 1 for all three candidate schedules; Jacobs improves only under BOTH_10K; Peng improves under the single-branch seed schedules but not the joint schedule. These are per-reconstruction descriptive aggregates, not biological population estimates. The result therefore does not support morphology-independent spatial generalization.

### Report provenance correction

The report regeneration workflow had overwritten a manually corrected source-run link because the legacy numerical report JSON has no `github_actions_run_id`. The report workflow now supplies `AMSN_PRIMA_ARCHIVE_SOURCE_RUN_ID=45788056271` as an explicit fallback; IDs recorded in future numerical archives take precedence. Regression tests cover both cases. A test assertion was also updated to the new “Source numerical workflow” label. Latest provenance/test update commits: `48ef2d0`, `fb24e7d`, `4226bab`, `da76722`.


## Final report pipeline pass — 26 November 2026, 09:41 UTC

- Report workflow [#45794211911](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45794211911) completed successfully.
- All six report tests passed in 0.31 s; archive metadata preflight, complete case-level report generation, and generated-report commit steps all succeeded.
- Verified the generated report now links to source numerical run [#45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271), rather than displaying a missing-run fallback.
- The report now contains the morphology aggregate table and explicit source-run provenance. Report helper prefers a future archive's embedded `github_actions_run_id`, falling back to `AMSN_PRIMA_ARCHIVE_SOURCE_RUN_ID` only for this legacy archive.
- Report generator/test/workflow changes are in commits `48ef2d0`, `fb24e7d`, `4226bab`, `da76722`; report was regenerated and reconciled by the workflow.

The separate numerical reliability diagnostic run #45793076160 remains in progress at its isolated numerical step; the queued latest focused runner test run #45793084446 has not started. The accepted archive from #45788056271 remains authoritative unless a new run finishes and independently clears every gate.


## Follow-on experiment: q25-versus-edge multilocation seed transfer — 26 November 2026

A new preregistered experiment has been added to test the reverse transfer direction. It holds the seven canonical input ports, six primal shifts, order-224 cap, full-Hines reference, four morphologies, nine passive scenarios, sources, pulse widths, windows and all 13 outputs fixed. Only the set of output-dual seed coordinates changes.

New protocol: `research/PRIMA_Q25_MULTILOCATION_OUTPUT_DUAL_SEED_PROTOCOL_2026-11-26.md`.

Five locked schedules:
- D0_none: no output-dual vectors.
- Q25_BOTH_10K: basal/apical q25 seeds.
- BASAL_EDGES_10K: basal q10/q95 seeds.
- APICAL_EDGES_10K: apical q10/q95 seeds.
- BOTH_EDGES_10K: all four q10/q95 edge seeds.

All non-D0 schedules use the same 10-kHz dual shift. The same 13 measured outputs are retained in every schedule. A row is treated as an unseeded transfer readout only for schedules that do not seed it.

Expected coverage: 36 workers; 28,080 case rows; 4,680 group summaries; 520 morphology/window summaries; 1,170 scenario/window summaries; 130 pooled/window summaries; 180 finite-record DFT identities; 180 basis metadata rows. The new runner writes a separate result stem, leaving the accepted q25 spatial archive unchanged.

Implementation:
- Runner: `research/run_prima_q25_multilocation_seed_sweep.py`.
- Unit tests: `research/test_prima_q25_multilocation_seed_sweep.py`.
- Numerical workflow: [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978), currently in its numerical sweep.
- Extra regression run: [#45796720006](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796720006), queued after adding a static guard against stale schedule-registry references.
- First execution [#45796325682](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796325682) passed all preflights and 11 tests, built the first Peng/nominal tree, D0 PRIMA model and full-Hines trace, then stopped on one stale `ROLE_SPECIFIC_SCHEDULES` reference in a later summary loop. The reference was corrected to `MULTILOCATION_SCHEDULES`; this run produced no accepted matrices.
- Report analyzer: `research/analyze_prima_q25_multilocation_seed_results.py`; report tests: `research/test_prima_q25_multilocation_seed_results.py`.
- Report workflow: [#45796600538](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796600538) passed compile and 5/5 tests; archive validation/report generation were correctly skipped because the numerical archive is not yet present.

The older q25 faulthandler diagnostic #45793076160 remains active and the old focused rerun #45793084446 remains queued. They do not block the separate multilocation workflow, and the previously accepted q25 archive/report remain authoritative for the completed prior experiment.


## Multilocation report integration tests — 26 November 2026

- Added an end-to-end synthetic archive test with all five schedules, four morphologies, nine scenarios, 13 outputs and 28,080 paired cases.
- The test exercises nine-file manifest hashing, exact D0 pairing, per-schedule seed label/node metadata validation, and the generated strategy/output/morphology/scenario report tables.
- Report workflow [#45797384246](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797384246) completed successfully: **6 tests passed in 0.44 s**. As expected, real archive validation/report generation were skipped because no accepted multilocation archive exists yet.
- Analyzer independently checks actual CSV read-back counts for all five summary CSVs, not just the numerical report JSON.
- The numerical workflow [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978) remains in its numerical step. Its first predecessor #45796325682 failed on a corrected stale summary-loop constant after 11/11 tests and D0/full-Hines setup; the corrected runner is under execution. No multilocation result is accepted yet.
