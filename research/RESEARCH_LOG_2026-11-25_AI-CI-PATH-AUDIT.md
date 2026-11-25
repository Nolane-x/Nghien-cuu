# Research log — 2026-11-25 CI archival path audit

## Question
Why did the q25 fixed-vs-enriched output-observer workflow fail after completing its numerical analysis, and how can the result-archival failure be corrected without changing the scientific calculation?

## Sources inspected
- GitHub Actions run [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599) and its job log.
- Workflow `.github/workflows/amsn-prima-q25-output-observer.yml` on branch `research/prima-q25-cross-morphology-boundary-replication-2026-11-25`.
- Repository instructions in `AGENTS.md`.

## Diagnosis
The job declares a job-level `defaults.run.working-directory: amsn-core`. The numerical analysis therefore writes its outputs under the process working directory's `results/` directory. The archival step incorrectly passed repository-root-prefixed paths (`amsn-core/results/...`) to `git add` while still running from `amsn-core`. Git consequently looked for `amsn-core/amsn-core/results/...` and exited with code 128.

The failing run's log shows:
- Runtime installation, pinned NumPy/OpenBLAS dispatch verification, source checksum, regression tests and the strict primary-result gate succeeded.
- The full observer analysis completed and emitted report status `passed`; reported wall time was 2,512.5718 seconds.
- The artifact upload succeeded as artifact [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308).
- Only the subsequent Git archival step failed because of the path mismatch. This is a CI packaging failure, not evidence that the numerical analysis failed.

## Change made
- Updated only `.github/workflows/amsn-prima-q25-output-observer.yml`.
- Changed the `git add` arguments from `amsn-core/results/...` to `results/...`, matching the job's declared working directory.
- Added an explanatory comment next to the archival command.
- No solver, numerical method, parameters, morphology data, output values, scientific thresholds or production defaults were changed.

## Verification
- GitHub file was read before update; original blob SHA: `48f8dec90f7a796dbd235ff2543d5554dccae55d`.
- Updated file was read back from the same branch; new blob SHA: `52d1c4ab8e10069431f92882a46e70515287ac5a`.
- Fix commit: `707acd4fcb0ba8daf10a42930e60f5f3bbd16bf3`.
- Push-triggered verification run: [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575). At log creation it had started but had not yet completed; no claim is made that the repaired archival step has passed.
- No local pytest or simulator execution was performed in this session. The passing analysis/test evidence above is taken from the recorded GitHub Actions run, not represented as a local rerun.

## Interpretation limits
The observer run's uploaded artifact is retained evidence, but the result is not treated as fully archived in the branch until a successful post-fix workflow or an independently verified artifact-recovery commit exists. The 112/168/224 basis-order sweep and four-morphology boundary ablation are separate runs and must be evaluated independently. Full Hines remains the canonical reference.

## Next actions
1. Inspect run 45625185575 and verify that its corrected `git add`, rebase and push step complete.
2. Confirm exact result-file paths, commit SHA, row counts and artifact hashes after archival.
3. Review the still-running four-morphology ablation and 112/168/224 basis-order sweep; preserve failures and do not interpret incomplete outputs.
4. Only after those gates pass, update the next dated research handoff with the cross-morphology q25 findings.
