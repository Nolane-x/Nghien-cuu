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
