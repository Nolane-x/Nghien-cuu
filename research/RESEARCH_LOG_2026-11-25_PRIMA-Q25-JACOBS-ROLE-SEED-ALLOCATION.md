# Research log — Jacobs q25 role-specific seed allocation

**Date:** 25 November 2026  
**Repository:** Nolane-x/Nghien-cuu  
**Branch:** \`research/prima-q25-cross-morphology-boundary-replication-2026-11-25\`  
**Accepted workflow:** [45650388401](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401)  
**Result commit:** [bc0fa11dc136107d0cfee17ab14771f919dea81c](https://github.com/Nolane-x/Nghien-cuu/commit/bc0fa11dc136107d0cfee17ab14771f919dea81c)  
**Artifact:** [15041330718](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401/artifacts/15041330718)  
**Artifact ZIP SHA-256:** \`a510ff14720304c498ff0c5cc474a974fb7dcf483449af0afad37c864a37161a\`

## Work performed

- Pre-registered a Jacobs-only role-specific dual-seed experiment with ten schedules, nine passive scenarios, order224, seven unchanged input ports and nine measured output rows.
- Added a dedicated runner, three focused basis-contract tests and an independent GitHub Actions workflow.
- Isolated NEURON-dependent imports inside child workers, constructed canonical D0 before native full-Hines replay, and added the required NumPy SIMD dispatch preflight to make the run reproducible.
- Passed compile, 8/8 focused tests, morphology/SWC preflight, 9/9 workers, exact data read-back, global numerical gates, Git archival and artifact upload.

## Accepted coverage

- 9 workers; 9,720 case metrics; 1,620 scenario summaries; 180 pooled summaries; 45 finite-record DFT identities; 90 basis metadata rows.
- D0 exactly matches production multishift PRIMA across all scenarios. Nominal D0 and BOTH_10K hashes and case metrics replay bit-for-bit against the prior accepted run.
- All models reached order224, retained seven input ports, and passed reduced G/C Cholesky. Maximum orthogonality error: 1.77636e-15.
- All 45 DFT identities passed tolerance 2e-8; maximum full-Hines relative residual 4.70924e-13 and reduced residual 3.61286e-13.

## Scientific result

The apical-only 0/1k/10k dual-seed hypothesis is not supported. Apical q25 scenario-median candidate/D0 ratios stay above one in both windows; each schedule improves only 2–3 of nine scenario medians. All seven shared-output pooled medians also worsen under APICAL-only schedules.

Basal q25 is much more responsive. BASAL_0 and BASAL_10K improve it in most scenarios. BOTH_10K gives the best pooled basal ratios (0.449 at 20ms, 0.464 at 40ms) while leaving apical q25 near-neutral (scenario-median ratios 1.035 and 1.049).

Apical D0 median NRMSE is only 8.85e-12% at 20ms and 1.15e-11% at 40ms. The resulting absolute apical error differences are tiny; relative ratios must not be treated as meaningful accuracy gains at this numerical floor. No production solver/default was changed.

## Detailed report and next step

Detailed analysis: [PRIMA_Q25_JACOBS_ROLE_SPECIFIC_SEED_ALLOCATION_RESULTS_2026-11-25.md](PRIMA_Q25_JACOBS_ROLE_SPECIFIC_SEED_ALLOCATION_RESULTS_2026-11-25.md).

Next research should not add apical seeds merely to chase ratios. First define a meaningful absolute error target/noise floor, then pre-register a larger-order or alternate error-functional experiment if apical readout accuracy remains a real requirement. Keep BOTH_10K as the best Jacobs-specific research compromise and BASAL_0/BASAL_10K as basal-focused candidates. Full Hines remains canonical.
