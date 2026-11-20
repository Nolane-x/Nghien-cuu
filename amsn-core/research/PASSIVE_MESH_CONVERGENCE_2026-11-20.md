# AMSN passive mesh-sensitivity experiment — 2026-11-20

**Status:** full package CI passed on Python 3.12 and 3.13.  
**Code:** `amsn-core/examples/passive_mesh_convergence.py`  
**Test:** `amsn-core/tests/test_discretization.py`  
**Run:** GitHub Actions workflow run [44735191202](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44735191202)  
**Code commit:** `0c4871df50e83e95f8446cbfe6058023312057da`

## Question

How sensitive are passive input resistance and a distal-to-soma steady-state voltage ratio to progressively finer electrotonic discretization in one branching tapered cable morphology?

## Scope and hypothesis

This is a numerical-method experiment using an explicitly synthetic 7-point morphology. It is **not** a biological reconstruction, a human-neuron fit, or a reproduction of Eyal et al. (2018).

Hypothesis: decreasing the maximum electrotonic extent should increase the number of control volumes and the passive observables should approach a stable value.

The hypothesis is supported only for the tested synthetic geometry, parameter set and observables. No claim is made that the resulting numerical values are biologically realistic.

## Morphology and model configuration

Input SWC is embedded in `passive_mesh_convergence.py` and labelled synthetic. It contains a soma/root, one apical-like path, a bifurcation and a basal-like path. No external biological data are used.

| Parameter | Value | Status |
|---|---:|---|
| Reference frequency | 100 Hz | Numerical discretization setting |
| Maximum electrotonic length | 0.2, 0.1, 0.05, 0.025 | Sweep |
| Axial resistivity | 0.7 ohm m | Generic default, not human-fitted |
| Specific membrane capacitance | 0.01 F/m² | Generic default, not human-fitted |
| Specific membrane resistance | 1.0 ohm m² | Existing core generic default |
| Leak reversal | -65 mV | Existing core generic default |
| Injected current | 100 pA at root | Constant current |
| Duration / time step | 0.15 s / 0.1 ms | 1,500 backward-Euler steps |
| Initial voltage | -65 mV | Uniform |
| Random seed | Not applicable | Deterministic passive model |

The passive membrane time constant from these generic values is 0.01 s; the 0.15 s observation window is 15 time constants. Reported resistance is estimated from the root voltage change at the final time divided by the injected current. The transfer ratio is the distal terminal voltage change divided by the root voltage change.

## Results

### Observable values

The two GitHub Actions jobs produced identical compartment counts and electrical values at the printed precision.

| Maximum electrotonic length | Compartments | Input resistance (MΩ) | Distal/root ratio |
|---:|---:|---:|---:|
| 0.2 | 13 | 77.6958 | 0.90595764 |
| 0.1 | 22 | 77.6752 | 0.90658815 |
| 0.05 | 41 | 77.6435 | 0.90725289 |
| 0.025 | 80 | 77.6361 | 0.90740885 |

Relative to the finest tested mesh (`d_lambda=0.025`):
- The `d_lambda=0.05` input-resistance difference is approximately **0.00953%**.
- The `d_lambda=0.05` distal/root ratio differs by approximately **0.0156 percentage points**.
- The coarsest (`0.2`) to finest (`0.025`) input-resistance difference is approximately **0.0769%**.
- The coarsest to finest distal/root ratio difference is approximately **0.1451 percentage points**.

Both observables change monotonically across these four meshes in this particular run. The 0.05 and 0.025 meshes are close for these two observables, but this is **not** proof that every voltage response, branch-point event, active spike or calcium signal has converged.

### Runtime (single CI run per interpreter; informational only)

| d_lambda | Python 3.12.16 (s) | Python 3.13.18 (s) |
|---:|---:|---:|
| 0.2 | 0.070328 | 0.078431 |
| 0.1 | 0.080637 | 0.100715 |
| 0.05 | 0.126962 | 0.163896 |
| 0.025 | 0.218906 | 0.264513 |

These are single wall-clock measurements on hosted CI runners, not a benchmark. They should not be compared as precise performance claims across Python versions or environments.

### Separate refinement example

The small `synthetic_branching.swc` example was also changed to impose a 5 µm physical maximum. CI output:
- Original points: 7
- Refined points: 18
- Cable compartments: 18
- Total path length before/after: 67.941125 µm / 67.941125 µm
- Estimated membrane area before/after: 1213.926292 µm² / 1213.926292 µm²

This verifies the demonstration now visibly subdivides its input and preserves these geometry summaries for that synthetic example.

## Reproducibility and automated validation

GitHub Actions run: [44735191202](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44735191202)

- Python 3.12.16: **29 passed in 1.10 s**
- Python 3.13.18: **29 passed in 1.35 s**
- Both jobs: editable package installation succeeded; pytest succeeded; `compileall` succeeded; all four examples succeeded, including the mesh sweep.
- CI dependency versions in the captured logs: NumPy 2.5.5 and pytest 9.2.0.
- Commands in CI:
  - `python -m pytest -q`
  - `python -m compileall -q src tests examples`
  - `python examples/inspect_swc.py`
  - `python examples/passive_tree.py`
  - `python examples/scaling_smoke.py`
  - `python examples/electrotonic_refinement.py`
  - `python examples/passive_mesh_convergence.py`

A raw CSV copy of the values from the two CI runners is stored alongside this report at `amsn-core/results/passive_mesh_convergence_2026-11-20.csv`.

## Interpretation

For this passive synthetic cable:
- A tighter electrotonic bound increases the compartment count as expected.
- Input resistance and distal/root ratio become progressively less sensitive to refinement.
- The changes from 0.05 to 0.025 are small for the selected observables.
- The additional mesh points increase the simulation wall time in these single CI runs, as expected, but no formal complexity/performance benchmark was conducted.

The mesher uses an analytic integral of `dx/lambda_f` for an SWC edge whose diameter varies linearly between endpoints. NEURON's documented `d_lambda` example uses 100 Hz and 0.1 as reasonable defaults and accounts for sampled 3-D diameter points; AMSN's implementation is a simpler straight-edge / linear-taper approximation. Arbor documents maximum physical-extent discretization policies and policy composition, which provides a useful complementary model for the union of physical and electrotonic constraints.

## Limitations

- The input is synthetic, not an experimentally reconstructed human neuron.
- Passive parameters are generic defaults, not calibrated to a human L2/3 subtype, donor, depth or temperature.
- The soma is approximated by a spherical-area root control volume.
- The cable model is one-dimensional and passive; no voltage-dependent dendritic channels, synapses, spikes, calcium, glia, metabolism or gene expression are included.
- The high-frequency AC length criterion is a meshing heuristic. It is not direct validation of time-domain EPSPs, active dendritic spikes, calcium transients or plasticity.
- No NEURON, Arbor or ModelDB cross-simulator reference was executed.
- Only one synthetic branching geometry and one current-injection protocol were used.
- Runtime numbers are one-run CI timing observations only.

## Next experiment

Use a morphology with redistribution permission and sufficient metadata. Repeat mesh refinement on several real, license-cleared reconstructions and vary physical extent as well as `d_lambda`. Compare:
1. DC input resistance;
2. membrane time constant;
3. transfer resistance from soma to multiple branch locations;
4. passive EPSP peak and attenuation under identical point-current inputs;
5. branch-point response and solver runtime.

Then run the same morphology and protocol in a reference simulator (NEURON or Arbor) before adding active channels. Do not tune human parameters to make this numerical mesh test look like biological validation.

## Sources

- NEURON 9.0.1 documentation, “Using the d_lambda Rule”: https://www.neuronsimulator.org/en/9.0.1/guide/using_the_d_lambda_rule.html
- Arbor documentation, “Discretization”: https://docs.arbor-sim.org/en/latest/concepts/discretization.html
- Hines, M.L. & Carnevale, N.T. (2001), “NEURON: a tool for neuroscientists,” *The Neuroscientist* 7, 123–135.
