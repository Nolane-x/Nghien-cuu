# Research log — PRIMA q25 strict-dispatch four-layout replay

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Workflow:** [45616046681](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681), completed success  
**Calculation head:** 62214bb20652723ae486843016225c319c3379a7  
**Results commit:** 2326ea077c3c6821ba427aef9b009b655e052cfe

## 1. Research question

Can the four-morphology q25 7/8/8/9-port order-168 matrix be fully rerun and archived under a pinned Python/NumPy/SciPy/NEURON and CPU-dispatch configuration, and do the resulting reduced bases and tracked numerical matrices match the previously archived run?

## 2. Sources inspected

- Repository instructions: AGENTS.md.
- Active branch handoff: HANDOFF.md and HANDOFF_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-SEED-BUDGET.md.
- Previous four-layout result and protocol: PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_RESULTS_2026-11-25.md and associated protocol.
- Current workflow 45616046681, full job log and artifact metadata.
- Current machine-readable report, posthoc report, result CSVs and artifact archive manifest.
- Previous report snapshot at commit 27c3e6668a34c4ea97de4cde5412602d896fb0dc.

## 3. Work performed

- Confirmed the current run completed all workflow steps: runtime/dispatch preflight, four morphology SHA-256 and q25 preflight checks, focused tests, complete 7/8/8/9-port calculation, exact coverage and finite-DFT identity gates, result archival commit and full artifact upload.
- Re-read the machine-readable report and all six primary output row counts.
- Compared the prior and current report's 144 basis-model records, including basis, projected conductance, projected capacitance and input hashes.
- Compared Git blob SHA-1 values for the tracked case-metric, candidate-vs-seven comparison, morphology/layout/window summary, source/layout/window summary and finite-DFT identity CSVs.
- Re-read the posthoc report and verified that its case-metric/comparison input SHA-256 values match the archived matrix manifest.
- Added a separate strict-dispatch replay report and run-specific artifact manifest. The existing artifact_archive_manifest.json remains the historical recovery manifest for source run 45585262246/artifact 15010408589; it was not overwritten or relabelled.

## 4. Protocol and runtime

The experiment uses order 168, four separate SWC morphologies, four port layouts, six expansion shifts, nine passive parameter scenarios, three source locations, two pulse widths, 10-pA pulses at 2-ms onset, 0.00625-ms step, 20/40-ms windows and a 0.5-µm NEURON segment cap.

- Python 3.12.16; NumPy 2.5.5; SciPy 1.16.3; NEURON 9.0.2.
- Haswell OpenBLAS, one thread; active NumPy targets X86_V3 and baseline(X86_V2).
- Runtime 2,510.29 s; peak RSS 1,233,904 KiB.

## 5. Acceptance results

- Report status: prima_q25_four_morphology_four_layout_boundary_ablation_passed.
- All four morphology checksums and q25 preflight contracts passed.
- Exact read-back coverage: 3,201 master frequency points; 1,075,536 frequency-summary rows; 12,096 case-metric rows; 9,072 matched candidate/seven comparisons; 144 source/layout/window summaries; 24 morphology/layout/window summaries; 1,728 finite-DFT identity rows.
- Maximum finite-DFT identity relative residual: 8.781488969255743e-12, below the 2e-8 tolerance.
- Maximum model identity relative residual: 8.743810650683813e-12.
- Maximum finite identity absolute residual: 4.809833427024806e-11 V-samples.
- Artifact 15027292605, 70,254,593 bytes; upload log SHA-256: 4171ef306c4e53a4f5ec0637883c33243d0f36294c80ff093753ec070ca0c8ab.

## 6. Reproducibility result

The prior/current reports contain the same 144/144 basis, projected-G, projected-C and input hash records; each report records 144 unique basis hashes. Five tracked numerical CSV Git blobs are byte-identical by Git object SHA. The report diff records CPU feature availability and runtime metadata changes, not a numerical matrix/hash change in these audited files.

This supports repeatability across the two observed runner CPU-feature maps for this pinned software and protocol. It is not a universal reproducibility claim for arbitrary CPUs, BLAS libraries, operating systems or future dependency versions. The 190-MB frequency-summary CSV remains in the Actions artifact and was not committed to Git.

## 7. Post-analysis and scientific interpretation

The posthoc report is marked passed and covers 3,024 matched case keys, 336 interaction summaries, 168 morphology summaries and 1,008 source summaries. Its input hashes match the primary case-metric and comparison matrices.

At fixed order 168, the combined q25 layout is strongly morphology-dependent. The median candidate/seven perturbation-coordinate transient ratios across 378 matched cases per morphology/window are about 25.27/49.84 for Tamas, 106.94/66.25 for Peng, 1.43/1.35 for the Allen epilepsy specimen, and 1.32/1.43 for Jacobs. Single-port layouts are generally much less extreme in Tamas/Peng. Ratios are reported alongside absolute error deltas because near-zero seven-port residuals can inflate ratios. The paired multiplicative contrast is descriptive of reduction errors, not a biological or causal interaction.

All four inputs are individual reconstructions, not population samples. Allen NMO_162186 is an epilepsy-surgery specimen. Peng NMO_163775 source metadata says No Diameter. The study is passive linear-RC only; it does not validate active channels, action potentials, synapses, plasticity, calcium signalling or biology. Full Hines remains canonical.

## 8. Files written and verification

- Detailed report: amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_STRICT_DISPATCH_REPLAY_2026-11-25.md; blob SHA-1 c5fd6293e0bd54d49887a62f8e66d2a38d2497f9.
- Run-specific artifact manifest: amsn-core/results/prima_q25_four_morphology_four_layout_strict_dispatch_replay_2026-11-25_manifest.json; blob SHA-1 5d27b8777f49d60e76d07bd9de63e25775c35bad.
- Updated handoff: HANDOFF.md; blob SHA-1 dfed41b693cff1e295b10af7adf589fb54705549.
- Result report includes the complete paired four-layout summary and limits. The run-specific manifest records artifact ID, ZIP digest, runtime, coverage and input/output hashes.
- No local solver execution was performed in this session. Numerical acceptance is based on the cited GitHub Actions run and read-back/commit evidence; no unperformed local test is claimed.

## 9. Next experiment and unresolved work

1. Complete isolated order-112/168/224 convergence run [45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005); the numerical sweep was still in progress at the last check after its runtime, checksum, test and strict order-168 reference gates passed.
2. Complete corrected q25 output-observer run [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575); its regression/reference gates passed, but the long analysis and corrected Git archival step were still in progress at the last check.
3. Keep PR #33/#34 open; do not merge or change production solver/port/order defaults without explicit authorization.
