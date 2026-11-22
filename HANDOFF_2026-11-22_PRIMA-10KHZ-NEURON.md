# Handoff — PRIMA high-frequency direct NEURON validation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/prima-high-frequency-neuron-validation-2026-11-22`  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/1  
**Checkpoint commit:** 11ccddba3adc7f3f0e25ee3608ed8ba0432a9722

## Read first

1. `AGENTS.md` and `HANDOFF.md`.
2. `HANDOFF_2026-11-21_PRIMA-PASSIVE-REDUCTION.md`.
3. `amsn-core/research/HUMAN_PASSIVE_PRIMA_NEURON_DIRECT_COMPARISON_2026-11-21.md`.
4. `amsn-core/research/HUMAN_PASSIVE_PRIMA_PARAMETER_ROBUSTNESS_2026-11-21.md`.
5. `research/RESEARCH_LOG_2026-11-22_PRIMA-10KHZ-NEURON.md`.

## What this checkpoint adds

A controlled direct comparison of two order-56 passive PRIMA bases:

- Control shifts: 0, 100, 1,000 and 3,000 Hz.
- Extended shifts: 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz.

The human Schur port audit now measures full AMSN Hines and native NEURON matrices over 0.1–10 kHz, records extended-basis impedance/admittance errors against both references, and saves an extended-basis transient comparison. The regression test checks Cholesky positive definiteness plus finite reciprocal port matrices through 10 kHz. The original main-branch outputs are preserved; new outputs use the 2026-11-22 suffix.

## Validation state

Implementation is in PR #1 and is not merged. GitHub read-back confirms the changed files. The PR-specific Python workflow results had not appeared at checkpoint creation; no new test or high-frequency result is claimed. Existing main-branch evidence is not a substitute for running the modified branch.

## Next action

Verify that Core CI and all six morphology × NEURON-mesh jobs execute on PR #1. Examine 10 kHz matrix conditioning, positive definiteness, reciprocity, and transient data. Record the measured direct-NEURON trade-off before changing the recommended order/shifts. Do not make the extended basis a default merely because its full-Hines error is lower.

## Guardrails

This work remains passive linear RC validation at selected ports. Do not generalize it to active channels, synapses, calcium, metabolism, plasticity, intelligence, or biological validity. Keep full Hines canonical.