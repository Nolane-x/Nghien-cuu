# Research log — NMO_162186 matched PRIMA port-count validation

**Date:** 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45184621520

The matched seven-port/nine-port order112/order168 replay passed. It used the pinned NMO_162186 SWC (7,287 records; SHA-256 a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc), identical extended10kHz shifts, nine deterministic Rm/Cm/Ra scenarios, three stimulation sources and two pulse widths.

Coverage was complete: 36 models, 324 frequency rows, 1,728 per-port transient rows, 756 matched shared-output pairs, 216 q25-only observations and 378 exact shared-Hines checks. All 36 models passed the Cholesky passivity checks. The shared Hines references were exactly identical at all 378 common-node tests.

At order112, nine-port error was worse on 377/378 shared comparisons; median transient error ratio 9-port/7-port was 8.162×. At order168, the median ratio was 0.99999985×, with 190 better, 187 worse and one tie. Thus the nine-port order168 parity conclusion from PR #6 reproduces on the NMO_162186 holdout; nine-port order112 remains a poor trade-off for adding q25 ports.

The added q25 outputs were accurate against full Hines at both orders: maximum NRMSE 3.6711e−6% at order112 and 8.6226e−8% at order168. At order168 they are added without degrading the original shared outputs beyond numerical parity.

High-frequency median Z/Y residuals at 10 kHz were: 7-port/112 4.6124e−6% / 9.5816e−6%; 9-port/112 1.0498e−4% / 2.5063e−4%; 7-port/168 2.7305e−10% / 7.2223e−10%; 9-port/168 3.3864e−8% / 9.8754e−8%. Numeric storage is basis plus reduced G/C arrays, not whole-process RSS: 6.4104 MB at order112 and 9.7592 MB at order168 for both port counts in this implementation.

Workflow resource summary: 422.61 s wall, 518.23 s user CPU, 187,160 KiB peak RSS. This is one end-to-end run, not a controlled per-candidate resource ranking.

The NMO_162186 specimen is one epilepsy surgical morphology with incomplete axon. This remains a passive linear-RC numerical validation, not active-neuron or population-level biological validation. Full Hines remains canonical; no production default changed.
