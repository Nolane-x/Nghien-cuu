# Segev matched-support passive admittance operator — verified results

**Date:** 2026-11-21 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation commit:** [96f857c41d4e7263209125a28d680baa05b95d47](https://github.com/Nolane-x/Nghien-cuu/commit/96f857c41d4e7263209125a28d680baa05b95d47)  
**Passive operator workflow:** [44904475571 — successful, 2/2 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571)  
**Core CI:** [44904475559 — successful, 4/4 jobs](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475559)  
**Summary CSV:** [human_segev_passive_admittance_operator_summary_2026-11-21.csv](../results/human_segev_passive_admittance_operator_summary_2026-11-21.csv)

## 1. Research question

After validating the global axial graph and projecting NEURON's measured membrane area onto the same SWC electrical control volumes, do the combined passive leak-plus-capacitance admittance operators remain close across DC and 0.1–3,000 Hz?

## 2. Operator and scope

The matched-support small-signal phasor operator is:

Y(ω) = L_axial + diag(A_i/Rm + j·2πf·Cm·A_i).

The experiment used fixed parameters:
- Rm = 1.0 Ω·m²
- Cm = 0.01 F/m²
- Eleak = −65 mV
- NEURON 9.0.2, 0.125 µm maximum segment length.

The reversal potential affects the steady-state source/reference term; it does not add a diagonal contribution to the linear small-signal admittance matrix. Both models use the same electrical SWC nodes and axial edges. The NEURON support area is allocated from actual segment.area() values over the pt3d overlap of each SWC half-edge.

**Important distinction:** the NEURON side is a matched-support finite-volume projection built from the already-validated reduced axial edge conductances and projected segment areas. It is not an exact Schur complement of the original fine NEURON segment-level admittance matrix. Therefore this result validates the matched-support passive operator, not exact equivalence of the original native discretizations.

For each morphology, the operator was applied to 32 deterministic complex random voltage vectors (seed 20261121, 10 mV standard deviation) at eight frequencies: DC, 0.1, 1, 10, 100, 300, 1,000 and 3,000 Hz. The reported relative L2 statistics are sampled-vector errors, not a formal induced matrix norm.

## 3. Results

| Metric | NMO_68174 / cell1125 | NMO_68175 / cell1204 |
|---|---:|---:|
| Electrical nodes | 12,399 | 13,747 |
| Axial edges | 12,398 | 13,746 |
| NEURON segments | 166,856 | 156,471 |
| Specific membrane resistance | 1.0 Ω·m² | 1.0 Ω·m² |
| Specific capacitance | 0.01 F/m² | 0.01 F/m² |
| Maximum sampled passive-operator relative L2 error over 0–3 kHz | **0.0078381%** | **0.0025449%** |
| Maximum leak-diagonal sampled relative L2 error | 0.0002472% | 0.0002153% |
| Maximum capacitance-diagonal sampled relative L2 error | 0.0002472% | 0.0002153% |
| Maximum absolute node-current difference | 7.159e-10 A | 2.581e-10 A |
| Maximum axial current conservation residual | 3.547e-21 A | 6.035e-21 A |
| Constant-voltage axial nullspace residual | 0 A | 0 A |

### Passive operator by frequency

The following statistics are percentages, converted from the raw relative L2 ratios in the CSV.

| Cell | Frequency | Median | P95 | Maximum |
|---|---:|---:|---:|---:|
| NMO_68174 | DC | 0.00378423% | 0.00628628% | 0.00783803% |
| NMO_68174 | 0.1 Hz | 0.00378423% | 0.00628628% | 0.00783803% |
| NMO_68174 | 1 Hz | 0.00378423% | 0.00628628% | 0.00783803% |
| NMO_68174 | 10 Hz | 0.00378423% | 0.00628628% | 0.00783803% |
| NMO_68174 | 100 Hz | 0.00378422% | 0.00628628% | 0.00783803% |
| NMO_68174 | 300 Hz | 0.00378422% | 0.00628628% | 0.00783803% |
| NMO_68174 | 1,000 Hz | 0.00378420% | 0.00628630% | 0.00783804% |
| NMO_68174 | 3,000 Hz | 0.00378413% | 0.00628635% | 0.00783807% |
| NMO_68175 | DC | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 0.1 Hz | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 1 Hz | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 10 Hz | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 100 Hz | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 300 Hz | 0.00202198% | 0.00252775% | 0.00254492% |
| NMO_68175 | 1,000 Hz | 0.00202198% | 0.00252776% | 0.00254492% |
| NMO_68175 | 3,000 Hz | 0.00202198% | 0.00252776% | 0.00254492% |

The combined operator error changes only slightly over this frequency range under the chosen fixed passive parameters. The axial graph dominates these sampled-vector differences; leak and capacitance diagonal differences are much smaller because the per-node area distributions already agree closely.

## 4. Interpretation

For these two Segev morphologies, the matched-support passive admittance operator agrees very closely across the tested frequencies:
- Maximum sampled relative L2 error is below 0.008% for NMO_68174 and below 0.0026% for NMO_68175.
- The leak and capacitance diagonal terms independently inherit the close node-area support agreement and remain below 0.00025% in the reported sampled relative L2 metric.
- Axial current is conserved to approximately 1e-21 A, and a constant voltage produces zero axial current.

This is a substantial numerical consistency result for the matched electrical support. It does not prove that the fine NEURON segment-level admittance matrix is exactly equivalent to the reduced node-centred operator; that would require an explicit, independently verified Schur-complement reduction. It also does not validate the biological correctness of the generic passive parameters, active channels, synapses, spines or human cortical physiology.

## 5. Reproducibility

Workflow [44904475571](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571) passed both Segev jobs:
- NMO_68174 / cell1125: [artifact 14707505849](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571/artifacts/14707505849).
- NMO_68175 / cell1204: [artifact 14706784655](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571/artifacts/14706784655).

Core CI [44904475559](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475559) passed 4/4 jobs: Python 3.12/3.13 tests and both NEURON 9.0.2 cross-validation jobs.

Raw artifacts contain the area-support CSV, axial edge-conductance CSV, passive admittance CSV and job log. Summary data: [CSV](../results/human_segev_passive_admittance_operator_summary_2026-11-21.csv).

## 6. Next step

The next scientifically meaningful step is not to add arbitrary nonlinear mechanisms yet. First compare this matched-support operator against selected direct NEURON Impedance and transient responses, then assess whether a true fine-tree Schur-complement reduction can be built and validated. After the passive baseline is locked, introduce active channels and synapses as separately named configurations with traceable source provenance.
