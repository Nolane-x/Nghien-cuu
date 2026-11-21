# Research log — Segev human L2/3 morphology expansion — 2026-11-21

## Direct morphology data
Two standardized NeuroMorpho CNG SWCs have been committed unchanged:
- NMO_68174 / cell1125: 12,410 rows; soma/axon/basal/apical counts 3/116/5,595/6,696; Git blob SHA1 0659a889d47e44cb67b0685181ce7c8d8ebdc6f6.
- NMO_68175 / cell1204: 13,758 rows; counts 3/379/5,847/7,529; SHA1 5bbfdb0e8c5ab49fb6eae8a873d49b89d8fd551f.
Both: human temporal cortex, Brodmann area 21, L2–3 pyramidal/principal cells; dendrite completeness moderate; axon completeness incomplete. CC BY 4.0 attributions recorded in the data folder README.

## FCI read-only source audit
Pinned FCI commit: 75ad8b4d81a7f51bf888b30650c543592340db06. Two folders labelled Eyal map to the same morphology IDs, but FCI models.csv cites Mohan et al. 2015 morphology. FCI HOC is reduced (passive dendrites, Na/Kv in soma + synthetic 45 µm axon, no explicit 3-D spine compartments). Channel scalings are based on rat Hay L5b references; synapse parameters are FCI-specific. No FCI code/ASC source copied because the root repo has no license and individual MOD notices differ. Full conversion, provenance and caveats in FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md.

## New validation code/workflow
Added exact SWC node/type/soma/cable tests and parameterized the passive frequency audit with morphology path/label environment variables. Added four-job NEURON 9.0.2 matrix for NMO_68174/75 at 0.25 and 0.125 µm, each job running all tests and 120 impedance rows. Workflow run 44885009077 is in progress at checkpoint time; no numerical results are asserted yet.

## Guardrails
Do not combine NMO_290988 passive parameters with FCI reduced active channels or FCI synaptic values. Keep NMO_290988, Segev1125, Segev1204, FCI-reduced and original Eyal2018 as separate named configurations. Numerical passive agreement is not biological validation.


## Preliminary multi-morphology AC finding

Workflow 44885009077: four jobs passed. NMO_68174 maximum transfer-complex error ~0.365% at 0.25 µm and ~0.131% at 0.125 µm. NMO_68175 remains ~5.7% max at both meshes; input-complex discrepancy is ~0.94% at 0.1 Hz. This is a persistent morphology/import/compartment-mapping discrepancy requiring area, soma/wire, section and site mapping diagnostics. Raw CSV artifacts are linked in amsn-core/research/HUMAN_MULTI_MORPHOLOGY_AUDIT_2026-11-21.md.
