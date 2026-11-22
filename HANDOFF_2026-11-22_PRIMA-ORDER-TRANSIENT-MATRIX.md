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

## Final validation — verified 22/11/2026

PR #2: https://github.com/Nolane-x/Nghien-cuu/pull/2 — implementation and six-configuration validation complete; merge was not yet performed at checkpoint creation.

- Schur/PRIMA workflow [44966510373](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373): 6/6 jobs passed. Each job ran 111 tests and asserted exactly 232 rows; total 1,392 rows across six morphology/mesh configurations.
- Core CI [44966510441](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510441): 4/4 jobs passed on Python 3.12 and 3.13, including both NEURON cross-validation jobs.
- Frequency audit [44966510356](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510356): 3/3 jobs passed.
- All 24 projected G/C models passed Cholesky positive-definiteness checks; maximum NEURON impedance condition number was 91.263.
- Order 28 failed the full-band/input-diversity accuracy gate (maximum direct-NEURON Z/Y 9.4902%/8.4540%; maximum all-port transient NRMSE 0.4161%; maximum single-port 5.1199%).
- Order 56 six-shift improved the upper-band errors but modestly worsened transient error versus the four-shift control.
- Order 84 six-shift produced maximum Hines residuals 0.000296% Z / 0.000376% Y, direct-NEURON maxima 0.2163% Z / 0.1193% Y, all-port transient maximum 0.00001835% and single-port maximum 0.000229% while retaining 99.055–99.389% state reduction.
- The four-shift order-56 model remains default/control; six-shift order 84 is an optional high-fidelity passive preset. Full Hines remains canonical.

See [the validated report](amsn-core/research/HUMAN_PASSIVE_PRIMA_ORDER_TRANSIENT_SWEEP_2026-11-22.md) and its three summary CSVs under amsn-core/results/.

## Next experiment — apical-q90 port enrichment

Investigate why the apical-q90 retained port is the recurring worst transient output. Compare the current seven-port basis with a port-enriched alternative preserving additional apical/basal transfer locations, using identical morphology, passive parameters, pulse scenarios and reference meshes. Measure whether local accuracy improves without degrading soma/basal paths; do not infer biological mechanisms from numerical error alone.
