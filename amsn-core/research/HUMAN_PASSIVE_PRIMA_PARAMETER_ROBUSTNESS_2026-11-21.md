# Human passive PRIMA parameter-robustness audit

**Date:** 2026-11-21 (Asia/Bangkok)  
**Implementation commit:** https://github.com/Nolane-x/Nghien-cuu/commit/71b68e0a8820ef72375f765213e8468af7d5b357  
**Human parameter audit:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384 — 3/3 morphologies passed  
**Core CI:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676436 — 4/4 jobs passed, 108 tests on Python 3.12 and 3.13  
**Morphology summary CSV:** ../results/human_passive_prima_parameter_robustness_morphology_summary_2026-11-21.csv

## 1. Question

Can a 56-state multi-shift PRIMA model reuse its nominal Krylov basis when passive parameters change, or must the basis be rebuilt every time? The audit tests three human neuron morphologies while holding morphology geometry, compartment ordering, parent topology and seven retained source/probe ports fixed.

The parameter changes are deterministic sensitivity scenarios, not estimates of biological population variability:
- Specific membrane resistance Rm: −20% and +20%.
- Specific membrane capacitance Cm: −20% and +20%.
- Axial resistivity Ra: −20% and +20%.
- Joint corners: all three parameters −20% and all three +20%.
- A nominal unchanged-parameter scenario provides the baseline.

Leak reversal potential is held constant. Each scenario compares two 56-state models: (a) a frozen nominal basis reprojected onto the perturbed G/C matrices, and (b) a fresh multi-shift basis rebuilt with the perturbed parameters.

## 2. Method

The nominal basis uses positive-real shifts labelled 0, 100, 1,000 and 3,000 Hz. The frozen basis is not altered; the target model is formed by congruently projecting perturbed conductance, capacitance and port-input operators onto the original basis. The API rejects geometry or topology changes and checks positive definiteness of projected Gr and Cr by Cholesky factorization.

Each model is compared against the full Hines solution for the perturbed tree at nine frequencies: 0.1, 1, 10, 100, 300, 1,000, 3,000, 6,000 and 10,000 Hz. The 6–10 kHz points deliberately stress extrapolation beyond the original 3 kHz expansion band. The 10 pA basal-q75 pulse is applied from 2 to 12 ms and simulated for 20 ms with backward Euler at 0.1 ms. All seven retained port traces are compared.

The three morphology models have 8,893–13,747 full compartments. A 56-state projection removes 99.3703–99.5926% of states. The audit includes 27 parameter scenarios and compares 54 projected models (27 frozen-basis, 27 fresh-basis).

## 3. Results

All maximum frequency-response errors in this robustness run occurred at 10 kHz. The following table reports worst-case error over nine scenarios for each morphology.

| Morphology | Full states | Frozen basis max Z/Y error | Fresh basis max Z/Y error | Frozen max single-port transient NRMSE | Fresh max single-port transient NRMSE |
|---|---:|---:|---:|---:|---:|
| NMO_68174 cell1125 | 12,399 | 0.76097% / 0.97683% | 0.35161% / 0.48450% | 0.00005640% | 0.00029749% |
| NMO_68175 cell1204 | 13,747 | 0.50385% / 0.86312% | 0.24125% / 0.43753% | 0.00001119% | 0.00001961% |
| NMO_290988 Mohan2015 | 8,893 | 0.99456% / 0.89531% | 0.45866% / 0.45339% | 0.00062678% | 0.00162920% |

Global worst values:
- Frozen basis: Z 0.99456%, Y 0.97683%, all-port transient NRMSE 0.000003155%, maximum single-port transient NRMSE 0.00062678%.
- Fresh basis: Z 0.45866%, Y 0.48450%, all-port transient NRMSE 0.000008216%, maximum single-port transient NRMSE 0.00162920%.

All 54 reduced models passed Cholesky checks for projected Gr and Cr. Therefore basis reprojection preserved the passive positive-definite structure for every tested parameter set.

## 4. Interpretation

**Passivity is robust; accuracy is not automatically invariant.** Reprojection preserves the mathematical passive/stable structure, but it does not preserve the nominal transfer function exactly. At the combined +20% corner, frozen-basis worst errors reach 0.995% in impedance and 0.895% in admittance for NMO_290988, while the fresh basis lowers these values to 0.459% and 0.453%.

**A fresh basis is not uniformly better for every scenario.** For several −20% scenarios, the frozen basis has smaller frequency-response errors than a freshly built basis of the same order. Conversely, the fresh basis generally improves the +20% high-capacitance/high-resistance corners. Same-order basis rebuilding is therefore not a guaranteed accuracy improvement; the basis distribution and target parameter regime both matter.

**Transient accuracy remains high in this one pulse protocol.** The worst frozen-basis individual-port NRMSE is 0.0006268%; the fresh-basis maximum is 0.0016292%. The difference in transient error is larger for NMO_290988 than the other two morphologies, but remains small under this tested basal-q75 pulse. Other pulse locations and waveforms remain untested.

**The frequency stress test matters.** The model was originally built with shifts up to 3 kHz, whereas this sensitivity audit also evaluates at 6 and 10 kHz. The maxima occur at 10 kHz. These results are extrapolation-stress measurements, not proof that a 56-state model is uniformly validated through 10 kHz.

## 5. Implementation and validation

New API: amsn.reproject_passive_cable_basis(reference_tree, perturbed_tree, reference_model).

It checks equal compartment counts, identical parent-index topology, equal membrane areas and equal axial geometry. It then reprojects the new parameter matrices onto the unchanged basis. It fails closed for geometry/topology mismatches. Its contract explicitly requires callers to revalidate approximation error after each parameter change.

Core CI run 44922676436 passed all four jobs. Python 3.12 and 3.13 each passed 108/108 tests; both NEURON cross-validation jobs passed. Human audit 44922676384 passed all three morphology jobs, each with nine scenarios and 54 parameterized reduced models across the whole matrix.

Raw artifacts:
- NMO_68174 cell1125: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384/artifacts/14714446601
- NMO_68175 cell1204: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384/artifacts/14714033920
- NMO_290988 Mohan2015: https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384/artifacts/14714670830

## 6. Limits and next work

This is numerical sensitivity analysis on a passive RC model, not biological parameter fitting or biological validation. The ±20% scenarios are deterministic perturbations, not a claim about physiological distributions. The 6–10 kHz region lies outside the current multi-shift basis expansion points. NMO_290988 is a partial dendritic reconstruction without an axon and has a mesiotemporal-sclerosis context; it is not a healthy-control morphology.

Keep the full Hines implementation as the canonical solver and PRIMA as an optional reduced passive subsystem. Before using basis reuse in a broader simulation, test multiple source ports, broader pulse widths and waveforms, finer frequency grids near 3–10 kHz, and parameter paths rather than only the eight nonzero perturbation scenarios. A useful next design is a parameter-aware or multi-basis library with an explicit error-triggered rebuild rule.
