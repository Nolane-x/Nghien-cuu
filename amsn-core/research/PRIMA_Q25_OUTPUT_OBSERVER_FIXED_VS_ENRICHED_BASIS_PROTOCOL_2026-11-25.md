# PRIMA q25 output-observer: fixed versus enriched basis protocol

**Date:** 25 November 2026  
**Reference:** accepted four-morphology 7/8/8/9-port finite-window study at basis order 168  
**Analysis:** analyze_prima_q25_output_observer_fixed_vs_enriched_basis.py  
**Workflow:** ../../.github/workflows/amsn-prima-q25-output-observer.yml

## 1. Scientific question

The four-layout experiment adds basal-q25 and apical-q25 to the PRIMA retained-port set. The current implementation uses the retained-port selector as both the input matrix and the output observation map. Therefore, adding an output probe also changes the block rational-Krylov starting space.

This follow-up separates these two actions:

1. **Observe q25 without retaining it as an input/output port.** The q25 voltage is computed from the full-compartment basis row \(V[q25,:]\) while the input matrix \(B_r\) remains the seven-port selector.
2. **Retain q25 as a port.** The same q25 node is part of the layout's port selector, so it participates in the Krylov starting blocks as well as in the output map.

This is an observational counterfactual, not a new production model. It directly tests whether adding q25 to the retained-port set improves that q25 measurement and whether the basis change affects the seven shared observations.

## 2. Fixed data and numerical protocol

The study reuses the same four morphology SWCs, preflight checksums, q25 node IDs, source injection IDs and passive parameter scenarios as the accepted four-layout experiment:

- NMO_163775 Peng mouse Control.
- NMO_107159 Tamas human Control comparison pyramidal cell.
- NMO_03524 Jacobs human Control.
- NMO_162186 Allen human L2/3 epilepsy surgical specimen.

All four layouts are evaluated at the same PRIMA order 168. The numerical dispatch is pinned to OPENBLAS_CORETYPE=Haswell and NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR; one-thread settings and exact package versions are checked before the calculation. The observer run refuses to continue unless its runtime matches the primary run and all 144 basis/G/C/input hashes reproduce exactly.

The remainder is unchanged: nine passive parameter scenarios; source locations soma, basal-q75 and apical-q75; 10-pA pulses of 2 ms and 10 ms beginning at 2 ms; timestep 0.00625 ms; windows 20 ms and 40 ms; six rational-Krylov expansion shifts (0, 100, 1,000, 3,000, 6,000 and 10,000 Hz); NEURON segment cap 0.5 µm.

## 3. Output map

For each layout, the reduced output map is constructed in this order:

1. Seven shared output rows from the reduced model's input matrix, selected in the canonical seven-node order.
2. One full-compartment PRIMA basis row for basal-q25.
3. One full-compartment PRIMA basis row for apical-q25.

When a q25 node is retained in the layout, its full-compartment basis row must match its input-matrix row to 2 × 10⁻¹⁵ absolute tolerance. When it is not retained, the row is an observation-only output and does not enter the input selector, initial Krylov blocks or basis construction.

The reduced backward-Euler state trajectory uses the unchanged layout input matrix and source injection slots. Only its output map differs. Full-Hines comparison traces and frequency responses are measured at the seven shared nodes plus both q25 nodes.

## 4. Expected coverage

| Output | Rows |
|---|---:|
| Four morphology × nine scenarios × four layouts × three sources × two pulses × two windows × two q25 readouts | 3,456 |
| Matched candidate-layout vs seven-port q25 readout pairs | 2,592 |
| Source/layout/q25-role/window/metric summaries | 2,016 |
| Morphology/layout/q25-role/window/metric summaries | 336 |
| Finite-record DFT identity rows | 3,456 |
| Basis/G/C/input hash matches to the accepted primary report | 144 |

Every finite-record output includes full-model, reduced-model and finite-error DFT identity residuals. The maximum accepted relative identity residual remains bounded by 2 × 10⁻⁸. The output metrics include continuous-AC weighted error, discrete backward-Euler periodic-transfer error, canonical transient NRMSE, perturbation-coordinate transient NRMSE, finite error norm, periodic and terminal-boundary component norms, and their cross-term.

## 5. Interpretation

- If q25 output-only accuracy is poor in the seven-port basis but improves substantially in the eight-/nine-port layouts, the q25 nodes benefit from entering the Krylov starting space.
- If shared-seven output errors change among layouts while the basis hash for each layout matches the primary report, that change is attributable to the different retained-port basis, not to a changed numerical runtime.
- If the q25 output-only error is already low, adding the q25 port may have little marginal value for observation accuracy, even if it changes the rest of the basis.
- Ratios are reported alongside absolute error differences. A nearly zero seven-port q25 observer residual can make ratios unstable.
- The seven-port observer-only counterfactual is distinct from a true exact Schur/Kron port extension. It is a reduced output measurement using the same projected state basis.

This remains a passive linear-RC numerical study on four individual morphologies. It is not population-level or biological validation, and it does not change the full-Hines reference or any production default.
