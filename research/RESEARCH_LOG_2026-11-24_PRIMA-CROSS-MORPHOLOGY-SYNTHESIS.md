# Research log — PRIMA cross-morphology synthesis

**Date:** 24 November 2026  
**Topic:** matched 7-port / 9-port PRIMA holdouts across four morphologies  
**Branch:** research/prima-cross-morphology-synthesis-2026-11-24

## Question and hypothesis

Question: does adding basal-q25 and apical-q25 output probes impose a stable accuracy penalty on the seven shared ports, or is the penalty morphology- and basis-order-dependent?

Working hypothesis: the penalty depends on morphology and reduction order; relative error ratios must be interpreted alongside absolute NRMSE because the seven-port baseline can already be extremely accurate.

## Sources examined

Repository data on the PRIMA holdout chain:

- NMO_162186: report JSON, matched-summary CSV, q25-summary CSV, shared-Hines CSV; successful workflow 45184621520.
- NMO_03524: corresponding four archived outputs; successful workflow 45198027785.
- NMO_163775: corresponding four archived outputs; successful workflow 45311916600.
- NMO_107159: corresponding four archived outputs; successful workflow 45314100588.
- Repository instructions: AGENTS.md, HANDOFF.md, AMSN_RESEARCH_DOSSIER.md and the 24 November Tamas checkpoint/log.

External research lead: Esparza Rivera & Gomez, “Hierarchical Matrix Compression for Fast Bidomain Simulation of Multicellular Neuron Models”, bioRxiv v1 posted 23 November 2026, DOI 10.64898/2026.11.20.768225. Its bidomain/Cable-BEM scope differs from passive cable PRIMA and is recorded only as a separate future investigation lead.

## Work performed

1. Inspected repository branches and PR sequencing. PR #17 is stacked on #16, which is stacked on #15; the synthesis branch is based on the current PR #17 head and must be reviewed as a stacked follow-up.
2. Compared all four machine-readable report JSONs and their CSV summaries.
3. Verified that each morphology has 36 model rows, 324 AC rows, 1,728 transient rows, 756 shared-output pairs, 216 q25 observations and 378 Hines checks.
4. Inspected the raw Hines CSV schema and verified the files contain the expected zero-difference trace columns.
5. Added a standard-library analysis script, focused tests and a GitHub Actions workflow. The workflow will generate the aggregate report/CSV only after validation.

## Observed numerical pattern

- Order 112: NMO_03524 is near parity (median 9/7 ratio approximately 1.0000); NMO_162186, NMO_163775 and NMO_107159 show larger relative penalties.
- Order 168: NMO_162186, NMO_03524 and NMO_107159 are near parity; NMO_163775 remains approximately 14.501x by median relative ratio.
- The maximum nine-port shared-output NRMSE for NMO_163775 at order 168 is approximately 6.07e-7 percent. The relative ratio is therefore not a substitute for absolute error.
- The two 0.125 µm holdouts and two 0.5 µm holdouts are not pooled for absolute error or runtime comparisons.
- Full-Hines consistency is exact in the archived 378 checks per morphology.

## Files created

- amsn-core/research/synthesize_prima_cross_morphology.py
- amsn-core/tests/test_prima_cross_morphology_synthesis.py
- .github/workflows/amsn-prima-cross-morphology-synthesis.yml
- HANDOFF_2026-11-24_PRIMA-CROSS-MORPHOLOGY-SYNTHESIS.md

Generated research report and CSV are produced by the workflow:
- amsn-core/research/PRIMA_CROSS_MORPHOLOGY_SYNTHESIS_2026-11-24.md
- amsn-core/results/prima_cross_morphology_synthesis_2026-11-24.csv

## Validation state

The synthesis workflow has not yet been observed completing in this log revision. No local Python tests or new NEURON simulations are claimed. The expected workflow performs focused standard-library tests, generates both aggregate outputs, verifies reproducibility, and commits them to this branch. Update this log with the actual run ID, conclusions and commit SHA after observing the workflow result.

## Limitations

Four individual morphology holdouts do not represent a human or mouse population. The experiments validate passive linear-RC numerical reductions against full Hines only. The Peng data record has no measured diameter metadata. Mesh caps differ (0.125 versus 0.5 µm). No active-channel, nonlinear-synapse, plasticity, calcium, metabolic or biological inference is supported.

## Next concrete experiment

Run a mesh-harmonization factorial on at least one holdout from each mesh stratum, using both 0.125 and 0.5 µm caps with identical ports, orders, shifts and passive scenarios. In parallel, localize the NMO_163775 order-168 residual by port/source/pulse/scenario before considering any order recommendation.


## Verified synthesis workflow closeout

GitHub Actions run [45317943578](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45317943578) completed successfully on CPython 3.12.16.

Actual workflow output:
- 7/7 focused `unittest` checks passed.
- `python amsn-core/research/synthesize_prima_cross_morphology.py --write` generated the Markdown report and CSV.
- `python amsn-core/research/synthesize_prima_cross_morphology.py --check` returned: `OK: 2 generated files match all four validated source datasets`.
- The output commit is `fde2876cc6b2c808c306e93629de2a18510178ca`.
- Markdown report blob SHA: `916dfc523faa5e356dfc5626a6278634eb60b789`.
- CSV blob SHA: `0e605ed5849f59f996007e68f68f06d60727189`.

Aggregated verified coverage across the four archived holdouts: 144 model configurations, 1,296 frequency matrices, 6,912 transient rows, 3,024 paired shared-output comparisons, 864 q25-only observations and 1,512 shared-Hines checks. Every recorded Hines check is exactly zero absolute trace difference and zero relative L2 difference.

This closeout supersedes the earlier note in this log stating that the synthesis workflow had not yet completed. No additional NEURON replay was run during this synthesis step. The synthesis branch remains separate from `main` and stacked on the NMO_107159/PR #17 branch.
