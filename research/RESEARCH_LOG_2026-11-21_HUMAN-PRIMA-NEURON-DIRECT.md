# Research log — direct PRIMA versus NEURON — 2026-11-21

## Question

Does the multi-shift reduced passive port model preserve agreement with independent NEURON port matrices, not merely agreement with the full AMSN Hines network?

## Method

Extended human_schur_port_matrix_audit.py to compute direct Frobenius relative errors between each PRIMA port impedance/admittance matrix and the NEURON port impedance/admittance at the same seven SWC-defined ports and eight frequencies. Added these metrics for DC PRIMA, multi-shift order 56, and order-sweep orders 28/56/84. The six morphology × NEURON-mesh jobs test three morphologies with 0.125 and 0.0625 µm NEURON reference caps.

## Results

Human run 44921474635 passed 6/6. Core CI 44921474632 passed 4/4, with 99/99 tests on Python 3.12 and 3.13 and both NEURON cross-validation jobs.

Full AMSN-Hines-to-NEURON discrepancy:
- Z maximum 0.08941851%.
- Y maximum 0.02617965%.

Direct PRIMA-to-NEURON global maxima:
- Order 28: Z 1.87920%, Y 2.33160%; max individual transient NRMSE 1.70973%.
- Order 56: Z 0.0939333%, Y 0.0213333%; max individual transient NRMSE 0.000315604%.
- Order 84: Z 0.0894285%, Y 0.0261073%; max individual transient NRMSE 0.0000008743%.

Order 84 internal PRIMA-versus-Hines errors are only 0.00009368% Z and 0.0001823% Y, so further increasing order is unlikely to reduce the direct NEURON difference materially until the full-model discrepancy is reduced.

## Interpretation

Order 56 is the balanced passive port model; order 84 is the high-accuracy reduction whose internal residual is below the observed cross-simulator discrepancy. Order 28 is not sufficient for the full test band and pulse protocol. This is numerical validation, not biological validation; active channels and synapses are out of scope.

## Next experiments

Test more source ports/pulse widths; measure robustness under passive parameter perturbation with a fixed basis; extend the frequency evaluation above 3 kHz; and only then evaluate controlled coupling to active channels.
