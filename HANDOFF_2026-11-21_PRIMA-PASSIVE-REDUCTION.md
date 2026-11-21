# Handoff — PRIMA passive reduced-order model

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Latest implementation commit:** 7cfd4b7b59b828582fa81c336d3073ef05fe579b  
**Human audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972 — 6/6 passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918897010 — 4/4 passed

## Read first

1. HANDOFF.md and the previous Schur handoff HANDOFF_2026-11-21_HUMAN-SCHUR-PORT-MATRIX.md.
2. AMSN core code in amsn-core/src/amsn/cable.py, reduction.py and prima.py.
3. Research report amsn-core/research/HUMAN_PASSIVE_PRIMA_REDUCTION_AUDIT_2026-11-21.md.
4. The human Schur port audit report and its exact port-matrix results.

## New API

- amsn.prima_reduce_passive_cable(tree, retained_indices, max_order=64, relative_tolerance=1e-12)
- amsn.PassiveReducedModel
- Module: amsn-core/src/amsn/prima.py

The reduction is a PRIMA-style, structure-preserving block Krylov projection for the passive RC descriptor system. The basis begins with G inverse times B and expands under negative G inverse C. The full Hines solver is reused for each DC inverse action. Congruence projection forms reduced G, C and B, and Cholesky checks verify positive definiteness.

The reduced state is not in one-to-one correspondence with anatomical compartments. It is a set of global voltage modes whose outputs are the retained port voltages. It is intended only for the passive linear RC subsystem.

## Verified scope

- Six human morphology/reference-mesh jobs passed.
- Each job ran 95 tests and compared seven-port impedance/admittance at eight frequencies from 0.1 to 3,000 Hz.
- Each job compared a 20 ms, 10 pA basal-q75 pulse at dt=0.1 ms.
- The order-56 model reduced 8,893–13,747 full compartments to 56 states (99.37–99.59% fewer).
- Worst tested port impedance error: 1.9661%; worst admittance error: 2.3601%, both at 3 kHz.
- Worst individual-port transient NRMSE: 0.00015662%.
- Core CI passed on Python 3.12 and 3.13 (95/95 tests each) and both NEURON validation jobs.

## Limits

This does not establish biological validity or accuracy for active ion channels, nonlinear synapses, calcium, ion concentration, metabolic or plasticity subsystems. NMO_290988 is incomplete, has no axon, and is associated with a mesiotemporal-sclerosis context. The fixed passive parameters are numerical defaults, not human population fits. Keep the full Hines solver as canonical.

## Next work

Run a frequency-aware/multi-shift passive Krylov order sweep (28, 56, 84, 112), optimize the high-frequency residual without losing passivity, then repeat with different pulse locations and waveform widths. Only after that should this be coupled to active/synaptic dynamics.


## Follow-on: multi-shift PRIMA and order sweep — completed 21/11/2026

Added public API amsn.prima_reduce_passive_cable_multishift with positive-real expansion points 0/100/1,000/3,000 Hz. It retains congruence projection and Cholesky checks. Human audit [44919965612](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44919965612) passed 6/6; Core CI [44919965657](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44919965657) passed 4/4 and 99 tests on Python 3.12/3.13. At equal order 56, maximum 3 kHz impedance/admittance errors fell to 0.02002%/0.02361% across all three morphologies.

The subsequent order sweep [44920477444](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477444) passed 6/6, with Core CI [44920477434](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44920477434) passing 4/4 (99 tests on both Python versions). Orders 28/56/84 were evaluated. Order 28 is too inaccurate for the full tested band; order 56 is a strong balance; order 84 reduces worst 3 kHz admittance error to 0.0001823% while still removing 99.055–99.389% of states. See [multi-shift/order-sweep report](amsn-core/research/HUMAN_PASSIVE_PRIMA_MULTISHIFT_ORDER_SWEEP_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_multishift_order_sweep_summary_2026-11-21.csv).


## Current API and recommendation

Multi-shift method: amsn.prima_reduce_passive_cable_multishift(..., expansion_frequencies_hz=(0, 100, 1000, 3000)). The order sweep indicates order 56 as the balanced preset and order 84 as the high-accuracy option for the tested 0.1–3 kHz passive seven-port problem. Order 28 is not recommended for full-band use because the worst individual-port transient error is much larger. Full Hines remains canonical.
