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
