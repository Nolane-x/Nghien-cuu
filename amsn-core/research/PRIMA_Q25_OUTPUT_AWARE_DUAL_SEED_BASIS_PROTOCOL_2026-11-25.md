# PRIMA q25 output-aware dual-seed basis — research protocol

**Date:** 25 November 2026  
**Status:** design proposal and research-only implementation; no full morphology result has been computed  
**Prototype:** amsn-core/research/experimental_prima_output_aware_basis.py  
**Unit tests:** amsn-core/tests/test_prima_q25_output_aware_dual_seed_basis.py

## 1. Motivation

The accepted q25 output-observer experiment separates output measurement from the retained input selector. It demonstrates that q25 outputs can be measured from rows of a full-compartment basis without adding q25 to the input matrix. However, the basis itself still came from the seven-port primal input block. Retaining the corresponding q25 node as a port can sharply improve that node's own output error, while sometimes worsening the other q25 observer.

This suggests a different question:

> Can the state basis be enriched with a small number of output-directed vectors while the reduced input selector remains the canonical seven ports?

This is a design proposal motivated by the recovered observer results. It is not yet an empirically validated improvement.

## 2. Mathematical construction

For a passive linear cable,

[
Cdot{x}+Gx=B_7u,qquad y_q=L_qx,
]

where B_7 contains only the seven canonical retained current-injection coordinates, and L_q selects basal-q25 and apical-q25 voltage observations.

At a positive-real shift σ=2πf, the conventional primal seed is

[
R_p(sigma)=(G+sigma C)^{-1}B_7.
]

For a symmetric passive RC operator, the corresponding output-dual seed is

[
R_d(sigma)=(G+sigma C)^{-1}L_q^T.
]

Build an orthonormal basis from the union of the primal shifted blocks and a predeclared, sparse subset of dual shifted blocks. Round-robin rational-Krylov growth then expands all accepted blocks under their own shifts. The final model is

[
G_r=V^TGV,qquad C_r=V^TCV,
]
[
B_r=V^TB_7,qquad L_{q,r}=L_qV.
]

The q25 observations therefore influence the state basis, but **q25 is never added to B_7** in this experiment. The input selector and all current-source slots remain the same seven-port selector used by the reference.

Because G and C are symmetric positive definite and the projection is congruent, the reduced G/C pair should remain symmetric positive definite up to numerical tolerance. The prototype uses the repository's existing passive projection function and its Cholesky checks rather than implementing a second projection path.

## 3. What this experiment isolates

The proposed comparisons separate three distinct design choices:

1. **Seven-port primal baseline:** only the seven-port shifted input blocks are used.
2. **Seven-port primal + sparse q25 dual seeds:** the input matrix remains seven-port, but selected q25 output resolvent columns enter the state basis.
3. **Nine-port primal reference:** both q25 nodes enter the retained input selector, as in the existing combined nine-port result.

The second case is the new treatment. It must not be mislabeled as a nine-port model: its input port count remains seven, even though its state basis has extra output-directed seed directions.

## 4. Initial seed schedules to compare

The initial pilot should use the same six primal shifts already validated for the primary study:

[
F_p={0,100,1000,3000,6000,10000} 	ext{Hz}.
]

Output-dual schedules should be declared before examining holdout errors:

| Schedule | Output-dual shifts | Purpose |
|---|---|---|
| D0 | none | exact implementation-parity control |
| D1-low | 0 Hz | DC / slow-output targeting |
| D1-mid | 1,000 Hz | mid-band targeted output moments |
| D1-high | 10,000 Hz | fast output-moment targeting |
| D2-mid-high | 1,000 and 10,000 Hz | modest multi-band output enrichment |

At each selected dual shift, both q25 output coordinates are seeded. The state-order cap is held fixed at 168 for the first full comparison. The initial added seed count, accepted rank per output shift, total final order, basis orthogonality and projected-matrix conditioning must be recorded. The D0 schedule must reproduce the existing multishift PRIMA basis bit-for-bit under the same runtime.

The schedules above are candidates, not a claim that 1,000 or 10,000 Hz is optimal. They are intentionally few to limit additional seed-budget consumption.

## 5. Fixed experiment protocol

Reuse the accepted four-morphology, four-layout provenance and source/node preflights:
- NMO_03524 Jacobs human Control.
- NMO_107159 Tamas human Control comparison cell.
- NMO_162186 Allen L2/3 epilepsy-surgery specimen.
- NMO_163775 Peng mouse Control (metadata says No Diameter).

Hold fixed: order 168; six primal expansion shifts; nine passive parameter scenarios; soma, basal-q75 and apical-q75 input sources; 10-pA current pulses of 2 and 10 ms at 2-ms onset; timestep 0.00625 ms; 20- and 40-ms windows; 0.5-µm NEURON segment cap; pinned Python/NumPy/SciPy/NEURON and one-thread Haswell OpenBLAS/NumPy dispatch contract.

The primary outcome is q25 perturbation-coordinate transient NRMSE versus full Hines. Also report canonical absolute-voltage transient NRMSE, discrete-BE transfer error, finite-record DFT identity, absolute error deltas, p90 ratios and source/pulse strata. Do not use a large relative ratio without its absolute error change.

## 6. Acceptance and falsification criteria

A schedule is accepted for numerical comparison only if:
- D0 reproduces the current production-library multishift basis exactly for the same input ports and runtime.
- The reduced input matrix is exactly V[B_7,:]^T, with exactly seven retained input ports.
- The output map is exactly the requested q25 rows L_qV; q25 output rows do not appear in the input selector unless they are already one of the seven canonical inputs (they are not in this pilot).
- The basis is orthonormal within the declared tolerance.
- Reduced G and C are symmetric positive definite and pass the existing Cholesky checks.
- The selected full-Hines and reduced finite-record DFT identities remain below 2×10⁻⁸.
- All expected case, comparison, summary and hash counts are read back exactly.

The hypothesis that sparse dual seeding is useful is weakened or falsified if it:
- consumes many states but does not reduce q25 output error relative to the seven-port basis;
- improves q25 only by degrading the seven shared output metrics materially;
- is unstable to the selected dual shift or passive parameter scenario;
- requires a substantially higher order to obtain the same error as the nine-port primal basis;
- fails any passivity, identity, or runtime-reproducibility gate.

A candidate is not recommended solely because it lowers q25 residuals; shared-seven outputs, runtime, peak RSS and conditioning must be evaluated together.

## 7. Scope and implementation boundary

The prototype lives in research/experimental_prima_output_aware_basis.py. It imports the existing private shifted Hines solve, orthogonalization and congruence projection helpers. It does not edit src/amsn/prima.py, the public PassiveReducedModel contract, the production runner, or any default. The final reduced model's input_matrix is formed from the original seven retained coordinates only; the q25 observation rows are exposed separately.

The first CI workflow is intentionally limited to deterministic unit tests and implementation-parity/passivity checks. It does not run the expensive four-morphology simulation and does not claim numerical improvement.

## 8. Next steps

1. Pass the research-only unit tests and confirm D0 bitwise parity.
2. Run a small, checksum-pinned pilot on one morphology to compare D0, D1-low, D1-mid, D1-high and D2-mid-high with fixed order and full-Hines reference.
3. If the pilot preserves seven shared outputs and improves q25 metrics, extend to all four morphologies and all nine parameter scenarios.
4. Only after the full matrix passes should a publication-quality result report be written. No production solver or default changes are authorized by this protocol.
