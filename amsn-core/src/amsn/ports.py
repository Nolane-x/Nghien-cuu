"""Deterministic path-distance quantile selection for SWC source/probe ports.

These helpers select morphology node IDs only. They do not imply that a
quantile is a physical compartment or a biological boundary.
"""
from __future__ import annotations

from math import hypot, isfinite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amsn.morphology import SWCMorphology


def path_distances_um(morphology: "SWCMorphology") -> dict[int, float]:
    """Return root-to-node path distances along the SWC tree in micrometres."""
    distances = {morphology.root_id: 0.0}
    stack = [morphology.root_id]
    while stack:
        parent_id = stack.pop()
        parent = morphology.nodes[parent_id]
        for child_id in morphology.children[parent_id]:
            child = morphology.nodes[child_id]
            distances[child_id] = distances[parent_id] + hypot(
                child.x_um - parent.x_um,
                child.y_um - parent.y_um,
                child.z_um - parent.z_um,
            )
            stack.append(child_id)
    if len(distances) != len(morphology.nodes):
        raise ValueError("path-distance traversal did not visit every SWC node")
    return distances


def quantile_node(
    morphology: "SWCMorphology",
    distances_um: dict[int, float],
    neurite_type: int,
    quantile: float,
) -> int:
    """Select the deterministic SWC node nearest a path-distance rank."""
    if isinstance(neurite_type, bool) or not isinstance(neurite_type, int):
        raise TypeError("neurite_type must be an integer SWC type")
    if isinstance(quantile, bool) or not isinstance(quantile, (int, float)):
        raise TypeError("quantile must be a real number")
    quantile = float(quantile)
    if not isfinite(quantile) or not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be finite and between 0 and 1")
    missing = set(morphology.nodes).difference(distances_um)
    if missing:
        raise ValueError(f"path distances are missing SWC node IDs: {sorted(missing)[:8]}")
    ordered = sorted(
        (
            (float(distances_um[node_id]), node_id)
            for node_id, node in morphology.nodes.items()
            if node.neurite_type == neurite_type
        ),
        key=lambda pair: (pair[0], pair[1]),
    )
    if not ordered:
        raise ValueError(f"morphology contains no SWC nodes of type {neurite_type}")
    if not all(isfinite(distance) and distance >= 0.0 for distance, _ in ordered):
        raise ValueError("path distances must be finite and non-negative")
    index = round((len(ordered) - 1) * quantile)
    return ordered[index][1]
