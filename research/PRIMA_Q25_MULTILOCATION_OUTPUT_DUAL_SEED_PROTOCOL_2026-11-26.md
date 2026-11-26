# PRIMA q25-versus-edge multilocation output-dual seed experiment

**Date:** 26 November 2026  
**Status:** pre-registered research-only follow-up  
**Target:** four checksum-pinned reconstructions × nine passive scenarios  
**Basis cap:** 224  
**Model class:** passive linear-RC

## 1. Question

The accepted q25 study shows strong improvement at seeded q25 target nodes but inconsistent change at the four unseeded edge locations. This experiment reverses the seed placement: do dual seeds placed at the two basal/apical path-distance extremes improve the q25 readouts, and do q25 seeds transfer to the edge readouts?

The experiment tests seed-location transfer and seed-count effects. It is not allowed to tune seed frequencies or choose new locations after inspecting the current results.

## 2. Fixed model and measurement map

Keep unchanged:
- the seven canonical input ports and their exact SWC mapping;
- the six existing primal input expansion shifts;
- 10 kHz output-dual shift;
- order-224 basis cap and congruent projection;
- dt = 0.00625 ms backward-Euler integration;
- full-Hines reference;
- four pinned morphology reconstructions and nine passive parameter scenarios;
- three current sources (soma, basal-q75, apical-q75), 10 pA amplitude, 2 ms onset, 2 ms/10 ms pulses and 20 ms/40 ms windows.

All schedules observe the same 13 rows: seven canonical shared rows, basal/apical q25, and basal/apical q10/q95. The q10/q95 mapping and q25 mapping are pinned by the previous study's source hashes and node-ID assertions. No additional input port is created.

## 3. Predeclared schedules

| Schedule | Output-dual seed locations | Independent seed directions before orthogonalization |
|---|---|---:|
| D0_none | none | 0 |
| Q25_BOTH_10K | basal-q25 + apical-q25 | up to 2 |
| BASAL_EDGES_10K | basal-q10 + basal-q95 | up to 2 |
| APICAL_EDGES_10K | apical-q10 + apical-q95 | up to 2 |
| BOTH_EDGES_10K | basal-q10 + basal-q95 + apical-q10 + apical-q95 | up to 4 |

Every non-control schedule uses the same 10-kHz positive-real dual shift. All edge and q25 readouts remain measured in every schedule, even when a row is also used as a seed. This allows the same case keys to be compared across seed strategies.

For D0, the basis builder receives q25 observer indices only to preserve its non-empty output-selector contract; its output-seed frequency list is empty, so no dual output-seed vectors are constructed.

## 4. Schedule-specific interpretation

- Q25_BOTH_10K: q25 is seeded; four edge rows are unseeded spatial readouts.
- BASAL_EDGES_10K: two basal edge rows are seeded; q25 and apical edge rows are unseeded.
- APICAL_EDGES_10K: two apical edge rows are seeded; q25 and basal edge rows are unseeded.
- BOTH_EDGES_10K: all four edge rows are seeded; q25 is the principal unseeded dendritic readout.
- D0_none: all six q25/edge rows are unseeded baseline readouts.

A seed-location row is not described as a held-out validation for the schedule that uses it. Transfer claims must be evaluated on the other readout family and checked against the seven shared outputs.

## 5. Expected exact coverage

For each of 36 morphology/scenario workers, five schedules × two windows × six source/pulse records × 13 outputs produce:
- 780 case-metric rows per worker;
- 130 worker-summary rows per worker;
- 28,080 unique case rows globally;
- 4,680 worker-summary rows;
- 520 morphology/window summaries;
- 1,170 scenario/window summaries;
- 130 pooled/window summaries;
- 180 finite-record DFT identities (five schedules per worker);
- 180 basis/schedule metadata rows.

The finite-record DFT identity is evaluated on the established soma / 2-ms pulse / 20-ms reference record for all 13 output rows per schedule and morphology/scenario group. It is an algebraic consistency check for the declared record, not a new frequency sweep.

## 6. Acceptance gates

- All four SWC sources and preflight records match pinned SHA-256 hashes.
- Seven retained input ports remain bitwise identical in every schedule.
- Each schedule resolves exactly the predeclared seed labels and 10-kHz frequency.
- Seed indices are unique within a schedule and disjoint from the seven input ports.
- q25 and all four edge nodes are mutually distinct and disjoint from the seven shared nodes.
- D0 basis, reduced G/C and input matrix match production multishift PRIMA exactly.
- Every model reaches order 224; reduced G/C pass Cholesky; maximum basis orthogonality error < 2e-12.
- All 180 finite-record DFT identity rows pass relative tolerance 2e-8.
- CSV read-backs, exact row counts, unique paired keys and nine-file SHA-256 manifest all pass.
- Report all seed rows and unseeded readout rows separately, by output, morphology and passive scenario.

## 7. Primary analysis and interpretation

For every candidate/D0 pairing, compute:
- transient NRMSE (%);
- candidate/D0 ratio;
- candidate-minus-D0 absolute NRMSE delta in percentage points;
- better/worse case counts.

Use paired absolute error deltas as the primary practical effect measure when D0 is near the numerical floor. Ratios are secondary and must not obscure baseline errors near zero.

The primary directional tests are:
1. Does Q25_BOTH_10K improve the four edge readouts compared with D0?
2. Do basal/apical edge seeds improve the two q25 outputs?
3. Does BOTH_EDGES_10K transfer to q25 more reliably than single-branch edge seeding?
4. Are gains consistent across all four morphology strata, and do any candidate strategies materially regress the seven shared outputs?

No post-hoc schedule is promoted solely on its pooled median. These four morphologies are individual reconstructions, not a population sample. Report descriptive heterogeneity; do not claim inferential significance or a population effect.

## 8. Scientific and engineering limits

The model remains passive linear-RC. It does not simulate active channels, action potentials, synapses, plasticity, calcium signalling, metabolism or cognition. Full Hines remains canonical. The study is research-only and does not change production solver behavior, default port layout, integration method or default basis order.
