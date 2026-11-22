# Human somatic NaV/KV evidence baseline — Wilbers 2023 and Eyal 2018

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Base commit:** `7655389b9d95dc85a54f81185a037ab026e32300`  
**Status:** source-backed literature audit and machine-readable transcription; **not** an active-channel implementation or biologically validated parameter set.

## Research question

Can AMSN establish a defensible starting evidence set for active sodium and potassium conductances in human supragranular pyramidal neurons without confusing measured somatic currents, fitted single-compartment parameters, and compartment-specific model estimates?

## Main result

Two studies provide complementary but fundamentally different evidence:

1. **Wilbers et al. (2023)** directly measured pharmacologically isolated voltage-gated Na+ and K+ currents in somatic nucleated patches and characterized their voltage dependence and kinetics. These measurements constrain **somatic** channel behavior; they are not AIS/axon density measurements.
2. **Eyal et al. (2018)** used multi-objective optimization of recorded spike waveforms to estimate somatic/axonal channel densities in six human L2/L3 pyramidal-cell models, while assuming rodent-like channel kinetics. These are **model estimates**, not direct measurements of human channel density.

They must remain separate provenance classes in AMSN. The machine-readable transcription is in [`references/human_nav_kv_evidence_2023.json`](references/human_nav_kv_evidence_2023.json).

## 1. Wilbers et al. 2023 — direct somatic measurements

The article reports human somatic nucleated-patch conductance densities (mean +/- SEM):

| Current | Mean | SEM | n | Unit |
|---|---:|---:|---:|---|
| Na+ | 5.9 | 0.8 | 17 | pS/um^2 |
| K+ | 31.2 | 4.2 | 13 | pS/um^2 |

Because (1\ \mathrm{pS}/\mu\mathrm{m}^2 = 1\ \mathrm{S}/\mathrm{m}^2), the corresponding SI means are 5.9 S/m^2 and 31.2 S/m^2. The thesis appendix reports the same patch-density estimates as mean +/- SD (Na+: 5.85 +/- 3.38; K+: 31.22 +/- 14.71 pS/um^2). The two summaries describe different measures of spread; the primary article's SEM must not be relabelled as SD.

The recordings used somatic nucleated patches and pharmacological isolation of Na+ and K+ currents. Most channel recordings were carried out at 34 C, with sodium-channel kinetic recordings at 25 C. The human material came from neurosurgical resections; the thesis methods describe 19 subjects and tissue from temporal, frontal and parietal cortex, removed to access deeper structural pathology. This context must accompany any later generalization.

### Voltage dependence and kinetics

The paper reports more depolarized Na+ activation and inactivation curves in human neurons than mouse, slower Na+ activation and inactivation time constants, and faster Na+ recovery from inactivation. At -80 mV, Na+ availability was 0.81 +/- 0.16 in human versus 0.63 +/- 0.21 in mouse.

For K+, both steady-state activation and inactivation were shifted toward more depolarized voltages. Human K+ currents activated faster at lower membrane potentials in the tested protocol; the fast and slow inactivation components were similar between species, while recovery time constants were similar and human currents recovered to a larger proportion of their initial amplitude. Reported K+ availability at -80 mV was 0.94 +/- 0.05 in human versus 0.86 +/- 0.06 in mouse.

The mean half-voltages in Table S1 are recorded in the JSON with sample counts and SD. Table S1 explicitly states that the voltage data were not corrected for a 15 mV liquid-junction potential. The extracted thesis table labels Boltzmann slope-factor units as ms^-1, which is dimensionally suspect for a voltage slope; those slopes are deliberately excluded from runtime-ready data pending source-equation verification.

### Measured density is not the same as the paper's fitted HH density

The Wilbers paper also reports a single-compartment HH-based AP model with a 10 um diameter and model parameters of 114.5 pS/um^2 for Na+ and 29.05 pS/um^2 for K+. These are computational model parameters, not the measured patch densities above. In particular, the authors explicitly note that the sodium conductance density required to generate APs in their single-compartment model exceeded the sodium density measured in somatic nucleated patches.

Therefore AMSN must not silently substitute the 114.5 pS/um^2 fitted sodium conductance for the 5.9 pS/um^2 measured somatic mean, or vice versa. They answer different questions in different model contexts.

## 2. Eyal et al. 2018 — compartment-specific model estimates

Eyal et al. modeled six human layer 2/3 pyramidal cells using approximately 900 recorded spikes and multi-objective optimization. Their reported estimates include:

| Component | Model compartment | Estimate (S/cm^2) |
|---|---|---:|
| Na+ | axon | 4.9 +/- 1.0 |
| Kv3.1 | axon | 1.9 +/- 0.1 |
| Persistent K+ | axon | 0.019 +/- 0.039 |
| Persistent K+ | soma | 0.0002 +/- 0.0004 |
| Na+ | soma | 0.33 +/- 0.17 |

The paper states that these model estimates assumed rodent-like channel kinetics. They are not direct human channel-density measurements. The authors also state that direct recordings from human pyramidal-cell dendrites were lacking, leaving the extent of dendritic back-propagating action potentials unresolved.

The Kv3.1 and persistent-K model components are not equivalent to the total voltage-gated K+ current measured in Wilbers' somatic patches. Comparing the raw numerical values across those studies without matching channel subtype, compartment, experimental method and model role would be misleading.

## 3. Implications for AMSN architecture

The current AMSN `hh.py` is the canonical Hodgkin-Huxley 1952 squid-axon smoke test, explicitly not a human cortical parameterization. The current synapse code is a double-exponential conductance kernel, not a full receptor-state model. This evidence review does not change either module and does not activate a human channel model.

A safe next implementation stage should be a separate, opt-in **human somatic NaV/KV reference mechanism**, with:

- explicit channel provenance and evidence class (measured versus fitted);
- independent parameter namespaces for measured patch data and model-fit data;
- documented temperature and liquid-junction-potential handling;
- channel-state equations and rate functions verified against the original dataset/model source before coding;
- independent voltage-clamp reproduction tests for activation, inactivation, recovery and AP-waveform clamp;
- an isolated single-compartment reproduction before spatial insertion into an L2/L3 cable morphology;
- no dendritic or AIS density extrapolation until independently supported.

The dataset DOI for Wilbers et al. is **10.34894/L5J0SD**. The VU Research Portal confirms that the accompanying data files are listed at DataverseNL. Dataverse's public API and object-store downloads were used to inspect selected source code and mechanism files, with independent SHA-256 hashes recorded. Raw numerical workbooks and the 15.1 MB AP-clamp trace matrix remain undownloaded; the selected files have not been compiled or reproduced in NEURON.

## 4. Provenance and limitations

- Wilbers primary article: https://doi.org/10.1126/sciadv.ade3300
- Wilbers data record: https://doi.org/10.34894/L5J0SD
- Wilbers thesis (appendix tables S1-S3): https://research.vu.nl/ws/files/226991367/phdthesisrenewilbers%20-%206446c97ab7c6a.pdf
- Eyal et al. 2018: https://doi.org/10.3389/fncel.2018.00181
- ModelDB accession 238347: https://modeldb.science/238347

The curated Wilbers source inventory and selected source hashes are recorded; no raw mechanism or script bytes were copied into AMSN. The original Eyal ModelDB ZIP remains not downloaded/not reproduced. This document records literature observations and source-audit findings, not an executed active-channel model.

## 5. Decision

**Accepted for evidence catalog only:** Wilbers 2023 patch measurements, voltage half-voltages and the separate one-compartment fitted conductances; Eyal 2018 compartment-specific model estimates.

**Not accepted as runtime defaults:** any of the above. No conductance has been assigned to the current AMSN cable tree; no production parameter or simulator default was changed.

## Next concrete experiment

Retrieve and hash the original Wilbers Dataverse data/model archive. Reconstruct the exact human Na+ and K+ gating equations from the publication's source files, then reproduce the somatic voltage-clamp protocols at the reported temperatures before attempting AP generation or integrating the channels into a multicompartment human morphology.


The official DataverseNL API resolves DOI 10.34894/L5J0SD to dataset ID 317867, released version 3.0 (internal version ID 24561), published 2022-11-10 and last updated 2022-12-13. The dataset declares CC0-1.0 and contains 65 files.

The inventory includes raw Figure 1–4 workbooks, AP-clamp traces and amplitudes, channel-fitting code, two distinct MOD folders, current-clamp code and conductance-density grids, and frequency-tracking data. A curated inventory with file paths, IDs, MIME types, byte sizes, official SHA-1 checksums and independently computed SHA-256 values is stored in `references/wilbers2023_dataverse_source_manifest_2026-11-22.json`.

Selected Na/K mechanism files and fitting/helper scripts were read from the Dataverse public object-store endpoints in an isolated research session and SHA-256 hashed. Their byte counts and SHA-1 values were cross-checked against the Dataverse file metadata API. The source bytes were not committed into AMSN. Numeric workbooks and the 15.1 MB AP-clamp `H_wide.csv` remain undownloaded; this manifest is a curated subset, not a 65-file mirror.

## Sodium mechanism — Figures5_6/MOD/na_human.mod

Dataverse file ID 318629; 3,602 bytes; SHA-1 `b199d70c3d0e7a2e991fd8d26c54b1318e3c0970`; observed SHA-256 `e23ed354aa683639bfd2ffdeae4b2544adf8c5cce6f8a4adbada42549310f2fd`.

The source comments describe an HH-style sodium channel based on Mainen (1994), edited by Kole (2006), then modified/fitted by René Wilbers at VU in 2020. It uses two gates `m,h`:

[
g_{Na}=tadj\,\bar g_{Na}m^3h,\qquad I_{Na}=10^{-4}g_{Na}(V-E_{Na}).
]

Steady-state activation/inactivation are separated from activation/inactivation time constants. Reference temperature is 25 °C, (Q_{10}=2.3), and the MOD file has an active 199-point `TABLE` over -120 to +100 mV. The fitting driver uses a 10 µm single-compartment section (`Ra=200`, `cm=1`) and sequentially fits inactivation/recovery, activation kinetics, and activation steady-state Vhalf/slope. The script's final parameter dictionary matches the distributed Na MOD values. Its voltage-clamp analysis runs steps from -80 to +10 mV in 5 mV increments at 25 °C.

## Potassium mechanism — Figures5_6/MOD/k_human.mod

Dataverse file ID 318647; 4,220 bytes; SHA-1 `d299b3430ecda7a94f6d1c37ac76b2878052c7d5`; observed SHA-256 `899aa0dfa697b7f735258e10b002c8876c108902afc0c13b82fc619decb66063`.

This is a mixed population of fast-, slow- and non-inactivating potassium channels. It uses `m,h1,h2`; default mixture values are `prop_inact=0.85`, `prop_h2=0.4`, `h2tau_inact=450 ms`, and `h2tau_inact_rec=2789.7929 ms`. Reference temperature is 34 °C and (Q_{10}=2.3). Unlike the sodium file, the `TABLE` directive in the distributed potassium MOD is commented out.

The fitting driver uses test steps from -110 to +50 mV in 10 mV increments and a long recovery protocol. **A parameter-provenance discrepancy remains unresolved:** its intermediate inactivation-fit dictionary matches the distributed MOD, but a later dictionary labelled “final best fit” reports different values for `thi1, thi2, qi1, qi2, Rd, Rg`. The driver also sets `h12factor=10.5`, while the distributed MOD comments out the `h1tau*h12factor` expression and uses fixed slow-inactivation/recovery time constants. No K kinetic snapshot is selected as definitive.

## Separate current-clamp variants

The dataset also contains `na_human.mod` and `k_human.mod` under `Figures5_6/Current_clamp/mod`. These are different Dataverse file records with different hashes; they add global conductance scaling and human-fraction variables `na_human_ratio` and `k_human_ratio`. They must not be silently substituted for the `Figures5_6/MOD` variants used for the channel comparison.

The current-clamp helper initializes a 10 µm compartment at 34 °C, inserts both human and mouse mechanisms and adjusts reversal potentials/voltage offsets for liquid-junction potentials. Its Powell gbar fit uses a target constructed as a **50:50 average of human and mouse median AP amplitude, upstroke and downstroke**. The resulting conductance densities are therefore not a human-only fit. The K voltage-clamp helper's recovery target is also explicitly the mean of human and mouse values.

## High-priority source-level warning — trap0

Both canonical human MOD files contain a `trap0` implementation where:

- the branch condition tests `fabs((v+th)/q)`;
- the main quotient uses `a*(v-th)/(1-exp(-(v-th)/q))`;
- the commented intended limit is `a*q`;
- the active fallback is `q*(1--(v-th)/q/2)`, omitting multiplier `a`.

At (v=th), the main expression has a removable (0/0) limit, but for nonzero `th` the current branch condition does not select that limit. The active fallback also does not equal the standard (a q) limit. This is a source-level numerical warning, **not yet a proven simulation failure**. The Na MOD uses tabulated rates while K calculates rates directly, so the runtime consequences may differ.

Before porting, compile the original mechanisms and probe values at (v=th-\epsilon), (v=th), and (v=th+\epsilon), comparing with a stable analytic reference and the published voltage-clamp protocols. Do not patch the source and claim equivalence without that comparison.

## Verification decision

The source audit has not cleared the runtime implementation gate. The sodium and potassium mechanism equations, source variants, fitted parameter snapshots and the trap0 issue must be resolved by independent NEURON reproduction before any mechanism is enabled. No production defaults or passive solver settings are changed.
