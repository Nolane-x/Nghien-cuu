# Human AMPA temporal convergence on refined morphology — 2026-11-20

**Status:** reproducible temporal-convergence audit passed; remaining cross-engine error is now nearly timestep-independent over the tested range.  
**NEURON:** 9.0.2  
**Python:** 3.12.16 GitHub Actions runner  
**Workflow:** [44760319787 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787)  
**Code snapshot:** `a78fcd1ab00d4175b60898b9ad539d84d9d8bf74`  
**Raw CSV:** [human_ampa_temporal_convergence_2026-11-20.csv](../results/human_ampa_temporal_convergence_2026-11-20.csv), 18,615 data rows  
**Workflow artifact:** [14640319049](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787/artifacts/14640319049)

## Research question

After choosing a spatially refined reference (NEURON max segment length 0.5 um) and a fixed AMSN mesh (2,000-Hz electrotonic reference), do the AMPA voltage traces converge as the fixed time step is reduced? Does the remaining AMSN-versus-NEURON error decrease with dt, or approach a non-temporal error floor?

The goal is to separate temporal integration error from differences between the two spatial representations. This is a numerical comparison, not biological calibration.

## Fixed morphology, mesh and input

### Morphology and sites

- Source: NeuroMorpho.Org NMO_290988 / `1094_Mohan_etal_2015.CNG.swc`.
- 8,903 SWC nodes, soma and basal/apical dendrites; no axon. The reconstruction is partial, with moderate dendritic completeness and metadata indicating mesiotemporal sclerosis. Retain the source CC BY 4.0 attribution; do not generalize this cell to healthy human cortical neurons.
- Input: basal q75, SWC node 3784.
- Probes: basal q75 source 3784, soma 1, basal q90 3814.
- NEURON segment-centre mapping offsets with 0.5-um maximum segment length:
  - basal q75: 0.079655 um;
  - soma: 0 um;
  - basal q90: 0.242787 um.

### Spatial meshes held fixed

| Simulator | Spatial resolution | Electrical nodes |
|---|---|---:|
| NEURON 9.0.2 | max section segment length 0.5 um | 25,233 segments |
| AMSN | 2,000-Hz electrotonic reference, max electrical edge extent 0.1, physical cap 100 um | 2,541 compartments |

The two simulators do not use identical compartment/segment locations. The sites are protected/matched through the SWC source identifiers and NEURON segment-centre mapping is explicitly reported.

### Passive and synaptic parameters

- (R_i=0.7\;\Omega\,m)
- (R_m=1.0\;\Omega\,m^2)
- (C_m=0.01\;F/m^2)
- (E_{leak}=-65\;mV)
- AMPA-like peak conductance 0.8 nS
- τ_rise = 0.2 ms; τ_decay = 2.0 ms
- (E_{rev}=0\;mV)
- Deterministic NetStim: one event, start 0 ms, noise 0
- Duration 5 ms

The synaptic parameters are the established engineering test waveform from the earlier audits, not a fitted human synapse. The passive parameter set is generic, not cell-specific.

## Method

Script: `amsn-core/examples/human_ampa_temporal_convergence.py`.

The same morphology, spatial meshes, protected SWC sites, passive parameters, event and conductance waveform are used in all runs. Only the timestep is changed:

`0.025, 0.0125, 0.00625, 0.003125, 0.0015625 ms`

The five time grids are nested exactly (each coarser step is an integer multiple of the finest step). Each simulator is compared to its own finest-dt trace by sampling the 0.0015625-ms trace at the matching coarse points. Cross-engine voltage traces are compared at equal physical times.

Event timing is aligned using the previously verified fixed-step convention: in the tested NetStim/Exp2Syn protocol, NEURON's recorded conductance at time (t) matches the analytic conductance at (t-dt); AMSN samples its callback at the left edge of each implicit step. The protocol-specific offset must not be generalized to variable-step NEURON or other event schedules.

## Results: q90 basal probe

All voltage values are deflections above the -65 mV leak. Self-convergence errors compare each timestep with that simulator's own 0.0015625-ms trace.

| dt (ms) | Cross-engine max abs (mV) | Cross-engine RMS (mV) | NEURON vs finest RMS (mV) | AMSN vs finest RMS (mV) |
|---:|---:|---:|---:|---:|
| 0.025 | 0.006266 | 0.003798 | 0.088665 | 0.088695 |
| 0.0125 | 0.006376 | 0.003826 | 0.041208 | 0.041222 |
| 0.00625 | 0.006433 | 0.003840 | 0.017625 | 0.017631 |
| 0.003125 | 0.006461 | 0.003847 | 0.005869 | 0.005871 |
| 0.0015625 | 0.006475 | 0.003851 | 0 | 0 |

The corresponding q90 self-convergence max absolute errors (NEURON / AMSN) are:

| dt (ms) | NEURON max abs (mV) | AMSN max abs (mV) |
|---:|---:|---:|
| 0.025 | 0.203078 | 0.203189 |
| 0.0125 | 0.094326 | 0.094381 |
| 0.00625 | 0.040332 | 0.040358 |
| 0.003125 | 0.013429 | 0.013437 |
| 0.0015625 | 0 | 0 |

Both simulators' self-convergence errors decrease monotonically as dt is reduced. Across the full range, q90 self-convergence RMS error falls from about 0.0887 mV to zero by definition at the finest reference. The halving ratios are not constant, so these five runs do not establish a precise asymptotic convergence order; they do demonstrate that the temporal error is being reduced.

### Cross-engine discrepancy approaches a floor

The q90 AMSN-versus-NEURON RMS difference changes only from 0.003798 mV at 0.025 ms to 0.003851 mV at 0.0015625 ms (about 1.4% change). Maximum absolute difference changes from 0.006266 to 0.006475 mV (about 3.3%).

This is the key result: once both models are temporally refined, their cross-engine difference is nearly unchanged. The residual is therefore not dominated by the tested timestep range. It is more plausibly associated with spatial representation, segment/control-volume geometry, mapping, area lumping, or other discretization/formulation differences. This experiment does not separate those remaining components individually.

### Peak values

| dt (ms) | NEURON q90 peak (mV above leak) | AMSN q90 peak | NEURON peak time (ms) | AMSN peak time (ms) |
|---:|---:|---:|---:|---:|
| 0.025 | 11.200768 | 11.204347 | 1.700000 | 1.700000 |
| 0.0125 | 11.227663 | 11.231268 | 1.687500 | 1.687500 |
| 0.00625 | 11.241034 | 11.244652 | 1.681250 | 1.681250 |
| 0.003125 | 11.247709 | 11.251343 | 1.681250 | 1.681250 |
| 0.0015625 | 11.251039 | 11.254675 | 1.678125 | 1.679688 |

At the finest dt, the peak-amplitude difference is about 0.003635 mV. The sampled peak times differ by one fine step; peak-time estimates are grid-quantized and should not be overinterpreted as a continuous-time latency difference.

### Source and soma cross-engine results

Across the five dt values:
- q75 source RMS difference remains about 0.003283–0.003304 mV, with max absolute difference about 0.004325–0.004347 mV.
- Soma RMS difference remains about 0.00003455–0.00003472 mV, with max absolute difference about 0.00004321–0.00004328 mV.

This is consistent with q90 having the largest residual mismatch along the tested dendritic path.

### Relative error and reference floors

The q90 maximum relative error (reference deflection floor 0.02 mV) ranges from 1.03% to 1.48%, while the absolute/RMS error is nearly constant. The 1.0-mV reference-floor relative errors are about 0.44–0.49%.

Relative errors near the EPSP onset are sensitive to small denominators. The report and raw output therefore retain several reference-voltage floors and the absolute/RMS metrics; a single maximum-relative-error number is not a meaningful acceptance criterion by itself.

## CI and preserved raw output

- Workflow: [44760319787](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787), conclusion success, 1/1 job successful.
- Command: `python examples/human_ampa_temporal_convergence.py`.
- NEURON: 9.0.2; Python: 3.12.16.
- Raw dataset: `amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv`, 18,615 rows (5 timesteps × their samples × 3 recording sites).
- Compressed workflow artifact: [14640319049](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787/artifacts/14640319049).

The harness itself required two corrections, which remain visible in GitHub Actions history:
1. Run 44759371095 failed because the coarse/fine timestep ratio was inverted, yielding a zero slice step.
2. Run 44760000836 corrected the ratio but revealed that previous NEURON `Vector.record()` objects were retained across `finitialize()`, allowing new runs to overwrite their recorded arrays. The script now copies each trace into independent NumPy arrays and releases the HOC record vectors before the next timestep. NEURON's documentation describes record-vector storage as being updated on later runs and explains its lifecycle: https://www.neuronsimulator.org/en/9.0.1/progref/programming/math/vector.html.
3. Run 44760319787 passed with the nested-grid check and isolated trace storage.

The Core CI associated with the code snapshot was still running when this report was prepared; refresh its latest run before describing the full-repository CI status. The dedicated temporal audit is independently successful.

## Interpretation and limits

- The one-compartment membrane equation and event-timing convention have already passed a controlled NEURON equivalence audit.
- The selected refined spatial configuration is stable in time over the tested dt range.
- The q90 cross-engine error is now close to a spatial/representation floor of roughly 0.00385 mV RMS and 0.00648 mV max absolute for this particular passive morphology and AMPA event.
- The result does not establish biological accuracy, a universal tolerance, or general performance on other cells/branches.
- The 0.5-um NEURON mesh is the finest reference in this experiment, not exact analytical truth.
- No voltage-gated dendritic channels, NMDA magnesium block, spine neck, calcium, active conductances or experimental EPSP fitting are included.
- No parameter was tuned to force agreement.

## Next experiments

1. At dt=0.0015625 ms, run an AMSN spatial-frequency sweep beyond 2,000 Hz (e.g. 2,000/3,000/4,000 Hz) against the fixed NEURON 0.5-um reference to see whether the remaining ~0.00385-mV RMS floor decreases.
2. Repeat at a second basal branch and an apical path to distinguish a local mapping issue from a general representation difference.
3. Add a branch-local matched-location test and quantify membrane-area allocation on each side of the protected input/probe site.
4. Only after spatial and temporal error budgets are separated should a numerical acceptance tolerance be proposed.
5. Reproduce an original Eyal/ModelDB cell with its own morphology and mechanisms before claiming a matched human L2/3 model; do not combine unrelated source morphology and parameter sets and call the result a reproduction.
