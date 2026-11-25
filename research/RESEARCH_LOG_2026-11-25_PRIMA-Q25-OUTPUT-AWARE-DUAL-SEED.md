# Research log — output-aware dual-seed PRIMA prototype

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Implementation commit:** `8a99f9a87e1f43d8f490760907d20f270b5a1840`  
**Focused test fix:** `0107abc8615bb113b249f7d907e96e0c4858a948`  
**CI:** [45633147052](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45633147052), completed success

## 1. Research motivation

The recovered q25 output-observer experiment showed that a q25 voltage can be measured from a full-compartment basis row without inserting that location into the retained input selector. However, the seven-port basis is still constructed exclusively from the seven retained input blocks. Retaining a q25 port can sharply reduce its own output error in some morphologies, while the other q25 observer may worsen.

The next hypothesis is that selected output-directed resolvent vectors could enrich the state basis without expanding the canonical seven-port input matrix.

## 2. Proposed construction

For a passive symmetric cable system,

[
Cdot{x}+Gx=B_7u,qquad y_q=L_qx,
]

the conventional primal shifted block is

[
R_p(sigma)=(G+sigma C)^{-1}B_7.
]

The proposed dual output block is

[
R_d(sigma)=(G+sigma C)^{-1}L_q^T.
]

The prototype orthogonalizes selected primal and dual blocks into one state basis V, then uses the repository's existing congruence projection:
- (G_r=V^TGV)
- (C_r=V^TCV)
- (B_r=V^TB_7)
- (L_{q,r}=L_qV)

The essential separation is that q25 dual vectors contribute to V, but q25 coordinates are **not added to B7**. The reduced input selector therefore remains the original seven retained ports. Because the final G/C projection is congruent, positive definiteness should be preserved subject to numerical tolerance; Cholesky checks are required.

## 3. Implementation and test result

Added research-only implementation:
- `amsn-core/research/experimental_prima_output_aware_basis.py`
- `amsn-core/tests/test_prima_q25_output_aware_dual_seed_basis.py`
- `amsn-core/research/PRIMA_Q25_OUTPUT_AWARE_DUAL_SEED_BASIS_PROTOCOL_2026-11-25.md`
- `.github/workflows/amsn-prima-q25-output-aware-dual-seed-tests.yml`

The first CI run [45632266526](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45632266526) failed during test collection because the research directory was not on `sys.path`. This was an import-path issue, not a numerical test failure. The test module was updated to insert its adjacent research directory, following the repository's existing test convention.

The repaired run [45633147052](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45633147052) completed **success**:
- both prototype and test modules passed `compileall`;
- **5 focused tests passed** in 0.12 seconds;
- empty dual-seed schedule reproduced the production multishift PRIMA basis, reduced G/C and input matrix exactly;
- selected output-dual seed inclusion in the basis was checked;
- the reduced input matrix retained only the requested original input ports;
- q25 output rows were exposed separately from the input selector;
- reduced G and C passed Cholesky checks and basis orthogonality passed;
- invalid index, duplicate index, frequency and order contracts were rejected.

## 4. What is and is not established

This CI establishes implementation parity for the no-dual-seed control and basic numerical invariants on a small branched passive cable fixture. It does **not** establish that output-aware dual seeding improves q25 accuracy on any of the four full morphologies. No full-morphology calculation has yet used this prototype. No production source, default, retained-port behavior or solver path has changed.

## 5. Proposed pilot

Prioritize Peng NMO_163775 because the order224 sweep still shows a residual combined-q25 transient ratio of 1.947 at 20 ms and 3.745 at 40 ms, even though the absolute median changes are only about 8.80e-12 and 4.12e-11 percentage points.

At order224 and the existing six primal shifts, compare predeclared q25 dual schedules:
- D0: no output dual seeds (bitwise-parity control).
- D1-low: 0 Hz.
- D1-mid: 1,000 Hz.
- D1-high: 10,000 Hz.
- D2-mid-high: 1,000 and 10,000 Hz.

Both q25 coordinates are seeded at selected output-dual shifts. Keep the input matrix B fixed at the seven canonical ports and keep the same current-source slots. Measure both q25 outputs and all seven shared outputs against full Hines. Record basis rank/orthogonality, projected G/C conditioning, seed columns per shift, absolute and relative errors, finite-window DFT identity, wall time and peak RSS.

Accept no schedule on q25 improvement alone: any material degradation of the seven shared outputs, passivity, DFT identity, or reproducibility is a reason to reject it. If the pilot is promising, extend to Tamas, Allen and Jacobs and then to the complete nine-scenario matrix.

## 6. Scientific guardrails

The four morphologies are individual reconstructions, not populations. The model remains passive linear-RC. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 metadata says No Diameter. No active channels, action potentials, synapses, plasticity, calcium signalling or biological validity is implied. Full Hines remains canonical and no production solver/default has changed.
