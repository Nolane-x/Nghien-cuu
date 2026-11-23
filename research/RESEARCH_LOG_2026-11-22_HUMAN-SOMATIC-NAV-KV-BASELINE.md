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


## Dataverse v3 / original NMODL source audit — 22/11/2026

- Official DataverseNL API verified DOI 10.34894/L5J0SD, released v3.0, CC0-1.0, 65 files.
- Selected Na/K mechanisms, human fitting drivers and supporting Python tools were read from public object-store downloads and SHA-256 hashed. The file manifest records IDs, bytes, official SHA-1 and observed SHA-256.
- Na mechanism: m/h states, m^3h conductance, 25 C reference, Q10=2.3, active TABLE lookup. Its script's final parameter dictionary agrees with distributed MOD.
- K mechanism: m/h1/h2 states, mixed fast/slow/non-inactivating populations, 34 C reference, Q10=2.3. Intermediate fit values match the MOD, but the later final-best-fit dictionary differs on six inactivation parameters; no snapshot is selected.
- Separate current-clamp MOD variants add human-fraction conductance scaling; they are not byte-identical to the channel-comparison files.
- Current-clamp gbar fitting uses a 50:50 human/mouse median AP target; it is not a human-only fit. K recovery fitting also uses a human/mouse average target.
- Both canonical MOD files contain a potential trap0 branch/limit mismatch. This is a source-level warning, not yet a proven NEURON failure.
- Raw spreadsheets and the 15.1 MB AP-clamp matrix were not downloaded. Selected source files were not vendored. Original mechanisms not compiled or executed; no pytest run is claimed; no runtime mechanism or default changed.

Files added:
- `amsn-core/research/references/wilbers2023_dataverse_source_manifest_2026-11-22.json`
- `amsn-core/research/references/wilbers2023_nmodl_mechanism_audit_2026-11-22.json`
- `amsn-core/research/WILBERS_2023_DATAVERSE_AND_NMODL_SOURCE_AUDIT_2026-11-22.md`

Next gate: compile original MOD files with pinned NEURON, probe trap0 around singular points, reproduce voltage clamp and AP-clamp traces, and resolve the K fit snapshot before implementing a distinct opt-in human somatic channel.


## Extended NMODL stable-reference comparison — 23/11/2026

- Workflow 45115543259 passed with 11 registry tests. The audit compiled unchanged source and a separate diagnostic clone with mathematically stable trap0 handling.
- Na: no non-finite values on 41 probe points; all fields matched the diagnostic clone at exported precision.
- K: three non-finite values at positive singular parameters; negative h1tau in the mirror region around -thi1 and at -thi2; 91.61% mtau discrepancy at -tha's mirror voltage.
- On 19 discrete Na and 17 discrete K command test-step voltages, original and diagnostic clone outputs matched at exported precision; this is only static initialization of rate variables, not a time-domain voltage-clamp or AP-clamp replay.
- No stable clone was promoted into runtime; raw workbooks/traces remain to be replayed.
