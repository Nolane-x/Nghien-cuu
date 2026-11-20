# Research log — 2026-11-20 — AMSN Neuron Core v0.1.0 and SWC cable conversion

## Objective
Rebuild a real, testable numerical foundation after the previous AMSN Alpha source directories were found empty, improve morphology-to-cable mapping, and preserve recent human L2–3 evidence.

## Repository baseline and preservation
- Repository: `Nolane-x/Nghien-cuu`, default branch `main`.
- Before this checkpoint the known main HEAD was `d01b3b4c05aa58643b5a45d092722f32fe327a3b`.
- Existing research documents were fetched and read before creating the new implementation files.
- Previous files are preserved; the code is added under a new `amsn-core/` directory and new dated research/handoff files.

## Literature/source update
1. Planert et al., *Nature Neuroscience* 29, 455–466 (2026), published online 10 Dec 2025, DOI `10.1038/s41593-025-02134-7`. The study recorded 1,479 human middle-temporal-gyrus L2–3 pyramidal neurons from 23 epilepsy surgery patients; 1,214 met QC, 901 cells were used for cellular-property analysis, and 1,419 monosynaptic connections were detected among 9,834 potential pairs. Four e-types were identified: LowRin, DoubSpk, FastAP and SlowAP. Cellular features (including input resistance, firing/F–I properties and sag) were depth-dependent, whereas the dataset did not show significant depth correlations for EPSP amplitude or PPR. Median EPSP amplitude was 0.46 mV and median PPR 0.93 at 20 Hz. The cohort consists of surgical epilepsy tissue, so do not equate it with a healthy-population reference. Processed data/code are linked from Figshare; original participant data are not openly shared due to data-protection restrictions.
2. Sharma et al. (2026 bioRxiv preprint): paired Patch-Seq/transcriptomic and electrophysiological features from 495 human neurons; cell-type representations were strong predictors, hybrid cell-type plus scGPT outputs performed best. Preprint, not peer-reviewed evidence.
3. Owen et al. (2026 bioRxiv preprint): developmental changes in human L2–3 spike timing and a candidate BK-channel contribution. Keep preprint status explicit.
4. BRAINCELL is a peer-reviewed 2026 *Nature Communications* platform paper; its platform models stochastic nanoscale morphology and dynamic extracellular signalling. Repository source inspected at commit `bf7d9255aac988b4b52acb177c82063b56894773`; repository license metadata is BSD-3-Clause, but individual third-party components have separate restrictions.
5. NEURON official changelog: 8.2.7 supports Python 3.13 and NumPy >=2; 9.0.2 was released 10 Aug 2026. Legacy MOD files must be tested before assuming either release works.

## Implementation created from scratch
Repository path: `amsn-core/`.
- SI unit conversion helpers.
- Strict SWC parser; connectivity validation is iterative and handles a 5,000-point chain without recursion-limit errors.
- Morphology geometry summary.
- `SWCMorphology.to_cable_tree(...)`: vertex-centred 1-D cable conversion; optional max physical segment length; area partition across tapered frusta; exact axial resistance integral for linearly tapered radii; explicit root soma-area estimate or caller override.
- Passive branched cable solver with backward Euler and Hines elimination/back-substitution.
- Classic HH 1952 kinetics as numerical smoke test only (squid axon at 6.3 C, not human cortex).
- Unit/numerical tests, examples, package metadata and GitHub Actions workflow.

## Validation evidence
Environment: Python 3.13.5, NumPy 2.3.5, pytest 9.0.2, Linux x86_64.

Final command results in the local workspace:
- `PYTHONPATH=src pytest -q` — **21 passed in 1.06s**.
- `python -m compileall -q src tests examples` — completed with no syntax errors.
- Passive tree example — 4 compartments, peak -59.8187 mV, terminal voltages ~-63.366 mV.
- Synthetic SWC example — 7 input points, 2 branch points; 10 µm max segment length produced 12 cable nodes/11 links and preserved 1,213.926 µm² estimated total membrane area.
- Hines dense-matrix test passed at `rtol=1e-12`, `atol=1e-14`.
- A 5,000-node SWC chain test passed.
- Tapered edge axial resistance matched `R = rho_i * L/(pi*r0*r1)` and area was conserved.
- Analytic sealed-cylinder input resistance: a 1 mm, 1 µm-radius cable gave relative errors ~5.95e-5 at 20 µm and ~1.49e-5 at 10 µm spacing; halving spacing reduced error by about fourfold in this test.
- Hines scaling smoke (one run, not a formal benchmark): n=1,000 build ~0.0033 s, step ~0.0018 s; n=5,000 build ~0.0159 s, step ~0.0082 s; n=10,000 build ~0.0338 s, step ~0.0184 s.
- Classic HH 1 nA pulse (1–2 ms), dt=10 µs, duration=30 ms: peak +103.861 mV relative to rest (-65 mV), equivalent to about +38.861 mV absolute; this is a canonical squid-HH smoke test.

## Limits and blockers
- No NEURON binary/module is installed in this execution environment; package installation previously failed because DNS/network was unavailable.
- The original Eyal et al. 2018 ModelDB archive was not downloaded, extracted or hashed. This checkpoint does not reproduce the human L2–3 model.
- The SWC-to-cable method is a vertex-centred 1-D approximation, not a 3-D soma or branch-junction mesh; no real licensed morphology was added.
- Generic passive defaults are not fitted human L2–3 parameters.
- No active human channel distributions, synapses, calcium, plasticity, transcription/translation, ATP metabolism, astrocytes or extracellular signalling have been implemented.
- CI workflow was added but has not yet been run by GitHub Actions in this checkpoint; only local tests were run.

## Next concrete work
1. Validate the converter with real, redistribution-cleared human morphologies; audit soma conventions and area allocation.
2. Add electrotonic-length refinement and spatial convergence tests for input resistance, attenuation, time constant and branch responses.
3. Obtain and hash ModelDB 238347; run its original mechanisms under NEURON 8.2.x and separately assess 9.0.x.
4. Build subtype-aware parameter records from processed Planert data, preserve participant grouping, field definitions and uncertainty; do not infer inaccessible participant-level raw data.
5. Only after electrical baseline reproduction, add active dendritic channels and synaptic kinetics; later add causal calcium-to-plasticity and metabolic coupling.
