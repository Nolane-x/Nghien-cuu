# Research log — NMO_03524 Jacobs control PRIMA holdout

**Date:** 23 November 2026  
**Workflow:** https://github.com/Nolane-x/Nghien-cuu/actions/runs/45196546471

## Source and validation

Pinned NeuroMorpho NMO_03524 / Jacobs / 1-5-3 (human Control metadata, occipital BA18, 23-year-old male). Source SWC is 31,199 bytes with SHA-256 6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748. It contains 869 records (3 soma, 42 axon, 816 basal dendrite, 8 apical dendrite), one root and no missing parent references.

NEURON 9.0.2 Import3D passed with 68 sections, 35,248 segments, maximum segment length 0.12499949 µm, 862 AMSN electrical compartments and seven distinct PRIMA ports. One terminal basal-q90 probe is at normalized x=1.0 and is read from the nearest endpoint segment rather than extrapolated beyond segment-centre voltages.

GitHub Actions run 45196546471 passed 146/146 tests, source validation, preflight, 81-model matrix, summary checks, result commit and artifact upload (#14827204708).

## Matrix

81 candidates × scenario rows, 729 AC rows, 3,402 transient-port rows. All candidates achieved their requested basis order and passed Cholesky checks. Nine deterministic passive parameter scenarios; seven output ports; full Hines reference.

High-frequency extended10kHz candidate medians at 10 kHz:
- Order56: Z 0.0011971%, Y 0.00024464%; numeric storage 0.4161 MB.
- Order84: Z 5.5775e−7%, Y 2.8753e−7%; numeric storage 0.6601 MB.
- Order112: Z 3.6005e−10%, Y 1.8143e−10%; numeric storage 0.9280 MB.

Order84 extended10kHz is the best accuracy/storage compromise on this holdout (~29% less numeric storage than order112, with very small AC and transient residuals). Order112 extended10kHz is the high-frequency precision choice. Order56 narrow3kHz is the low-footprint option but has higher 10kHz residuals (median Z/Y 0.00857% / 0.00546%).

Extended10kHz was the best high-frequency shift distribution at all three tested orders. No single order is universally required; the conditional choice depends on accuracy and storage budget.

## Next gate

Run the matched seven-port/nine-port order112/order168 test on this same Control morphology to see whether the q25/port-count result from NMO_162186 transfers. Then add another independent morphology, preferably with a more complete axon, and separately pursue fixed-hardware timing and active/nonlinear validation.

Full Hines remains canonical; no production default or runtime path changed.
