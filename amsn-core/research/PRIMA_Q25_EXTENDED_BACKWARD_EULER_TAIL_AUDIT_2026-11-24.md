# PRIMA q25 extended backward-Euler tail audit

**Date:** 24 November 2026  
**Workflow:** [45389212537 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537)  
**Result commit:** 4307c716dca8f10b9b209e028aedddb2483dd3d8  
**Artifact:** [prima-q25-extended-backward-euler-tail-audit](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45389212537/artifacts/14918605464)  
**Artifact SHA-256:** 5b80eec96074fec275eaaded1d958802aafe4693e1f6635d0b94150e97ee8faa

## Aim

Test whether extending the same 0.1-ms backward-Euler transient protocol from 20 ms to 200 ms reveals a late passive response tail that explains the gap between continuous-time pulse-spectrum-weighted AC transfer error and the archived 20-ms transient NRMSE.

## Design

- Morphologies: NMO_163775 Peng mouse Control and NMO_107159 Tamas human pyramidal Control; exact SWC hashes pinned.
- Layouts: canonical seven-port and dual-q25 nine-port, order 168.
- Nine passive parameter scenarios; three sources; seven shared output nodes; 10-pA rectangular current pulses at 2-ms onset, with 2-ms and 10-ms widths.
- Time step: 0.1 ms. Cumulative observation windows: 20, 40, 100 and 200 ms.
- Full-cable reference: compiled C implementation of the original Hines tree elimination, preserving node traversal and floating-point operation order.
- Reduced trace: original per-vector solve and per-vector port projection for the strict 20-ms parity window; factorized per-RHS solve for the later tail.

## Validation and coverage

Workflow 45389212537 passed all stages: environment, source checksums, C compiler check, six focused tests, both morphology preflights, simulation, result commit and artifact upload.

| Data set | Expected | Verified |
|---|---:|---:|
| Extended transient rows | 6,048 | 6,048 |
| Nine/seven comparisons | 3,024 | 3,024 |
| 20-ms parity rows | 1,512 | 1,512 |
| By-output summaries | 672 | 672 |
| Comparison summaries | 336 | 336 |
| By-source summaries | 48 | 48 |
| Window summaries | 16 | 16 |
| Layout/window summaries | 32 | 32 |

Archived parity uses an absolute NRMSE percentage-point tolerance of 5e-8. The maximum observed absolute delta was 3.0818710679657265e-8 percentage points, so the gate passed. Maximum relative delta was 21.2146%; this is retained because the archived residual denominator can be extremely small. Do not read the relative figure without the absolute delta.

## Main result

Median nine-port NRMSE / seven-port NRMSE over 189 matched scenario/source/output pairs per morphology and pulse/window. Values above 1 mean the nine-port model has higher NRMSE on the shared outputs.

| Morphology | Pulse | 20 ms | 40 ms | 100 ms | 200 ms |
|---|---:|---:|---:|---:|---:|
| Tamas human pyramidal | 2 ms | 1.0018× | 1.0073× | 1.0047× | 1.0024× |
| Tamas human pyramidal | 10 ms | 1.0007× | 1.0635× | 1.0462× | 1.0218× |
| Peng mouse | 2 ms | 14.95× | 23.38× | 16.13× | 14.07× |
| Peng mouse | 10 ms | 12.05× | 34.54× | 22.17× | 19.77× |

Tamas remains close to parity in median shared-output NRMSE. The 10-ms pulse shows a moderate increase at 40–100 ms that relaxes by 200 ms; the longer passive tail therefore does not explain its much larger AC spectral ratio.

Peng shows a much larger nine/seven error ratio at every observation window, with the highest median penalty at 40 ms. At 200 ms, median absolute NRMSE for the nine-port layout is 6.91e-8% versus 7.27e-9% for seven-port at 2 ms, and 4.78e-8% versus 3.35e-9% at 10 ms. These are small absolute errors despite large relative ratios.

## Scientific limits

This is passive linear-RC numerical analysis on two individual morphology reconstructions, not a population study or biological validation. Comparisons are restricted to the seven SWC outputs shared by the seven- and nine-port models; q25-only output nodes are not included in the nine/seven paired ratios. Full Hines remains canonical; no production code or solver defaults changed.

## Reproducible outputs

Result stem: prima_q25_extended_backward_euler_tail_2026-11-24.

- extended_transient.csv: 6,048 cumulative traces.
- comparisons.csv: 3,024 matched nine/seven rows.
- 20ms_parity.csv: 1,512 archived parity checks.
- by_output_summary.csv, by_source_summary.csv, comparison_summary.csv, window_summary.csv, layout_window_summary.csv.
- report.json: deterministic scope, coverage, parity and environment metadata.

The CI artifact also preserves the timing file and preflight evidence.
