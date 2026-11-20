# Human L2/3 excitatory-synapse reference notes

**Date:** 2026-11-20  
**Scope:** Literature-derived priors for the next AMSN synaptic experiments. This is not a calibration of the bundled NeuroMorpho cell.

## Evidence and interpretation

### Eyal et al. (2018): human temporal-cortex L2/3 pyramidal connections

Primary paper: Guy Eyal et al., *Human Cortical Pyramidal Neurons: From Spines to Spikes via Models*, Frontiers in Cellular Neuroscience 12:181 (2018), https://doi.org/10.3389/fncel.2018.00181. Open full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/

The abstract reports predicted per-contact AMPA and NMDA conductances of 0.88 nS and 1.31 nS. These are model-derived estimates based on paired recordings, blockers, extracellular current injection and an assumption of five contacts per connection; they are not universal constants.

The paper's Table 1 reports connection-specific fits for seven human L2/3-to-L2/3 pairs. The published values are:

| Pair | AMPA gmax (nS) | AMPA tau1 (ms) | AMPA tau2 (ms) | NMDA gmax (nS) | NMDA tau1 (ms) | NMDA tau2 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| 110602A | 0.71 | 0.33 | 0.33 | 0.39 | 0.23 | 31 |
| 280503A | 0.21 | 0.99 | 2.0 | 1.0 | 5.0 | 46 |
| 130602A | 0.25 | 0.060 | 0.63 | 0.13 | 0.79 | 97 |
| 120902A | 0.46 | 0.26 | 2.0 | 0.22 | 1.6 | 7.6 |
| 060202B | 0.67 | 0.41 | 0.41 | 0.0010 | 4.1 | 12 |
| 110602A2 | 0.51 | 0.45 | 0.77 | 0.40 | 2.0 | 22 |
| 260802A | 0.84 | 0.020 | 1.8 | 0.69 | 3.2 | 34 |
| **Mean** | **0.52** | **0.36** | **1.1** | **0.40** | **2.4** | **36** |
| **SD** | **0.24** | **0.32** | **0.75** | **0.34** | **1.7** | **30** |

The table demonstrates substantial between-connection heterogeneity. Rounded table entries with tau1=tau2 (0.33/0.33 and 0.41/0.41 ms) must not be passed blindly into a strict double-exponential implementation that requires tau1<tau2; the unrounded source model or an analytically justified alpha-function limit is needed.

A later passage in the same paper describes one selected "best typical" model with gAMPA=0.73 nS, blocked AMPA=0.13 nS, gNMDA=1.31 nS, NMDA tau-rise=8.02 ms, tau-decay=34.99 ms and voltage-dependence slope gamma=0.077 mV^-1. These belong to that selected model, not to every row of Table 1.

Table 1 source view: https://academic.oup.com/view-large/43203137

### NEURON Exp2Syn reference implementation

The official NEURON mechanism source is https://github.com/neuronsimulator/nrn/blob/master/src/nrnoc/exp2syn.mod. It stores two kinetic states A and B, solves their kinetics with cnexp, then computes conductance as g = B - A. The event initializes both states with a peak-normalization factor. NEURON's documented NetCon weight unit for Exp2Syn is microsiemens.

This source ordering matters for time indexing: a fixed-step simulation's kinetic state is advanced to the integration endpoint before the conductance is used in the membrane current calculation. AMSN's synaptic callback is therefore now sampled at the endpoint of each implicit voltage step, rather than at its left edge. See the source implementation and endpoint regression test.

## How these sources should and should not be used

- **Literature observation:** human L2/3 excitatory synapses show broad per-connection conductance and kinetic variation in the Eyal fits.
- **Model-specific estimate:** 0.73 nS AMPA and 1.31 nS NMDA are values from one selected typical model, while the abstract reports 0.88 and 1.31 nS as headline estimates.
- **Not a universal biological prior:** do not replace all synapses with one mean parameter set without an uncertainty/distribution model.
- **Not a matched-cell parameter set:** the AMSN fixture NMO_290988 / 1094_Mohan_etal_2015.CNG.swc is a separate, partial temporal-cortex reconstruction whose provenance notes mesiotemporal sclerosis and moderate dendritic completeness. It is not one of Eyal's six cells. Combining the morphology and Eyal parameters creates a cross-source model and must be labelled as such.
- **Current AMSN test waveform:** 0.8 nS, tau-rise 0.2 ms, tau-decay 2.0 ms, Erev 0 mV is an engineering AMPA-like test input. It is not an Eyal-calibrated or patient-specific synapse.

## Research implications

1. Preserve the published pair-level variation instead of hard-coding a "human AMPA default".
2. Reproduce one original Eyal/ModelDB model and its own morphology/mechanisms before claiming biological reproduction. Repository landing page: https://github.com/ModelDBRepository/238347 (the repository README points to the original model archive).
3. First validate the event waveform and numerical integration independently of the cable morphology. Then test the full cable response with timestep and spatial convergence.
4. For near-equal rise/decay constants, derive and test the alpha-function limit rather than silently perturbing rounded literature parameters.
5. Only then add an NMDA component with a literature-sourced kinetic waveform and voltage-dependent Mg2+ block, and compare against the original mechanism.
6. Report per-cell and per-contact assumptions, units, uncertainty and morphology provenance at every stage.

## Limits of this note

This is a targeted source review, not a full reimplementation of the Eyal model. The original ModelDB archive and its active mechanisms have not yet been imported or reproduced in this checkpoint. No experimental trace has been fitted here.
