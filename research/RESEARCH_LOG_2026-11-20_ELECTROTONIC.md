# Research log — 2026-11-20 — electrotonic SWC refinement

## Question

Improve the AMSN SWC-to-cable discretizer so that mesh resolution is controlled by both physical length and local electrotonic distance, especially along linearly tapered dendritic edges.

## Source review

- Checked the actual GitHub `main` tree and current HEAD before modifying anything. The repo already contained `amsn-core/`, a source archive, 21-test package and CI workflow; older initial handoff sections saying the source modules were missing are historical and superseded by the newer core handoff.
- Read current `morphology.py`, `cable.py`, existing tests, package metadata, README and workflow before adding the extension.
- NEURON 9.0.1 documentation shows a d_lambda example using 100 Hz and 0.1 and bounds section segment length relative to the AC length constant. Its 3-D path approximates varying diameter from morphology samples.
- Arbor documentation describes composable CV discretization policies including maximum physical extent.

## Implementation added

- `amsn-core/src/amsn/discretization.py`
  - SI-aware high-frequency AC length constant;
  - analytic `dx/lambda` integral for linearly tapered SWC edges;
  - physical and electrotonic cut-set union;
  - exact inverse integrated-coordinate placement for electrotonic cuts;
  - non-mutating SWC refinement preserving original node IDs and branching;
  - convenience conversion to the existing passive cable tree.
- `amsn-core/tests/test_discretization.py`: seven tests.
- `amsn-core/examples/electrotonic_refinement.py`: synthetic morphology demonstration.
- `amsn-core/research/ELECTROTONIC_DISCRETIZATION_2026-11-20.md`: derivation, source mapping, validation limits and next experiment.
- Existing package README and CI workflow updated to expose/run the new example.
- A new handoff and repository index links added.

## Local test evidence

Environment: Python 3.13.5, NumPy 2.3.5, pytest 9.0.2, Linux x86_64.

Command: `PYTHONPATH=src python -m pytest -q`  
Result: **7 passed in 0.08 s**.  
Command: `python -m compileall -q src tests`  
Result: completed without syntax errors.

Integrity note: the local harness included a small morphology-compatible test double because local shell DNS could not resolve github.com and the whole repository could not be cloned. Therefore the local run validates the new equations, refinement logic, limit bounds and interface shape, but not full integration with the repository's existing cable solver. The GitHub Actions run triggered by this commit is the authoritative full-suite integration check and must be read before claiming it passed.

## Preserved geometry / numerical properties

- For the constant-diameter case, integrated electrotonic length is identical to physical length divided by the AC length constant.
- For the tapered case, analytic integration was checked against 100,000 midpoint samples.
- In the tested branched SWC, inserted points preserved original IDs, total path length, approximate frustum membrane area and branch count within test tolerances.
- Physical and electrotonic cuts were unioned, so each resulting interval was checked against both maximums.

## Limitations

- This is a passive high-frequency cable discretization heuristic, not proof of spatial convergence for active human dendrites.
- It uses generic passive `Ri`/`Cm` defaults, not cell-specific human measurements.
- The test morphology is synthetic. No real morphology was committed.
- No NEURON/Arbor comparison or Eyal 2018 reproduction was run.
- Full repository integration awaits GitHub Actions result.

## Next concrete experiment

Use a morphology with redistribution-cleared license and metadata. Run successive `d_lambda`/physical extent levels; compare input resistance, time constant, distal transfer ratio and runtime. Report convergence tables and only then move to active conductances or subtype-specific human calibration.
