# Research log — q25 role-specific spatial held-out generalization

**Date:** 26 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-spatial-heldout-generalization-2026-11-26  
**Parent source revision:** 831d0892e587b9c5a51f6347b54ba5d155ac157f

## Question and hypothesis

The accepted four-morphology output-aware q25 study builds output-dual basis vectors only for basal-q25 and apical-q25. The next question is whether this enrichment improves reduced-model predictions away from the optimized q25 observation locations.

Hypothesis (not yet tested): q25 dual seeds may improve some unseeded dendritic readouts through shared state-space directions, but that effect may vary by morphology, branch and path-distance quantile. A reduction in q25 error does not imply spatially uniform accuracy.

## Sources inspected

- AGENTS.md and the dated research handoff files.
- HANDOFF.md and research/AMSN_RESEARCH_DOSSIER.md.
- The active q25 four-morphology role-specific sweep protocol, runner, tests and workflow.
- The accepted four-morphology output-aware dual-seed results and Jacobs role-specific seed-allocation results.
- Existing human_fine_mesh_passive_dc_audit.py and human_prima_port_enrichment.py mapping logic.
- Existing output-aware PRIMA builder and finite-record backward-Euler DFT identity implementation.
- GitHub Actions run 45760007155 was still in progress at the time of initial inspection; it is a separate parent experiment and must not be treated as a completed result.

## Design decision

Use four preregistered path-distance readouts: basal q10/q95 and apical q10/q95. They must be distinct from the seven canonical shared nodes and both q25 nodes. They are appended only to the observation map; they are not inserted into the seven-port input matrix or the q25 dual-seed selector.

The same four role-specific schedules, basis order 224, six primal shifts, four morphology sources, nine passive parameter scenarios, three stimulus sources, two pulse widths, two windows, pinned numerical environment, and Hines reference are retained. This isolates the question of off-target spatial prediction.

## Implementation in this checkpoint

- Added a research-only runner derived from the reviewed role-specific q25 sweep runner.
- Added a fail-closed map validator for four distinct held-out SWC node IDs.
- Added held-out readouts to the full-Hines and reduced-model observation maps without changing the input selector or output-dual seed set.
- Expanded output metrics from 9 to 13 rows per schedule (seven shared, two q25 targets, four spatial holdouts).
- Locked expected coverage at 22,464 case metrics, 3,744 worker summaries, 416 morphology/window summaries, 936 scenario/window summaries, 104 pooled/window summaries, and 144 finite-record DFT identity summaries.
- Added a preregistered protocol, focused tests and a dedicated GitHub Actions workflow.

## Validation status

No local Python test or simulation is claimed in this log. The dedicated GitHub Actions workflow performs compileall, focused pytest, source checksum/preflight, NumPy dispatch checks, D0 exact parity, basis/Cholesky/orthogonality checks, full-Hines comparison, exact CSV read-back and finite-record DFT identity checks.

The run is not accepted until every worker, exact coverage gate, DFT identity, archival commit and artifact upload succeeds. Any morphology whose quantile mapper yields colliding nodes will fail closed rather than silently substituting a different location.

## Limits

Four individual morphology reconstructions are not a biological population. The model is passive linear-RC only. A q10/q95 prediction is a spatial numerical holdout within a known morphology, not a biological holdout subject. Ratios must be read beside absolute NRMSE and absolute percentage-point deltas. No production solver/default changes are made.

## Next step

Inspect the dedicated Actions run, repair any failed mapping or numerical gate with a documented code/test change, then publish the validated result report and update HANDOFF.md only after the result is accepted.


## Worker isolation revision — 26 November 2026

Inspection showed that the q25 experiment only needs SWC node identities and the exact passive CableTree. NEURON Import3D section/segment locations are not consumed by the CableTree Hines or reduced-state calculation. The runner has therefore been revised to build the canonical seven input nodes and q25 observation nodes directly from the pinned SWC, avoiding native Import3D instantiation in every morphology/scenario worker.

Compatibility is preserved deliberately:
- The seven legacy source/probe nodes use the same NumPy path-length arithmetic as the existing fine-mesh mapper.
- The q25 target nodes use the amsn.ports path-distance/quantile implementation used by the original q25 enrichment mapper.
- Three available SWC files have pinned q25 and q10/q95 node identities. The fourth (Allen) is still checked by fail-closed uniqueness/collision guards at runtime.
- An additional synthetic SWC test exercises canonical seven-port mapping and all four held-out output rows without NEURON.

This change narrows the native code surface; it does not change the passive electrical model, input selector, basis construction, stimulation protocol, or numerical gates. The first pre-revision run remains separate and must not be combined with a rerun.


## SWC mapping audit — pinned node identities

The repository-resident SWC files were independently re-read and the deterministic node maps were recomputed using the same parent-to-child path-distance accumulation and Python rank-rounding convention as the runner.

| Morphology | Type-3 nodes | Type-4 nodes | Basal q25 / apical q25 | Basal q10 / q95 | Apical q10 / q95 |
|---|---:|---:|---|---|---|
| Peng NMO_163775 | 306 | 298 | 224 / 4096 | 7 / 94 | 3967 / 4042 |
| Tamas NMO_107159 | 1,767 | 1,428 | 6609 / 4404 | 6739 / 7206 | 4355 / 4820 |
| Jacobs NMO_03524 | 816 | 8 | 272 / 864 | 631 / 702 | 863 / 869 |

For all three files, all four q10/q95 nodes are distinct from one another, the seven canonical shared nodes, and both q25 targets. Jacobs has only eight type-4 nodes; its apical q10/q95 values are therefore discrete node-rank endpoints within a very small apical sample, not dense spatial coverage. These identifiers are now enforced as compatibility pins in the runner. The Allen SWC is fetched by CI and is validated at runtime against its pinned SHA-256 and fail-closed node-collision gates.


## Interpretation gates locked before results

The protocol now makes absolute NRMSE percentage-point deltas primary when D0 is near the numerical floor; candidate/D0 ratios are secondary. Basal/apical and q10/q95 readouts must remain separate. A pooled median alone is explicitly insufficient: the interpretation must inspect all four morphology strata and both branch classes. A result that improves only q25 targets is target-local basis specialization, not spatial generalization.


## Post-hoc reporting utility

Added research/analyze_prima_q25_spatial_heldout_results.py. It is intentionally separate from the numerical runner. It verifies the archive manifest's byte counts and SHA-256 digests, re-pairs every candidate case to its exact D0 key, recomputes medians/P90/worst ratios and absolute NRMSE deltas, validates the archived SWC node map, and writes a morphology-stratified Markdown results report. The reporting workflow will be activated only after the archival-complete numerical run has produced the required metadata.


## Report utility CI — passed

The independent reporting workflow [45767963050](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45767963050) completed **success**. Both reporter scripts passed compileall and all four unit tests passed, covering percentile interpolation, paired candidate/D0 absolute NRMSE summaries, four-morphology node-map shape, and fail-closed collision detection. The report-generation step was correctly skipped because no accepted numerical archive existed at this checkpoint.

The report now includes median absolute D0 NRMSE and candidate NRMSE (not only ratios and deltas), and a held-out breakdown across all nine passive parameter scenarios. This avoids hiding near-zero denominators and makes parameter-specific regressions visible.


## Report workflow validation — latest success

Report workflow [45768111004](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768111004) completed **success** on the current branch head. Compileall passed and the four reporting tests passed. Its archive-completeness preflight correctly skipped report generation because the numerical result archive is not present yet. This is an expected successful validation of the reporting path, not a numerical-result claim.


## End-to-end reporting archive fixture — passed

Reporting workflow [45768511692](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768511692) completed success. Compileall passed and **5/5 tests passed in 0.28 s**. The added fifth test builds a full synthetic archive with 22,464 paired case rows, 144 basis/node metadata rows and nine hash-manifest entries, then executes the full Markdown report generator. It verifies pooled, morphology-stratified and nine-scenario tables, plus the absolute D0/candidate NRMSE columns. This validates report mechanics only; it is not a simulated-neuron result.



## Failure diagnosis and recovery patch — 26 November 2026

The completed job logs clarified two independent failures:

1. **Run 45766414695** finished all 36/36 isolated workers, each with 624 case rows and 104 worker summaries. It then raised `FileNotFoundError` while building the global morphology manifest because registry `preflight` paths are relative to `amsn-core`, but the parent process reads them while running from the repository root. The matrices were only in an ephemeral Actions workspace and were neither archived nor uploaded. They are not an accepted or retrievable numerical archive.
2. **Run 45767091643** exited `-11` in `NMO_163775/nominal`. Stage markers show SWC-only layout construction completed and the crash occurred after entering the production D0 PRIMA construction call. This localizes the failing boundary but does not identify why native execution terminated; no backtrace was available, so the underlying cause remains unproven.

### Implemented fixes

- Added a single cwd-independent preflight resolver that anchors all relative registry paths to the absolute `AMSN_CORE` directory. Both worker preflight loading and parent manifest assembly use it.
- Added bounded retry for isolated workers that return exactly `-11`: at most two retries after the initial attempt, with the worker output directory deleted before each retry. Non-SIGSEGV exit codes still fail immediately and preserve diagnostic stdout/stderr. Per-worker attempts and total retries are included in the numerical report.
- Added regression tests for cwd-independent resolution, cleanup/retry after a simulated SIGSEGV, and fail-fast behavior for an ordinary nonzero worker exit.

### Validation after the patch

- Numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) checked out runner-fix commit `32741e56b877fc00f0e16b426ca957336c2b026b`. At the last inspection, setup, pinned source/checksum validation, SIMD preflight, compileall and the then-current focused test step had passed; the four-morphology numerical sweep was still running.
- Numerical run [45788063611](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788063611) was queued for the subsequent test commit `c3b47dcf4a9b80dd1dafc0a7687752e2e8492f2e`, which adds the three reliability regression tests.
- The report workflow [45768511692](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45768511692) passed 5/5 tests using a synthetic complete archive. It confirms reporter mechanics only and must not be represented as neuron simulation evidence.

No spatial-generalization result has been accepted. The next acceptance checkpoint remains exact coverage and case-key uniqueness; D0 production parity; Cholesky positive definiteness; order-224 basis and orthogonality; all 144 finite-record DFT identities; exact 144-row SWC node metadata; nine-file manifest hashes; Git archive commit; Actions artifact upload; and successful generation of the report from the actual archive. PR #35 must remain Draft until all are verified.


## Worker checkpoint preservation revision — 26 November 2026

The earlier runner's `finally` block deleted the temporary output from all completed worker processes even when a subsequent worker or the parent archive stage failed. This created an avoidable loss of evidence. The runner now retains its per-worker CSV and JSON files whenever global archive creation does not complete. A failure-only Actions artifact step uploads any retained worker checkpoints for 14 days. Once the global CSVs, report and manifest are written and the manifest is read back with `status == "passed"`, the scratch directory is removed.

A regression test exercises both cleanup states. The latest workflow commit is [94dd28d](https://github.com/Nolane-x/Nghien-cuu/commit/94dd28dd22f78e243ce398dca325fc132a48482c). Its run [45789499169](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45789499169) was pending behind earlier numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271), which had not yet left the numerical sweep step at last inspection.

This change improves reproducibility and failure diagnosis; it is not scientific evidence and does not relax any acceptance gate.


## Checkpoint regression import correction — 26 November 2026

A final source review found that the new checkpoint cleanup regression used `cleanup_worker_checkpoints` without importing it in the test module. The import is now explicit in commit [0568971](https://github.com/Nolane-x/Nghien-cuu/commit/056897139dd32da42cb6f4a87dfaaf06fad9260d). The earlier pending checkpoint workflow was superseded/cancelled by branch concurrency; corrected workflow [45789829523](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45789829523) was pending behind active numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) at the last check.

This correction is a test harness fix only. It does not change the numerical method or provide scientific simulation evidence.


## Report provenance and D0 baseline revision — 26 November 2026

The numerical runner now records the actual GitHub Actions run ID and attempt in the global report JSON. The post-hoc Markdown reporter links to that archived run ID dynamically, removing the old static link to failed run 45767091643. Its pooled D0 rows now report the median absolute D0 NRMSE in both the reference and candidate columns (the two values match), instead of displaying blank values.

The end-to-end reporter fixture now asserts the dynamic run URL and the complete basal-q10 D0 pooled row. Reporter run [45790090210](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790090210) completed success on the reporter-only revision; the archive gate skipped report generation as there is no accepted numerical archive yet. Updated reporter tests [45790113319](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790113319) were running at last inspection. Updated numerical run [45790064294](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790064294) was pending behind numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271).

This revision changes traceability and reporting only. It does not change the model, numerical protocol or acceptance criteria.


## Latest reporter CI — passed

The updated report workflow [45790113319](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790113319) completed success. Compileall passed and the complete report test module passed **5/5 in 0.42 s**. Its end-to-end synthetic archive test confirms that the output workflow link is derived from the report JSON run ID and that the D0 pooled row carries its median absolute baseline NRMSE. The real archive gate skipped generation correctly because no accepted numerical simulation archive exists yet.

At the same observation point, numerical run [45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) was still running the 36-group sweep, and the updated run [45790064294](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45790064294) remained pending behind it.


## 2026-11-26 — execution observability and timing correction

The numerical runner previously used captured child-process output. Although each worker emitted flushed stage markers, the parent hid them from the Actions log until a subprocess completed. The worker runner now inherits stdout/stderr so stage markers appear live in the workflow, prints an explicit worker-start record, and formats failure diagnostics correctly when output was streamed instead of captured.

A timing review also found that the per-worker stopwatch began after D0 production reduction and the full-Hines reference solve. It now begins at entry to `worker()`, making the reported worker duration include setup, morphology conversion, D0, Hines, enriched-basis construction, and reduced simulations.

Regression tests were added for the inherited-output execution contract and no-captured-stream failure path. Commits: `262c88198ea4362ff66f709cde7a16e7a2c23d72`, `00e389a478c81709476c563da9fffc2f7e4f8520`.

Current execution record: legacy run `45788056271` is still in the numerical step; superseded run `45790064294` is cancelled; streaming-enabled run `45791629647` is pending behind the active run. Report workflow `45790113319` passed 5/5 report tests, but no scientific result is accepted until the full 36-worker archive passes all coverage, parity, positivity, orthogonality, DFT, and checksum gates.


### Latest CI queue state — 26 November 2026, 09:25 UTC

The two intermediate queued pushes (`45791623532` and `45791629647`) were superseded before start by a subsequent runner-docstring correction. The latest complete code/test revision is queued in `45791762970`. Legacy numerical run `45788056271` remains active and predates live streaming/checkpoint retention. Report mechanics pass in `45790113319` (5/5). No scientific archive has been accepted.


## 2026-11-26 — accepted q25 spatial holdout numerical archive

### Provenance and acceptance

GitHub Actions run [#45788056271](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45788056271) completed successfully. All 36 isolated morphology/scenario workers completed with zero SIGSEGV retries. Runtime: 1,667.54 s wall, 1,593.98 s summed worker time, maximum worker 58.74 s. The run committed archive commit `b49a53d5aa31574ce3ae73d68d1a30a1bac17168` and uploaded artifact ID `15102807205` (595,032 bytes).

The artifact was downloaded for independent inspection. Its nine files all match the manifest's exact byte counts and SHA-256 values. Exact coverage: 36/36 workers; 22,464 unique case rows; 3,744 group summaries; 416 morphology/window summaries; 936 scenario/window summaries; 104 pooled/window summaries; 144 DFT identities; 144 basis metadata rows.

Numerical gates passed: D0 production parity on all scenarios; positive-definite reduced G/C by Cholesky; order 224 everywhere; seven input ports unchanged; maximum basis orthogonality error `1.9984014443252818e-15`; all DFT identities pass with max full-Hines residual `3.1660560529975156e-12` and max reduced residual `3.591793134473286e-13`, versus tolerance `2e-8`.

### Main observation

Across all four independent spatial holdouts and both windows there are 1,728 paired candidate/D0 cases per schedule. BASAL_10K has median ratio 0.9789, median absolute delta `-4.4300e-13` percentage points, 879 better / 849 worse. APICAL_10K has median ratio 1.1805, median delta `+5.8267e-12` pp, 742 better / 986 worse. BOTH_10K has median ratio 1.2647, median delta `+2.7403e-11` pp, 700 better / 1,028 worse. Only 3/12 held-out-label × schedule medians are below 1. Improvement is not consistent across basal/apical branch classes, four morphology strata, or candidate seed roles.

At the q25 target locations themselves, role-specific seeding is strongly specialized: basal-q25 median ratio about 0.00203 under BASAL_10K and 0.00228 under BOTH_10K; apical-q25 about 0.00566 under APICAL_10K and 0.00667 under BOTH_10K. The contrast supports target-local basis enrichment, not broad spatial generalization.

D0 held-out median NRMSE values lie around `8.4e-9%` to `3.6e-8%` across labels/windows. Because this is already a very small error range, ratios should not be used alone; paired absolute deltas and strata must be read together. This descriptive experiment provides no inferential p-values or population-level biological claim.

### Later runner diagnostic

Run `45792818861` reached the first Peng/nominal worker's `before_production_d0` marker and then returned SIGSEGV (`-11`) on all three bounded attempts. No worker output directory had been completed. A later runner revision added Python `faulthandler`; run `45793076160` is examining the stack trace. This failure concerns repeatability of the current runner revision and does not alter the separately archived successful run `45788056271`.

The reporting utility is being extended to publish both target-q25 and spatial-holdout aggregate summaries, avoiding a single pooled metric that could conceal branch-specific regressions.


## 2026-11-26 — report generation accepted

Report workflow [#45793176156](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793176156) completed: it accepted the archived metadata, generated the 552-line result report from the case-level archive, and reconciled the report commit. The report includes the descriptive aggregate schedule table, all 12 held-out output/schedule medians, q25-target summaries, morphology/scenario breakdowns, and node maps.

Report workflow [#45793184489](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793184489) passed compile and all 5 reporting tests (0.38 s), including the new target-vs-spatial summary section checks. The report links to numerical source run #45788056271 because the accepted archive was generated before source Actions run IDs were recorded in its JSON metadata; this limitation is explicitly disclosed in the report.

A later numerical retry run [#45792818861](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45792818861) failed reproducibly at Peng/nominal `before_production_d0` (SIGSEGV on three consecutive attempts). Python faulthandler is now enabled for child workers; diagnostic run #45793076160 is active and run #45793084446 is queued. The already accepted run #45788056271 and its checksummed archive remain the source of results.


## 2026-11-26 — morphology-level heterogeneity and report provenance

The generated report now explicitly aggregates the four unseeded spatial outputs across both windows by morphology, 432 paired cases per schedule:

| Morphology | BASAL_10K median ratio | APICAL_10K median ratio | BOTH_10K median ratio |
| --- | ---: | ---: | ---: |
| NMO_03524 (Jacobs) | 1.215 | 1.242 | 0.9261 |
| NMO_107159 (Tamas) | 1.045 | 1.259 | 1.519 |
| NMO_162186 (Allen) | 1.080 | 1.333 | 1.614 |
| NMO_163775 (Peng) | 0.4748 | 0.9065 | 1.015 |

Both Tamas and Allen worsen under every candidate schedule. Jacobs improves only with BOTH_10K. Peng improves with its single-branch schedules, but not the joint schedule. This is strong morphology dependence within the tested reconstructions and rules out a morphology-independent generalization claim. These aggregates are descriptive, not inferential or population-level.

The report workflow now gets a legacy source-run fallback from `AMSN_PRIMA_ARCHIVE_SOURCE_RUN_ID=45788056271`, while preferring an Actions run ID present in future archive JSON. This is necessary because the accepted archive predates run-ID capture. Added tests for that fallback and updated the rendered-label assertion. Commits: `48ef2d0`, `fb24e7d`, `4226bab`, `da76722`.


## 2026-11-26 09:41 UTC — final report pipeline acceptance

Report workflow [#45794211911](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45794211911) passed. Six tests passed in 0.31 s; archive completeness, report generation and report commit steps succeeded. The generated Markdown now carries the explicit source link to numerical run #45788056271 and the four-morphology aggregate table. The analyzer prefers a `github_actions_run_id` embedded in future numerical archives and uses the workflow-provided legacy source-run fallback only when absent. Tests cover both paths.

The independent numerical runner diagnostic #45793076160 is still active; latest runner-focused test #45793084446 remains queued. The accepted 36-worker archive is unchanged and remains the authoritative scientific data.


## 2026-11-26 — q25-versus-edge multilocation seed transfer experiment

A separate protocol and runner were added to test whether edge-location dual seeds transfer inward to q25 readouts, and whether q25 seeds transfer outward to the four edge readouts. The seven input ports, six primal shifts, order224 basis, full-Hines reference, 13 outputs and all simulation dimensions are unchanged.

Locked schedules (all non-D0 dual shifts = 10 kHz): D0_none; Q25_BOTH_10K; BASAL_EDGES_10K; APICAL_EDGES_10K; BOTH_EDGES_10K. Edge seed coordinates are the existing pinned q10/q95 SWC readout mappings; q25 coordinates are the existing pinned q25 map. No schedule is selected post hoc.

Exact expected coverage: 36 workers; 28,080 case rows; 4,680 worker summaries; 520 morphology/window summaries; 1,170 scenario/window summaries; 130 pooled/window summaries; 180 finite-record DFT identities; 180 basis metadata rows.

Files added:
- `research/PRIMA_Q25_MULTILOCATION_OUTPUT_DUAL_SEED_PROTOCOL_2026-11-26.md`
- `research/run_prima_q25_multilocation_seed_sweep.py`
- `research/test_prima_q25_multilocation_seed_sweep.py`
- `research/analyze_prima_q25_multilocation_seed_results.py`
- `research/test_prima_q25_multilocation_seed_results.py`
- `.github/workflows/amsn-prima-q25-multilocation-seed-sweep.yml`
- `.github/workflows/amsn-prima-q25-multilocation-seed-report.yml`

First run [#45796325682](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796325682) passed preflight and 11 tests but hit a stale schedule-registry name in the worker summary loop, after D0/full-Hines construction. No outputs were accepted. Fixed the loop to use `MULTILOCATION_SCHEDULES`; added a static regression assertion. Corrected numerical run [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978) is in the numerical sweep, and regression run [#45796720006](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796720006) is queued.

The dedicated report pipeline passed [#45796600538](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796600538): report analyzer/tests compile, 5/5 tests passed; archive validation and report generation were skipped because there is no accepted multilocation archive yet. Do not claim results until the full 28,080-case archive passes exact coverage, numerical and checksum gates.


## 2026-11-26 — multilocation report end-to-end test

Added a synthetic complete archive test covering all five seed schedules, four morphology strata, nine passive scenarios, 13 outputs and 28,080 paired case records. It builds a nine-file checksummed manifest and validates D0 pairing, exact per-schedule seed metadata and generated strategy/output/morphology/scenario report tables.

Report workflow [#45797384246](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797384246) passed compile and all six report tests in 0.44 seconds. Since no accepted multilocation numerical archive exists yet, archive-dependent generation was skipped. The analyzer now also reads and checks actual row counts from all five summary CSVs, rather than trusting JSON coverage values alone.

Numerical workflow [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978) remains in its numerical step; its predecessor #45796325682 exposed and localized a stale schedule registry name in a post-simulation summary loop. The corrected runner is executing. No multilocation scientific result has been accepted.


## 2026-11-26 — matched seed-budget controls and analyzer regression tests

The analysis protocol now identifies Q25_BOTH_10K, BASAL_EDGES_10K and APICAL_EDGES_10K as the primary resource-matched comparison: two requested dual sites, one 10-kHz shift. BOTH_EDGES_10K requests four sites and must be interpreted as a higher-budget coverage condition rather than a pure seed-location comparison.

The result analyzer reports both requested sites and observed accepted initial dual columns (median/min–max over 36 morphology/scenario cells), validates that accepted rank does not exceed requested sites, and requires zero accepted output-dual columns for D0.

Synthetic archive report workflows [#45797853943](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797853943) and [#45797861246](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797861246) both passed 7/7 tests (0.43 s and 0.47 s respectively). The numerical sweep [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978) remains active; queued rerun [#45797716852](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797716852) includes protocol and static-regression updates. No accepted multilocation archive yet.


## 2026-11-26 — schedule-specific seed-target/transfer split

The multilocation analyzer now applies the exact per-schedule seed mask before constructing transfer aggregates:
- q25 seeds → q25 is reported as seed-target accuracy and all four edges as unseeded transfer.
- basal edge seeds → basal edge rows are seed-target accuracy; q25 and apical edges are unseeded transfer.
- apical edge seeds → apical edge rows are seed-target accuracy; q25 and basal edges are unseeded transfer.
- four-edge seeds → all edge rows are seed-target accuracy; q25 is unseeded transfer.

This avoids treating an output as a holdout for the same schedule that used it to construct dual seeds. Seeded and unseeded medians/counts now appear separately in the strategy, morphology and scenario tables. Empty transfer families display zero count and an em dash for metrics.

Report workflow [#45799248302](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45799248302) passed 7/7 tests (0.42 s), including a synthetic full archive with exact schedule-specific transfer row assertions. Actual archive report generation was skipped because no numerical archive is present. Numerical run #45796697978 remains active.


## 2026-11-26 — final analyzer tests for transfer masking and build cost

The report generator now applies the schedule-specific seed mask to every aggregate: seed targets are reported separately, and only unseeded q25/edge outputs enter transfer summaries. Morphology/scenario tables use the same split. It also reports accepted initial dual rank, median/P90 basis construction time, maximum reduced G/C condition numbers and orthogonality error by schedule.

Report workflow [#45799887740](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45799887740) passed all 7 tests in 0.41 seconds after adding the synthetic archive metadata. Report generation from real numerical data was correctly skipped because the new archive is still pending. Numerical run #45796697978 remains active.


## 2026-11-26 — independent q25 rerun reproduces exact numerical archive

Faulthandler-enabled numerical run [#45793076160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793076160) completed successfully: 36/36 workers, zero native SIGSEGV retries, one process attempt per worker. All exact coverage, D0 production parity, reduced G/C positivity, order 224, seven-port invariance, basis orthogonality and 144 DFT identity gates passed.

The artifact (ID `15106218185`, 595,050 bytes) was downloaded and verified. All nine manifest files match their exact SHA-256/byte counts. Crucially, all six numerical CSVs are byte-identical to the earlier accepted archive from #45788056271. Across all 144 metadata rows, basis/input/reduced-G/reduced-C hashes, node maps, seed metadata, actual order, orthogonality and condition numbers are also identical. Only per-worker `wall_seconds` changed; report JSON changed in runtime/provenance/CPU diagnostic fields.

Runtime: 2,516.24 s wall; worker time 2,501.26 s; max worker 93.97 s. Zero retries. Earlier failed re-run #45792818861 had SIGSEGV on Peng/nominal at production D0; the successful full rerun shows that failure was not reproduced, though its original native root cause remains unknown.

Report workflow [#45801634554](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45801634554) passed 6/6 tests and regenerated the report to point to source numerical run #45793076160.

## 2026-11-26 — final accepted q25 reproducibility and multilocation result

### q25 spatial-heldout rerun

Run [#45793076160](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793076160) completed successfully with 36/36 workers, zero SIGSEGV retries and every numerical gate passing. Artifact [15106218185](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45793076160/artifacts/15106218185) passed independent nine-file SHA-256/byte-count verification. The six numerical CSV files are byte-for-byte identical to the earlier accepted run #45788056271; all 144 model basis/input/G/C hashes and mapping/rank/conditioning/orthogonality metadata are identical. Only wall-time and runtime/provenance diagnostics differ. The original SIGSEGV cause remains unresolved because the successful rerun did not reproduce it.

### Multilocation seed-transfer numerical run

Run [#45796697978](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978) passed all 36 isolated workers and all numerical gates. Exact coverage: 28,080 case metrics; 4,680 worker summaries; 520 morphology/window summaries; 1,170 scenario/window summaries; 130 pooled/window summaries; 180 finite-record DFT identities; 180 basis metadata rows; 28,080 unique case keys.

D0 exactly matched production multishift PRIMA. All models reached order224, retained exactly seven input ports, all reduced G/C passed Cholesky, maximum basis orthogonality error was 2.220446049250313e-15, and all DFT identities passed (max Full-Hines residual 3.1660560529975156e-12; max reduced residual 3.6403602430240796e-13; tolerance 2e-8). Runtime: 3,010.96 s wall; zero worker SIGSEGV retries.

Artifact [15109150731](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45796697978/artifacts/15109150731) (752,900 bytes) was downloaded and independently checked against all nine manifest SHA-256 hashes and byte counts; archive contents correspond to the committed Git files.

### Interpreted result

Three primary schedules use a matched two-coordinate seed budget: Q25_BOTH_10K, BASAL_EDGES_10K and APICAL_EDGES_10K. BOTH_EDGES_10K uses four coordinates and is interpreted as a higher-budget coverage condition.

The seeded readout families show large reductions versus D0 (median candidate/D0 ratios 0.004211, 0.003165, 0.008682, and 0.007064 respectively; BOTH_EDGES is the four-seed condition). However, all available pooled unseeded-transfer families have median ratios above one: Q25_BOTH edge transfer 1.265; BASAL_EDGES q25 1.330 and opposite-edge 1.087; APICAL_EDGES q25 1.712 and opposite-edge 1.614; BOTH_EDGES q25 2.187.

The morphology-stratified analysis prevents a universal statement: Jacobs has q25-to-edge transfer ratio 0.9261, and Peng has basal-edge-to-apical-edge transfer ratio 0.5063. The pooled pattern is consistent with target-local specialization rather than broad spatial generalization in this passive linear-RC setting. These are descriptive medians; absolute percentage-point changes matter because D0 residuals are often near the numerical floor.

Final generated report: research/PRIMA_Q25_MULTILOCATION_OUTPUT_DUAL_SEED_RESULTS_2026-11-26.md. Report CI [#45815168477](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45815168477) passed 7/7 tests in 0.58 seconds, full manifest/source/hash validation, full Cartesian pairing check, generation and commit.

A duplicate numerical workflow [#45797716852](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45797716852) passed its numerical/archive checks but failed only at a duplicate add/add Git rebase when it attempted to commit files already committed by primary run #45796697978. The primary run and its archive remain authoritative.