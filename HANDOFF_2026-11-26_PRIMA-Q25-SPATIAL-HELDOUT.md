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
