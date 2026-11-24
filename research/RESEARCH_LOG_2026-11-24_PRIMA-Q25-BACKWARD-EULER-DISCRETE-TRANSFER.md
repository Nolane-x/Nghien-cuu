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



## Validated findings — perturbation-coordinate correction

Workflow [45419651741](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45419651741) completed the exact backward-Euler discrete transfer and finite-record boundary audit. Its maximum identity residual was \(1.4323466885\times10^{-11}\) against \(2\times10^{-8}\); 864 identity diagnostics and all declared CSV coverage checks passed. The result data were archived, then independently replayed in [45420670698](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45420670698), which also passed **9 focused tests** in 0.71 s and committed result set \`1d6f64a83ccc7d1310a19baa50b2bc9b738dd7f5\`.

The coordinate fix is evidence-driven. On Tamas, the canonical full-Hines absolute-voltage trace followed by subtracting the leak reversal had a maximum per-group discrepancy of \(2.6494\times10^{-6}\%\) relative to the zero-origin perturbation replay. This numerical floor masked the much smaller reduced-model error. The second Hines replay uses the same linear recurrence, current protocol, Hines kernel and tree, but starts from zero perturbation and uses a zero leak source. It is used only for the discrete-transfer/DFT identity and stable transient comparison; the absolute-voltage trace is retained for historical comparison. Production code is unchanged.

### Stable transient vs periodic transfer

Ratios are nine-port/seven-port medians. Within each source × pulse group, median over nine passive scenarios × seven shared outputs; then median over the six source × pulse groups for each morphology/window.

| Morphology | Window | Legacy absolute-voltage transient | Stable perturbation transient | Discrete BE transfer | Continuous AC + ZOH |
|---|---:|---:|---:|---:|---:|
| Tamas | 20 ms | 1.001× | 24.54× | 31.76× | 33.17× |
| Tamas | 40 ms | 1.029× | 56.18× | 26.64× | 27.19× |
| Tamas | 100 ms | 1.023× | 32.22× | 28.28× | 28.62× |
| Tamas | 200 ms | 1.011× | 32.08× | 28.63× | 28.96× |
| Peng | 20 ms | 31.43× | 162.7× | 38.82× | 38.04× |
| Peng | 40 ms | 38.71× | 63.57× | 32.83× | 32.85× |
| Peng | 100 ms | 25.52× | 34.11× | 34.01× | 33.80× |
| Peng | 200 ms | 24.88× | 34.02× | 34.02× | 33.81× |

The q25 nine-port absolute perturbation-coordinate NRMSE medians are still tiny: Tamas \(2.41e{-9}\%\), \(1.11e{-8}\%\), \(1.72e{-8}\%\), \(1.72e{-8}\%\); Peng \(9.80e{-9}\%\), \(5.19e{-8}\%\), \(7.15e{-8}\%\), \(7.16e{-8}\%\), across 20/40/100/200 ms. Large relative ratios must always be read with these absolute values.

The boundary correction explains part of the mismatch: for the nine-port finite-window error, the median boundary-component norm is about 655% (Tamas) / 777% (Peng) at 20 ms; 103% / 110% at 40 ms; 2.4% / 2.2% at 100 ms; and about 0.005% at 200 ms. Norm ratios above 100% are possible because periodic and boundary components cancel; these are not energy shares.

The first table corrects the previous interpretation of the Tamas near-unity transient ratio. The earlier number is preserved as a historical absolute-voltage replay metric but is not accepted as evidence of q25 parity because the arithmetic difference between absolute and perturbation Hines traces is larger than the model-reduction residual in that regime.

## Secondary summary-generator update

The analysis code now adds an eight-row morphology × observation-window summary and explicit perturbation-coordinate ratios to the 48 source × pulse × window summaries. A unit test checks that the new aggregate keeps the legacy and stable metrics separate. Workflow [45422549114](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45422549114) exposed a test-contract mismatch (the expected-count test omitted the new eight-row table; 8 tests passed, that one assertion failed). The expected-count contract has been updated; workflow [45422624509](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45422624509) is validating the corrected test suite and full result generation. No morphology-window summary CSV from that new generator is accepted until the corrected run passes.

