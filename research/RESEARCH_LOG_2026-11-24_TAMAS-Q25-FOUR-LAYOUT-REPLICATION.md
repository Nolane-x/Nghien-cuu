# Research log — Tamas human pyramidal q25 four-layout replication

**Date:** 24 November 2026  
**Branch:** research/prima-tamas-q25-four-layout-replication-2026-11-24  
**Status at creation:** implementation prepared; no simulation result claimed.

## Motivation

The completed NMO_163775 four-layout experiment found that each isolated q25 addition had a modest order-168 shared-output penalty, whereas adding both q25 outputs produced a much larger relative penalty. The next research question is whether that non-additive pattern is morphology-specific or appears on an independent human pyramidal reconstruction.

NMO_107159 is selected because it already has a pinned source, complete-axon provenance, canonical seven-port mapping and a 0.5 µm preflight. It remains a distinct human morphology; results must not be pooled with the Peng mouse sample.

## Design

Four layouts:
1. canonical seven;
2. seven + basal-q25;
3. seven + apical-q25;
4. seven + both q25 outputs.

All layouts preserve the canonical seven SWC node IDs. The preflight q25 IDs are basal = 6609 and apical = 4404. A common script template is rebound to the existing NMO_107159 baseline module, so the scientific protocol, exact coverage guards, frequency matrix construction, pulse settings and matched Hines comparisons remain the same as the Peng experiment.

## Expected coverage

- 72 model configurations.
- 648 frequency matrices.
- 3,456 transient output rows.
- 2,268 shared-output pairs.
- 432 q25-only observations.
- 1,134 shared-Hines comparisons.

## Files created

- `amsn-core/examples/replay_nmo107159_four_layout_replication.py`
- `amsn-core/tests/test_nmo107159_four_layout_replication.py`
- `.github/workflows/amsn-prima-tamas-q25-four-layout-replication.yml`
- `HANDOFF_2026-11-24_TAMAS-Q25-FOUR-LAYOUT-REPLICATION.md`
- This research log.

## Validation limits

No numeric result is claimed at file creation. Verify the exact SWC SHA-256 and q25 node IDs from the independent preflight, then inspect all result tables. This is one human pyramidal passive-RC morphology, not biological validation or a population-level replication. Full Hines remains canonical; no production solver defaults are changed.
