# Human cortical L2–3 evidence update — 2026-11-20

This note captures literature that materially changes the parameterization strategy for AMSN. It supplements rather than rewrites the original research dossier.

## 1. Planert et al. — electrophysiological subtypes and synaptic microcircuits

**Reference:** Planert et al., *Electrophysiological classification of human layer 2–3 pyramidal neurons reveals subtype-specific synaptic interactions*, Nature Neuroscience 29, 455–466 (published online 10 Dec 2025; volume year 2026). https://doi.org/10.1038/s41593-025-02134-7

Key scope and observations:
- Tissue: acute slices from middle temporal gyrus in 23 patients undergoing anterior temporal lobe resection for pharmacoresistant epilepsy. Therefore, results describe this sampled clinical tissue and should not automatically be generalized to healthy cortex or other cortical regions.
- 1,479 pyramidal neurons were recorded; 1,214 passed stated QC. Cellular property analysis used 901 neurons from 22 individuals. The study tested 9,834 potential connections and detected 1,419 monosynaptic connections; 1,094 of 6,911 included tests contributed to the reported mean connection probability of 15.8% after stated exclusions.
- Fifteen cellular and five synaptic electrophysiological properties were analysed. Four electrophysiological types were identified: LowRin, DoubSpk, FastAP and SlowAP. In the 901-cell morphology/property analysis, reported group counts were 293 LowRin, 27 DoubSpk, 136 FastAP and 445 SlowAP.
- Cellular properties including input resistance, AP frequency, F/I slope, sag ratio and AP upstroke vary with cortical depth. Median pia-to-soma depth was 637 µm (IQR 216 µm) in the analysed population.
- Synaptic features showed broad distributions. Median EPSP amplitude was 0.46 mV; median paired-pulse ratio was 0.93 at 20 Hz. In this study these synaptic amplitude/PPR measures did not show a statistically significant relationship with cortical depth, although intrinsic cellular properties did.
- Subtypes were associated with different morphology and synaptic embedding. LowRin cells received more synaptic inputs, with smaller initial EPSPs and stronger facilitation. SlowAP cells received fewer but stronger inputs; their outgoing and incoming EPSPs were larger and more depressing. Homotypic SlowAP synapses had a reported median EPSP amplitude around 0.9 mV versus 0.58 mV for LowRin and 0.45 mV for FastAP; homotypic SlowAP PPR was 0.87, LowRin 1.01 and FastAP 1.24.

### Consequence for AMSN

The earlier plan to build a single "canonical human L2/3 pyramidal neuron" is too coarse. The project should represent a **population of subtype-conditioned parameter sets**, not collapse all cells into one mean:

1. Keep morphology and electrophysiology linked by cell or at least by explicitly stated population-level assumptions.
2. Treat e-type and cortical depth as separate covariates; depth influences intrinsic cellular phenotypes, while synaptic amplitude/PPR in this dataset were not significantly depth-dependent.
3. Model distributions (including skew/heavy tails) and donor-level variation, not only mean/standard-deviation where the data support something else.
4. Build a microcircuit-level extension only after the single-cell electrical kernel is validated; use subtype-conditioned connection probability and synaptic dynamics.
5. Do not use the patient-level raw human data as if freely downloadable. The article states that processed data and analysis/visualization code are available via Figshare, while original human participant data are not publicly open due to data-protection regulations.

**Data/code:** https://doi.org/10.6084/m9.figshare.28184126

## 2. Sharma et al. — paired transcriptomics and electrophysiology

**Reference:** Sharma et al., *The Unreasonable Effectiveness of Cell Types in Describing Neuronal Physiological Features*, bioRxiv preprint, DOI https://doi.org/10.64898/2026.08.27.744753 (published 16 Sep 2026; preprint, not a peer-reviewed journal article at this checkpoint).

The study uses paired patch-sequencing data from 495 human neurons from neurosurgical tissue to predict electrophysiological features from transcriptomic representations. Its abstract reports that cluster-level cell-type representations generally outperformed highly variable genes, ion-channel gene sets and context-enriched scGPT embeddings; combining cell-type and scGPT model outputs performed best.

### Consequence for AMSN

When adding gene expression, do not assume an end-to-end foundation model is automatically a better route than explicit cell-type variables. Test baselines in this order: subtype-only, channel-gene panel, broader variable genes, scGPT representation, then combined models. Avoid interpreting predictive association as causal channel regulation. Use the preprint as provisional evidence until independently peer-reviewed.

## 3. Owen et al. — human L2/3 postnatal maturation and BK channels

**Reference:** Owen et al., *Adolescent development accelerates responses to input in human neocortical neurons*, bioRxiv preprint, DOI https://doi.org/10.64898/2026.09.16.746058 (18 Sep 2026).

The preprint reports Patch-Seq and electrophysiology from neurosurgically resected pediatric human tissue, finding postnatal changes in human L2/3 pyramidal-cell spike-train dynamics, including faster spike latencies and selective acceleration of early spiking. It identifies BK-type calcium-activated K channels as a candidate driver and reports pharmacological and computational tests.

### Consequence for AMSN

Developmental age is another population covariate. A BK mechanism may be a high-value channel to investigate, but do not add a human L2/3 BK density profile without extracting the paper's measured parameters and experimental conditions. Treat the paper as a preprint until peer-reviewed validation.

## 4. BRAINCELL — current platform status and implications

**Reference:** Savtchenko et al., *BRAINCELL modelling platform for stochastic nanoscale organisation and dynamic extracellular signalling among neurons and glia*, Nature Communications 17 (2026), DOI https://doi.org/10.1038/s41467-026-77525-w, published 14 Sep 2026.

The paper presents a NEURON-based platform that generates empirical-statistics-constrained stochastic populations of nanoscale morphological/physiological features and models dynamic extracellular ion/signalling environments for neurons and glia. The public repository is https://github.com/RusakovLab/BRAINCELL; the inspected main-branch commit was `bf7d9255aac988b4b52acb177c82063b56894773` (28 Sep 2026).

Repository facts observed:
- The repository metadata reports BSD-3-Clause for the platform's own source.
- Its README specifies NEURON 8.2.x (tested with 8.2.2), Python 3.11 and an 8 GB recommended RAM footprint for the Windows GUI; it states exported HOC/MOD models can run on other OS platforms and HPC.
- Its README also warns that third-party binaries, vendored source and reference models may carry separate licenses, including a non-commercial component; review `THIRD_PARTY_NOTICES.md` before copying or redistributing components.
- The source tree has 1,015 entries. A complete source audit was not done in this checkpoint.

### Consequence for AMSN

BRAINCELL is now a directly relevant 2026 peer-reviewed platform, not just a possible older code sample. Before extending AMSN nanoscale or extracellular mechanisms, map BRAINCELL modules and licenses more comprehensively and run one controlled exported-model smoke test. The user's local 8 GB system is at the README's stated recommended RAM threshold, so prefer the exported command-line model route or cloud CI/HPC for larger simulations, not its full GUI plus large morphology datasets.

## 5. NEURON toolchain note

Official NEURON documentation lists release 9.0.2 dated 10 Aug 2026. The 9.0 line includes newer NMODL/C++ changes; NEURON 8.2.7 (25 May 2025) is explicitly noted as supporting Python 3.13 and NumPy >=2. For initial reproduction of an older published model with legacy MOD files, test a known compatible 8.2.x release first, then separately assess 9.0.2; never assume old MOD mechanisms compile unchanged across major versions.

Sources:
- https://www.neuronsimulator.org/en/latest/changelog.html
- https://www.neuronsimulator.org/en/8.2.7/changelog.html
- https://www.neuronsimulator.org/en/latest/install/install_instructions.html

## 6. Source and data boundaries

- Eyal et al. (2018) ModelDB 238347 is still the primary published detailed human L2/3 neuron baseline. The ModelDB landing page says its archive is about 133 MB and the source is provided as a downloadable zip, while the ModelDB GitHub mirror has only the README page. The full archive was not obtained in this runtime.
- The current container had Python 3.13.5, NumPy 2.3.5 and pytest 9.0.2, but no NEURON executable or Python module. An install attempt failed because the runtime could not resolve package-index DNS. Therefore no Eyal model reproduction is claimed.
- This checkpoint includes only literature interpretation and newly authored independent numerical foundations; it does not vendor BRAINCELL, Eyal mechanisms or restricted morphology data.
