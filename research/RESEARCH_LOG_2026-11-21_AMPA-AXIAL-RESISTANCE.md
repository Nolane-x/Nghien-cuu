# Research log — 2026-11-21 — matched-support axial resistance

**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** 56a731c156db32f6beb35b813e177039d739a850  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391  
**Report:** amsn-core/research/HUMAN_AMPA_AXIAL_RESISTANCE_AUDIT_2026-11-21.md

## Research question

Does the residual in the human-morphology AMPA comparison plausibly arise from a mismatch in the axial resistance geometry over the same local control-volume support?

## Hypothesis

If AMSN and NEURON use the same tapered cable geometry over the same incoming/outgoing half-edge support, their axial geometry factors should agree closely. A material discrepancy would indicate a geometry/discretization issue to investigate before changing solver parameters.

## Sources examined

- Repository instructions: AGENTS.md, HANDOFF.md, HANDOFF_2026-11-20_AMPA-PROBE-INTERPOLATION-AREA.md, HANDOFF_2026-11-20_AMPA-SYNAPTIC-TIMING-FINAL.md, AMSN research dossier and previous matched-area report.
- Human morphology: NMO_290988 / 1094_Mohan_etal_2015.CNG.swc and provenance metadata (CC BY 4.0).
- NEURON 9.0.2 source: https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/treeset.cpp (nrn_area_ri, diam_from_list and ri implementation).
- NEURON documentation: https://www.neuronsimulator.org/en/latest/progref/modelspec/programmatic/topology/geometry.html

## Work completed

1. Added amsn-core/examples/human_ampa_axial_resistance_audit.py.
2. Added .github/workflows/amsn-ampa-axial-resistance-audit.yml.
3. The audit preserves two prior basal sites and selects one additional basal and two apical internal/unbranched sites.
4. For each site, it integrates incoming and outgoing AMSN half-edge taper factors separately, integrates the same NEURON pt3d support directly, and independently reconstructs the support from actual adjacent segment.ri() values plus endpoint caps.
5. Added deterministic analytical checks for cylindrical units, taper partition additivity and direction symmetry.
6. Committed the code and workflow on main; read back both files and verified their blob SHAs.
7. Preserved all 15 raw result rows in amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv and wrote a standalone report and handoff.

## Commands and environment actually run

GitHub Actions workflow run 44870476391:
- Runner: Ubuntu 26.04.1.
- Python: CPython 3.12.16.
- NumPy: 2.5.5.
- NEURON: 9.0.2.
- NEURON segmentation: max 0.5 um, 25,233 segments.
- Install: python -m pip install -e ".[test]"
- Install reference: python -m pip install --only-binary=neuron "neuron==9.0.2"
- Run: python examples/human_ampa_axial_resistance_audit.py
- Workflow conclusion: success; all steps completed successfully.
- Artifact uploaded: 14693647848.

## Results

- 15 rows: five sites across three AMSN frequencies.
- AMSN mesh sizes: 2,540 / 3,525 / 4,287 compartments at 2,000 / 4,000 / 6,000 Hz.
- Maximum absolute relative factor difference between AMSN and NEURON: 0.00023967596732%, at apical q90 (SWC 4665) on 2,000 Hz.
- At 6,000 Hz the apical q90 difference magnitude is 0.000128834149842%.
- Maximum NEURON segment.ri() versus pt3d segment-integral mismatch: 5.7432610218e-12%.
- Maximum NEURON network reconstruction versus direct support integral mismatch: 6.07299914906e-13%.
- Maximum support-length mapping mismatch: 4.64308609684e-13%.
- All 15 rows passed the audit's internal consistency gates.

## Interpretation and uncertainty

This locally reproduced geometry result makes a large local axial taper-integral discrepancy unlikely at the five selected unbranched sites under this exact mapping and NEURON version. It does not validate branch junctions, soma/terminal handling, the full global cable matrix, synaptic dynamics or biology. The tiny apical q90 residual has not been independently attributed to importer precision, mapping or any single numerical source.

The audit thresholds are internal numerical consistency checks, not experimentally justified biological tolerances.

## Files created

- amsn-core/examples/human_ampa_axial_resistance_audit.py
- .github/workflows/amsn-ampa-axial-resistance-audit.yml
- amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv
- amsn-core/research/HUMAN_AMPA_AXIAL_RESISTANCE_AUDIT_2026-11-21.md
- HANDOFF_2026-11-21_AMPA-AXIAL-RESISTANCE.md
- research/RESEARCH_LOG_2026-11-21_AMPA-AXIAL-RESISTANCE.md

## Next experiment

Audit the entire tree's axial edge and junction conductances, explicitly handling branchpoints, soma attachment, section joins and terminals. After that, reproduce the published Eyal et al. 2018 / ModelDB 238347 cell and mechanism baseline as a separate matched-source experiment.


## Comprehensive Core CI completion (recorded after run)

Workflow [44870476392](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476392) completed successfully on code commit `56a731c156db32f6beb35b813e177039d739a850`: all 4 jobs green. Unit/numerical tests passed 65/65 on Python 3.12 and 65/65 on Python 3.13. Both jobs also compiled all Python modules and ran configured examples. Both NEURON cross-validation jobs completed all steps on Python 3.12/3.13. The dedicated axial audit workflow [44870476391](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391) also completed successfully.
