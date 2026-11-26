# HANDOFF — Nolane-x Research

## Four-morphology role-specific q25 seed sweep — running

- Pre-registered protocol: [PRIMA_Q25_FOUR_MORPHOLOGY_ROLE_SPECIFIC_SEED_SWEEP_PROTOCOL_2026-11-26.md](research/PRIMA_Q25_FOUR_MORPHOLOGY_ROLE_SPECIFIC_SEED_SWEEP_PROTOCOL_2026-11-26.md).
- Dedicated runner: [run_prima_q25_four_morphology_role_specific_q25_seed_sweep.py](research/run_prima_q25_four_morphology_role_specific_q25_seed_sweep.py); focused tests: [test_prima_q25_four_morphology_role_specific_q25_seed_sweep.py](research/test_prima_q25_four_morphology_role_specific_q25_seed_sweep.py).
- Current workflow [45760007155](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45760007155), head `831d0892e587b9c5a51f6347b54ba5d155ac157f`, is in the numerical sweep step. Source preflights, pinned runtime, NumPy SIMD preflight, compile and 11/11 focused tests passed. No cross-morphology numerical result has been accepted yet.
- Four predeclared schedules: D0_none, BASAL_10K, APICAL_10K and BOTH_10K. Fixed basis order224, seven original input ports, nine observed rows, four individual morphologies × nine passive scenarios.
- Expected coverage: 36 workers, 15,552 case rows, 2,592 group summaries, 288 morphology summaries, 648 scenario summaries, 72 pooled summaries, 144 finite-DFT identities and 144 basis metadata rows.
- The first attempt [45759776685](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45759776685) failed in the first Peng worker with native exit -11 before any stage log. The runner was revised to construct the canonical D0 model before full-Hines and to emit stage markers around NEURON import, layout, D0 and Hines. The current run is the first replay with these diagnostics.
- Keep full Hines canonical and do not promote any role-specific seed to a production default. The study remains passive linear-RC numerical evidence, not biological validation.


## Session continuation update — 25 November 2026

This update supersedes older status statements below when they refer to the same workflow or result. Earlier checkpoint sections are retained as historical records.


### Jacobs q25 role-specific output-dual seed allocation — accepted

- Canonical workflow [45650388401](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401) completed **success** through calculation, full verification, Git archival and artifact upload.
- Result archive commit: [bc0fa11dc136107d0cfee17ab14771f919dea81c](https://github.com/Nolane-x/Nghien-cuu/commit/bc0fa11dc136107d0cfee17ab14771f919dea81c).
- Artifact [15041330718](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45650388401/artifacts/15041330718), 254,430 bytes; ZIP SHA-256 \`a510ff14720304c498ff0c5cc474a974fb7dcf483449af0afad37c864a37161a\`.
- Scope: Jacobs NMO_03524 only; nine passive scenarios; ten predeclared role-specific dual-seed schedules; order224; seven fixed input ports and nine output rows.
- Exact coverage: 9/9 workers; 9,720 case metrics; 1,620 scenario summaries; 180 pooled summaries; 45/45 finite-DFT identities; 90 basis metadata; no duplicate case keys.
- D0 matched production multishift PRIMA in all scenarios. Nominal D0 and BOTH_10K matrices and case metrics replayed bit-exactly against the prior accepted study. All G/C Cholesky checks passed, maximum basis orthogonality error 1.77636e-15, maximum full-Hines DFT residual 4.70924e-13 and reduced residual 3.61286e-13.
- Main result: APICAL-only seeds at 0/1k/10k do not fix apical q25; their scenario-median error ratios remain above 1 and all seven shared-output medians worsen. Apical D0 NRMSE is already near \(10^{-11}\%\), so relative ratios are numerically fragile.
- Basal q25 improves with BASAL_0 and BASAL_10K. BOTH_10K is the best current Jacobs-specific research compromise: pooled basal ratios 0.449/0.464 (20/40 ms), apical scenario-median ratios 1.035/1.049 (near-neutral), and the strongest shared-output profile.
- Detailed report: [PRIMA_Q25_JACOBS_ROLE_SPECIFIC_SEED_ALLOCATION_RESULTS_2026-11-25.md](research/PRIMA_Q25_JACOBS_ROLE_SPECIFIC_SEED_ALLOCATION_RESULTS_2026-11-25.md). Research log: [RESEARCH_LOG_2026-11-25_PRIMA-Q25-JACOBS-ROLE-SEED-ALLOCATION.md](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-JACOBS-ROLE-SEED-ALLOCATION.md).
- Limits: one human control reconstruction, passive linear-RC only; no biological-population inference. Full Hines remains canonical; no production solver/default changed.


### Newly verified four-morphology finite-window decomposition

- Accepted run: [45571400424](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45571400424); results commit: [14fd51e6ade9d9cae359c9077f55174e3d0347f7](https://github.com/Nolane-x/Nghien-cuu/commit/14fd51e6ade9d9cae359c9077f55174e3d0347f7).
- Report: [PRIMA_Q25_FOUR_MORPHOLOGY_BOUNDARY_RESULTS_2026-11-25.md](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_BOUNDARY_RESULTS_2026-11-25.md).
- All source checksums, four morphology preflights, focused tests, exact CSV read-back counts, and finite-record DFT identity passed. Coverage: 537,768 frequency rows, 6,048 case metrics, 3,024 paired 9/7 comparisons, 48 source/window summaries, 8 morphology/window summaries and 864 finite-DFT identity rows. Maximum relative identity residual was 8.9204e-12 against the 2e-8 gate.
- Median 9-port/7-port error ratios (six source × pulse groups per morphology/window) show the effect is morphology-dependent:

| Morphology | Window | Continuous AC | Discrete BE | Absolute-voltage transient | Perturbation transient |
|---|---:|---:|---:|---:|---:|
| Jacobs human Control | 20 ms | 4.073 | 1.002 | 0.9999 | 0.9657 |
| Jacobs human Control | 40 ms | 4.094 | 1.004 | 0.9999 | 0.9819 |
| Tamas human Control | 20 ms | 13.263 | 32.169 | 0.9963 | 25.692 |
| Tamas human Control | 40 ms | 13.499 | 27.824 | 1.0001 | 49.921 |
| Allen human epilepsy specimen | 20 ms | 2.577 | 2.560 | 1.0002 | 4.502 |
| Allen human epilepsy specimen | 40 ms | 2.577 | 2.191 | 1.0001 | 3.409 |
| Peng mouse Control | 20 ms | 37.212 | 38.668 | 17.432 | 135.135 |
| Peng mouse Control | 40 ms | 31.153 | 32.866 | 27.046 | 59.814 |

Both transient coordinate conventions must remain in reports. The ratio is not absolute biological error and can be inflated by a very small seven-port denominator. Keep the four reconstructions as separate strata; Allen is an epilepsy-surgery specimen, and Peng metadata says No Diameter. The result is limited to passive linear-RC numerical reduction, not active-neuron or biological-population validation. Full Hines remains canonical.

### Strict full-dispatch four-layout replay — accepted

- [Run 45616046681](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681) completed **success**: full four-morphology 7/8/8/9-port order-168 calculation, exact CSV read-back, finite-DFT identity, Git archival and artifact upload all passed.
- Coverage: 1,075,536 frequency rows; 12,096 case metrics; 9,072 matched comparisons; 144 source/layout/window summaries; 24 morphology/layout/window summaries; 1,728 finite-DFT identity rows. Maximum identity residual 8.78149e-12 against 2e-8.
- Artifact [15027292605](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681/artifacts/15027292605), 70,254,593 bytes; ZIP SHA-256 4171ef306c4e53a4f5ec0637883c33243d0f36294c80ff093753ec070ca0c8ab. Results commit 2326ea077c3c6821ba427aef9b009b655e052cfe.
- Compared with the previously archived report at commit 27c3e6668a34c4ea97de4cde5412602d896fb0dc, all 144 basis/G/C/input hash records match, and five tracked numerical CSV Git blobs are identical. The current report captures different runner CPU-feature availability and runtime metadata, not changed matrices. This is strong replay evidence for these pinned conditions, not a universal all-hardware reproducibility claim.
- Paired post-analysis is marked passed: 3,024 matched case keys, 336 interaction summaries, 168 morphology summaries and 1,008 source summaries. Inputs match the archived primary-matrix hashes.
- Detailed report: [PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_STRICT_DISPATCH_REPLAY_2026-11-25.md](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_STRICT_DISPATCH_REPLAY_2026-11-25.md). Run-specific artifact manifest: [prima_q25_four_morphology_four_layout_strict_dispatch_replay_2026-11-25_manifest.json](amsn-core/results/prima_q25_four_morphology_four_layout_strict_dispatch_replay_2026-11-25_manifest.json). Research log: [RESEARCH_LOG_2026-11-25_PRIMA-Q25-STRICT-DISPATCH-FOUR-LAYOUT-REPLAY.md](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-STRICT-DISPATCH-FOUR-LAYOUT-REPLAY.md).

### Q25 output-observer — corrected workflow success and official archive

- Original run [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599) completed the full observer numerical analysis successfully. The job failed only in the later Git archival step; artifact preservation succeeded.
- Artifact [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308) was downloaded and its ZIP SHA-256 independently recomputed: `2391661263ef1c959d550e8a336c8fed89e1f1dfcc626ddab16b3db60bed8aa3`. Exact extracted CSV/report checksums and row counts are in [the recovery manifest](amsn-core/results/prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25_recovery_manifest.json).
- The observer JSON declares **passed**, matches **144/144** primary basis/G/C/input hashes, and records max finite-DFT identity relative error `5.386622461553216e-12` against `2e-8`. Coverage: 3,456 case rows; 2,592 paired comparisons; 2,016 source summaries; 336 morphology summaries; 3,456 finite-DFT identity rows.
- Scientific result: a q25 output can be evaluated from a full-compartment basis row without adding it to the retained input selector B. Retaining that q25 node often sharply improves its own readout versus the seven-port observer-only basis (especially Tamas, Allen and Peng), while leaving the other q25 node observation-only can increase its error. Retaining both q25 nodes can recover both outputs relative to the seven-port baseline, but the second retained q25 can worsen the first q25 output compared with its single-port basis. The effect is morphology-dependent; Jacobs apical is a notable near-neutral exception.
- Ratios must be read with absolute deltas; a low seven-port q25 baseline error can make relative ratios unstable. The result remains passive linear-RC numerical evidence from four individual reconstructions, not biological validation.
- Detailed analysis: [PRIMA_Q25_Q25_OUTPUT_OBSERVER_FIXED_VS_ENRICHED_BASIS_RESULTS_2026-11-25.md](amsn-core/research/PRIMA_Q25_Q25_OUTPUT_OBSERVER_FIXED_VS_ENRICHED_BASIS_RESULTS_2026-11-25.md). Recovery manifest: [prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25_recovery_manifest.json](amsn-core/results/prima_q25_q25_output_observer_fixed_vs_enriched_basis_2026-11-25_recovery_manifest.json). Research log: [RESEARCH_LOG_2026-11-25_PRIMA-Q25-OUTPUT-OBSERVER-RECOVERY.md](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-OUTPUT-OBSERVER-RECOVERY.md).
- Corrected workflow [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575) is now **complete success** through analysis, Git archival and artifact upload. Results commit: `8f971b74807ec715cff2f4db39ebc9db7398cf32`; artifact [15032389094](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575/artifacts/15032389094), 1,441,661 bytes, SHA-256 `8c82e3a4c43eabe98e95e482749ccf3f7af7a1c7145ba2ecf39f6f1e9a00f4d1`. All six numerical CSVs are byte-identical to the recovered original artifact; corrected report Git blob `09c03edbce0cbb0661c2507cef3abcfdd308ce74`. Use the corrected artifact as the official branch archive; retain the original 15027601308 only as independent recovery evidence.

### Basis-order convergence 112/168/224 — accepted and archived

- Canonical run [45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400) completed **success**, including numerical calculation, exact CSV read-back, Git result commit and artifact upload.
- Result archive commit: `09d65210d081ad3acecb6bcb0ff8bf34ffa8b04a`.
- Artifact [15031057886](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400/artifacts/15031057886), 134,290,729 bytes; ZIP SHA-256 `3eb04bf772ef93f90facac5cf4ea7b4f126f37bfbab12dd4acf81b377b79e65e`.
- Orders 112, 168 and 224 all passed. Order168 is the accepted strict reference; orders112 and224 were independently recomputed in child Python/NEURON processes.
- Per-order coverage: 1,075,536 frequency rows; 12,096 cases; 9,072 matched comparisons; 144 source/layout/window summaries; 24 morphology/layout/window summaries; 1,728 finite-DFT identity rows. Posthoc: 336 interaction,168 morphology,1,008 source summaries per order.
- Maximum finite-DFT identity residuals: order112 8.74381e-12; order168 8.78149e-12; order224 8.75736e-12 (tolerance2e-8). Maximum basis orthogonality error1.77636e-15; 144 unique basis hashes per order.
- Key result: order224 nearly removes the combined-q25 transient penalty in Tamas (ratios1.004/1.016) and Allen (1.043/1.043), brings Jacobs below/near1 (0.944/0.894), but Peng retains1.947/3.745 despite very small absolute error increases. Periodic-BE and finite-window transient metrics remain different estimands.
- Detailed report: [PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_BASIS_ORDER_SWEEP_RESULTS_2026-11-25.md](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_BASIS_ORDER_SWEEP_RESULTS_2026-11-25.md).
- Run manifest: [prima_q25_four_morphology_four_layout_basis_order_sweep_2026-11-25_manifest.json](amsn-core/results/prima_q25_four_morphology_four_layout_basis_order_sweep_2026-11-25_manifest.json).
- Research log: [RESEARCH_LOG_2026-11-25_PRIMA-Q25-BASIS-ORDER-CONVERGENCE.md](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-BASIS-ORDER-CONVERGENCE.md).

An overlapping rerun [45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005) completed calculation and artifact upload but its duplicate Git archive step failed with add/add rebase conflicts after the canonical result commit had already written the same paths. Its numerical CSVs and summaries match the canonical artifact; its conflict-marked report/time files are not accepted. Use run45616046400 as the canonical report and artifact.

### Research-only output-aware dual-seed prototype — focused CI passed

- Prototype: `amsn-core/research/experimental_prima_output_aware_basis.py`.
- Tests: `amsn-core/tests/test_prima_q25_output_aware_dual_seed_basis.py`.
- Protocol: [PRIMA_Q25_OUTPUT_AWARE_DUAL_SEED_BASIS_PROTOCOL_2026-11-25.md](amsn-core/research/PRIMA_Q25_OUTPUT_AWARE_DUAL_SEED_BASIS_PROTOCOL_2026-11-25.md).
- Workflow [45633147052](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45633147052) completed **success**: compileall passed and **5 tests passed**.
- Tests verify exact D0 parity with production multishift PRIMA when no dual seeds are added; q25 dual resolvent vectors enter the state basis while the input selector remains the original retained ports; q25 observation rows are separate; reduced G/C remain Cholesky-positive; basis orthogonality and input/index/frequency contracts pass.
- The five-test implementation milestone preceded the successful Peng pilot. The prototype now has a full single-morphology nominal-scenario numerical result (see the accepted pilot report below); cross-morphology/nine-scenario robustness is still untested. Production `src/amsn/prima.py`, solver behavior and defaults remain unchanged.

### Peng output-aware dual-seed pilot — accepted and archived

- Research-only prototype `amsn-core/research/experimental_prima_output_aware_basis.py`; focused tests `amsn-core/tests/test_prima_q25_output_aware_dual_seed_basis.py`; [protocol](amsn-core/research/PRIMA_Q25_OUTPUT_AWARE_DUAL_SEED_BASIS_PROTOCOL_2026-11-25.md).
- Focused CI [45633147052](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45633147052) passed: compileall and 5 tests, including bitwise D0 parity on a toy fixture, fixed input selector, separate output rows, positive-definite projected G/C and orthogonality.
- Added Peng NMO_163775 order-224 pilot runner `amsn-core/research/run_prima_q25_peng_output_aware_dual_seed_pilot.py` and workflow `.github/workflows/amsn-prima-q25-peng-output-aware-dual-seed-pilot.yml`. Five schedules: D0 none; D1-low 0 Hz; D1-mid 1,000 Hz; D1-high 10,000 Hz; D2-mid-high 1,000/10,000 Hz. B remains the original seven input ports; all seven shared outputs and both q25 outputs are measured.
- Canonical run [45636631081](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081) completed **success** through computation, exact 540-case/90-summary read-back, result commit and artifact upload. Results commit `22ba7b6994c871d3784f5abf15a2fe9311abe60d`; artifact [15033336785](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636631081/artifacts/15033336785), 77,205 bytes, ZIP SHA-256 `a19c928f99eb361300a6f5c8e793550e3cc1854dd177ed4739271ba459d5a95b`.
- All five schedules reached order224. Exact D0 parity against the production multishift basis was asserted; seven input ports remained unchanged; all reduced G/C Cholesky checks passed; max basis orthogonality error was 1.55e-15. D0 and D2 finite-record BE DFT identity checks passed at 1,601 bins with max relative residuals 1.10e-13 and 2.25e-13 (tolerance2e-8).
- Dual seeds improved both q25 outputs in **24/24 paired cases per schedule**. Pooled q25 median NRMSE fell from 5.16e-7% under D0 to 9.92e-12%–2.08e-11%. The seven shared outputs remain around 1e-11% absolute NRMSE; their relative ratios move because D0 is near the numerical floor. See detailed report [PRIMA_Q25_PENG_OUTPUT_AWARE_DUAL_SEED_PILOT_RESULTS_2026-11-25.md](amsn-core/research/PRIMA_Q25_PENG_OUTPUT_AWARE_DUAL_SEED_PILOT_RESULTS_2026-11-25.md), manifest [prima_q25_peng_output_aware_dual_seed_pilot_order224_2026-11-25_manifest.json](amsn-core/results/prima_q25_peng_output_aware_dual_seed_pilot_order224_2026-11-25_manifest.json), and [research log](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-PENG-OUTPUT-AWARE-DUAL-SEED-PILOT.md).
- Overlapping run [45636849975](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45636849975) also passed calculation/coverage but failed only during duplicate Git add/add rebase conflicts on report/time after the canonical result had committed those paths. It uploaded no artifact; 45636631081 is canonical.
- This remains a single-morphology, nominal-scenario proof of concept. No production solver/default change and no biological inference.

### Four-morphology, nine-scenario output-aware dual-seed sweep — accepted and archived

- Runner: `amsn-core/research/run_prima_q25_four_morphology_output_aware_dual_seed_sweep.py`.
- Protocol: [PRIMA_Q25_FOUR_MORPHOLOGY_OUTPUT_AWARE_DUAL_SEED_SWEEP_PROTOCOL_2026-11-25.md](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_OUTPUT_AWARE_DUAL_SEED_SWEEP_PROTOCOL_2026-11-25.md).
- Canonical workflow [45639939767](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767) completed **success** through all 36 workers, exact read-back, DFT identity checks, Git commit and artifact upload.
- Results commit: `fe048f52d376e3d5269f80d0009eefafd01e1565`; artifact [15035937283](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45639939767/artifacts/15035937283), 527,486 bytes; ZIP SHA-256 `fe798929f805f3702c89a704e42e4567a9371c456bc8baf71c8d9a76f7791f84`.
- Exact coverage: 19,440 case rows; 3,240 group summaries; 360 morphology summaries; 810 scenario summaries; 90 pooled summaries; 72/72 finite-DFT identities; 180 basis metadata rows. No duplicate case keys. All four morphology preflights/checksums passed.
- All 180 models reached order224, retained exactly seven input ports, passed reduced G/C Cholesky checks and D0 exact parity. Maximum basis orthogonality error: 1.776e-15. Maximum full-Hines/reduced finite-DFT relative residuals: 3.286e-12 / 3.261e-13 against 2e-8.
- Aggregate q25 results: D1-high (10 kHz) median paired ratio 0.00421, P90 0.904, and 790/864 paired cases improved. D1-mid had the smallest shared-output median ratio increase (1.0086) but weaker q25 median (0.00985). D2 had no aggregate benefit over D1-high sufficient to justify more seed directions.
- Morphology exception: D1-high improved q25 in every Tamas, Allen and Peng case (216/216 each); Jacobs improved 142/216 only. Jacobs apical-q25 is often near the numerical floor and can worsen; do not claim a universal improvement.
- Seven shared outputs remain near 1e-11% absolute NRMSE. Relative ratios can move on this near-zero baseline; report absolute deltas. D1-high shared-output median ratio is 1.0098; D1-mid 1.0086.
- Detailed report: [PRIMA_Q25_FOUR_MORPHOLOGY_OUTPUT_AWARE_DUAL_SEED_SWEEP_RESULTS_2026-11-25.md](research/PRIMA_Q25_FOUR_MORPHOLOGY_OUTPUT_AWARE_DUAL_SEED_SWEEP_RESULTS_2026-11-25.md). Manifest: [prima_q25_four_morphology_output_aware_dual_seed_order224_2026-11-25_manifest.json](amsn-core/results/prima_q25_four_morphology_output_aware_dual_seed_order224_2026-11-25_manifest.json). Protocol and runner remain under `amsn-core/research/`. Research log: [RESEARCH_LOG_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-OUTPUT-AWARE-DUAL-SEED.md](research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-OUTPUT-AWARE-DUAL-SEED.md).
- An overlapping push-triggered duplicate run [45641197995](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45641197995) started from an older documentation commit and is separate from the accepted result. Treat run45639939767 and commit fe048f5 as canonical; reconcile the duplicate only if it completes, without replacing the accepted files.
- This remains passive linear-RC evidence on four individual reconstructions, not a biological-population result. Full Hines and all production defaults remain unchanged.

### Output-observer CI archival correction

- Original observer run [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599) passed runtime/dispatch, source checksum, regression tests, primary-reference gate and the numerical observer calculation (report status passed; reported run time 2,512.57 s). Artifact [15027601308](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599/artifacts/15027601308) uploaded successfully.
- Its overall Actions failure occurred only at Git archival: job-level working directory amsn-core was active, but git add incorrectly used amsn-core/results/..., resolving to a nonexistent nested path.
- Fixed only .github/workflows/amsn-prima-q25-output-observer.yml: archival paths are now relative results/.... Fix commit: 707acd4fcb0ba8daf10a42930e60f5f3bbd16bf3; the changed workflow was fetched back and its new blob SHA verified as 52d1c4ab8e10069431f92882a46e70515287ac5a.
- Dated diagnosis: [research/RESEARCH_LOG_2026-11-25_AI-CI-PATH-AUDIT.md](research/RESEARCH_LOG_2026-11-25_AI-CI-PATH-AUDIT.md).
- Corrected push-triggered run [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575) is now **completed success**: the fixed relative `results/...` paths worked, Git archival succeeded, and the fresh artifact uploaded. The original numerical CSVs and 144/144 primary basis-hash match are unchanged.

### Other downstream runs — last inspected status

- [Basis-order convergence 45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400) is now **accepted success** for orders 112/168/224; see the result report and manifest above. The overlapping run45616919005 is a duplicate archive conflict, not the canonical result.
- [Four-morphology four-layout ablation 45616046681](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046681) is now **complete success**; full matrix, exact coverage/identity gates, archival commit and 70.25-MB evidence artifact are verified above.
- These are independent workflows. Do not infer completion from preflight gates; require full coverage, identity checks, report/CSV read-back, archival and artifact evidence.

### Current guardrails and next sequence

1. Keep the accepted observer, order-convergence, Peng pilot and four-morphology dual-seed sweep reports/manifests as canonical. The current full-sweep result is run45639939767 / commit fe048f5.
2. Continue with a targeted Jacobs apical-q25 investigation: compare basal-only, apical-only and paired dual-output seeds, using predeclared shifts and holdout passive scenarios. This is the main exception that prevents a universal D1-high recommendation.
3. Keep D1-high (10 kHz) and D1-mid (1 kHz) as explicit research candidates: D1-high is strongest for q25, D1-mid slightly minimizes shared-output median ratio/delta. Do not promote either to a production default.
4. Check the overlapping run45641197995 only as an additional replay; never replace the accepted canonical output files unless its numerical matrices are checksum-identical and its report/archive is clean.
5. Preserve seven input ports, congruent projection, D0 exact parity, G/C positivity, orthogonality, per-morphology/scenario summaries and DFT identity gates. Full Hines remains canonical; no active-neuron or biological-population claims are established.
6. Do not merge PR #33/#34 or change production solver/defaults without explicit authorization.

---

## Latest active checkpoint — PRIMA q25 four-morphology, seed-budget and isolated downstream replay (25/11/2026)

Continue from [the four-morphology handoff](HANDOFF_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-SEED-BUDGET.md), [the primary four-layout result](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FOUR_LAYOUT_ABLATION_RESULTS_2026-11-25.md) and [the seed-budget result](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_RESULTS_2026-11-25.md). Active branch: `research/prima-q25-cross-morphology-boundary-replication-2026-11-25`. Do not merge or change production defaults.

### Accepted numerical results

- [Four-layout primary run 45608561071](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071) completed **success** after about 39.5 minutes; result commit `1ccac2315a3580505474dbbd188dfc89ef884543`; artifact 15021668387. It passed the long calculation, coverage, DFT identity, commit and upload steps.
- Coverage: 3,201 master frequencies; 1,075,536 frequency rows; 12,096 case metrics; 9,072 candidate/seven comparisons; 144 source/layout/window summaries; 24 morphology/layout/window summaries; 1,728 finite-DFT identity rows. Maximum finite identity relative error \(8.78149\times10^{-12}\) against \(2\times10^{-8}\); maximum absolute residual \(4.80983\times10^{-11}\) V-samples. There are 144 distinct basis, projected-G and projected-C hashes.
- This 456085 matrix used the strict three-feature environment and verified Haswell OpenBLAS (one thread) plus active selected NumPy targets `X86_V3` and `baseline(X86_V2)`. It predates the unfiltered all-functions NumPy SIMD inventory, so keep it labelled as selected-kernel validated; the separate seed-budget run and fresh primary run below prove the all-functions preflight.
- [Initial six-shift seed-budget audit 45612672472](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472) completed **success**; result commit `f06e277165d6cd8929c152c2ddb2b6e537e4ccb1`; artifact 15021770119. It passed 8 tests and strict full-function NumPy dispatch. Coverage is 864 per-shift rows, 144 morphology/scenario/layout groups and 16 morphology/layout summaries in 31.62 seconds.
- Independent initial seed ranks for layouts `seven / eight_basal_q25 / eight_apical_q25 / nine_both_q25`: Jacobs 33/39/34/40; Tamas, Allen and Peng each 42/48/48/54. The count is after cross-shift orthogonalization and before later round-robin Krylov growth. Equal ranks but divergent response errors in Allen vs Tamas/Peng show this scalar seed count is not a complete explanation.

### Current unfinished runs

- [Fresh all-functions strict order-168 primary 45613803039](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039) passed runtime, unfiltered SIMD dispatch, four-layout tests, all q25 preflights, the 12,096/9,072/1,728 coverage gates and finite-DFT identity (max relative error 8.78149e-12). Its overall Actions conclusion is failure only because the later rebase conflicted in report.json and time.txt; full artifact 15023602612 uploaded successfully. See [full-dispatch rerun result](amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FULL_DISPATCH_RERUN_RESULTS_2026-11-25.md) and [machine-readable summary](amsn-core/results/prima_q25_four_morphology_full_dispatch_rerun_2026-11-25_summary.json).
- **Superseded:** the basis-order sweep is now accepted at [run 45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400), with orders112/168/224, exact read-back and archived artifact. See the new report and manifest near the top of this handoff. The later overlapping [run45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005) also completed its numerical matrix and artifact upload, but its duplicate Git archive rebase conflicted because the accepted run had already written those paths; its conflict-marked report/time files are not accepted.
- **Superseded:** original observer run [45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599) completed its numerical analysis with report status passed and artifact15027601308; its failure was only at Git archival. The recovered report/manifest and checksum evidence are documented near the top. Corrected run [45625185575](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45625185575) is the official successful Git archive. Independent replay [45616883949](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616883949) also completed its numerical calculation with report status passed and artifact15032804913; all six numerical CSVs are byte-identical to the official archive, while its duplicate Git archive rebase failed on report/time paths. It is additional reproducibility evidence, not another canonical commit.
- Older basis/observer runs with failure or pending status are retained in Actions history. Do not interpret them as current final results. In particular, the previous in-process basis sweep exited 139; the first observer attempts hit variable-order errors and then a native exit 139. These are recorded in the dated research log.

### Strict runtime

Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2, threadpoolctl 3.6.0; `OPENBLAS_CORETYPE=Haswell`, one BLAS thread; `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR`; active full-function NumPy targets are `X86_V3` and `baseline(X86_V2)`. The full-function check is executed in an isolated preflight process and its JSON target list is handed to the numerical process through `GITHUB_ENV`.

### Main files to read next

1. `research/RESEARCH_LOG_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-SEED-BUDGET.md`
2. `amsn-core/research/PRIMA_Q25_NUMERICAL_DISPATCH_REPRODUCIBILITY_AUDIT_2026-11-25.md`
3. `amsn-core/research/PRIMA_Q25_BASIS_ORDER_CONVERGENCE_PROTOCOL_2026-11-25.md`
4. `amsn-core/research/PRIMA_Q25_OUTPUT_OBSERVER_FIXED_VS_ENRICHED_BASIS_PROTOCOL_2026-11-25.md`

No active-neuron, synapse, plasticity, action-potential or biological-population claim is established. The four inputs are individual reconstructions; Allen NMO_162186 is an epilepsy-surgery specimen, and Peng NMO_163775 metadata says No Diameter. Full Hines remains canonical, and no production solver/default has changed.

---

## Latest validated checkpoint — PRIMA q25 short-window reproducibility (25/11/2026)

Continue from [short-window handoff](HANDOFF_2026-11-25_PRIMA-Q25-SHORT-WINDOW-DT00625.md) and [research report](amsn-core/research/PRIMA_Q25_SHORT_WINDOW_DT00625_2026-11-25.md). Active branch: `research/prima-q25-short-window-dt00625-2026-11-25`; [PR #33](https://github.com/Nolane-x/Nghien-cuu/pull/33) is draft/open and must not be merged without explicit authorization.

- [Workflow 45552298117](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45552298117) passed in two attempts: 20/20 tests, both morphology checksums/preflights, full short-window matrix, six exact CSV read-backs, commit and artifact upload.
- Same-commit reproducibility confirmed: **36/36 basis/model hashes**, **360/360 trace hashes**, and all six numerical CSVs are byte-identical. BLAS/OpenMP variables were pinned to one thread and `PYTHONHASHSEED=0`. Only runtime wall time/report metadata differs.
- Result commit `455b304a9f79c118196c6669c61fb4206a24375b`; artifacts 14994563122 and 14994278136.
- Median 9/7 ratios for dt 0.1/0.05/0.025/0.0125/0.00625 ms:
  - Tamas, 20 ms: 24.47/26.80/27.19/26.39/24.64×; 40 ms: 55.21/57.13/54.88/49.79/49.14×.
  - Peng, 20 ms: 138.26/128.38/123.56/119.50/114.77×; 40 ms: 70.09/67.67/64.52/65.31/65.06×.
- The short-window ratios are reproducible but still dt-dependent. Absolute nine-port NRMSE remains around (10^{-9}%)–(10^{-8}%). Full-Hines coarse-vs-0.00625-ms median errors fall from about 0.66–0.73% at dt 0.1 to 0.045–0.050% at dt 0.0125.
- Next: explain 20–40-ms residual variation by separating periodic-transfer and terminal-boundary components. Do not repeat a generic all-window timestep sweep. No production solver/default changed.

---

## Latest validated checkpoint — PRIMA q25 fine-step convergence (24/11/2026)

Continue from [fine-step handoff](HANDOFF_2026-11-24_PRIMA-Q25-BACKWARD-EULER-FINE-STEP-CONVERGENCE.md) and [research report](amsn-core/research/PRIMA_Q25_BACKWARD_EULER_FINE_STEP_CONVERGENCE_2026-11-24.md). Active branch: `research/prima-q25-backward-euler-fine-step-convergence-2026-11-24`; [PR #32](https://github.com/Nolane-x/Nghien-cuu/pull/32) is draft/open and must not be merged without explicit authorization.

- [Workflow 45428685906](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45428685906) passed 15/15 tests, both morphology checksums/preflights, full matrix, six exact CSV read-backs, result commit and artifact upload. Result commit `d79ca743cbb662bf4536b28c527bfa5234058c15`; artifact 14937828066.
- Coverage: 24,192 layout metrics; 12,096 paired 7/9 comparisons; 192 source summaries; 32 morphology × dt × window summaries; 9,072 Hines temporal rows; 24 Hines summary rows.
- Median 9/7 transient ratios at dt 0.1/0.05/0.025/0.0125 ms (20/40/100/200-ms windows):
  - Tamas: 24.44/55.24/31.87/31.64; 26.59/57.04/31.73/31.59; 27.05/54.85/31.72/31.59; 26.55/49.91/32.05/31.84×.
  - Peng: 138.24/70.09/33.67/33.43; 130.11/67.68/33.62/33.42; 123.68/63.89/33.64/33.46; 118.81/64.98/33.62/33.45×.
- At 100–200 ms, 9/7 ratios are stable within about 0.6% (Tamas) and 0.2% (Peng) across the full timestep grid. At 20–40 ms, variation remains, particularly Peng and Tamas at 40 ms.
- Against dt 0.0125 ms, full-Hines median NRMSE is ~0.63–0.68% at dt 0.1, ~0.265–0.296% at dt 0.05, and ~0.089–0.100% at dt 0.025. Adjacent error ratios 2.30–2.32 and 2.94–2.96 support first-order BE convergence.
- Next: target 20–40-ms windows at dt 0.00625 ms and separate periodic-transfer and terminal-boundary contributions. Long-window full-grid refinement has diminishing value. No production solver/default changed.

---


---

## Latest validated research checkpoint — exact PRIMA q25 backward-Euler transfer (24/11/2026)

Continue from [HANDOFF_2026-11-24_PRIMA-Q25-BACKWARD-EULER-DISCRETE-TRANSFER.md](HANDOFF_2026-11-24_PRIMA-Q25-BACKWARD-EULER-DISCRETE-TRANSFER.md). Active branch: `research/prima-q25-backward-euler-discrete-transfer-2026-11-24`; PR [#30](https://github.com/Nolane-x/Nghien-cuu/pull/30) is draft/open and must not be merged without explicit authorization.

- Exact backward-Euler transfer and finite-window terminal-state correction are implemented; discrete mapping \(s_{BE}=(1-e^{-j2\pi f\Delta t})/\Delta t\), with the \(x[N-1]\) boundary term retained.
- [Workflow 45420670698](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45420670698): 9/9 focused tests, both morphology checksums and preflights, full calculation, DFT identity gate, result commit and artifact upload passed. Maximum identity residual \(1.4290\times10^{-11}\) vs \(2\times10^{-8}\). Result commit `1d6f64a83ccc7d1310a19baa50b2bc9b738dd7f5`; artifact 14934013973.
- Important correction: Tamas' earlier ~1.00–1.03× nine/seven transient ratio was affected by cancellation in the absolute-voltage Hines replay. The stable perturbation-coordinate replay gives ~24.5× / 56.2× / 32.2× / 32.1× for 20/40/100/200 ms; Peng gives ~162.7× / 63.6× / 34.1× / 34.0×. Absolute NRMSE remains very small; see the full report and its explicit aggregation method.
- The eight-row morphology × window summary and regression test were validated in workflow 45422624509; exact result CSVs and the corrected Tamas interpretation are in the q25 discrete-transfer report.
- No production solver or default changed. Full Hines remains canonical; only two passive morphology instances are studied.

---


---

## Latest implementation checkpoint — PRIMA phase profiler (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md](HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`; profiler code checkpoint: `9050c6a075c12af564fa86c0e5c2b1ce1564eac4`.

- Added `amsn-core/examples/prima_phase_profile.py`, targeted tests in `amsn-core/tests/test_prima_phase_profile.py`, and `.github/workflows/amsn-prima-kernel-phase-profile.yml`.
- Profile scope: existing PRIMA shifted Hines solves, orthogonalization, congruence projection, orchestration; separate Python/native self-time; same-order unprofiled build reference; reduced frequency/transient solvers; full-Hines baseline in an independent process.
- The matrix is three morphology fixtures × orders84/112/168 × two profiled repeats, with a separate Hines process for each morphology.
- **Validation pending:** Actions [45034830634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45034830634) was queued at the last check. The targeted pytest command has not yet been observed passing; no profiler measurements have been accepted. See the new handoff for exact parameters and next actions.
- No production defaults or canonical Hines equations were changed. PR #8 remains draft/open.

---

## Latest implementation checkpoint — PRIMA phase profiler (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md](HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md). Latest implementation commit: `fb642cce096a1fb2920c5b30bbaf471c1dd2d3a0`.

- Added phase timing for the real PRIMA builder, unprofiled build reference, reduced solver timing and a separate full-Hines process baseline.
- Files: `amsn-core/examples/prima_phase_profile.py`, `amsn-core/tests/test_prima_phase_profile.py`, `.github/workflows/amsn-prima-kernel-phase-profile.yml`.
- Targeted workflow [45035222028](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222028) and Core CI [45035222163](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222163) were **queued** at the last inspection. No tests or profile results have been accepted as passing yet.
- Keep full Hines canonical and production defaults unchanged. PR #8 remains draft/open.

---

## Latest validated checkpoint — complete PRIMA resource benchmark (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md](HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`. Resource benchmark code head tested: `e556625b9f0b1f31f9c822e603cf0ae220eefe0f`.

- [Completed GitHub Actions run 45016243390](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45016243390): 37/37 jobs passed (one validator + 36 resource jobs); validator log: 16 tests passed.
- 36/36 artifact ZIPs downloaded; 36/36 SHA-256 digests match GitHub metadata. Matrix coverage 3 morphologies × 2 mesh caps × orders84/112/168 × 2 repeats = 36 unique conditions.
- 7,560 sweep rows checked: 1,080 frequency, 5,832 per-port transient, 648 aggregate transient; each artifact has 210 rows and exit status 0.
- Median process user CPU / peak RSS: order84 = 141.45 s / 268.16 MiB; order112 = 205.96 s / 277.29 MiB; order168 = 278.31 s / 300.76 MiB. State reductions: 99.3225%, 99.0967%, 98.6451%.
- Whole audit-process measurements only, not isolated PRIMA kernels. Seven runner CPU models mean wall time is not a controlled speed comparison. Full Hines remains canonical; production defaults unchanged.
- Complete report: [HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md](amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md). Raw per-run data, summaries, manifest, validation JSON and reproducer are linked in that report.

The preceding 12/36 resource note remains in the history below, but is superseded for resource status by this 36/36 verified run. PR #8 remains draft/open; do not merge or mark ready without explicit authorization.

---

## Previous validated checkpoint — PRIMA held-out morphology and port/order study (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-HELDOUT-AND-PORT-ORDER.md](HANDOFF_2026-11-22_PRIMA-HELDOUT-AND-PORT-ORDER.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`; validated code head: `5180f0bc72dbfad0a460b0870ca80fec772db0e3`.

- Held-out human L2–3 dendritic morphology NMO_162186: [workflow 45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648), 2/2 jobs pass. Exact SWC SHA-256 `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`; 7,287 records; dendrites complete and axon incomplete; epilepsy surgical specimen. PRIMA coverage 81/729/3,402 rows and all 81 G/C Cholesky checks passed.
- Equal-order 7-port/9-port: [workflow 45012282737](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282737), 12/12 pass. At order56/112, all 252 common-output pairs worsened when nine ports were retained. At order168, 138/252 worsened and 114/252 improved, median ratio 1.000001: practical parity, not a systematic improvement.
- Nine-port order capacity: [workflow 45012282650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282650), 6/6 pass. Maximum transient NRMSE falls from 12.10% (order28) to 0.5231% (56), 0.001775% (84), 3.447e-5% (112), 3.450e-6% (168). Order168's incremental value varies by morphology.
- Core CI [45012282476](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282476) 4/4 pass; enrichment [45012282496] 6/6; parameter robustness [45012282485] 3/3.
- Resource/RSS matrix [45012282723](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723): validator preflight passed; 12/36 resource artifacts for NMO_68174 have now been independently verified (two mesh caps × orders84/112/168 × two replicates, all SHA-256 matched and exit0). Other morphology jobs remain; full matrix incomplete. See [partial report](amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_PARTIAL_2026-11-22.md).

Full Hines remains canonical. No production defaults changed. All claims are limited to passive linear RC; ±20% parameter scenarios are deterministic stress tests, not biological distributions. PR #8 remains draft/open.

**Ngày checkpoint ban đầu:** 2026-11-20  
**Kho chuẩn:** https://github.com/Nolane-x/Nghien-cuu  
**Nghiên cứu đang bàn giao:** AMSN — Adaptive Multi-Scale Neuron  
**Phạm vi:** tài liệu này phản ánh snapshot ban đầu, không phải trạng thái repo mới nhất. Ở thời điểm snapshot, các thư mục nguồn AMSN Alpha cũ trống; sau đó AMSN Neuron Core đã được xây dựng lại từ đầu và có mã nguồn/test thật trong `amsn-core/`. Xem `HANDOFF_2026-11-20_MESH.md` để biết trạng thái mới nhất. Không coi code mới là recovery của Alpha cũ.

---

## 0. Chỉ dẫn bắt buộc cho AI/phiên mới

Trước khi làm bất cứ việc gì:

1. Đọc toàn bộ file này và checkpoint `HANDOFF_*.md` mới nhất.
2. Kiểm tra trạng thái branch/commit mới nhất; các mục lịch sử phía dưới có thể đã được supersede bởi handoff mới hơn.
3. Đọc `research/AMSN_RESEARCH_DOSSIER.md`.
3. Đọc `research/AMSN_RECOVERY_STATUS_2026-11-20.md` và phần mới nhất trong `research/RESEARCH_LOG.md`.
4. Kiểm tra trạng thái GitHub hiện tại (nhánh, commit mới nhất, files) trước khi ghi. Không giả định repo vẫn giống checkpoint.
5. Tiếp tục nghiên cứu và thực hiện thí nghiệm; không chỉ lặp lại kế hoạch cho người dùng. Sau mỗi phát hiện có giá trị, ghi lại vào repo trước khi kết thúc phiên.

**Không yêu cầu người dùng lặp lại mục tiêu đã ghi ở đây.** Người dùng muốn tiến hành nghiên cứu thật, không dừng ở lời hứa hay báo cáo kế hoạch. Khi có thể thực hiện một bước an toàn và hữu ích thì hãy làm luôn.

## 1. Mục tiêu dài hạn

Xây dựng và kiểm chứng một mô hình tính toán có độ trung thực sinh học cao cho một neuron thực, sau đó dùng các nguyên lý tính toán rút ra để thiết kế và đánh giá những kiến trúc AI mới.

Mục tiêu không phải tạo một mô hình “trông giống neuron”, cũng không phải nhồi mọi cơ chế vào một class Python. Mục tiêu là một **digital twin đa thang, có provenance, uncertainty, coupling đúng đơn vị và validation độc lập**.

Các lớp sinh học cần được nghiên cứu theo mức độ có bằng chứng:

- Hình thái: soma, axon initial segment, axon, basal/apical dendrite, branch, spine, synaptic bouton; về sau mới thêm ER, mitochondria, nucleus và extracellular geometry.
- Điện sinh học: cable equation, màng, điện dung, điện trở trục, Na/K/Ca/Cl, leak, HCN, Ca-activated K, pump/exchanger.
- Synapse: vesicle pools, release probability, glutamate/GABA, uptake/clearance, AMPA/NMDA/GABA receptors, Markov kinetics.
- Tính toán dendrite: branch-specific integration, NMDA/Na/Ca local events, spine neck resistance, tương tác dendrite–soma–AIS.
- Calcium/signaling: diffusion, buffering, pumps, ER, mitochondria, CaM/CaMKII, calcineurin/PP1, PKA/PKC, ERK/CREB khi có dữ liệu.
- Plasticity: STDP, LTP/LTD, homeostasis, receptor trafficking, intrinsic excitability.
- Gene/protein: synapse-to-nucleus, CREB/IEGs, mRNA, translation, protein turnover; không mô phỏng toàn bộ genome nếu chưa có câu hỏi và dữ liệu.
- Năng lượng: Na/K pump, calcium handling, vesicle cycling, ATP/ADP, mitochondria/oxidative phosphorylation.
- Môi trường/glia: extracellular ions, glutamate, astrocytic uptake/buffering và neuromodulation.
- Cấu trúc dài hạn: remodeling và thay đổi hình thái khi có cơ chế và dữ liệu thích hợp.

Không cần đưa tất cả vào phiên bản đầu tiên. Mỗi cơ chế phải có lý do, nguồn tham số, kiểm tra và tiêu chí loại bỏ.

## 2. Đối tượng khởi đầu

Ưu tiên **human layer 2/3 cortical pyramidal neuron** vì đã có mô hình hình thái/điện sinh học người và nghiên cứu quần thể L2–3.

Các nguồn nền tảng đã được ghi trong dossier:

- Eyal et al. 2018 — mô hình neuron tháp vỏ não người từ gai dendrite đến spike: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/
- ModelDB 238347: https://modeldb.science/238347
- Aizenbud et al. 2026 / FCI: https://doi.org/10.1073/pnas.2533168123
- FCI source: https://github.com/ido4848/fci
- Planert et al. human L2–3 electrophysiological subtypes: https://www.nature.com/articles/s41593-025-02134-7
- Allen Cell Types: https://celltypes.brain-map.org/
- NeuroMorpho: https://neuromorpho.org/

Thông số từ paper/model cụ thể không được biến thành “hằng số phổ quát của neuron người”. Ghi rõ loài, vùng não, cell type, phương pháp, cỡ mẫu, điều kiện và nguồn.

## 3. Nền tảng/phát hiện kỹ thuật đã khảo sát

### FCI repository

Đã đọc một phần source/README/model files của https://github.com/ido4848/fci.

- Có các mô hình compartmental người/chuột dùng trong phân tích functional complexity.
- Cấu hình được xem xét có dendrite thụ động, soma/axon phát spike, AMPA/NMDA, GABA-A và cơ chế phát xung Na/K.
- Đây là baseline có giá trị cho hình thái + tích hợp synapse + NMDA nonlinearity, **không phải** mô phỏng toàn bộ kênh ion hoạt động trên dendrite, calcium signaling, gene expression hay metabolism.
- FCI đo độ phức tạp của ánh xạ input-output trong protocol/mô hình cụ thể; không phải phép đo trí thông minh, ý thức hoặc cognition của con người.
- Dùng FCI làm metric phụ; phải match firing rate, input statistics, dataset, training budget.

### BRAINCELL

Đã khảo sát source tree và một số mechanism files của https://github.com/RusakovLab/BRAINCELL.

- Nền tảng NEURON-based tập trung vào neuron, astrocyte, synapse và extracellular dynamics; README đề cập nanoscale spine/stalk geometry và ion diffusion.
- Đã thấy các module thuộc calcium diffusion/handling, receptor states, glutamate transporter và một số ion/pump mechanisms.
- Không được tuyên bố đã audit đầy đủ mọi module. Trước khi tự xây mechanism tương tự, đọc source đúng path, xác định license từng thành phần và benchmark khả năng mở rộng.
- Khuyến nghị: tận dụng/đối chiếu BRAINCELL thay vì viết lại những gì nó đã cung cấp.

### Bộ công cụ cần benchmark

- **MOOSE**: ứng viên tích hợp đa ngăn + hóa sinh/reaction-diffusion; phải kiểm tra thực nghiệm trước khi chọn làm core. License cần xét.
- **NEURON + RxD**: baseline quan trọng cho cable electrophysiology và reaction-diffusion.
- **STEPS / MCell**: subdomain stochastic 3D cho spine, nanodomain, vesicle/receptor.
- **Jaxley**: differentiable biophysical modeling, parameter fitting và sensitivity ở phần phù hợp.
- **Arbor**: hiệu năng neuron/network.
- **COPASI**: reaction network, ODE/SDE/SSA và parameter estimation.
- **NeuroML / SBML / NWB**: định dạng trao đổi mô hình/dữ liệu, không phải simulator thay thế.

Nguồn chính thức được liệt kê trong dossier. Phiên bản hiện hành cần kiểm tra lại ở mỗi phiên dùng phần mềm.

## 4. Trạng thái lưu trữ và sự thật về mã nguồn (20/11/2026)

Đã kiểm tra filesystem của phiên làm việc:

- `/mnt/data/AMSN_research_dossier_v1.md`: có hồ sơ nghiên cứu Markdown, khoảng 32.586 byte, 340 dòng.
- `/mnt/data/amsn_alpha/README.md`: có README mô tả AMSN Alpha 0.2.0a2, khoảng 9.341 byte.
- Các thư mục `amsn/`, `tests/`, `scripts/`, `docs/`, `results/`, `data/` trong `/mnt/data/amsn_alpha/` có tồn tại nhưng rỗng tại lần kiểm tra.
- Vì vậy, các module Python, test suite, scripts và output dữ liệu không còn trong thư mục được kiểm tra.
- README cũ **tuyên bố** có SWC import, Hines solver, HH/Mainen-like channels, AMPA/NMDA/GABA, stochastic release, STDP, calcium/plasticity, metabolism/ATP, chloride homeostasis, astrocyte coupling và “69 passing tests”. Nhưng khi code/tests trống, không thể xác minh các chức năng hay con số test đó.
- Ba PNG còn thấy trong vùng mount tạm của phiên: `astrocyte_eaat_sweep.png`, `amsn_astrocyte_closed_loop.png`, `amsn_alpha_integrated.png`. Chúng không nằm trong thư mục `/mnt/data/amsn_alpha/results/` chuẩn ở thời điểm kiểm tra; chưa có nguồn dữ liệu/mã tái tạo đủ để coi hình là kết quả có thể tái lập.
- Một mô hình SWC 10.660 node tên `790872626_raw.swc` từng được xem trong nghiên cứu trước, nhưng license/provenance và việc có còn file nguồn không phải kiểm tra lại trước khi dùng. Không commit/redistribute nếu chưa kiểm tra license.

**Điểm sửa quan trọng:** không lặp lại tuyên bố “69 tests passed” hoặc tuyên bố alpha đã chạy được cho đến khi mã nguồn thật được khôi phục/tái dựng và toàn bộ test được chạy lại. Dossier hiện là hồ sơ nghiên cứu, không phải bằng chứng code hoạt động.

## 5. Thiết kế nghiên cứu

AMSN nên là một hệ nhiều solver, nhiều thang thời gian, nhiều độ phân giải, với sổ cái provenance.

Mỗi subsystem phải khai báo:

- state variables và đơn vị;
- spatial domain/compartment mapping;
- solver/integrator, deterministic hay stochastic;
- timestep hoặc tolerance;
- inputs/outputs/fluxes và quy ước dấu;
- cách coupling và độ trễ đồng bộ;
- conservation checks phù hợp;
- nguồn và uncertainty của mọi parameter.

Không kết nối subsystem bằng cách cập nhật các biến tùy tiện. Đặc biệt phải kiểm tra đơn vị (m, cm, µm; s, ms; mol/L, mM; A, nA; F, µF), area/volume conversion và flux direction. Kiểm tra numerical convergence và seed reproducibility trước khi tin hình vẽ.

### Pipeline validation

- V0 Morphology: import/branch topology, lengths, diameters, area, volume.
- V1 Passive cable: input resistance, membrane time constant, attenuation/transfer impedance.
- V2 Action potential: threshold, amplitude, width, AHP, adaptation.
- V3 Synapse: EPSP/IPSP rise/decay, paired-pulse, receptor kinetics.
- V4 Dendritic nonlinearities: branch-local voltage/calcium, NMDA/Na/Ca events, soma coupling.
- V5 Calcium/signaling: transient, spatial profile, time course, perturbation.
- V6 Plasticity: STDP window, LTP/LTD magnitude/time course, receptor/kinase dependence.
- V7 Gene/protein: transcript/protein dynamics and perturbations.
- V8 Metabolism: ATP demand/recovery, pump cost, mitochondrial calcium.
- V9 Generalization: protocols withheld from fit; uncertainty/calibration.
- V10 Computational utility: FCI, task accuracy, data efficiency, continual learning, energy/computation.

Chia train/calibration/holdout theo cell/subject/experiment nếu có thể; không chỉ chia ngẫu nhiên các time window của cùng một trace.

## 6. Lộ trình có thứ tự ưu tiên

### P0 — Khôi phục và khóa provenance

1. Lưu các tài liệu nghiên cứu này lên GitHub.
2. Không giả định source code cũ có thể khôi phục từ README.
3. Tìm lại artifacts/source từ GitHub Actions, commit history hoặc backup chỉ khi người dùng chỉ rõ vị trí/repo; không tự bịa đường dẫn hay ghi đè.
4. Tạo project Python tối thiểu mới trong branch riêng khi đến lúc code; mỗi module/test phải được lưu ngay sau khi tạo.
5. Ghi SHA commit, package lock, Python version, OS và lệnh tái tạo.

### P1 — Reproduce baseline

1. Chạy nguyên bản Eyal/ModelDB NEURON model (không thay mechanism).
2. Chọn một morphology có license rõ ràng và metadata đầy đủ.
3. Lưu protocol, voltage traces và test output.
4. Đối chiếu một baseline bằng NEURON; chỉ thử MOOSE sau khi có reference outputs.
5. Không bắt đầu bằng full gene/metabolism; điện sinh học chưa vững thì chemistry chỉ làm tăng sai số khó truy tìm.

### P2 — Dendrite/spine benchmark

- Single synapse, same-branch coincident cluster, distributed multi-branch inputs, jitter, inhibitory veto.
- Ghi spine head/neck, dendrite local, soma và AIS.
- Ablation: passive vs NMDA vs active channel variants.
- Match rate/input distribution trước khi so sánh FCI.

### P3 — Causal calcium-to-plasticity loop

- NMDAR/CaV → Ca²⁺/CaM → CaMKII/phosphatase → AMPAR state/trafficking.
- Block từng mắt xích và dự đoán đầu ra nhiều tầng.
- So ODE/continuum với STEPS/MCell stochastic ở một microdomain.

### P4 — Synapse-to-nucleus / gene & protein

- Ca²⁺/ERK/CREB → immediate early genes → mRNA/protein → receptor trafficking.
- Phân biệt local translation và nuclear transcription.
- Mở rộng theo time course và perturbation, không mô phỏng whole genome trước.

### P5 — Metabolic constraint

- Nối Na/K pumping, calcium handling, vesicle recycling với ATP cost/recovery.
- Dùng cùng tổng spike nhưng khác temporal patterns để đánh giá lịch sử hoạt động.

### P6 — AI architecture translation

- Trích cơ chế có bằng chứng, xây abstraction nhỏ và kiểm thử độc lập với biological simulator.
- Baselines: MLP, RNN/GRU/LSTM, TCN, SNN và Transformer phù hợp.
- Match parameter count, data, training steps, compute/energy budget và evaluation protocol.
- Metrics: data efficiency, continual learning/forgetting, temporal memory, robustness, compositional generalization, energy, interpretability.
- Không kết luận vượt Transformer dựa trên một task nhỏ, một plot hoặc FCI.

## 7. Giả thuyết nghiên cứu mở

Các ý sau là giả thuyết, không phải kết quả:

1. **Adaptive Biological Resolution:** tăng chi tiết ở spine/branch đang hoạt động mạnh, giảm chi tiết ở nơi ít liên quan, có error bound và flux conservation.
2. **Causal Cell Twin:** dự đoán hậu quả perturbation chứ không chỉ fit waveform baseline.
3. **Energetically Constrained Computation:** đo lợi ích tính toán trên mỗi chi phí năng lượng sinh học.
4. **Hybrid differentiable + stochastic inference:** Jaxley/gradient cho subsystem khả vi; Bayesian/SBI cho subsystem stochastic; kiểm tra identifiability.
5. **Population digital twins:** sau cell đơn đã validation, dùng distributions của morphology/subtype/synapse thay vì một neuron trung bình.

## 8. Quy tắc khoa học và an toàn dữ liệu

- Không tự đặt thông số sinh học để làm demo rồi gọi là human-calibrated.
- Không dùng một trace phù hợp làm bằng chứng toàn cục.
- Báo cáo negative results, failure cases, confidence/credible intervals và seed variance.
- Mọi bảng so sánh công cụ phải gắn phiên bản/ngày kiểm tra.
- License phải được kiểm tra trước khi vendoring mã và dữ liệu; giữ nguyên license của từng nguồn.
- Không commit dữ liệu người/bệnh nhân có thông tin định danh hoặc dữ liệu bị hạn chế.
- Không tuyên bố “mô phỏng hoàn chỉnh neuron người”, “AGI”, hay “vượt Transformer” khi chưa có bằng chứng được kiểm định độc lập.

## 9. Quy trình bắt buộc khi tiếp tục nghiên cứu

Mỗi phiên AI phải:

1. Kiểm tra branch và commit mới nhất trên GitHub.
2. Đọc checkpoint gần nhất, không sửa dựa trên bản nhớ cũ.
3. Làm một bước nghiên cứu/thực nghiệm cụ thể, lưu log command và output.
4. Tạo file log theo ngày, ví dụ `research/log/2026-11-21-<topic>.md`.
5. Với kết quả mới, cập nhật dossier bằng file version mới thay vì xóa lịch sử, ví dụ `AMSN_RESEARCH_DOSSIER_v1.1.md`.
6. Cập nhật handoff checkpoint mới (có thể tạo `HANDOFF_YYYY-MM-DD.md`), chỉ ra điểm khác so với bản trước.
7. Đẩy file lên repo, kiểm tra commit SHA/URL và xác nhận đúng path.
8. Khi hết phiên, ghi rõ: đã làm gì, file nào được tạo, test nào đã chạy, test nào chưa chạy, next action cụ thể.

**Ưu tiên tiếp theo ngay sau checkpoint này:** dựng một reproduction tối thiểu của Eyal 2018 bằng NEURON/ModelDB ở một môi trường có thể chạy; thu output baseline; khóa source version; rồi xây test đối chiếu đầu tiên. Không thêm các lớp gene/ATP/astrocyte vào trước khi baseline điện học qua kiểm chứng.

## 10. Cách ghi kết quả

Mỗi báo cáo thực nghiệm phải có:

- Research question
- Hypothesis (và điều kiện bác bỏ)
- Biological scope and cell type
- Data/source/license/provenance
- Model equations and parameter table
- Software/OS/package versions
- Run command/configuration/random seed
- Outputs and plots with source data
- Validation metrics and uncertainty
- Limitations and failed cases
- Commit SHA that contains code/data/report

Nếu thiếu một thành phần, phải ghi rõ “not collected/not validated”, không được tự điền bằng suy đoán.

---

**Trạng thái handoff:** Đây là checkpoint tài liệu để tiếp tục từ dữ liệu còn xác minh được. Nó không khẳng định có sẵn mã AMSN Alpha chạy được.


---

## Latest dated checkpoint — FCI derivatives and Segev morphologies (21/11/2026)

Read `HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md` before continuing. Two direct NeuroMorpho human L2/3 morphologies have been added with CC BY 4.0 attribution. The FCI `human/eyal` configurations are reduced derivatives, with passive dendrites and active soma/synthetic axon; their Na/Kv scaling is based on a rat Hay L5b exemplar. No FCI code was copied. The original Eyal 2018 ModelDB archive remains unavailable/unintegrated. Keep configurations separate.


---

## Latest dated checkpoint — FCI derivative / Segev morphologies (21/11/2026)

Continue from [HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md](HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md). The commit adds two direct NeuroMorpho human L2/3 morphologies, CC BY 4.0 attribution, parser/soma/cable tests, an FCI read-only provenance/parameter audit, and a four-job passive AC matrix. Do not claim results until that workflow passes. FCI is a reduced derivative, not original Eyal 2018; no FCI code is copied.


## Segev morphology investigation — 21/11/2026

The four-job AC matrix [44885009077](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077) passed but shows NMO_68175 residuals (~0.94% low-frequency input, ~5.7% transfer maximum) that do not reduce on mesh refinement. Do not claim multi-cell validation is complete. Follow [HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md](HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md) and compare geometry/area/import mapping before changing parameters.



---

## Latest dated checkpoint — Segev AC source and probe coordinate audits (21/11/2026)

- Three-reference source audit [workflow 44899442076](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076) passed both NMO_68174/68175 morphology jobs on NEURON 9.0.2; Core CI [44899349672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899349672) passed.
- Source-reference results and limitations are recorded in [triplet handoff](HANDOFF_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md) and [research log](research/RESEARCH_LOG_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md). The measured legacy-to-exact transfer effect reached 0.021954% for cell1125 and 0.228926% for cell1204; exact-to-refined centre changes were zero at exported precision for those identifiable source sites.
- Next active experiment: [AC probe-coordinate audit](HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md), comparing exact SWC readout, nearest segment centre and complex interpolation with source fixed at exact SWC arc. Do not infer results until raw CSVs and both CI jobs pass.



## Verified Segev AC probe-coordinate checkpoint — 21/11/2026

Probe audit [44901688035](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901688035) passed both human Segev morphologies on NEURON 9.0.2 (120 rows each); Core CI [44901673896](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901673896) passed. Exact-SWC and nearest-centre probe readouts were identical at exported precision. Complex-linear interpolation altered cross-simulator residuals non-uniformly: for cell1125 median/p95/max 0.001555/0.049634/0.130599% → 0.000670/0.046984/0.132786%; for cell1204 0.002297/0.073495/0.169222% → 0.001105/0.059094/0.125637%. It must remain a diagnostic option, not a new default. Continue from [probe mesh sweep handoff](HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md) to test 0.25/0.125/0.0625 µm convergence.




## Verified Segev AC probe mesh-convergence checkpoint — 21/11/2026

The six-job matrix [44902130621](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621) passed 6/6; Core CI [44902130609](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130609) passed 4/4. Exact-SWC and nearest-centre transfer readouts were identical at exported precision for all 720 rows. Complex-interpolation readout sensitivity shrank with mesh refinement, but its effect on the cross-simulator residual did not converge to a universal benefit: at 0.0625 µm it improved the NMO_68174 aggregate and worsened all three NMO_68175 aggregate metrics. Keep exact-SWC canonical and interpolation diagnostic-only. See [report](amsn-core/research/HUMAN_SEGEV_AC_PROBE_MESH_SWEEP_2026-11-21.md), [summary CSV](amsn-core/results/human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv) and [mesh-sweep handoff](HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md).


## Verified Segev axial operator checkpoint — 21/11/2026

The Segev full-tree axial matrix [44903533060](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060) passed 2/2 jobs; original NMO_290988 regression [44903453372](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453372) passed. The 32-vector sampled axial-operator relative L2 max is 0.0106860% (NMO_68174) and 0.0032929% (NMO_68175). This is axial-only and not a formal operator-norm or biological validation. Next, establish matched membrane-area/control-volume support before adding leak and capacitance. See [matrix report](amsn-core/research/HUMAN_SEGEV_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md).


## Verified Segev membrane-area support checkpoint — 21/11/2026

Matched-support membrane-area workflow [44904138720](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720) passed both Segev cells. Total area mismatch is below 1.2e-6%; maximum per-node difference is 0.0256% (NMO_68174) and 0.00908% (NMO_68175); every NEURON segment area was allocated with section coverage closure below 2.3e-14%. Next: combine this validated per-node area support with the locked axial graph to compare the passive leak+capacitance operator. See [report](amsn-core/research/HUMAN_SEGEV_MEMBRANE_AREA_SUPPORT_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-MEMBRANE-AREA-SUPPORT.md).


## Verified Segev matched-support passive operator checkpoint — 21/11/2026

Matched-support passive admittance workflow [44904475571](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571) passed 2/2 cells, and Core CI [44904475559](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475559) passed 4/4 jobs. The maximum sampled relative L2 error across DC–3 kHz was 0.0078381% for NMO_68174 and 0.0025449% for NMO_68175. Leak/capacitance diagonal errors were below 0.00025%. This is a matched-support finite-volume projection, not a native fine-grid Schur complement or biological validation. See [report](amsn-core/research/HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-PASSIVE-ADMITTANCE-OPERATOR.md).


## Verified Segev native passive transient checkpoint — 21/11/2026

Native transient validation [44907890895](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895) passed 2/2 cells; Core CI [44907890934](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934) passed 4/4 jobs. Maximum waveform NRMSE was 0.001641% (NMO_68174) and 0.002370% (NMO_68175); absolute waveform errors stayed below 5.2e-6 mV. This directly compared native NEURON segment trees against AMSN's SWC node-centred trees with backward Euler and recorded nonzero source/probe mapping offsets. See [report](amsn-core/research/HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-PASSIVE-TRANSIENT.md). Next: time-step/spatial mesh factorial convergence.

## Verified Segev transient time/space convergence — 21/11/2026

The 12-job matrix [44908381318](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318) passed 12/12; Core CI [44908381336](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336) passed 4/4. It produced 126,180 time-series rows and 360 summaries.

Backward-Euler temporal refinement is first-order (pairwise maximum-NRMSE ratios 1.985/1.984 as dt is halved). Cross-simulator residuals barely change with dt at fixed mesh. Spatial refinement is cell-specific: it improves NMO_68174 but worsens NMO_68175, where interpolation is no longer better at 0.0625 µm. Do not choose a universal finer mesh or probe rule from these two morphologies.

See [full convergence report](amsn-core/research/HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md), [configuration summary](amsn-core/results/human_segev_passive_transient_convergence_summary_2026-11-21.csv), and [pairwise measurements](amsn-core/results/human_segev_passive_transient_pairwise_convergence_2026-11-21.csv).

Next: test source placement by comparing nearest-centre IClamp with a charge-conserving two-centre weighted current split at the exact SWC arc.


## Verified Segev transient source-placement checkpoint — 21/11/2026

Source-placement audit [44910070325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325) passed 4/4; Core CI [44910070326](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326) passed 4/4. The weighted two-centre IClamp split conserves total 10 pA at every sample, but its benefit is morphology-/mesh-dependent: it strongly improves NMO_68175 and is mixed/worse for NMO_68174 at the finer mesh. Keep it optional, not the default. Full report: [HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md). Next: direct AC source-placement comparison.


## Verified Segev AC source-placement checkpoint — 21/11/2026

AC source placement [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4, Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4. Weighted adjacent-centre source superposition strongly improves NMO_68175 at both meshes, but is mixed/worse on NMO_68174 at the finer mesh. Keep it optional, not the default. See [AC report](amsn-core/research/HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md), [summary](amsn-core/results/human_segev_ac_source_alignment_summary_2026-11-21.csv), and [comparison](amsn-core/results/human_segev_ac_source_alignment_comparison_2026-11-21.csv).


## AC source-placement worst-path localization — 21/11/2026

The four raw AC matrices peak at 3 kHz and are concentrated in apical transfer paths. NMO_68174's worst path remains basal q75→apical q90; NMO_68175's worst path changes with mesh, and weighted source moves the remaining worst path to basal q75→apical q90 at both meshes. See [AC worst-pair table](amsn-core/results/human_segev_ac_source_alignment_worst_pairs_2026-11-21.csv).


## Third-morphology source-alignment replication — 21/11/2026

A six-job independent morphology matrix has been added: NMO_68174, NMO_68175 and NMO_290988 / 1094_Mohan_etal_2015 at mesh caps 0.125 and 0.0625 µm. The third morphology is a distinct NeuroMorpho.Org/DeKock record but is a partial dendritic reconstruction (no axon, moderate completeness) with mesiotemporal sclerosis context; do not label it a healthy control. Each job runs all AMSN tests, validates source/probe mapping and produces both transient and AC raw measurements.


## Completed three-morphology source-placement replication — 21/11/2026

Workflow [44914135217](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217) passed 6/6; every job ran the full 81-test suite. The matrix covers NMO_68174, NMO_68175 and NMO_290988 at 0.125/0.0625 µm, with transient and AC comparisons. NMO_68175 benefits consistently, NMO_68174 is mixed, and NMO_290988 shows strong transient improvement but slight AC degradation at the finer mesh. Keep exact-SWC canonical and weighted source optional. See the [replication report](amsn-core/research/HUMAN_MORPHOLOGY_SOURCE_ALIGNMENT_REPLICATION_2026-11-21.md) and [summary CSV](amsn-core/results/human_morphology_source_alignment_summary_2026-11-21.csv).


## NMO_290988 transient time/space convergence — in progress

A six-job factorial run now varies dt=0.1/0.05/0.025 ms and NEURON mesh cap=0.125/0.0625 µm on the independent 8,903-record NMO_290988 morphology. Each job runs the complete AMSN test suite and preserves raw transients. Do not infer convergence until all six artifacts have been reviewed.


## NMO_290988 transient time/space convergence — completed 21/11/2026

Workflow [44915125555](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555) passed 6/6. At fixed mesh, AMSN–NEURON mismatch barely changes with dt; refining the NEURON mesh from 0.125 to 0.0625 µm reduces maximum interpolated NRMSE by about 90.4%. Direct NEURON temporal pairwise error halves with dt as expected for backward Euler. See [convergence report](amsn-core/research/HUMAN_NMO_290988_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md) and [pairwise data](amsn-core/results/human_nmo290988_passive_transient_pairwise_convergence_2026-11-21.csv).


## Exact passive Schur port reduction — in progress

Core API amsn.schur_reduce_passive_admittance eliminates non-retained passive cable vertices and returns the frequency-dependent complex admittance on retained ports. Unit tests compare it with dense Schur and full Hines results. The six-job human audit compares seven-port AMSN and NEURON operators over eight frequencies.


## Exact passive Schur port-matrix audit — completed 21/11/2026

The new exact frequency-dependent Schur reduction is validated against an independent full-tree AMSN port impedance inverse to 9.40e-11% maximum error. The six-job human audit [44916411567](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567) passed 6/6, and Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed 4/4. Seven-port admittance matrix errors remain below 0.0262% and impedance errors below 0.0895%; maxima occur at 3 kHz, with off-diagonal couplings more sensitive than diagonal ports. See [report](amsn-core/research/HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md).


The six Schur audit jobs each passed 90 tests; Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed all 90 tests on Python 3.12 and 3.13 and both NEURON jobs.


## Schur port error localization extension — in progress

The Schur audit now records per-frequency, per-port row-norm and diagonal/off-diagonal errors so the high-frequency residual can be localized without unstable relative percentages on near-zero matrix entries. Each configuration will upload 56 port-localization rows in addition to the 392 raw matrix entries and eight frequency summaries.


## Schur port-resolved residual localization — completed

The rerun [44917323461](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44917323461) passed 6/6 and adds a 56-row per-configuration port-localization CSV. Dominant 3 kHz rows: NMO_68174 apical q50; NMO_68175 basal q50/apical q50 depending on mesh; NMO_290988 apical q90 with off-diagonal coupling error dominating its diagonal. See [localization data](amsn-core/results/human_schur_port_matrix_port_localization_2026-11-21.csv).


## PRIMA passive reduced-order model — completed 21/11/2026

A structure-preserving passive state-space reduction has been added after the exact Schur port audit. Human audit [44918896972](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972) passed 6/6; Core CI [44918897010](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918897010) passed 4/4. The reduced order is 56 for full models of 8,893–13,747 compartments (99.37–99.59% fewer states). Worst 3 kHz impedance/admittance errors are 1.9661%/2.3601%; worst individual-port transient NRMSE is 0.00015662%. This validates the passive numerical subsystem, not active or biological behavior. Read [PRIMA handoff](HANDOFF_2026-11-21_PRIMA-PASSIVE-REDUCTION.md), [research report](amsn-core/research/HUMAN_PASSIVE_PRIMA_REDUCTION_AUDIT_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_reduction_summary_2026-11-21.csv).

Next: multi-shift/frequency-aware PRIMA order sweep, retaining passivity and measuring the high-frequency error trade-off.


## Multi-shift passive PRIMA and order sweep — completed 21/11/2026

Added positive-real multi-shift Krylov expansion at 0/100/1,000/3,000 Hz and a human order sweep at 28/56/84 states. Across three morphologies and six NEURON reference-mesh configurations, order 56 gives maximum 3 kHz Z/Y errors below 0.0201%/0.0237%; order 84 lowers them below 0.000094%/0.000183%, with more than 99.05% state reduction. Six human jobs and four Core CI jobs passed; 99 tests passed on Python 3.12 and 3.13. Read [multi-shift/order-sweep handoff](HANDOFF_2026-11-21_PRIMA-PASSIVE-REDUCTION.md), [report](amsn-core/research/HUMAN_PASSIVE_PRIMA_MULTISHIFT_ORDER_SWEEP_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_multishift_order_sweep_summary_2026-11-21.csv).


## Direct PRIMA-to-NEURON comparison — completed 21/11/2026

Added a three-layer validation: exact Schur vs Hines, PRIMA vs full Hines, and PRIMA vs NEURON. Human audit [44921474635](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635) passed 6/6; Core CI [44921474632](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474632) passed 4/4 with 99 tests on both Python versions. At order 84, direct PRIMA–NEURON errors (0.08943% Z and 0.02611% Y) are essentially at the full-model cross-simulator discrepancy floor. Detailed [report](amsn-core/research/HUMAN_PASSIVE_PRIMA_NEURON_DIRECT_COMPARISON_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_neuron_direct_comparison_summary_2026-11-21.csv).


## Human passive PRIMA parameter robustness — completed 21/11/2026

The basis-reprojection API has been tested on three human morphologies with nine parameter scenarios each (Rm/Cm/Ra ±20%, plus joint corners). Human workflow [44922676384](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384) passed 3/3; Core CI [44922676436](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676436) passed 4/4 with 108 tests on Python 3.12 and 3.13. All 54 reduced models (27 frozen and 27 fresh) passed Cholesky passivity checks. Across the scenarios, the frozen order-56 basis stayed below 0.995% Z / 0.977% Y error at the 10 kHz stress point and below 0.000627% worst individual-port transient NRMSE. A fresh order-56 basis improved the global high-frequency error envelope, but not uniformly scenario-by-scenario. See [parameter robustness report](amsn-core/research/HUMAN_PASSIVE_PRIMA_PARAMETER_ROBUSTNESS_2026-11-21.md) and [morphology summary CSV](amsn-core/results/human_passive_prima_parameter_robustness_morphology_summary_2026-11-21.csv).


---

## Latest checkpoint — PRIMA nine-port result (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-NINE-PORT-RESULTS.md](HANDOFF_2026-11-22_PRIMA-NINE-PORT-RESULTS.md), not the older initial snapshot above. PR #3 merged as `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`. The nine-port workflow passed 6/6 jobs, Core CI 4/4 and the seven-port control 6/6. The full report is [HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md](amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md). Key negative result: all 144 matched apical-q90 comparisons worsened after expanding seven to nine ports at the same tested reduction orders. Keep seven-port as the reference and full Hines canonical; next test basis capacity/order 112 and 168 or a block-Krylov/source-probe weighted basis. See the new dated research log for exact metrics and limits.


---

## Current validated state — PRIMA nine-port high-order basis (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md](HANDOFF_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md) and [the full result](amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md). PR #4 merged at `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`. High-order workflow 44979673244 (6/6), Core CI 44979673250 (4/4), nine-port control 44979673251 (6/6) and seven-port Schur control 44979673239 (6/6) all passed. Orders 112/168 beat seven-port and nine-port order84 apical-q90 in all 36 matched pairs each and had no regression in 252 shared-port comparisons each. Do not promote defaults: retain default 28/56/84 and full Hines canonical until CPU/peak-RSS and held-out morphology benchmarks finish.
