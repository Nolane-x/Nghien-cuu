# Handoff — PRIMA shift-distribution and order Pareto sweep

**Date:** 2026-11-22 (Asia/Bangkok)  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22  
**Pull request:** https://github.com/Nolane-x/Nghien-cuu/pull/7  
**Validated Actions run:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45002816664

## Validated result

The three-morphology matrix completed with **3/3 jobs successful**. Each job passed the complete AMSN test suite before running the Pareto sweep.

Validated coverage:
- 243 model records: 3 morphologies × 9 candidates × 9 parameter scenarios.
- 2,187 frequency records across nine AC frequencies.
- 10,206 transient per-port records across three sources, two pulse widths and seven retained output nodes.
- All 243 requested/achieved PRIMA orders matched exactly and every reduced G/C matrix passed Cholesky positive-definiteness checks.
- All three Actions artifacts were downloaded and SHA-256 verified against GitHub metadata.

## Key decision

Order112_extended_10khz gave the best AC residuals at 3, 6 and 10 kHz. At 10 kHz its median Z/Y errors were 0.000004681% / 0.00001390%, versus 0.0001951% / 0.0006225% for order112_narrow_3khz. Its median transient NRMSE was only 1.38% higher and the worst transient error was effectively identical. This is the strongest high-fidelity passive candidate in this matrix.

Order84_narrow_3khz is the lower-storage transient-oriented candidate. Order56_narrow_3khz is the smallest state/storage option but has materially larger transient and high-band errors.

The full 19-objective Pareto analysis leaves all nine candidates non-dominated. No single model should be declared universally best; candidate choice depends on the intended AC band, transient tolerance and resource budget.

## Persisted outputs

- amsn-core/research/HUMAN_PRIMA_SHIFT_ORDER_PARETO_2026-11-22.md
- amsn-core/research/analyze_human_prima_shift_order_pareto.py
- Candidate, frontier, transient, runtime, process-resource and artifact-manifest CSVs under amsn-core/results.

Full Hines remains canonical; production defaults are unchanged. These are passive linear RC results only.
