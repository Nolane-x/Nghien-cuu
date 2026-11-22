# Handoff — PRIMA order × input-location × pulse-width validation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Base main commit:** c7b61733c4dc3aa744509218640d774e953ee20d  
**Work branch:** `research/prima-order-transient-matrix-2026-11-22`  
**Previous checkpoint:** [10 kHz direct NEURON validation](HANDOFF_2026-11-22_PRIMA-10KHZ-NEURON.md)

## Read first

1. `AGENTS.md` — provenance, test and log rules.
2. `HANDOFF.md` and `research/AMSN_RESEARCH_DOSSIER.md` — long-range objective and evidence gates.
3. `HANDOFF_2026-11-22_PRIMA-10KHZ-NEURON.md` — prior 10 kHz result and limitations.
4. `amsn-core/research/HUMAN_PASSIVE_PRIMA_HIGH_FREQUENCY_NEURON_2026-11-22.md` — prior direct NEURON comparison.
5. `research/RESEARCH_LOG_2026-11-22_PRIMA-ORDER-TRANSIENT-MATRIX.md` — exact new protocol and validation state.

## Why this experiment follows

The preceding 10 kHz experiment held PRIMA order at 56 and tested one basal-q75, 10 ms pulse. It showed improved worst-case Z/Y frequency error in the upper band, but also some intermediate-frequency and transient trade-offs. The next useful question is whether those results survive changes in reduced order, input location and pulse width.

## Four model configurations

- Four-shift order-56 control: (0, 100, 1,000, 3,000) Hz.
- Six-shift order-28: (0, 100, 1,000, 3,000, 6,000, 10,000) Hz.
- Six-shift order-56: same six shifts.
- Six-shift order-84: same six shifts.

Each model is compared with full AMSN Hines and native NEURON at ten frequencies for seven retained ports. The report must distinguish requested order from actual rank returned by the basis builder.

## Six transient scenarios

Three input locations (soma, basal q75, apical q75) × two pulse widths (2 and 10 ms). All use a 10 pA current, 2 ms start time, 20 ms total duration and 0.1 ms backward Euler step. Every output port is recorded. Each configuration must yield 40 frequency rows and 192 transient rows; total expected: 232 rows.

## Validation gates

- Complete AMSN pytest suite.
- Six morphology × NEURON-mesh jobs; no missing artifact.
- Cholesky checks on every model's reduced G/C.
- Same ordered retained ports across all models.
- Finite reciprocal Z response and acceptable matrix conditioning.
- Exactly 232 output rows per configuration.
- Per-port/all-port transient errors for every source and pulse width.
- No biological or active-neuron claims from passive RC results.

## Status at checkpoint creation

Implementation has been written and read back from GitHub. It is not yet a validated result or merged code. Await the PR workflows, inspect raw CSVs/artifacts, then write the result report and update README. Keep the prior four-shift preset and full Hines canonical until evidence supports a change.

## Decision rule

The six-shift basis remains optional unless the order sweep and all six transient scenarios demonstrate a stable accuracy/performance trade-off across the three morphology records and both meshes. Retain and document negative results; do not tune morphology-specific passive parameters to force agreement.
