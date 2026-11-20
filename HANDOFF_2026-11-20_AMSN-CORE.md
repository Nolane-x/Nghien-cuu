# Handoff — AMSN Neuron Core v0.1.0

**Checkpoint:** 2026-11-20 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Implementation directory:** `amsn-core/`  
**Research direction:** AMSN — Adaptive Multi-Scale Neuron

## Read this first

A future session should read, in order:
1. `AGENTS.md` — preservation and scientific-integrity rules.
2. `HANDOFF.md` — original broad research context and recovery history.
3. This file — latest implementation state and next concrete tasks.
4. `amsn-core/README.md` and `amsn-core/research/TEST_REPORT_2026-11-20.md`.
5. `research/HUMAN_L23_EVIDENCE_UPDATE_2026-11-20.md`.
6. Latest dated research log.

Check `main` HEAD and the Git tree before editing. Preserve previous checkpoints; prefer new dated files.

## 1. What was built in this checkpoint

A clean, newly authored Python package was created because the previous AMSN Alpha executable modules were not present in the inspected filesystem. This is not recovered old code.

Path `amsn-core/` contains:
- `src/amsn/units.py`: electrophysiology unit conversion helpers; numerical core uses SI units.
- `src/amsn/morphology.py`: strict SWC parser; rejects duplicate IDs, invalid radii, missing parents, self-parent, disconnected components and malformed lines; uses iterative stack validation safe for long morphologies. Includes `to_cable_tree(...)`, a vertex-centred 1-D conversion with optional maximum edge length, tapered-frustum membrane-area allocation and exact linearly tapered axial resistance.
- `src/amsn/cable.py`: passive branched cable tree, backward-Euler voltage step and O(N) Hines elimination/back-substitution. Supports per-control-volume membrane-area and per-edge axial-geometry overrides for SWC-derived cables.
- `src/amsn/hh.py`: classic Hodgkin–Huxley 1952 Na/K/leak gates (Rush–Larsen state update plus implicit voltage step). This is a squid giant-axon numerical benchmark, not a human cortical cell model.
- `tests/`: unit/numerical tests including Hines vs dense matrix, analytic backward-Euler decay, timestep refinement, malformed SWC and HH action-potential generation.
- `examples/`: passive tree demo and an explicitly synthetic SWC file.
- `pyproject.toml`: Python >=3.10, NumPy >=1.24, pytest optional.
- Root `.github/workflows/amsn-core.yml`: CI matrix for Python 3.11/3.13; it installs the package, runs tests and the SWC/passive examples.

## 2. Verified local execution

Environment:
- Python 3.13.5
- NumPy 2.3.5
- pytest 9.0.2
- Linux x86_64
- NEURON absent; neither `nrniv` nor `nrnivmodl` detected.

Commands actually run:
```bash
python -m pip install -e ".[test]" --no-build-isolation
PYTHONPATH=src pytest -q
PYTHONPATH=src python examples/passive_tree.py
PYTHONPATH=src python examples/inspect_swc.py
PYTHONPATH=src python examples/scaling_smoke.py
python -m compileall -q src tests examples
```

Results:
- `21 passed in 1.06 seconds` (latest verified run).
- Hines result matches dense NumPy linear solve at `rtol=1e-12`, `atol=1e-14` for the tested branched tree.
- Passive one-compartment decay matches the exact backward-Euler recurrence at `rel=1e-10`.
- Passive timestep refinement, SWC validation, 5,000-node stack safety, tapered-edge resistance and HH smoke tests pass.
- A sealed finite cylindrical cable matched its analytic input resistance: 20 µm spacing relative error ~5.95e-5; 10 µm spacing ~1.49e-5 (about 4× lower).
- HH single-compartment, 1 nA pulse from 1–2 ms, dt=0.01 ms, duration=30 ms: peak `+103.861 mV` relative to resting reference (-65 mV), i.e. about `+38.861 mV` absolute; peak time 3.54 ms; at 30 ms voltage is `-0.088 mV` relative to rest.
- Passive example: 4 compartments, peak -59.819 mV and terminal voltages ~-63.366 mV.
- Synthetic SWC example: 7 points, 2 branches; conversion at 10 µm maximum edge length produced 12 nodes/11 links and preserved 1,213.926 µm² estimated area.
- Hines scaling smoke (single run, not a formal benchmark): 1,000 compartments ~0.0033 s build / 0.0018 s step; 5,000 ~0.0159 s / 0.0082 s; 10,000 ~0.0338 s / 0.0184 s. Timings are runtime-specific.

These results validate numerical consistency of the written code only. They are not validation against a human neuron, and the HH benchmark must not be mistaken for human L2/3 physiology.

## 3. Biological evidence update that changes the plan

Planert et al., Nature Neuroscience 29, 455–466 (2026), DOI `10.1038/s41593-025-02134-7`, studied human middle-temporal-gyrus L2–3 tissue from 23 epilepsy surgery patients. They recorded 1,479 pyramidal neurons; 901 cells were used for the main cellular-property analysis; 1,419 monosynaptic connections were identified. Four electrophysiological subtypes were identified: LowRin, DoubSpk, FastAP and SlowAP. Intrinsic cellular features varied with cortical depth; synaptic amplitude/PPR in that dataset did not show significant depth relationships. LowRin and SlowAP subtypes differed in their synaptic embedding and dynamics.

Do not implement one average human L2/3 parameter set. The next population-data layer should model subtype, depth, donor/sample grouping, experimental condition and uncertainty separately. Note the epilepsy-surgery sampling limitation. Original participant data are not open; processed data and analysis code are linked via Figshare.

Other evidence added in `research/HUMAN_L23_EVIDENCE_UPDATE_2026-11-20.md`:
- Sharma et al. 2026 preprint (495 paired human Patch-Seq neurons): cluster cell-type labels generally outperformed several gene-only or scGPT representations for predicting measured electrophysiological features; hybrid combinations did best. Preprint, not yet treat as settled.
- Owen et al. 2026 preprint: human L2/3 postnatal spike dynamics and BK-type calcium-activated K channels as a candidate mechanism; preprint status must remain explicit.
- BRAINCELL is now a 2026 Nature Communications platform paper; source inspected at commit `bf7d9255aac988b4b52acb177c82063b56894773`; platform source BSD-3-Clause but third-party components can have separate restrictions.

## 4. Eyal 2018 baseline reproduction — still blocked

The target reference remains Eyal et al. (2018), *Human cortical pyramidal neurons: From spines to spikes via models*, ModelDB accession 238347. ModelDB's page identifies six human L2/L3 pyramidal models and says the downloadable archive is approximately 133 MB. The GitHub mirror contains the readme but not the archive payload.

In this runtime, attempted NEURON installation could not reach the package index because DNS/network access was unavailable; therefore do not claim that the Eyal model ran. The archive has not been downloaded or hashed.

Current toolchain note: NEURON 9.0.2 was released 10 Aug 2026. NEURON 8.2.7 explicitly supports Python 3.13 and NumPy >=2. Because older model MOD files may be sensitive to newer NMODL/C++ toolchains, first reproduce under a tested 8.2.x build, then test 9.0.2 separately. Do not assume compatibility without running the original MOD files.

## 5. Numerical design limits to keep visible

- The SWC-to-cable conversion is now implemented, but remains a vertex-centred 1-D approximation; it is not a 3-D morphology reconstruction.
- The converter approximates the root as a spherical-area control volume unless an explicit soma area is provided; frustum area and linear-taper axial resistance are exact within the 1-D edge geometry, but this is not a full mesh or exact soma reconstruction.
- Manually specified cable compartments still use uniform-cylinder geometry and center-to-center half-compartment axial resistance. SWC-derived nodes use explicit lumped membrane areas and per-edge tapered axial-resistance factors.
- No 3-D branch-junction geometry, soma mesh or spine-neck geometry exists yet.
- The passive cable uses generic defaults (Cm=1 µF/cm², Rm=10,000 ohm*cm², Ri=70 ohm*cm), not human-fitted values.
- HH mechanism is canonical squid HH at 6.3°C; no human channel distributions.
- No synapses, dendritic active conductances, calcium, plasticity, gene/protein, ATP, astrocyte or extracellular signaling yet.

## 6. Next implementation sequence

### P1 — verify the passive solver more broadly
- Add convergence tests against analytic cable solutions and electrotonic attenuation.
- Test larger branched trees and report runtime/scaling rather than claim O(N) without profiling.
- Add conservation/energy sanity checks and parameter validation.

### P2 — validate and refine the new geometry-to-compartment converter
- The first vertex-centred 1-D converter exists; test it on real, license-cleared SWC files.
- Decide soma handling based on source SWC conventions and measured soma geometry; root-sphere area is only a fallback.
- Add electrotonic-length-based refinement in addition to max physical segment length.
- Perform convergence studies for input resistance, attenuation, time constant and branch-point responses.
- Decide whether a 3-D junction/spine mesh must be delegated to NEURON/RxD, STEPS or BRAINCELL rather than approximated in this core.

### P3 — reproduce Eyal baseline
- Obtain and hash the official ModelDB 238347 archive.
- Test a compatible NEURON 8.2.x environment and compile the published MOD mechanisms unchanged first.
- Reproduce the published figures/protocols with the exact original model before refactoring.
- Save raw traces, config, package lock, NEURON version, compiler, OS, and full commands.

### P4 — human L2/3 subtype-aware parameters
- Access the processed Figshare data under its terms and identify exact measured field definitions.
- Construct descriptive distributions conditioned on e-type and depth; preserve donor grouping.
- Do not impute missing channels as observed values; store provenance and uncertainty.
- Use subtype-specific synaptic dynamics only where data supports them.

### P5 — additional biology
Only after P1–P4: active human dendritic channels, synapse release/receptors, Ca2+/CaM/CaMKII/phosphatase, LTP/LTD, BK channels/development, metabolism, astrocyte/extracellular coupling, then transcription/translation.

## 7. Research integrity

- Do not use the old Alpha README's “69 passing tests” as a result; its source/test directories were empty when inspected.
- Do not call the HH test human-neuron validation.
- Do not call the synthetic SWC a measured morphology.
- Do not claim Eyal reproduction until original files run and reference outputs are compared.
- Record all negative/failing tests and exact versions.
- Do not vendor BRAINCELL, ModelDB or third-party data until license and terms are checked.
- Preserve user data by adding dated checkpoints and committing at each meaningful milestone.
