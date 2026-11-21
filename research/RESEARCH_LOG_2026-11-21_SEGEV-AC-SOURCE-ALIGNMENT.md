# Research log — Segev AC source-placement alignment — 2026-11-21

## Question

Does a charge-conserving weighted two-centre source distribution improve or worsen passive transfer impedance relative to NEURON's nearest-centre and exact-SWC arc source references?

## Motivation

The native transient source-placement audit passed 4/4 jobs and found:
- weighted source placement strongly improved NMO_68175 at both meshes;
- NMO_68174 was mixed at 0.125 µm and worsened for interpolated probes at 0.0625 µm;
- total source current remained conserved to within 1.735e-18 nA.

The AC version checks the same source variable using linear frequency-domain superposition.

## Method

New script: amsn-core/examples/human_segev_ac_source_alignment_audit.py.  
New workflow: .github/workflows/amsn-segev-ac-source-alignment.yml.

The NEURON weighted source transfer is computed as (1-w)*Z(lower source centre → probe) + w*Z(upper source centre → probe). Exact-SWC and nearest-centre point-source controls are preserved. Three probe readouts are stored separately. The AMSN response always uses the exact SWC electrical node.

## Verification

Pending. Inspect all four raw CSV and summary artifacts before reporting conclusions.

## Limits

The weighted complex superposition is valid for the linear passive frequency response, but remains a discrete source-placement diagnostic and not a biological claim.


## Verified results — AC source-placement alignment

Workflow [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4 morphology/mesh jobs; Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4.

Each of the four configurations generated 1,080 raw rows and 135 summary rows. NEURON exact-SWC and nearest-centre source references are identical at exported precision.

Weighted source alignment:
- NMO_68175: strong improvement at both meshes; maximum complex error falls to 0.068720%/0.071947% at 0.125 µm and 0.069568%/0.072209% at 0.0625 µm for exact/nearest and interpolated probe readouts, respectively.
- NMO_68174: small mixed benefit at 0.125 µm; at 0.0625 µm, median/P95 and interpolated-probe statistics worsen.

Keep weighted source optional/diagnostic; it is not universally superior. Full report: [HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](../research/HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md).
