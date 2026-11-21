# Research log — human passive PRIMA parameter robustness — 2026-11-21

## Question

Can a nominal order-56 multi-shift PRIMA basis be reused after passive parameter changes while retaining passivity and adequate current-to-voltage accuracy?

## Method

Added reproject_passive_cable_basis(reference_tree, perturbed_tree, reference_model). The API verifies same compartment count/order, same parent topology, same membrane geometry and same axial geometry. It holds the reference basis fixed and recomputes target projected G/C/B by congruence. Cholesky checks enforce positive-definite reduced matrices.

The human audit applies Rm, Cm and Ra changes ±20% individually and jointly (all-minus20/all-plus20) across three morphologies. Every scenario compares a frozen nominal 56-state basis with a freshly rebuilt 56-state multi-shift basis, both against the full perturbed Hines model. Frequency points are 0.1–10,000 Hz; transient is a basal-q75 10 pA, 2–12 ms pulse with 0.1 ms backward-Euler steps over 20 ms.

## Verification

Human workflow 44922676384 passed all 3 morphologies, 9 scenarios each. All 27 frozen and 27 fresh projected models passed Cholesky. Core CI 44922676436 passed 4/4; Python 3.12 and 3.13 each passed 108 tests and NEURON cross-validation passed.

## Results

- 56 states reduce 8,893–13,747 compartments by 99.3703–99.5926%.
- Frozen basis worst-case: Z 0.99456%, Y 0.97683%; max individual-port transient NRMSE 0.00062678%.
- Fresh basis worst-case: Z 0.45866%, Y 0.48450%; max individual-port transient NRMSE 0.00162920%.
- All worst frequency errors occur at 10 kHz, above the 3 kHz maximum expansion shift.
- Fresh basis is not better for every scenario; frozen basis wins several negative perturbations at equal order.

## Interpretation

Reprojection preserves positive definiteness and thus passive RC stability for the tested parameter sets, but it does not preserve approximation accuracy automatically. Accuracy must be checked against the full perturbed model. A parameter-aware multi-basis library or error-triggered rebuild rule is more defensible than always assuming either frozen or fresh is superior.

## Limits and next experiment

Parameter changes are deterministic ±20% sensitivity cases, not fitted biological parameter ranges. No active channels or nonlinear synapses are present. The high-frequency stress test goes beyond the 3 kHz expansion band. Next test source-location and waveform diversity and determine whether a 6/10 kHz shift or parameter-aware basis selection controls the residual more effectively.
