# Research log — independent Wilbers K voltage-clamp replay

**Date:** 23 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/wilbers-k-independent-voltage-clamp-replay-2026-11-23

## Implementation and validation

The branch replayed all nine unchanged K MOD sources using the original Wilbers channel_tools.py current and fitting helpers. The K_IV_ss and K_recovery_ss voltage commands, temperature, dt, cell setup, sample windows and fit methods were validated against the released source before simulation.

GitHub Actions run 45180834231 passed 9/9 tests, checksum-verified all nine K MODs and both original helper scripts, compiled all nine MOD files jointly with NEURON 9.0.2, and completed both protocols for every mechanism. The result workflow committed the JSON and three CSV tables to this branch and uploaded artifact 14821441838 (ZIP SHA-256 64ea571889de5ab0ffcf233fa8aab0a5ea42f53af6f50bc962f457b6191806e6).

Outputs contain 855 model curve rows, 945 per-voltage comparisons and 162 endpoint/cohort summaries.

## Numerical observations

No single mechanism is best across all endpoints and both cohorts. The highest-performing variant differs by curve and species:
- Human: k_human_h1 leads activation G/Gmax and activation tau; k_human leads inactivation G/Gmax and fast inactivation tau; k_hybrid5 leads slow inactivation tau.
- Mouse: k_hybrid4 leads activation G/Gmax; k_mouse leads inactivation G/Gmax; k_hybrid2 leads activation tau and inactivation Vhalf; k_human_h1 leads fast inactivation tau; k_hybrid5 leads slow inactivation tau.

The prior AP-clamp winner k_hybrid2 is not a universal independent voltage-clamp winner. It performs well for selected Mouse endpoints but poorly for Human activation tau.

k_human_hm12inf and k_human generated exactly identical K-IV curves, fit outputs and recovery outputs under the two tested protocols. This is limited to the tested initialization and commands and does not prove general mechanism equivalence.

The original source fit bounds are consequential: some slow inactivation fits approach 300–1,000 ms, and k_human_h1 recovery slow tau is 1,000.006 ms, essentially on the source-defined 1,000-ms lower bound. Such fits are weakly identified.

The Figure 4 targets represent 13 Human cells nested in 2 subjects and 30 Mouse cells nested in 7 subjects. Comparisons remain descriptive at cell level. No mechanism or runtime setting is promoted.

## Next gate

Compare with raw voltage-clamp current traces if available, use subject-aware uncertainty, investigate identical K mechanism outputs and source-bound fits, then evaluate current-clamp and morphology behavior.


## Figure 2 AP-clamp waveform coverage audit

Inspected the official Figure 2 K workbook and original \`plots_fig2.py\` source. The workbook has 25 recording rows (14 Human, 11 Mouse), AP1–AP201 columns for four series (\`amp_h_\`, \`amp_m_\`, \`amp_h_n_\`, \`amp_m_n_\`) and exact AP1 normalization. PR #9 already compared all 14 Human and 11 Mouse recordings against the \`amp_h_n_\` normalized human-waveform series.

The Figure 2 article describes applying both human- and mouse-origin AP command waveforms and reports that species differences were independent of command waveform origin. The public Dataverse APclamp directory contains \`H_wide.csv\`, but no \`M_wide.csv\` command was present in the inspected v3 directory inventory. Thus the mouse-waveform response series \`amp_m_n_\` is a measured target without its corresponding downloadable command waveform. A faithful second-condition model replay cannot be performed from these public assets alone; no synthetic substitution should be made.
