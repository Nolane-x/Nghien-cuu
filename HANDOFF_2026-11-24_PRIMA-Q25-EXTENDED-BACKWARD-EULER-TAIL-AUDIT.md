# Handoff — PRIMA q25 extended backward-Euler tail audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-extended-backward-euler-tail-audit-2026-11-24  
**PR:** [#28 — extended backward-Euler tail audit](https://github.com/Nolane-x/Nghien-cuu/pull/28) (draft; stacked on PR #27)  
**Successful workflow:** [45389212537](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537)  
**Result archive commit:** 4307c716dca8f10b9b209e028aedddb2483dd3d8  
**Artifact:** [prima-q25-extended-backward-euler-tail-audit](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537/artifacts/14918605464)  
**Artifact SHA-256:** 5b80eec96074fec275eaaded1d958802aafe4693e1f6635d0b94150e97ee8faa

## Research question

The pulse-spectrum-weighted continuous-time AC proxy did not explain why the Tamas human-pyramidal holdout showed a large spectral ratio while its 20-ms transient NRMSE ratio stayed near one. This experiment extends the same 0.1-ms implicit backward-Euler protocol to 200 ms and measures cumulative NRMSE over 20, 40, 100 and 200-ms windows.

## Method

- Two checksum-pinned morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control.
- Canonical seven-port versus dual-q25 nine-port, basis order 168.
- All nine passive parameter scenarios, three inputs, seven exact shared output SWC nodes, and 2-ms/10-ms 10-pA pulses with 2-ms onset.
- Full cable reference: exact-order compiled C implementation of the original Hines tree-elimination traversal. The kernel preserves node order, pivot updates and back-substitution order; it is not a general sparse-LU approximation.
- Reduced model: exact original per-vector backward-Euler solve and per-vector port-voltage projection through the strict 20-ms parity window; a fixed LU factorization is reused per RHS only for the later tail.
- Cumulative observation windows: 20, 40, 100 and 200 ms.

## Validation and exact coverage

Workflow 45389212537 completed successfully:
- 6 focused tests, both source checksums, C compiler check and both morphology preflights passed.
- The 20-ms archived parity gate passed using an explicit absolute tolerance of 5e-8 NRMSE percentage points.
- Maximum observed absolute archived parity delta: 3.0818710679657265e-8 percentage points.
- Maximum relative delta: 21.2146%; this occurs where the archived NRMSE denominator is extremely small, so both absolute and relative diagnostics are retained.

| Dataset | Expected | Read-back |
|---|---:|---:|
| Cumulative transient rows | 6,048 | 6,048 |
| Paired nine/seven comparisons | 3,024 | 3,024 |
| 20-ms archived parity rows | 1,512 | 1,512 |
| Per-output summaries | 672 | 672 |
| Comparison summaries | 336 | 336 |
| By-source summaries | 48 | 48 |
| Whole-window summaries | 16 | 16 |
| Layout/window summaries | 32 | 32 |

Runtime from the successful workflow: 99.55 s wall, 161.69 s user CPU, 0.23 s system CPU, 222,316 KB maximum RSS. Environment: Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2.

## Main result

The table reports the median nine-port NRMSE / seven-port NRMSE ratio over 189 matched scenario/source/output pairs per morphology and pulse/window.

| Morphology | Pulse | 20 ms | 40 ms | 100 ms | 200 ms |
|---|---:|---:|---:|---:|---:|
| Tamas human pyramidal | 2 ms | 1.0018× | 1.0073× | 1.0047× | 1.0024× |
| Tamas human pyramidal | 10 ms | 1.0007× | 1.0635× | 1.0462× | 1.0218× |
| Peng mouse | 2 ms | 14.95× | 23.38× | 16.13× | 14.07× |
| Peng mouse | 10 ms | 12.05× | 34.54× | 22.17× | 19.77× |

A ratio above one means the dual-q25 nine-port model has higher NRMSE than the canonical seven-port model on the seven shared outputs. For Tamas, the median ratio stays close to one, with a modest pulse/window-dependent rise. For Peng, the dual-q25 model is substantially worse on shared outputs; the largest median penalty occurs at 40 ms, then decreases but remains large at 200 ms.

At 200 ms, absolute median NRMSE values also matter: for Peng they are about 6.91e-8% versus 7.27e-9% for the 2-ms pulse, and 4.78e-8% versus 3.35e-9% for the 10-ms pulse (nine-port versus seven-port). For Tamas the corresponding medians are much closer: 3.06e-7% versus 3.05e-7%, and 6.86e-8% versus 6.61e-8%.

## Interpretation limits

- Extending the observation window does not reveal a large transient penalty on the Tamas holdout that would explain its much larger continuous-time spectral ratio. The 10-ms pulse shows a moderate increase at 40–100 ms, which relaxes by 200 ms.
- The Peng holdout shows a substantial nine/seven NRMSE penalty on shared outputs at every window; the median ratio is highest at 40 ms for both pulse widths.
- These ratios are relative comparisons against the seven-port baseline; inspect absolute NRMSE values and detailed rows before interpreting them as absolute voltage errors.
- Only two individual passive linear-RC morphology reconstructions are included. This is not a cell-class population study or biological validation.
- Full Hines remains canonical. No production solver code or defaults were changed.

## Reproducible result files

Result stem: prima_q25_extended_backward_euler_tail_2026-11-24.

- extended_transient.csv: 6,048 cumulative output rows.
- comparisons.csv: 3,024 paired nine/seven comparisons.
- 20ms_parity.csv: 1,512 archived parity checks.
- by_output_summary.csv: 672 summaries.
- by_source_summary.csv: 48 summaries.
- comparison_summary.csv: 336 summaries.
- window_summary.csv: 16 summaries.
- layout_window_summary.csv: 32 summaries.
- report.json: exact coverage, scope and environment metadata.

Verified Git blob SHA-1:
- report JSON: 411c2c6aa556cc3e25a12a169e2627b315469f0e
- extended transient CSV: 956aadd0ac41612ed11660778e0e4980314104b0
- comparisons CSV: a5a552213eeb49e3e5b4a25c6f9a0b948176e84f
- 20-ms parity CSV: 00c58e84f25018cdb18b5d341812d73b43c51040
- by-output summary: 0575c7db23c283b5cf1e3d9fe511d566a2b9c964
- by-source summary: 4660ed9d1d84d3f965f9ae5c0a441c4d47a8b0c5
- comparison summary: 835187ac412a56c901dc2e29daaa8dd8cd8d1080
- window summary: bf3db5437fbd2688a35f8e1788c33ba8960de4e1
- layout/window summary: 29cbe001cb791ea8667d068f2e48d7c6ca1b0629
- timing file: 9f940359b6de117393e8503be290fab9634f00fd

## CI rerun note

A second run recalculated the same numeric outputs successfully but collided while attempting to add files already committed by the successful run. The workflow commit step has since been made idempotent: it fetches the current branch tip, resets the index to it, and skips committing unchanged CSV/JSON results. The timing text remains in the downloadable artifact.
