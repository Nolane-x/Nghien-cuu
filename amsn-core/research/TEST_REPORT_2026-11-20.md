# AMSN Neuron Core — test report 2026-11-20

## Environment
- Runtime: Python 3.13.5
- NumPy: 2.3.5
- pytest: 9.0.2
- Platform: Linux x86_64, glibc 2.41
- NEURON: not installed (no `nrniv` or `nrnivmodl` detected)

## Command

```bash
cd amsn-core
PYTHONPATH=src pytest -q
PYTHONPATH=src python examples/passive_tree.py
PYTHONPATH=src python examples/inspect_swc.py
PYTHONPATH=src python examples/scaling_smoke.py
```

## Results
- **21 tests passed in 1.06s**.
- Hines solution on a branched tree matched a dense NumPy matrix solve to `rtol=1e-12`, `atol=1e-14`.
- One-compartment passive membrane decay matched its exact backward-Euler recurrence to `rel=1e-10`.
- Time-step refinement test passed for a branched passive response.
- Independent sealed finite-cylinder cable input resistance matched the analytic cable solution. For a 1 mm cable of 1 µm radius, reducing segment spacing from 20 µm to 10 µm reduced relative error from approximately `5.95e-5` to `1.49e-5` (about a fourfold reduction). This is one controlled numerical test, not a claim of universal convergence order.
- SWC parser tests passed for geometry summary, branch counts, type-length aggregation, invalid morphology rejection and a 5,000-node chain (stack-safe traversal).
- SWC-to-cable conversion preserved the full estimated root-plus-frustum membrane area exactly to `rel=1e-12`; the tested taper edge used the analytic resistance `R = rho * L / (pi * r0 * r1)`. A max-segment-length example generated 12 compartments from the 7-point synthetic tree while preserving all 11 links.
- Canonical HH 1952 single-compartment test generated an action potential. Under the exact test stimulus (1 nA from 1–2 ms, dt=0.01 ms, 30 ms duration), peak voltage was +103.861 mV relative to the -65 mV rest reference, equivalent to about +38.861 mV absolute (peak time 3.54 ms); final voltage at 30 ms was -0.088 mV relative to rest, equivalent to about -65.088 mV absolute.
- HH timestep refinement (10 µs vs 2.5 µs): peak changed from 103.861 to 104.021 mV relative to rest (0.160 mV difference); peak time changed from 3.540 to 3.518 ms (0.0225 ms difference). This is a numerical convergence check for the canonical HH smoke test, not biological validation.
- Hines scaling smoke (one passive step, this runtime): 1,000 compartments ~0.0018 s; 5,000 ~0.0082 s; 10,000 ~0.0184 s. Build times in this run were ~0.0033/~0.0159/~0.0338 s. Single-run timings are environment-specific observations, not a formal performance benchmark.
- `examples/passive_tree.py` output: 4 compartments; peak -59.819 mV; terminal voltages approximately -63.366 mV per compartment.
- `examples/inspect_swc.py`: 7 synthetic SWC points, 2 branch points; converter created 12 electrical nodes/11 links and preserved estimated membrane area at 1,213.926 µm².

## Interpretation and limits

These tests validate internal numerical consistency for the implemented simplified cable model and a canonical squid HH smoke test. They do **not** validate human cortical physiology, reproduce Eyal et al. (2018), or establish biological parameter accuracy. The HH model is the 1952 squid-axon model and is not used as a human-neuron prior. The synthetic SWC example is pedagogical only.

## External baseline blocker

The Eyal et al. ModelDB archive was not downloaded (ModelDB mirror exposes only a README page in the GitHub mirror; its landing page links an approximately 133 MB external archive). NEURON is absent from this execution image and installation was blocked by unavailable DNS/network. No external NEURON results are recorded.
