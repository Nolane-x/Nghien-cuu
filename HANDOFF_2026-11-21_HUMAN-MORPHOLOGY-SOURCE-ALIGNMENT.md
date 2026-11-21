# Handoff — independent human morphology source-alignment replication

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Scope:** replicate transient and AC source-placement audits on a third human morphology, NMO_290988 / 1094_Mohan_etal_2015  
**Status:** workflow committed; six morphology/mesh jobs pending.

## Why this cell

The current source-placement result is strong for NMO_68175 but mixed for NMO_68174. A third morphology is required before generalizing the source rule.

The additional fixture already present in the repository is:
- NeuroMorpho.Org record NMO_290988 / API ID 290988;
- standardized file amsn-core/data/human/1094_Mohan_etal_2015.CNG.swc;
- 8,903 SWC records, 3 soma points, 4,051 basal dendrite points, 4,849 apical dendrite points, no axon;
- human adult middle temporal gyrus, Brodmann area 21, layer 2–3 principal/pyramidal reconstruction;
- dendritic completeness is marked moderate; the metadata records mesiotemporal sclerosis and does not report shrinkage correction.

This is a distinct neuron record and source archive from the two Segev fixtures, but it shares a broad cortical region/class. It is not a healthy-control sample. Preserve the CC BY 4.0 attribution in amsn-core/data/human/README.md.

## Matrix

Three morphologies × two NEURON mesh caps:
- NMO_68174 / cell1125: 0.125 and 0.0625 µm.
- NMO_68175 / cell1204: 0.125 and 0.0625 µm.
- NMO_290988 / Mohan 2015: 0.125 and 0.0625 µm.

Every job:
1. runs the complete 81-test AMSN suite;
2. checks the exact SWC record count and that all three source/five probe sites map through Import3D;
3. runs the passive transient nearest-centre vs weighted two-centre source-placement audit at dt=0.05 ms;
4. runs the passive AC exact-SWC / nearest-centre / weighted source audit at eight frequencies;
5. uploads raw trace/transfer CSVs, summaries and logs.

Expected per morphology/mesh:
- transient: 18,030 trace rows and 60 summary rows;
- AC: 1,080 raw transfer rows and 135 grouped summary rows.

## Interpretation limits

NMO_290988 has no axon and only moderate dendritic completeness. All three fixtures are partial morphologies and share overlapping cortical region/cell class. These tests assess numerical source-placement behavior on three reconstructed cells, not population generalization or biological validity.

The exact SWC source remains the canonical reference. Weighted source is an optional discrete approximation until a wider independent morphology set supports a stable policy. Do not tune Ri/Rm/Cm/Eleak.

## Next

After the six jobs complete, compare source-mode effects on the third cell against the two Segev fixtures. If the effect is morphology-dependent, retain per-cell diagnostics and move to a source-aware reduced fine-tree operator rather than introducing a global source-placement switch.


## Completed three-morphology source-placement replication — 21/11/2026

Workflow [44914135217](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217) passed 6/6 jobs. The matrix includes NMO_68174, NMO_68175 and NMO_290988 / Mohan 2015 at mesh caps 0.125 and 0.0625 µm.

Every job passed the full 81-test suite, verified SWC counts and Import3D source/probe mapping, ran transient and AC source-placement audits, and uploaded raw artifacts. Aggregate data: 108,180 transient trace rows, 360 transient summaries, 6,480 AC transfer rows and 810 AC summaries. Maximum total-current conservation error: 1.735e-18 nA.

Weighted source is strongly beneficial for NMO_68175 in both domains and for NMO_290988 transient. However, NMO_290988 AC improves at 0.125 µm but worsens slightly at 0.0625 µm. NMO_68174 remains mixed.

Decision: exact SWC stays canonical; weighted source stays optional/diagnostic. No automatic source-offset threshold is justified from three morphologies.

Full report: [HUMAN_MORPHOLOGY_SOURCE_ALIGNMENT_REPLICATION_2026-11-21.md](amsn-core/research/HUMAN_MORPHOLOGY_SOURCE_ALIGNMENT_REPLICATION_2026-11-21.md); summary [CSV](amsn-core/results/human_morphology_source_alignment_summary_2026-11-21.csv).


## Third-morphology transient time/space convergence — pending

A six-job factorial workflow has been added for NMO_290988 / 1094_Mohan_etal_2015:
- mesh caps 0.125 and 0.0625 µm;
- dt 0.1, 0.05 and 0.025 ms;
- full AMSN test suite in every job;
- exact 8,903-record morphology verification;
- 10 pA passive pulse transient comparison with raw trace/summary artifact preservation.

Workflow: [AMSN NMO-290988 Passive Transient Time-Space Convergence](https://github.com/Nolane-x/Nghien-cuu/actions/workflows/amsn-nmo290988-passive-transient-convergence.yml). Inspect each artifact before claiming temporal or spatial convergence.


## Completed NMO_290988 transient time/space convergence — 21/11/2026

Workflow [44915125555](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555) passed 6/6 jobs. The 2×3 matrix covers mesh caps 0.125/0.0625 µm and dt 0.1/0.05/0.025 ms. Each job passed the complete 81-test suite and uploaded raw traces and summaries.

The six runs produced 63,090 trace rows and 180 summaries. At fixed mesh, reducing dt barely changed the cross-simulator NRMSE. Refining the NEURON mesh to 0.0625 µm reduced maximum interpolated-probe NRMSE by about 90.4%. Direct NEURON temporal pairwise error halved as dt halved (maximum-NRMSE ratio ≈1.954), consistent with backward-Euler first-order convergence.

Full report: [HUMAN_NMO_290988_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md](amsn-core/research/HUMAN_NMO_290988_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md); configuration [CSV](amsn-core/results/human_nmo290988_passive_transient_convergence_summary_2026-11-21.csv); pairwise [CSV](amsn-core/results/human_nmo290988_passive_transient_pairwise_convergence_2026-11-21.csv).
