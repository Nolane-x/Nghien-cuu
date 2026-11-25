# PRIMA q25 four-morphology output-aware dual-seed validation — protocol

**Date:** 25 November 2026  
**Status:** pre-registered research protocol; no cross-morphology result has yet been computed  
**Runner:** `research/run_prima_q25_four_morphology_output_aware_dual_seed_sweep.py`  
**Prototype:** `research/experimental_prima_output_aware_basis.py`

## 1. Research question

The Peng NMO_163775 nominal-scenario order224 pilot showed that q25 output-dual resolvent seeds can sharply reduce q25 transient residuals while preserving the original seven-port input selector. The next test asks whether that result persists across the four established morphology strata and all nine passive parameter scenarios, and whether the trade-off across the seven shared outputs is acceptable.

The cross-morphology sweep is confirmatory. It must not select a new schedule based only on the Peng nominal result.

## 2. Fixed model construction

For each morphology and passive scenario, hold the original seven retained input coordinates fixed:

[
C\dot{x}+Gx=B_7u,\qquad y_q=L_qx.
]

The six primal shifts remain the accepted values:

[
F_p=\{0,100,1000,3000,6000,10000\}\;\mathrm{Hz}.
]

At a predeclared subset of dual shifts, add

[
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T
]

for both q25 observation coordinates. The final reduced operators remain congruent:

[
G_r=V^TGV,\quad C_r=V^TCV,\quad
B_r=V^TB_7,\quad L_{q,r}=L_qV.
]

The input selector remains exactly seven ports for every schedule. The nine output rows are the seven shared observation coordinates and both q25 coordinates. No q25 node is inserted into (B_7).

Every morphology/scenario group is run in an isolated Python/NEURON child process to avoid carrying native HOC state between distinct SWC imports.

## 3. Morphology and scenario matrix

Run all four pinned reconstructions:
- NMO_03524 — Jacobs human Control.
- NMO_107159 — Tamas human pyramidal Control comparison.
- NMO_162186 — Allen L2/3 epilepsy-surgery specimen.
- NMO_163775 — Peng mouse Control (source metadata says No Diameter).

For every morphology, run all nine already-pinned passive parameter scenarios from the accepted four-morphology boundary-ablation contract. Do not change their parameter values or names. Each child process must validate the exact SWC SHA-256, record count and matching morphology preflight before importing it into NEURON.

## 4. Five predeclared dual-seed schedules

| Schedule | Dual q25 shifts | Initial dual columns | Rationale |
|---|---|---:|---|
| D0 | none | 0 | bitwise production multishift parity control |
| D1-low | 0 Hz | 2 | slow/DC output targeting |
| D1-mid | 1,000 Hz | 2 | intermediate output moment |
| D1-high | 10,000 Hz | 2 | fast output moment |
| D2-mid-high | 1,000 and 10,000 Hz | 4 | two-band output targeting |

Retain all five schedules in the confirmatory sweep. The Peng pilot suggests different median/tail and shared-output trade-offs, so pruning a schedule before observing the other morphology strata would be premature.

## 5. Fixed transient protocol

Hold fixed:
- basis order 224;
- six primal input expansion shifts listed above;
- nine passive parameter scenarios;
- current sources at soma, basal-q75 and apical-q75;
- 10-pA pulses starting at 2 ms, with 2-ms and 10-ms widths;
- timestep 0.00625 ms;
- 20-ms and 40-ms windows;
- NEURON segment cap 0.5 µm;
- pinned Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2;
- Haswell OpenBLAS with one thread and the verified NumPy dispatch target list X86_V3 plus baseline(X86_V2).

For each morphology/scenario group, compute the full-Hines reference once and reuse it across the five reduced bases. Every schedule is evaluated on all six source/pulse records, all nine output rows and both windows.

## 6. Acceptance and falsification gates

Every morphology/scenario group must satisfy:
1. Exact D0 equality with the existing production multishift PRIMA basis, projected G/C and input matrix.
2. Exactly seven retained input ports and nine independent output rows.
3. All five schedules reach order224.
4. Reduced G and C pass Cholesky positive-definiteness checks.
5. Basis orthogonality maximum absolute error below (2\times10^{-12}).
6. Record rank/seed columns, reduced-G/C condition numbers and hashes for each schedule.
7. Both q25 and all seven shared outputs are measured; report absolute percentage-point deltas with all paired ratios.
8. Exact worker-level and global CSV row counts are read back.
9. The predeclared finite-record BE DFT identity (soma input, 2-ms pulse, 20-ms record) passes for D0 and D2 in every morphology/scenario group, using tolerance (2\times10^{-8}).

A schedule is not accepted simply because q25 ratios become small. It is weakened or rejected if the shared outputs lose accuracy materially, a morphology/scenario subgroup regresses, conditioning deteriorates, D0 parity fails, or DFT/passivity/read-back gates fail.

## 7. Expected coverage

There are 4 morphologies × 9 scenarios = 36 isolated worker groups. Per group:
- 5 schedules × 2 windows × 6 source/pulse records × 9 outputs = 540 case rows.
- 5 schedules × 2 windows × 9 outputs = 90 group-summary rows.
- 2 finite-DFT identity rows (D0 and D2).

Global expected coverage:
- 19,440 case metrics.
- 3,240 morphology/scenario group summaries.
- 360 per-morphology summaries (including all nine scenarios).
- 810 per-scenario summaries (including all four morphologies).
- 90 pooled summaries.
- 72 finite-DFT identity rows.
- 180 schedule/basis metadata records.

Any missing group or read-back mismatch fails the run. All reports retain separate morphology/scenario strata; pooled statistics are supplementary.

## 8. Interpretation guardrails

The four inputs are individual morphology reconstructions, not a biological population. Allen NMO_162186 is an epilepsy-surgery specimen; Peng NMO_163775 metadata says No Diameter. This remains passive linear-RC model reduction. No active channels, action potentials, synapses, plasticity, calcium signalling or biological validity is established.

D0 q25 residuals in the initial Peng pilot were already very small in absolute terms. Relative ratios can exaggerate tiny changes when their baseline denominator is near zero. Always show absolute errors, absolute deltas, ratio distributions and all morphology/scenario strata together.

No production solver, retained-port default or PRIMA order default changes are authorized by this protocol. Full Hines remains canonical.
