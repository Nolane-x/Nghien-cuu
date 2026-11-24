# Handoff — Tamas human pyramidal q25 four-layout replication

**Date:** 24 November 2026  
**Branch:** research/prima-tamas-q25-four-layout-replication-2026-11-24  
**Parent:** q25 Peng ablation branch / PR #19  
**Morphology:** NMO_107159 Tamas human pyramidal Control  
**Mesh cap:** 0.5 µm

## Research question

Does the non-additive dual-q25 error pattern observed in the NMO_163775 Peng mouse passive-RC ablation reproduce on an independent human pyramidal morphology under the same four-layout protocol?

## Source and port identity

The source SWC is pinned at 7,228 records and SHA-256 `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`. Existing preflight pins the canonical seven SWC nodes `[1, 5564, 6363, 7023, 4301, 4735, 4623]` and q25-only nodes `[6609, 4404]`. The q25 role mapping is basal-q25 = 6609 and apical-q25 = 4404. The source metadata identifies one female human Control-condition pyramidal comparison cell; age is not reported. It is not the rosehip interneuron.

## Four matched layouts

- `seven`: canonical seven ports.
- `eight_basal_q25`: canonical seven + basal-q25.
- `eight_apical_q25`: canonical seven + apical-q25.
- `nine_both_q25`: canonical seven + both q25 probes.

The same 0.5 µm cap, six expansion shifts, orders 112/168, nine passive parameter scenarios, AC grid, source sites, pulse widths and transient settings are retained from the Peng ablation. Every layout receives an independently generated full-Hines reference. Shared outputs are joined by SWC node identity.

## Expected exact coverage

- 72 model configurations.
- 648 frequency matrices.
- 3,456 per-port transient rows.
- 2,268 matched shared-output pairs versus seven-port.
- 432 q25-only output observations.
- 1,134 shared-Hines comparisons.

The workflow must pass checksum verification, regression tests, Import3D preflight, exact node-set guards, Hines consistency, exact coverage, result archival and artifact upload before numeric conclusions are claimed.

## Scientific constraints

This is one human morphology, not a population. NeuroMorpho lists Diameter, 3D and Angles for this specimen, but passive membrane parameters remain model assumptions. The experiment remains passive linear-RC numerical validation; it does not validate active channels, synapses, plasticity or biological behavior. Keep NMO_107159 separate from the mouse mesh stratum despite both using a 0.5 µm cap. Full Hines remains canonical and no production defaults change.
