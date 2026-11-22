# Research log — Allen Cell Types held-out morphology source preflight

**Date:** 2026-11-22 (Asia/Bangkok)  
**Repository:** https://github.com/Nolane-x/Nghien-cuu  
**Branch:** `research/allen-human-morphology-heldout-preflight-2026-11-22`  
**Base:** `main`

## Why this candidate

NeuroMorpho.Org identifies NMO_162186 (`770307286_transformed`) as a human right middle temporal gyrus layer 2–3 pyramidal, excitatory intratelencephalic cell from the Allen Cell Types archive. The metadata marks dendrites complete and axon incomplete, and reports epilepsy as the experimental condition. Therefore this can be an external held-out dendritic morphology, but must not be described as healthy control or a complete neuron.

The official standardized SWC ends at node ID 7287 and the metadata reports 7,284 total fragmentation; the preflight verifies 7,287 total records, including the three-point soma, directly from downloaded bytes.

## Scope of the new preflight

- Download the official standardized SWC by direct file URL with an explicit User-Agent, as required by NeuroMorpho.Org usage guidance.
- Calculate and preserve SHA-256 for the exact downloaded bytes.
- Strictly parse the topology, expected record count, connected root, neurite types 1/2/3/4 and recognized three-point soma.
- Build the full-node AMSN passive cable representation.
- Reuse the established NEURON Import3D node-to-section mapping and current seven-port soma/basal/apical placement protocol.
- Run one passive NEURON steady comparison at soma source, plus AMSN passive DC at all three source ports and one finite 1 kHz AC response.
- Preserve raw SWC, JSON result and mapping CSV as one Actions artifact.

## Code and tests added

- `amsn-core/src/amsn/provenance.py`: reusable provenance-aware SWC structural validation.
- `amsn-core/tests/test_provenance.py`: strict topology/type/soma validation tests.
- `amsn-core/examples/allen_human_holdout_preflight.py`: source-specific preflight and passive solver smoke test.
- `.github/workflows/amsn-allen-human-holdout-preflight.yml`: pinned NEURON 9.0.2 workflow that downloads source directly and preserves evidence.
- `amsn-core/data/human/allen_cell_types/NMO_162186_PROVENANCE.md`: metadata, use constraints and required attribution.

## Acceptance gate and caveats

This preflight must pass before the morphology is admitted into a separate held-out PRIMA matrix. The source SWC is not committed/vendored yet; it is downloaded during Actions and preserved as an artifact so its hash can be inspected first.

NeuroMorpho.Org terms state CC BY 4.0 and require attribution to the original reconstruction paper, NeuroMorpho.Org (RRID:SCR_002145), and Tecuatl et al. 2024, DOI 10.1096/fba.2024-00048. The record metadata title and published Nature paper title differ, so both titles are retained explicitly.

No production defaults, passive parameters or Hines solver equations are changed. Results remain limited to passive linear RC; neither active-channel validity nor biological population generalization is inferred.
