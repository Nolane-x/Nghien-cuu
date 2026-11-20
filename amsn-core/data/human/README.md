# Human morphology fixture — NeuroMorpho.Org

## Included reconstruction

`1094_Mohan_etal_2015.CNG.swc` is a standardized CNG SWC distributed by NeuroMorpho.Org, not the original Neurolucida file.

- Record: NeuroMorpho.Org NMO_290988 / API ID 290988
- Cell: `1094_Mohan_etal_2015`; archive: DeKock
- Species: human; adult
- Region: neocortex → temporal → middle temporal gyrus → Brodmann area 21 → layer 2–3
- Type: principal / pyramidal
- Domains: soma + dendrites; **no axon in this reconstruction**
- Physical integrity: **dendrites moderate**
- Condition in source metadata: **mesiotemporal sclerosis**
- Protocol: in vitro; coronal slice; biocytin; 350 µm; 100× oil; Neurolucida reconstruction
- Shrinkage: not reported
- Age range in API: 20–58 years; sex field says “Male/Female” and does not state a specific value for this cell.

The original study used surgically resected human temporal cortex. It reports no association between morphology metrics and etiology/severity/duration at the study level, but that does not erase this cell's recorded clinical context. This sample is not to be labelled a healthy control.

## License and required attribution

NeuroMorpho.Org Terms of Use state repository data are CC BY 4.0:
https://creativecommons.org/licenses/by/4.0/

This repository stores only the standardized morphology data and our own metadata/validation notes. It does not copy the paper text, figures or images.

Retain all three citations on reuse:
1. Mohan H, Verhoog MB, Doreswamy KK, Eyal G, Aardse R, Lodder BN, Goriounova NA, Asamoah B, Brakspear ABCB, Groot C, van der Sluis S, Testa-Silva G, Obermayer J, Boudewijns ZSRM, Narayanan RT, Baayen JC, Segev I, Mansvelder HD, de Kock CPJ. **Dendritic and Axonal Architecture of Individual Pyramidal Neurons across Layers of Adult Human Neocortex.** *Cerebral Cortex*. 2015;25(12):4839–4853. https://doi.org/10.1093/cercor/bhv188 (PMID 26318661).
2. **NeuroMorpho.Org** (RRID:SCR_002145), record NMO_290988.
3. Tecuatl C, Ljungquist B, Ascoli GA. **Accelerating the continuous community sharing of digital neuromorphology data.** *FASEB BioAdvances*. 2024;6(7):207–221. https://doi.org/10.1096/fba.2024-00048.

Source links:
- Metadata API: https://neuromorpho.org/api/neuron/name/1094_Mohan_etal_2015
- Morphometry API: https://neuromorpho.org/api/morphometry/name/1094_Mohan_etal_2015
- Standardized SWC: https://neuromorpho.org/dableFiles/dekock/CNG%20version/1094_Mohan_etal_2015.CNG.swc
- Terms: https://www.neuromorpho.org/useterm.jsp
- API: https://www.neuromorpho.org/api.jsp
- CNG soma convention: https://cngpro.gmu.edu/SomaFormat.html
- SWC specification: https://github.com/INCF/swc-specification

Retrieved 2026-11-20 (UTC+7); repository v8.7 (released 2026-10-29). The exact file's Git blob SHA is in the adjacent provenance JSON.

## Integrity and morphology notes

The unchanged source file has 321,865 text characters and 8,903 SWC records; one root; unique IDs; seven numeric fields per row; valid parents; positive radii; no disconnected points or cycles. Type counts: 3 soma, 4,051 basal dendrite, 4,849 apical dendrite, 0 axon.

NeuroMorpho's standardized CNG soma is a multi-point, cylinder-like representation. Do not add an additional root sphere on top of type-1 soma edges. AMSN now avoids that double count and rejects a conflicting explicit sphere override for multi-point soma files.

## Morphometry comparison convention

The API's rounded values (neurite length 12,611 µm; surface 22,768.8 µm²; volume 4,826.47 µm³; 58 bifurcations; 8 stems; soma surface 921.346 µm²) are reproduced on this reconstruction by:
- length: sum non-soma edges;
- surface: `2π × distal radius × edge length` on non-soma edges;
- volume: `π × distal radius² × edge length`;
- soma surface: frustum lateral area of type-1 edges;
- bifurcations: non-soma nodes with at least two children;
- stems: non-soma edges whose parent is type-1 soma.

This is an empirical comparison convention matching this one record, not a claim about all NeuroMorpho archives. AMSN's frustum-area estimate is reported separately.

## Intended use and limitations

Use as a real dendritic-geometry fixture for SWC parsing, cable conversion, passive electrotonic analysis and comparison with reference simulators. It has no axon, moderate dendritic completeness, clinical-context caveats and no shrinkage correction report. It does not include matched ion-channel parameters, synaptic connectivity or recorded voltage traces.
