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
