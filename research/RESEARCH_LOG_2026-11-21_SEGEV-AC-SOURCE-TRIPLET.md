# Research log — Segev three-reference passive AC source audit — 2026-11-21

## Research question

How much of the observed passive AC impedance change is caused by moving NEURON's fixed reference location from the legacy base-mesh segment centre to the exact SWC arc coordinate, and how much is introduced by snapping that coordinate to a refined segment centre?

## Hypothesis

The source coordinate matters in a frequency- and morphology-dependent way. The two-position audit found a potentially non-negligible within-NEURON effect, but it did not include the exact SWC coordinate used by the existing cross-simulator AC matrix. Separating all three locations is required before attributing any AMSN-versus-NEURON residual to source placement.

## Sources and implementation

- SWC sources: NeuroMorpho NMO_68174/cell1125 and NMO_68175/cell1204, original CNG files with CC BY 4.0 attribution in the repository.
- Reference: NEURON 9.0.2 Import3D.
- Existing site-selection and same-mesh nseg refinement logic: human_fine_mesh_passive_dc_audit.py and human_passive_source_placement_control.py.
- New audit: amsn-core/examples/human_segev_ac_source_reference_triplet_audit.py.
- Workflow: .github/workflows/amsn-segev-ac-source-reference-triplet.yml.
- Three source reference positions, same final morphology mesh, five probes, eight frequencies, and unchanged generic passive parameters.
- Raw rows: expected 80 per morphology, with three pairwise comparisons per row.

## Prior result motivating this extension

The preceding audit (workflow 44898976514, commit fb4b78907f455cb6eafe933749a3f599046cb7a3) compared legacy base-mesh centre and refined segment centre:
- NMO_68174 apical q75: transfer-complex median/p95/max 0.001357/0.021954/0.021954%; input-complex max 0.010201%.
- NMO_68175 basal q75: transfer-complex median/p95/max 0.007487/0.228926/0.228926%; input-complex max 0.074897%.
- NMO_68174 basal q75 was pre-aligned; NMO_68175 apical q75 remained unresolved under the NEURON nseg cap and was excluded from sensitivity summaries.
These are within-NEURON position effects, not cross-simulator errors.

## Verification

Pending. Do not state triplet results until both matrix jobs and the raw CSVs have been read back and analyzed.

## Limits

No biological passive parameter fitting or experimental recordings are involved. The models remain individual partial cells. The numerical impact of source reference position cannot be generalized to every morphology, source site or conductance model. The original Eyal 2018 archive remains not downloaded and not integrated.

## Next step

Compare the legacy-to-exact SWC effect with the exact-to-refined-centre snapping effect; then match the exact coordinate convention to the existing AMSN-vs-NEURON AC CSV. If residuals remain, isolate probe interpolation, section junction and membrane-area/axial mapping as separate factors.

## Verified three-reference results — 2026-11-21

Workflow [44899442076](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076) passed both morphology jobs on NEURON 9.0.2; each wrote 80 rows (2 sources × 5 probes × 8 frequencies). The jobs uploaded both raw CSV and log:
- NMO_68174 artifact 14705865103.
- NMO_68175 artifact 14705880425.

Core CI [44899349672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899349672) passed Python 3.12/3.13 test/compile/example jobs and both NEURON cross-validation jobs.

Distinct source contrasts:
- NMO_68174 apical q75 (SWC 9934): legacy-centre offset 0.008323994 µm; refined-centre offset 0.001960224 µm. Legacy-to-exact transfer-complex maximum by frequency 0.0003209, 0.0003215, 0.0003790, 0.0006844, 0.0020304, 0.0057770, 0.0141009, 0.0219544%.
- NMO_68175 basal q75 (SWC 3253): legacy-centre offset 0.087630399 µm; refined-centre offset 0.000504592 µm. Legacy-to-exact transfer-complex maximum by frequency 0.0017634, 0.0017668, 0.0020825, 0.0037624, 0.0112115, 0.0330902, 0.1042289, 0.2289258%.

For these distinct source sites, exact-SWC-to-refined-centre complex impedance changes are zero at exported precision at all eight frequencies. This indicates that the exact SWC coordinate and refined centre resolve to the same effective NEURON discrete location in the tested configuration; it does not imply general zero spatial discretization error.

Non-distinct statuses:
- NMO_68174 basal q75 is pre_aligned (0.001440892 µm), so there is no distinct placement contrast.
- NMO_68175 apical q75 is unresolved_nseg_cap (best possible centre offset 4.26217e-7 µm, but no distinct segment index under cap); identical values are not evidence of insensitivity.

These results isolate a measurable base-mesh source-location effect for two tested sites. The cross-simulator AC audit already uses exact SWC source coordinates. Biological parameters and active/synaptic validity remain untested. The next experiment is the AC probe-coordinate audit, documented in [HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md](../HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md).
