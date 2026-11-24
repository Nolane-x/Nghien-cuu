# Research log — PRIMA q25 extended backward-Euler tail audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-extended-backward-euler-tail-audit-2026-11-24  
**PR:** [#28](https://github.com/Nolane-x/Nghien-cuu/pull/28)  
**Successful workflow:** [45389212537](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537)  
**Result commit:** 4307c716dca8f10b9b209e028aedddb2483dd3d8  
**Artifact:** [run 45389212537 artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537/artifacts/14918605464)

## Motivation

Continuous-time pulse-spectrum-weighted AC errors remained much larger than finite-window transient errors on Tamas. The experiment therefore extended the original 20-ms backward-Euler transient protocol to 200 ms to see whether late passive tails explain the mismatch.

## Method

- Morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control; both SWC hashes are pinned.
- Layouts/order: canonical seven-port and dual-q25 nine-port, order 168.
- Scenarios: all nine passive parameter cases.
- Inputs: soma, basal-q75 and apical-q75; 10 pA; 2-ms onset; 2-ms and 10-ms rectangular pulses.
- Time step: 0.1 ms implicit backward-Euler.
- Observation windows: 20, 40, 100 and 200 ms.
- Full cable: exact-order compiled C implementation of the original Hines tree-elimination traversal.
- Reduced cable: original model.step_backward_euler and per-vector model.port_voltages path through 20 ms; factorized per-RHS solve for the later tail.

The 20-ms archived parity gate is absolute in NRMSE percentage points with tolerance 5e-8. Relative deltas are reported separately because tiny baseline residuals can make them appear large.

## CI and exact coverage

Workflow 45389212537 succeeded end-to-end:
- Environment installation and both SWC SHA-256 checks passed.
- The C compiler check, six focused tests and both morphology preflights passed.
- The 200-ms audit completed and committed all outputs.
- Artifact size: 281,029 bytes; SHA-256 5b80eec96074fec275eaaded1d958802aafe4693e1f6635d0b94150e97ee8faa.

| Dataset | Expected | Verified |
|---|---:|---:|
| Extended transient rows | 6,048 | 6,048 |
| Nine/seven comparison rows | 3,024 | 3,024 |
| 20-ms parity rows | 1,512 | 1,512 |
| By-output summaries | 672 | 672 |
| Comparison summaries | 336 | 336 |
| By-source summaries | 48 | 48 |
| Window summaries | 16 | 16 |
| Layout/window summaries | 32 | 32 |

Maximum 20-ms archived absolute delta: 3.0818710679657265e-8 percentage points (within the 5e-8 floor). Maximum relative delta: 21.2146%, retained as a diagnostic rather than used as the gate.

Runtime: 99.55 s wall, 161.69 s user CPU, 0.23 s system CPU, 222,316 KB max RSS. Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3 and NEURON 9.0.2.

## Median nine-port/seven-port NRMSE ratio

Each value is a median over 189 matched scenario/source/output pairs at that morphology, pulse width and observation window. Values above one mean the dual-q25 nine-port model has higher NRMSE on the seven shared output nodes.

| Morphology | Pulse | 20 ms | 40 ms | 100 ms | 200 ms |
|---|---:|---:|---:|---:|---:|
| Tamas | 2 ms | 1.0018× | 1.0073× | 1.0047× | 1.0024× |
| Tamas | 10 ms | 1.0007× | 1.0635× | 1.0462× | 1.0218× |
| Peng | 2 ms | 14.95× | 23.38× | 16.13× | 14.07× |
| Peng | 10 ms | 12.05× | 34.54× | 22.17× | 19.77× |

The Tamas median stays close to one, with a modest transient penalty at 40–100 ms for the 10-ms pulse that relaxes by 200 ms. Thus, a late tail does not explain the large continuous-time AC ratio on Tamas.

Peng shows a much larger nine/seven NRMSE ratio on shared outputs at every window. The median ratio peaks at 40 ms and then decreases, but remains about 14–20× at 200 ms. Interpret ratios alongside absolute NRMSE values: at 200 ms the nine-port medians for Peng are still only 6.91e-8% (2-ms pulse) and 4.78e-8% (10-ms pulse), while the seven-port denominators are much smaller.

## Interpretation and limitations

The late-window experiment does not support the idea that a long passive transient tail is the main reason for Tamas's AC/transient discrepancy. It does show that dual-q25 worsens shared-output transient NRMSE substantially on this Peng reconstruction. These are two individual passive linear-RC morphologies, not populations or biological validation. Full Hines remains canonical; no production solver/defaults changed.

## Follow-up engineering

The follow-up CI run 45389236981 repeated the numerical computation successfully but failed only when committing files already added by 45389212537 (Git add/add conflict). The workflow was updated to fetch/reset to the latest branch tip and skip an unchanged CSV/JSON result commit. This is a CI idempotency repair; it does not change numerical results.

## Files

- amsn-core/research/audit_prima_q25_extended_backward_euler.py
- amsn-core/research/hines_be_kernel.c
- amsn-core/tests/test_prima_q25_extended_backward_euler.py
- .github/workflows/amsn-prima-q25-extended-backward-euler-tail-audit.yml
- amsn-core/results/prima_q25_extended_backward_euler_tail_2026-11-24_*.csv
- [Handoff](../HANDOFF_2026-11-24_PRIMA-Q25-EXTENDED-BACKWARD-EULER-TAIL-AUDIT.md)
