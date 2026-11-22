# Research log — final nine-port PRIMA enrichment result

**Date:** 2026-11-22 (Asia/Bangkok)  
**Merged code commit:** `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`  
**PR:** https://github.com/Nolane-x/Nghien-cuu/pull/3

## Question and hypothesis

Would adding basal/apical q25 probe ports to the seven-port retained basis reduce the recurring apical-q90 transient error while preserving existing transfer paths?

Hypothesis: enriching the retained boundary with intermediate branch quantiles may improve the reduced transfer representation at apical-q90. Falsification criterion: apical-q90 error fails to improve against the same seven-port node under identical model, morphology, mesh and input scenario.

## Implementation completed

- Added deterministic SWC path-distance quantile helpers in `amsn-core/src/amsn/ports.py`.
- Added an optional Import3D enrichment helper in `amsn-core/examples/human_prima_port_enrichment.py`.
- Added opt-in nine-port mode to the Schur/PRIMA audit; the canonical seven-port mapper remains unchanged.
- Added stable-ID and unique-electrical-port morphology tests.
- Added a dedicated GitHub Actions workflow.
- Merged PR #3 via squash commit `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`.

## Experimental configuration

Three human morphology datasets × two NEURON mesh caps (0.125/0.0625 µm) = six configurations. Nine unique retained ports: soma and basal/apical q25/q50/q75/q90. Three source locations: soma, basal-q75, apical-q75. Four reduced models: four-shift order 56 control and six-shift orders 28/56/84. Ten frequencies through 10 kHz. Six transients with 2/10 ms pulses, 10 pA, start 2 ms, total 20 ms, dt 0.1 ms. All transient outputs recorded at all nine ports.

## Commands actually executed and evidence

GitHub Actions performed the environment installs and runs. The dedicated nine-port run [44976224651](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224651) completed six matrix jobs; each job completed full pytest, morphology record check, numerical audit, and artifact upload. A sampled job log (job 137066657325) recorded Python 3.12.16, NEURON 9.0.2, 118 tests passed in 5.36 s, nine boundary ports and 280 order/transient rows. All six matrix jobs ended success.

Core CI [44976224745](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44976224745) completed 4/4 jobs across Python 3.12 and 3.13. Seven-port baseline workflow [44966510373](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44966510373) completed 6/6 jobs. All 14 Actions workflows associated with the final PR code SHA completed successfully before merge.

## Results

Each nine-port morphology/mesh configuration yielded 280 rows; 1,680 total. The exact aggregate metrics and artifact links are in `amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md`. Key result: 144 matched apical-q90 comparisons against the seven-port raw sweep, with 36 pairs per model. All 36/36 pairs worsened for every model. Median error ratios (nine port / seven port): four-shift order56 11.515×; six-shift order28 2.118×; six-shift order56 127.706×; six-shift order84 7.814×. Maximum ratios: 22.350×, 3.394×, 613.199× and 28.749× respectively.

The expanded basis therefore fails the primary non-degradation criterion. The best nine-port model is six-shift order84, but it remains worse on apical-q90 than its paired seven-port reference. The result does not identify a biological cause; it is a model reduction/port basis result within a passive RC protocol.

## Decision and limits

- Keep seven-port as the reference port set for the next passive PRIMA study.
- Keep full Hines canonical.
- Do not promote nine ports as an accuracy improvement.
- Reject order28 for the tested expanded port/frequency/transient domain.
- Treat order84 as the best of the nine-port variants tested, not a new production default.
- Do not extrapolate to active channels, nonlinear synapses, plasticity, calcium, gene regulation, metabolism, cognition or complete neuron biology.
- NMO_290988 is partial dendrite-only morphology without an axon, not a healthy-control specimen.

## Next concrete experiment

Run orders 112 and 168 and a block-Krylov/source-probe-weighted basis against the existing seven-port and nine-port controls. Preserve all source locations, pulse protocols, frequency points and six mesh configurations. Evaluate actual basis rank, positive-definiteness, Hines and native NEURON errors, and matched per-port transient errors. Require q90 improvement without regression on the other common outputs.
