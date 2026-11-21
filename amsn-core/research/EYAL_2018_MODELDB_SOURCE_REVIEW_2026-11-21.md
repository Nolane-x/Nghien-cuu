# Eyal et al. 2018 ModelDB source review

**Date:** 2026-11-21  
**AMSN repository:** https://github.com/Nolane-x/Nghien-cuu  
**ModelDB accession:** 238347  
**ModelDB record:** https://modeldb.science/238347  
**ModelDB GitHub record:** https://github.com/ModelDBRepository/238347  
**Paper:** https://doi.org/10.3389/fncel.2018.00181  
**Status:** source metadata verified; official ZIP access/download and archive integrity not yet verified.

## Why this is a relevant reference

ModelDB identifies accession 238347 as *Comprehensive models of human cortical pyramidal neurons (Eyal et al. 2018)*. Its record describes six human layer 2/3 pyramidal cells modelled using anatomical and physiological data from fresh and postmortem human temporal cortex. It explicitly covers dendritic spines, dendritic NMDA spikes, somatic/axonal Na+ spikes, and AMPA/NMDA receptors. The ModelDB record reports predicted AMPA and NMDA conductance per synaptic contact of 0.88 nS and 1.31 nS, respectively. These are publication-level model predictions, not values to blindly assign to the current AMSN morphology.

The Human Brain Project's *Human Neurons* resource lists the Eyal et al. 2018 ModelDB download and the publicly stated access code `eyal2018`. It also states that the 2018 work extended the human L2/3 passive models to synaptic properties (including NMDAR kinetics) and ion channels underlying somatic/axonal spiking.

## What is verified about source availability

1. The official ModelDB record exists at accession 238347.
2. The ModelDB record links to GitHub repository `ModelDBRepository/238347`.
3. The public GitHub tree for that repository contains only `readme.html` (971 bytes); it does not contain the simulation source tree or mechanism files.
4. That README directs users to the official Yale/SenseLab archive `EyalEtAl2018.zip`, described there as 133 MB, and lists source folders such as `ActiveMechanisms/`, `Morphs/`, `Figure1/`, `Figure3/`, `Figure4/`, `Figure6/` and `Figure8/`.
5. The Human Brain Project page publishes the ModelDB access code `eyal2018`; this is not a personal credential.

**Important:** the full ZIP has not yet been downloaded and integrity-checked in this checkpoint. Do not claim that AMSN has incorporated, reproduced, or run the Eyal archive. Do not substitute an unofficial mirror or treat the single-file GitHub record as the complete model.

## Scientific integration plan after official archive retrieval

Before any code is imported, create a manifest for the archive and verify:
- ZIP integrity, full byte size, folder tree and file hashes.
- Original morphologies, cell identities, provenance and license/attribution terms.
- All `.mod` mechanisms, NMODL states/parameters, units, temperature assumptions and reversal potentials.
- Section/cell parameterization, passive membrane constants, axial resistance, spine handling and area scaling.
- Synapse types, kinetics, conductance units, location rules, and the exact experimental protocols for each published figure.
- Reproducibility instructions and the NEURON version/build expected by the original implementation.

Then implement a separate *reference reproduction harness* in AMSN. Start with one clearly documented Eyal cell and one figure-level protocol; do not combine the Eyal morphology with the existing NMO_290988 morphology. Compare intermediate quantities (area, axial graph, passive DC, AC impedance, synaptic conductance waveform and spike thresholds) before comparing final voltage traces.

## Guardrails

- The current AMSN human morphology is a separate partial NMO_290988 reconstruction, without an axon; its metadata notes mesiotemporal sclerosis. It is not one of the Eyal cell morphologies by default.
- Do not transplant conductance values between cells without checking the corresponding model/cell configuration.
- Do not tune AMSN passive parameters to force the external model to match.
- Do not redistribute source files until archive-specific license/terms have been read.
- Preserve original source files and hashes separately from AMSN implementation code.

## Current AMSN status when this review was written

The passive frequency-domain phasor solver has been compared with NEURON 9.0.2 on the NMO_290988 morphology at 0.5, 0.25, 0.125 and 0.0625 µm segment caps, with 120 source/probe/frequency rows per mesh. Four-mesh aggregates and raw artifact links are in [the passive frequency-domain audit](HUMAN_PASSIVE_FREQUENCY_RESPONSE_AUDIT_2026-11-21.md).

The complete AMSN Core CI on commit `ccde2542c62843ac2a7f3c41efe2206e16eee543` passed 4/4 jobs ([run 44881036875](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44881036875)), including Python 3.12/3.13 tests and NEURON cross-validation, transient pulse/step, AMPA-like conductance, Exp2Syn timing and single-compartment checks.
