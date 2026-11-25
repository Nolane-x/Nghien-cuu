# Research log — PRIMA q25 four-morphology boundary, seed budget and downstream convergence

**Date:** 25 November 2026  
**Repository:** `Nolane-x/Nghien-cuu`  
**Branch:** `research/prima-q25-cross-morphology-boundary-replication-2026-11-25`  
**Primary handoff:** [HANDOFF.md](../HANDOFF.md)  
**Detailed handoff:** [four-morphology q25 handoff](../HANDOFF_2026-11-25_PRIMA-Q25-FOUR-MORPHOLOGY-SEED-BUDGET.md)

## 1. Research questions

1. Across four individual passive morphology reconstructions, how do the basal-q25 and apical-q25 retained-port additions change the fixed-order PRIMA approximation of the same seven shared outputs?
2. How much of each requested state order is occupied by the independent columns contributed by the six initial multishift blocks, after orthogonalization across shifts?
3. Does the observed fixed-order error penalty shrink when the basis order is increased from 112 to 224?
4. Can a q25 readout be evaluated as an observation-only output without changing the retained input selector, and does that distinction reproduce the accepted primary basis hashes exactly?

## 2. Scope, inputs and fixed protocol

Four NeuroMorpho reconstructions are held as separate strata:

| Morphology | ID | Condition / provenance |
|---|---|---|
| Peng mouse pyramidal | NMO_163775 | Control; NeuroMorpho metadata says No Diameter |
| Tamas human pyramidal | NMO_107159 | Control comparison cell |
| Jacobs human pyramidal | NMO_03524 | Control |
| Allen L2/3 | NMO_162186 | Epilepsy surgery specimen, not a healthy control |

Every layout retains the same canonical seven shared output nodes and matched soma/basal-q75/apical-q75 input sources. Candidate retained layouts are seven, seven+basal-q25, seven+apical-q25 and seven+both q25 nodes. Source SWC identities and SHA-256 values are pinned in the protocol and per-run reports. The common NEURON segment cap is 0.5 µm.

The primary response protocol is order 168, nine passive parameter scenarios, three source locations, 10-pA rectangular current pulses of 2 and 10 ms at 2 ms onset, timestep 0.00625 ms, 20- and 40-ms observation windows, six expansion shifts (0/100/1000/3000/6000/10000 Hz), and a 0–80-kHz master frequency grid at 25-Hz spacing. The finite-record DFT identity includes the terminal-state correction; periodic transfer alone is not treated as the complete finite response.

## 3. Accepted four-layout response matrix

Primary run: [45608561071 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071)  
Result commit: `1ccac2315a3580505474dbbd188dfc89ef884543`  
Artifact: [15021668387](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071/artifacts/15021668387)

All job steps passed: pinned runtime verification, selected NumPy hot-loop dispatch verification, source/preflight checks, finite-window tests, the four-morphology numerical calculation, coverage and finite-DFT identity assertion, compact result commit and artifact upload. The simulation took 2,369.84 seconds (about 39.5 minutes).

The committed report declares:

`prima_q25_four_morphology_four_layout_boundary_ablation_passed`

| Output | Expected | Read back |
|---|---:|---:|
| Master frequency points | 3,201 | 3,201 |
| Frequency summary rows | 1,075,536 | 1,075,536 |
| Case metrics | 12,096 | 12,096 |
| Matched candidate-vs-seven comparisons | 9,072 | 9,072 |
| Source/layout/window summaries | 144 | 144 |
| Morphology/layout/window summaries | 24 | 24 |
| Finite-DFT identity rows | 1,728 | 1,728 |

The maximum finite-error identity relative error is \(8.781488969255743\times10^{-12}\), against a tolerance of \(2\times10^{-8}\). The maximum absolute identity residual is \(4.809833427024806\times10^{-11}\) V-samples; maximum full/reduced model identity relative error is \(8.743810650683813\times10^{-12}\). The report contains 144 basis, projected-G and projected-C hashes, each set with 144 distinct values.

The strict three-feature environment for this primary run used Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2, Haswell OpenBLAS with one thread, and `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR`. Its report records active selected-operation targets `X86_V3` and `baseline(X86_V2)`. This run predates the later all-functions unfiltered NumPy dispatch preflight, so it is retained as the accepted strict three-feature/selected-kernel response matrix, not described as proof that every NumPy function was inspected in that same process.

The full frequency CSV is too large for GitHub's 100-MB single-blob limit. It is preserved in the Actions artifact; compact metrics, comparisons, identity rows and the report are committed.

## 4. Accepted initial multishift seed-budget diagnostic

Audit run: [45612672472 — success](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472)  
Result commit: `f06e277165d6cd8929c152c2ddb2b6e537e4ccb1`  
Artifact: [15021770119](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45612672472/artifacts/15021770119)

Implementation, tests, protocol and result report:

- `amsn-core/research/audit_prima_q25_four_morphology_initial_shift_seed_budget.py`
- `amsn-core/tests/test_prima_q25_four_morphology_initial_shift_seed_budget.py`
- `amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_PROTOCOL_2026-11-25.md`
- `amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_INITIAL_SHIFT_SEED_BUDGET_RESULTS_2026-11-25.md`

The workflow passed its pinned numerical runtime, unfiltered `numpy.lib.introspect.opt_func_info()` dispatch check, all four source/preflight checks, eight regression tests, 864-row computation, compact result commit and artifact upload. Runtime was 31.62 seconds. Expected/observed coverage was 864 shift rows, 144 morphology/scenario/layout groups and 16 morphology/layout summaries. Raw seed-row SHA-256: `4aa61b37b5923e4383114afc005e4793b8ed629450d82d801b2f732c352ccda4`.

After cross-shift orthogonalization, total independent seed ranks across the six initial expansion shifts were:

| Morphology | Seven | Basal-only | Apical-only | Both q25 |
|---|---:|---:|---:|---:|
| Jacobs | 33 | 39 | 34 | 40 |
| Tamas | 42 | 48 | 48 | 54 |
| Allen | 42 | 48 | 48 | 54 |
| Peng | 42 | 48 | 48 | 54 |

For nominal Jacobs, per-shift independent ranks (0/100/1000/3000/6000/10000 Hz) are 7/6/5/6/5/4 for seven, 8/7/6/7/6/5 for basal-only, 8/7/4/7/4/4 for apical-only, and 9/8/5/8/5/5 for both. The apical-only addition therefore contributes one net independent column across the six initial shifts in Jacobs, compared with six for basal-only. For Tamas, Allen and Peng every shift contributes the full retained-port count (7, 8, 8, or 9).

This diagnostic counts only the initial shifted inverse blocks after orthogonalization. It does not include later round-robin Krylov growth, final basis construction, or response error. It supports initial seed-budget competition as one plausible fixed-order mechanism, not a sole causal explanation.

An important counterexample is retained: Allen, Tamas and Peng have identical initial ranks (42/48/48/54), but their previously accepted pre-strict-dispatch combined-nine-port perturbation-transient error ratios are very different. This shows that scalar initial rank alone cannot predict response error; basis-vector direction, projected dynamics and source/output weighting also matter.

## 5. Numerical runtime and SIMD reproducibility

The full-function preflight in seed-budget run 45612672472 and the new full-dispatch primary preflight check:

- Python 3.12.16, NumPy 2.5.5, SciPy 1.16.3, NEURON 9.0.2, threadpoolctl 3.6.0;
- `OPENBLAS_CORETYPE=Haswell`, `OPENBLAS_NUM_THREADS=1`;
- `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR`;
- unfiltered `numpy.lib.introspect.opt_func_info()`, traversing every returned current implementation;
- active NumPy targets `X86_V3` and `baseline(X86_V2)`; no active X86_V4/AVX-512 target.

The raw CPU feature map can still report individual AVX-512 feature bits as hardware-detected. The acceptance gate concerns *active NumPy dispatch targets* together with the explicit disabled-feature environment; do not conflate the detected CPU feature map with selected function implementations.

Because the analysis runner can be long-running and NumPy introspection/native NEURON state has caused hosted-runner exit-139 failures when invoked in the same process, active dispatch is collected in an isolated preflight and handed to the analysis process via `GITHUB_ENV`. The basis-order driver has now been changed to run order 112 and 224 in separate fresh subprocesses rather than importing the full NEURON runner and invoking its main function in-process.

## 6. Downstream failures, fixes and current run status

### Order convergence

- Basis-order run [45615532277](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45615532277) passed the strict reference gate and all tests, but its in-process order calculation ended with native exit code 139.
- A fresh-process driver was added in commit `fd6f54de901e47c521e93b5ad5f826096cae2277`; the runner now accepts `AMSN_PRIMA_BASIS_ORDER` and `AMSN_PRIMA_RESULT_STEM` environment overrides (commit `62214bb20652723ae486843016225c319c3379a7`).
- Tests now validate the strict order-specific environment handoff (commit `961c60e570f5d4d547bc2c46fb999c642bfe6533`).
- Latest isolated subprocess sweep: [run 45616919005](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616919005). At the latest check it had passed runtime/dispatch verification, SWC checksum, regression tests, morphology preflights and the strict order-168 gate; the 112/224 calculation was running. It uses a new concurrency group so old in-process runs do not block it.
- Older run [45616046400](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616046400) is still in progress under the former group and uses the pre-subprocess driver. Do not treat it as the current sweep.

### q25 output observer

The observer workflow evaluates basal/apical q25 readouts as output observations and compares them with retained-port cases, while requiring all 144 primary basis/G/C/input hashes and active NumPy dispatch targets to match.

Failures recorded and fixes applied:
- An initial observer version compared dispatch targets before assigning `primary_dispatch`; assignment order was corrected and factored into a testable exact-match helper.
- A subsequent run referenced `q25_retained` before creating the map; the retained-role map was moved before its projection check and factored into a tested helper.
- The observer still produced native exit code 139 without a Python traceback. Flushed `OBSERVER_STAGE` markers have been added around module import, morphology import, Hines replays, PRIMA basis build and reduced simulation to locate the native failing stage.

Current instrumented observer: [run 45616908599](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45616908599). It passed runtime, full dispatch, SWC, regression tests and primary gate; the observer analysis stage remains in progress. An additional older pending observer run and older attempts are retained in Actions history.

### Fresh all-functions primary

Fresh full-functions strict primary response rerun: [run 45613803039](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039). It passed runtime installation, unfiltered NumPy dispatch preflight, four-layout regression tests, all four morphology preflights, the full 12,096/9,072/1,728 coverage matrix and finite-DFT identity. Artifact 15023602612 uploaded successfully. The overall workflow conclusion is failure only because its archival rebase conflicted in report.json and time.txt. The uploaded report had three textual conflict blocks in two detected-feature booleans and wall_seconds. The run's incoming side was selected for those fields to reconstruct a valid JSON locally; its coverage, identity, active-dispatch target list, basis/G/C/input hashes and CSVs were validated. The raw conflicted report member SHA-256 is 1aa7e47e41134e0e3e3cb013c6800c6df695962813ceb534020e37931e6737b0; reconstructed clean report SHA-256 is f3f3a75926fe88d0c9963365875f59fc0b990ae7541f20e5566c0aa214e558d7. See `amsn-core/research/PRIMA_Q25_FOUR_MORPHOLOGY_FULL_DISPATCH_RERUN_RESULTS_2026-11-25.md` and `amsn-core/results/prima_q25_four_morphology_full_dispatch_rerun_2026-11-25_summary.json`. This is accepted full-dispatch numerical evidence, while the selected-kernel report 456085 remains the committed baseline.

## 7. Commands and CI evidence

The workflows run the following key commands in `amsn-core/`:

- `python -m pytest -q tests/test_prima_q25_four_morphology_four_layout_boundary_ablation.py tests/test_prima_q25_four_layout_basis_order_convergence.py` (or the workflow's dedicated test files).
- `python -m pytest -q tests/test_prima_q25_four_morphology_initial_shift_seed_budget.py` — 8 passed in the accepted seed-budget run.
- `python -m pytest -q tests/test_prima_q25_output_observer_fixed_vs_enriched_basis.py` — the latest observer workflow's regression step passed before its native analysis stage.
- `python research/audit_prima_q25_four_morphology_initial_shift_seed_budget.py --output-dir results`.
- `python research/run_prima_q25_four_layout_basis_order_convergence.py` now orchestrates separate fresh subprocesses for orders 112 and 224; each child runs `python research/analyze_prima_q25_four_morphology_four_layout_boundary_ablation.py` with explicit order/stem environment overrides.
- `python research/analyze_prima_q25_output_observer_fixed_vs_enriched_basis.py --primary-results-dir results --output-dir results`.

No production solver, retained-port default or PRIMA order was changed. All conclusions remain limited to four individual passive linear-RC morphologies; no active channels, synapses, plasticity, spikes, biological-population or general neuron claims are made.

## 8. Next actions

1. Inspect the flushed stage log from run 45616908599 and isolate the observer's native exit-139 stage; preserve the 144-hash, dispatch and finite-DFT gates.
2. Finish run 45616919005. If 112/224 pass, verify each coverage matrix, all finite-DFT identity rows, paired posthoc row counts and the combined report before accepting convergence.
3. Finish run 45613803039. Accept its order-168 report only after all-function dispatch, exact row counts, all 144 basis hashes and finite-DFT identity pass.
4. Update observer and sweep reports/handoffs with the final run IDs and exact checksums. GITHUB_TOKEN-generated archival commits do not automatically trigger push workflows; a separate connector-authored workflow-path commit is needed to launch downstream automation after the strict primary archive is created.
5. Update root `HANDOFF.md`, this dated log and the focused handoff; fetch/read every changed path back and record the final branch head SHA.

