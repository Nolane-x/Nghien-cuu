# Research log — Wilbers released K MOD AP-clamp variant replay

**Date:** 23 November 2026  
**Branch:** \`research/wilbers-k-variant-apclamp-2026-11-23\`

## Motivation

The latest preceding K MOD provenance audit passed 5/5 source/parser tests, verified all nine immutable Dataverse K mechanism files against official SHA-1 and byte-size metadata, and compiled all nine with NEURON 9.0.2. Its report explicitly left the full AP-clamp replay of released variants as the next research gate.

## Implementation checkpoint

Added \`amsn-core/examples/replay_wilbers_k_mod_variants.py\`, its focused regression tests and a pinned GitHub Actions workflow. The runner uses the original H_wide trace and K workbook, performs Dataverse integrity checks for every source, preserves each mechanism's declared SUFFIX and state structure, and executes the original 5-AP and 200-AP K helper routines.

The test design also requires the first five amplitudes from the 200-AP execution to agree with the separate original 5-AP execution for every mechanism. Model curves are AP1-normalized and compared with Human and Mouse recording cohorts separately. All outputs are machine-readable and include per-AP residuals.

## Validation

**Pending.** No numerical performance result, all-nine replay pass, or model promotion is claimed until the Actions run and uploaded artifacts have been checked.


## Validation correction

The first full run successfully verified the source files, compiled all nine K mechanisms together, and extracted the exact 5-AP and 200-AP command windows. It then exposed an invalid invariant: the separate original source functions \`Ik_AP1_5\` and \`Ik_AP1_5_200\` do not return equal first-five amplitude values. The prior code had incorrectly treated them as interchangeable.

The acceptance gate is now corrected. For every K MOD variant, the same \`Ik_AP1_5\` helper is run before and after the already-tested list-backed recorder replacement; only that same-helper comparison must be identical within 1e-12. The 5-AP versus 200-AP helper difference is retained as a descriptive diagnostic, not a failure condition. The 200-AP replay remains the target for comparison to the full workbook cohort.


## Validated numerical results

GitHub Actions run [45170480109](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45170480109) completed successfully. The 30-test suite passed; all nine pinned K MOD source files matched their Dataverse ID, exact byte count and SHA-1, all nine compiled together under NEURON 9.0.2, and all nine returned 200 finite AP amplitudes on the original H_wide command. The same original five-AP helper run before and after current-recorder replacement was bit-identical for all nine mechanisms (maximum absolute difference 0). The separate five-AP versus 200-AP helper difference is recorded as a diagnostic, not a failed test.

The command window contains 622,876 samples and 200 peaks from 199–5,182 ms at 125 kHz, dt=0.008 ms and 34 °C. The K source voltage offset remains 0 mV. The two recording cohorts were kept separate: 14 Human and 11 Mouse recordings.

Across AP1–200, \`k_hybrid2\` ranked first in both groups: Human MAE 0.189698 and Mouse MAE 0.280801. Compared with canonical \`k_human\`, this is a 21.6% and 15.7% MAE reduction, respectively. \`k_hybrid5\` was nearly tied (0.189957 / 0.281061), followed by \`k_hybrid4\` (0.194284 / 0.285388) and canonical \`k_mouse\` (0.194580 / 0.285684).

The improvement is incomplete. At AP200, \`k_hybrid2\` remains +0.194293 above the Human cohort mean and +0.348123 above the Mouse cohort mean. Only 1/200 points falls inside pointwise mean ±1.96 SEM for each tested mechanism/cohort pair. The ranking is descriptive and does not establish statistical significance or biological validity. \`k_human_hm12inf\` produced an exactly identical 200-point trajectory to \`k_human\` under this single command; this needs independent kinetic-protocol investigation.

Artifact: \`wilbers-released-k-mod-variant-apclamp-replay\`, ID \`14817955509\`; ZIP SHA-256 \`45e1287889191a03b2a31de50fab67be7b2dd9a90f3dfc2fcacadf70cd83312d\`.

The next research gate is independent voltage-clamp reproduction of steady-state activation/inactivation, activation/inactivation time constants and recovery, retaining per-recording data and keeping the AP-clamp selection metric separate from validation.
