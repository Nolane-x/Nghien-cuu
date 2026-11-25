# PRIMA q25 four-morphology — full-function NumPy dispatch rerun

**Date:** 25 November 2026  
**Workflow:** [45613803039](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039)  
**Workflow conclusion:** failed at the later Git rebase/commit step only  
**Numerical result:** passed calculation, exact coverage and finite-DFT identity  
**Artifact:** [15023602612](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45613803039/artifacts/15023602612)  
**Artifact ZIP SHA-256:** \`0869385fec44572fcfe77327043bf2d2e88f312f926a99617d5801a55ee3afc6\`  
**Artifact size:** 70,254,874 bytes (23 files)  
**Machine-readable reconciliation:** [summary JSON](../results/prima_q25_four_morphology_full_dispatch_rerun_2026-11-25_summary.json)

## 1. What passed

Run 45613803039 used the full-function NumPy SIMD dispatch preflight, then completed the four-morphology 7/8/8/9-port calculation and the explicit coverage/finite-DFT identity gate.

| Output | Expected | Read back |
|---|---:|---:|
| Master frequency points | 3,201 | 3,201 |
| Frequency summary rows | 1,075,536 | 1,075,536 |
| Case metrics | 12,096 | 12,096 |
| Candidate-vs-seven comparisons | 9,072 | 9,072 |
| Source/layout/window summaries | 144 | 144 |
| Morphology/layout/window summaries | 24 | 24 |
| Finite-DFT identity rows | 1,728 | 1,728 |

Finite-record identity:
- Maximum relative error: **8.781488969255743 × 10⁻¹²**
- Acceptance tolerance: **2 × 10⁻⁸**
- Maximum absolute residual: **4.809833427024806 × 10⁻¹¹ V-samples**
- Maximum full/reduced identity relative error: **8.743810650683813 × 10⁻¹²**

The report contains 144 basis hashes, 144 projected-G hashes, 144 projected-C hashes and 144 input hashes; each set has 144 unique entries. All four morphology SWC/preflight checks passed.

## 2. Full-function numerical dispatch

Runtime versions:
- Python 3.12.16
- NumPy 2.5.5
- SciPy 1.16.3
- NEURON 9.0.2
- threadpoolctl 3.6.0

Environment:
- \`OPENBLAS_CORETYPE=Haswell\`
- \`OPENBLAS_NUM_THREADS=1\`
- \`NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR\`
- OMP, MKL, BLIS, vecLib and NumExpr thread counts = 1
- \`PYTHONHASHSEED=0\`

The preflight called unfiltered \`numpy.lib.introspect.opt_func_info()\`, traversing the returned function/signature dispatch inventory. The active target list handed into the analysis process was exactly:

\`\`\`text
X86_V3
baseline(X86_V2)
\`\`\`

No active X86_V4 or AVX-512 target was returned. Both observed OpenBLAS pools reported Haswell and one thread.

The calculation report wall time was 1,827.463 seconds; shell wall time was 1,827.88 seconds, user CPU 1,798.04 seconds, system CPU 29.56 seconds and peak RSS 1,233,884 KiB (about 1.18 GiB).

## 3. Why the Actions run is marked failed

The primary numerical calculation and identity/coverage steps all passed. The subsequent archival commit created a result commit, then tried to rebase it over a concurrent branch update. Git reported content conflicts in only:
- \`prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25_report.json\`
- \`prima_q25_four_morphology_four_layout_boundary_ablation_2026-11-25.time.txt\`

The always-run artifact upload then succeeded. The uploaded JSON therefore contains three visible rebase conflict blocks: two booleans in the detected CPU-feature map and the runtime wall-time field. The current-run (“incoming”) sides were selected to reconstruct a valid JSON locally; the reconstruction parsed successfully and preserved the report status, coverage, identity validation, active dispatch, 144 basis/G/C/input hashes and run timing. Reconstructed clean report SHA-256: \`f3f3a75926fe88d0c9963365875f59fc0b990ae7541f20e5566c0aa214e558d7\`. The original conflicted artifact-member report SHA-256 is \`1aa7e47e41134e0e3e3cb013c6800c6df695962813ceb534020e37931e6737b0\`.

The exact data remains in the Actions artifact. This separate committed summary JSON records the recovered validation fields and CSV hashes without overwriting the previously accepted 456085 report in the repository. The commit failure is an archival conflict, **not** a numerical test failure.

## 4. CSV provenance

| CSV | Rows | SHA-256 |
|---|---:|---|
| Case metrics | 12,096 | \`dff980e065b2f497f8aea930b3fd5a16e1db680e80ff84c1d79968430b020c13\` |
| Finite-DFT identity | 1,728 | \`eced64a36c73a8ef1d963f08a5f716dc4bd317101360d14d9f1eebe2adc9e902\` |
| Frequency summary | 1,075,536 | \`dabb47d4c5c06bd26ebd90165b50584ecb8448b8e2fe3bc76cdfff7a9b3bcdce\` |
| Candidate-vs-seven comparisons | 9,072 | \`29af1a3897c44d0aa946768a23ee815299e4fa982e7223e4b9130aa359fd2e6e\` |
| Source/layout/window summary | 144 | \`a2164e1fdc67350e75bf9efb39834537691a328838b739da907a8ec6d269e84a\` |
| Morphology/layout/window summary | 24 | \`192a2b24400ffec4174f3b81ef8e25874ae3b4b29d818a649b8d1e040ee0327d\` |

The full 199-MB frequency summary is retained in the artifact rather than committed as a Git blob.

## 5. Relationship to the earlier accepted matrix

The earlier [run 45608561071](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45608561071) remains the branch's previously accepted selected-kernel strict matrix. Run 45613803039 adds the missing full-function dispatch evidence while re-running the same numerical design. Its morphology/layout/window summary values match the earlier displayed medians; no new production choice is implied by this reproducibility replay.

The full-function-dispatch run may be treated as an accepted numerical result because the numerical computation and validation gates passed and the full artifact is preserved. Its overall Actions conclusion remains failed solely because the report/time archival rebase conflicted. Keep that distinction visible in downstream references.

No production PRIMA order, retained-port default, solver behavior or runtime default was changed. This remains a passive linear-RC numerical experiment on four individual reconstructions, not biological population or active-neuron validation.
