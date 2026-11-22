# Research log — PRIMA order × input-location × pulse-width sweep

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Base commit:** c7b61733c4dc3aa744509218640d774e953ee20d  
**Work branch:** `research/prima-order-transient-matrix-2026-11-22`  
**Status:** implementation staged for PR validation; experimental results not yet available.

## Research question

Does the six-shift 10 kHz passive PRIMA basis remain useful across model orders and distinct input locations/waveform widths, or was the previous 10 kHz improvement specific to order 56 and one basal-q75, 10 ms current pulse?

## Hypothesis and falsification criteria

The six-shift basis (positive-real shifts 0, 100, 1,000, 3,000, 6,000 and 10,000 Hz) should improve upper-band frequency response against both full AMSN Hines and native NEURON across several model orders. The expected trade-off is that lower order may lose accuracy and that improvements in frequency response may not transfer to all transient input patterns.

Reject a broad "10 kHz basis is better" claim if any of these occur:
- direct NEURON Z/Y error becomes worse across the full tested band for a reduced-order configuration;
- Cholesky passivity, finite response, reciprocity or matrix-conditioning checks fail;
- transient errors become unacceptable at soma or apical-q75 stimulation or at either pulse width;
- one model order only appears better because state budget changed without being reported.

No default will be changed solely because one maximum error decreases.

## Experimental design

### Frequency-domain model matrix

Four models are compared using the same seven retained ports, morphology, NEURON mesh, passive parameters and ten frequencies:

1. Four-shift order-56 control: shifts (0, 100, 1,000, 3,000) Hz.
2. Six-shift order-28: shifts (0, 100, 1,000, 3,000, 6,000, 10,000) Hz.
3. Six-shift order-56: same six shifts.
4. Six-shift order-84: same six shifts.

Each model is compared against both full AMSN Hines and native NEURON for Z and Y. State count and requested/actual reduced order are recorded. Conductance and capacitance matrices must pass Cholesky positive-definiteness checks.

### Transient input matrix

Each of the four models receives six current-pulse scenarios:

- Source: soma, basal-q75, apical-q75.
- Pulse width: 2 ms and 10 ms.
- Current: 10 pA.
- Start: 2 ms.
- Duration: 20 ms.
- Backward Euler time step: 0.1 ms.

Every scenario is evaluated at all seven retained output ports. Raw rows include scenario, source, pulse width, per-port NRMSE, peak error and all-port NRMSE. The four models × six scenarios × (seven ports + aggregate) produce 192 transient rows per morphology/mesh configuration. The ten-frequency sweep adds 40 frequency-domain rows, for 232 expected rows per configuration; the code enforces this count.

### Morphology/reference matrix

The workflow reuses the same three morphology records and two NEURON reference mesh caps (0.125 and 0.0625 µm), for six independent configurations. This keeps the experiment comparable with the prior validated 10 kHz audit.

## Implementation

- Generalize the transient comparison helper to support a named source and parameterized pulse width, start, amplitude, timestep and duration, with strict input validation.
- Add the four-model frequency comparison and six-scenario transient matrix.
- Verify each reduced model retains the same ordered port set as the audit.
- Check positive definiteness before any frequency/time response.
- Assert the exact number of output rows before saving.
- Preserve one dated CSV per morphology/mesh artifact using the existing Schur/PRIMA Actions workflow.
- Extend unit tests to cover multi-shift order caps, finite reciprocal frequency responses and transient current injection through every retained input port.
- Correct the previous 10 kHz report so it records the completed 4/4 Core CI and post-merge checks.

## Reproduction protocol

GitHub Actions installs Python 3.12, the editable AMSN test package and NEURON 9.0.2. The matrix job executes:

```bash
cd amsn-core
python -m pytest
python examples/human_schur_port_matrix_audit.py
```

The base PRIMA 10 kHz audit on main has already passed. This experiment is not considered validated until the new code, tests, six matrix jobs and raw artifacts all pass.

## Current validation state

- Base main Core CI [44965966066](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966066): success, 4/4 jobs.
- Base main Schur/PRIMA [44965966021](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966021): success, 6/6 jobs.
- Base main fine-mesh audit [44965966005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965966005): success.
- Base main frequency audit [44965965999](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44965965999): success, 3/3 jobs.
- New order/transient branch: files have been written and read back from GitHub; PR-specific checks have not yet run. No new order-sweep or transient result is claimed.

## Interpretation limits

The experiment remains a passive linear RC validation at seven chosen ports. It does not establish accuracy of active ion channels, nonlinear synapses, calcium, gene expression, metabolism, plasticity or biological behavior. The fixed passive parameters are numerical reference values rather than population-fitted distributions. NMO_290988 is a partial dendritic reconstruction without an axon and is not a healthy-control morphology. The full Hines solver remains canonical.

## Next decision

After all six jobs complete, aggregate the frequency-domain and transient matrices. Choose an optional order/basis preset only if direct NEURON errors and transient behavior are acceptable across all three morphology records and both mesh caps. Otherwise retain the four-shift default, record the failures, and identify the source/port/scenario driving each error.
