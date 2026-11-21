# Handoff — AMSN matched-support axial-resistance audit

**Date:** 2026-11-21 (UTC+7)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** main  
**Code commit:** 56a731c156db32f6beb35b813e177039d739a850  
**Audit workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391  
**Research report:** amsn-core/research/HUMAN_AMPA_AXIAL_RESISTANCE_AUDIT_2026-11-21.md  
**Raw CSV:** amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv  
**Research log:** research/RESEARCH_LOG_2026-11-21_AMPA-AXIAL-RESISTANCE.md

## Start here

1. Read AGENTS.md and HANDOFF.md; GitHub main is the durable source of truth.
2. Read this checkpoint and the full audit report above.
3. For previous AMPA baselines, read HANDOFF_2026-11-20_AMPA-PROBE-INTERPOLATION-AREA.md and HANDOFF_2026-11-20_AMPA-SYNAPTIC-TIMING-FINAL.md.
4. Inspect current main head and CI before changing code. The audit code is in commit 56a731c156db32f6beb35b813e177039d739a850.
5. Do not change Ri, AMPA kinetics or solver semantics merely to reduce an unexplained voltage mismatch.

## What was added

- `amsn-core/examples/human_ampa_axial_resistance_audit.py`: matched-support axial geometry audit.
- `.github/workflows/amsn-ampa-axial-resistance-audit.yml`: NEURON 9.0.2 CI job and artifact preservation.
- `amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv`: 15 raw rows copied from successful workflow output.
- `amsn-core/research/HUMAN_AMPA_AXIAL_RESISTANCE_AUDIT_2026-11-21.md`: methods, tables, interpretation and limits.

## Verified result

Workflow 44870476391 completed successfully on Ubuntu 26.04.1, Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2.

The run used a 0.5-um NEURON maximum segment length (25,233 segments), and five sites:
- basal q75 source, SWC 3784, dend[54];
- basal q90, SWC 3814, dend[54];
- other basal branch q75, SWC 2986, dend[42];
- apical q75, SWC 5078, apic[20];
- apical q90, SWC 4665, apic[17].

The five sites were checked at AMSN reference frequencies 2,000/4,000/6,000 Hz (2,540/3,525/4,287 compartments), yielding 15 rows.

- Maximum AMSN vs NEURON axial-factor difference: 0.00023967596732% (apical q90, 2,000 Hz).
- Maximum actual NEURON `segment.ri()` vs its pt3d centre-to-centre integral: 5.7432610218e-12%.
- Maximum NEURON network reconstruction vs direct support integral: 6.07299914906e-13%.
- Maximum support-length mapping mismatch: 4.64308609684e-13%.
- All checks passed. The workflow artifact is 14693647848.

This is a local geometry/numerics result for five unbranched supports in one partial morphology. It is not biological validation; it does not cover branchpoints, soma, section joins, terminals or the full global cable matrix. The tiny apical q90 difference has no separately isolated cause.

## Next work — strict order

1. **Full tree axial network audit.** Compare every AMSN electrical edge against the corresponding NEURON parent-child conductance, including the two half-segment contributions, branchpoints, soma attachment, section joins and terminals. Keep exact mapping/provenance and report unsupported connections explicitly. Do not skip difficult edges silently.
2. **Voltage impact test.** Once the full resistance network comparison is understood, revisit the fast-AMPA source/probe waveform using unchanged parameters and timing. Attribute any changes to a measured cause.
3. **Published reference reproduction.** Reproduce the Eyal et al. 2018 / ModelDB 238347 neuron with its own morphology and mechanisms. Keep that source-matched reproduction separate from the NMO_290988 engineering fixture.
4. **Only after baseline stability:** add calibrated NMDA Mg²⁺ block, then calcium/signalling/plasticity. Preserve source ranges and uncertainty; do not leap to whole-genome or multi-neuron intelligence claims.

## CI state and final verification

Both workflows are now confirmed successful for code commit `56a731c156db32f6beb35b813e177039d739a850`:

- Dedicated matched-support axial audit: [44870476391](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391), 1/1 job successful.
- Comprehensive AMSN Core CI: [44870476392](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476392), 4/4 jobs successful.
- Unit/numerical tests: 65 passed under Python 3.12 and 65 passed under Python 3.13.
- Both matrix jobs compiled all Python modules and ran the configured examples.
- Both NEURON 9.0.2 cross-validation jobs completed all steps, including transient, AMPA, Exp2Syn timing and single-compartment voltage/current checks.

The audit's geometry conclusions remain local to the five tested unbranched supports in one partial morphology. Do not expand them into a biological validation claim.
