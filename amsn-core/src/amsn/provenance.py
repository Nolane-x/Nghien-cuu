"""Provenance-aware SWC preflight checks for held-out morphology fixtures."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .morphology import MorphologyError, MorphologySummary, SWCMorphology


@dataclass(frozen=True, slots=True)
class SWCMorphologyValidation:
    morphology: SWCMorphology
    summary: MorphologySummary
    neurite_type_counts: dict[int, int]
    three_point_soma_detected: bool


def validate_swc_morphology(
    path: str | Path,
    *,
    expected_node_count: int,
    required_neurite_types: tuple[int, ...] = (1, 2, 3, 4),
    require_three_point_soma: bool = True,
) -> SWCMorphologyValidation:
    """Load and validate a held-out SWC without making biological completeness claims."""
    morphology = SWCMorphology.from_file(path)
    if len(morphology.nodes) != expected_node_count:
        raise MorphologyError(
            f"SWC record count {len(morphology.nodes)} != expected {expected_node_count}"
        )

    type_counts = Counter(node.neurite_type for node in morphology.nodes.values())
    missing_types = sorted(set(required_neurite_types) - set(type_counts))
    if missing_types:
        raise MorphologyError(
            f"SWC is missing required neurite types {missing_types}; "
            f"observed {dict(sorted(type_counts.items()))}"
        )

    soma = morphology.detect_neuromorpho_three_point_soma()
    if require_three_point_soma and soma is None:
        raise MorphologyError(
            "SWC does not satisfy the recognized NeuroMorpho three-point soma convention"
        )

    summary = morphology.summary()
    if summary.root_count != 1 or summary.edge_count != summary.node_count - 1:
        raise MorphologyError("SWC root/edge topology summary is inconsistent")

    return SWCMorphologyValidation(
        morphology=morphology,
        summary=summary,
        neurite_type_counts=dict(sorted(type_counts.items())),
        three_point_soma_detected=soma is not None,
    )
