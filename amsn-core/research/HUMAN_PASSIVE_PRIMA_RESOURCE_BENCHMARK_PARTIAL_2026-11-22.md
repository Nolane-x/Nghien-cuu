# PRIMA high-order runtime/resource benchmark — partial verified results

**Status:** partial, not the final resource comparison  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723  
**Code head:** 5180f0bc72dbfad0a460b0870ca80fec772db0e3  
**Matrix definition:** 36 resource jobs (3 morphologies × 2 mesh caps × 3 candidate orders × 2 replicates), plus one 16-test validator preflight.

## Verified subset

Twelve artifacts have been uploaded and independently downloaded from this run. They cover **NMO_68174 cell1125 only**, with both NEURON mesh caps (0.125 and 0.0625 µm), orders 84/112/168 and two replicates per combination.

- 12/12 ZIP SHA-256 digests match GitHub artifact metadata.
- Each raw sweep CSV contains exactly 210 rows: 30 frequency, 162 per-port transient and 18 all-port transient rows.
- Each resource record reports exit_status=0, matching the time-file exit status.
- Each output includes the order-56 control and selected higher-order candidate with the requested rank achieved.
- Total inspected raw sweep rows: **2,520**.
- The benchmark ran under Python 3.12.16 on four logical CPUs; GitHub assigned more than one host CPU model across replicates (AMD EPYC 9V74 and Intel Xeon 6975P-C), so wall-time comparisons should be treated cautiously.

## Median runtime and peak RSS by mesh/order

Medians over two replicates on the single NMO_68174 morphology:

| NEURON segment cap | PRIMA order | Wall time (s) | User CPU (s) | Peak process RSS (MiB) | State reduction |
|---|---:|---:|---:|---:|---:|
| 0.125 µm | 84 | 124.87 | 151.00 | 263.59 | 99.323% |
| 0.125 µm | 112 | 112.16 | 239.99 | 276.17 | 99.097% |
| 0.125 µm | 168 | 143.16 | 312.73 | 297.87 | 98.645% |
| 0.0625 µm | 84 | 125.21 | 150.63 | 403.75 | 99.323% |
| 0.0625 µm | 112 | 99.38 | 199.00 | 411.30 | 99.097% |
| 0.0625 µm | 168 | 171.77 | 362.33 | 416.36 | 98.645% |

## Interpretation, with limits

- Peak RSS rises as the requested reduced order increases, but the mesh cap has a larger influence on process RSS in this subset: at order84 the 0.0625 µm reference uses about 140 MiB more peak process RSS than 0.125 µm.
- From order84 to 168, median RSS rises by about 13.0% at the 0.125 µm cap and 3.1% at the 0.0625 µm cap. The high fine-mesh baseline appears to dominate the process footprint; this is a single morphology and not a universal memory law.
- User CPU time rises more consistently with order: order168 is about 2.07× order84 at 0.125 µm and 2.41× at 0.0625 µm. This is the full audit process, including the order-56 control and candidate comparison, not candidate-only timing.
- Wall time is non-monotonic between orders in this small sample. Two replicates used different cloud CPU models; do not derive a universal speed ranking from elapsed time.
- Numeric PRIMA storage for the same morphology/order is already reported in the candidate summary; these RSS values include Python, NEURON and the full audit process and are not comparable to basis-array storage.

The other two morphologies and the remaining resource jobs have not yet been completely verified. Do not select production defaults from this partial subset. Full Hines remains canonical and the current work remains passive linear-RC only.

## Reproducibility

- Resource benchmark workflow: https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723
- 12-artifact partial raw summary: ../results/human_prima_resource_benchmark_partial_12_NMO68174_2026-11-22.csv
- Full matrix design: ../../../.github/workflows/amsn-human-prima-high-order-resource-benchmark.yml
