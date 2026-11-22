# Research log — nine-port apical/basal PRIMA enrichment

**Date:** 2026-11-22 (Asia/Bangkok)  
**Base main commit:** 7cf8164b4d59deb62eef6b21b4703bb6456d392c  
**Work branch:** `research/prima-apical-port-enrichment-2026-11-22`  
**Status:** implementation staged for CI; new nine-port numerical results are not yet available.

## Research question

The validated seven-port experiments repeatedly identify the apical-q90 output as the most difficult transient port. Does adding intermediate and upper-branch observation points to the retained PRIMA port set improve accuracy at apical-q90 without degrading soma, basal or other apical transfer paths?

## Port-set design

Keep the three original stimulation locations:
- soma
- basal-q75
- apical-q75

Expand the output probe labels from five to nine:
- soma
- basal-q25, basal-q50, basal-q75, basal-q90
- apical-q25, apical-q50, apical-q75, apical-q90

The q75 source nodes are the same SWC node IDs as the q75 probe labels. They must be represented as one retained electrical port each, carrying both source and probe roles. The final unique port set must therefore contain exactly nine SWC nodes, not eleven.

The four model variants remain identical to the prior order/transient study:
1. Four-shift order-56 control: shifts (0, 100, 1,000, 3,000) Hz.
2. Six-shift order-28: shifts (0, 100, 1,000, 3,000, 6,000, 10,000) Hz.
3. Six-shift order-56: same six shifts.
4. Six-shift order-84: same six shifts.

## Fixed experimental protocol

- Morphologies: NMO_68174 cell1125, NMO_68175 cell1204 and NMO_290988 / 1094_Mohan_etal_2015.
- NEURON mesh caps: 0.125 and 0.0625 µm.
- Frequencies: 0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz.
- Transient sources: soma, basal-q75 and apical-q75.
- Pulse widths: 2 ms and 10 ms; 10 pA amplitude; 2 ms onset; 20 ms duration; 0.1 ms backward-Euler step.
- Every transient is scored at all nine retained ports.

For four models × ten frequencies, the frequency matrix contributes 40 rows. The transient matrix contributes 4 × 6 × (9 ports + one all-port aggregate) = 240 rows. Each morphology/mesh job must therefore emit exactly 280 rows; all six jobs together must emit 1,680 rows.

## Software changes

- Centralize deterministic SWC path-distance quantile selection in `amsn.ports`.
- Preserve the established rank/tie-breaking rule: sort by (path distance, SWC node ID), then select `round((N-1)*q)`.
- Keep the existing seven-port `build_sites` behavior as the default; add optional quantile probes only when the dedicated workflow sets `AMSN_PORT_ENRICHMENT=apical_basal_q25_q75`.
- Require exactly 3 source labels, 9 probe labels and 9 unique retained SWC nodes in enriched mode.
- Isolate output filenames with a `9port_` prefix so this run cannot overwrite seven-port artifacts.
- Preserve raw matrix, localization, frequency, order-sweep and transient CSV artifacts.

## Morphology mapping guard

The pure morphology test suite fixes the selected q25/q50/q75/q90 SWC IDs for each of the three datasets and requires nine unique retained IDs. The NEURON workflow separately verifies that every retained node maps into Import3D before computing any matrix.

## Validation gates

- Python 3.12/3.13 Core CI and all morphology tests pass.
- Six morphology × mesh jobs complete with no missing output artifact.
- Each job reports 9 unique ports, 3 sources and 9 probes.
- Every projected conductance/capacitance matrix passes Cholesky.
- Every frequency response is finite and reciprocal; port impedance conditioning remains below the established limit.
- Each job emits exactly 280 extended sweep rows, not a partial table.
- Preserve per-port transient errors, especially apical-q90, and compare them with the seven-port baseline.
- No active-channel, nonlinear-synapse, plasticity or biological-validity claims are permitted from this passive RC test.

## Decision rule

A nine-port basis is only useful if it reduces apical-q90 error while keeping the remaining ports stable and preserving a meaningful state-count reduction. If the enriched port set makes all models substantially worse, or if apical-q90 barely improves at a large order cost, retain the seven-port reference and investigate an adaptive/local basis instead. Full Hines remains canonical.
