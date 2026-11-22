# Handoff — PRIMA high-frequency direct NEURON validation

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/prima-high-frequency-neuron-validation-2026-11-22`  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/1  
**Original checkpoint commit:** 11ccddba3adc7f3f0e25ee3608ed8ba0432a9722  
**Merged to main:** 2026-11-22, commit `c7b61733c4dc3aa744509218640d774e953ee20d`  
**PR:** [#1 merged](https://github.com/Nolane-x/Nghien-cuu/pull/1)

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

## Final validation and merge status

PR #1 was merged to main at `c7b61733c4dc3aa744509218640d774e953ee20d`.

- PR Core CI [44965696105](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965696105): 4/4 passed, including Python 3.12/3.13 tests and NEURON cross-validation.
- PR Schur/PRIMA matrix audit [44965696254](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965696254): 6/6 passed.
- PR frequency-domain audit [44965696159](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965696159): 3/3 passed.
- Post-merge main workflows [Core CI 44965966066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966066), [Schur 44965966021](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966021), [fine mesh 44965966005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966005) and [frequency 44965965999](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965965999) all passed.

## Next action

Verify that Core CI and all six morphology × NEURON-mesh jobs execute on PR #1. Examine 10 kHz matrix conditioning, positive definiteness, reciprocity, and transient data. Record the measured direct-NEURON trade-off before changing the recommended order/shifts. Do not make the extended basis a default merely because its full-Hines error is lower.

## Verified continuation — 2026-11-22

The high-frequency PRIMA branch has completed its six-job direct NEURON matrix audit:

- PR #1: https://github.com/Nolane-x/Nghien-cuu/pull/1
- Workflow [44965325079](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079): 6/6 passed; each job ran 109 tests.
- The 56-state six-shift basis (0, 100, 1,000, 3,000, 6,000, 10,000 Hz) improves worst direct-NEURON Z/Y errors over the four-shift control from 0.527300%/0.404489% to 0.216765%/0.211010%.
- Full-Hines residual maxima improve from 0.416133%/0.432732% to 0.113574%/0.124064%.
- The gain is specific to the upper band; some 1–3 kHz admittance residuals and the one tested transient pulse become modestly worse. Keep this basis experimental/optional; do not change the default.
- Report: `amsn-core/research/HUMAN_PASSIVE_PRIMA_HIGH_FREQUENCY_NEURON_2026-11-22.md`
- Aggregate table: `amsn-core/results/human_passive_prima_high_frequency_neuron_aggregate_2026-11-22.csv`
- Checkpoint protocol/status: `research/RESEARCH_LOG_2026-11-22_PRIMA-10KHZ-NEURON.md`

The regular test, compile and example jobs in Core CI passed on Python 3.12 and 3.13; the two longer NEURON cross-validation jobs were still running when this checkpoint was written. Recheck that workflow before merging. Keep full Hines canonical and retain the passive/biological validity guardrails from the earlier handoffs.

## Next experiment — order × source × pulse-width matrix

Continue with the next research checkpoint `HANDOFF_2026-11-22_PRIMA-ORDER-TRANSIENT-MATRIX.md`. The next experiment evaluates four models at equal/controlled order (four-shift order 56 control; six-shift orders 28, 56 and 84) and six transient scenarios (soma, basal-q75, apical-q75 × 2 ms/10 ms pulses). Keep the full Hines reference, Cholesky/passivity checks and direct NEURON frequency comparison. Do not choose a default from one aggregate number.

## Guardrails

This work remains passive linear RC validation at selected ports. Do not generalize it to active channels, synapses, calcium, metabolism, plasticity, intelligence, or biological validity. Keep full Hines canonical.