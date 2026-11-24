# Handoff — Tamas human pyramidal q25 four-layout replication

**Date:** 24 November 2026  
**Branch:** research/prima-tamas-q25-four-layout-replication-2026-11-24  
**Parent:** q25 Peng ablation branch / PR #19  
**Morphology:** NMO_107159 Tamas human pyramidal Control  
**Mesh cap:** 0.5 µm  
**Successful workflow:** [45330512800](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800)  
**Result commit:** `83e3fd8de612404fe821365a87489ce591355705`  
**Detailed report:** [PRIMA_TAMAS_Q25_FOUR_LAYOUT_REPLICATION_2026-11-24.md](amsn-core/research/PRIMA_TAMAS_Q25_FOUR_LAYOUT_REPLICATION_2026-11-24.md)

## Research question

Does the non-additive dual-q25 error pattern observed on the NMO_163775 Peng mouse passive-RC ablation reproduce on an independent human pyramidal morphology under the same four-layout protocol?

## Source and port identity

The source SWC is pinned at 7,228 records and SHA-256 `6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023`. The independent preflight pins canonical seven SWC nodes `[1, 5564, 6363, 7023, 4301, 4735, 4623]` and q25-only nodes `[6609, 4404]`. The q25 role mapping is basal-q25 = 6609 and apical-q25 = 4404. The source is one female human Control-condition pyramidal comparison cell; age is not reported. It is not the rosehip interneuron.

## Four matched layouts

- `seven`: canonical seven ports.
- `eight_basal_q25`: canonical seven + basal-q25.
- `eight_apical_q25`: canonical seven + apical-q25.
- `nine_both_q25`: canonical seven + both q25 probes.

The same 0.5 µm cap, six expansion shifts, orders 112/168, nine passive parameter scenarios, AC grid, source sites, pulse widths and transient settings as the Peng ablation were retained. Each layout receives an independent full-Hines reference. Shared outputs are joined by exact SWC node identity.

## Verified execution and exact coverage

The corrected workflow 45330512800 completed successfully. The earlier run 45330465196 completed simulation but failed at the result-commit shell step; the shell continuation was corrected and the entire workflow was rerun successfully. The corrected run passed 25 tests, source SHA-256 verification, Import3D preflight, simulation, result commit and artifact upload.

Verified actual row counts:
- 72 model configurations.
- 648 frequency matrices.
- 3,456 per-port transient rows.
- 2,268 matched shared-output pairs versus seven-port.
- 432 q25-only output observations.
- 1,134 shared-Hines comparisons.

All 1,134 Hines comparisons are exactly zero for both maximum absolute voltage difference and relative L2 difference. Runtime used Python 3.12.16, NumPy 2.5.5 and NEURON 9.0.2; wall time 792.91 s, maximum RSS 143,324 KB.

Artifact: [nmo107159-tamas-q25-four-layout-prima-replication](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45330512800/artifacts/14892657539), SHA-256 `defc9964f3a2bca8670d6f7fb4552c2202d6afb04c0b8172a4d2cd7958e245ad`.

## Main numerical result

At basis order 168, the median shared-output NRMSE ratios versus the seven-port baseline are:
- basal-q25 only: 1.000026× (216 worse, 161 better, 1 tie out of 378).
- apical-q25 only: 1.000023× (213 worse, 165 better).
- both q25: 1.001032× (214 worse, 164 better).

The order-168 maximum absolute transient NRMSE across all layouts is 5.456e-7%. The nine-port dual-q25 penalty seen on the Peng mouse morphology (14.525× median ratio at order 168) does **not** reproduce on this Tamas human pyramidal morphology.

At order 112, the pattern is stronger: median ratios are 2.924× for basal-only, 3.745× for apical-only and 42.723× for dual-q25; the dual-q25 candidate is worse on all 378 shared-output pairs. Its maximum absolute transient NRMSE is 3.951e-5%. This confirms substantial basis-order dependence.

For the q25-only output traces at order 168, median NRMSE is 3.047e-8% for basal-only, 2.152e-8% for apical-only and 2.490e-8% for dual-q25. The dual configuration is not worse than both single-probe values on this output-only metric.

## Cross-morphology interpretation

The striking dual-q25 order-168 penalty observed on NMO_163775 is morphology-dependent in the current evidence: it is present on the Peng mouse reconstruction but absent on the independent Tamas human pyramidal reconstruction. The low-order (112) degradation appears in both morphologies. A useful hypothesis is that the high-order behavior is sensitive to morphology-dependent basis geometry/conditioning and not simply to port count, but this mechanism has not been established.

Do not pool the two morphologies as one biological population or infer that the q25 layout is universally safe or harmful. The next step is a targeted basis-conditioning/shift-sensitivity audit on both morphology/layout pairs, followed by additional independent morphologies if warranted.

## Scientific constraints

This is one human morphology, not a population. NeuroMorpho lists Diameter, 3D and Angles for the specimen, but passive membrane parameters remain model assumptions. This remains passive linear-RC numerical validation, not active-neuron or biological validation. Keep NMO_107159 separate from the Peng mouse mesh stratum despite both using a 0.5 µm cap. Full Hines remains canonical and no production defaults change.
