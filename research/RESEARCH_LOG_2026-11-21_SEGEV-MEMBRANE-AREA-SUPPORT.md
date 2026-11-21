# Research log — Segev membrane area on matched control-volume support — 2026-11-21

## Question

Can NEURON's actual segment.area() values be projected onto the same endpoint control volumes as AMSN's node-centred CableTree without relying only on total membrane area?

## Motivation

AMSN CableTree partitions every tapered SWC frustum into proximal and distal surface-area halves, then assigns these halves to the parent and child electrical nodes. The global axial conductance matrices already agree closely, but the passive voltage operator also depends on capacitance and leak area at each node.

## Implementation

New script: amsn-core/examples/human_segev_membrane_area_support_audit.py.  
New workflow: .github/workflows/amsn-segev-membrane-area-support.yml.

The audit imports NEURON 9.0.2 at a 0.125 µm segment cap, reads actual segment.area(), and distributes each segment's measured area among mapped SWC half-edge intervals in proportion to the pt3d surface-area overlap. Each half-edge is assigned to the corresponding electrical parent or child node. Soma-section area is assigned to the root soma control volume; collapsed soma-wire edges remain separate.

## Verification

Pending. Do not choose a canonical passive area mapping until both cells pass, raw CSVs are inspected, and per-node/edge distributions are compared.

## Limits

The method is a matched-support area allocation using actual segment totals and pt3d geometric overlap fractions. It does not yet compare the complete NEURON passive admittance matrix or validate biological membrane parameters.
