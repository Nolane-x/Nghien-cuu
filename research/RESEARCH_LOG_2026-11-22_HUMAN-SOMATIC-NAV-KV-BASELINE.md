# Research log — human somatic NaV/KV evidence baseline

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/wilbers-human-active-channel-baseline-2026-11-22`  
**Base:** `7655389b9d95dc85a54f81185a037ab026e32300`  
**Status:** literature audit and data-registry implementation; no active-channel simulation run.

## Question and hypothesis

The passive AMSN core is already numerically grounded, while the existing HH smoke test is a squid-axon model. The next biological gap is an evidence-based human cortical active-channel baseline. The hypothesis is that published somatic channel measurements and existing human L2/3 model estimates can provide useful constraints, but only if measurement, model fit and compartment-specific inference are represented as distinct evidence classes.

## Sources examined

- Wilbers et al. 2023, *Science Advances* 9, eade3300, DOI 10.1126/sciadv.ade3300.
- Wilbers thesis appendix, Tables S1-S3, for detailed mean/SD and model parameter tables.
- VU Research Portal DataverseNL record, DOI 10.34894/L5J0SD.
- Eyal et al. 2018, *Frontiers in Cellular Neuroscience* 12:181, DOI 10.3389/fncel.2018.00181.
- Existing AMSN source: `amsn-core/src/amsn/hh.py`, `cable.py`, `synapses.py`.
- Existing source audits: `FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md` and `EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md`.

## Main source observations

1. Wilbers et al. directly measured isolated voltage-gated Na+ and K+ currents in somatic nucleated patches. Main-article mean +/- SEM conductance densities are 5.9 +/- 0.8 pS/um^2 for Na+ (n=17) and 31.2 +/- 4.2 pS/um^2 for K+ (n=13).
2. The paper describes human-specific voltage dependence and kinetics: Na+ activation/inactivation curves shift toward depolarized voltages, activation and inactivation are slower, and recovery from inactivation is faster. K+ steady-state curves are also right-shifted; at lower voltages the measured K+ activation was faster, while recovery time constants were similar and recovery amplitude was larger in human.
3. The study's fitted single-compartment HH AP model uses gbarNa=114.5 and gbarK=29.05 pS/um^2. These are model parameters, not patch measurements. The paper explicitly notes that the sodium density needed for the single-compartment AP model exceeds the somatic patch density.
4. Eyal et al. 2018 model six human L2/L3 pyramidal cells with about 900 recorded spikes and multi-objective optimization. Their reported axonal/somatic channel densities are model estimates and assume rodent-like channel kinetics. Direct human dendritic channel recordings were unavailable in that paper.
5. The Wilbers data record is published at DataverseNL DOI 10.34894/L5J0SD, but the archive files could not be retrieved through the accessible landing page in this checkpoint.

## Implementation performed

- Added a provenance-aware JSON evidence registry separating measured somatic patch data, fitted single-compartment parameters and Eyal 2018 compartment-specific model estimates.
- Preserved raw reported means and uncertainty types, plus SI conversions.
- Captured sample counts, experimental region, channel recording temperature nuance, liquid-junction-potential caveat and the unknown dendritic/AIS mapping.
- Added tests that validate JSON structure, evidence labels, unit conversions, sample counts and the guard against runtime use.
- Added a human-readable research report and handoff.
- Updated the top-level handoff pointer without modifying the existing PR #8 branch.

## Validation status

- The JSON was parsed and its unit/evidence fields were programmatically checked before commit.
- The new pytest file has **not** been executed in this checkpoint.
- No Python active-channel solver was added or executed.
- No raw Wilbers Dataverse files or Eyal ModelDB archive bytes were obtained, hashed or replayed.
- No conductance values were assigned to AMSN runtime parameters.
- Existing CI runs on PR #8 remain queued at the last inspection; see the handoff for exact IDs.

## Limitations

- Wilbers conductance measurements are from somatic nucleated patches, not the AIS or axon.
- The cohort consists of neurosurgical human tissue; source context includes deeper pathology and cortical regions. It is not a population-wide healthy control reference.
- The voltage-dependence table is uncorrected for a 15 mV liquid-junction potential.
- The Table S1 slope-factor unit label in the thesis extraction is dimensionally suspect, so slope factors are not marked runtime-ready.
- The Wilbers single-compartment HH gbar values and Eyal compartment-specific densities are model-derived, not direct measurements.
- The original model equations and raw data must be retrieved and reproduced before implementation.

## Files added

- `amsn-core/research/references/human_nav_kv_evidence_2023.json`
- `amsn-core/research/HUMAN_SOMATIC_NAV_KV_EVIDENCE_BASELINE_2026-11-22.md`
- `amsn-core/tests/test_human_channel_evidence_registry.py`
- `HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md`

## Next concrete experiment

Retrieve and hash the Wilbers DataverseNL archive; reconstruct the original human Na+ and K+ equations and reproduce the published voltage-clamp command protocols before building a separate opt-in human somatic channel mechanism. Only after single-cell traces and channel kinetics pass should an independently justified spatial distribution be explored.
