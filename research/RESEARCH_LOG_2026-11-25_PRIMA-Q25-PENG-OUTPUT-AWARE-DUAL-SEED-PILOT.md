# Research log — Peng q25 output-aware dual-seed pilot

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** research/prima-q25-cross-morphology-boundary-replication-2026-11-25  
**Accepted workflow:** [45636631081](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081)  
**Results commit:** `22ba7b6994c871d3784f5abf15a2fe9311abe60d`  
**Artifact:** [15033336785](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081/artifacts/15033336785)

## 1. Question

Can output-directed dual resolvent vectors improve both q25 voltage readouts without adding the q25 locations to the seven-port current-input selector?

## 2. Implemented pilot

A research-only prototype builds a state basis from the existing six shifted seven-port primal input blocks plus a sparse, predeclared set of output-dual q25 blocks. The final projection remains congruent and the model retains exactly seven input ports with a separate nine-row output map.

The Peng NMO_163775 nominal-scenario order-224 pilot compared:
- D0: no output dual seeds;
- D1-low: 0 Hz;
- D1-mid: 1,000 Hz;
- D1-high: 10,000 Hz;
- D2-mid-high: 1,000 and 10,000 Hz.

All five schedules reached order224. Six primal shifts contributed 42 accepted initial input columns; each single-shift dual schedule contributed two output columns and D2 contributed four. The input selector was exactly unchanged at seven ports.

## 3. Accepted CI and archive

Workflow 45636631081 completed success through the numerical pilot, report/CSV read-back, Git commit and artifact upload. The five focused tests also passed.

- Expected/read-back case metrics: 540/540.
- Expected/read-back schedule summaries: 90/90.
- Artifact ZIP size: 77,205 bytes.
- Artifact ZIP SHA-256: `a19c928f99eb361300a6f5c8e793550e3cc1854dd177ed4739271ba459d5a95b`.
- Runtime: 28.82 seconds.
- Source SWC has 4,209 records and SHA-256 `94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f`.

The artifact's four numerical/report files, SWC and preflight are checksummed in the machine-readable manifest.

## 4. Main result

Across 24 q25 cases per schedule (two q25 outputs × six current records × two windows), every dual-seed schedule improved every paired q25 transient NRMSE against D0.

Pooled q25 median NRMSE fell from (5.162\times10^{-7}\%) under D0 to:
- D1-low: (1.840\times10^{-11}\%);
- D1-mid: (2.079\times10^{-11}\%);
- D1-high: (9.924\times10^{-12}\%);
- D2-mid-high: (1.138\times10^{-11}\%).

Median paired ratios ranged from (1.60\times10^{-5}) to (4.11\times10^{-5}), equivalent to approximately 24,000–62,000× lower q25 residuals at the median. The worst paired ratio per schedule remained below 0.0052; the q25 cases were 24/24 improved for each schedule.

However, D0 q25 errors were already very small in absolute terms. This is a numerical residual reduction, not proof of a material physical measurement gain.

## 5. Shared-output trade-off

Across 84 shared-output cases per schedule (seven rows × six current records × two windows), the D0 median error was (1.230\times10^{-11}\%). Candidate medians ranged from (1.388\times10^{-11}\%) to (1.843\times10^{-11}\%). Relative ratios sometimes rose because the baseline denominator is near zero. The largest paired absolute change was (6.782\times10^{-11}) percentage points (D2).

D1-low is a conservative low-seed candidate with the smallest median shared-output ratio increase. D1-high gives the lowest median q25 absolute error. D2 has a similar q25 median ratio but uses four dual seeds and has the largest maximum shared-output absolute delta. D1-mid provides a different tail/median trade-off. No schedule is promoted as a default.

## 6. Numerical checks

- D0 basis, projected G/C and input matrix were asserted exactly equal to the existing production multishift PRIMA build; successful completion confirms parity.
- All five bases reached order224, kept seven input ports, and passed Cholesky checks for reduced G and C.
- Basis orthogonality errors were (9.99\times10^{-16}) to (1.55\times10^{-15}).
- Reduced-G condition numbers were about (5.251\times10^5)–(5.258\times10^5); reduced-C condition numbers about 125.47–125.54.
- A finite-record BE DFT identity on the predeclared soma/2-ms/20-ms record passed for D0 and D2 over 1,601 bins. Full-Hines, D0 reduced and D2 reduced maximum relative identity residuals were 3.36e-13, 1.10e-13 and 2.25e-13 respectively, all below 2e-8.

The DFT identity sample is limited to one input record and two schedules; it is not a complete frequency audit of all cases.

## 7. Duplicate rerun reconciliation

An overlapping run [45636849975](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636849975) passed calculation and exact coverage checks but hit add/add conflicts on report and timing files during Git rebase because the canonical successful run 45636631081 had already committed those paths. The duplicate run uploaded no artifact. Use run45636631081 as the canonical result.

## 8. Limits and next action

This is one morphology and one nominal passive scenario, not a four-morphology or nine-scenario conclusion. The model is passive linear-RC only. No active-channel, synaptic, plasticity, action-potential or biological-population inference is established. Production `src/amsn/prima.py` and all defaults remain untouched; full Hines remains canonical.

Next: extend the same five schedules to all four morphology strata and all nine passive parameter scenarios at order224. Keep separate morphology/scenario summaries, require D0 exact parity and all seven shared/two q25 outputs, check G/C positivity and orthogonality, and include a predeclared DFT identity sample for every morphology/scenario under D0 and D2.
