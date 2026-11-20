# Real human L2-3 morphology import and validation

**Date:** 2026-11-20 (UTC+7)  
**Record:** NeuroMorpho.Org NMO_290988 / API ID 290988  
**File:** `amsn-core/data/human/1094_Mohan_etal_2015.CNG.swc`  
**Git blob SHA:** `7f06d10b929ec3ae215cbc0a2e3222e9bbaff46e`

## Selection and limits

The record identifies a human temporal-neocortex pyramidal/principal cell from middle temporal gyrus, Brodmann area 21, layer 2–3. It contains soma and dendrites but no axon; dendritic integrity is rated moderate. Metadata records mesiotemporal sclerosis and does not report shrinkage. Age range is 20–58 years; the sex field is “Male/Female” rather than an individual value. This is a real dendritic-geometry fixture, not a complete neuron or healthy-control specimen.

Mohan et al. (2015) report human temporal-cortex reconstructions from surgical tissue. Their study-level finding that measured morphology did not correlate with etiology/severity/duration does not erase the sample-specific clinical annotation; this cell must retain its metadata context.

## License and provenance

NeuroMorpho.Org Terms of Use state repository data are CC BY 4.0. The attribution in `data/human/README.md` includes the original paper, NeuroMorpho.Org RRID and Tecuatl et al. (2024). Only the standardized SWC data file is mirrored; no paper text or figures are copied.

## SWC integrity

The exact standardized CNG SWC contains 321,865 text characters and 8,903 records, each with seven numeric fields. Validation found 8,903 unique IDs, one root, all parent IDs present, positive radii and no disconnected points or cycles.

| SWC type | Count |
|---|---:|
| Soma | 3 |
| Basal dendrite | 4,051 |
| Apical dendrite | 4,849 |
| Axon | 0 |

## Morphometry reproduction

| Metric | NeuroMorpho API | Independent calculation |
|---|---:|---:|
| Neurite length (µm) | 12,611.0 | 12,610.981 |
| Neurite surface (µm²) | 22,768.8 | 22,768.848 |
| Neurite volume (µm³) | 4,826.47 | 4,826.466 |
| Soma surface (µm²) | 921.346 | 921.346 |
| Bifurcations | 58 | 58 |
| Stems | 8 | 8 |

For this record, the independent calculation uses non-soma edge length, distal-node cylinder surface (2\pi r_{distal}L), distal-node cylinder volume (\pi r_{distal}^{2}L), soma-edge frustum surface, non-soma bifurcations and neurite stems directly connected to soma. This is an empirically reproduced comparison convention for this record, not a claim about every NeuroMorpho archive's internal implementation.

## Multi-point soma bug found and fixed

The standardized SWC represents soma with three type-1 points. The previous AMSN geometry summary and cable converter always added a spherical root area, even when type-1 soma edges already represented a multi-point soma. This double-counted soma membrane area.

The code now:
- adds a spherical estimate only for a single-point type-1 soma;
- uses type-1 soma edges for a multi-point soma;
- does not assume a spherical soma where the root is not type 1;
- rejects a conflicting explicit root-soma-area override for a multi-point soma;
- excludes soma nodes from neurite bifurcation counts.

AMSN's frustum-area estimate is not expected to numerically match the distal-cylinder surface convention. They are reported separately rather than being forced to agree.

## Implementation added

- `src/amsn/morphology.py`: multi-point soma handling and non-soma bifurcation count.
- `src/amsn/morphometrics.py`: explicit distal-cylinder comparator.
- `tests/test_human_morphology.py`: structural, soma-area and API morphometry tests.
- `examples/human_morphology_inspect.py`: reproducible inspection example.
- `data/human/README.md` and provenance JSON: license, record metadata and file-integrity checks.

## Next steps

1. Run package CI on Python 3.12 and 3.13 against the committed 8,903-point SWC.
2. Compare the multi-point soma and branch attachment approximation with NEURON or Arbor using the same exact SWC.
3. Run passive convergence on multiple injection and recording locations on this real morphology.
4. Find another human L2–3 cell with traced axon and stronger reconstruction completeness; preserve pathology/shrinkage context.
5. Reproduce the published human cortical model in Eyal et al. 2018 / ModelDB 238347 unchanged before adding active conductance fits.

## Sources

- Mohan et al. (2015), *Cerebral Cortex* 25(12):4839–4853, DOI 10.1093/cercor/bhv188, PMID 26318661.
- NeuroMorpho.Org NMO_290988, RRID:SCR_002145; Terms: https://www.neuromorpho.org/useterm.jsp
- Tecuatl et al. (2024), *FASEB BioAdvances* 6(7):207–221, DOI 10.1096/fba.2024-00048.
- Standard SWC specification: https://github.com/INCF/swc-specification
- NeuroMorpho standardized soma convention: https://cngpro.gmu.edu/SomaFormat.html
