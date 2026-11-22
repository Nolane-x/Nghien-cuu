# Research log — PRIMA shift distribution × order Pareto sweep

**Date:** 2026-11-22  
**Branch:** research/prima-basis-transfer-protocol-robustness-2026-11-22

## Motivation

The 2026-11-22 basis-transfer experiment (PR #7) compared three basis construction methods at achieved order 56. The 10 kHz-extended basis improved 6 kHz and 10 kHz Z/Y residuals in all matched cases, but its transient per-port NRMSE was higher in all 1,134 pairings. This demonstrates that choosing expansion shifts from only one metric is unsafe.

## Hypothesis

At larger orders, the basis may have enough dimensions to retain useful high-frequency directions without sacrificing as much transient accuracy. A log-balanced shift allocation may also preserve low-frequency behavior better than the current extended set.

## Design

Cross orders 56, 84, 112 with three shift lists:
- narrow 3 kHz: 0/100/1,000/3,000 Hz;
- extended 10 kHz: 0/100/1,000/3,000/6,000/10,000 Hz;
- balanced 10 kHz: 0/10/100/1,000/3,000/10,000 Hz.

The same three morphology fixtures, nine Rm/Cm/Ra stress cases, nine frequency points, three source locations, two pulse widths and seven output ports are held fixed.

Expected per morphology: 81 model rows, 729 frequency rows, 3,402 transient-port rows. Every model must achieve its requested order and pass Cholesky positive-definiteness checks.

## Evidence state

Pending GitHub Actions. No model ranking or recommended default is recorded before all three morphology jobs and artifact validations finish.

## Scope limits

Deterministic ±20% passive parameter perturbations are stress cases, not biological confidence intervals. The Mohan2015 morphology is a partial dendritic reconstruction without an axon. All results remain passive linear RC reduction.
