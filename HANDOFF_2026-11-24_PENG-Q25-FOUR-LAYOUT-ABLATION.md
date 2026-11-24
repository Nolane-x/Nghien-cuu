# Handoff — Peng four-layout q25 PRIMA ablation

**Date:** 24 November 2026  
**Branch:** research/prima-peng-q25-four-layout-ablation-2026-11-24  
**Parent:** research/prima-residual-localization-2026-11-24 / PR #18  
**Successful workflow:** [45326802613](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45326802613)  
**Generated result commit:** `f459e82`  
**Detailed report:** [amsn-core/research/PRIMA_PENG_Q25_FOUR_LAYOUT_ABLATION_2026-11-24.md](amsn-core/research/PRIMA_PENG_Q25_FOUR_LAYOUT_ABLATION_2026-11-24.md)

## Research question

Does the q25 port-count trade-off on NMO_163775 arise from the basal-q25 probe, the apical-q25 probe, or their joint addition to the canonical seven ports?

## Four matched layouts

- seven: canonical seven ports.
- eight_basal_q25: canonical seven + basal-q25.
- eight_apical_q25: canonical seven + apical-q25.
- nine_both_q25: canonical seven + both q25 probes.

Every layout uses the same NMO_163775 SWC, 0.5 µm NEURON segment cap, six extended-10-kHz shifts, basis orders 112/168, nine passive parameter scenarios, nine AC frequencies, three source nodes, two pulse widths, 10 pA, 2 ms onset, 20 ms duration and dt 0.1 ms.

## Verified execution and exact coverage

The corrected workflow run 45326802613 completed successfully. The earlier run 45326775736 failed on the pre-fix commit and is superseded; it is not evidence against the corrected run.

The generated report and every CSV were read back from the branch. Actual row counts exactly match the coverage contract:

- 72 model rows.
- 648 frequency rows.
- 3,456 per-port transient rows.
- 2,268 paired shared-output comparisons versus seven ports.
- 432 q25-only output observations.
- 1,134 shared-Hines consistency checks.

All 1,134 shared-Hines comparisons are exactly zero in both maximum absolute voltage difference and relative L2 difference. The workflow used Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2. Simulation wall time was 317.18 s; maximum RSS was 160,180 KB.

## Main numerical result

At basis order 168, the median shared-output NRMSE ratios versus the seven-port baseline were 1.036× for basal-q25-only, 1.046× for apical-q25-only, and 14.525× for both q25 probes together. The paired comparisons marked the candidate worse in 302/378, 303/378 and 351/378 pairs, respectively. Despite the relative increases, the largest absolute transient NRMSE among all layouts at order 168 was 6.066e-7%.

The q25-only measurements at order 168 had median NRMSE of 1.840e-9% for basal-q25, 4.587e-10% for apical-q25, and 1.557e-8% for the dual-q25 layout. This is a non-additive empirical pattern in this one setup; it does not establish a causal mechanism.

At order 112, every q25-enriched layout was worse than the seven-port baseline on all 378 matched shared-output pairs. Detailed values and both orders are in the research report.

## Scientific constraints and interpretation

NMO_163775 is one mouse Control-condition morphology. NeuroMorpho marks the dendrites and axon complete but lists No Diameter; standardized SWC radii are not measured biological diameters. This is a passive linear-RC numerical experiment, not active-neuron or biological validation.

Full Hines remains the reference. The result is limited to this one morphology, 0.5 µm mesh cap, chosen source/input set and tested basis orders. Relative error ratios can look large when the seven-port baseline error is already extremely small; absolute NRMSE must be read alongside those ratios. Do not infer that adding ports is generally harmful, or that the dual-q25 interaction is mechanistically explained.

No production solver defaults change. Keep this PR stacked on PR #18; do not merge it ahead of its parent review.
