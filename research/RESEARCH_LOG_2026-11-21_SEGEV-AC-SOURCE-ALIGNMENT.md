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
