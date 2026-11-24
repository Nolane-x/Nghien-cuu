# Research log — Cross-morphology PRIMA q25 extended backward-Euler tail audit

**Date:** 24 November 2026  
**Branch:** research/prima-q25-extended-backward-euler-tail-audit-2026-11-24  
**Status at creation:** implementation prepared; no extended-window numeric result claimed.

## Motivation

The pulse-weighted continuous-time AC proxy did not explain the large Tamas spectral ratio versus near-unity 20-ms transient NRMSE. The most direct next test is to use the exact finite-step implicit backward-Euler recurrence and determine whether the mismatch accumulates in the passive response tail after 20 ms.

## Design

For two checksum-pinned morphologies, 7- and 9-port order168 models, nine passive scenarios, three sources and two pulse widths:
- same 10-pA rectangular current, 2-ms onset, 2-ms/10-ms widths;
- exact dt=0.1ms backward-Euler equation;
- observation windows 20, 40, 100 and 200ms;
- compare every one of seven shared outputs against the same full-cable reference;
- verify computed 20-ms NRMSE against the previously archived 20-ms matched transient rows.

To keep the long tail tractable, the full cable tree matrix is factored once per morphology/scenario and solves six source/pulse right-hand sides together. Reduced BE transition/input operators are precomputed per layout/scenario and evolved with the same recurrence. No production solver code is modified.

## Expected exact coverage

- 6,048 cumulative transient output rows.
- 3,024 paired nine/seven rows.
- 756 20-ms archived NRMSE parity rows.
- 672 by-output summaries.
- 336 comparison summaries.
- 48 by-source summaries.
- 16 whole-window summaries.
- 32 layout/window summaries.

## Files

- `amsn-core/research/audit_prima_q25_extended_backward_euler.py`
- `amsn-core/tests/test_prima_q25_extended_backward_euler.py`
- `.github/workflows/amsn-prima-q25-extended-backward-euler-tail-audit.yml`
- `HANDOFF_2026-11-24_PRIMA-Q25-EXTENDED-BACKWARD-EULER-TAIL-AUDIT.md`
- This research log.

## Interpretation limits

A changing error ratio with observation window can indicate tail sensitivity, but not by itself a biological mechanism. The 20-ms parity gate must pass before interpreting later windows. Two passive morphologies are not populations. Full Hines remains the reference; production defaults remain untouched.
