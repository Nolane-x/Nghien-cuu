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
