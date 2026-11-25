# PRIMA q25 Jacobs role-specific output-dual seed allocation — protocol

**Date:** 25 November 2026  
**Status:** pre-registered research experiment  
**Target:** Jacobs human control reconstruction, NeuroMorpho ID NMO_03524  
**Basis order:** 224  
**Code:** research/prima_q25_jacobs_role_specific_seed_allocation.py

## 1. Motivation and question

The accepted four-morphology × nine-scenario sweep found that the joint 10 kHz dual-seed schedule strongly improved q25 output errors in Tamas, Allen and Peng, but Jacobs was an exception. In Jacobs, the basal q25 output generally improved while the apical q25 output was near-neutral or slightly worse; adding both 1 kHz and 10 kHz dual shifts produced a clear apical penalty in the pooled scenario summaries.

This experiment isolates the output-seed target. It asks whether adding a dual resolvent column for the apical q25 coordinate alone can improve apical readout without paying for a basal dual seed, and whether basal-only targeting gives the complementary trade-off. It also checks whether the joint-seed result is reproducible under the same pinned conditions.

## 2. Fixed construction

Keep the seven original retained input coordinates exactly fixed:

\[
C\dot{x}+Gx=B_7u,\qquad y_q=L_qx.
\]

The six accepted primal expansion shifts, order 224, congruent PRIMA projection, reduced BE integrator, NEURON segment cap, full-Hines reference, and output readout protocol remain unchanged. A dual seed for selected output rows is added only to the state basis:

\[
R_d(\sigma)=(G+\sigma C)^{-1}L_q^T.
\]

The input selector remains the original seven-port B_7. The two q25 nodes are measured through independent basis rows and are not inserted into the input selector. Every model exposes the same seven shared outputs plus basal-q25 and apical-q25 observations.

## 3. Predeclared schedules

| Schedule | Dual-seed target | Dual shifts |
|---|---|---:|
| D0_none | none | none |
| APICAL_0 | apical q25 only | 0 Hz |
| APICAL_1K | apical q25 only | 1,000 Hz |
| APICAL_10K | apical q25 only | 10,000 Hz |
| BASAL_0 | basal q25 only | 0 Hz |
| BASAL_1K | basal q25 only | 1,000 Hz |
| BASAL_10K | basal q25 only | 10,000 Hz |
| BOTH_1K | both q25 nodes | 1,000 Hz |
| BOTH_10K | both q25 nodes | 10,000 Hz |
| BOTH_1K_10K | both q25 nodes | 1,000 and 10,000 Hz |

The schedule list is fixed before inspecting the new experiment's measurements. The joint BOTH_10K schedule is an exact replay anchor against the accepted cross-morphology study, not a newly selected candidate.

## 4. Scenario and measurement matrix

Run all nine pre-existing Jacobs passive parameter scenarios, without changing their values or names. For each scenario, build the full-Hines reference once and compare all ten schedules over:

- three current-source locations: soma, basal-q75 and apical-q75;
- two pulse widths: 2 ms and 10 ms; 10 pA amplitude, 2 ms onset;
- two observation windows: 20 ms and 40 ms;
- all nine readout rows: seven shared outputs, basal q25 and apical q25.

This yields 10 × 9 scenarios × 6 source/pulse records × 2 windows × 9 outputs = **9,720 paired case rows**. Each schedule/window/output summary contains six paired cases within a scenario. Pooled summaries retain explicit output labels and windows.

## 5. Verification gates

Every scenario worker must pass:

1. source SHA-256, record-count and morphology-preflight checks;
2. exact D0 parity with production multishift PRIMA for basis, reduced G/C and input matrix;
3. exact seven-port input selector and all nine measurement rows;
4. order 224 for every schedule;
5. Cholesky-positive reduced G and C matrices;
6. basis orthogonality error below 2e-12;
7. finite transient metrics for every declared output/source/pulse/window combination;
8. the finite-record BE DFT identity for D0, apical-only 10 kHz, basal-only 10 kHz, joint 10 kHz and joint 1+10 kHz schedules, on the declared soma/2 ms/20 ms record, tolerance 2e-8;
9. exact CSV read-back and unique case keys;
10. bit-exact nominal Jacobs basis hashes and case metrics for D0 and joint 10 kHz against the already accepted four-morphology archive.

An apical-only seed is not deemed successful merely because the apical q25 improves. Report all seven shared outputs and basal q25 too. Use absolute NRMSE and absolute percentage-point deltas alongside paired ratios.

## 6. Interpretation limits

This is one individual human control morphology with nine passive parameter perturbations, not a biological population. It remains passive linear-RC model-reduction evidence. It does not validate active channels, action potentials, synapses, plasticity, calcium signalling or biological function. Relative ratios can be unstable when the D0 output error is close to the numerical floor. No production solver, default retained-port layout or default PRIMA order is changed; full Hines remains canonical.
