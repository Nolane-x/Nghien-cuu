# Research log — exact backward-Euler discrete-time transfer for PRIMA q25

**Date:** 24 November 2026  
**Branch:** \`research/prima-q25-backward-euler-discrete-transfer-2026-11-24\`  
**Parent checkpoint:** PR #29

## Question

Does the exact discrete-time transfer function of the backward-Euler recurrence change the q25 comparison relative to continuous-time AC, and can finite-record output DFTs be reconstructed with a terminal-state correction?

## Sources examined

- \`AGENTS.md\`, \`HANDOFF.md\` and \`research/AMSN_RESEARCH_DOSSIER.md\`.
- PR #29 handoff and validated finite-window DFT report.
- The prior q25 continuous-time transfer, Krylov-stage, extended-tail and transient-spectrum audits.
- Existing exact-order Hines and reduced backward-Euler implementations.

## Derivation

Starting with
\[
(G+C/\Delta t)x[n]-(C/\Delta t)x[n-1]=Bu[n],
\]
and the convention that \(u[n]\) is held during one time interval while \(x[n]\) is sampled at the interval end, the discrete transfer is
\[
H_{BE}(e^{j\Omega})=L(G+(1-e^{-j\Omega})C/\Delta t)^{-1}B.
\]
It is the continuous resolvent evaluated at \(s_{BE}=(1-e^{-j\Omega})/\Delta t\), not at \(j\Omega/\Delta t\). For a finite record initialized at rest, the DFT obeys
\[
(G+(1-e^{-j\Omega})C/\Delta t)X=BU-(C/\Delta t)x[N-1].
\]
The last term is retained as the terminal-state boundary correction.

## Frequency-map implication (analytic, not a simulation result)

At dt=0.1 ms, Im(s_BE)/omega is 0.999342 at 100 Hz, 0.983632 at 500 Hz, 0.935489 at 1 kHz, 0.756827 at 2 kHz and approximately zero at the 5-kHz Nyquist frequency. Re(s_BE) rises from 19.73 s^-1 at 100 Hz to 20,000 s^-1 at Nyquist. This demonstrates that the backward-Euler transfer samples the continuous resolvent at a frequency-warped, damped complex shift; comparison with the continuous AC proxy must not use j*omega in place of s_BE. These values follow directly from the formula and timestep and are not morphology-derived measurements.

## Implementation authored

- Added exact complex-shift Hines and reduced solves for both \(s=j\omega\) and \(s=s_{BE}\).
- Added sample-and-hold pulse-spectrum construction.
- Added full/reduced transient replays that retain terminal state at 20, 40, 100 and 200 ms.
- Added finite-record DFT reconstruction checks.
- Added focused unit tests, workflow, report, handoff and this log.
- No production solver or default was changed.

## Execution record

Workflow 45416403878 ran Python 3.12 / NumPy 2.5.5 / NEURON 9.0.2 / SciPy 1.16.3. The 7 focused tests passed, both SWC checksums passed, both morphology preflights passed, and the complete numerical replay finished. The run then failed the finite-record identity gate at 5.05389. Inspection showed that the residual for the difference between reduced and full traces was normalized by the small inter-model residual norm; because it subtracts two independently reconstructed transfer terms, that denominator can magnify ordinary floating-point cancellation. It is now normalized against the corresponding output DFT L2 norm, while the individual full/reduced model identities remain measured against their own output norms. The validator also separates these two residual classes, writes the 864-row diagnostic CSV before gate evaluation, and adds a regression test for scale normalization. Run 45417410370 (Python 3.12.16, NumPy 2.5.5, NEURON 9.0.2, SciPy 1.16.3) passed all seven then-current focused tests and both morphology preflights. It completed the numerical computation in 405.70 s wall time (745.15 s user CPU, peak RSS 346,800 KB) and wrote the 864-row identity diagnostic, but failed the output-scaled identity gate: maximum 2.737742435e-8 against 2e-8. This was highly localized to full-Hines on Tamas; max reduced-model identity residual was 1.135328e-13 and Peng max full-Hines residual was 6.389262e-10. The maximum Tamas rows were 2-ms pulses at 200 ms, notably Cm_minus20/apical_q75/output 7023 and Rm_minus20/basal_q75/output 4623. The error did not arise in the reduced PRIMA state identity.

The leading numerical hypothesis is loss of precision in the canonical full-Hines absolute-voltage recurrence: it evolves voltages around E_leak and the audit subtracts that offset to recover the small perturbation, while the frequency-domain linear model is defined directly in perturbation coordinates. To test rather than assume this, commit 71de870b adds a second full-Hines replay initialized at zero perturbation with leak source zero, records its difference from the canonical absolute-voltage trace, uses the perturbation replay only for the transfer/DFT identity, and retains the canonical trace for the historical transient NRMSE. The new run 45419651741 is queued; run 45417470042 was still running the older eight-test version at the last check. Artifact 14932942667 (SHA-256 4cf890875ee023588491f59a9cd482a6cba8c951be422aecb4db182bc24567d7) contains the prior diagnostic CSVs. No numerical transfer/boundary interpretation is accepted yet.

Run 45417470042 subsequently passed the eight focused tests but reproduced the same absolute-coordinate identity maximum of 2.737742435e-8 against 2e-8; artifact 14934170131 was uploaded with ZIP SHA-256 a1f6b09189c9c703c336cab1d61d10feeea196802265470a2f407d82191e67ea. This repeat confirms the old failure is deterministic; it does not validate the perturbation-coordinate correction.

## Expected outputs

- \`frequency_summary.csv\`
- \`case_metrics.csv\`
- \`nine_seven_comparisons.csv\`
- \`source_window_summary.csv\`
- \`finite_dft_identity.csv\`
- \`report.json\`

## Limits and next step

The continuous comparator is sampled at discrete DFT frequencies and weighted by the ZOH input spectrum; it is not the exact sampled response of the continuous-time ODE. Only two passive linear-RC morphologies are included. After CI, compare absolute weighted norms, ratios, transient NRMSE and boundary correction separately. Keep full Hines canonical.


## Perturbation-coordinate parity regression added

Commit `6488d38a68127debe82c28dd421ece02070d659f` adds a focused synthetic three-compartment test that runs both the canonical absolute-voltage Hines replay and the zero-origin perturbation-coordinate Hines replay over the same pulse protocol, then checks their relative waveform delta. The test complements the full-morphology DFT identity gate; it is not a substitute for that gate. Workflow `45420670698` is queued on this commit to run the newest nine-test suite and complete matrix. Workflow `45419651741` is currently executing the eight-test version on commit `71de870b1d27af05737cc1e4b7285ecfa46967f3`.
