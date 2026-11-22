# Research log — direct PRIMA/NEURON validation through 10 kHz

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Work branch:** `research/prima-high-frequency-neuron-validation-2026-11-22`  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/1  
**Implementation commit at log creation:** 11ccddba3adc7f3f0e25ee3608ed8ba0432a9722  
**Status:** implementation staged for validation; do not treat the experiment as passed.

## Research question

Does an order-matched passive PRIMA model whose positive-real expansion points extend through 6 and 10 kHz improve the seven-port voltage/current transfer response against the independent NEURON reference, or does it merely improve agreement with the AMSN full Hines solver?

## Scientific motivation

The current passive parameter-robustness experiment on three human morphology records reports improved high-band agreement when using shifts (0, 100, 1,000, 3,000, 6,000, 10,000) Hz instead of the established (0, 100, 1,000, 3,000) Hz basis. That experiment compares reduced models with full AMSN Hines. A direct NEURON comparison at 6 and 10 kHz is still required before any claim of cross-simulator improvement can be made.

The order is held at 56, and the original four-shift model remains in the same run as the control. This is designed to isolate the effect of changing expansion points rather than changing state budget.

## Implementation in this PR

- Extend the shared full-Hines and native-NEURON seven-port comparison grid from 0.1–3 kHz to 0.1–10 kHz, adding 6 and 10 kHz.
- Keep the established four-shift, order-56 basis as the within-run control.
- Add a six-shift, order-56 basis at (0, 100, 1,000, 3,000, 6,000, 10,000) Hz.
- Record full-Hines errors and direct NEURON errors for impedance and admittance separately.
- Record the same basal-q75 transient protocol for the extended basis.
- Check Cholesky positive definiteness of both projected conductance and capacitance matrices.
- Add a regression test checking finite and reciprocal port impedance/admittance at frequencies through 10 kHz.
- Preserve dated CSVs and raw logs as workflow artifacts rather than overwriting the previous 2026-11-21 outputs.

## Reproducibility protocol

Expected workflow commands, on GitHub-hosted Ubuntu:

```bash
cd amsn-core
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pip install --only-binary=neuron "neuron==9.0.2"
python -m pytest
python examples/human_schur_port_matrix_audit.py
```

The Schur/PRIMA workflow matrix evaluates the three existing morphology records at NEURON reference mesh caps 0.125 and 0.0625 µm. It retains the seven SWC-defined source/probe ports. The frequency grid is 0.1, 1, 10, 30, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz.

## Validation status at checkpoint creation

- Existing main-branch Core CI at commit `60c16d2dd51931cb40c111dbbca3c5e61063776b`: success; 108 tests in the main parameter-robustness run on Python 3.12, and the corresponding core CI workflow succeeded.
- Existing main-branch parameter robustness workflow at that commit: 3/3 morphology jobs succeeded.
- New PR branch: implementation files were read back from GitHub and the branch compares three or more commits ahead of main.
- New PR-specific Actions execution: not yet observed at checkpoint creation. The external check suites returned by GitHub were queued with zero check runs; those are not evidence that the Python workflows passed.
- Therefore no test/passivity/cross-simulator result is claimed for this PR yet. The new regression test and 6 morphology × mesh jobs must run before acceptance.

## Validation results from PR #1 (2026-11-22)

The PR-specific run is now verified; this supersedes the earlier pending-validation paragraph above.

- Schur/PRIMA matrix workflow [44965325079](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325079): **6/6 morphology × NEURON-mesh jobs passed**. Every job ran **109 tests**, validated source/probe mapping and completed the 10-frequency, seven-port comparison.
- Separate passive frequency-domain audit [44965325128](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325128): **3/3 jobs passed**.
- Core CI [44965325088](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965325088): regular test/compile/example jobs passed on Python 3.12 and 3.13. Its two longer NEURON cross-validation jobs were still in progress when this log was updated; do not call the whole Core CI complete yet.
- All six extended-basis projected conductance/capacitance matrices passed the Cholesky checks. The maximum NEURON port-impedance condition number was 91.263.
- Across the six configurations, worst direct-NEURON impedance error fell from 0.527300% to 0.216765%; worst direct-NEURON admittance error fell from 0.404489% to 0.211010%.
- Worst PRIMA-vs-full-Hines impedance/admittance errors fell from 0.416133%/0.432732% to 0.113574%/0.124064%.
- The improvement is concentrated at 6–10 kHz. The six-shift basis slightly increases some intermediate-band (1–3 kHz) admittance residuals and the tested transient error, so it remains optional and does not replace the existing default.
- Full per-frequency results: [HUMAN_PASSIVE_PRIMA_HIGH_FREQUENCY_NEURON_2026-11-22.md](../amsn-core/research/HUMAN_PASSIVE_PRIMA_HIGH_FREQUENCY_NEURON_2026-11-22.md) and [aggregate CSV](../amsn-core/results/human_passive_prima_high_frequency_neuron_aggregate_2026-11-22.csv).

The 10 kHz protocol is validated only for the passive linear RC network, the three available morphology records and the seven retained ports. Full Hines remains canonical.

## Interpretation limits## Interpretation limits

The experiment covers only the linear passive RC subsystem and the selected seven ports in the three existing morphology records. It does not validate active ion channels, synapses, calcium, gene expression, metabolism, plasticity or biological realism. The passive parameter settings remain numerical defaults rather than population-fitted physiology. The NMO_290988 morphology is partial and must not be described as a healthy-control neuron. The full Hines solver remains canonical.

## Decision criteria

1. If the six-shift model lowers direct NEURON errors across the upper band without unacceptable degradation at lower frequencies, report the measured trade-off and keep it optional.
2. If it improves only AMSN-Hines error but worsens direct NEURON error, reject the basis as a cross-simulator improvement.
3. If reciprocity, Cholesky, matrix conditioning, or transient checks fail, preserve the failure and diagnose it before further use.
4. Do not switch the default solver or merge based solely on lower full-Hines residuals.

## Next concrete action

Run the PR's Core CI and six morphology × NEURON-mesh comparison jobs. Inspect job logs and artifacts; then add the actual numerical result table and a follow-up checkpoint. If the pull-request workflow is not scheduled automatically, use the repository Actions UI to dispatch the named workflows against this branch.
