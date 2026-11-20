"""Morphometric summaries with explicit geometric conventions."""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot, pi, sqrt

from .morphology import SWCMorphology


@dataclass(frozen=True, slots=True)
class DistalCylinderMorphometrics:
    neurite_length_um: float
    neurite_surface_area_um2: float
    neurite_volume_um3: float
    soma_surface_area_um2: float
    bifurcation_count: int
    stem_count: int


def distal_cylinder_morphometrics(
    morphology: SWCMorphology,
) -> DistalCylinderMorphometrics:
    """Calculate distal-node cylinder metrics for transparent comparison.

    For each non-soma edge with length L ending at radius r, area is 2*pi*r*L
    and volume is pi*r**2*L. Type-1 soma edges are measured separately as
    tapered-frustum lateral area. Stems are neurite edges parented by soma;
    bifurcations count non-soma nodes with at least two children.

    This convention reproduces one NeuroMorpho record's public API values.
    It is not claimed to be the universal NeuroMorpho implementation.
    """
    length_um = surface_um2 = volume_um3 = soma_surface_um2 = 0.0
    stems = 0
    for node in morphology.nodes.values():
        if node.parent_id == -1:
            continue
        parent = morphology.nodes[node.parent_id]
        dx = node.x_um - parent.x_um
        dy = node.y_um - parent.y_um
        dz = node.z_um - parent.z_um
        edge_length = hypot(hypot(dx, dy), dz)
        if node.neurite_type == 1:
            slant = sqrt(edge_length**2 + (node.radius_um-parent.radius_um)**2)
            soma_surface_um2 += pi*(parent.radius_um+node.radius_um)*slant
            continue
        length_um += edge_length
        surface_um2 += 2.0*pi*node.radius_um*edge_length
        volume_um3 += pi*node.radius_um**2*edge_length
        if parent.neurite_type == 1:
            stems += 1
    bifurcations = sum(
        1 for node_id, child_ids in morphology.children.items()
        if morphology.nodes[node_id].neurite_type != 1 and len(child_ids) >= 2
    )
    return DistalCylinderMorphometrics(
        neurite_length_um=length_um,
        neurite_surface_area_um2=surface_um2,
        neurite_volume_um3=volume_um3,
        soma_surface_area_um2=soma_surface_um2,
        bifurcation_count=bifurcations,
        stem_count=stems,
    )
