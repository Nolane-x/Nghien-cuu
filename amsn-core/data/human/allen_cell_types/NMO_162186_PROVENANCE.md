# Held-out morphology provenance — NMO_162186

**Status:** candidate selected; external-file preflight pending  
**Role:** independent morphology-level holdout for passive cable / PRIMA research  
**Do not describe this record as a healthy-control cell or as a complete axon reconstruction.**

## Source identity

- NeuroMorpho.Org ID: **NMO_162186**
- Cell name: `770307286_transformed`
- Archive: Allen Cell Types
- Species: human; adult, 36 years; male
- Region: right middle temporal gyrus, neocortex, layer 2–3
- Cell class: principal / pyramidal; excitatory intratelencephalic (IT)
- Experimental condition: **epilepsy**
- Reconstruction source format: Vaa3D SWC; this project requests the standardized NeuroMorpho CNG SWC
- NeuroMorpho integrity: **dendrites complete; axon incomplete**
- NeuroMorpho morphometry metadata: 7,284 total fragmentation; 48 bifurcations; 103 branches; 7 stems; total length 10,476.9 µm; total surface 21,367.1 µm²; maximum path distance 620.43 µm.

## Direct source file

`https://neuromorpho.org/dableFiles/allen%20cell%20types/CNG%20version/770307286_transformed.CNG.swc`

The file is fetched by a GitHub Actions runner using the direct SWC URL and an explicit User-Agent. The workflow does not scrape the JSP metadata page. The exact downloaded bytes, SHA-256 digest, parser results, and NEURON Import3D preflight are preserved as a workflow artifact. The SWC is deliberately **not vendored into the repository yet**; that decision is deferred until the source bytes and checksum are verified.

## Attribution and license

NeuroMorpho.Org states that material found on or downloaded from the site is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Its terms require all three citations when using the material in a publication:

1. The original reconstruction paper associated with the record: Berg J, Sorensen SA, Ting JT, et al. (2021), “Human neocortical expansion involves glutamatergic neuron diversification,” *Nature* 598, 151–158, DOI: [10.1038/s41586-021-03813-8](https://doi.org/10.1038/s41586-021-03813-8). The NeuroMorpho detail page displays the related-article title “Human cortical expansion involves diversification and specialization of supragranular intratelencephalic-projecting neurons”; preserve that metadata wording when describing the record.
2. The complete repository name **NeuroMorpho.Org (RRID:SCR_002145)**.
3. Tecuatl C, Ljungquist B, Ascoli GA (2024), “Accelerating the continuous community sharing of digital neuromorphology data,” *FASEB BioAdvances* 6(7):207–221, DOI: [10.1096/fba.2024-00048](https://doi.org/10.1096/fba.2024-00048).

The Allen Cell Types collection is associated with the Brain Image Library collection DOI [10.35077/g.19](https://doi.org/10.35077/g.19).

## Scientific use constraints

- The cell is from an epilepsy surgical specimen according to the source metadata. It must not be labelled a healthy control.
- Its dendritic reconstruction is marked complete but the axon is explicitly incomplete. The record can test an external human L2–3 pyramidal **dendritic morphology**, but it is not a complete axon-to-dendrite neuron.
- The metadata says dendrites, soma and axon are present, but the axon-integrity field is authoritative for completeness. Never infer a complete AIS/axon from the presence of type-2 SWC nodes.
- The study is a single held-out morphology, not a representative human-neuron sample.
- No biological parameter fitting or active-channel validation is implied by morphology import or passive RC matching.
- All current results are limited to passive linear RC cable equations. Full Hines remains the canonical reference; PRIMA is an experimental reduced representation only.

## Preflight acceptance criteria

1. Download direct standardized SWC bytes and record SHA-256.
2. Strictly parse the file and verify expected record count 7,287, one connected root, and required SWC neurite types 1/2/3/4.
3. Verify the recognized NeuroMorpho three-point soma convention.
4. Build the AMSN full-node cable tree and confirm finite passive DC/AC responses.
5. Import the same SWC through pinned NEURON 9.0.2 Import3D.
6. Recreate the existing seven-port soma/basal/apical source-probe protocol and preserve mapping offsets.
7. Preserve the SWC, source hash and generated preflight report as a workflow artifact.
8. Only after these checks pass should the morphology be added to a separate held-out PRIMA matrix. Do not change production defaults.

## Source URLs

- Cell detail: [NeuroMorpho.Org NMO_162186](https://neuromorpho.org/neuron_info.jsp?neuron_name=770307286_transformed)
- Standardized SWC: [770307286_transformed.CNG.swc](https://neuromorpho.org/dableFiles/allen%20cell%20types/CNG%20version/770307286_transformed.CNG.swc)
- Terms of use: [NeuroMorpho.Org terms](https://neuromorpho.org/useterm.jsp)
- Published paper DOI: [10.1038/s41586-021-03813-8](https://doi.org/10.1038/s41586-021-03813-8)
- Dataset collection DOI: [10.35077/g.19](https://doi.org/10.35077/g.19)
- NeuroMorpho citation DOI: [10.1096/fba.2024-00048](https://doi.org/10.1096/fba.2024-00048)
