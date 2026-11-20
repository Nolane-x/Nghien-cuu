# Human morphology integration — CI verification checkpoint

**Date:** 2026-11-20 (UTC+7)  
**Code commit:** `869e4faa80c6cf4145cd0a176c1000aad5ed0964`  
**Test correction commit:** `6b99618f8b6d76d6bb0f8c943500db8c6804d2d9`  
**GitHub Actions:** [run 44737462769 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44737462769)

## Actual CI results

The final workflow completed successfully on both Python matrix versions:

| Environment | Pytest | Result |
|---|---:|---|
| Python 3.12.16 | 33 passed in 0.98 s | success |
| Python 3.13.18 | 33 passed in 1.54 s | success |

Both jobs also completed:
- editable package installation;
- `python -m compileall -q src tests examples`;
- all configured examples, including `human_morphology_inspect.py`.

The human morphology example output from each runner confirmed:
- NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015`;
- 8,903 SWC points;
- neurite length 12,610.981 µm;
- 58 bifurcations / 8 stems.

## Failure found and corrected

The first run of the import commit had one legacy test failure: `test_swc_file_example_is_explicitly_synthetic_and_parseable` expected the soma/root to count as a branch point. The new scientific definition counts neurite bifurcations and excludes soma nodes, so the expected value was corrected from 2 to 1. The import commit had 32 passing tests and this one stale assertion; the follow-up commit fixed it. The final run is 33/33 on both versions.

No implementation rollback was needed. This correction aligns the existing synthetic fixture test with the new morphology convention and the source record's API bifurcation count.

## Validated scope

The passing tests verify:
- structural parse of the exact 8,903-row human SWC in CI;
- expected node-type counts;
- soma multi-point area is not double-counted;
- invalid multi-point-soma spherical override is rejected;
- the explicit distal-cylinder comparator reproduces this record's published morphometry values to the stated tolerances;
- the real morphology summary has 58 non-soma bifurcations.

This remains a morphology + passive-cable software foundation. Passing CI does not establish human electrophysiological calibration or reproduce Eyal et al. (2018). The cell still has no axon and moderate dendritic completeness, and metadata records mesiotemporal sclerosis.

## Next checkpoint

Run a passive steady-state transfer experiment at multiple dendritic injection/probe sites on this real morphology, then compare the same discretization and geometry against NEURON or Arbor. Record exact node selection, mesh criterion, conductance assumptions and matrix solver output.
