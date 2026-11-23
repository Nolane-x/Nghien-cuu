# Research log — NMO_03524 Jacobs Control matched 7-port / 9-port PRIMA

**Date:** 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45198027785

The matched order112/order168 comparison between seven and nine ports passed on NMO_03524 / Jacobs / 1-5-3, a single human Control-condition occipital BA18 Golgi morphology. The source SWC was pinned at 869 records and SHA-256 6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748. Seven shared nodes were [1,367,583,751,866,867,868]; the two distinct q25 nodes were basal 272 and apical 864.

Coverage: 36 models, 324 frequency rows, 1,728 transient-port rows, 756 shared pairs, 216 q25-only observations and 378 shared-Hines checks. All models achieved their requested orders and passed Cholesky checks. All 378 common Hines references were exactly identical.

Order112 9-port was effectively at parity with 7-port: 204 worse, 173 better, one tie, median error ratio 1.000004647 and maximum 1.006136. Order168 was also at parity: 189 worse / 189 better, median ratio 0.999999905 and maximum 1.007211. q25 max NRMSE was 3.058499e−8% at order112 and 3.058557e−8% at order168.

This differs materially from NMO_162186: there, order112 nine-port had 377/378 regressions and median 9/7 error ratio 8.162×; order168 was required to restore parity. Thus port-count overhead is morphology-dependent, not a universal order threshold. The q25 outputs themselves are accurate on both morphologies tested; the seven/eight? - no: this experiment confirms exactly nine-port layout with q25 nodes 272/864.

Model numeric storage on NMO_03524: 0.92798 MB at order112, 1.53552 MB at order168, same across port count at each order. End-to-end runtime: 42.67 s wall, 89.88 s user CPU, 98,100 KiB peak RSS.

The morphology is one Control-condition cell, with moderate dendrites and incomplete axon. This is passive linear-RC numerical validation only; no active-neuron or population claim. Full Hines remains canonical and no production default changed.
