# Research log — Peng four-layout q25 PRIMA ablation

**Date:** 24 November 2026  
**Topic:** isolate basal-q25 versus apical-q25 port enrichment  
**Branch:** research/prima-peng-q25-four-layout-ablation-2026-11-24

## Question and hypothesis

Question: on the NMO_163775 Peng Control morphology, which q25 probe contributes to the shared-output error trade-off observed when both q25 outputs are added?

Hypothesis: basal-q25-only and apical-q25-only layouts will have distinguishable accuracy profiles; the dual-q25 result may not be explained by either isolated probe alone. This is a testable hypothesis, not a result.

## Design

Four layouts are tested under the same model and transient protocol:
1. canonical seven ports;
2. seven plus basal-q25;
3. seven plus apical-q25;
4. seven plus both q25 probes.

The seven shared nodes, source sites, parameter scenarios, basis orders, shifts, AC frequencies, pulse widths, timestep and NEURON mesh cap remain fixed. Hines references are computed independently for each layout and paired at identical shared SWC node IDs.

## Files created

- amsn-core/examples/replay_nmo163775_four_layout_ablation.py
- amsn-core/tests/test_nmo163775_four_layout_ablation.py
- .github/workflows/amsn-prima-peng-q25-four-layout-ablation.yml
- HANDOFF_2026-11-24_PENG-Q25-FOUR-LAYOUT-ABLATION.md

Workflow will preserve:
- models, frequency matrices, transient traces;
- pairwise shared-output comparisons against the seven-port baseline;
- q25-only output traces;
- full-Hines shared-node consistency rows;
- summary and report JSON;
- runtime resource log and GitHub Actions artifact.

## Validation state

No simulation result is claimed at file creation. Run the dedicated workflow, inspect all steps and verify its exact coverage report before interpreting the ablation. Do not use the post-hoc NMO_163775 nine-port ratio as the causal explanation.

## Interpretation limits

One mouse morphology, passive linear-RC only, no biological validation. NeuroMorpho metadata says No Diameter. Keep full Hines canonical and production defaults unchanged.
